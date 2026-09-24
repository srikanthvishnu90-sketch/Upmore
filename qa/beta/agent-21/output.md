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
