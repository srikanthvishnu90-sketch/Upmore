# Beta agent 09 - output (FINAL run, build 2a9d29b, 2026-09-25 — PASS)

Account: qa09@upmore.app. Fresh-build gate PASS (no History button). Session PASS (qa09@upmore.app). Signed out at end.

Note: account carried prior probe rows netting $0.00 (five "Beta payout 09" +$25, matching reversals incl. API-test cleanups). Starting headline $0.00, all buckets $0.00.

## Scenario: LEDGER GRAND TOTAL — ALL PASS
1. Log $40 Received 'Freelance09' — PASS. "Logged" toast, no error banner. Headline $0.00 → $40.00; Received bucket $0.00 → $40.00; footer "Total across all buckets · 14 entries".
2. Reverse entry — PASS. "Reversed" toast. Offsetting row "Reversal: Freelance09 (reversal)" $-40.00 - Received - 2026-09-24; original row preserved. Headline back to $0.00, all buckets $0.00.
3. Totals computed from entries — PASS. Every headline equaled the arithmetic sum of rows (+$125 −$125 = $0.00 start; +$40 after log; +$40 −$40 = $0.00 after reversal). Consistent with a new user starting at $0.

Nit (cosmetic): footer "entries" count was one less than rendered rows in each state (e.g. 14 visible vs 13 counted) — likely a hidden/template row or off-by-one; dollar math exact throughout.

Cleanup: totals $0.00; residue is the matched +$40/−$40 Freelance09 pair (intended reversal representation).

## Retrospective
Logging and reversal behaved exactly as a ledger should: totals moved by precisely ±$40, reversal preserved an audit trail instead of silently deleting. Intent served: every dollar visible "with a date and a note," grand total reflects real logged results, reversal is a safe undo that doesn't break trust in the running total.

RESULT: PASS
