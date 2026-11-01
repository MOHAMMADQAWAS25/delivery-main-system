# Artwork exhibition badges

Work, search, infinite-feed, related-artwork and exhibition-submission responses
include additive `exhibitions: [{exhibition_id, name, year}]` metadata. Empty is `[]`.
No client-supplied badge flag and no database migration. Old clients ignore it.

The shared SQL expression uses existing submission/exhibition indexes and returns
approved submissions whose exhibition has started, excluding blocked participants.
It matches public gallery visibility; future, pending and rejected entries are not
advertised. Past participation remains eligible. Pending withdrawals stay public;
approved withdrawal deletes the submission, removing its badge on subsequent reads.
Deleting an exhibition also removes its metadata through existing cascade behavior.
The event start year uses Asia/Hebron, never the artwork upload/approval date.
Unique exhibition/work constraint prevents duplicate entries. Order: event date
descending, exhibition ID as deterministic tie-breaker. Existing artwork owner
visibility and endpoint authorization remain authoritative.

This metadata is aggregated inside the existing page query, not a per-card network
request or join that multiplies page rows. Feed/related page selection and cursor
semantics are unchanged. No import-time clocks, connections or new SnapStart state.
Badge information follows the application's existing cache refresh behavior, not
a new real-time invalidation channel. Opening artwork details fetches fresh data.

Deploy this backend first, then frontend branch `feature/artwork-exhibition-badges`.
Frontend treats absent metadata as no badge for rollout compatibility. To undo,
revert frontend badge commit first, then this backend ticket commit if needed;
no destructive reset or data rollback. Backend baseline
`653e98969f310f94bd92c72316c32fb228e11296`.

Verification includes relational eligibility fixtures (PostgreSQL JSON/year syntax
adapted for SQLite), single-query feed serialization and existing pagination tests.
No claim of a production PostgreSQL query plan or physical-device certification.
