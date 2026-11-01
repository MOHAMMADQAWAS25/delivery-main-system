from typing import Protocol
from uuid import UUID

from src.entities.dto.exhibition_ratings import RatingState


class ExhibitionRatingRepository(Protocol):
    async def change(self, exhibition_id: UUID, work_id: UUID, actor: UUID, score: int | None) -> RatingState: ...
