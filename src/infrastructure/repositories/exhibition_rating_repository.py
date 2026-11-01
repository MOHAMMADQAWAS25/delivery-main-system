from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.entities.dto.exhibition_ratings import RatingState
from src.entities.dto.exhibitions import ExhibitionError
from src.infrastructure.repositories.exhibition_rating_sql import rating_state_sql


class SqlAlchemyExhibitionRatingRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def change(self, exhibition_id: UUID, work_id: UUID, actor: UUID, score: int | None) -> RatingState:
        params: dict[str, object] = {"exhibition": exhibition_id, "work": work_id, "viewer": actor, "score": score}
        try:
            # Shared locks allow concurrent votes while serializing with existing
            # exhibition edit/review/block/withdrawal operations (FOR UPDATE).
            found = await self.session.scalar(text("select exhibition_id from exhibitions where exhibition_id=:exhibition for share"), params)
            if found is None:
                raise ExhibitionError(404, "Exhibition not found.")
            found = await self.session.scalar(text("""select s.submission_id from exhibition_submissions s
                join works w on w.work_id=s.work_id join user_accounts owner on owner.user_id=w.owner_user_id
                join user_accounts voter on voter.user_id=cast(:viewer as uuid)
                where s.exhibition_id=:exhibition and s.work_id=:work
                for share of s,w,owner,voter"""), params)
            if found is None:
                raise ExhibitionError(404, "Exhibition artwork not found.")
            state = await self._state(params)
            if not state.can_rate:
                raise ExhibitionError(409 if state.unavailable_reason == "closed" else 403, "Voting is closed." if state.unavailable_reason == "closed" else "You cannot rate this exhibition artwork.")
            if score is None:
                await self.session.execute(text("delete from exhibition_ratings where exhibition_id=:exhibition and work_id=:work and user_id=:viewer"), params)
            else:
                await self.session.execute(text("""insert into exhibition_ratings(exhibition_id,work_id,user_id,score)
                    values(:exhibition,:work,:viewer,:score)
                    on conflict(exhibition_id,work_id,user_id) do update set score=excluded.score,updated_at=clock_timestamp()
                    where exhibition_ratings.score is distinct from excluded.score"""), params)
            state = await self._state(params)
            if not state.can_rate:
                raise ExhibitionError(409, "Voting eligibility changed. Please refresh the gallery.")
            await self.session.commit()
            return state
        except Exception:
            await self.session.rollback()
            raise

    async def _state(self, params: dict[str, object]) -> RatingState:
        data = await self.session.scalar(text(f"""select {rating_state_sql()}
            from exhibition_submissions s join exhibitions e on e.exhibition_id=s.exhibition_id
            join works w on w.work_id=s.work_id join user_accounts owner on owner.user_id=w.owner_user_id
            where s.exhibition_id=:exhibition and s.work_id=:work"""), params)
        if data is None:
            raise ExhibitionError(404, "Exhibition artwork not found.")
        return RatingState.model_validate(data)
