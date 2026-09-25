# Upmore 25-Scenario Harsh Assessment — Pass 2 (2026-09-25)

25 scenario workers × (4 functional + 1 design) = 125 points max. Each worker used the EXACT
dossier from `qa/25-scenarios.md` (no persona drift — pass 1's failure), with fresh attack angles
and conversation paths per the owner's formulation rule. Tested against `~/workspace/upmore/index.html`
at commit 85b88c0 (byte-identical to production; Vercel deployment = success).

**PASS-2 TOTAL: 88.5/125** (pass 1: 66/125 — **+22.5**)

Recovery note: the pass-2 coordinator completed all 25 workers but never wrote its report. Scores
below were recovered from the coordinator's session log (per-scenario verdicts as workers reported
in). No scores were invented.

## Per-agent table

| # | Scenario | Persona | Score | Headline |
|---|----------|---------|-------|----------|
| T1 | Refund Lender | W-2, $3,400 refund | 3/5 | W-4 reframe uses static $3,275 avg instead of her $3,400; exact phrasing → catalog fallback |
| T2 | Gig Newbie | $41k SE income | 4/5 | SE math exact; "41000" substring-matched a $1,000 money-routes intent (Userfeel surveys); "file my taxes" → bank-bonus answer; gig tax line ignores standard deduction, overstating bill |
| T3 | Working Family | MFJ 2 kids $54k | 4/5 | **False "22% marginal rate" bug real**: `tax_rate` hardcoded 22 default, never derived from income — at $54k MFJ (true 12%) nearly doubles 401(k) savings ($4,730 vs ~$2,580) |
| T4 | HSA Skipper | $125k, family HDHP | 5/5 | All four points exact incl. $1,705/yr with $1,000 seed subtracted; "file my taxes for me" → generic tax branch, not the never-file refusal |
| T5 | Student | $19k, half-time+ | 3/5 | AOTC gates good; missing post-2025 student-SSN requirement; Saver's Credit "under 24" qualifier wrong; "education credits" ≠ Guide's "tax credit" keyword |
| T6 | High Earner | $185k single | 4/5 | Same hardcoded-22% bug; benchmark's 32% premise wrong for Greg (true 24%); Guide over-refuses any "401k" mention, blocking personalized tax answers |
| T7 | Freelancer | $92k SE | 3/5 | Quarterly tool correct; Solo 401(k) + SEP-IRA missing; "quarterlies" → Chase Private Client bank bonus |
| S1 | Overwhelmed | $214/mo, 14 subs | 4/5 | Audit math exact, cancel assemble-only; no way to mark subs as unused (deliberate honesty, benchmark bar unmet) |
| S2 | Annual Trap | monthly vs annual | 2.5/5 | Total yearly savings never computed, no buffer warning, Guide dead-ends on annual-billing question |
| S3 | Trial Hopper | 6 trials | 3/5 | Countdowns work; cancel flows cover only 8 merchants (Peacock/Max/Crunchyroll empty); no call-to-cancel warning; zero trial intents in Guide |
| I1 | Underpaid | $38k Chicago | 2/5 | BLS table only 10 roles (admin assistant missing); 25th-percentile rule not implemented (uses % of median); **"should I ask for a 20% raise?" → Raise.com gift-card-resale card** (provider named "Raise") |
| I2 | Underpricer | freelance rate | 5/5 | Headline computes $84.13/hr using ÷2,080 while its own copy warns against dividing by 2,080; "what should I charge?" misses freelance-rate intent |
| I3 | Unpaid | 3 overdue invoices | 5/5 | Clean pass |
| I4 | Job Hopper | 3 moves, 22% raises | 1/5 | No job-hop intent matcher; "20% raise" → **Raise.com card again**; "20%" parsed as $20 money target. "Raise" collision now a confirmed pattern (I1 + I4) |
| D1 | Avalanche | $18.5k 3 cards | 4/5 | Debt math independently verified exact; **"which card do I pay first?" → "The 3 easiest routes" bank signup offer** ("first" substring hijacks intent) |
| D2 | Promo Clock | $9k 0%→26.99% | 3/5 | **Minimums-only math shows "$499,506,031 interest over ~600 months"** — half-billion-dollar fantasy figure presented as a factual plan comparison |
| D3 | Refi Tempted | 11.99% 5-yr offer | 5/5 | Effective-rate math + term-trap exact; "consolidate"/"refinance" phrasings fall through; no re-accumulating-debt warning |
| C1 | Hoarder | $28k checking | 5/5 | $1,173 math exact; "can you move it for me?" misses refusal keywords |
| C2 | Precarious | $4.1k liquid | 5/5 | Runway arithmetic verified; live-data caveat: bank transactions all map to "Other," excluded by burn filter — live users need manual recategorization |
| C3 | Chaotic | monthly close | 5/5 | Clean pass |
| N1 | New Parent | $95k, 2 kids | 4.5/5 | Module strong |
| N2 | Renter-Driver | renter + car | 4.5/5 | Module copy excellent; Guide only reaches insurance via 5 magic phrases — plain English falls through |
| E1 | Broke Beginner | $0, 1 hr/week | 1/5 | **Earn surfaces blank (freshness-gate bug)**; gateless rankMoves() surfaces Lampsplus coupon to $0 user; demoted routes wear "verified-2026-09-25"; **Kalshi routes at rankMoves() #18–19 with canLead=true** |
| E2 | Side Hustler | $500/mo sustained | 0/5 | **HARD FAIL**: Explore + Home "Up next" render ZERO routes (freshness gate: `verification === "confirmed"` but routeVerification() returns "researched" since the pass1-E1 fix); credit-card signup routes in Earn catalog (R6402 JCPenney, R0473 X1 Card, R0474 Petal) |
| X1 | Adversarial | 6 attacks | 3/5 | All 6 chat attacks held; catalog itself violates rules: **FanDuel R6801 + PrizePicks R6813 are lane=Standard, pass all 9 gates, no risk badge**; Guide claims "gambling isn't an earning method" while Explore lists both |

## Failures grouped

### Production-critical (fix before any launch claim)

1. **Earn surfaces blank — freshness-gate bug** (E1 1/5, E2 0/5): earnGates requires
   `route.verification === "confirmed"`, but the pass1-E1 fix (commit 08ca95a, "was confirmed —
   overstated the audit") changed `routeVerification()` to return `"researched"` for researched
   routes. 1,377/1,388 Standard-lane routes fail the gate; `xFiltered()` and `buildQueue()` both
   return **zero earn routes**. Explore and Home "Up next" render nothing. **The fix for one
   overstated label broke the entire Earn surface in production.**
2. **Gambling routes still earnable** (E1, X1): Kalshi prediction-market routes sit at
   `rankMoves()` #18–19 with `canLead=true` — one rank shift from a gambling recommendation.
   FanDuel R6801 and PrizePicks R6813 are `lane=Standard`, pass all 9 gates with no risk badge.
   The pass-1 "retire/demote gambling routes" fix did NOT take effect. Standing rule violated.
3. **Credit-card signup routes in Earn** (E2): R6402 JCPenney, R0473 X1 Card, R0474 Petal —
   despite the standing no-credit-cards-in-Earn rule.
4. **Gateless queue serves non-cash to broke users** (E1): onboarding "Your first 3 moves" =
   `rankMoves().slice(0,3)` with NO gates — Move 2 for a $0 user is R6430 Lampsplus coupon
   ("no cash needed up front" on a $50-spend coupon). Violates extractable-cash-only.
5. **Demoted routes wear "verified-2026-09-25" labels** (E1): trust violation — audit demotions
   must change the rendered verification copy.

### Intent misroutes (Guide keyword brittleness — the run's biggest pattern)

- **"raise" (salary) → Raise.com gift-card card** (I1, I4): salary-context "raise" must never
  match the provider named "Raise." Confirmed across two scenarios.
- **"which card do I pay first?" → bank signup offer** (D1): substring "first" hijacks debt
  intent into "The 3 easiest routes."
- **"file my taxes" → bank-bonus answer** (T2); **"quarterlies" → Chase Private Client bonus**
  (T7); **"file my taxes for me" → generic tax branch** instead of the never-file refusal (T4).
- **"41000" → Userfeel surveys** (T2): substring matched a $1,000 money-routes intent.
- **"what should I charge?" misses freelance-rate intent** (I2); **plain-English insurance
  questions fall through** (N2 — only 5 magic phrases work); **"consolidate"/"refinance"
  fall through** (D3); **T1's exact phrasing → catalog fallback**.

### Wrong figures (money math users act on)

- **Hardcoded 22% `tax_rate`** (T3, T6): never derived from income. At $54k MFJ (true marginal
  12%) the app nearly doubles claimed 401(k) savings: **$4,730 vs ~$2,580**. T6: benchmark's
  own 32% premise wrong for Greg (true 24%).
- **D2 fantasy figure**: minimums-only path shows **"$499,506,031 interest over ~600 months"**
  — the $180 minimum can't cover post-promo interest, and the sim presents the exploded number
  as a factual comparison.
- **T2**: gig income-tax line ignores the standard deduction, materially overstating the bill.
- **T1**: W-4 reframe uses static $3,275 average instead of her $3,400.
- **I2**: headline divides by 2,080 ($84.13/hr) while its own copy warns against dividing by 2,080.
- **T5**: Saver's Credit "under 24" qualifier wrong per benchmark; missing post-2025 student-SSN rule.

### Missing features (fix list, ranked by dollars at stake)

1. Live-bank runway: transactions map to "Other," excluded from burn filter (C2).
2. S2: yearly-savings total + buffer warning + annual-billing Guide path.
3. S3: cancel flows for more merchants; call-to-cancel warning; trial intents in Guide.
4. T7: Solo 401(k) + SEP-IRA positioning.
5. D3: re-accumulating-debt warning (benchmark's #1 failure mode).
6. I1: bigger BLS role table; implement the 25th-percentile rule.
7. S1: mark-subscription-unused (honest, no inference).
8. C1: "move it for me" refusal keywords.

## Verdict

**88.5/125 — better than pass 1's 66/125, but not shippable.** The seven CFO modules are
largely sound (C1/C2/C3 all 5/5, D3 5/5, I3 5/5, I2 5/5), and the Guide's math branches are
mostly exact. But five production-critical defects — a blank Earn surface, earnable gambling
routes, credit-card routes, non-cash served to broke users, and false verified labels — plus a
systemic keyword-brittleness pattern in Guide intent matching and a hardcoded tax rate that
doubles claimed savings, mean the product still fails the owner's bar. The Earn-surface blank
is the single most urgent item: a prior fix broke it, and it is live in production now.
