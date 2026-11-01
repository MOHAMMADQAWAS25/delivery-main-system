from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.entities.dto.exhibitions import Exhibition


class LeaderboardItem(BaseModel):
    rank: int
    work_id: UUID
    title: str
    artist_name: str
    artist_avatar_url: str | None
    image_url: str
    type_name_en: str
    type_name_ar: str
    average: float
    vote_count: int


class ExhibitionLeaderboard(BaseModel):
    exhibition: Exhibition
    fetched_at: datetime
    started: bool
    voting_open: bool
    total: int
    items: list[LeaderboardItem]
    next_cursor: int | None
