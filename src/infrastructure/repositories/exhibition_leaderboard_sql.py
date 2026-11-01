from src.infrastructure.repositories.exhibition_rating_sql import counted_vote_sql


def leaderboard_sql() -> str:
    # Rank the complete eligible set before limiting. Inner rating join excludes
    # unrated works, including works whose votes all stopped being eligible.
    return f"""
    with scores as (
      select s.work_id, s.created_at, avg(r.score) average, count(*) vote_count
      from exhibition_submissions s
      join exhibitions event on event.exhibition_id=s.exhibition_id
      join works artwork on artwork.work_id=s.work_id
      join user_accounts owner on owner.user_id=artwork.owner_user_id
      join user_accounts participant on participant.user_id=s.user_id
      join exhibition_ratings r on r.exhibition_id=s.exhibition_id and r.work_id=s.work_id
      join user_accounts voter on voter.user_id=r.user_id
      where s.exhibition_id=:id and s.status='approved' and event.event_at<=statement_timestamp()
        and artwork.status='published' and owner.account_status='active' and owner.is_active=true
        and participant.account_status='active' and participant.is_active=true
        and not exists(select 1 from exhibition_blocks b
                       where b.exhibition_id=s.exhibition_id and b.user_id=s.user_id)
        and {counted_vote_sql()}
      group by s.work_id,s.created_at
    ), ranked as (
      select *,rank() over(order by average desc,vote_count desc) rank from scores
    ), page as (
      select * from ranked order by average desc,vote_count desc,created_at,work_id
      limit :limit offset :cursor
    )
    select statement_timestamp() fetched_at,
      e.event_at<=statement_timestamp() started,
      e.event_at<=statement_timestamp() and statement_timestamp()<e.event_ends_at voting_open,
      (select count(*) from ranked) total,
      page.rank,page.work_id,page.average,page.vote_count,w.title,w.storage_path,
      p.full_name artist_name,p.avatar_object_path,
      t.name_en type_name_en,t.name_ar type_name_ar
    from exhibitions e left join page on true
    left join works w on w.work_id=page.work_id
    left join user_profiles p on p.user_id=w.owner_user_id
    left join work_types t on t.type_id=w.type_id
    where e.exhibition_id=:id
    order by page.average desc,page.vote_count desc,page.created_at,page.work_id
    """
