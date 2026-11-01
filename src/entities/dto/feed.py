from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.entities.dto.media import ImageMedia


@dataclass(frozen=True)
class FeedPosition:
    created_at: datetime
    work_id: UUID


class FeedCardResponse(BaseModel):
    has_exhibition: bool = False
    work_id: UUID
    owner_user_id: UUID
    artist_name: str
    artist_avatar_url: str | None = None
    type_id: UUID
    type_name_en: str
    type_name_ar: str
    title: str
    image_url: str
    media: ImageMedia | None = None
    mime_type: str
    like_count: int
    liked_by_me: bool
    saved_by_me: bool
    created_at: datetime


class InfiniteFeedResponse(BaseModel):
    items: list[FeedCardResponse]
    next_cursor: str | None = Field(default=None, serialization_alias="nextCursor")
    has_next_page: bool = Field(default=False, serialization_alias="hasNextPage")
