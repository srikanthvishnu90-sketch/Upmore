# Beta agent 08 - output (FINAL run, build 2a9d29b, 2026-09-25 — PASS after data-layer fix)

Account: qa08@upmore.app. Fresh-build gate PASS (no History button). Session PASS (qa08@upmore.app). Signed out at end; no test data left. Pre-existing "Reversal: Freelance08 (reversal)" -$40.00 entry left untouched.

## Attempt 1: blocked by product bug (missing save_renewals.amount column) — fixed via ALTER TABLE ... ADD COLUMN amount numeric on the Upmore project; verified via direct API (HTTP 201 insert, 204 delete). No code change; deployed build 2a9d29b unchanged.

## Attempt 2 (solo rerun): ALL PASS
1. Add 2 deadlines — PASS. 'DeadlineTestA' due 2026-09-26 and 'DeadlineTestB' due 2026-09-29 (kind "Bill renewal") both saved with no error banners, no retry needed. Track listed "DeadlineTestA / renewal - in 2 days" and "DeadlineTestB / renewal - in 5 days". (Dates set via per-segment digit key-presses; bulk fill refused on native date segments — tooling limitation.)
2. Expiring-soon queue card — PASS. Up next card for the sooner deadline: "DeadlineTestA", "Renews in 2 days", "Deadline in 2 days - no dollars set, ranked on urgency", "Mark done" button — ranked ahead of DeadlineTestB's "Renews in 5 days" card.
3. Mark Done — PASS. Done on DeadlineTestA's row removed it from Track and the queue; only DeadlineTestB's card remained.
4. Cleanup to empty — PASS. Done on DeadlineTestB → Track "No deadlines tracked - add renewals and claims below.", no deadline cards in queue; empty state persisted across reload. (Only removal path is "Done"/"Mark done" — no separate delete; muddies cancel-vs-complete but achieves removal.)

Minor frictions: due labels are relative-only ("in 2 days", no absolute date for cross-checking).

## Retrospective
Deadlines fulfilled function and intent: add → surface → complete → clear all worked and persisted across reload. The queue proactively surfaced the sooner deadline first with an urgency-ranking note. Serves "stay ahead of upcoming bills without forgetting them" — one-tap completion reflected in both queue and Track.

RESULT: PASS
