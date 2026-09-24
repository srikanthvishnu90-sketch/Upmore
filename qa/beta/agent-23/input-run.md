# Beta agent 23 — RUN (build d80a9bd)

Site: https://upmore-srikanthvishnu90-sketchs-projects.vercel.app/
Viewport: 390x844 (phone).
Sign in as qa23n@upmore.app (disposable QA account; credentials are provided in your task instructions, NOT in this file — never write them anywhere).

You are beta agent 23. Test BOTH: (1) can it do the function, (2) in retrospect, did it serve the underlying intent?
Clean up ALL test data you create before finishing.

## Fresh-build protocol (do FIRST)
Load the site, wait 5 seconds, then reload. Open the Guide tab and assert there is NO "History" button in the Guide header (stale-build marker — if present, stop and report STALE BUILD).

## Scenario: RENEWAL EXACT
1. Go to Track. Add subscription: merchant "RenewExact23", amount $8, Monthly, with next bill date set to exactly 5 days from today (today is 2026-09-24, so 2026-09-29).
2. Go to Home. ASSERT the queue card for RenewExact23 says exactly "renews in 5 days" (exact wording).
3. ASSERT the Track section shows the renewal countdown consistently (same "in 5 days" / equivalent date).
4. Cleanup: cancel RenewExact23 (Track Cancel -> sheet "Cancel subscription"). Assert Track is empty. Sign out.

IMPORTANT: this browser profile is shared across tests and its stored session can be unreliable. After signing in, sanity-check the You tab profile name reads "qa23n". If it shows any other name, STOP and report SESSION MISMATCH.

## Report format
Per step: PASS/FAIL with the exact observed copy. End with:
AGENT 23 RESULT: PASS / FAIL
One-paragraph retrospective: did the exact renewal countdown serve the intent (never missing a renewal / knowing exactly when money moves)?
