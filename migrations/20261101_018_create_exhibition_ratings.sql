create table public.exhibition_ratings (
 exhibition_id uuid not null,
 work_id uuid not null,
 user_id uuid not null references public.user_accounts(user_id) on delete cascade,
 score smallint not null check (score between 1 and 5),
 created_at timestamptz not null default clock_timestamp(),
 updated_at timestamptz not null default clock_timestamp(),
 primary key(exhibition_id,work_id,user_id),
 foreign key(exhibition_id,work_id)
   references public.exhibition_submissions(exhibition_id,work_id) on delete cascade
);
create index exhibition_ratings_voter_idx on public.exhibition_ratings(user_id);
insert into public.permissions(code,description) values
 ('exhibitions.rate','Rate approved artwork during an active exhibition') on conflict do nothing;
insert into public.role_permissions(role_code,permission_code)
 select role_code,'exhibitions.rate' from public.role_permissions where permission_code='works.like'
 on conflict do nothing;
alter table public.exhibition_ratings enable row level security;
revoke all on public.exhibition_ratings from anon,authenticated;
grant select,insert,update,delete on public.exhibition_ratings to service_role;
-- No existing records changed. Rollback: revert application first; export votes
-- before any approved table removal. Do not drop voting data automatically.
