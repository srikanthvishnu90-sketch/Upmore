# Beta agent 01 - input

Site: https://upmore-srikanthvishnu90-sketchs-projects.vercel.app/
Viewport: 390x844 (phone). Hard-refresh first.
Sign in as demo@upmore.app using the browser's saved login (session may already persist; if signed out, sign in with the saved credentials).
You are beta agent 01. Test BOTH: (1) can it do the function, (2) in retrospect, did it serve the underlying intent?
Clean up any test data you create (cancel test subscriptions, reverse test ledger entries, mark test deadlines done) before finishing.

## Scenario
HOME QUEUE RENDER. On Home assert: exactly one 'Up next' queue section; >=1 queue card; the top card shows an 'Up next' label, a title, a sub-line, a plain-words why-line, and a CTA button; EVERY card carries data-dollar, data-conf, data-urg, data-eff, data-score attributes; document has no horizontal overflow (scrollWidth <= 390). Report PASS/FAIL per assertion.
