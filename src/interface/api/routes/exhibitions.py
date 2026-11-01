from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response
from src.entities.dto.exhibition_leaderboard import ExhibitionLeaderboard
from src.app.services.exhibition_rating_service import ExhibitionRatingService
from src.entities.dto.exhibition_ratings import RatingInput, RatingState
from src.interface.dependencies.exhibition_ratings import get_exhibition_rating_service

from src.app.services.exhibition_service import ExhibitionService
from src.entities.dto.exhibitions import (
    BannerCompleteInput,
    BannerUploadInput,
    BlockInput,
    Exhibition,
    ExhibitionInput,
    ExhibitionPage,
    ReviewInput,
    SubmissionInput,
    SubmissionPage,
    WithdrawalInput,
)
from src.interface.dependencies.authentication import get_optional_user
from src.interface.dependencies.exhibitions import get_exhibition_service

router = APIRouter(prefix="/exhibitions", tags=["exhibitions"])
Service = Annotated[ExhibitionService, Depends(get_exhibition_service)]
Actor = Annotated[UUID | None, Depends(get_optional_user)]


@router.get("/{exhibition_id}/leaderboard", response_model=ExhibitionLeaderboard)
async def leaderboard(
    exhibition_id: UUID, service: Service, response: Response,
    limit: int = Query(20, ge=1, le=50),
    cursor: int = Query(0, ge=0, le=100000),
) -> ExhibitionLeaderboard:
    response.headers["Cache-Control"] = "no-store"
    return await service.leaderboard(exhibition_id, limit, cursor)


@router.get("", response_model=ExhibitionPage)
async def list_exhibitions(
    service: Service,
    limit: int = Query(20, ge=1, le=50),
    cursor: int = Query(0, ge=0, le=100000),
    period: Literal["all", "current", "upcoming", "past"] = "all",
) -> ExhibitionPage:
    return await service.list(limit, cursor, period)


@router.get("/eligible", response_model=ExhibitionPage)
async def eligible_exhibitions(
    service: Service,
    actor: Actor,
    limit: int = Query(20, ge=1, le=50),
    cursor: int = Query(0, ge=0, le=100000),
    work_id: UUID | None = None,
    exhibition_id: UUID | None = None,
) -> ExhibitionPage:
    return await service.eligible(actor, limit, cursor, work_id, exhibition_id)


@router.post("", response_model=Exhibition, status_code=201)
async def create_exhibition(
    data: ExhibitionInput, service: Service, actor: Actor
) -> Exhibition:
    return await service.save(actor, data)


@router.get("/pending-counts")
async def pending_counts(service: Service, actor: Actor) -> dict[str, object]:
    return await service.pending_counts(actor)


@router.get("/{exhibition_id}", response_model=Exhibition)
async def get_exhibition(exhibition_id: UUID, service: Service) -> Exhibition:
    return await service.get(exhibition_id)


@router.put("/{exhibition_id}", response_model=Exhibition)
async def edit_exhibition(
    exhibition_id: UUID, data: ExhibitionInput, service: Service, actor: Actor
) -> Exhibition:
    return await service.save(actor, data, exhibition_id)


@router.post("/{exhibition_id}/submissions", status_code=204)
async def submit(
    exhibition_id: UUID, data: SubmissionInput, service: Service, actor: Actor
) -> None:
    await service.submit(actor, exhibition_id, data.work_id)


@router.delete("/{exhibition_id}", status_code=204)
async def delete_exhibition(
    exhibition_id: UUID, service: Service, actor: Actor
) -> None:
    await service.delete(actor, exhibition_id)


@router.get("/{exhibition_id}/submissions", response_model=SubmissionPage)
async def submissions(
    response: Response,
    exhibition_id: UUID,
    service: Service,
    actor: Actor,
    scope: Literal["public", "mine", "manage"] = "public",
    status: Literal["pending", "approved", "rejected"] | None = None,
    limit: int = Query(20, ge=1, le=50),
    cursor: int = Query(0, ge=0, le=100000),
) -> SubmissionPage:
    response.headers["Cache-Control"] = "private, no-store"
    response.headers["Vary"] = "Cookie, Authorization"
    return await service.submissions(actor, exhibition_id, scope, limit, cursor, status)


@router.put("/{exhibition_id}/works/{work_id}/rating", response_model=RatingState)
async def rate_artwork(exhibition_id: UUID, work_id: UUID, data: RatingInput, actor: Actor,
                       service: Annotated[ExhibitionRatingService, Depends(get_exhibition_rating_service)], response: Response) -> RatingState:
    response.headers["Cache-Control"] = "private, no-store"
    response.headers["Vary"] = "Cookie, Authorization"
    return await service.change(exhibition_id, work_id, actor, data.score)


@router.delete("/{exhibition_id}/works/{work_id}/rating", response_model=RatingState)
async def remove_artwork_rating(exhibition_id: UUID, work_id: UUID, actor: Actor,
                               service: Annotated[ExhibitionRatingService, Depends(get_exhibition_rating_service)], response: Response) -> RatingState:
    response.headers["Cache-Control"] = "private, no-store"
    response.headers["Vary"] = "Cookie, Authorization"
    return await service.change(exhibition_id, work_id, actor, None)


@router.patch("/{exhibition_id}/submissions/{submission_id}", status_code=204)
async def review(
    exhibition_id: UUID,
    submission_id: UUID,
    data: ReviewInput,
    service: Service,
    actor: Actor,
) -> None:
    await service.review(actor, exhibition_id, submission_id, data)


@router.put("/{exhibition_id}/blocks/{user_id}", status_code=204)
async def block(
    exhibition_id: UUID, user_id: UUID, data: BlockInput, service: Service, actor: Actor
) -> None:
    await service.block(actor, exhibition_id, user_id, data.reason)


@router.post("/{exhibition_id}/submissions/{submission_id}/withdrawal", status_code=204)
async def withdraw(
    exhibition_id: UUID,
    submission_id: UUID,
    data: WithdrawalInput,
    service: Service,
    actor: Actor,
) -> None:
    await service.withdraw(actor, exhibition_id, submission_id, data.reason)


@router.patch(
    "/{exhibition_id}/submissions/{submission_id}/withdrawal", status_code=204
)
async def review_withdrawal(
    exhibition_id: UUID,
    submission_id: UUID,
    data: ReviewInput,
    service: Service,
    actor: Actor,
) -> None:
    await service.review_withdrawal(actor, exhibition_id, submission_id, data)


@router.delete("/{exhibition_id}/blocks/{user_id}", status_code=204)
async def unblock(
    exhibition_id: UUID, user_id: UUID, service: Service, actor: Actor
) -> None:
    await service.block(actor, exhibition_id, user_id, None)


@router.get("/{exhibition_id}/blocks")
async def blocks(
    exhibition_id: UUID,
    service: Service,
    actor: Actor,
    limit: int = Query(20, ge=1, le=50),
    cursor: int = Query(0, ge=0, le=100000),
) -> dict[str, object]:
    return await service.blocks(actor, exhibition_id, limit, cursor)


@router.post("/{exhibition_id}/banner-uploads")
async def prepare_banner(
    exhibition_id: UUID, data: BannerUploadInput, service: Service, actor: Actor
) -> dict[str, str]:
    return await service.prepare_banner(actor, exhibition_id, data)


@router.post("/{exhibition_id}/banner-uploads/complete", status_code=204)
async def complete_banner(
    exhibition_id: UUID, data: BannerCompleteInput, service: Service, actor: Actor
) -> None:
    await service.complete_banner(actor, exhibition_id, data.object_path)
