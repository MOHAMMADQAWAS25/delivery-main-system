from typing import Any
from src.entities.dto.exhibition_leaderboard import ExhibitionLeaderboard
from uuid import UUID, uuid4

from src.entities.dto.exhibitions import (
    BannerUploadInput,
    Exhibition,
    ExhibitionError,
    ExhibitionInput,
    ExhibitionPage,
    ReviewInput,
    SubmissionPage,
)
from src.entities.repositories.exhibitions import ExhibitionRepository
from src.entities.repositories.works import WorkMediaProcessor, WorkStorage


class ExhibitionService:
    async def leaderboard(self, exhibition_id: UUID, limit: int, cursor: int, type_id: UUID | None = None) -> ExhibitionLeaderboard:
        exhibition = await self.get(exhibition_id)
        page = await self.repository.leaderboard(exhibition_id, limit, cursor, type_id)
        return ExhibitionLeaderboard(exhibition=exhibition, **page)

    async def pending_counts(self, actor: UUID | None) -> dict[str, Any]:
        await self.authorize(actor, "exhibitions.manage")
        return await self.repository.pending_counts()

    def __init__(
        self,
        repository: ExhibitionRepository,
        storage: WorkStorage,
        media: WorkMediaProcessor,
    ) -> None:
        self.repository, self.storage, self.media = repository, storage, media

    async def authorize(self, user_id: UUID | None, permission: str) -> UUID:
        if user_id is None:
            raise ExhibitionError(401, "Authentication is required.")
        if not await self.repository.allowed(user_id, permission):
            raise ExhibitionError(
                403, "You do not have permission to perform this action."
            )
        return user_id

    async def list(
        self, limit: int, cursor: int, period: str = "all"
    ) -> ExhibitionPage:
        rows = await self.repository.list_exhibitions(limit + 1, cursor, period)
        return ExhibitionPage(
            items=rows[:limit],
            next_cursor=cursor + limit if len(rows) > limit else None,
        )

    async def get(self, exhibition_id: UUID) -> Exhibition:
        return await self.repository.get(exhibition_id)

    async def eligible(
        self,
        actor: UUID | None,
        limit: int,
        cursor: int,
        work_id: UUID | None = None,
        exhibition_id: UUID | None = None,
    ) -> ExhibitionPage:
        user = await self.authorize(actor, "exhibitions.participate")
        rows = await self.repository.eligible(
            user, limit + 1, cursor, work_id, exhibition_id
        )
        return ExhibitionPage(
            items=rows[:limit],
            next_cursor=cursor + limit if len(rows) > limit else None,
        )

    async def blocks(
        self, actor: UUID | None, exhibition_id: UUID, limit: int, cursor: int
    ) -> dict[str, object]:
        await self.authorize(actor, "exhibitions.manage")
        await self.repository.get(exhibition_id)
        rows = await self.repository.blocks(exhibition_id, limit + 1, cursor)
        return {
            "items": rows[:limit],
            "next_cursor": cursor + limit if len(rows) > limit else None,
        }

    async def save(
        self,
        actor: UUID | None,
        data: ExhibitionInput,
        exhibition_id: UUID | None = None,
    ) -> Exhibition:
        user = await self.authorize(actor, "exhibitions.manage")
        return await self.repository.save(user, data, exhibition_id)

    async def submit(
        self, actor: UUID | None, exhibition_id: UUID, work_id: UUID
    ) -> None:
        user = await self.authorize(actor, "exhibitions.participate")
        await self.repository.submit(exhibition_id, user, work_id)

    async def delete(self, actor: UUID | None, exhibition_id: UUID) -> None:
        user = await self.authorize(actor, "exhibitions.manage")
        if not await self.repository.is_administrator(user):
            raise ExhibitionError(403, "Only administrators may delete exhibitions.")
        await self.repository.delete(exhibition_id)

    async def submissions(
        self,
        actor: UUID | None,
        exhibition_id: UUID,
        scope: str,
        limit: int,
        cursor: int,
        status: str | None = None,
    ) -> SubmissionPage:
        if scope == "manage":
            await self.authorize(actor, "exhibitions.manage")
        elif scope == "mine":
            await self.authorize(actor, "exhibitions.participate")
        await self.repository.get(exhibition_id)
        rows = await self.repository.submissions(
            exhibition_id, actor, scope, limit + 1, cursor, status
        )
        return SubmissionPage(
            items=rows[:limit],
            next_cursor=cursor + limit if len(rows) > limit else None,
        )

    async def review(
        self,
        actor: UUID | None,
        exhibition_id: UUID,
        submission_id: UUID,
        data: ReviewInput,
    ) -> None:
        user = await self.authorize(actor, "exhibitions.manage")
        await self.repository.review(
            exhibition_id, submission_id, user, data.status, data.reason
        )

    async def block(
        self, actor: UUID | None, exhibition_id: UUID, user_id: UUID, reason: str | None
    ) -> None:
        manager = await self.authorize(actor, "exhibitions.manage")
        if manager == user_id:
            raise ExhibitionError(409, "You cannot block yourself.")
        await self.repository.block(exhibition_id, user_id, manager, reason)

    async def withdraw(
        self,
        actor: UUID | None,
        exhibition_id: UUID,
        submission_id: UUID,
        reason: str | None,
    ) -> None:
        user = await self.authorize(actor, "exhibitions.participate")
        await self.repository.withdraw(exhibition_id, submission_id, user, reason)

    async def review_withdrawal(
        self,
        actor: UUID | None,
        exhibition_id: UUID,
        submission_id: UUID,
        data: ReviewInput,
    ) -> None:
        manager = await self.authorize(actor, "exhibitions.manage")
        await self.repository.review_withdrawal(
            exhibition_id, submission_id, manager, data.status, data.reason
        )

    async def prepare_banner(
        self, actor: UUID | None, exhibition_id: UUID, data: BannerUploadInput
    ) -> dict[str, str]:
        await self.authorize(actor, "exhibitions.manage")
        await self.repository.get(exhibition_id)
        extension = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}[
            data.mime_type
        ]
        path = f"{exhibition_id}/{uuid4()}.{extension}"
        url, token = await self.storage.create_signed_upload(path)
        return {"object_path": path, "upload_url": url, "upload_token": token}

    async def complete_banner(
        self, actor: UUID | None, exhibition_id: UUID, path: str
    ) -> None:
        await self.authorize(actor, "exhibitions.manage")
        await self.repository.get(exhibition_id)
        if (
            not path.startswith(f"{exhibition_id}/")
            or ".." in path
            or len(path.split("/")) != 2
        ):
            raise ExhibitionError(422, "Invalid banner path.")
        await self.media.prepare(path)
        old = await self.repository.banner(exhibition_id, path)
        if old and old != path:
            await self.storage.delete_object(old)
