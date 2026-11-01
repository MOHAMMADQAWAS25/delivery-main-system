# Internal SQL expression evaluated only for artworks in the selected page.
# Match the public exhibition gallery: approved entries after the event starts.
# Approved withdrawals delete the submission; pending withdrawals remain public.
def work_exhibitions_sql(work_id: str) -> str:
    if work_id not in {"w.work_id", "page.work_id"}:
        raise ValueError("Unsupported internal work alias")
    return f"""coalesce((
        select jsonb_agg(jsonb_build_object(
            'exhibition_id', e.exhibition_id, 'name', e.name,
            'year', extract(year from e.event_at at time zone 'Asia/Hebron')::int
        ) order by e.event_at desc, e.exhibition_id)
        from exhibition_submissions es
        join exhibitions e on e.exhibition_id=es.exhibition_id
        where es.work_id={work_id} and es.status='approved' and e.event_at<=now()
          and not exists(select 1 from exhibition_blocks eb
                         where eb.exhibition_id=es.exhibition_id and eb.user_id=es.user_id)
    ), '[]'::jsonb)"""


def has_work_exhibition_sql(work_id: str) -> str:
    if work_id not in {"w.work_id", "page.work_id"}:
        raise ValueError("Unsupported internal work alias")
    return f"""exists(select 1 from exhibition_submissions es
        join exhibitions e on e.exhibition_id=es.exhibition_id
        where es.work_id={work_id} and es.status='approved' and e.event_at<=now()
          and not exists(select 1 from exhibition_blocks eb
                         where eb.exhibition_id=es.exhibition_id and eb.user_id=es.user_id))"""
