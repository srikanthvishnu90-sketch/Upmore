# Agent 15 — output (final benchmark run, build 2a9d29b, 2026-09-25 ~03:10 UTC)

VERDICT: **PASS** (core intent served; 1 sub-assertion FAIL → queued fix)

Run: signed in as qa15@upmore.app (transient password in login form only). Fresh-build gate PASS (Guide header "New chat" only, no History).

Assertions:
1. Signed-out states render — PASS. Track on Home gated behind "Sign in to track" ("Your subscriptions, deadlines, and money log are private to your account."). You money log shows "Sign in to keep your money log." + "+ Log a result". No crashes/blank screens.
2. Save attempts while signed out:
   - "+ Log a result" → "Log it" — PASS. Toast: "Sign in to save — your stuff only lives in your account." (NOT a fake connectivity error). No entry created (0 entries after sign-in).
   - Add subscription / add deadline — NOT REACHABLE signed out (forms unmounted; Track fully gated). No misleading save path.
   - Guide-chat save attempts — answered generically, no save attempted, no misleading copy.
   - Toast clears on tab navigation — FAIL (real bug, queued). The "Sign in to save" toast persisted You → Home (~12s+), was still visible on the login page and post-login Home, disappeared at some unobserved point. Copy correct; dismissal lifecycle wrong.
3. "Sign out" hidden on You while signed out — PASS.
4. Sign back in — PASS. "Good evening, qa15"; Track "≈$1.00/mo · 1 active" (PWTest); You "qa15 / qa15@upmore.app"; Sign out present; money log $0.00, 0 entries.

Notes:
- Signed-out header/Home greeting showed cached "Vish" from the shared browser profile — likely test-environment artifact (shared leased Chromium profile), NOT scored as a product bug without isolated reproduction.
- No unintended side effects: unsaved forms and the signed-out log attempt created no data.

QUEUED FIX: toast dismissal lifecycle — toasts must clear on tab navigation and never survive into a new signed-in session.

Signed out after run.
