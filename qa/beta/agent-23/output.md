# Beta agent 23 - output

## RUN (2026-09-24, build d80a9bd, account qa23n@upmore.app) — RESULT: FAIL (1 gap, since fixed)
Fresh-build protocol PASS (no History button). Profile "qa23n" (no session mismatch).
- Step 1 PASS: added "RenewExact23" $8 Monthly, next bill 2026-09-29 (date spinbuttons needed digit key-presses; fill/type refused). Track showed "≈$8.00/mo · 1 active", "RenewExact23 / $8.00/mo". Cancel sheet confirmed stored date "Next bill: 2026-09-29".
- Step 2 PASS: queue card "Up next" — "RenewExact23 renews in 5 days"; body "$8.00/mo - review before it renews", "$8 x 100% / 5 min - renews in 5 days". Exact wording confirmed. Day math correct; fired inside the 14-day reminder window.
- Step 3 FAIL: Track section showed only name + amount ("≈$8.00/mo · 1 active", "RenewExact23", "$8.00/mo", Cancel) — no countdown, no bill date. The countdown appeared ONLY in the queue card. Underlying data consistent; placement gap: the managed list never shows when money moves.
- Cleanup PASS: cancelled via Track Cancel -> sheet; Guide drafted the confirm-cancellation message; Track empty ("Nothing tracked yet"); money log $0.00; signed out to splash.
FIX (same day): Track subscription rows now render the countdown via qSubDue() — "$8.00/mo · renews in 5 days" (qDueText handles today/overdue). Pending rebuild + redeploy.
Retrospective: the exact countdown serves "never miss a renewal" via the queue, but Track and queue were inconsistent in what they display; now both surface when money moves.

## RERUN — final suite (build 968ece1, 2026-09-25)
Account: qa23n@upmore.app (email-matched gate).
Fresh-build gate: PASS.
1. Added renewal RenewTest23, 2026-09-29 (5 days out), $50 — PASS (minor: Up next card read "no dollars set", amount may not have registered).
2. Track countdown — PASS ("RenewTest23 / renewal - in 5 days", not 4).
3. Home queue card — PASS ("Renews in 5 days", not 4).
4. Guide "when does RenewTest23 renew" — FAIL. Guide deflected to catalog boilerplate, then went silent on two follow-ups. It has no access to tracked deadlines despite "Knows your plan".
RETROSPECTIVE: countdown fix solid on every surface; conversational trust layer missing.
FIX QUEUED (uncommitted, syntax OK): new async trackedAnswer() in the Guide — answers named deadline/renewal/subscription lookups ("when does X renew") and overview queries ("my upcoming deadlines", "my subscriptions", "my money log" incl. live ledger total) from the user's real Supabase rows; signed-out users get a sign-in prompt; catalog questions naming a provider are never hijacked (provider guard).
AGENT 23 FINAL RESULT: FAIL (assertions); fix queued for final build
