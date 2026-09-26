# Personal Finance App Benchmarks (2026) — Competitive Analysis
Research completed 2026-09-26.

## Pricing Summary

| App | Price | Free tier |
|---|---|---|
| **Monarch Money** | Core: $14.99/mo or **$99.99/yr**; Plus (2026 new tier): **$199/yr** — advanced long-range planning, scenario modeling, small-business finance | 7-day trial only |
| **YNAB** | **$14.99/mo or $109/yr**; students free 12 mo; YNAB Together shares with up to 6 | 34-day trial only |
| **Empower** (Personal Capital) | Dashboard **free forever**; Wealth Management **0.89% AUM/yr** ($100k min; tiers down to 0.49% at $10M+) | Free dashboard |
| **Rocket Money** | Free tier; Premium **$7–$14/mo pay-what-you-want**; Premium+ $15/mo (adds AI assistant Rowan, no bill-negotiation success fee) | Yes (basic) |
| **Copilot Money** | **$13/mo or $95/yr**; iOS/Mac/web only, no Android | 30-day trial only |
| **Fidelity** | Planning & Guidance Center **free** for account holders; Fidelity Go robo: **$0 under $25k, 0.35% above** | Free tools |
| **Betterment** | Digital **0.25%/yr** ($0 min; $5/mo under $24k); Premium **0.65%/yr** ($100k min, human advisors) | — |
| **Wealthfront** | **0.25%/yr**, $500 min; no human advisors | — |

Sources: Monarch/YNAB/Rocket pricing — thepennyhoarder.com, gettidyflow.com, wallstreetsurvivor.com, northvilletech.com; Empower — fincrati.com, wallethacks.com; Copilot — pocketguard.com; Fidelity — fidelity.com; Betterment/Wealthfront — mikimoneyai.com, betterment.com, wsj.com.

## Feature Matrix

| Feature | Monarch | YNAB | Empower | Rocket Money | Copilot | Fidelity | Betterment / Wealthfront |
|---|---|---|---|---|---|---|---|
| Bank account aggregation | ✓ (13k+ institutions, Plaid/MX/Finicity) | ✓ (banks + cards) | ✓ (Yodlee) | ✓ (Plaid) | ✓ | ✓ | Partial (external linking for net-worth view) |
| Debt payoff planning | Partial (goals; Plus forecasting) | ✓ (loan payoff simulator, interest-saved) | ✗ | ✓ (Premium debt paydown) | ✗ | ✗ | ✗ |
| Tax planning | Partial (Plus: tax-impact tools) | ✗ | Partial (TLH in managed tier) | ✗ | ✗ | Partial (no TLH in Go) | ✓ (TLH; Wealthfront: daily TLH + direct indexing $100k+) |
| Insurance adequacy check | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Income benchmarking | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Unclaimed money search | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Human advisor access | ✗ (AI assistant only) | ✗ (coach directory, unpaid) | ✓ 0.89% AUM, $100k min, CFP advisors | Partial (chat experts, Premium) | ✗ | ✓ (branch/wealth advisors; Go includes coaching) | Betterment Premium ✓ 0.65%/$100k; Wealthfront ✗ |

Key notes:
- **No major PFM app does insurance adequacy or income benchmarking** — confirmed via search; insurance-adequacy tooling exists only in AI-agent/open-source projects, not mainstream apps.
- **Unclaimed money** is offered by adjacent players only: DoNotPay ("Missing Money" feature) and Credit Karma (unclaimed-money search). None of the 7 benchmarked apps have it.
- YNAB explicitly does *not* track investments — "no holdings view". Its strength is debt payoff and behavior change.
- Empower's free dashboard is a lead funnel for its wealth-management upsell (advisor calls above ~$100k aggregated assets).
- Monarch's AI assistant is positioned as a "mirror rather than a mechanic… not meant to give financial advice".

## What it legally takes to call yourself an "investment advisor" in the US

Under the Investment Advisers Act of 1940, anyone who **for compensation** gives advice about securities must register as an investment adviser (RIA) — with the **SEC** if they have ≥$100M in regulatory AUM (or must register in 15+ states), otherwise with **state securities regulators**, filing Form ADV (Parts I/II) through the IARD system. The individual giving advice must pass the **Series 65** (Uniform Investment Adviser Law Exam) or the Series 7 + 66 combination — waived in most states for CFP, CFA, ChFC, CIC, or PFS designees. Registration imposes a **fiduciary duty** (duties of loyalty and care — act solely in the client's best interest, disclose conflicts). Using the title "investment advisor/adviser" while giving personalized securities advice without registration is illegal; only general financial *education* (no personalized recommendations, no compensation tied to advice) stays outside the registration trigger.

## Competitive takeaway for Upmore

The benchmarked apps cluster into budgeting trackers (YNAB, Monarch, Copilot, Rocket Money), a free aggregation funnel (Empower), a brokerage's free planner (Fidelity), and robo-advisors (Betterment/Wealthfront). **None** of the seven offers insurance adequacy checks, income benchmarking, or unclaimed-money search — and only the expensive AUM-based tiers offer human advisors (0.65–0.89%). The "best finance app" gap is exactly the CFO layer: debt sequencing, idle cash, tax positioning, insurance adequacy, and found-money — none of which the incumbents productize.
