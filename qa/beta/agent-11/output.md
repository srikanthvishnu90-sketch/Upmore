# Beta agent 11 - output

## Scenario
NAVIGATION. Tap Home, Guide, You tabs - each renders its screen. Visit the legacy hashes #save, #money, #explore directly - each must land on Home (no dead screens). Assert the tab bar shows exactly 3 tabs: Home, Guide, You.

## FINAL-BUILD run (2026-09-24, build fac0778)
AGENT: 11 — Navigation. RESULT: PASS (8/8).
- Sign-in via #login email+password as qa11@upmore.app succeeded, landed on Home queue.
- Home tab renders the queue ("Good afternoon, Friend", "Up next" ranked offers with "Walk me through it" buttons).
- Guide tab renders the agent/chat ("Ask about any move, offer, or step.", suggested prompts, message box).
- You tab renders the profile (avatar "Friend", Illinois, money log $0.00).
- Legacy #save: cold load redirected #save -> #home, queue rendered. No dead screen.
- Legacy #money: in-session navigation rendered the Home queue (URL stayed #money). No dead screen.
- Legacy #explore: in-session navigation rendered the Home queue; cold load redirected #explore -> #home with full queue. No dead screen.
- Tab bar shows exactly 3 tabs — Home, Guide, You — in that order, verified across all screens.
Retrospective: fully serves intent — three plainly labeled tabs, one tap to each of the only three screens; obsolete deep links degrade gracefully to Home. A non-technical user genuinely cannot get lost. Friction: in-session navigation to #save while signed in changed the URL but left the view on Profile until a reload — the router only normalized legacy hashes on cold load, not on in-page hash changes. FIX APPLIED same day (unreleased): hashchange listener routes external hash changes (address-bar edits, back/forward) through show(), with OAuth-callback guard. Pending rebuild + redeploy.
Cleanup: done — no test data created. (Note: "Beta payout 09 / Reversal" entries seen in the first shared-session view belonged to a pre-existing session, not qa11; left untouched. One reload dropped the session — known localStorage quirk; signed back in.)
