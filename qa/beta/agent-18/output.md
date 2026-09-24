# Beta agent 18 - output

## Scenario
INTENT RETROSPECTIVE (queue). Read the top 3 queue cards as a user who wants fast extra cash. Judge in retrospect: do they answer 'what should I do right now'? Give a qualitative verdict and name what would serve the intent better, if anything.

## FINAL-BUILD run (2026-09-24, build 654ab68)
AGENT: 18 — Queue intent retrospective. RESULT: FAIL (qualitative).
Card 1 — "JM Bullion — Niche Buyback". "$50000 x 70% / 33 min - pays fast". Why-line: "Payment is typically issued in 1-3 business days from the time your items have been verified. / Orders are currently being verified and paid 3-7 business days after receipt. · Minutes to hours". CTA "Walk me through it". Verdict [FAIL]: cash-seeker must sell items they likely don't own ("Niche Buyback" is jargon; hidden prerequisite is owning precious metals). The "- pays fast" badge directly contradicts the why-line's "1-3 business days" and "currently 3-7 business days after receipt."
Card 2 — "SoFi Invest — Brokerage account bonus". "$50000 x 70% / 45 min - pays fast". Why-line: "1% ACAT match up to $50,000, no minimum, ends Sept 30, 2026 — requires moving EXISTING brokerage assets; 5-year lock; an ordinary user with no other brokerage earns $0 · Weeks to months". CTA "Walk me through it". Verdict [FAIL]: headline promises $50,000 "pays fast" while the why-line admits an ordinary user earns $0, payment takes "Weeks to months," money locked 5 years. Honest fine print fighting a misleading headline.
Card 3 — "Microsoft — Code Bounties". "$250000 x 70% / 165 min". Why-line: "Earn up to $250,000 USD in bug bounty awards · Weeks to months". CTA "Walk me through it". Verdict [FAIL]: requires elite security-researcher skills with lottery odds and weeks-to-months payout — the opposite of "fast extra cash today."
Retrospective: the top 3 answer "what do I tap" (clear CTAs) but fail "what should I DO right now" — every action demands assets/skills an ordinary user lacks (bullion to sell, a large existing brokerage, zero-day discovery) and none pays today despite "pays fast" badges. The ranking formula surfaces fantasy-maximum payouts ($50k, $250k) rather than realistic fast payouts; two cards badge "pays fast" while their own why-lines admit days-to-months latency. What would serve intent better: rank by realistic expected payout for an ordinary user with no prerequisites; lead with eligibility and payment latency instead of burying them; drop the "pays fast" badge unless money lands within ~24 hours; prefer actionable first steps over skill-gated jackpots.
Cleanup: done — read-only observation; nothing to clean.
FIX (same day, unreleased): narrowed the "- pays fast" badge to only routes whose speed is genuinely same-day (speed === "today"); "days"-speed routes no longer claim fast payout. The deeper ranking question (formula inputs: max-dollar figures, flat 0.7 confidence, prerequisite-blind ordering) is a product-design decision flagged for the owner, not a mechanical bug. Pending rebuild + redeploy, then rerun agent 18.

## RERUN (2026-09-24, build dbb4578 — pays-fast badge narrowed to speed=today)
AGENT: 18 — Badge honesty rerun. RESULT: PASS (3/3).
- [PASS] "JM Bullion — Niche Buyback": "- pays fast" NOT present. Subtext honestly states "Orders are currently being verified and paid 3-7 business days after receipt."
- [PASS] "SoFi Invest — Brokerage account bonus": "- pays fast" NOT present. Subtext honestly states "Weeks to months" + "5-year lock; an ordinary user with no other brokerage earns $0".
- [PASS] "Microsoft — Code Bounties": "- pays fast" NOT present. Subtext honestly states "Weeks to months".
- Full rendered page text searched: the string "pays fast" appears nowhere on the page.
Retrospective: Better. The two problem cards previously implied near-instant payout while actually paying in 3-7 business days / weeks-to-months with a 5-year lock — the mismatch that would burn a cash-seeking user. With the bogus suffix gone and true payout timelines stated plainly, the top 3 set honest expectations without changing the ranking; "what should I do right now" is answered more truthfully than before. (The deeper ranking-formula question — max-dollar figures, flat 0.7 confidence — remains a product-design decision for the owner.)
Cleanup: done — read-only observation; no test data.
