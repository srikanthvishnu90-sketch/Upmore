# Beta agent 14 - output

## Scenario
ONBOARDING. Sign out first (You tab -> Sign out). Then go through the full onboarding: splash -> welcome -> questions -> Home. Assert it completes and lands on Home with the queue rendered. Sign back in afterwards.

## FINAL-BUILD run (2026-09-24, build fac0778)
AGENT: 14 — Onboarding. RESULT: PASS (4/4).
- Signed in as qa14@upmore.app, signed out (You -> Sign out) to clean signed-out state (#splash/#welcome).
- Full onboarding from signed-out: splash ("Get started") -> time question ("About an hour") -> about screen (name "Friend", birthday 01/15/1990, state Illinois) -> situation screen (direct deposit "Yes", cash "Up to $100") -> plan screen -> Home. Home rendered with queue: "Good afternoon, Friend", "Today's queue", cards visible (JM Bullion — Niche Buyback, SoFi Invest — Brokerage account bonus, Microsoft — AI Skills Fest, Robinhood Referral, "Show more (1632 left)").
- Answers reflected: plan screen "Friend, here are your first 3 moves", "Picked for Illinois · a few hours a week"; profile "Friend", "Illinois · about an hour a week". Each move carried a "Why this one" rationale tied to time/budget.
- Signed back in as qa14@upmore.app via #login; landed on #home signed in, queue rendered, profile confirmed on You tab.
Note (non-blocking): after the plan screen, "Save my plan" leads to a #phone screen whose only option is "Continue with Google" (real Google OAuth via Supabase); no skip, no email+password option; note says "You can't switch accounts later." Google OAuth not completed (no credentials; account creation not authorized). Queue/Home remain viewable from the locally saved plan — an account-save gate, not a hard block.
Retrospective: intent well served — ~1 minute through 4 short screens to a personalized plan and 1,632-offer queue, each pick explained. Friction: (1) save-plan is Google-only with no skip/email alternative — may cost users who won't link Google; (2) BUG: after backing out of Google OAuth, "Continue with Google" stuck disabled in "Opening Google…" state with no recovery except reload; (3) label inconsistency — "About an hour" renders as "a few hours a week" (plan) vs "about an hour a week" (profile); (4) router ignores direct address-bar hash navigation (in-app nav fine). None blocked the 60-second path.
Cleanup: done. Signed out; reload rests at #welcome in clean signed-out state. No server-side test data created; qa14's profile/money log ($0.00) untouched — "Delete data" deliberately not used.
Note: mid-run sign-outs from the known localStorage-drop quirk; signed back in and continued.

## RERUN — final suite (build 968ece1, 2026-09-25)
Account: qa14@upmore.app (email-matched gate).
Fresh-build gate: PASS. No test data.
(a) No Referral Bonus leads — PASS (lead: Old National Bank; referrals only in Researched section).
(b) No credit-card/gift-card/points/locked-value leads — PASS (top 3: Old National Bank, BOK Financial, Nymcu — all cash bank bonuses).
(c) Every why-line shows scoring math — PASS (all 9; scores descend 54.4 → 7.8).
Top 3 verbatim: "Old National Bank" "$3500 x 70% / 45 min"; "BOK Financial" "$3000 x 70% / 45 min"; "Nymcu" "$3000 x 70% / 45 min".
RETROSPECTIVE FINDING (real): the "dollars" in the math was the DEPOSIT REQUIREMENT, not the bonus — R0069 scored on $3,500 (deposit) vs the $300 bonus; R0071 on $3,000 vs $450; R0633 on $3,000 vs $150–$350. Catalog data had payout_min/max = deposit figures.
DATA FIX APPLIED (uncommitted): 18 routes corrected to bonus amounts (R0069 300/300, R0071 450/450, R0633 150/350, R0031 100/100, R0569 400/400, R0568 400/400, R0083 400/400, R0639 350/350, R0934 400/400, R0959 300/700, R5785 50/5000, R4644 500/500, R3239 300/300, R0579 100/100, R0096 50/400, R0085 100/100, R0089 100/300, R0032 30/30); stored earn_ratio recomputed with the app's formula. Tiered bonuses verified against full reward text (R0958, R5595, R0945, R0923, R0928, R3825, R0893, R5969, R1002 already correct).
AGENT 14 FINAL RESULT: PASS (assertions); data fix queued for final build
