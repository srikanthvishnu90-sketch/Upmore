# Evidence schema — R8000+ discovery batch (2026-09-23)

Work directory: `~/workspace/upmore`. Write evidence ONLY to `qa/verification/R####.json`
(your assigned ID block only). Never touch the DB, never commit, never deploy.

## Discovery + verification tools
- `browser.search` to discover, `browser.open` to fetch pages.
- Verify ONLY against the PROVIDER'S OWN official terms page (their domain) or the
  venue's own official rules page. Aggregators (reddit threads, blogs, review sites)
  are discovery leads only — never evidence. Exception for watering-hole routes:
  the venue's own official rules/FAQ/marketplace page counts as official.
- Dedupe BEFORE writing: `grep -i "<provider>" ~/workspace/upmore/qa/existing-providers.txt`
  and glob `~/workspace/upmore/qa/verification/R*.json` for the same provider/mechanism.
  When in doubt, reject as duplicate.

## Ethics (reject aggressively — when in doubt, REJECT)
No fake accounts, no deception, no review manipulation, no ToS violations, no academic
misconduct, no pay-to-apply, no risk capital / wagers, no MLM, no scams, no credit cards,
no physical/in-person anything. All online-only (phone/computer).

## Speed (STRICT — this batch is fast-only)
- `today`: usable cash can actually arrive the SAME day (task done + paid out same day).
- `days`: usable cash within ~7 days.
- Anything slower → REJECT (reason: slow). Nothing in this batch may be `weeks`.

## Required keys on every verify file
Canonical: `route_id`, `verdict` ("verify"), `provider` (display name), `official_url`,
`terms_url`, `payout_quote` (verbatim from official terms), `steps` (concrete strings),
`catches` (array), `biggest_catch` (string), `eligibility` (string), `timing` (string),
`upfront_fee` (bool), `weasel_words` (array), `app_links` ({android, ios} or {"",""}),
`checked_at` (real UTC ISO), `critical` ({c1..c4: {pass, evidence}}),
`standard` ({s1..s7: {pass, note}}), `notes` (string).
Numeric: `payout_min_usd`, `payout_max_usd`, `payout_value_note`, `time_min_minutes`,
`time_max_minutes` (active minutes, honest estimate, min 1), `numeric_basis`.
Fast-lane: `speed` ("today"|"days"), `when_cash_arrives` (string), `maximize` (string:
ethical, provider-compliant speed/max tips only), `repeatable` ({"value": bool,
"cadence": string}).
7 answers: `who_pays`, `who_qualifies`, `work_available` (say honestly if oversubscribed
or unverifiable — "unverified" is allowed), `what_gets_accepted`,
`costs_and_unpaid_time`, (`when_cash_arrives` doubles as #6).
NEW: `demand_side` (string, REQUIRED): the actual venue where buyers post/offer this —
platform name + URL, how gigs/opportunities appear there, how the user reaches it today,
how people get picked/accepted. This is the owner-mandated demand-side field.

## Rejects
Do NOT write a JSON file for rejects. Append ONE line per reject to
`qa/discovery/rejects-R8xxx.txt` (create it):
`R####|Provider Name|2026-09-23T<UTC>Z|https://source-url-or-empty|one-line reason`
Use the next free ID in your block for each reject (IDs are consumed by both).

## AI-proof lens (top priority)
Frame `who_qualifies` around the human requirement: WHY does the buyer need a real
human (real device, lived experience, real judgment, real voice, real identity)?
Reject anything where AI could trivially do the task AND the platform doesn't care —
we want the AI-proof moat, not commodity tasks AI undercuts.

## Report back
verified count, rejected count, ID range consumed, 3–5 most unique finds,
systemic weak-evidence caveats.
