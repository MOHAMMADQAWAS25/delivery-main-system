def rating_totals_sql(exhibition_id: str, work_id: str) -> str:
    if (exhibition_id, work_id) not in {("e.exhibition_id", "es.work_id"), ("s.exhibition_id", "s.work_id"), (":exhibition", ":work")}:
        raise ValueError("Unsupported rating scope")
    return f"""(select jsonb_build_object(
        'average', round(avg(r.score)::numeric,1), 'vote_count', count(*))
        from exhibition_ratings r
        join user_accounts voter on voter.user_id=r.user_id
        join exhibitions event on event.exhibition_id=r.exhibition_id
        join works artwork on artwork.work_id=r.work_id
        where r.exhibition_id={exhibition_id} and r.work_id={work_id}
          and voter.account_status='active' and voter.is_active=true
          and voter.email_verified_at is not null
          and r.user_id<>artwork.owner_user_id and r.user_id<>event.creator_user_id
          and not exists(select 1 from exhibition_blocks b
                         where b.exhibition_id=r.exhibition_id and b.user_id=r.user_id))"""


def work_rating_sql(work_id: str) -> str:
    if work_id not in {"w.work_id", "page.work_id"}:
        raise ValueError("Unsupported work scope")
    return f"""(select jsonb_build_object(
        'exhibition_id',e.exhibition_id, 'name',e.name,
        'year',extract(year from e.event_at at time zone 'Asia/Hebron')::int
        ) || {rating_totals_sql('e.exhibition_id', 'es.work_id')}
        from exhibition_submissions es join exhibitions e on e.exhibition_id=es.exhibition_id
        where es.work_id={work_id} and es.status='approved' and e.event_at<=now()
          and not exists(select 1 from exhibition_blocks b
                         where b.exhibition_id=es.exhibition_id and b.user_id=es.user_id)
        order by e.event_at desc,e.exhibition_id limit 1)"""


def rating_state_sql() -> str:
    # Gallery and mutation responses share the exact same eligibility expression.
    return f"""{rating_totals_sql('s.exhibition_id', 's.work_id')} || jsonb_build_object(
        'my_rating',(select score from exhibition_ratings r where r.exhibition_id=s.exhibition_id
                     and r.work_id=s.work_id and r.user_id=cast(:viewer as uuid)),
        'can_rate', {rating_denial_sql()} is null,
        'unavailable_reason', {rating_denial_sql()})"""


def rating_denial_sql() -> str:
    return """case
        when cast(:viewer as uuid) is null then 'signed_out'
        when not exists(select 1 from user_accounts voter
            join user_roles role on role.user_id=voter.user_id
            join role_permissions permission on permission.role_code=role.role_code
            where voter.user_id=cast(:viewer as uuid) and voter.account_status='active'
              and voter.is_active=true and voter.email_verified_at is not null
              and permission.permission_code='exhibitions.rate') then 'restricted'
        when not (e.event_at<=statement_timestamp() and statement_timestamp()<e.event_ends_at) then 'closed'
        when w.owner_user_id=cast(:viewer as uuid) then 'own_work'
        when e.creator_user_id=cast(:viewer as uuid) then 'organizer'
        when s.status<>'approved' or w.status<>'published'
          or owner.account_status<>'active' or owner.is_active=false
          or exists(select 1 from exhibition_blocks b where b.exhibition_id=s.exhibition_id
                    and b.user_id in (s.user_id,cast(:viewer as uuid))) then 'restricted'
        else null end"""
