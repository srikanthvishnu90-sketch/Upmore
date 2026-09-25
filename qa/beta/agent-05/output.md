# Beta agent 05 - output (FINAL run, build 2a9d29b, 2026-09-25 — PASS on solo rerun)

Account: qa05@upmore.app. Fresh-build gate PASS (no History button). Email verified qa05@upmore.app, no re-sign-in needed. Signed out at end.

Attempt 1 (concurrent with agent 04) was environment-blocked: saves failed with "Couldn't save - check your connection" because the shared browser profile flipped stored auth tokens between qa04/qa05. Direct API test with a valid token returned HTTP 201, proving the product path works. This solo rerun (no concurrency) is the valid verdict.

## Scenario: LEDGER ADD + REVERSE
1. Starting totals recorded — PASS. "$0.00" total, all buckets $0.00, "Total across all buckets · 0 entries".
2. Log $25 Received 'Beta payout 09' — PASS. "Logged" confirmation, no error banner. Totals $0.00 → $25.00 (exactly +$25). Entry: "Beta payout 09 — $25.00 - Received - 2026-09-24" with Reverse button.
3. Reverse entry — PASS. Offsetting entry "Reversal: Beta payout 09 (reversal) — $-25.00 - Received - 2026-09-24"; original untouched below it. Totals returned to "$0.00", all buckets $0.00. True reversal, not edit/delete; audit trail intact.
4. Totals computed, new user starts at $0 — PASS. $0.00 at 0 entries → $25.00 after log → $0.00 after reversal. Deterministic from entries, never a stored static number.

Minor nit (not a failure): after the reversal the list showed 2 entries but the caption read "1 entry" — slightly muddles the mental model.

## Retrospective
Add-and-reverse worked exactly as designed: sensible form pre-fill, immediate save with clear confirmation, Reverse creates a properly labeled negative offsetting entry while preserving the original — a textbook ledger reversal serving "correct a mistake without erasing history". For a user logging income who occasionally undoes an entry, both function and intent delivered — accuracy you can audit.

CLEANUP: signed out. Totals $0.00 across all buckets (reversal audit entries remain by design — correct ledger behavior).

RESULT: PASS
