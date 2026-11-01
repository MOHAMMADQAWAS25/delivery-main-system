from uuid import UUID

from src.entities.dto.exhibition_ratings import RatingState
from src.entities.dto.exhibitions import ExhibitionError
from src.entities.repositories.exhibition_ratings import ExhibitionRatingRepository


class ExhibitionRatingService:
    def __init__(self, repository: ExhibitionRatingRepository) -> None:
        self.repository = repository

    async def change(self, exhibition_id: UUID, work_id: UUID, actor: UUID | None, score: int | None) -> RatingState:
        if actor is None:
            raise ExhibitionError(401, "Authentication is required.")
        if score is not None and (type(score) is not int or not 1 <= score <= 5):
            raise ExhibitionError(422, "Choose an integer rating from 1 to 5.")
        return await self.repository.change(exhibition_id, work_id, actor, score)
