# Upmore 25-Scenario Harsh Assessment — Pass 1 (2026-09-25)

25 scenario workers × (4 functional + 1 design) = 125 points max. Each worker drove real
onboarding + tools in a fresh Chromium context against the built app, harsh fail-near-misses.

**PASS-1 TOTAL: 66/125**

## Per-agent table

| # | Scenario | Persona | Score | Headline |
|---|----------|---------|-------|----------|
| T1 | Refund Lender | W-2, $3,275 refund | 5/5 | Correct refund→$273/mo IRS loan reframe, W-4 guidance, IRS estimator named |
| T2 | Gig Newbie | $41k SE income | 5/5 | SE tax math exact, quarterly dates + safe harbor right |
| T3 | Working Family | MFJ 2 kids $62k | 1/5 | App shows generic $8,231 EITC (wrong for 2 kids: max $7,316); no income/children gates |
| T4 | HSA Maxer | $125k, family HDHP | 1/5 | Limits right; no personal forgone-savings, no Apr 15 2027 deadline, no OOP max |
| T5 | Student | $19k, half-time+ | 0/5 | AOTC gates missing; Saver's Credit shown to an ineligible full-time student = misleading |
| T6 | High Earner | $185k single | 1/5 | Generic $24,500 limit; no personal $12,500 gap, no 32% deferral calc, no IRA phaseout honesty |
| T7 | Gig Pro | $92k SE | 2/5 | Quarterly math right; SEP-IRA/Solo 401(k) content absent; no expense-tracking nudge |
| S1 | Subscription Bleed | $214/mo, 14 subs | 1/5 | Sign-in gated; no annual total; no usage-awareness; no $-ranking |
| S2 | Annual Trap | monthly vs annual | 1/5 | No annual-vs-monthly math anywhere; no lump-sum cash-flow honesty |
| S3 | Trial Stacker | 6 trials | 1/5 | No trial-expiry tracking at all; no cancel-before-charge checklists |
| I1 | Underpaid Assistant | $38k Chicago | 2/5 | No role/pay/location inputs; no admin-assistant or Chicago benchmark data |
| I2 | Freelance Dev | $70k→freelance | 4/5 | Formula right; the $70/hr floor number never renders on screen |
| I3 | Invoice Chaser | 3 overdue invoices | 4/5 | Tracker + cadence correct; no per-invoice stage guidance or templates |
| I4 | Job Hopper | 3 moves, 22% raises | 5/5 | Stale job-hop advice correctly labeled stale with 0.1% BofA/Fed data |
| D1 | Avalanche Chris | $18.5k 3 cards | 3/5 | Math exact; promo warning renders false "then 0% applies"; expiry not in payoff sim |
| D2 | Promo Amy | $9k 0%→26.99% | 3/5 | Warning fires; no 60-day payoff target; sim accrues revert APR during promo months (bug) |
| D3 | Refinance Pat | 11.99% 5-yr offer | 1/5 | No refinance-vs-paydown comparison exists at all |
| C1 | Idle Cash Beth | $28k checking | 5/5 | $1,173/yr gap computed live, dated 4.2%; minor layout overlap defect |
| C2 | Runway Jay | $4.1k liquid, $2.9k burn | 4/5 | Formula correct; can't compute from HIS inputs; `.pcard` layout clips context lines |
| C3 | Monthly Close | 90-second check | 5/5 | In/out/net, 3-mo comparison, categories, labeled sample data, no shame mechanics |
| N1 | Insurance Gap Luis | $95k, 2 kids | 3/5 | Cost anchors right; no numeric inputs → no personal $950K–$1.14M target |
| N2 | Adequate Zoe | renter + car | 5/5 | 100/300/100 + UM, renters pitch, you're-fine logic, no umbrella upsell — clean |
| E1 | Broke Tyler | $0, 1 hr/week | 2/5 | Spend-gated coupons lead for $0 user; demo-data queue tells him to cancel a stranger's ComEd |
| E2 | Experienced Nina | $500/mo sustained | 0/5 | Undisclosed affiliate links (R0495, R0032); gambling promo routes discoverable; no $/hr |
| X1 | Adversarial | 6 attacks | 2/5 | Fraud-framed direct-deposit got a bank-bonus how-to, no refusal; refusal template unreachable |

## Failures grouped

### Wrong figures (must fix — money math users act on)
- **T3**: generic $8,231 EITC shown to a 2-child household (max $7,316). Overstating a refund is the worst tax error.
- **T5**: Saver's Credit shown without ineligibility note — misleads a full-time student toward claiming ineligible credit.
- **T1/T2** passed; tax figures elsewhere verified against IRS 2026 (research/tax-positioning-2026.md).

### Missing features (ranked by dollars at stake — the fix list)
1. **Tax personalization engine** (T3 1/5, T4 1/5, T5 0/5, T6 1/5): filing-status/children/income inputs gating every
   credit (EITC gates: $65,899 MFJ 2-child, $12,200 investment income; CTC/ACTC formulas; AOTC gates; Saver's
   ineligibility; HSA forgone math; 401(k) personal gap; IRA phaseout honesty). ~$2,000–$4,000/user stakes.
2. **Undisclosed affiliate links** (E2): R0495 HealthyWage (ShareASale) and R0032 Wealthfront (Impact Radius) ship
   affiliate URLs with `affiliate: False` — paid relationships, zero disclosure. Violates the hard constraint.
   Fix: mark affiliate:true + badge + non-affiliate alternative. ~$50–$200/user, but a trust violation.
3. **Gambling routes in earnable catalog** (E2): R6801 FanDuel Promo Arbitrage, R6813 PrizePicks Promo Arbitrage —
   R6813 passes age-19 gates and is discoverable. Violates "No gambling routes as general Earn methods."
   Fix: retire/demote R6801, R6813 (and review R0495/R0496 bet-your-own-money pools). ~$100s at risk/user.
4. **Refinance-vs-paydown comparison** (D3 1/5): no loan-offer input, no fee/effective-APR, no 5-yr term-trap math,
   no decision rule ("refinance wins only if all-in cost < current path"). ~$3,500 trap in benchmark scenario.
5. **0%-promo handling** (D1/D2): (a) false warning "then 0% applies" — no post-promo APR field; (b) sim accrues
   revert APR during promo months; (c) promo expiry not factored into payoff order/math; (d) no payoff-before-expiry
   target ($4,500/mo for Amy). ~$200+/mo post-expiry interest.
6. **Guide refusal gaps** (X1 2/5): fraud-framed direct-deposit request got a bank-bonus how-to with no refusal;
   refusal template unreachable (keyword gaps: "sportsbook", "fake"/"fraud", "credit card"). Company-ending risk.
7. **"Confirmed" badge overreach** (E1): `routeVerification()` maps all 1,381 researched routes to "confirmed" —
   audit says "researched, not verified". Fix badge to "researched". Trust violation at scale.
8. **Subscription tracker** (S1/S2/S3, all 1/5): sign-in gated with no annual total; no annual-vs-monthly math;
   no trial-expiry/conversion-date tracking; no cancel-before-charge checklists; no dark-pattern honesty.
9. **Income tool inputs** (I1 2/5, I2 4/5): no role/pay/location benchmark inputs; $70/hr floor number never renders;
   (I3 4/5: per-invoice stage labels/templates missing).
10. **Runway manual inputs** (C2 4/5): can't compute from user inputs (Jay's $4,100/$2,900 → 6.1 weeks unproducible);
    `.pcard` layout clips context lines.
11. **N1 numeric inputs** (N1 3/5): insurance tool has zero inputs → no personal coverage target.

### Guardrail breaches
- X1: no refusal on fraud-framed request (bank-bonus how-to served instead).
- E2: undisclosed affiliate links + gambling routes in earnable catalog.
- E1: spend-gated coupons lead for a $0-cash user (NEEDS_SPEND_CATS misses "Signup Bonus").
- E1: "confirmed" badge overstates verification on 1,381 routes.

### Design
- E1: demo-data queue tells a broke user to cancel a stranger's ComEd; plan Move 2 is an un-actionable coupon.
- I3: invoice rows identical ("follow up today") across 12/30/45-day stages; flagship invoice past app's own escalation ladder.
- C1: layout overlap in idle-cash card; C2: `.pcard` clipping runway context lines.
- T4/T7/N1: persona-critical numbers (forgone HSA, combined quarterly, coverage target) never computed.

## Hard-fail check (app-wide)
- No money movement anywhere; read-only bank framing consistent.
- No guaranteed-income promises (all 5 "guaranteed" hits are negations or program terms).
- No credit-card-in-Earn offers surfaced; no ToS-trick routes surfaced.
- Zero console/page errors across all 25 runs.

## Notes for pass 2
- Workers tested `file://` build in fresh contexts without sign-in; subscription tracking (S1) is sign-in gated —
  pass 2 should include an authenticated path or the gate must be fixed for unauthenticated trial tracking.
- Screenshots saved to /tmp per scenario (T7, I3, C1, C2, E1); kept for visual diff in pass 2.
