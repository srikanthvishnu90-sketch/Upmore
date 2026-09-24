# Beta agent 20 — RERUN (build 00826d2)

Site: https://upmore-srikanthvishnu90-sketchs-projects.vercel.app/
Viewport: 390x844 (phone).
Sign in as qa20r@upmore.app (disposable QA account; credentials are provided in your task instructions, NOT in this file — never write them anywhere).

You are beta agent 20. Test BOTH: (1) can it do the function, (2) in retrospect, did it serve the underlying intent?
Clean up ALL test data you create (cancel test subscriptions, reverse test ledger entries, mark test deadlines done) before finishing.

## Fresh-build protocol (do FIRST)
1. Load the site, wait 5 seconds, then reload.
2. Open the Guide tab. Assert the Guide header shows ONLY "Knows your plan" and the "New chat" icon — there must be NO "History" button (it was removed; its presence means you have a stale build — stop and report STALE BUILD).

## Scenario: PHONE FIT + write-path regression
At 390px width, visit all 3 tabs (Home, Guide, You).

A. Layout (phone fit):
- Assert NO horizontal page overflow on any tab (document scrollWidth <= 390).
- Offer/promo text must not be clipped at phone width.
- The deadline form's "Kind" select option must fit inside its half-width cell (no clipped text).
- Every visible button must do something (tap queue CTAs, Track add, You controls).
- Every sheet/modal you open must close.

B. Write paths (these FAILED in run 1 on a stale build — verify they now work):
- Track: add a subscription (name "Fit20", $9.99/mo). Assert it appears in Track AND the queue shows the exact yearly value with cents ("$119.88/yr" — NOT "$120/yr", no rounding).
- Track: add a deadline (name "D20", date 2026-10-20, Bill renewal). Assert it appears with exact "renews in 26 days" wording.
- You > Money log: log $20 Received with note "M20". Assert the entry appears and totals show $20.
- Bank sync row: tap "Bank sync — private beta", enter a test email, assert it confirms (waitlist join).
- If any write shows "Couldn't save - check your connection", retry once after 5s; if it persists, report exactly which write failed.

C. Regression checks:
- Guide: start a walkthrough from the queue, advance one step, use "I'm stuck" help, then close it.
- Guide: open a promo sheet; assert the "catches"/requirements render as readable sentences (no bare ", ," comma joins).
- You tab: assert the profile name shows "qa20r" (the account's email prefix) — NOT "Friend", NOT "Vish".
- Export data: tap Export, assert it produces a download/payload.
- Delete data: open the delete sheet, assert the DELETE confirmation gate works (type DELETE to enable), but DO NOT confirm deletion (cancel the sheet).

D. Sign-out / re-sign-in:
- Sign out via You tab. Assert you land on Welcome.
- Sign back in as qa20r@upmore.app. Assert the items from step B survived (Fit20, D20, $20 M20) AND the profile name still shows "qa20r".
- IMPORTANT: this browser profile is shared across tests and its localStorage can be unreliable. After re-sign-in, sanity-check that you are really signed in as qa20r (profile name should read "qa20r"). If the profile shows any other name, STOP and report SESSION MISMATCH instead of continuing.

E. Cleanup:
- Cancel/delete Fit20 and D20. Reverse the $20 M20 entry (if the app offers reversal) or log a -$20 offset; verify Track is empty and money log returns to $0.00.
- Sign out.

## Report format
Per assertion: PASS/FAIL with the exact observed copy. End with:
AGENT 20 RERUN RESULT: PASS / FAIL
One-paragraph retrospective: did the phone-fit + write paths serve the underlying intent (a dead-simple money page that works on a phone)?
