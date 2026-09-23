# Evidence schema + rules for the Upmore 1500 expansion (R0851+)

Work directory: `~/workspace/upmore`. Write evidence ONLY. Never touch the DB, never commit.

## File format
One JSON file per candidate: `qa/verification/R0851.json`, `R0852.json`, … (your assigned block only).
Use `browser.search` to discover, `browser.open` to fetch pages. You may only verify against the
PROVIDER'S OWN official terms page (their domain). Aggregator pages (doctorofcredit, nerdwallet,
bankrate, thepointsguy, reddit, etc.) are discovery leads only — never evidence.

## The 17 canonical keys (exact names) + 6 numeric keys = 23 keys total

Canonical 17: `route_id`, `verdict` ("verify" or "reject"), `official_url`, `terms_url`,
`payout_quote` (verbatim quote from official terms; null for rejects), `steps` (array of concrete
strings; [] for rejects), `catches` (array of strings), `biggest_catch` (string), `eligibility`
(string), `timing` (string), `upfront_fee` (bool), `weasel_words` (array), `app_links`
({android, ios}), `checked_at` (UTC ISO), `critical` ({c1..c4: {pass, evidence}}),
`standard` ({s1..s7: {pass, note}}), `notes` (string).

Numeric 6 (REQUIRED on every verify file):
- `payout_min_usd`, `payout_max_usd`: numbers, USD cash value of the payout. Points/miles/gift
  cards → cash ONLY via the provider's own stated redemption value (e.g. "points worth 1¢ each
  toward travel"); record the conversion in `payout_value_note`. If the official terms state a range
  ($300–$500) use it. If "up to $X" with no floor, payout_min_usd = 0. If variable (gig work),
  use the official stated per-unit or per-hour range.
- `payout_value_note`: string, one line explaining any conversion or what the numbers mean.
- `time_min_minutes`, `time_max_minutes`: numbers = estimated ACTIVE minutes a typical person
  spends to earn that payout (signup forms, applications, the survey itself, the donation visit —
  NOT the weeks of waiting for payout). Estimate honestly from the steps; never 0 (min 1).
- `numeric_basis`: string, one line, e.g. "payout from official terms ($400 flat); time: online
  application + DD setup est. 30–60 min active".

Time-estimation guide (active minutes, adjust from the actual steps when evidence says otherwise):
bank/brokerage signup 30–60 · credit-card application 20–40 · insurance quote 10–20 ·
survey: stated minutes else 10–20 · focus group: 10–15 screener + stated session (60–120) ·
mock jury: stated case length (60–240) · microtask: stated task minutes · transcription: 30–60 per
typical assignment · referral share 5–15 · rebate application 15–30 · plasma: per-visit ~90–150
× number of visits the payout requires · clinical trial: stated visit hours · buyback 15–30 ·
mystery shop 30–90 + report · tutoring/gig: 60 per hour of work · jury duty: 480/day ·
car-wrap: 30–60 setup.

## Counting rules (non-negotiable)
- Count ONLY distinct earning mechanisms backed by current official-provider evidence.
- One provider × one distinct product/mechanism = one route. Same provider's checking bonus vs
  savings bonus = distinct. Same bonus, different landing URL = duplicate.
- REJECT: dead/expired programs, aggregator-only terms, sub-features of existing routes
  (e.g. "Fetch daily receipt" under Fetch), anything requiring upfront spending or risk capital
  (crypto rebates, pay-to-play, pay-to-apply), prediction markets, MLM, academic misconduct.
- Dedupe against existing catalog BEFORE writing: `grep -i "<provider>" qa/existing-providers.txt`
  and `python3 qa/dedupe-check.py "<provider name>"`. Also glob qa/verification/R*.json for the
  same provider. When in doubt, reject as duplicate.

## Honesty posture (every file)
- Never promise beyond exact conditional terms. "Guaranteed" only conditional on eligibility +
  exact completion.
- Credit cards: catches must include never-spend-extra-to-chase, annual-fee net math, hard
  inquiry, ~20%+ APR wipes the bonus if a balance is carried.
- Rebates/discounts: framed as SAVINGS on planned spending, not income.
- Variable work (gig, tutoring, POD, transcription piece rates): labeled variable, never fixed.
- Plasma/clinical: include the medical-screening disclosure (must pass health screening; not
  everyone qualifies; physical time/effort involved).
- Unclaimed property: recovers the user's OWN money; promise no payout.
- Points/miles: never present at inflated transfer-partner values; use provider's own
  redemption value.

## Rejects
For every rejected candidate, append ONE line to `qa/discovery/rejects-<yourgroup>.txt`:
`R####|Provider Name|2026-09-24T00:00:00Z|https://source-url-or-empty|one-line reason`
(Use real UTC time in checked_at. Do NOT write a JSON file for rejects.)

## Report back
When done, report: lane → verified count, rejected count, ID range consumed, and any
systemic weak-evidence caveats.
