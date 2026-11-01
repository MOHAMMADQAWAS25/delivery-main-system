from datetime import UTC, datetime
from typing import Any
from uuid import UUID

import httpx
from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.entities.dto.exhibitions import (
    Exhibition,
    ExhibitionError,
    ExhibitionInput,
    Submission,
)
from src.entities.exceptions.works import StorageDeleteError
from src.infrastructure.integrations.notification_realtime import (
    publish_exhibition_updates,
)
from src.infrastructure.integrations.supabase_storage import SupabaseWorkStorage


class SqlAlchemyExhibitionRepository:
    def __init__(
        self,
        session: AsyncSession,
        banners: SupabaseWorkStorage,
        works: SupabaseWorkStorage,
    ) -> None:
        self.session, self.banners, self.works = session, banners, works

    async def pending_counts(self) -> dict[str, Any]:
        rows = (await self.session.execute(text("""
            select s.exhibition_id,
                   count(*) filter(where s.status='pending') submissions,
                   count(*) filter(where s.withdrawal_status='pending') withdrawals
            from exhibition_submissions s join works w on w.work_id=s.work_id
            join user_accounts a on a.user_id=s.user_id
            where a.account_status='active' and w.status='published'
              and (s.status='pending' or s.withdrawal_status='pending')
            group by s.exhibition_id
        """))).mappings().all()
        items = [dict(row) for row in rows]
        return {"items": items, "total": sum(int(row["submissions"]) + int(row["withdrawals"]) for row in rows)}

    async def decision_notification(self, exhibition_id: UUID, submission_id: UUID, actor: UUID, event: str, reason: str | None, key: str) -> None:
        await self.session.execute(text("""
            insert into notifications(recipient_user_id,actor_user_id,event_type,work_id,
                exhibition_id,submission_id,exhibition_name,decision_reason,decision_key)
            select s.user_id,:actor,:event,s.work_id,s.exhibition_id,s.submission_id,e.name,:reason,:key
            from exhibition_submissions s join exhibitions e on e.exhibition_id=s.exhibition_id
            where s.exhibition_id=:id and s.submission_id=:submission and s.user_id<>:actor
            on conflict do nothing
        """), {"id": exhibition_id, "submission": submission_id, "actor": actor, "event": event, "reason": reason, "key": key})

    async def allowed(self, user_id: UUID, permission: str) -> bool:
        return bool(
            await self.session.scalar(
                text("""
            select exists(select 1 from user_accounts a join user_roles r on r.user_id=a.user_id
            join role_permissions p on p.role_code=r.role_code
            where a.user_id=:user and a.account_status='active' and a.is_active=true
            and a.email_verified_at is not null and p.permission_code=:permission)
        """),
                {"user": user_id, "permission": permission},
            )
        )

    def exhibition(self, row: RowMapping) -> Exhibition:
        data: dict[str, Any] = dict(row)
        path = data.pop("banner_path")
        now = datetime.now(UTC)
        return Exhibition(
            **data,
            banner_url=self.banners.public_url(path) if path else None,
            participation_open=data["participation_opens_at"]
            <= now
            < data["participation_closes_at"],
        )

    async def is_administrator(self, user_id: UUID) -> bool:
        return bool(await self.session.scalar(text("""
            select exists(select 1 from user_roles
            where user_id=:user and role_code in ('admin','system_administrator'))
        """), {"user": user_id}))

    async def delete(self, exhibition_id: UUID) -> None:
        # Serialize with submission/review/banner operations. Storage is removed
        # before committing SQL so cleanup failures leave a retryable exhibition.
        try:
            await self.lock(exhibition_id)
            path = await self.session.scalar(
                text("select banner_path from exhibitions where exhibition_id=:id"),
                {"id": exhibition_id},
            )
            if path:
                await self.banners.delete_object(str(path))
            await self.session.execute(
                text("delete from exhibitions where exhibition_id=:id"),
                {"id": exhibition_id},
            )
            # Foreign keys cascade memberships (including withdrawal metadata)
            # and blocks; original works, their media and embeddings are retained.
            await self.session.commit()
        except (StorageDeleteError, httpx.HTTPError) as error:
            await self.session.rollback()
            raise ExhibitionError(503, "Exhibition banner cleanup failed. Please retry deletion.") from error
        except Exception:
            await self.session.rollback()
            raise
        await publish_exhibition_updates(self.session, exhibition_id)

    async def list_exhibitions(
        self, limit: int, cursor: int, period: str = "all"
    ) -> list[Exhibition]:
        end = "coalesce(event_ends_at,event_at + interval '24 hours')"
        condition = {"upcoming": "event_at > now()", "current": f"event_at <= now() and {end} > now()", "past": f"{end} <= now()"}.get(
            period, "true"
        )
        order = "asc" if period in ("upcoming", "current") else "desc"
        rows = (
            (
                await self.session.execute(
                    text(
                        f"select * from exhibitions where {condition} order by event_at {order},exhibition_id {order} limit :limit offset :cursor"
                    ),
                    {"limit": limit, "cursor": cursor},
                )
            )
            .mappings()
            .all()
        )
        return [self.exhibition(row) for row in rows]

    async def get(self, exhibition_id: UUID) -> Exhibition:
        row = (
            (
                await self.session.execute(
                    text("select * from exhibitions where exhibition_id=:id"),
                    {"id": exhibition_id},
                )
            )
            .mappings()
            .first()
        )
        if row is None:
            raise ExhibitionError(404, "Exhibition not found.")
        return self.exhibition(row)

    async def eligible(
        self,
        user_id: UUID,
        limit: int,
        cursor: int,
        work_id: UUID | None = None,
        exhibition_id: UUID | None = None,
    ) -> list[Exhibition]:
        params = {
            "user": user_id,
            "work": work_id,
            "id": exhibition_id,
            "limit": limit,
            "cursor": cursor,
        }
        if work_id is not None:
            owned = await self.session.scalar(
                text(
                    "select exists(select 1 from works where work_id=:work and owner_user_id=:user and status='published')"
                ),
                params,
            )
            if not owned:
                raise ExhibitionError(404, "Select one of your published works.")
        rows = (
            (
                await self.session.execute(
                    text("""
            select e.* from exhibitions e
            where e.participation_opens_at <= now() and now() < e.participation_closes_at
            and e.event_at > now() and (cast(:id as uuid) is null or e.exhibition_id=:id)
            and not exists(select 1 from exhibition_blocks b where b.exhibition_id=e.exhibition_id and b.user_id=:user)
            and (select count(*) from exhibition_submissions s where s.exhibition_id=e.exhibition_id and s.user_id=:user and s.status in ('pending','approved')) < 10
            and (cast(:work as uuid) is null or not exists(select 1 from exhibition_submissions s where s.exhibition_id=e.exhibition_id and s.work_id=:work))
            order by e.event_at,e.exhibition_id limit :limit offset :cursor
        """),
                    params,
                )
            )
            .mappings()
            .all()
        )
        return [self.exhibition(row) for row in rows]

    async def check_capacity(self, exhibition_id: UUID, user_id: UUID) -> None:
        count = await self.session.scalar(
            text("""select count(*) from exhibition_submissions
            where exhibition_id=:id and user_id=:user and status in ('pending','approved')"""),
            {"id": exhibition_id, "user": user_id},
        )
        if count is not None and count >= 10:
            raise ExhibitionError(
                409,
                "You can have at most 10 pending or approved works in this exhibition.",
            )

    async def save(
        self, user_id: UUID, data: ExhibitionInput, exhibition_id: UUID | None
    ) -> Exhibition:
        params = {**data.model_dump(), "creator": user_id, "id": exhibition_id}
        if exhibition_id:
            statement = """update exhibitions set name=:name,description=:description,event_at=:event_at,event_ends_at=:event_ends_at,
                participation_opens_at=:participation_opens_at,participation_closes_at=:participation_closes_at,
                updated_at=now() where exhibition_id=:id returning *"""
        else:
            statement = """insert into exhibitions(creator_user_id,name,description,event_at,event_ends_at,participation_opens_at,participation_closes_at)
                values(:creator,:name,:description,:event_at,:event_ends_at,:participation_opens_at,:participation_closes_at) returning *"""
        row = (await self.session.execute(text(statement), params)).mappings().first()
        if row is None:
            raise ExhibitionError(404, "Exhibition not found.")
        result = self.exhibition(row)
        await self.session.commit()
        return result

    async def lock(self, exhibition_id: UUID) -> None:
        found = await self.session.scalar(
            text(
                "select exhibition_id from exhibitions where exhibition_id=:id for update"
            ),
            {"id": exhibition_id},
        )
        if found is None:
            raise ExhibitionError(404, "Exhibition not found.")

    async def submit(self, exhibition_id: UUID, user_id: UUID, work_id: UUID) -> None:
        await self.lock(exhibition_id)
        params = {"id": exhibition_id, "user": user_id, "work": work_id}
        opened = await self.session.scalar(
            text(
                "select participation_opens_at <= now() and now() < participation_closes_at from exhibitions where exhibition_id=:id"
            ),
            params,
        )
        if not opened:
            raise ExhibitionError(409, "Participation is not open.")
        blocked = await self.session.scalar(
            text(
                "select exists(select 1 from exhibition_blocks where exhibition_id=:id and user_id=:user)"
            ),
            params,
        )
        if blocked:
            raise ExhibitionError(
                403, "You are blocked from participating in this exhibition."
            )
        owned = await self.session.scalar(
            text(
                "select work_id from works where work_id=:work and owner_user_id=:user and status='published' for share"
            ),
            params,
        )
        if not owned:
            raise ExhibitionError(404, "Select one of your published works.")
        duplicate = await self.session.scalar(
            text(
                "select exists(select 1 from exhibition_submissions where exhibition_id=:id and work_id=:work)"
            ),
            params,
        )
        if duplicate:
            raise ExhibitionError(409, "This work has already been submitted.")
        await self.check_capacity(exhibition_id, user_id)
        try:
            await self.session.execute(
                text(
                    "insert into exhibition_submissions(exhibition_id,work_id,user_id) values(:id,:work,:user)"
                ),
                params,
            )
            await self.session.commit()
        except IntegrityError as error:
            await self.session.rollback()
            raise ExhibitionError(
                409, "This work has already been submitted."
            ) from error
        await publish_exhibition_updates(self.session, exhibition_id, user_id)

    async def submissions(
        self,
        exhibition_id: UUID,
        viewer: UUID | None,
        scope: str,
        limit: int,
        cursor: int,
        status: str | None = None,
    ) -> list[Submission]:
        condition = (
            "s.status='approved' and exists(select 1 from exhibitions e where e.exhibition_id=s.exhibition_id and e.event_at <= now())"
            if scope == "public"
            else "s.user_id=cast(:viewer as uuid)"
            if scope == "mine"
            else "true"
        )
        rows = (
            (
                await self.session.execute(
                    text(f"""
            select s.*,w.title,w.description,w.storage_path,t.name_en type_name_en,t.name_ar type_name_ar,p.full_name artist_name,
                   p.avatar_object_path as artist_avatar_path from exhibition_submissions s
            join works w on w.work_id=s.work_id join user_profiles p on p.user_id=s.user_id
            join work_types t on t.type_id=w.type_id
            join user_accounts a on a.user_id=s.user_id
            where s.exhibition_id=:id and {condition} and a.account_status='active' and w.status='published'
            and (cast(:status as text) is null or s.status=:status)
            {"and not exists(select 1 from exhibition_blocks b where b.exhibition_id=s.exhibition_id and b.user_id=s.user_id)" if scope == "public" else ""}
            order by s.created_at desc,s.submission_id desc limit :limit offset :cursor
        """),
                    {
                        "id": exhibition_id,
                        "viewer": viewer,
                        "limit": limit,
                        "cursor": cursor,
                        "status": status,
                    },
                )
            )
            .mappings()
            .all()
        )
        result = []
        for row in rows:
            data = dict(row)
            avatar_path = data.pop("artist_avatar_path", None)
            if scope == "public":
                for key in (
                    "withdrawal_status",
                    "withdrawal_reason",
                    "withdrawal_requested_at",
                    "withdrawal_review_reason",
                ):
                    data[key] = None
            result.append(
                Submission(
                    **data,
                    image_url=self.works.public_url(row["storage_path"]),
                    artist_avatar_url=self.works.profile_avatar_url(avatar_path),
                )
            )
        return result

    async def review(
        self,
        exhibition_id: UUID,
        submission_id: UUID,
        actor: UUID,
        status: str,
        reason: str | None,
    ) -> None:
        await self.lock(exhibition_id)
        previous = (await self.session.execute(text(
            "select user_id,status,rejection_reason from exhibition_submissions where exhibition_id=:id and submission_id=:submission"
        ), {"id": exhibition_id, "submission": submission_id})).mappings().first()
        if previous is None:
            raise ExhibitionError(404, "Submission not found.")
        if previous["status"] == status and previous["rejection_reason"] == (reason if status == "rejected" else None):
            return
        if status == "approved":
            await self.session.execute(
                text(
                    "select w.work_id from works w join exhibition_submissions s on s.work_id=w.work_id where s.exhibition_id=:id and s.submission_id=:submission for share of w"
                ),
                {"id": exhibition_id, "submission": submission_id},
            )
            if previous is not None and previous["status"] == "rejected":
                await self.check_capacity(exhibition_id, previous["user_id"])
        found = await self.session.scalar(
            text("""update exhibition_submissions set status=cast(:status as varchar),rejection_reason=:reason,
            reviewer_user_id=:actor,reviewed_at=now(),
            withdrawal_status=case when cast(:status as varchar)='rejected' then null else withdrawal_status end,
            withdrawal_reason=case when cast(:status as varchar)='rejected' then null else withdrawal_reason end,
            withdrawal_requested_at=case when cast(:status as varchar)='rejected' then null else withdrawal_requested_at end,
            withdrawal_review_reason=case when cast(:status as varchar)='rejected' then null else withdrawal_review_reason end
            where exhibition_id=:id and submission_id=:submission
            returning reviewed_at"""),
            {
                "id": exhibition_id,
                "submission": submission_id,
                "actor": actor,
                "status": status,
                "reason": reason if status == "rejected" else None,
            },
        )
        if found is None:
            raise ExhibitionError(404, "Submission not found.")
        changed = previous["status"] != status
        if changed:
            await self.decision_notification(exhibition_id, submission_id, actor, f"submission_{status}", reason, f"submission:{submission_id}:{status}:{found}")
        await self.session.commit()
        await publish_exhibition_updates(self.session, exhibition_id, previous["user_id"], notification=changed)

    async def withdraw(
        self, exhibition_id: UUID, submission_id: UUID, actor: UUID, reason: str | None
    ) -> None:
        await self.lock(exhibition_id)
        params = {
            "id": exhibition_id,
            "submission": submission_id,
            "actor": actor,
            "reason": reason,
        }
        row = (
            (
                await self.session.execute(
                    text(
                        "select status,withdrawal_status from exhibition_submissions where exhibition_id=:id and submission_id=:submission and user_id=:actor for update"
                    ),
                    params,
                )
            )
            .mappings()
            .first()
        )
        if row is None:
            raise ExhibitionError(404, "Submission not found.")
        if row["status"] == "pending":
            await self.session.execute(
                text(
                    "delete from exhibition_submissions where submission_id=:submission"
                ),
                params,
            )
        elif row["status"] == "approved":
            if not reason:
                raise ExhibitionError(
                    422, "A deletion reason is required for approved works."
                )
            if row["withdrawal_status"] == "pending":
                raise ExhibitionError(409, "A deletion request is already pending.")
            await self.session.execute(
                text("""update exhibition_submissions set withdrawal_status='pending',
                withdrawal_reason=:reason,withdrawal_requested_at=now(),withdrawal_review_reason=null,
                withdrawal_reviewer_user_id=null,withdrawal_reviewed_at=null where submission_id=:submission"""),
                params,
            )
        else:
            raise ExhibitionError(
                409, "Only pending or approved submissions can be withdrawn."
            )
        await self.session.commit()
        await publish_exhibition_updates(self.session, exhibition_id, actor)

    async def review_withdrawal(
        self,
        exhibition_id: UUID,
        submission_id: UUID,
        actor: UUID,
        status: str,
        reason: str | None,
    ) -> None:
        await self.lock(exhibition_id)
        params = {
            "id": exhibition_id,
            "submission": submission_id,
            "actor": actor,
            "reason": reason,
        }
        record = (await self.session.execute(
            text(
                "select user_id,withdrawal_requested_at from exhibition_submissions where exhibition_id=:id and submission_id=:submission and status='approved' and withdrawal_status='pending' for update"
            ),
            params,
        )).mappings().first()
        if record is None:
            raise ExhibitionError(409, "No pending deletion request was found.")
        await self.decision_notification(exhibition_id, submission_id, actor, f"withdrawal_{status}", reason, f"withdrawal:{submission_id}:{record['withdrawal_requested_at']}")
        await self.session.execute(
            text("""insert into exhibition_withdrawal_audits(exhibition_id,submission_id,work_id,user_id,reason,decision,review_reason,reviewer_user_id)
            select exhibition_id,submission_id,work_id,user_id,withdrawal_reason,:decision,:reason,:actor
            from exhibition_submissions where submission_id=:submission"""),
            {**params, "decision": status},
        )
        if status == "approved":
            await self.session.execute(
                text(
                    "delete from exhibition_submissions where submission_id=:submission"
                ),
                params,
            )
        else:
            await self.session.execute(
                text("""update exhibition_submissions set withdrawal_status='rejected',
                withdrawal_review_reason=:reason,withdrawal_reviewer_user_id=:actor,withdrawal_reviewed_at=now()
                where submission_id=:submission"""),
                params,
            )
        await self.session.commit()

        await publish_exhibition_updates(self.session, exhibition_id, record["user_id"], notification=True)

    async def block(
        self, exhibition_id: UUID, user_id: UUID, actor: UUID, reason: str | None
    ) -> None:
        await self.lock(exhibition_id)
        params = {
            "id": exhibition_id,
            "user": user_id,
            "actor": actor,
            "reason": reason,
        }
        if reason is None:
            await self.session.execute(
                text(
                    "delete from exhibition_blocks where exhibition_id=:id and user_id=:user"
                ),
                params,
            )
        else:
            exists = await self.session.scalar(
                text("select user_id from user_accounts where user_id=:user"), params
            )
            if exists is None:
                raise ExhibitionError(404, "Account not found.")
            await self.session.execute(
                text("""insert into exhibition_blocks(exhibition_id,user_id,blocked_by,reason)
                values(:id,:user,:actor,:reason) on conflict(exhibition_id,user_id)
                do update set blocked_by=excluded.blocked_by,reason=excluded.reason,created_at=now()"""),
                params,
            )
        await self.session.commit()
        await publish_exhibition_updates(self.session, exhibition_id, user_id)

    async def blocks(
        self, exhibition_id: UUID, limit: int, cursor: int
    ) -> list[dict[str, str]]:
        rows = (
            (
                await self.session.execute(
                    text("""select b.user_id,p.full_name,b.reason from exhibition_blocks b
            join user_profiles p on p.user_id=b.user_id where exhibition_id=:id
            order by b.created_at desc,b.user_id desc limit :limit offset :cursor"""),
                    {"id": exhibition_id, "limit": limit, "cursor": cursor},
                )
            )
            .mappings()
            .all()
        )
        return [
            {
                "user_id": str(r["user_id"]),
                "full_name": r["full_name"],
                "reason": r["reason"],
            }
            for r in rows
        ]

    async def banner(self, exhibition_id: UUID, path: str | None) -> str | None:
        await self.lock(exhibition_id)
        old = await self.session.scalar(
            text("select banner_path from exhibitions where exhibition_id=:id"),
            {"id": exhibition_id},
        )
        await self.session.execute(
            text(
                "update exhibitions set banner_path=:path,updated_at=now() where exhibition_id=:id"
            ),
            {"id": exhibition_id, "path": path},
        )
        await self.session.commit()
        return old
