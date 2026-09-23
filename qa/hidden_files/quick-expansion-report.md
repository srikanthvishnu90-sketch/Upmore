# Quick-Income Catalog Expansion — Final Report (2026-09-23)

**Outcome: 178 new verified routes ingested** into the Upmore Supabase project
(`mrwngntwmnaqrqhupvlt`), app bundle rebuilt and deployed.
Bundle now: **1,945 routes, 1,468 verified** (ranks 1–1468 unique, ratio-descending).
Zero verified credit-card routes anywhere in the served bundle.

## Lane results (verified / rejected)

| Lane | IDs | Verify | Reject | Notes |
|---|---|---|---|---|
| User testing | R6600–R6659 | 11 | — | R6634 demoted → dup of R7830 (better-grounded Prolific) |
| Microtasks/gigs | R6700–R6799 | 34 | — | R6754 demoted → dup of R7842 (better-grounded User Interviews) |
| Promo arbitrage | R6800–R6852 | 5 | 48 | 40 demoted: same-week re-verifications of live catalog routes (bank/brokerage/fintech bonuses); 8 worker rejects kept |
| Fast referrals | R6900–R6999 | 4 | — | Canada-only / slow-pay / no-official-amount rejects |
| Gift-card resale | R7000–R7099 | 37 | — | |
| Mystery shopping | R7100–R7199 | 6 | — | |
| Focus groups | R7200–R7270 | 4 | 67 | R7216 dup Respondent, R7239 dup PlaybookUX, R7248 invite-only single event demoted |
| Cashback | R7300–R7399 | 4 | — | |
| Buyback/sell-it-today | R7400–R7499 | 31 | — | |
| Plasma/donation | R7500–R7599 | 15 | — | |
| Delivery instant cashout | R7600–R7699 | 9 | — | |
| Labor/moving apps | R7700–R7799 | 11 | — | |
| Tutoring/translation/voice | R7800–R7899 | 7 | 93 | 5 demoted: catalog dups (Preply, Mindrift, Rev, PlaytestCloud) + R7840 dup Respondent |
| UGC video | R6500–R6599 | 0 | 0 | **EMPTY** — two worker safety-system refusals; not retried |

**Totals: 178 verified / ~250+ rejected / 1 empty lane.**

## Duplicate accounting

- Cross-lane duplicates resolved by keeping the better-grounded version:
  - R6634 (Prolific) → R7830 (official $8/hr minimum vs mislabeled points quote)
  - R6754 (User Interviews) → R7842 (concrete $50/$150 listings vs 0–0 variable)
  - R6819 Survey Junkie, R6821 CSL Plasma → rejected (dup / weak evidence)
- Catalog duplicates demoted: 40 in promo lane (bank/brokerage/fintech bonuses already live),
  5 in tutoring lane (Preply→R1732, Mindrift→R0282, Rev→R0390, PlaytestCloud→R0167/R0226, Rover→R0817),
  Respondent/User Interviews/Prolific/Amazon Shopper Panel new-lane overlaps.
- Near-duplicate guard: each lane verified distinct mechanisms; same-provider routes kept only
  when the mechanism differs (e.g. Kalshi promo-code R6800 vs Kalshi referral R6802).

## Speed distribution (178 new verified)

- today: 73 · days: 96 · weeks: 7 · unknown: 2 (R7513, R7527 — official payout exists,
  payment method/timing unpublished; disclosed in `when_cash_arrives`)

## Repeatability

- Every verified route carries `repeatable: {value, cadence}` with an explicit loop.
- One-time routes say so: all 4 referral-lane routes, betting promos (R6800/R6801/R6813 one-time;
  R6802 repeatable per referral up to 40), buyback routes ("once per item you own"),
  bank/brokerage bonuses excluded as catalog dups.
- Bill-credit/store-credit routes labeled as credit, never cash (Mint Mobile R6834, 7 gift-card
  savings routes, Samsung/Amazon/Target trade-ins lead with "NOT cash").

## 7-field framework

All 178 verified routes carry `who_pays`, `who_qualifies`, `work_available`,
`what_gets_accepted`, `costs_and_unpaid_time`, `when_cash_arrives`, and `repeatable.cadence`.
Validation: 0 missing fields, 0 literal-"unverified" whole-field fallbacks except 5 honest
`work_available: "unverified"` marks where evidence didn't support a claim.
DB columns added: `who_pays, who_qualifies, work_available, what_gets_accepted,
costs_and_unpaid_time, when_cash_arrives` (TEXT), `repeatable` (JSONB).
App renders the 7 fields in each route's detail view (`sevenFields` in template).

## Corrections made during adjudication

- R7128 Call Center QA payout max $8 → $7 (fresh official page: $6–$7).
- R7504 KEDPlasma $35–$70 → $55 flat (only the $55 second-donation bonus officially supported).
- R6711 BeMyEye GBP 5–25 → ≈$7–$34 (was entered as USD).
- R7501 BioLife numerics: $40–$115/90–180min → $700 fixed / 720–1440 min (8-donation coupon economics).
- R6819/R6821 JSON trailing-comma repairs; 24 R67 files given explicit repeatable loops.
- R7501 `expires_at` = 2026-09-27T23:59:59Z (BioLife $700 coupon code 40019 first-donation deadline);
  must be re-verified/replaced after expiry.
- Time-sensitive promos tracked: Citizens 9/30, tastytrade 9/30, TopCashback 9/28–9/30,
  Associated 10/2, M&T 10/8, Chase 10/14, Wintrust 11/3, U.S. Bank 11/10, BMO 12/15,
  SoFi/Huntington/PrizePicks/moomoo 12/31, PNC 1/7/27, E*TRADE 1/10/27, Wells Fargo 1/12/27.

## Betting/promo routes (owner's narrow exception)

R6800 (Kalshi promo code), R6801 (FanDuel NFL promo), R6802 (Kalshi referral),
R6813 (PrizePicks) — all framed as bets, not income: own stake can be lost 100%,
credits non-withdrawable with 7-day expiry, only profits withdrawable, lottery odds
disclosed (70% of Kalshi claimants get $15), state/age eligibility, 1-800-GAMBLER.
R6801 realistic max value ≈$114 (not $250); R6813 payout floor $0.

## Rejected lanes / empty lanes

- R65 UGC video: EMPTY after two safety-system refusals. Not retried this session.
- Promo lane: 8 worker rejects kept (BetMGM, Venmo, PayPal, Webull, eJury, Survey Junkie, Swagbucks, CSL Plasma).
- Focus-group lane: 67 rejects (saturated panels, no official pay, invite-only studies).
- Tutoring lane: 93 rejects (self-set rates with no platform pay floor, unpaid models, academic-misconduct services excluded).

## Pipeline artifacts (modified, committed)

- `qa/apply-quick.py` — lane mappings R7200–R7899, 7-field columns, R7501 expiry
- `qa/rebuild-app-data.py` — 7 fields synced into bundle
- `qa/backfill-quick-numerics.py` — new: numerics backfill for R6600–R7899
- `qa/numerics.json` — 178 entries added (1680 total)
- `src/upmore-app-template.html` — 7-field detail section + 6 new category icons
- `src/build-app.py` — unchanged (template-driven)

## Open follow-ups

1. R7501 BioLife coupon expires 2026-09-27 — re-verify or replace after expiry.
2. R7308 Ibotta Thanksgiving expected November 2026 — check when live.
3. Existing catalog cleanup still pending: non-promo prediction-market/risk-capital audit,
   R0495 HealthyWage framing, "make me $X" repairs.
4. Public-copy branding rewrite still pending (welcome/onboarding/metadata/"Make Money" labels).
5. R65 UGC lane: needs a different sourcing strategy (worker refusals).
