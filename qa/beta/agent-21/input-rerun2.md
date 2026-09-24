# Beta agent 21 — RERUN (build 6e9bac8)

Site: https://upmore-srikanthvishnu90-sketchs-projects.vercel.app/
Viewport: 390x844 (phone).
Sign in as qa21r@upmore.app (disposable QA account; credentials are provided in your task instructions, NOT in this file — never write them anywhere).

You are beta agent 21. Test BOTH: (1) can it do the function, (2) in retrospect, did it serve the underlying intent?
Clean up ALL test data you create before finishing.

## Fresh-build protocol (do FIRST)
Load the site, wait 5 seconds, then reload. Open the Guide tab and assert there is NO "History" button in the Guide header (stale-build marker — if present, stop and report STALE BUILD).

## Scenario: DUPLICATE EXACT NUMBERS
1. Go to Track. Add subscription: merchant name "DupeExact21", amount $9.99, Monthly. Assert Track shows "~$9.99/mo · 1 active".
2. Add the SAME subscription again ("DupeExact21", $9.99, Monthly). Assert Track shows "~$19.98/mo · 2 active" and two Cancel buttons.
3. Go to Home. Find the duplicate queue card ("Possible duplicate: DupeExact21", sub "2 active charges look like the same subscription").
   - ASSERT the card shows the EXACT figure "$119.88/yr at stake" (x 80% / 3 min) — NOT bare "$120/yr". Exact math: $9.99 x 12 = $119.88/yr per subscription.
   - ASSERT the "Cancel DupeExact21" cards show exact cents ("Keep $119.88/yr"), not rounded "$120/yr".
   - Note: does the card make clear whether "$119.88/yr at stake" is per-subscription or combined ($239.76)? Record the exact wording as an observation (not a failure either way).
4. Tap "Review" on the duplicate card. Record what happens: does it open a detail sheet for ONE subscription, or compare both side-by-side? Record exactly which entry it acts on (observation only).
5. Cleanup: cancel BOTH DupeExact21 subscriptions (Track Cancel buttons). Assert Track returns to empty ("Nothing tracked yet"). Sign out.

IMPORTANT: this browser profile is shared across tests and its stored session can be unreliable. After any sign-in, sanity-check the You tab profile name reads "qa21r". If it shows any other name, STOP and report SESSION MISMATCH.

## Report format
Per step: PASS/FAIL with the exact observed copy. End with:
AGENT 21 RERUN RESULT: PASS / FAIL
One-paragraph retrospective: did duplicate detection + exact numbers serve the intent (catching a user paying twice and showing exactly what's at stake)?
