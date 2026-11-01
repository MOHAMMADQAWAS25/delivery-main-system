from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl, field_validator, model_validator

from src.entities.dto.media import ImageMedia
from src.entities.dto.work_exhibitions import WorkExhibition
from src.entities.dto.exhibition_ratings import WorkRatingSummary


class WorkTypeResponse(BaseModel):
    type_id: UUID
    code: str
    name_en: str
    name_ar: str


class WorkLinkRequest(BaseModel):
    url: HttpUrl
    label: str | None = Field(default=None, max_length=120)


class WorkLinkResponse(BaseModel):
    url: str
    label: str | None = None


class CreateWorkUploadRequest(BaseModel):
    type_id: UUID
    title: str = Field(min_length=1, max_length=160)
    description: str = Field(default="", max_length=2000)
    links: list[WorkLinkRequest] = Field(default_factory=list, max_length=10)
    file_name: str = Field(min_length=1, max_length=255)
    mime_type: str
    file_size: int = Field(gt=0, le=10_485_760)

    @model_validator(mode="after")
    def links_must_be_unique(self) -> "CreateWorkUploadRequest":
        urls = [str(link.url) for link in self.links]
        if len(urls) != len(set(urls)):
            raise ValueError("Work links must be unique.")
        return self


class UpdateWorkRequest(BaseModel):
    type_id: UUID
    title: str = Field(min_length=1, max_length=160)
    description: str = Field(default="", max_length=2000)
    links: list[WorkLinkRequest] = Field(default_factory=list, max_length=10)

    @field_validator("title")
    @classmethod
    def title_must_have_content(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Work title must not be blank.")
        return normalized

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str) -> str:
        return value.strip()

    @model_validator(mode="after")
    def links_must_be_unique(self) -> "UpdateWorkRequest":
        urls = [str(link.url) for link in self.links]
        if len(urls) != len(set(urls)):
            raise ValueError("Work links must be unique.")
        return self


class ModerateWorkDeletionRequest(BaseModel):
    reason: str = Field(min_length=10, max_length=1000)

    @field_validator("reason")
    @classmethod
    def normalize_reason(cls, value: str) -> str:
        normalized = " ".join(value.split())
        if len(normalized) < 10:
            raise ValueError("Deletion reason must contain at least 10 characters.")
        return normalized


class ModeratedWorkTarget(BaseModel):
    work_id: UUID
    owner_user_id: UUID
    type_id: UUID
    title: str
    description: str
    storage_bucket: str
    storage_path: str
    mime_type: str


class WorkUploadResponse(BaseModel):
    work_id: UUID
    object_path: str
    upload_url: str
    upload_token: str


class WorkResponse(BaseModel):
    exhibition_rating: WorkRatingSummary | None = None
    has_exhibition: bool = False
    exhibitions: list[WorkExhibition] = Field(default_factory=list)
    work_id: UUID
    owner_user_id: UUID
    artist_name: str
    artist_avatar_url: str | None = None
    type_id: UUID
    type_name_en: str
    type_name_ar: str
    title: str
    description: str
    links: list[WorkLinkResponse]
    image_url: str
    media: ImageMedia | None = None
    mime_type: str
    like_count: int
    liked_by_me: bool = False
    saved_by_me: bool = False
    created_at: datetime


class WorkFeedResponse(BaseModel):
    items: list[WorkResponse]
    next_cursor: datetime | None = None


class WorkSearchResponse(WorkResponse):
    search_rank: int = Field(ge=1)
    similarity_score: float = Field(ge=-1.0, le=1.0)


class WorkSearchFeedResponse(BaseModel):
    items: list[WorkSearchResponse]
    next_cursor: int | None = Field(default=None, ge=0)
