# Beta agent 11 - output (FINAL run, build 2a9d29b, 2026-09-25)

Account: qa11@upmore.app. Fresh-build gate PASS (no History button). Session PASS (qa11@upmore.app, stable throughout). Signed out at end.

## Scenario: NAVIGATION
1. Home tab — PASS. "Good evening, qa11", "Money score" 30 of 100 ("Early — every bit you learn counts."), plan cards, "Try this today", "What this costs" $0.00, "Your offers" / "No offers yet" / "View all offers".
2. Guide tab — PASS. "Knows your plan", "New chat", "Ask about any move, offer, or step.", "Your plan: Illinois · direct deposit · about an hour a week", quick actions "Sell old clothes online" / "Save more on groceries" / "Earn your first $50", "Message your guide…".
3. You tab — PASS. "You", qa11@upmore.app, "Your money plan" (Illinois, Direct deposit, An hour a week, Making extra money, Complete beginner), "Reset plan", "Sign out".
4. Legacy hashes — PASS. #save, #money, #explore all land on Home. No dead screens.
5. Tab bar exactly 3 tabs — PASS. Counted 3: Home, Guide, You.

Nit: hash fallbacks keep the stale hash in the URL bar (minor, tester-facing only).

## Retrospective
Navigation is sound: every tab renders its screen, the three-tab contract holds, legacy hashes fail safe into Home instead of blank screens. Graceful degradation serves intent — an old bookmark lands somewhere useful rather than lost.

RESULT: PASS
