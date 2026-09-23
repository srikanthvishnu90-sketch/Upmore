# Speed sweep report — 2026-09-23

Owner mandate: "try and get all of them to pay fast. Be creative."

## Result

All **1,200** verified routes previously classified `weeks` were audited by 8 parallel workers against official provider terms.

| Outcome | Count |
|---|---|
| Moved to `today` | **31** |
| Moved to `days` | **101** |
| Structurally slow (kept `weeks`) | **1,068** |
| New faster-provider routes added | **7** |

Verified speed distribution after sweep: **today 108 / days 195 / weeks 1,068** (was: weeks 1,200 of 1,364 verified; now 1,371 verified).

Every reclassified route has the fast path documented in `maximize` + `when_cash_arrives` and a dated `speed_history` entry in its evidence file. DB `speed` matches evidence on all 1,371 verified rows (0 mismatches, full-catalog cross-check).

## Movers by chunk

- **Referral Bonus A1 (179):** 3 today (PeoplesBank, MembersCU, Byron Bank — referrer paid at account opening) + 29 days (SoFi ≤7 biz days, GO2bank ≤48h, Stanford FCU next-day; 19 event-triggered/no-stated-clock, flagged judgment-heavy in evidence).
- **Referral Bonus A2 (180):** 15 days (CIBM $50 at opening, Cal Coast $100/3 biz days, HACU $25/5 days, no-hurdle CUs). One revert: Great Erie FCU back to weeks (friend needs direct deposit — payroll trigger).
- **Bank Bonus B (314):** 1 today — **Blaze Credit Union R0616, $250 deposited upon account opening** (online qualifies; clawback terms documented). Rest structural.
- **Energy/Rebate/Telecom C (215):** 2 today (Gault Energy signup credit, Strike fee-free trading) + 4 days (Rover, MoneyLion, Ultra Mobile, H2O Wireless referrals).
- **Mixed online D (112):** 12 today + 10 days.
- **Brokerage/Fintech E (69):** 6 today (BP earnify, student software) + 13 days (SoFi ACAT/IRA 5 biz days, SoFi checking 7 days, Robinhood IRA immediate on settlement, Notarize next biz day).
- **Research/Survey F (57):** 4 days (UserInterviews, PlaytestCloud ≤3 days, PrizeRebel hours–24h, Chicago Booth 3–4 biz days).
- **Buyback/AI/UGC G (74):** 7 today (Revolut Learn & Earn seconds, Microsoft Rewards ≤24h, Samsung instant credit, CareYaya at session end) + 26 days (DataAnnotation weekly, Prolific instant post-threshold, Scribie on acceptance, buybacks 1–5 days post-receipt).

## New faster-provider routes (7 inserted, verified)

- R7930 MoneyLion Shake 'N' Bank — today (near-real-time cashback)
- R7940 SurveyJunkie — days ($5 PayPal; timing caveat documented)
- R7941 Forthright — today (official instant payout, no minimum)
- R7942 Branded Surveys — days (official 1–3 biz days at $5)
- R7950 Microsoft 365 Education — today (free, same-day)
- R7951 Autodesk Education — today (free 1-yr licenses)
- R7960 Qmee — days (no-minimum PayPal cashout)

Rejected at adjudication (not inserted): R7961 Poll Pay (no official terms observed), R7910 Fetch referral (figure unconfirmable — browser down at adjudication; resubmit with official help-center citation).

## Structurally slow — dominant blockers

1. **Bank/brokerage qualification windows** — 60–90-day direct-deposit cycles, 12-month funding holds, 90-day seasoning; bonus clock starts after qualification, not effort.
2. **Rebate/energy processing** — 4–8 week check/card fulfillment, 30–90-day good-standing waits, multi-month credit spreads.
3. **Mailed reward cards** (4–6 weeks) and **monthly pay cycles** (survey/research platforms).
4. **Unpublished payout timelines** — kept honest at weeks rather than guessed.
5. **Prediction-market resolution windows / promo-credit holds** (disclosures preserved).

## Flags for owner (not actioned — need your call)

1. **Branch-visit-required bank bonuses (10):** R0536, R0567, R0625, R0636, R0637, R0948, R2128, R2341, R2407, R5545 — violate online-only if enforced strictly.
2. **Physical-prerequisite routes spotted by chunk C:** propane/fuel-delivery routes (R5497–R5527 range, R0763/64/71/77/79/80/83/84), ISP-installation promos (R1191–R1195, R6378), R0817 Rover (in-person pet care). The money action is online signup; the underlying service is physical.
3. **R1141 insurance quote** requires a phone call (outside online-only scope per worker).
4. **Possible duplicates:** R0637/R2407 (same Summit CU page); cross-lane dups noted earlier (Prolific R0220/R6619/R7830, User Interviews R0229/R7842, Cambly R6751/R7802, Wyzant R6752/R7801, JuryTest R0293/R7202, Mindswarms R0290/R7242, Userbrain R0223/R7220).
5. DB `when_cash_arrives`/`maximize` columns are NULL for pre-existing routes (only the 178 quick-lane + 7 new rows carry them); the app's expanded panel reads DB columns, so older routes show no seven-field detail there. Consider a backfill.
6. 6 chunk-C evidence files missing (R0791, R0801, R0812, R0813, R0816, R0818) — untouched, remain weeks.

## Production

- DB: 1,952 total rows (1,371 verified / 265 unverified / 316 retired).
- Served bundle: 1,636 cards, 0 retired, 0 credit-card, ranks 1–1371 unique, ratio-descending.
- Commit + push + HTTP 200 check follow in session log.
