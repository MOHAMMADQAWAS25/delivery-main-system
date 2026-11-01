from datetime import UTC, datetime
from typing import cast
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.entities.dto.feed import FeedPosition
from src.infrastructure.integrations.supabase_storage import SupabaseWorkStorage
from src.infrastructure.repositories.work_repository import SqlAlchemyWorkRepository


@pytest.mark.asyncio
async def test_feed_sql_uses_bound_composite_key_and_limits_before_counting() -> None:
    session = MagicMock(spec=AsyncSession)
    result = MagicMock()
    result.mappings.return_value = []
    session.execute = AsyncMock(return_value=result)
    storage = SupabaseWorkStorage("https://storage.test", "unused", "works")
    repository = SqlAlchemyWorkRepository(cast(AsyncSession, session), storage)
    position = FeedPosition(datetime(2026, 10, 11, tzinfo=UTC), UUID(int=3))
    viewer, owner = UUID(int=100), UUID(int=200)
    assert (
        await repository.list_feed_cards(viewer, 21, position, "digital-art", owner)
        == []
    )
    statement, parameters = session.execute.call_args.args
    query = str(statement)
    assert "(w.created_at, w.work_id) < (:created_at, :work_id)" in query
    assert "order by w.created_at desc, w.work_id desc" in query
    assert query.index("limit :limit") < query.index("select count(*)")
    assert "a.account_status = 'active'" in query
    assert "w.status = 'published'" in query
    assert "offset" not in query.lower()
    assert "description" not in query
    assert "work_links" not in query
    assert "p.avatar_object_path as artist_avatar_path" in query
    assert parameters == {
        "viewer": viewer,
        "limit": 21,
        "created_at": position.created_at,
        "work_id": position.work_id,
        "type_code": "digital-art",
        "owner_id": owner,
    }


def test_creator_avatar_urls_preserve_missing_and_encoded_paths() -> None:
    storage = SupabaseWorkStorage("https://storage.test", "unused", "works")
    assert storage.profile_avatar_url(None) is None
    assert storage.profile_avatar_url("user/photo one.jpg") == "https://storage.test/storage/v1/object/public/profile-avatars/user/photo%20one.jpg"


@pytest.mark.asyncio
async def test_feed_serializes_badge_metadata_in_the_same_page_query() -> None:
    session = MagicMock(spec=AsyncSession)
    values = {"work_id": UUID(int=1), "owner_user_id": UUID(int=2), "artist_name": "Artist",
              "type_id": UUID(int=3), "type_name_en": "Art", "type_name_ar": "Art", "title": "Artwork",
              "mime_type": "image/png", "like_count": 0, "liked_by_me": False, "saved_by_me": False,
              "created_at": datetime.now(UTC), "has_exhibition": True}
    row = MagicMock()
    row.items.return_value = values.items()
    row.artist_avatar_path = None
    row.storage_path = "art.png"
    result = MagicMock()
    result.mappings.return_value = [row]
    session.execute = AsyncMock(return_value=result)
    repository = SqlAlchemyWorkRepository(cast(AsyncSession, session), SupabaseWorkStorage("https://storage.test", "unused", "works"))
    cards = await repository.list_feed_cards(None, 20, None, None, None)
    assert cards[0].has_exhibition is True
    assert "exhibitions" not in cards[0].model_dump(mode="json")
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize("detail", [False, True])
async def test_full_exhibition_metadata_is_selected_only_for_single_artwork(detail: bool) -> None:
    session = MagicMock(spec=AsyncSession)
    result = MagicMock()
    result.mappings.return_value = []
    session.execute = AsyncMock(return_value=result)
    repository = SqlAlchemyWorkRepository(cast(AsyncSession, session), SupabaseWorkStorage("https://storage.test", "unused", "works"))
    await repository.list_published(None, 20, None, None, work_id=UUID(int=1) if detail else None)
    statement, _ = session.execute.call_args.args
    query = str(statement)
    assert ("'[]'::jsonb as exhibitions" not in query) == detail
    assert "as has_exhibition" in query
