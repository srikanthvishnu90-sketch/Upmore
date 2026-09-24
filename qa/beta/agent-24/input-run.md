# Beta agent 24 — RUN (build d80a9bd)

Site: https://upmore-srikanthvishnu90-sketchs-projects.vercel.app/
Viewport: 390x844 (phone).
Sign in as qa24n@upmore.app (disposable QA account; credentials are provided in your task instructions, NOT in this file — never write them anywhere).

You are beta agent 24. Test BOTH: (1) can it do the function, (2) in retrospect, did it serve the underlying intent?
Clean up ALL test data you create before finishing.

## Fresh-build protocol (do FIRST)
Load the site, wait 5 seconds, then reload. Open the Guide tab and assert there is NO "History" button in the Guide header (stale-build marker — if present, stop and report STALE BUILD).

## Scenario: LEDGER EXACT
1. Go to the You tab, Money log. Record the STARTING totals exactly (received total, and any other totals shown).
2. Log $100 Received with note "Beta24a". Log $50 Found with note "Beta24b". (Use "+ Log a result" / "Log it".)
3. ASSERT the totals rose by EXACTLY $150 over the starting totals. Quote the exact totals.
4. Reverse the $100 "Beta24a" entry using its Reverse button. (Reversals are offsetting entries — nothing is edited or deleted.)
5. ASSERT the net is now EXACTLY +$50 over the starting totals. Quote the exact totals and confirm the reversal entry appears as an offsetting entry (e.g. "Reversal: Beta24a", -$100).
6. Cleanup: reverse the $50 "Beta24b" entry too, so the log returns to its starting totals. Assert the final totals equal the starting totals. Sign out.

IMPORTANT: this browser profile is shared across tests and its stored session can be unreliable. After signing in, sanity-check the You tab profile name reads "qa24n". If it shows any other name, STOP and report SESSION MISMATCH.

## Report format
Per step: PASS/FAIL with the exact observed figures. End with:
AGENT 24 RESULT: PASS / FAIL
One-paragraph retrospective: does the ledger's exact-cents math + reversal-as-offset (never edit/delete) serve the intent (trustworthy record of money actually earned)?
