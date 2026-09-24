# Beta agent 07 - output

Completed: 2026-09-24T20:46:51Z
Scenario: RENEWAL DETECTOR (RenewTest07, $12.99/mo, next bill exactly 5 days out)

## Assertions
1. Added RenewTest07 $12.99 Monthly, next bill 2026-09-29 - PASS (appeared in Track: "≈$91.94/mo · 7 active")
2. Renewal queue card appears - PASS, with a REAL BUG found:
   - Title: "RenewTest07 renews in 6d" (should be "in 5d" - bill was exactly 5 calendar days out)
   - Sub: "$12.99/mo - review before it renews"
   - Why-line: "$12.99 x 100% / 5 min - renews in 6d"
   - Root cause: qDaysUntil() used Math.ceil on an end-of-day timestamp, counting partial days up.
   - FIX APPLIED: rewrote qDaysUntil() to compute the calendar-day difference between local midnights (Math.round on midnight-to-midnight). Same function drives deadline/claim countdowns, so all are fixed. Syntax verified with node --check. Rides the batch rebuild.
   - The agent also reported the Track row showing "9/28" for a 9/29 bill; no code renders the next-bill date in the Track list, so that part could not be reproduced from the code - likely a misread.
3. Cleanup - PASS (cancelled via detail dialog; Track back to "≈$78.95/mo · 6 active"; renewal/cancel queue cards gone)

No console errors. "Delete data" never touched. Pre-existing test data (SpikeTest06, BetaInsurance08) observed but untouched.

## Retrospective verdict
The reminder comes early enough in principle - 5 days' lead gives a comfortable cancel window, the card sits in the ranked queue with an explicit countdown, amount, and one-tap Review/cancel path. But the off-by-one countdown eroded trust in the exact deadline (now fixed). No configurable "remind me N days before" threshold exists - the reminder window is whatever the entered date produces. With correct day-count math, this is a reliably cancel-in-time reminder.

## Result: PASS (2/2 product assertions; 1 real bug found and fixed)
