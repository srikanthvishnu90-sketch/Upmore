# Beta agent 25 — RUN (build d80a9bd)

Site: https://upmore-srikanthvishnu90-sketchs-projects.vercel.app/
Viewport: 390x844 (phone).
Account: qa25n@upmore.app (disposable QA account; credentials are provided in your task instructions, NOT in this file — never write them anywhere). You will sign OUT first and judge the app as a first-time visitor, then sign back in.

You are beta agent 25. Test BOTH: (1) can it do the function, (2) in retrospect, did it serve the underlying intent?

## Fresh-build protocol (do FIRST)
Load the site, wait 5 seconds, then reload. (Do NOT sign in yet.)

## Scenario: FIRST-TIME INTENT
1. As a signed-out first-time visitor, walk the whole arc: landing/onboarding -> Home queue -> Guide -> You.
   - Is every screen VERY simple (the product bar: "very very very simple")?
   - Is every money claim honest (no promise of money the app can't control; extractable cash only; no "make extra money" guarantees)?
   - Does the arc serve the intent "make my first bit of extra money online" — would a first-timer know what to do in the first 60 seconds?
2. In the Guide, ask one beginner question (e.g. "I want to make my first $20 online today, where do I start?"). Judge: is the answer honest about what's actually achievable today, does it name who pays and how long payout takes?
3. Report a verdict (PASS/FAIL) plus the TOP 3 GAPS, ordered by importance. Be specific: quote the exact copy that is too complex, dishonest, or confusing.
4. Sign in as qa25n@upmore.app. Sanity-check the You tab profile name reads "qa25n" — if it shows any other name, STOP and report SESSION MISMATCH. (Create no test data; nothing to clean up.) Sign out when done.

## Report format
AGENT 25 RESULT: PASS / FAIL
Verdict paragraph, then TOP 3 GAPS (numbered, each with the exact copy quoted).
One-paragraph retrospective: does the first-time arc serve "make my first bit of extra money online"?
