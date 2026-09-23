# Inspector brief — Upmore 1500 expansion adjudication

Work directory: ~/workspace/upmore. Evidence ONLY reads + one JSON output. No DB writes, no commits.

## Task
Independently adjudicate every worker "verify" verdict in qa/verification/R0851.json … R2020.json.
Workers were told: distinct earning mechanisms only, current official-provider terms only,
no duplicates, no sub-features, no risk-capital/pay-to-play, no expired/dead programs.

## Procedure
1. Run `python3 qa/validate-1500.py` and read qa/validation-1500.json — start with every
   ISSUE and DUP group it flags.
2. For EVERY verify file (not just flagged): read the file, confirm
   a. official_url is the provider's OWN domain (not an aggregator, not a blog);
      spot-fetch 15–20 official_urls with browser.open and confirm the payout terms exist there.
   b. the mechanism is distinct: not a duplicate of another new file (same provider+mechanism),
      not a duplicate/sub-feature of an existing catalog route — check with
      `python3 qa/dedupe-check.py "<provider>"` and `grep -i "<provider>" qa/existing-providers.txt`.
   c. counting rules honored: reject dead/expired programs, aggregator-only terms,
      sub-features (e.g. "daily receipt" under an existing receipt app), risk-capital routes
      (crypto rebates, pay-to-play, pay-to-apply), prediction markets, MLM, academic misconduct.
   d. honesty posture: credit-card files carry never-spend-extra/annual-fee/hard-inquiry/APR
      catches; rebates framed as savings; variable work labeled variable; plasma/clinical carry
      medical-screening disclosures; points converted at provider's own redemption value only.
   e. numeric fields sane: 0 <= payout_min <= payout_max, 1 <= time_min <= time_max,
      payout_max not absurd vs the quoted terms.
3. Write qa/adjudication-1500.json: `{"R####": "one-line demotion reason", ...}` for EVERY
   file you demote. Demoted files are treated as rejects by the applier — do NOT edit the
   evidence files themselves.

Be strict: a weak verify demoted is better than an inflated count. But do not demote solid
verifications — the workers' official-terms evidence stands unless you find a concrete flaw.

## Report back
Kept-verified count, demoted count with the ID + reason for each demotion, and any systemic
issues (e.g. a whole lane's evidence pattern that worried you).
