from uuid import UUID

from pydantic import BaseModel


class WorkExhibition(BaseModel):
    exhibition_id: UUID
    name: str
    year: int
