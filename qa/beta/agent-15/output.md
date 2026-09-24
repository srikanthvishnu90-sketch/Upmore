# Beta agent 15 - output

## Scenario
AUTH STATES. On the You tab sign out. Assert signed-out states render correctly (Track shows a sign-in prompt, ledger shows a sign-in prompt, no crashes). Sign back in; assert data returns.

## FINAL-BUILD run (2026-09-24, build 654ab68)
AGENT: 15 — Auth states. RESULT: PASS (8/8).
- [PASS] Signed in via #login with qa15@upmore.app — redirected to #home; You tab showed "Sign out".
- [PASS] Added test subscription AuthTest15 / $9.99 / Monthly — Track showed "~$9.99/mo · 1 active" with AuthTest15 listed.
- [PASS] Signed out via You tab — redirected to #splash with "Get started"/"Log in".
- [PASS] Signed-out Track renders a proper sign-in prompt ("Stop the leaks, keep the cash", "Sign in with Google to track", privacy note) — not a crash or dead screen.
- [PASS] Signed-out Money log renders a proper sign-in prompt ("Sign in to keep your money log.") — not a crash or dead screen.
- [PASS] Signed-out save attempt NOT silently swallowed: "+ Log a result", $25 + note, "Log it" -> error banner "Couldn't save - check your connection and try again." Nothing persisted (log stayed empty). NOTE: the message misattributes the cause (connection vs. sign-in), but it is not a silent no-op.
- [PASS] Signed back in — redirected to #home; AuthTest15 returned ("~$9.99/mo · 1 active").
- [PASS] Cleanup: cancelled AuthTest15 via "Cancel subscription" — Track shows "Nothing tracked yet"; money log $0.00, no entries. No test data remains.
Retrospective: intent served — signed-out users get explicit sign-in prompts, save attempts surface instead of vanishing, data survives sign-out/sign-in. Friction: (1) the failed-save error blames the connection instead of saying sign-in is required, and the banner persisted/stuck across navigation and even after re-signing in; (2) You tab still shows a "Sign out" button while signed out; (3) profile header shows generic "Friend" even when signed in; (4) "Cancel subscription" routes into Guide chat with a prefilled draft rather than inline removal (draft never sent; subscription was removed from tracking).
Cleanup: done.
FIX (same day, unreleased): (1) save handlers now check sign-in FIRST and show "Sign in to save — your stuff only lives in your account." instead of the connection error; (2) toast banners now auto-dismiss after 4s and clear on navigation; (3) "Sign out" button hidden when signed out; (4) profile header shows the user's actual first name when signed in. Pending rebuild + redeploy, then rerun agent 15's signed-out-save probe.
