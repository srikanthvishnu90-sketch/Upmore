# Agent 13 — Rerun 2: the reserved $1000 flow (2026-09-25)

This flow was explicitly RESERVED by the owner for 2026-09-25 and is now
implemented (build f0653ca). Run 1 (2026-09-24) correctly recorded FAIL as
"expected, not a regression". This rerun verifies the reserved behavior.

Build under test: f0653ca. Production:
https://upmore-srikanthvishnu90-sketchs-projects.vercel.app/
Viewport: 390x844 phone. Signed-out; create no test data; do NOT sign in.

## Fresh-build gate (mandatory, do first)
Load the site, wait 5s, reload, wait 3s. In the Guide tab, ask "what pays
today". The answer MUST contain the exact line "Straight talk: you do the
work first, then the provider pays on the timing above. Nothing here is free
money with no effort." If absent: wait 30s, reload once, re-check. If still
absent, STOP and report STALE BUILD.

## The reserved scenario (do exactly this)
1. Complete the short onboarding as a signed-out beginner (any nickname;
   e.g. cash "$0").
2. Open the Guide tab. Ask: "how do I make $1000 fast?"
   ASSERT ALL:
   a. The FIRST line of the answer is exactly:
      "Straight answer on $1000: no single verified route gets you there fast."
   b. The answer recommends Userfeel (website/app testing, $3–$30 per test)
      with honest timing (about a week after each approved test, to PayPal).
   c. The answer does the honest math (~100 tests = weeks of steady work,
      not a fast payout) and offers a walkthrough ("walk you through step 1"
      or equivalent).
   d. NO promise or implication that any route gets $1,000 fast. NO
      manufactured shortcut, no guaranteed amount on a timeline.
   e. Only extractable cash is counted (no points, credits, discounts).
   Quote the full answer.
3. Reply: "Yes, walk me through step 1"
   ASSERT:
   a. The Guide starts the Userfeel walkthrough (step 1 of the Userfeel
      steps is shown — e.g. signing up / the qualification test).
   b. It does NOT start some other route's walkthrough.
   Quote what the Guide shows.
4. (Robustness, optional if time is short) In a NEW Guide chat, ask
   "how do I make $1000 fast?" again, then reply "no thanks, what is a
   bank bonus?" and then "yes". Assert the stray "yes" does NOT start the
   Userfeel walkthrough (the pending offer must have been cleared).

## Verdict
"AGENT 13 RERUN 2: PASS" if 2a–2e and 3a–3b hold (quote the evidence),
else "AGENT 13 RERUN 2: FAIL" naming the failed assertion with the quote.
