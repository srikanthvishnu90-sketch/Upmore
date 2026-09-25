# Debt Sequencing + Idle Cash — Research Report
**Date:** September 25, 2026
**Purpose:** Verified data + exact math for Upmore's debt-ordering and idle-cash features.
**How to read this:** Rates are *observed data as of the stated dates*, not rankings or recommendations. No affiliate links. All payoff math was computed by simulation (assumptions stated); not estimated.

---

## PART 1 — DEBT SEQUENCING

### 1.1 Why highest-APR-first minimizes total interest (the exact math)

Interest accrues each month as `balance × APR / 12`. Total interest paid over a payoff plan is the sum of that product across every month and every balance. The only thing the payer controls (given a fixed monthly budget) is *which balance shrinks first*.

Every extra dollar sent to a balance "earns" a return equal to that balance's APR — because it stops that dollar from accruing interest at that rate next month. A dollar sent to the 24% card saves 24¢/year; the same dollar sent to the 12% card saves 12¢/year. Sending it to the 24% card first is strictly better, every month, regardless of balances. That's the whole proof: **extra payments should always go to the highest APR first** (after minimums on everything — missing a minimum triggers late fees and penalty APR, which destroys the math).

The snowball method (smallest balance first) is *not* mathematically optimal — its value is behavioral (an early "win"). The honest product framing is: "snowball gets your first win in month X but costs you $Y more." Let the user choose with the price tag visible.

### 1.2 Worked example (simulated, not estimated)

**Setup:** Card A $8,000 @ 24% APR · Card B $5,000 @ 18% APR · Card C $3,000 @ 12% APR · $500/month total budget.
**Assumptions:** monthly compounding; minimum payment = interest + 1% of balance (floor $25) — the standard card formula; no new spending; payments applied minimums-first, then all extra to the target.

| Strategy | Months | Total interest | Total paid | First payoff |
|---|---|---|---|---|
| **Avalanche** (highest APR first) | 45 | **$6,438.77** | $22,438.77 | Card A, month 33 |
| **Snowball** (smallest balance first) | 48 | $7,687.16 | $23,687.16 | Card C, month 21 |
| **Minimums only** | 268 (22.3 yrs) | $22,602.24 | $38,602.24 | — |

- Avalanche saves **$1,248.39** vs snowball and finishes 3 months sooner.
- Avalanche saves **$16,163.47** vs minimums-only.
- Snowball's behavioral pitch is real: first card gone in month 21 vs month 33. The app should show that *and* its $1,248 price.

### 1.3 "This balance costs you $X/month" framing

Formula: `monthly interest cost = balance × APR / 12`. Per-day: `balance × APR / 365`.

On the example debts:
- Card A: $8,000 × 24% / 12 = **$160.00/month** ($5.26/day)
- Card B: $5,000 × 18% / 12 = **$75.00/month** ($2.47/day)
- Card C: $3,000 × 12% / 12 = **$30.00/month** ($0.99/day)

Product framing that survives scrutiny: *"Of your $500 payment this month, $265 is interest — only $235 touches what you owe."* Also show the minimum-payment trap honestly: the three minimums total $425/month ($240 + $125 + $60), of which $265 is pure interest.

⚠️ **Critical check for the app:** the "costs you $X/month" number must recompute from the *current* balance every month. A static figure goes stale as the balance drops and becomes a lie. Also, if the user is still spending on the card, the figure understates reality — the app should say so or exclude revolving cards from the framing.

### 1.4 Refinance vs aggressive paydown — the decision rule

**The rule:** refinancing wins when the **all-in cost of the new debt** (rate + fees amortized over the payoff horizon + any term-extension cost) is **less than the cost of the current path**. "Lower monthly payment" alone proves nothing.

Three-part check the app should run:
1. **Rate check:** new APR < weighted-average APR of the debts being replaced. (Weighted avg of the example: (8000×.24 + 5000×.18 + 3000×.12)/16000 = **19.875%**.)
2. **Fee check:** origination/transfer fees added to the comparison. A 3% fee on $8,000 is $240 — real money that must be in the math.
3. **Term-extension trap:** a lower rate stretched over a longer term can cost *more* total interest. Compare total interest, not monthly payment.

Worked (same $16k debts):
- Consolidation loan @ **10.54%** / 48 mo (MonitorBankRates avg, Sept 21 2026): payment $409.96/mo, total interest **$3,678** → beats avalanche ($6,439) by **$2,761**. Refinance wins.
- Same loan @ **20%** / 48 mo (Credible marketplace avg for debt-consolidation purpose, avg score 705): payment $486.89/mo, total interest **$7,371** → *worse* than avalanche. Refinance loses.
- Verdict: the average advertised "debt consolidation" rate is not automatically a win. The app must compare against the *offered* rate, not the average.

### 1.5 0% balance transfer promos — active September 2026

Longest verified intro periods (multiple aggregators, Sept 2026):

| Card | 0% intro (balance transfers) | Transfer fee | Annual fee | Regular APR after promo | Credit needed |
|---|---|---|---|---|---|
| Wells Fargo Reflect | 21 months | 5% (min $5) | $0 | ~17.7–28.5% var. | ~670+ |
| Citi Diamond Preferred | 21 months | 3% if transferred in first 4 mo, then 5% (min $5) | $0 | ~18–29% var. | ~680+ |
| Citi Simplicity | 21 months | 5% (min $5) | $0 | ~19–30% var. | ~670+ |
| U.S. Bank Shield Visa | 21 billing cycles | 5% (min $5) | $0 | ~17–28% var. | ~670+ |
| Discover it Balance Transfer | 18 months | 3% intro, then 5% | $0 | ~17–28% var. | ~670+ |
| Chase Slate Edge | 18 months | $0 first 60 days, then standard | $0 | varies | ~670+ |
| BankAmericard | 18 billing cycles | 3% | $0 | ~18–29% var. | ~670+ |
| Capital One Quicksilver | 15 months | 3% | $0 | varies | ~640+ |

Average card APR context (2026): **~21–22%** (Motley Fool/NerdWallet). A 0% transfer at 3–5% fee is nearly always cheaper than 21%+.

**Fee as effective APR:** a 3% fee spread over 21 months ≈ **1.70%** effective APR; a 5% fee ≈ **2.83%**. Still ~10x cheaper than carrying at 24%.

**Worked:** transfer Card A ($8,000) to Citi Diamond Preferred at 3% fee → $8,240 at 0% for 21 months, keep paying $500/mo total (minimums on B and C, rest to the transfer). Result: **$3,178 total cost** (incl. $240 fee), debt-free in **39 months** — saves **$3,260** vs plain avalanche and finishes 6 months sooner.

**The traps (must be on the card):**
1. **Deferred interest vs true 0%:** bank cards above are *true* 0% — at promo end, the *remaining* balance starts accruing at the regular APR. *Store* cards (CareCredit-style) use *deferred* interest: fail to pay in full by the deadline and interest is charged retroactively on the *original* amount. Different products, different danger.
2. **Grace-period loss:** new purchases on a balance-transfer card accrue interest immediately until the *entire* promo balance is paid off. Don't spend on the BT card.
3. **Transfer windows:** the transfer must usually complete within 60–120 days of account opening (varies by card) or the 0% doesn't apply.
4. **Same-issuer exclusion:** you can't transfer a Chase balance to a Chase Slate Edge.
5. **Hard inquiry cost:** ~5–10 point dip, typically recovers within months — but multiple applications compound the damage. Don't apply for three cards "to compare."
6. **Approval is not guaranteed:** 670+ FICO is typical for the 21-month cards; the credit *limit* granted may not cover the full balance.

### 1.6 Debt consolidation loans — when they help vs rate traps

**Genuinely helps when all four hold:** (a) offered all-in APR < weighted-average APR of debts replaced; (b) fees don't erase the gap; (c) term ≤ current payoff horizon (no term-extension trap); (d) the behavior changes — cards paid off and spending stopped. Re-accumulating card debt on top of the loan is the #1 failure mode and must be named.

**September 2026 rate landscape (verified):**
- Bankrate avg personal loan: **12.44%** (700 FICO, $5k, 3-yr term; Sept 16–23, 2026). Excellent credit as low as **5.96%**.
- MonitorBankRates avg (Sept 21, 2026): personal loan **10.88%**, "debt consolidation loan" **10.54%**, home equity loan **6.77%**, HELOC **6.75%**.
- Credible marketplace closed-loan avg for *debt consolidation purpose*: **20%** (avg score 705); for *credit card refinancing*: **18%**.
- Credit unions: national avg **10.64%**; federal credit unions legally capped at **18%**.

**Rate traps to flag:**
- **Origination fees** (1–8%): often deducted from proceeds — a $10,000 loan at 6% fee puts only $9,400 in your hands while you owe $10,000. Compare APR (includes fees), not "interest rate."
- **Long terms:** 7-year "low payment" loans can cost more total interest than the cards. Always compare total interest.
- **Secured loans:** home equity at ~6.77% looks cheap until you remember the house is collateral. Unsecured card debt becomes secured-against-your-home debt.
- **"Debt relief/settlement" companies:** charge fees, trash credit, and forgiven debt is generally taxable income (1099-C).
- **36% APR subprime lenders:** legal in many states; worse than the cards.

**Product rule:** never present the *average* consolidation rate as the user's rate. Require the actual prequalified offer (soft pull — no score impact) before running the comparison.

---

## PART 2 — IDLE CASH (September 2026)

### 2.1 Top high-yield savings rates — observed data

As reported by aggregators Sept 24–25, 2026. **Rates are variable and change without notice — verify on the bank's own page before acting.** Presented as data, not a ranking.

| Account | APY (as reported) | Minimums / conditions to earn it |
|---|---|---|
| Go2bank savings vault | up to 4.50% | On balances up to $5,000; checking must be active and in good standing |
| St. Mary's Credit Union | 4.50% | On balances up to $50,000; membership required |
| Elevault | 4.34% | No minimum, no requirements |
| E*TRADE Premium Savings | 4.25% | Rate guaranteed 6 months; promo bonus (up to $800 w/ code) is separate — don't confuse bonus with rate |
| Axos ONE | up to 4.21% | $1,500+/mo qualifying direct deposits AND $1,500 avg daily balance |
| Happen Bank LevelUp | 4.20% | $250+/mo deposits; otherwise 3.00%; top rate applies to first two statement cycles |
| Newtek Bank | 4.20% | $100 minimum to open; no minimum balance |
| Abound Credit Union | 4.25% | On balances up to $25,000; membership required |
| Pibank | 4.10% | No minimum, no requirements |
| CIT Bank Platinum Savings | up to 4.35% | On balances over $5,000 (tiered) |

**Context:** FDIC national average savings rate: **0.38%** (Sept 2026). Top-1% average: **3.94%**. Fed raised the funds rate 25bp at its September 2026 meeting (first hike since 2023); target range now ~3.75–4.00%, with officials signaling at least one more hike possible in 2026. HYSA rates typically follow the Fed with a lag.

⚠️ **Verification caveats:** "up to" rates are tiered or capped (Go2bank caps at $5,000; Varo pays 5% on the first $5,000 then 2.50% — a blended rate, not 5%). Credit-union membership is often geography- or employer-restricted — *varies by state*. Promotional rates expire (Happen's two-statement-cycle window, E*TRADE's 6-month guarantee).

### 2.2 The math (framing)

$10,000 for one year:
- Checking at 0.01% APY → **$1.00**
- HYSA at 4.20% APY → **$420.00**
- **Difference: $419/year = $34.92/month** — for moving money once.

Honest framing: *"Your checking account pays you $1 a year on $10,000. The same $10,000 elsewhere pays $419. The move takes 15 minutes and one ACH transfer."* At higher balances the number scales linearly — $25,000 idle is ~$1,048/year left on the table.

⚠️ Keep the framing net of reality: the $419 is taxable interest income (1099-INT). And the app must never imply the rate is locked — HYSAs are variable.

### 2.3 Before moving cash — the checklist

1. **FDIC limits:** $250,000 per depositor, per insured bank, per ownership category. Joint accounts get $500,000. Over the limit → spread across banks or use different ownership categories (individual vs joint vs trust).
2. **Fintech sweep programs:** some apps sweep cash across "partner banks" — verify *which* banks hold the funds and that your total per bank stays under $250k. Pass-through FDIC insurance depends on proper titling; "we sweep to partner banks" is not the same as "your deposits are FDIC-insured."
3. **Transfer times:** ACH takes 1–3 business days; new external accounts are often held 2–5 days. Wires are same-day but cost $15–30. Keep a bill-pay buffer in checking during the move.
4. **Direct deposit routing:** switching DD takes 1–2 pay cycles to take effect. Overlap the accounts; do not close the old account until DD *and* autopays are confirmed moved.
5. **Emergency fund sizing:** 3–6 months of *essential* expenses stays liquid (HYSA — not a CD). One month of bills stays in checking to avoid overdrafts. Only *above* that is "idle cash" eligible to move.
6. **State-tax angle:** HYSA interest is fully taxable at federal + state level. In high-tax states (CA, NY, NJ), Treasury bills or Treasury money-market funds (state-tax-exempt) can beat a higher HYSA APY on an after-tax basis. *Varies by state — flag, don't compute silently.*

### 2.4 Alternatives: CDs, T-bills, money market funds

| Vehicle | Yield (Sept 2026) | Liquidity | Insurance / risk | Min / access |
|---|---|---|---|---|
| HYSA | up to ~4.50% (variable) | Instant | FDIC to $250k | Often $0 |
| CD, 12-month (best) | ~4.10–4.50% (Lincoln County CU 4.50%, $1k min) | Locked; early-withdrawal penalty (typically 3–12 months' interest) | FDIC to $250k | $500–$1,000 typical |
| CD, 60-month (best) | 4.95% (Raymond James Bank, $1k min) | Locked 5 years | FDIC | $1,000 |
| No-penalty CD | ~3.90% (11-mo, per one issuer) | Withdraw after ~7 days, no penalty | FDIC | $1,000 typical |
| T-bills (13-week) | ~4.07% (Sept 14 auction) | Hold to maturity or sell on secondary market | U.S. government; **state/local tax exempt** | $100 via TreasuryDirect |
| T-bills (26-week) | ~4.20% (Sept 14 auction); ~4.28% secondary Sept 21 | Same | Same | $100 |
| Money market fund (e.g., Schwab SWVXX) | 3.52% 7-day SEC yield (Sept 16) | T+1 settlement | **Not FDIC-insured** (SIPC covers brokerage failure, not fund losses); $1 NAV not guaranteed | Often $0–$3,000 |
| Money market fund (Vanguard VMRXX) | ~3.7% dividend yield | T+1 | Same as above | $3,000 |

**Liquidity ranking:** HYSA (instant) → money market fund (next day) → T-bills (hold or sell) → CDs (penalty to exit).

**When each wins:** HYSA for emergency funds and anything needed within months. T-bills for 4–52 week horizons *in high-tax states* (state-tax exemption is the edge). CDs when the rate is locked and the money genuinely won't be needed (flat curve in Sept 2026 means little premium for going long — top 6-mo, 12-mo, and 5-yr CDs sit in a tight ~4.0–4.6% band, so short terms keep optionality). Money market funds for cash already inside a brokerage.

**CD promo specials** (e.g., Southland CU 9.00% 9-mo, Financial Partners CU 6.00% 8-mo) are real but member/geography-restricted (LA/Orange County; select CUs) — *varies by state*, verify eligibility before showing.

### 2.5 Disclaimers the app must carry

- **Not financial advice / not a recommendation.** Rates are data snapshots; the user decides.
- **Rates are variable** (HYSA, money market) — the number shown today can change tomorrow. Show the *as-of date* on every rate.
- **State variation:** credit-union eligibility, state-tax treatment of T-bill interest, and muni money-market relevance all vary by state.
- **Tax:** HYSA/CD interest is taxable income (1099-INT). T-bill interest is exempt from state/local tax but not federal.
- **Never move emergency money into a lockup.** The app should refuse to suggest CDs for the emergency-fund portion.

---

## SOURCES & VERIFICATION NOTES

- HYSA rates: Motley Fool "Top High-Yield Savings Accounts… Sept. 25, 2026" and WSJ BuySide "Today's High-Yield Savings Rates for September 25, 2026" (both crawled Sept 25, 2026; consistent with each other). FDIC national average 0.38% via WSJ/FDIC.
- CD rates: WSJ BuySide "Today's CD Rates for September 25, 2026"; CDValet Sept 2026 data; FDIC national avg 12-mo CD 1.71–1.73%.
- T-bill yields: Sept 14, 2026 Treasury auction results (13-week 4.066%, 26-week 4.203%) and Sept 21 secondary levels (~4.08% / ~4.28%), via cryptobriefing.com Treasury coverage.
- Balance-transfer terms: Forbes Advisor Sept 2026 comparison via curiosityfacts.com; issuer terms cited (wellsfargo.com, applications.usbank.com); NerdWallet/WalletHub Sept 2026 coverage via 247findscenter.com; Motley Fool (avg card APR ~21%, May 2026); NerdWallet Feb 2026 trends (avg ~22%).
- Personal/consolidation loan rates: Bankrate Monitor (12.44% avg, Sept 16–23, 2026); Credible marketplace closed-loan data (Sept 2025–Aug 2026); MonitorBankRates daily averages (Sept 21, 2026).
- Money market yields: Schwab Asset Management (SWVXX 7-day yield 3.52%, Sept 16, 2026); mutualfunds.com (VMRXX, SNVXX, Sept 2026).
- Fed policy: September 2026 25bp hike (first since 2023), funds rate ~3.75–4.00%, via WSJ BuySide and Credible rate coverage.
- Payoff simulations: computed in Python (monthly compounding, minimum = interest + 1% of balance floored at $25, no new spending). Rerun with the user's actual balances before presenting — the example numbers are illustrative.
