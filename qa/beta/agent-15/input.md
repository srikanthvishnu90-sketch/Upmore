# Beta agent 15 - input

Site: https://upmore-srikanthvishnu90-sketchs-projects.vercel.app/
Viewport: 390x844 (phone). Hard-refresh first.
Sign in as demo@upmore.app using the browser's saved login (session may already persist; if signed out, sign in with the saved credentials).
You are beta agent 15. Test BOTH: (1) can it do the function, (2) in retrospect, did it serve the underlying intent?
Clean up any test data you create (cancel test subscriptions, reverse test ledger entries, mark test deadlines done) before finishing.

## Scenario
AUTH STATES. On the You tab sign out. Assert signed-out states render correctly (Track shows a sign-in prompt, ledger shows a sign-in prompt, no crashes). Sign back in as demo@upmore.app; assert data returns.

## RERUN (build dbb4578 — sign-in-aware saves)
Re-test ONLY the signed-out save path: sign out, then attempt to save (subscription add, "+ Log a result" -> "Log it", deadline add). Assert the message now says sign-in is required (e.g. "Sign in to save") — NOT "check your connection". Assert the toast clears when you navigate to another tab. On the You tab while signed out, assert the "Sign out" button is HIDDEN. Sign back in and assert the profile header shows your name/email prefix, not "Friend".
