# Beta agent 08 - output

Completed: 2026-09-24T20:47:25Z
Scenario: DEADLINES AND CLAIMS

## Assertions
1. Added renewal deadline "BetaInsurance08" (Bill renewal, 10/04/2026 = 10 days out) - PASS. Appeared in Track "Deadlines & claims" list and as an "Up next" queue card ("BetaInsurance08 / Renews in 11d / Deadline in 11d - no dollars set, ranked on urgency", "Mark done" button). NOTE: countdown rendered "in 11d" for a 10-day-out date - the same off-by-one bug agent 07 found; already fixed in qDaysUntil (calendar-day difference).
2. Added claim "BetaRebate08" (Claim/rebate, $50, 10/14/2026 = 20 days out) - PASS. Track list: "BetaRebate08 - claim / $50.00 - due - in 21d"; queue card: "BetaRebate08 - claim / due in 21d / $50 x 90% / 15 min - due in 21d", "Mark claimed" button. Same off-by-one note (21d for 20 days) - fixed.
3. Both in list AND queue simultaneously - PASS.
4. Marked both done - PASS. Both disappeared from the list ("No deadlines tracked") and from the queue.

No console errors. No other user data touched; "Delete data" never tapped. Date entry needed visual-automation digit typing (native date input refused direct fill) - test-env quirk, not app bug.

## Retrospective verdict
Manual deadline/claim tracking is a feature users would adopt selectively but abandon as a habit - adding an entry is quick and low-friction, but it demands users remember to input obligations the app could more reliably detect, so maintenance would decay after the first wins. The queue surfacing meaningfully justifies the effort: once an entry exists it becomes a ranked action card competing alongside earning offers ("due in 21d", "$50 x 90% / 15 min"), giving tracking real consequence instead of a digital notebook. Worth shipping as a complement to automated detection, but only maintained if the app nudges at the right moment ("add the renewal date from this bill?").

## Result: PASS (4/4; off-by-one countdown confirmed again, already fixed)

---

## FINAL-BUILD run (2026-09-24T21:11:12Z, on aef5744; 390x844 phone frame)
1. Added renewal "DeadlineTest08" dated 2026-10-04 (exactly 10 days out; date via digit keypresses) - PASS. Queue card "DeadlineTest08 / Renews in 10d / Deadline in 10d"; section "DeadlineTest08 — renewal - in 10d".
2. Added claim "ClaimTest08" deadline 2026-10-14 (exactly 20 days out) - PASS. Queue card "ClaimTest08 - claim / due in 20d"; section "ClaimTest08 - claim — due - in 20d".
3. Exact "in 10d" / "in 20d" - PASS. No off-by-one (9d/11d/19d/21d) in cards or section.
4. Cleanup - PASS (both marked Done; cards gone; section "No deadlines tracked")
## Final-build result: PASS (4/4)
