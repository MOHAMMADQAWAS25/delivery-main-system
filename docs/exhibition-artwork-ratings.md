# Exhibition artwork ratings

## Model and access

Migration `20261101_018_create_exhibition_ratings.sql` creates the one-vote key
`(exhibition_id,work_id,user_id)`, score1–5 check, voter index, account/composite
submission foreign keys and RLS/service-role-only grants. It grants
`exhibitions.rate` to roles already allowed to like works. No JWT claim refresh
is required for this feature: live database account/role permission is checked.

Voting is allowed only for active, verified, permitted users, on published artwork
by an active owner, in an approved/unblocked submission of a started, not-ended
exhibition. Owner, organizer and exhibition-blocked voters cannot vote. Start is
inclusive; end exclusive. Server statement time decides, never browser/referrer
or client flags. Pending withdrawals remain public/eligible under existing rules.
Past results remain visible. Admin date edits can reopen/close the voting window;
this is not a separate immutable competition-results system.

## API and transactions

`PUT /exhibitions/{id}/works/{workId}/rating` takes only integer `score`.
`DELETE` removes the actor's vote. Session actor is authoritative, never body user
IDs. Response: average, vote_count, my_rating, can_rate, unavailable_reason.
Scores may be changed/removed only while eligible. Shared exhibition/submission/
work/account row locks serialize against existing edits, reviews, blocking,
withdrawals and deactivation without locking all concurrent voters exclusively.
Atomic upsert and unique key prevent duplicate votes; repeated same score does
not rewrite the row. Eligibility is rechecked after mutation/waits; closure or
changed permissions roll back rather than committing an ineligible vote.

Gallery submission responses carry these fields in their existing page query.
Personal gallery/mutation responses are private/no-store with Cookie/Authorization
Vary. No publicly exposed voter list or individual other-user scores.

The gallery-only restriction is enforced in the frontend presentation. A server
cannot prove which page a browser displayed; an authenticated custom client may
call the same endpoint if it meets every server-side eligibility rule. There is
no insecure fromGallery/referrer authorization bypass.

## Totals and visibility

Average/count are derived from stored votes, average rounded only for display.
Zero votes yields null average. Totals exclude inactive/unverified/blocked voters
and artwork owner/organizer. Account reactivation/unblocking restores retained
eligible votes even after closing; historical totals are therefore not frozen.
Changing a vote keeps count constant; removal decreases it. No denormalized
counters to drift, no ratings sorting or automatic winner selection.

Latest publicly eligible exhibition summary is included on card responses using
the existing paginated queries; summaries never merge different exhibitions.
Full artwork detail membership entries include independent totals for each event.
Existing public approval/owner visibility guards remain. Moderation can hide
results; approved withdrawal deletes submission and cascades its ratings. Work,
exhibition or account deletion follows declared foreign-key cascades. No votes
are sent as notifications. Results refresh on reads; no new realtime broadcast.

## Rollout and rollback

Matching branch `feature/exhibition-artwork-ratings` in main-system/user-FE;
user-system unchanged. Baselines backend `7dd7d40`, frontend `ca57072`.
Deploy migration and backend first via existing main workflow, then frontend.
Rollback frontend feature commit first, then backend feature commit if needed.
Keep the rating table/permission rows; do not drop live votes automatically.
Export/reconcile data and obtain explicit approval before any destructive schema
rollback. Reverting application does not require resetting existing artwork data.

Tests cover actual migration DDL/relational predicates adapted to SQLite, route
authentication/validation, upsert/rollback/lock behavior with session doubles,
scope and date boundaries. PostgreSQL concurrent-writer/load/query-plan behavior
is not certified by SQLite/mocks. Production verification is read-only; no real
votes or moderation actions are cast for testing. No new dependency, credential,
import-time client, clock or connection; compatible with existing SnapStart setup.
