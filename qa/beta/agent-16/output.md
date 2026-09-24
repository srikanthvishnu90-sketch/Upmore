# Beta agent 16 - output

## Scenario
RANKING ORDER. On Home read every queue card's data-score attribute. Assert scores are in strictly descending order. Read the top card's why-line; assert it states the ranking math in plain words (dollars x confidence x urgency / effort).

## FINAL-BUILD run (2026-09-24, build 654ab68)
AGENT: 16 — Ranking order. RESULT: FAIL (2 sub-assertions).
- [PASS] All 9 visible "Up next" queue cards carry data-dollar, data-conf, data-urg, data-eff, data-score.
- [PASS] data-score STRICTLY DESCENDING: 1615.38 (JM Bullion — Niche Buyback) > 1166.67 (SoFi Invest — Brokerage bonus) > 1060.61 (Microsoft — Code Bounties) > 1050.00 (Robinhood Referral) > 777.78 (SoFi Invest, claim) > 350.00 (Tradestation — Referral) > 344.62 (National Grid / Mass Save — Utility rebate) > 70.00 (Sunrun, claim) > 54.44 (Old National Bank, claim). All queue cards visible at once (the "Show more (1632 left)" button belongs to the researched-offers list above the queue, not the queue).
- [FAIL] Top card why-line reads "$50000 x 70% / 33 min - pays fast" — states dollars x confidence / effort but NOT the urgency multiplier numerically (data-urg=1.5 rendered only as qualitative "- pays fast", never "x 1.5"). Full formula appears only in the section heading, not the card why-line.
- [PASS] Spot-check SoFi #2: 50000 x 0.7 x 1.5 / 45 = 1166.67, exactly matching data-score. Cards #2-6, #8, #9 (7 of 9) match exactly.
- [FAIL] Spot-check top card: 50000 x 0.7 x 1.5 / 33 = 1590.91 vs data-score 1615.38 (1.54% mismatch, beyond rounding). National Grid shows the identical mismatch factor (computed 339.39 vs 344.62, same 66/65 ratio) — data-eff is rounded to an integer (33) while data-score was computed from the unrounded value (true eff = 32.5). Ranking order unaffected, but attributes inconsistent with the score.
Retrospective: queue is strictly score-ordered, but the top does not serve "fast extra cash" intent — #1 (JM Bullion buyback) needs sellable valuables, pays 1-3 days after verification; #2 (SoFi bonus) needs moving an existing brokerage with a 5-year lock ($0 for ordinary users); #3 (code bounties) needs elite security skills. Formula rewards huge dollar figures over accessibility; genuinely quick no-barrier payouts (e.g. $1,000 Sunrun referral) sit at #8. Worse, data-conf is 0.7 on every card — the confidence factor provides zero discrimination between a near-certain referral and a long-shot bounty. (Same concern raised by agent 01.)
Cleanup: done — no test data created.
Note: one mid-run sign-out from the known localStorage-drop quirk; signed back in and continued.
FIX (same day, unreleased): (1) why-line now renders the urgency multiplier numerically ("$50000 x 70% x 1.5 / 33 min - pays fast"); (2) data-eff now carries the unrounded value used in the score computation (e.g. data-eff="32.5") so attributes reconcile exactly with data-score. Pending rebuild + redeploy, then rerun agent 16.

## RERUN (2026-09-24, build dbb4578 — why-line urgency + data-eff fixes)
AGENT: 16 — Ranking order rerun. RESULT: PASS (5/5).
- [PASS] Top "Up next" card why-line states urgency numerically: "$50000 x 70% x 1.5 / 33 min" (x 1.5 present).
- [PASS] Top card (JM Bullion) math EXACT: 50000 x 0.7 x 1.5 / 32.5 = 1615.3846 -> data-score=1615.38 (diff 0.0046, within 0.01). data-eff is fractional (32.5); the why-line displays "33 min" (rounded display) while the score uses 32.5 as-is.
- [PASS] All 8 visible queue-card scores match dollar x conf x urg / eff within 0.01: 1166.67 (SoFi Invest earn), 1060.61 (Microsoft), 1050.00 (Robinhood), 777.78 (SoFi Invest claim), 344.62 (National Grid), 70.00 (Sunrun), 54.44 (Old National Bank).
- [PASS] data-scores strictly descending: 1615.38 > 1166.67 > 1060.61 > 1050.00 > 777.78 > 344.62 > 70.00 > 54.44.
- [PASS] No "- pays fast" suffix on any visible queue card (intentional).
Retrospective: rerun confirms the deployed fixes — urgency renders as a numeric multiplier, scores compute exactly from the fractional data-eff, ordering strictly descending.
Cleanup: done — no test data created.
