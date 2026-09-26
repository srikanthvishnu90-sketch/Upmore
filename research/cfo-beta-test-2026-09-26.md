# Upmore CFO Beta Test + Competitive Benchmark + Launch Verification
Date: 2026-09-26. Tester: Muse (code-level functional verification + independent math).

## 1. Beta test results — all 7 CFO tools

Method: extracted the app's real functions from the production build, ran realistic
fixtures, and cross-checked every number with an independent calculator.

| Tool | Fixture | Result | Verdict |
|---|---|---|---|
| Debt payoff plan | $9k@29.99% + $2k@7.99%, $300 extra | Avalanche $2,904 interest / 23 mo; Snowball $3,434 — matches independent amortization to the dollar | PASS |
| Debt promo | $6k at 0% for 6 mo, revert 26.99% | $770 interest, 20 mo — promo cliff priced correctly | PASS |
| Idle cash | $15k checking at 4.2% HYSA | $629/yr left on the table — arithmetic correct | PASS |
| Tax positioning | 2026 figures | Std ded $16,100/$32,200/$24,150 and all brackets match IRS Rev Proc 2025-32 exactly | PASS |
| Tax marginal rate | $62k single → 12%; $54k MFJ → 10%; $200k single → 24% | Derived from income + filing status, never hardcoded | PASS |
| Gig tax | $30k profit | $900/quarter + $4,239 SE tax — correct | PASS |
| HSA room | $1k contributed, individual | $3,400 room × 12% = $408 savings — correct | PASS |
| Insurance | Income $75k, 2 kids, no life cover | Target $950k (10× + $100k/child), "you're fine" paths present | PASS |
| Runway | $8k liquid, $2.5k/mo burn | 13.9 weeks — correct | PASS |
| Monthly close | Refunds net against categories, not income | Code-verified | PASS |
| Income side | $70k salary, 2.5× multiplier | $84.13/hr floor — correct; BLS medians labeled May 2024 | PASS |
| Guide chat | "which card do I pay first?" | Routes to debtSim, not earn offers (pass2-D1 fix holds) | PASS |

Fixed during this test:
- Wrong code comment ("12% at $54k MFJ" → actually 10%; code was right, comment wrong)
- "Powered by Plaid" → "Secure bank connection via SimpleFIN" (Plaid was never integrated)
- Privacy policy (in-app + PRIVACY_POLICY.md): bank connection is live via SimpleFIN, read-only; date 2026-09-26

## 2. Competitive benchmark — where Upmore wins and loses

Prices verified Sept 2026: Monarch Core $99.99/yr ($14.99/mo), Plus $199/yr; YNAB
$109/yr; Empower free (wealth-management upsell funnel); Rocket Money free +
Premium $6–14/mo; Copilot $95/yr (iOS/Mac only); Betterment/Wealthfront 0.25% AUM.

Upmore wins — no competitor combines all of these in one app:
- Earn routes (money-finding engine) + CFO tools + unclaimed-property search
- Debt sequencer with promo-aware APR and refinance-vs-paydown comparison
- 2026-verified tax positioning (EITC/CTC/HSA gated on user's actual situation)
- Insurance adequacy with "you're fine" outcomes (nobody else says that)
- Free (competitors charge $36–$199/yr)

Upmore loses — honest gaps:
- No investment portfolio management or retirement projections (Empower, Monarch Plus do)
- No human advisors (Empower, Vanguard PAS do — at a price)
- Single-bank SimpleFIN vs Plaid's thousands of institutions
- No credit-score tracking, no bill pay

## 3. The "investment advisor" question — straight answer

Upmore is NOT an investment advisor and must never claim to be one. Under the
Investment Advisers Act of 1940, giving investment advice for compensation requires
RIA registration (SEC or state), fiduciary duty, and licensed personnel (Series 65
or CFP/CFA). Upmore has none of these, recommends no securities, and its own code
says "Educational math only — not financial advice."

The defensible claim: "the best app at finding you money and showing your money
like a CFO." The indefensible claim: "best investment advisors on the planet."
Using the latter in marketing would be a regulatory liability, not a flex.

## 4. Launch verification

READY:
- Build clean, inline JS parses, production HTTP 200 with latest fixes
- Exactly 3 tabs (Home/Guide/You), dark mode only, no affiliate steering in code
- Privacy policy accurate as of 2026-09-26, Terms embedded in-app
- PWA manifest + icons present; service worker installs/activates correctly

STILL OPEN (needs Vishnu, cannot be done by agent):
- Owner live session: Vishnu completes Google sign-in + verifies SimpleFIN/Chase
  sync on his phone; signed-in splash/Home/Guide/You identity check
- Demo-vs-live data ambiguity: authenticated users can still see demo financial
  values without a visible sync-failure state (known gap from 2026-09-26)
- 15 of 50 agent slices errored on rate limits — reproduced locally, not rerun as agents
