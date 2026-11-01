from sqlalchemy import create_engine, text

from src.infrastructure.repositories.exhibition_leaderboard_sql import leaderboard_sql


def test_leaderboard_ranks_before_pagination_and_excludes_invalid_votes() -> None:
    engine = create_engine("sqlite://")
    with engine.connect() as db:
        driver = db.connection.driver_connection
        assert driver is not None
        driver.create_function("statement_timestamp", 0, lambda: "2026-11-01")
        for ddl in (
            "create table exhibitions(exhibition_id text,creator_user_id text,event_at text,event_ends_at text)",
            "create table works(work_id text,owner_user_id text,status text,title text,storage_path text,type_id text)",
            "create table user_accounts(user_id text,account_status text,is_active bool,email_verified_at text)",
            "create table user_profiles(user_id text,full_name text,avatar_object_path text)",
            "create table work_types(type_id text,name_en text,name_ar text)",
            "create table exhibition_submissions(exhibition_id text,work_id text,user_id text,status text,created_at text)",
            "create table exhibition_ratings(exhibition_id text,work_id text,user_id text,score int)",
            "create table exhibition_blocks(exhibition_id text,user_id text)",
        ):
            db.execute(text(ddl))
        db.execute(text("insert into exhibitions values ('e','organizer','2026-10-01','2026-12-01'),('other','organizer','2026-10-01','2026-12-01')"))
        db.execute(text("insert into work_types values ('art','Art','فن')"))
        for user in ("owner", "organizer", "v1", "v2", "blocked", "inactive", "unverified"):
            db.execute(text("insert into user_accounts values (:u,:status,true,:verified)"), {
                "u": user, "status": "self_deactivated" if user == "inactive" else "active",
                "verified": None if user == "unverified" else "2026-01-01",
            })
        db.execute(text("insert into user_profiles values ('owner','Artist',null)"))
        db.execute(text("insert into exhibition_blocks values ('e','blocked')"))
        for work in ("a", "b", "c", "d", "e", "unrated", "invalid", "rejected", "private"):
            db.execute(text("insert into works values (:w,'owner',:status,:w,:w,'art')"), {"w": work, "status": "draft" if work == "private" else "published"})
            db.execute(text("insert into exhibition_submissions values ('e',:w,'owner',:status,'2026-10-01')"), {"w": work, "status": "rejected" if work == "rejected" else "approved"})
        for work, voter, score in (
            ("a", "v1", 5), ("b", "v1", 5), ("b", "v2", 5),
            ("c", "v1", 4), ("d", "v1", 4), ("e", "v1", 3),
            ("invalid", "owner", 5), ("invalid", "organizer", 5),
            ("invalid", "blocked", 5), ("invalid", "inactive", 5), ("invalid", "unverified", 5),
            ("rejected", "v1", 5), ("private", "v1", 5),
        ):
            db.execute(text("insert into exhibition_ratings values ('e',:w,:v,:score)"), {"w": work, "v": voter, "score": score})
        sql = text(leaderboard_sql().replace("cast(:type_id as uuid)", ":type_id")).bindparams(type_id=None)
        rows = db.execute(sql, {"id": "e", "limit": 2, "cursor": 0}).mappings().all()
        assert [(r["work_id"], r["rank"], r["vote_count"]) for r in rows] == [("b", 1, 2), ("a", 2, 1)]
        assert rows[0]["total"] == 5
        second = db.execute(sql, {"id": "e", "limit": 2, "cursor": 2}).mappings().all()
        assert [(r["work_id"], r["rank"]) for r in second] == [("c", 3), ("d", 3)]
        last = db.execute(sql, {"id": "e", "limit": 2, "cursor": 4}).mappings().one()
        assert last["work_id"] == "e" and last["rank"] == 5
        db.execute(text("insert into work_types values ('second','Second','ثان')"))
        db.execute(text("update works set type_id='second' where work_id in ('c','d','e')"))
        filtered = db.execute(sql, {"id":"e", "type_id":"second", "limit":2, "cursor":0}).mappings().all()
        assert [(r["work_id"], r["rank"]) for r in filtered] == [("c",1),("d",1)]
        assert filtered[0]["total"] == 3
        filtered_next = db.execute(sql, {"id":"e", "type_id":"second", "limit":2, "cursor":2}).mappings().one()
        assert filtered_next["work_id"] == "e" and filtered_next["rank"] == 3
        empty = db.execute(sql, {"id": "other", "limit": 20, "cursor": 0}).mappings().one()
        assert empty["total"] == 0 and empty["work_id"] is None
        db.execute(text("update exhibitions set event_at='2027-01-01' where exhibition_id='e'"))
        upcoming = db.execute(sql, {"id": "e", "limit": 20, "cursor": 0}).mappings().one()
        assert not upcoming["started"] and upcoming["total"] == 0
