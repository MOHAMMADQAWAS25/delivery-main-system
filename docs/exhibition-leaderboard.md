# Exhibition leaderboard

Public read-only GET `/api/v1/exhibitions/{id}/leaderboard?limit=20&cursor=0`.
Limit 1–50, offset cursor 0–100000. Missing exhibition returns 404.
Response: exhibition metadata, database `fetched_at`, `started`, `voting_open`,
`total`, ranked `items`, and nullable `next_cursor`. No private voter information
or personal rating is returned. Responses use no-store.

An approved submission is eligible only after its exhibition starts, while its
work is published, its owner and participant are active, and its participant is
not blocked from that exhibition. Ratings join by BOTH exhibition and work.
Only active verified voters, excluding the artwork owner, organizer and blocked
voters, count. The counted-vote predicate is shared with existing artwork totals.
Inner joins to counted votes omit all zero-vote artworks entirely.

The database aggregates every eligible work, ranks by unrounded numeric average
descending and vote count descending, then paginates. Equal average AND count
share competition rank (1,2,3,3,5). Submission creation time then work UUID provide
deterministic presentation order within ties without affecting their rank.
Frontend shows two decimals; ranking never uses rounded display values.

Upcoming events have no standings. Past events retain results but do not become
immutable snapshots: moderation, deactivation and deletions can change results.
One perfect vote may outrank many slightly lower votes; no minimum threshold,
weighted scoring, prizes or automatic winner declaration is implemented.

Each response's totals, ranks, event state and page rows share one SQL statement
snapshot. The metadata read is separate. Pagination is live offset pagination:
new votes between page requests may move works across offsets, causing missing
or repeated entries. The client deduplicates work IDs and offers Refresh to
restart from page one. It does not silently reorder previously loaded pages.
No cross-request frozen snapshot is claimed.

Existing rating/submission indexes are reused. No migration, new permissions,
write endpoint, dependencies, startup connection, import-time clock or SnapStart
state is introduced. No changes to gallery order or rating eligibility.

Deploy main-system before user-FE. Rollback user-FE ticket commit first, then
main-system ticket commit using git revert; preserve feature logs and unrelated
work. No schema or votes need removal. Matching branch: feature/exhibition-leaderboard.
Baselines: backend3162130 and frontend7d0f78a. Exact published hashes in handoff.
