# Beta agent 22 - output

## Scenario
SPIKE EXACT NUMBERS. Add merchant 'SpikeExact22' $10 Monthly; update amount to $15. Assert the spike card shows +$60/yr annualized impact. Then cancel it (cleanup).

## FINAL-BUILD run (2026-09-24, build dbb4578)
AGENT: 22 — Spike exact numbers. RESULT: PASS (5/5).
- [PASS] Signed in as qa22@upmore.app; added SpikeExact22 $10 Monthly — Track showed "~$10.00/mo · 1 active"; queue showed "Cancel SpikeExact22" card with "Keep $120/yr" / "$120/yr x 100% / 5 min".
- [PASS] Edit control exists: the subscription row's "Cancel" button opens a detail sheet with an "Amount" textbox + "Update" button (no standalone edit button on the row; sheet also holds "Cancel subscription" / "Keep it").
- [PASS] After updating to $15: spike card heading "SpikeExact22 bill went up", text "$10.00 -> $15.00/mo (+$60/yr)", ranking line "+$60/yr x 95% / 10 min - price hike you entered". $5/mo x 12 = $60/yr — exact.
- [PASS] Track concurrently updated to "~$15.00/mo · 1 active"; "Cancel SpikeExact22" card updated to "Keep $180/yr" / "$180/yr x 100% / 5 min" — consistent.
- [PASS] Cleanup: "Cancel subscription" in the detail sheet; Track shows "Nothing tracked yet"; spike card gone from queue. Nothing remains.
Retrospective: spike math exact; the card serves intent well — "SpikeExact22 bill went up" with "+$60/yr" and "price hike you entered" ranked in "Up next", directly alerting the user. UX quirk: the edit control is nested behind a row button labeled "Cancel" (which actually opens an edit/cancel detail sheet) — users looking for edit may not discover it.
Cleanup: done.

## RERUN — final suite (build 968ece1, 2026-09-25)
Account: qa22@upmore.app (email-matched gate).
Fresh-build gate: PASS.
Top card: Old National Bank claim card ("Start").
(a) Steps — FAIL. No walkthrough anywhere in the promo flow: Start → detail sheet → "Start promo" → Guide brief → "Open move" dead-ends back to Home. (Lower-ranked cards like Reward XP Games DO have the real "Walk me through it" pattern.)
(b) Completion state — FAIL. "Open move" just navigates to #home.
(c) Queue progress — FAIL. Old National stayed top with unchanged "Start".
(d) Guide continuity — FAIL. "What's my next move" returned Mindswarms with no reference to Old National.
RETROSPECTIVE: the promo flow informs but never converts preparation into action — the highest-expected-value move can't be acted on step-by-step.
FIXES QUEUED (uncommitted, syntax OK):
1. Promo sheet "Start promo" now launches startWalkthrough directly (routes have real steps).
2. Guide "Open move" buttons now launch the walkthrough for step-bearing routes instead of the Home round-trip.
3. New lastRouteId: "what's my next move" now references the engaged move ("You were on Old National Bank — step 2 of 6. After this one: ...").
4. Fully-completed routes are excluded from earn + claim cards (no zombie "Start" after finishing).
AGENT 22 FINAL RESULT: FAIL (assertions); fixes queued for final build
