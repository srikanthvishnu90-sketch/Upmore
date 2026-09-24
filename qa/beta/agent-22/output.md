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
