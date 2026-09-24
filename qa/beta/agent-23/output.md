# Beta agent 23 - output

## RUN (2026-09-24, build d80a9bd, account qa23n@upmore.app) — RESULT: FAIL (1 gap, since fixed)
Fresh-build protocol PASS (no History button). Profile "qa23n" (no session mismatch).
- Step 1 PASS: added "RenewExact23" $8 Monthly, next bill 2026-09-29 (date spinbuttons needed digit key-presses; fill/type refused). Track showed "≈$8.00/mo · 1 active", "RenewExact23 / $8.00/mo". Cancel sheet confirmed stored date "Next bill: 2026-09-29".
- Step 2 PASS: queue card "Up next" — "RenewExact23 renews in 5 days"; body "$8.00/mo - review before it renews", "$8 x 100% / 5 min - renews in 5 days". Exact wording confirmed. Day math correct; fired inside the 14-day reminder window.
- Step 3 FAIL: Track section showed only name + amount ("≈$8.00/mo · 1 active", "RenewExact23", "$8.00/mo", Cancel) — no countdown, no bill date. The countdown appeared ONLY in the queue card. Underlying data consistent; placement gap: the managed list never shows when money moves.
- Cleanup PASS: cancelled via Track Cancel -> sheet; Guide drafted the confirm-cancellation message; Track empty ("Nothing tracked yet"); money log $0.00; signed out to splash.
FIX (same day): Track subscription rows now render the countdown via qSubDue() — "$8.00/mo · renews in 5 days" (qDueText handles today/overdue). Pending rebuild + redeploy.
Retrospective: the exact countdown serves "never miss a renewal" via the queue, but Track and queue were inconsistent in what they display; now both surface when money moves.
