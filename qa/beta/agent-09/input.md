# Beta agent 09 - input

Site: https://upmore-srikanthvishnu90-sketchs-projects.vercel.app/
Viewport: 390x844 (phone). Hard-refresh first.
Sign in as demo@upmore.app using the browser's saved login (session may already persist; if signed out, sign in with the saved credentials).
You are beta agent 09. Test BOTH: (1) can it do the function, (2) in retrospect, did it serve the underlying intent?
Clean up any test data you create (cancel test subscriptions, reverse test ledger entries, mark test deadlines done) before finishing.

## Scenario
LEDGER ADD + REVERSE. On the You tab record the current totals. Log $25 as Received titled 'Beta payout 09'. Assert totals increased by exactly $25. Reverse the entry. Assert totals returned to the starting value. Assert a brand-new user would start at $0 (totals are computed, never a stored static number).
