from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.services.exhibition_rating_service import ExhibitionRatingService
from src.infrastructure.db.postgres.session import get_database_session
from src.infrastructure.repositories.exhibition_rating_repository import SqlAlchemyExhibitionRatingRepository


def get_exhibition_rating_service(session: Annotated[AsyncSession, Depends(get_database_session)]) -> ExhibitionRatingService:
    return ExhibitionRatingService(SqlAlchemyExhibitionRatingRepository(session))
