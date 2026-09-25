# Beta agent 21 - output

## Scenario
DUPLICATE EXACT NUMBERS. Add merchant 'DupeExact21' $9.99 Monthly twice. Assert the duplicate queue card's math: ~$119.88/yr at stake. Then cancel both (cleanup).

## FINAL-BUILD run (2026-09-24, build dbb4578)
AGENT: 21 — Duplicate exact numbers. RESULT: FAIL (1/6 sub-assertions).
- [PASS] Added 'DupeExact21' $9.99 Monthly — Track showed "~$9.99/mo · 1 active".
- [PASS] Added the same subscription again — Track showed "~$19.98/mo · 2 active" with two Cancel buttons.
- [PASS] Duplicate detected: queue card "Possible duplicate: DupeExact21", sub "2 active charges look like the same subscription".
- [FAIL] Duplicate card math: card showed "$120/yr at stake" (x 80% / 3 min). Exact: $9.99 x 12 = $119.88/yr per subscription ($239.76 combined). The card never shows $119.88 (or $239.76) — bare "$120/yr" with no exact figure and no "~" prefix. The "Cancel DupeExact21" cards likewise showed "Keep $120/yr" / "$120/yr". Track monthly used the honest "~" prefix; queue cards did not.
- [PASS] Both subscriptions in the Track list ("~$19.98/mo · 2 active", one "DupeExact21" row "$9.99/mo", two Cancel buttons).
- [PASS] Cleanup: cancelled both (Track row Cancel -> sheet "Cancel subscription" -> Guide chat route); Home shows "Nothing tracked yet".
Retrospective: duplicate detection is clearly labeled, but figures are rounded to whole dollars everywhere on queue cards — $119.88/yr becomes bare "$120/yr" with no exact figure or "~" — and "Review" on the duplicate card opened a detail sheet for just one of the two identical subscriptions rather than both side-by-side (unclear which entry you're acting on). "At stake" is undefined (appears to be one subscription's annual cost, not the combined $239.76), which could mislead about the total.
Cleanup: done — both cancelled; Track empty.
Note: mid-test the known localStorage-drop quirk wiped the session; signed back in and re-ran the full scenario from scratch. Not a product failure.
FIX (same day, unreleased): queue money figures now render exact values via a qMoney() formatter — cents preserved when fractional ("$119.88/yr at stake", "Keep $119.88/yr", "+$60/yr" stays whole), no "~" prefix because nothing is rounded away. Earn-card why-lines and the queue data-dollar attribute also carry exact cents. Pending rebuild + redeploy, then rerun agent 21.

## Rerun 2 (2026-09-24, build 6e9bac8, account qa21r@upmore.app) — RESULT: PASS
Fresh-build protocol PASS (no History button). Profile "qa21r" (no session mismatch).
- Step 1 PASS: "DupeExact21" $9.99 Monthly -> Track "≈$9.99/mo · 1 active".
- Step 2 PASS: added again -> "≈$19.98/mo · 2 active", two Cancel buttons.
- Step 3 PASS: duplicate card "Possible duplicate: DupeExact21" / "2 active charges look like the same subscription" / "$119.88/yr at stake x 80% / 3 min" — EXACT cents, not $120. Both "Cancel DupeExact21" cards: "Keep $119.88/yr", "$119.88/yr x 100% / 5 min".
- Observation: "at stake" figure = sum of EXTRA subscriptions beyond the first (the actual duplicate waste, $119.88), not combined $239.76. Correct math, but wording left it ambiguous. Clarified in code: why-line now reads "$119.88/yr in duplicate charges x 80% / 3 min".
- Step 4 (observation): "Review" opens ONE subscription's detail sheet (acts on g[1]); defensible since cancellation is per-subscription.
- Step 5 PASS: both cancelled via Track Cancel -> sheet "Cancel subscription"; Track empty ("Nothing tracked yet"); duplicate/cancel cards gone; signed out. No test data remains.
- Minor label nit (not failed): Track row "Cancel" opens the detail sheet instead of cancelling directly — a two-tap confirm pattern; the destructive action itself is confirmed in-sheet.
Retrospective: duplicate detection + exact numbers serve the intent — the queue caught the double charge immediately with precise "$119.88/yr" and per-card "Keep $119.88/yr" framing at the decision point.

## RERUN — final suite (build 968ece1, 2026-09-25)
Account: qa21r@upmore.app (email-matched gate).
Fresh-build gate: PASS.
1. First sub — PASS ("≈$9.99/mo · 1 active"). 2. Duplicate added — PASS ("≈$19.98/mo · 2 active", 2 Cancel buttons).
3. Duplicate card — PASS ("Possible duplicate: DupeExact21", "2 active charges look like the same subscription", "$119.88/yr in duplicate charges x 80% / 3 min"; exact cents everywhere, never rounded).
   Observation: "$119.88/yr in duplicate charges" didn't say per-sub vs combined.
4. Review — opened in-page detail sheet for one entry ("DupeExact21 (this one)", "2 charges look like the same subscription — compare:") with per-entry Cancel buttons (observation only).
5. Cleanup — PASS (both cancelled; Track empty; signed out).
FIX QUEUED (uncommitted): duplicate card why-line now reads "$119.88/yr on the extra charge(s) x 80% / 3 min" — explicit that the figure is the redundant charge(s), not the combined total.
RETROSPECTIVE: exact-cent math makes the duplicate alert trustworthy and actionable.
AGENT 21 FINAL RESULT: PASS
