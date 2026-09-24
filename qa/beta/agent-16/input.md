# Beta agent 16 - input

Site: https://upmore-srikanthvishnu90-sketchs-projects.vercel.app/
Viewport: 390x844 (phone). Hard-refresh first.
Sign in as demo@upmore.app using the browser's saved login (session may already persist; if signed out, sign in with the saved credentials).
You are beta agent 16. Test BOTH: (1) can it do the function, (2) in retrospect, did it serve the underlying intent?
Clean up any test data you create (cancel test subscriptions, reverse test ledger entries, mark test deadlines done) before finishing.

## Scenario
RANKING ORDER. On Home read every queue card's data-score attribute. Assert scores are in strictly descending order. Read the top card's why-line; assert it states the ranking math in plain words (dollars x confidence x urgency / effort).

## RERUN (build dbb4578 — why-line + data-eff fixes)
Re-test ONLY: (1) the top queue card's why-line must now state the urgency multiplier NUMERICALLY (expect "$50000 x 70% x 1.5 / 33 min - pays fast" style — dollars x confidence% x urgency / effort); (2) spot-check the top card's math with the UNROUNDED data-eff (expect 50000 x 0.7 x 1.5 / 32.5 = 1615.38 exactly matching data-score); (3) confirm scores still strictly descending. Note: cards with speed "days" no longer carry the "- pays fast" suffix — that is intentional.
