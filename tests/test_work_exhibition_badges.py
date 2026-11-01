import json
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text

from src.infrastructure.repositories.work_exhibition_sql import work_exhibitions_sql, has_work_exhibition_sql


def test_public_badge_sql_filters_and_aliases() -> None:
    sql = work_exhibitions_sql("page.work_id")
    assert "es.work_id=page.work_id" in sql
    assert "es.status='approved'" in sql
    assert "e.event_at<=now()" in sql
    assert "exhibition_blocks" in sql
    assert "at time zone 'Asia/Hebron'" in sql
    assert "order by e.event_at desc, e.exhibition_id" in sql
    assert "event_ends_at" not in sql  # past participation retains its badge
    with pytest.raises(ValueError):
        work_exhibitions_sql("untrusted")


def test_badge_eligibility_uses_relational_data_not_client_flags() -> None:
    # SQLite adaptation changes only PostgreSQL JSON/year/time syntax; retain
    # the production joins, approval/start/blocked predicates and work scope.
    sql = work_exhibitions_sql("w.work_id").replace("jsonb_agg", "json_group_array").replace("jsonb_build_object", "json_object")
    sql = sql.replace("extract(year from e.event_at at time zone 'Asia/Hebron')::int", "cast(strftime('%Y',e.event_at) as integer)")
    sql = sql.replace(" order by e.event_at desc, e.exhibition_id", "").replace("'[]'::jsonb", "'[]'").replace("now()", "'2026-11-01'")
    flag_sql = has_work_exhibition_sql("w.work_id").replace("now()", "'2026-11-01'")
    engine = create_engine("sqlite://")
    try:
        with engine.begin() as connection:
            connection.execute(text("create table works(work_id text)"))
            connection.execute(text("create table exhibitions(exhibition_id text,name text,event_at text)"))
            connection.execute(text("create table exhibition_submissions(exhibition_id text,work_id text,user_id text,status text)"))
            connection.execute(text("create table exhibition_blocks(exhibition_id text,user_id text)"))
            connection.execute(text("insert into works values('art')"))
            for identifier, date, status, owner in [
                ("past", "2025-01-01", "approved", "artist"),
                ("current", "2026-10-31", "approved", "artist"),
                ("future", "2027-01-01", "approved", "artist"),
                ("pending", "2026-01-01", "pending", "artist"),
                ("rejected", "2026-01-01", "rejected", "artist"),
                ("blocked", "2026-01-01", "approved", "artist"),
            ]:
                connection.execute(text("insert into exhibitions values(:id,:id,:date)"), {"id": identifier, "date": date})
                connection.execute(text("insert into exhibition_submissions values(:id,'art',:owner,:status)"), {"id": identifier, "owner": owner, "status": status})
            connection.execute(text("insert into exhibition_blocks values('blocked','artist')"))
            result = json.loads(connection.scalar(text(f"select {sql} from works w")) or "[]")
            assert {(row["exhibition_id"], row["year"]) for row in result} == {("past", 2025), ("current", 2026)}
            assert connection.scalar(text(f"select {flag_sql} from works w")) == 1
            connection.execute(text("delete from exhibition_submissions where exhibition_id='current'"))
            assert len(json.loads(connection.scalar(text(f"select {sql} from works w")) or "[]")) == 1
            connection.execute(text("delete from exhibition_submissions where exhibition_id='past'"))
            assert connection.scalar(text(f"select {flag_sql} from works w")) == 0
    finally:
        engine.dispose()


def test_all_artwork_queries_include_badge_data_without_per_card_requests() -> None:
    root = Path(__file__).parents[1] / "src/infrastructure/repositories"
    works = (root / "work_repository.py").read_text(encoding="utf-8")
    assert 'work_exhibitions_sql("w.work_id") if work_id is not None' in works
    assert 'has_work_exhibition_sql("page.work_id")' in works
    assert 'has_work_exhibition_sql("page.work_id")' in (root / "related_artworks_repository.py").read_text(encoding="utf-8")
    assert "as exhibitions" not in (root / "exhibition_repository.py").read_text(encoding="utf-8")
