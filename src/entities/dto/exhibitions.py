from datetime import datetime, timedelta
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator


class ExhibitionInput(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    description: str = Field(min_length=1, max_length=5000)
    event_at: datetime
    event_ends_at: datetime | None = None
    participation_opens_at: datetime
    participation_closes_at: datetime

    @field_validator("name", "description")
    @classmethod
    def nonblank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field is required.")
        return value

    @model_validator(mode="after")
    def dates(self) -> "ExhibitionInput":
        if self.event_ends_at is None:
            self.event_ends_at = self.event_at + timedelta(hours=24)
        values = (
            self.event_at,
            self.event_ends_at,
            self.participation_opens_at,
            self.participation_closes_at,
        )
        if any(value.tzinfo is None or value.utcoffset() is None for value in values):
            raise ValueError("Dates must include a timezone.")
        if self.event_ends_at <= self.event_at:
            raise ValueError("The exhibition must end after it starts.")
        if (
            not self.participation_opens_at
            < self.participation_closes_at
            <= self.event_at
        ):
            raise ValueError(
                "Participation must open before closing and close by the event date."
            )
        return self


class Exhibition(ExhibitionInput):
    exhibition_id: UUID
    creator_user_id: UUID
    banner_url: str | None = None
    created_at: datetime
    participation_open: bool = False


class ExhibitionPage(BaseModel):
    items: list[Exhibition]
    next_cursor: int | None = None


class SubmissionInput(BaseModel):
    work_id: UUID


class WithdrawalInput(BaseModel):
    reason: str | None = Field(default=None, max_length=2000)

    @field_validator("reason")
    @classmethod
    def trim_reason(cls, value: str | None) -> str | None:
        return value.strip() or None if value else None


class ReviewInput(BaseModel):
    status: Literal["approved", "rejected"]
    reason: str | None = Field(default=None, max_length=2000)

    @model_validator(mode="after")
    def rejection_reason(self) -> "ReviewInput":
        self.reason = self.reason.strip() if self.reason else None
        if self.status == "rejected" and not self.reason:
            raise ValueError("A rejection reason is required.")
        return self


class BlockInput(BaseModel):
    reason: str = Field(min_length=1, max_length=2000)

    @field_validator("reason")
    @classmethod
    def nonblank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("A blocking reason is required.")
        return value.strip()


class Submission(BaseModel):
    submission_id: UUID
    work_id: UUID
    user_id: UUID
    artist_name: str
    artist_avatar_url: str | None = None
    title: str
    description: str = ""
    type_name_en: str = ""
    type_name_ar: str = ""
    image_url: str
    status: str
    rejection_reason: str | None
    created_at: datetime
    withdrawal_status: str | None = None
    withdrawal_reason: str | None = None
    withdrawal_requested_at: datetime | None = None
    withdrawal_review_reason: str | None = None


class SubmissionPage(BaseModel):
    items: list[Submission]
    next_cursor: int | None = None


class BannerUploadInput(BaseModel):
    mime_type: Literal["image/jpeg", "image/png", "image/webp"]
    file_size: int = Field(gt=0, le=10_485_760)


class BannerCompleteInput(BaseModel):
    object_path: str = Field(min_length=1, max_length=512)


class ExhibitionError(Exception):
    def __init__(self, status: int, detail: str) -> None:
        self.status, self.detail = status, detail
        super().__init__(detail)
