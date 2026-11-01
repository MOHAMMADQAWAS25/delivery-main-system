from uuid import UUID

from pydantic import BaseModel, Field


class RatingInput(BaseModel):
    score: int = Field(strict=True, ge=1, le=5)


class RatingTotals(BaseModel):
    average: float | None = None
    vote_count: int = 0


class RatingState(RatingTotals):
    my_rating: int | None = None
    can_rate: bool = False
    unavailable_reason: str | None = None


class WorkRatingSummary(RatingTotals):
    exhibition_id: UUID
    name: str = ""
    year: int
