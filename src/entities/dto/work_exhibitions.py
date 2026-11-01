from uuid import UUID

from pydantic import BaseModel
from pydantic import Field
from src.entities.dto.exhibition_ratings import RatingTotals


class WorkExhibition(BaseModel):
    rating: RatingTotals = Field(default_factory=RatingTotals)
    exhibition_id: UUID
    name: str
    year: int
