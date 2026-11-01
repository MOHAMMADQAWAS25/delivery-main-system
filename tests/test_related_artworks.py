import base64
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast
from uuid import UUID, uuid4
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from src.app.services.related_artworks_service import RelatedArtworksService
from src.entities.dto.feed import FeedCardResponse
from src.entities.exceptions.works import WorkNotFoundError
from src.infrastructure.config.settings import get_settings
from src.infrastructure.integrations.supabase_storage import SupabaseWorkStorage
from src.infrastructure.repositories.related_artworks_repository import SqlAlchemyRelatedArtworksRepository
from src.infrastructure.repositories.work_exhibition_sql import has_work_exhibition_sql
from src.entities.dto.related_artworks import RelatedArtworksResponse
from src.interface.dependencies.authentication import get_optional_user
from src.interface.dependencies.works import get_related_artworks_service
from src.main import create_app


def card() -> FeedCardResponse:
    return FeedCardResponse(work_id=uuid4(), owner_user_id=uuid4(), artist_name="Artist", type_id=uuid4(),
                            type_name_en="Art", type_name_ar="فن", title="Artwork", image_url="https://example.com/art.png",
                            mime_type="image/png", like_count=0, liked_by_me=False, saved_by_me=False, created_at=datetime.now(UTC))


class Repository:
    exists = True
    def __init__(self) -> None:
        self.calls: list[tuple[datetime, int, int]] = []
        self.rows = [card() for _ in range(4)]

    async def available(self, work_id: UUID) -> bool:
        return self.exists

    async def list_related(self, work_id: UUID, viewer: UUID | None, snapshot: datetime, offset: int, limit: int) -> list[FeedCardResponse]:
        self.calls.append((snapshot, offset, limit))
        return self.rows[offset:offset + limit]


@pytest.mark.asyncio
async def test_bounded_pages_keep_the_original_snapshot_and_scope() -> None:
    repository = Repository()
    service = RelatedArtworksService(repository)
    work_id = uuid4()
    first = await service.get(work_id, None, 2)
    assert len(first.items) == 2 and first.next_cursor
    second = await service.get(work_id, None, 2, first.next_cursor)
    assert second.next_cursor is None
    assert not set(item.work_id for item in first.items) & set(item.work_id for item in second.items)
    assert repository.calls[0][0] == repository.calls[1][0]
    assert repository.calls[0][2] == 3
    with pytest.raises(ValueError):
        await service.get(uuid4(), None, 2, first.next_cursor)


@pytest.mark.asyncio
@pytest.mark.parametrize("cursor", ["bad", "", "x" * 513, base64.urlsafe_b64encode(b'{}').decode()])
async def test_invalid_cursor_does_not_query_candidates(cursor: str) -> None:
    repository = Repository()
    with pytest.raises(ValueError):
        await RelatedArtworksService(repository).get(uuid4(), None, 20, cursor)
    assert not repository.calls


@pytest.mark.asyncio
async def test_unavailable_source_and_invalid_limits_fail_closed() -> None:
    repository = Repository(); repository.exists = False
    with pytest.raises(WorkNotFoundError):
        await RelatedArtworksService(repository).get(uuid4(), None)
    for limit in [0, 51]:
        with pytest.raises(ValueError):
            await RelatedArtworksService(repository).get(uuid4(), None, limit)
    assert not repository.calls


def test_related_sql_requires_threshold_without_category_fallback_or_ranking_bias() -> None:
    source = (Path(__file__).parents[1] / "src/infrastructure/repositories/related_artworks_repository.py").read_text(encoding="utf-8")
    for fragment in ["w.work_id<>:id", "w.status='published'", "a.account_status='active'", "e.model_name=source.model_name",
                     "where similarity>=0.20", "order by similarity desc, created_at desc, work_id desc",
                     "order by page.similarity desc, page.created_at desc, page.work_id desc",
                     "else null end as similarity", "limit :limit offset :offset", "cast(:viewer as uuid)"]:
        assert fragment in source
    for removed in ["same_type", "source.type_id", "floor(", "tier"]:
        assert removed not in source
    assert "embed_image" not in source


@pytest.mark.asyncio
async def test_no_qualifying_matches_returns_empty_page_without_continuation() -> None:
    repository = Repository()
    repository.rows = []
    page = await RelatedArtworksService(repository).get(uuid4(), None)
    assert page.items == []
    assert page.next_cursor is None
    assert len(repository.calls) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("source_embedding", [True, False])
async def test_query_filters_weak_missing_and_incompatible_vectors_without_category_bias(source_embedding: bool) -> None:
    # Exercise the real relational query offline. Only pgvector's distance operator
    # is replaced with a deterministic SQLite function; this is not a PG integration test.
    engine = create_engine("sqlite://")
    source_id = uuid4()
    strongest, closer_category = uuid4(), uuid4()
    try:
        with engine.connect() as connection:
            raw = connection.connection.driver_connection
            assert raw is not None
            raw.create_function("cosine_distance", 2, lambda candidate, source: float(candidate) if candidate is not None and source is not None else None)
            for statement in [
                "create table works (work_id text, owner_user_id text, type_id text, title text, storage_path text, mime_type text, created_at text, media text, status text)",
                "create table user_accounts (user_id text, account_status text)",
                "create table work_embeddings (work_id text, embedding text, model_name text)",
                "create table work_types (type_id text, name_en text, name_ar text)",
                "create table user_profiles (user_id text, full_name text, avatar_object_path text)",
                "create table work_likes (work_id text, user_id text)",
                "create table work_saves (work_id text, user_id text)",
            ]:
                connection.execute(text(statement))
            owner, same_category, other_category = uuid4(), uuid4(), uuid4()
            connection.execute(text("insert into user_accounts values (:owner, 'active')"), {"owner": str(owner)})
            for category in [same_category, other_category]:
                connection.execute(text("insert into work_types values (:id, 'Art', 'Art')"), {"id": str(category)})
            fixtures = [
                (source_id, same_category, "0", "current", "published"),
                (strongest, other_category, "0.10", "current", "published"),
                (closer_category, same_category, "0.15", "current", "published"),
                (uuid4(), same_category, "0.81", "current", "published"),
                (uuid4(), same_category, None, "current", "published"),
                (uuid4(), same_category, "0.01", "different-model", "published"),
                (uuid4(), same_category, "0.01", "current", "draft"),
            ]
            for work_id, category, distance, model, status in fixtures:
                connection.execute(text("insert into works values (:id,:owner,:category,'Artwork','art.png','image/png','2026-10-01T00:00:00Z',null,:status)"),
                                   {"id": str(work_id), "owner": str(owner), "category": str(category), "status": status})
                if distance is not None and (work_id != source_id or source_embedding):
                    connection.execute(text("insert into work_embeddings values (:id,:distance,:model)"), {"id": str(work_id), "distance": distance, "model": model})

            async def execute(statement: Any, parameters: dict[str, Any]) -> Any:
                sql = str(statement).replace("e.embedding <=> source.embedding", "cosine_distance(e.embedding, source.embedding)")
                # This fixture tests vector eligibility; badge SQL has independent
                # relational coverage in test_work_exhibition_badges.py.
                sql = sql.replace(has_work_exhibition_sql("page.work_id") + " as has_exhibition,", "")
                return connection.execute(text(sql), {key: value.isoformat() if isinstance(value, datetime) else str(value) if isinstance(value, UUID) else value for key, value in parameters.items()})

            session = MagicMock(spec=AsyncSession)
            session.execute = AsyncMock(side_effect=execute)
            storage = MagicMock(spec=SupabaseWorkStorage)
            storage.public_url.return_value = "https://example.com/art.png"
            storage.profile_avatar_url.return_value = None
            repository = SqlAlchemyRelatedArtworksRepository(cast(AsyncSession, session), storage)
            rows = await repository.list_related(source_id, None, datetime.now(UTC), 0, 20)
            assert [item.work_id for item in rows] == ([strongest, closer_category] if source_embedding else [])
    finally:
        engine.dispose()


@pytest.mark.parametrize("status", [200, 400, 404])
def test_related_endpoint_contract_and_personalized_cache_headers(status: int) -> None:
    actor, work_id = uuid4(), uuid4()
    service = AsyncMock()
    service.get.return_value = RelatedArtworksResponse(items=[card()])
    if status == 400:
        service.get.side_effect = ValueError("Invalid related artwork cursor.")
    elif status == 404:
        service.get.side_effect = WorkNotFoundError()
    app = create_app()
    app.dependency_overrides[get_related_artworks_service] = lambda: service
    app.dependency_overrides[get_optional_user] = lambda: actor
    response = TestClient(app).get(f"/api/v1/works/{work_id}/related?limit=4")
    assert response.status_code == status
    service.get.assert_awaited_once_with(work_id, actor, 4, None)
    if status == 200:
        assert response.headers["cache-control"] == "private, no-store"
        assert response.headers["vary"] == "Cookie, Authorization"
        assert len(response.json()["items"]) == 1
    else:
        assert "detail" in response.json()


@pytest.mark.asyncio
@pytest.mark.skipif(os.environ.get("INKFIG_RELATED_DB_TEST") != "1", reason="Opt-in read-only database verification")
async def test_related_query_against_real_database_is_read_only() -> None:
    settings = get_settings()
    if not settings.database_url:
        pytest.skip("Read-only database verification requires a configured DATABASE_URL")
    engine = create_async_engine(settings.database_url)
    try:
        async with engine.connect() as connection:
            transaction = await connection.begin()
            try:
                await connection.execute(text("set transaction read only"))
                work_id = await connection.scalar(text("select w.work_id from works w join user_accounts a on a.user_id=w.owner_user_id where w.status='published' and a.account_status='active' limit 1"))
                if work_id is None:
                    pytest.skip("No published artwork available for read-only verification")
                async with AsyncSession(bind=connection) as session:
                    storage = SupabaseWorkStorage(settings.supabase_url, settings.supabase_secret_key, settings.works_bucket)
                    repository = SqlAlchemyRelatedArtworksRepository(session, storage)
                    assert await repository.available(work_id)
                    rows = await repository.list_related(work_id, None, datetime.now(UTC), 0, 20)
                    assert len(rows) <= 20
                    assert all(item.work_id != work_id for item in rows)
                    assert len({item.work_id for item in rows}) == len(rows)
                    # Independently verify exact threshold/model eligibility and score order.
                    expected = (await connection.execute(text("""
                        select w.work_id, 1-(e.embedding <=> source.embedding) as similarity
                        from works w join user_accounts a on a.user_id=w.owner_user_id
                        join work_embeddings e on e.work_id=w.work_id
                        cross join work_embeddings source
                        where source.work_id=:id and e.model_name=source.model_name
                            and w.work_id<>:id and w.status='published' and a.account_status='active'
                            and 1-(e.embedding <=> source.embedding)>=0.20
                        order by similarity desc, w.created_at desc, w.work_id desc limit 20
                    """), {"id": work_id})).scalars().all()
                    assert [item.work_id for item in rows] == list(expected)
            finally:
                await transaction.rollback()
    finally:
        await engine.dispose()
