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
