import json
from datetime import UTC, datetime
from pathlib import Path
from typing import cast
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.services.exhibition_rating_service import ExhibitionRatingService
from src.entities.dto.exhibition_ratings import RatingInput, RatingState
from src.entities.dto.exhibitions import ExhibitionError
from src.entities.repositories.exhibition_ratings import ExhibitionRatingRepository
from src.infrastructure.repositories.exhibition_rating_repository import SqlAlchemyExhibitionRatingRepository
from src.infrastructure.repositories.exhibition_rating_sql import rating_denial_sql, rating_totals_sql, work_rating_sql
from src.interface.dependencies.authentication import get_optional_user
from src.interface.dependencies.exhibition_ratings import get_exhibition_rating_service
from src.main import create_app


@pytest.mark.parametrize("score", [0, -1, 6, 1.5, "4", True, None])
def test_rating_requires_an_integer_one_to_five(score: object) -> None:
    with pytest.raises(ValidationError):
        RatingInput.model_validate({"score": score})


@pytest.mark.parametrize("score", [1, 2, 3, 4, 5])
def test_valid_stars(score: int) -> None:
    assert RatingInput(score=score).score == score


@pytest.mark.asyncio
async def test_service_authenticates_before_any_rating_query() -> None:
    repository = AsyncMock()
    service = ExhibitionRatingService(cast(ExhibitionRatingRepository, repository))
    with pytest.raises(ExhibitionError) as failure:
        await service.change(uuid4(), uuid4(), None, 4)
    assert failure.value.status == 401
    repository.change.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize("score", [None, 4])
async def test_rating_write_uses_locked_scope_and_returns_authoritative_state(score: int | None, monkeypatch: pytest.MonkeyPatch) -> None:
    session = MagicMock(spec=AsyncSession)
    session.scalar = AsyncMock(side_effect=[uuid4(), uuid4()])
    session.execute, session.commit, session.rollback = AsyncMock(), AsyncMock(), AsyncMock()
    repository = SqlAlchemyExhibitionRatingRepository(cast(AsyncSession, session))
    result = RatingState(average=4, vote_count=1, my_rating=score, can_rate=True)
    monkeypatch.setattr(repository, "_state", AsyncMock(return_value=result))
    exhibition, work, actor = uuid4(), uuid4(), uuid4()
    assert await repository.change(exhibition, work, actor, score) == result
    query, params = session.execute.call_args.args
    assert params["viewer"] == actor and params["exhibition"] == exhibition and params["work"] == work
    if score is None:
        assert "delete from exhibition_ratings" in str(query)
    else:
        assert "on conflict(exhibition_id,work_id,user_id) do update" in str(query)
        assert "is distinct from excluded.score" in str(query)
    assert "for share" in str(session.scalar.call_args_list[0].args[0])
    assert "for share of s,w,owner,voter" in str(session.scalar.call_args_list[1].args[0])
    session.commit.assert_awaited_once()
    session.rollback.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize("reason,status", [("closed",409),("own_work",403),("organizer",403),("restricted",403)])
async def test_denied_votes_never_write(reason: str, status: int, monkeypatch: pytest.MonkeyPatch) -> None:
    session = MagicMock(spec=AsyncSession)
    session.scalar = AsyncMock(side_effect=[uuid4(), uuid4()])
    session.execute, session.commit, session.rollback = AsyncMock(), AsyncMock(), AsyncMock()
    repository = SqlAlchemyExhibitionRatingRepository(cast(AsyncSession, session))
    monkeypatch.setattr(repository, "_state", AsyncMock(return_value=RatingState(unavailable_reason=reason)))
    with pytest.raises(ExhibitionError) as failure:
        await repository.change(uuid4(), uuid4(), uuid4(), 5)
    assert failure.value.status == status
    session.execute.assert_not_awaited(); session.commit.assert_not_awaited(); session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_end_boundary_after_waiting_for_concurrent_vote_rolls_back(monkeypatch: pytest.MonkeyPatch) -> None:
    session = MagicMock(spec=AsyncSession)
    session.scalar = AsyncMock(side_effect=[uuid4(),uuid4()])
    session.execute, session.commit, session.rollback = AsyncMock(), AsyncMock(), AsyncMock()
    repository = SqlAlchemyExhibitionRatingRepository(cast(AsyncSession, session))
    monkeypatch.setattr(repository, "_state", AsyncMock(side_effect=[RatingState(can_rate=True),RatingState(unavailable_reason="closed")]))
    with pytest.raises(ExhibitionError) as failure:
        await repository.change(uuid4(),uuid4(),uuid4(),3)
    assert failure.value.status == 409
    session.commit.assert_not_awaited(); session.rollback.assert_awaited_once()


@pytest.mark.parametrize("method,score,status", [("PUT",4,200),("DELETE",None,200),("PUT",0,422),("PUT",1.5,422)])
def test_rating_endpoints_use_session_actor_and_private_responses(method: str, score: object, status: int) -> None:
    actor, exhibition, work = uuid4(),uuid4(),uuid4()
    repository = AsyncMock()
    repository.change.return_value = RatingState(average=4,vote_count=1,my_rating=4,can_rate=True)
    app = create_app()
    app.dependency_overrides[get_optional_user] = lambda: actor
    app.dependency_overrides[get_exhibition_rating_service] = lambda: ExhibitionRatingService(cast(ExhibitionRatingRepository,repository))
    client = TestClient(app)
    url = f"/api/v1/exhibitions/{exhibition}/works/{work}/rating"
    response = client.put(url,json={"score":score,"user_id":str(uuid4())}) if method == "PUT" else client.delete(url)
    assert response.status_code == status
    if status == 200:
        repository.change.assert_awaited_once_with(exhibition,work,actor,score)
        assert response.headers["cache-control"] == "private, no-store"
        assert response.headers["vary"] == "Cookie, Authorization"
        assert "user_id" not in response.json()
    else:
        repository.change.assert_not_awaited()


def test_anonymous_rating_endpoint_rejects_vote() -> None:
    repository = AsyncMock(); app = create_app()
    app.dependency_overrides[get_optional_user] = lambda: None
    app.dependency_overrides[get_exhibition_rating_service] = lambda: ExhibitionRatingService(cast(ExhibitionRatingRepository,repository))
    response = TestClient(app).put(f"/api/v1/exhibitions/{uuid4()}/works/{uuid4()}/rating",json={"score":5})
    assert response.status_code == 401
    repository.change.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize("found", [[None],[UUID(int=1),None]])
async def test_missing_rating_scope_never_writes(found: list[UUID | None]) -> None:
    session = MagicMock(spec=AsyncSession)
    session.scalar = AsyncMock(side_effect=found)
    session.execute, session.commit, session.rollback = AsyncMock(),AsyncMock(),AsyncMock()
    with pytest.raises(ExhibitionError) as failure:
        await SqlAlchemyExhibitionRatingRepository(cast(AsyncSession,session)).change(uuid4(),uuid4(),uuid4(),5)
    assert failure.value.status == 404
    session.execute.assert_not_awaited(); session.commit.assert_not_awaited(); session.rollback.assert_awaited_once()


def test_relational_rating_uniqueness_counts_visibility_window_and_cascades() -> None:
    # Execute the migration's actual table DDL and production predicates offline.
    # PostgreSQL JSON/time/cast syntax is adapted; this is not a concurrency/PG-plan certification.
    migration = (Path(__file__).parents[1]/"migrations/20261101_018_create_exhibition_ratings.sql").read_text()
    ddl = migration.split("create index")[0].replace("public.","").replace("uuid","text").replace("timestamptz","text").replace("default clock_timestamp()","default CURRENT_TIMESTAMP")
    engine = create_engine("sqlite://")
    try:
        with engine.begin() as db:
            db.execute(text("pragma foreign_keys=on"))
            for statement in [
                "create table user_accounts(user_id text primary key,account_status text,is_active boolean,email_verified_at text)",
                "create table exhibitions(exhibition_id text primary key,creator_user_id text,event_at text,event_ends_at text)",
                "create table works(work_id text primary key,owner_user_id text,status text)",
                "create table exhibition_submissions(exhibition_id text,work_id text,user_id text,status text,unique(exhibition_id,work_id))",
                "create table exhibition_blocks(exhibition_id text,user_id text)",
                "create table user_roles(user_id text,role_code text)",
                "create table role_permissions(role_code text,permission_code text)",
            ]: db.execute(text(statement))
            db.execute(text(ddl))
            for actor in ["owner","organizer","one","two"]:
                db.execute(text("insert into user_accounts values(:id,'active',true,'verified')"),{"id":actor})
                db.execute(text("insert into user_roles values(:id,'user')"),{"id":actor})
            db.execute(text("insert into role_permissions values('user','exhibitions.rate')"))
            db.execute(text("insert into exhibitions values('event','organizer','2026-11-01T10:00:00','2026-11-01T12:00:00')"))
            db.execute(text("insert into works values('art','owner','published')"))
            db.execute(text("insert into exhibition_submissions values('event','art','owner','approved')"))
            upsert = """insert into exhibition_ratings(exhibition_id,work_id,user_id,score) values('event','art',:user,:score)
                on conflict(exhibition_id,work_id,user_id) do update set score=excluded.score"""
            db.execute(text(upsert),{"user":"one","score":3}); db.execute(text(upsert),{"user":"two","score":5})
            totals = rating_totals_sql(":exhibition",":work").replace("jsonb_build_object","json_object").replace("avg(r.score)::numeric","avg(r.score)")
            def summary() -> dict[str, object]:
                return cast(dict[str, object],json.loads(db.scalar(text(f"select {totals}"),{"exhibition":"event","work":"art"}) or "{}"))
            assert summary() == {"average":4.0,"vote_count":2}
            # The actual migration DDL, not just application validation, protects
            # score range, one-vote uniqueness and valid voter references.
            for statement in [
                "insert into exhibition_ratings(exhibition_id,work_id,user_id,score) values('event','art','owner',0)",
                "insert into exhibition_ratings(exhibition_id,work_id,user_id,score) values('event','art','owner',6)",
                "insert into exhibition_ratings(exhibition_id,work_id,user_id,score) values('event','art','one',4)",
                "insert into exhibition_ratings(exhibition_id,work_id,user_id,score) values('event','art','missing',4)",
            ]:
                with pytest.raises(IntegrityError): db.execute(text(statement))
            db.execute(text("insert into exhibitions values('other','organizer','2026-10-01T10:00:00','2026-10-01T12:00:00')"))
            db.execute(text("insert into exhibition_submissions values('other','art','owner','approved')"))
            db.execute(text("insert into exhibition_ratings(exhibition_id,work_id,user_id,score) values('other','art','one',1)"))
            assert summary() == {"average":4.0,"vote_count":2}  # independent exhibition
            db.execute(text(upsert),{"user":"one","score":5}); db.execute(text(upsert),{"user":"one","score":5})
            assert summary() == {"average":5.0,"vote_count":2}
            db.execute(text("update user_accounts set account_status='self_deactivated' where user_id='two'"))
            assert summary()["vote_count"] == 1
            db.execute(text("update user_accounts set account_status='active' where user_id='two'"))
            assert summary()["vote_count"] == 2
            db.execute(text("insert into exhibition_blocks values('event','two')")); assert summary()["vote_count"] == 1
            db.execute(text("delete from exhibition_blocks"))
            denial = rating_denial_sql().replace("cast(:viewer as uuid)",":viewer").replace("statement_timestamp()",":now")
            def reason(viewer: str | None, now: str = "2026-11-01T11:00:00") -> str | None:
                return cast(str | None,db.scalar(text(f"select {denial} from exhibition_submissions s join exhibitions e on e.exhibition_id=s.exhibition_id join works w on w.work_id=s.work_id join user_accounts owner on owner.user_id=w.owner_user_id"),{"viewer":viewer,"now":now}))
            assert reason("one") is None and reason("one","2026-11-01T10:00:00") is None
            assert reason("one","2026-11-01T12:00:00") == "closed"
            assert reason("one","2026-11-01T09:59:59") == "closed"
            assert reason(None) == "signed_out" and reason("owner") == "own_work" and reason("organizer") == "organizer"
            db.execute(text("update user_accounts set email_verified_at=null where user_id='one'")); assert reason("one") == "restricted"
            db.execute(text("update user_accounts set email_verified_at='verified' where user_id='one'"))
            db.execute(text("update user_accounts set account_status='admin_suspended' where user_id='one'")); assert reason("one") == "restricted"
            db.execute(text("update user_accounts set account_status='active' where user_id='one'"))
            db.execute(text("insert into exhibition_blocks values('event','one')")); assert reason("one") == "restricted"
            db.execute(text("delete from exhibition_blocks"))
            db.execute(text("update exhibition_submissions set status='pending'")); assert reason("one") == "restricted"
            db.execute(text("update exhibition_submissions set status='approved'"))
            db.execute(text("delete from exhibition_ratings where user_id='one'")); assert summary()["vote_count"] == 1
            db.execute(text("delete from exhibition_submissions")); assert summary() == {"average":None,"vote_count":0}
    finally:
        engine.dispose()


def test_rating_schema_security_and_latest_scope_are_explicit() -> None:
    migration = (Path(__file__).parents[1]/"migrations/20261101_018_create_exhibition_ratings.sql").read_text()
    for fragment in ["primary key(exhibition_id,work_id,user_id)","score between 1 and 5","on delete cascade","enable row level security","revoke all","service_role"]:
        assert fragment in migration
    sql = work_rating_sql("page.work_id")
    assert "es.work_id=page.work_id" in sql and "order by e.event_at desc,e.exhibition_id limit 1" in sql
    assert "es.status='approved'" in sql and "e.event_at<=now()" in sql
    assert "'name',e.name" in sql


def test_public_rating_summary_keeps_exhibition_name_with_backward_compatibility() -> None:
    from src.entities.dto.exhibition_ratings import WorkRatingSummary
    old = WorkRatingSummary(exhibition_id=UUID(int=1), year=2026)
    assert old.name == ""
    named = WorkRatingSummary(exhibition_id=UUID(int=1), year=2026, name="Student exhibition")
    assert named.model_dump(mode="json")["name"] == "Student exhibition"
