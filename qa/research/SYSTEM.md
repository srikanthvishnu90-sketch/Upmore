# Upmore Offer Research System v1

Goal: never run out of verified ways to make people money. A standing pipeline that
discovers new offers, dedupes them against the catalog, verifies them against official
terms, inserts them, and re-verifies everything on a schedule.

## Pipeline stages

1. DISCOVER — watchers fetch source pages (see sources.yaml), extract candidate offers
   (provider, headline payout, official URL, spotted date).
2. DEDUPE — candidates are fuzzy-matched against the 535-route catalog (provider +
   method). New providers/methods become candidates; matches update the existing
   route's promo terms instead of duplicating.
3. EXTRACT — for each candidate, pull the official terms page and extract: concrete
   payout, requirements, timing, eligibility, catches. (Subagent with the verification
   checklist; same evidence-JSON schema as qa/verification/.)
4. VERIFY — human-checklist verdict: concrete payout in official terms, real company,
   no upfront fee, official source. Pass -> verified route. Fail -> rejected with reason
   logged (never silently dropped).
5. INSERT — verified routes enter the routes table with verified_at, verified_source_url,
   expires_at (promo end date or re-verify cadence). Rejected candidates go to
   route_candidates with status=rejected so we don't re-research them.
6. REVERIFY — every verified route has expires_at. A scheduler re-runs EXTRACT+VERIFY
   before expiry. Terms changed? Route updates, affected users get alerted. Promo gone?
   Route retires (status retired, never deleted — history matters for the flywheel).

## Storage (v1: files, v2: DB)

- `qa/research/candidates.jsonl` — one JSON object per candidate: {spotted_at, source,
  provider, method, headline_payout, official_url, status: new|verifying|verified|
  rejected|retired, route_id (once inserted), notes}.
- `qa/research/runs/` — dated logs of each watcher run.
- v2: migrate candidates into a `route_candidates` table so the app can show
  "new offers being verified" state.

## Cadence

- Bank/brokerage/fintech promos: weekly (they change constantly).
- Cashback/survey/research: monthly.
- Full catalog re-verification sweep: quarterly.
- A route within 30 days of expires_at: re-verify immediately.

## What Meta won't do

Run an always-on, human-checklisted monitoring operation over hundreds of merchants
for one vertical. This pipeline is pure ops cost with zero horizontal reuse — which
is exactly why it's a moat.
