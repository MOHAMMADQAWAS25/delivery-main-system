from datetime import datetime
from uuid import UUID
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.repositories.work_exhibition_sql import work_exhibitions_sql
from src.entities.dto.feed import FeedCardResponse
from src.infrastructure.integrations.supabase_storage import SupabaseWorkStorage


class SqlAlchemyRelatedArtworksRepository:
    def __init__(self, session: AsyncSession, storage: SupabaseWorkStorage) -> None:
        self._session, self._storage = session, storage

    async def available(self, work_id: UUID) -> bool:
        return bool(await self._session.scalar(text("""
            select exists(select 1 from works w join user_accounts a on a.user_id=w.owner_user_id
                where w.work_id=:id and w.status='published' and a.account_status='active')
        """), {"id": work_id}))

    async def list_related(self, work_id: UUID, viewer: UUID | None, snapshot: datetime,
                           offset: int, limit: int) -> list[FeedCardResponse]:
        # Compare stored, model-compatible vectors only. No provider/network call.
        rows = (await self._session.execute(text(f"""
            with source as (
                select e.embedding, e.model_name from works w
                join user_accounts a on a.user_id=w.owner_user_id and a.account_status='active'
                left join work_embeddings e on e.work_id=w.work_id
                where w.work_id=:id and w.status='published'
            ), scored as (
                select w.*,
                    case when e.model_name=source.model_name then
                        1 - (e.embedding <=> source.embedding) else null end as similarity
                from source cross join works w
                join user_accounts a on a.user_id=w.owner_user_id and a.account_status='active'
                left join work_embeddings e on e.work_id=w.work_id
                where w.work_id<>:id and w.status='published' and w.created_at<=:snapshot
            ), page as (
                select * from scored where similarity>=0.20
                order by similarity desc, created_at desc, work_id desc
                limit :limit offset :offset
            )
            select page.work_id, page.owner_user_id, page.type_id, page.title,
                {work_exhibitions_sql("page.work_id")} as exhibitions,
                page.storage_path, page.mime_type, page.created_at, page.media,
                t.name_en as type_name_en, t.name_ar as type_name_ar,
                coalesce(p.full_name, 'InkFig artist') as artist_name,
                p.avatar_object_path as artist_avatar_path,
                (select count(*) from work_likes l join user_accounts a on a.user_id=l.user_id
                    where l.work_id=page.work_id and a.account_status='active') as like_count,
                exists(select 1 from work_likes l where l.work_id=page.work_id
                    and l.user_id=cast(:viewer as uuid)) as liked_by_me,
                exists(select 1 from work_saves s where s.work_id=page.work_id
                    and s.user_id=cast(:viewer as uuid)) as saved_by_me
            from page join work_types t on t.type_id=page.type_id
            left join user_profiles p on p.user_id=page.owner_user_id
            order by page.similarity desc, page.created_at desc, page.work_id desc
        """), {"id": work_id, "viewer": viewer, "snapshot": snapshot, "offset": offset, "limit": limit})).mappings()
        return [FeedCardResponse(
            **{key: value for key, value in row.items() if key not in ("storage_path", "artist_avatar_path")},
            image_url=self._storage.public_url(row.storage_path),
            artist_avatar_url=self._storage.profile_avatar_url(row.artist_avatar_path),
        ) for row in rows]
