# Competitor feature details — 2026-09-26

Deep dive supporting Vishnu's feature-by-feature "why is each Upmore feature better" test and the launch-readiness reassessment. Public-web evidence only; every claim below carries its source URLs. This file only; no other files touched.

Bottom line up front: on a straight feature checklist, Upmore's portfolio-wide debt sequencing, idle-cash dollar-gap analysis, personal tax positioning (W-4 / credits / quarterly), insurance adequacy with honest "you're fine" outcomes, and income-side tools (pay benchmarking, freelance rates, late invoices, earn routes) have no verified equivalent in Monarch, Rocket Money, YNAB, Credit Karma, or Empower. Where competitors genuinely lead — YNAB's zero-based budgeting integration of its Loan Planner, Empower/Monarch's investment and retirement portfolio analysis, Rowan's authorized real-world execution — this file says so. "Better" on features does **not** equal launch-ready: the blockers from the 2026-09-26 assessment (demo-data masking, SimpleFIN failure masking, owner-authenticated mobile verification, transaction-pipeline traceability, incomplete sweep) still stand.

---

## 1. YNAB — Loan Planner

### Inputs
- Current balance, interest rate, monthly payment for a single loan account
- A target payoff date to test; a monthly-payment amount to test; a one-time payment to test

### Outputs
- Projected payoff timeline/date, interest remaining, time remaining
- How extra or one-time payments change payoff time; interest saved
- Real-time what-if output and a burndown-style visualization

### Limitations
- Models **one loan at a time**, not the whole debt portfolio. No avalanche-vs-snowball comparison across all debts, no generated payoff order.
- YNAB itself reportedly does not recommend Loan Planner for credit cards (designed for student, auto, personal, medical debt).
- No refinancing comparison, no 0%-promo-window logic, no per-month interest-cost readout as a CFO line item.
- Requires accurate manual balance/rate inputs; no payment execution; paid YNAB subscription required.

### Upmore comparison
- Upmore advantage: portfolio-wide sequencing — which balance to attack first across all debts, avalanche vs snowball comparison, refinance-vs-paydown, 0% promo windows closing, interest cost per month. YNAB's Loan Planner is a single-loan what-if slider.
- YNAB advantage: the slider sits inside a mature zero-based budgeting product, so the payment decision flows straight into the budget you already run. Upmore does not try to be a full budgeting replacement.
- Verdict: Upmore wins on the CFO question ("which balance to attack first, what does it cost per month"); YNAB wins on budget integration.

### Evidence
- https://www.cfosilvia.com/blog/cfo-silvia-vs-ynab
- https://lendedu.com/blog/best-debt-payoff-app/
- https://wallethub.com/edu/b/best-debt-payoff-plan/153300
- https://frugalharpy.com/debt-payoff-tracker-app/

---

## 2. Rocket Money — debt-paydown capability

### Inputs
- Linked liability balances (cards, loans, mortgages) flow into the dashboard/net-worth view.

### Outputs
- Aggregated view of what is owed and net worth including liabilities; subscription/bill reductions that can theoretically free cash for debt payments.

### Limitations
- **No dedicated strategic debt-paydown simulator found.** No evidence of a snowball/avalanche calculator, generated payoff order, payoff date, interest-saved comparison, or multi-debt optimization.
- Rocket Money publishes educational articles on snowball vs avalanche but the product itself does not appear to compute them.
- This supersedes the earlier competitor-matrix claim that "Rocket Money Premium has debt paydown" — evidence says it tracks debt and frees cash, not that it sequences it.

### Upmore comparison
- Clear Upmore advantage on debt sequencing: Upmore computes the payoff order, cost, and tradeoffs; Rocket Money shows balances and finds cancellable spending. These are adjacent but not the same job.
- Rocket Money advantage: bill negotiation and subscription cancellation as a service (it acts with providers). Upmore intentionally does not.

### Evidence
- https://econumo.com/posts/best-debt-payoff-apps/
- https://github.com/greigh/fihaven/blob/HEAD/client/public/rocket-money-alternative.md
- https://www.rocketmoney.com/learn/debt-and-credit/making-the-debt-snowball-method-work-for-you?p=ORGLearn&c=Learn-OrganizeDebtCovid
- https://thethriftyfamily.com/best-debt-payoff-apps-save-time-interest/

---

## 3. Monarch Plus — forecasting and tax-related tools

### Inputs
- Connected accounts; long-term events (retirement, career breaks, moves); ordinary spending categories (dining, childcare, travel); business and rental-property records for Plus.

### Outputs
- Multi-scenario future forecasting linking long-term events to ordinary spending
- Plus adds: business/rental tracking separated from personal, profit-and-loss reports and tax-preparation organization, advanced investment analysis (asset allocation, gains/losses), an estate-planning perk

### Limitations
- The "tax" capability in Plus is **business tax-preparation organization / P&L**, not forward-looking personal tax positioning. No evidence of: W-4 accuracy checks, EITC/CTC qualification gating, quarterly estimated-tax calculation, HSA/401(k) room timing.
- One third-party comparison describes Plus retirement planning as a single trajectory rather than Monte Carlo; treat as third-party evidence, not an official Monarch claim.

### Upmore comparison
- Upmore advantage: forward-looking personal tax positioning — W-4 accuracy, credits left on the table, quarterly estimates for gig work, HSA/retirement timing. Monarch Plus organizes tax paperwork for businesses; it does not answer "is my withholding right" or "what credits am I leaving."
- Monarch advantage: investment and retirement portfolio analysis with scenario forecasting; business/rental bookkeeping; estate-planning perk. Upmore is not a portfolio-analysis product and must not present itself as one.
- Earlier wording "tax-impact tools" is too broad and is corrected here.

### Evidence
- https://www.morningstar.com/news/pr-newswire/20260421la39327/monarch-launches-premium-tier-monarch-plus
- https://www.topconsumerreviews.com/best-personal-finance-software/reviews/monarch-money.php
- https://curlbudget.com/articles/curl-budget-vs-monarch-money/
- https://beelinger.com/monarch-money-review/

---

## 4. Monarch AI Assistant — capabilities and limits

### Inputs
- The user's connected Monarch data (accounts, transactions, budgets, investments).

### Outputs
- Conversational Q&A: ask about spending, cash flow, net worth; assistant pulls insights directly from connected accounts (Motley Fool: built on GPT-4 via OpenAI, data kept private, not used to train public models)
- AI transaction auto-categorization (~85–90% accuracy claimed by a third-party review), recurring-subscription detection, personalized spending-trend and cash-flow insights, CFP-backed goal advice per one review

### Limitations
- No evidence it can **act** on accounts: no budget changes, no cancellations, no money movement, no bill negotiation found in any source. It answers and categorizes.
- No official capability/limitation statement or "not financial advice" disclaimer text was located in public sources during this search. Claims about its exact limits beyond "answers questions over connected data" should be marked unverified, not asserted.

### Upmore comparison
- Different jobs. Monarch's assistant is a conversational mirror over tracked data inside a budgeting product; it does not sequence debt, find idle cash, or position taxes. Upmore's CFO features compute specific dollar answers (payoff order, idle-cash gap, withholding accuracy) from user data. Neither executes money movement.
- Honest note: a conversational assistant over connected accounts is a UX pattern Upmore does not have; Upmore's "explain" layer is card-based, not conversational.

### Evidence
- https://www.fool.com/the-ascent/personal-finance/monarch-money-review/?luri=%2Fpersonal-finance%2Froostermoney-review%2F&furi=%2Fpersonal-finance%2Froostermoney-review%2F&ltyp=txt
- https://www.fool.com/money/banks/articles/the-top-ai-money-management-apps-for-high-income-families/
- https://www.bestaitools.com/tool/monarch/

---

## 5. Rocket Money — Rowan

### Inputs
- Connected Rocket Money data (accounts, transactions, subscriptions, bills, balances); user text messages; user authorization to act with providers.

### Outputs
- Proactive texts: free trials nearing conversion, subscription price increases, new/unused subscriptions, unexpected fees, low balances, spending/budget items needing attention, weekly summaries
- Q&A: spending questions, transaction categorization help, safe-to-spend estimates
- **Action initiation**: subscription/free-trial cancellation, bill negotiation, refund pursuit, payment reminders, automated savings rules (e.g., purchase roundups into an HYSA)
- Execution model: specialized agents plus rule-based code plus human verification; contacts providers and later confirms completion

### Limitations
- Launched August 2026, initially limited to selected **Premium+** users (reported $15/month). Limited release as of September 2026.
...[truncated 11885 chars]- Action requests are not always instant; cancellation/negotiation may start a process that completes later. The user must authorize Rocket Money to act on their behalf.
- Rowan actually **moves money** (automated savings transfers into an HYSA) and transacts with merchants — an authorized-execution model.

### Upmore comparison
- Rowan leads at authorized real-world execution: cancel this, negotiate that, move savings automatically. Upmore's binding policy forbids all of that — Upmore never holds, pools, forwards, transfers, or moves money, and "execute" means assemble/prefill only, with the user doing every final tap.
- That is an intentional product difference, not a gap to close: Rowan's execution is precisely the money-transmission and provider-action surface Upmore's constraints rule out. On the CFO analysis side (debt sequencing, idle-cash gap in dollars, tax positioning), Rowan does not compete — it is an assistant over subscriptions and bills.
- Neutral framing: Rowan is the better "do it for me" agent; Upmore is the better "tell me the exact dollar answer" CFO. They do not overlap much.

### Evidence
- https://robberger.com/rocket-money-review/
- https://www.stocktitan.net/news/RKT/rocket-money-s-rowan-rewrites-what-ai-can-do-in-personal-olqznanz2unp.html
- https://www.wallstreetsurvivor.com/rocket-money-review/
- https://www.morningstar.com/news/pr-newswire/20260825de33238/rocket-moneys-rowan-rewrites-what-ai-can-do-in-personal-finance
- https://nypost.com/2026/08/25/shopping/rocket-moneys-rowan-ai-assistant-puts-your-finances-one-text-away/
- https://coverager.com/rocket-money-launches-ai-financial-assistant-rowan/

---

## 6. DoNotPay — Missing Money

### Inputs
- Full name including middle name, current and previous addresses, contact information.

### Outputs
- Search across state and federal unclaimed-property databases and former locations across the US; if a match is found, "Claim My Property" is said to file the claim on the user's behalf.

### Limitations
- Supporting documents may still be required by the state: ID, SSN proof, address proof, signed/notarized claim forms, relationship documentation — DoNotPay cannot waive state requirements.
- Pricing is **conflicting in sources**: DoNotPay's own pages say the feature is included in a DoNotPay subscription with no percentage of recovered property charged; a 2025 interview described a planned standalone MissingMoney app as "completely free." Whether the current in-product feature costs nothing beyond subscription, and what the subscription costs, was not independently verified. Do not quote a price.

### Upmore comparison
- DoNotPay's flow is arguably more done-for-you (it files the claim on your behalf; Upmore assembles/prefills and the user submits). Upmore's unclaimed-property workflow is one feature inside a full CFO product; DoNotPay is a legal-services bundle. Comparable on this single feature; Upmore's differentiator is everything around it.

### Evidence
- https://donotpay.com/learn/unclaimed-inheritance-money/
- https://donotpay.com/learn/unclaimed-money-georgia/
- https://donotpay.com/learn/unclaimed-money-reviews/
- https://donotpay.com/learn/unclaimed-money-new-mexico/
- https://donotpay.com/learn/unclaimed-money-vermont/
- https://knowtechie.com/empowering-consumers-dontpay/

---

## 7. Credit Karma — unclaimed-money search

### Inputs
- Name and state, searched one state at a time. Members get proactive matching: Credit Karma uses credit-report data (name, current and former addresses, former names/aliases) to monitor states without the user initiating a search.

### Outputs
- Matches against state unclaimed-property databases; links the user to the correct state site/claim process; member push alerts when new matches surface; can also search other people's names as a heads-up.

### Limitations
- **Searches one state at a time** in the manual flow (a Refinery29 interview with a Credit Karma exec described proactive monitoring of seven states for members at that time — treat the "seven" figure as dated, ~2017). DoNotPay claims multi-state search in one pass; Credit Karma does not claim that.
- Does **not file claims**: it links you to the state database and guides you through the state's own process; the user completes the claim with the state, including documentation and notarization where required.
- Free to use.

### Upmore comparison
- Credit Karma is a solid free discovery tool but stops at discovery + handoff; Upmore's workflow carries the user through the claim assembly. Neither product's core is unclaimed property — for Credit Karma it is a Resources-tab side tool, for Upmore one of several CFO features.
- DoNotPay's claim-filing is the most done-for-you of the three.

### Evidence
- https://www.crediful.com/credit-karma-review/
- https://donotpay.com/learn/credit-karma-unclaimed-money/
- https://moneyat30.com/credit-karma-unclaimed-funds-tool/
- https://www.refinery29.com/en-us/where-to-find-unclaimed-money

---

## 8. Empower — Retirement Planner and cash flow

### Inputs
- Linked accounts (checking, savings, credit cards, loans, investments) — the planner's defaults are built from real aggregated balances; more links = better results.
- User-set: age, income, annual savings goal, retirement age, Social Security withdrawal age, other retirement income streams, retirement spending goal.
- Life-event overlays: wedding, home purchase/upgrade, car purchase, education spending, vacation, charity/gift, dependent support, healthcare, renovation.
- Income events: Social Security, annuity, inheritance, pension, rental income, property sale/downsize, work during retirement, other income — each tagged before-tax or after-tax (Social Security always before-tax), with inflation treatment per type. RMDs assessed from tax-deferred accounts at 73 per the IRS table.

### Outputs
- Projected portfolio value, Social Security estimates (user + spouse), detailed year-by-year cash-flow table extending past age 90
- "Are you on track" retirement assessment using **Monte Carlo simulations** over real linked data
- Scenario recalculation: add events/goals and see the future change
- Cash-flow planner: monthly money-in vs money-out, line-chart view, month-over-month comparison
- Investment checkup: current vs target asset allocation, fee analyzer comparing fund fees to alternatives

### Limitations
- Retirement planner is portfolio-centric: it answers "will my savings last," not "what should I do with idle cash today," "is my withholding right," or "am I insured." No tax-positioning guidance (W-4, credits, quarterly) found; no income benchmarking; no insurance adequacy.
- Cash-flow tool is a tracker (in vs out, month comparison), not a forward-looking CFO planner; one reviewer notes Rocket Money's cash-flow breakdown is more granular.
- Investment checkup recommendations are generic (e.g., "add bonds, use index funds") and function partly as a funnel to advisor calls.
- Free dashboard; the business model is upsell to wealth management.

### Upmore comparison
- Empower wins decisively at investment and retirement portfolio analysis: Monte Carlo over real linked balances, RMD handling, allocation vs target, fee analysis. Upmore is not a portfolio product and should not claim parity.
- Upmore wins on the near-term CFO questions Empower never asks: idle cash sitting at ~0% vs HYSA rates in dollars, W-4 accuracy, quarterly estimates, insurance adequacy, runway, income benchmarking. Empower's planner starts at "linked investments"; Upmore's CFO starts at "the cash in your checking account."
- Overlap is small: both show cash flow, but Empower's is retrospective tracking and Upmore's CFO is forward-looking decision math.

### Evidence
- https://www.financialsamurai.com/personal-capital-retirement-planner-review/
- https://www.financialsamurai.com/empower-personal-dashboard-review/
- https://www.safesmartliving.com/empower-retirement-reviews/
- https://financebuzz.com/personal-capital-review?utm_source=msn&utm_medium=feed&synd_postid=17238&synd_backlink_title=Visit+Empower&synd_backlink_position=8&synd_slug=personal-capital-review
- https://docs.empower.com/PDF/p/misc/Empower_Retirement_Planner.pdf
- https://www.gocurrycracker.com/personal-capital-review/

---

## 9. Capability checks — do any competitors offer these?

### a) Idle-cash / HYSA opportunity-cost analysis
- **No, for the five named competitors.** No evidence Monarch, Rocket Money, YNAB, Credit Karma, or Empower compute "your checking balance at ~0% vs a HYSA rate = $X/year left on the table."
- Found in the wild, two adjacent products:
  - **Edwealth** (2026 high-earner product): its "Cash check-up" explicitly asks whether cash is working or just sitting — the closest direct equivalent found. (Third-party comparative article; Edwealth is a small/obscure product, not a market leader.)
  - **Rivo** (2026 fintech, raised $3.1M, out of beta): autopilot that automatically moves idle cash into short-term T-bills and back before bills are due. But Rivo *moves money itself* — the exact thing Upmore's binding policy forbids — and it is a new entrant, not an established competitor.
- Verdict: **Upmore differentiates.** A read-only dollar-gap analysis (no money movement, no account opening) has no verified equivalent among the named competitors.

Evidence:
- https://investor.wedbush.com/wedbush/article/globeprwire-2026-7-16-wealthfront-vs-empower-vs-edwealth-which-fits-a-high-earner-in-2026
- https://www.thisweekinfintech.com/p/exclusive-from-self-driving-cars-to-self-driving-money-inside-rivo-s-bet-on-idle-cash
- https://rivofi.com/faqs

### b) Insurance adequacy checks
- **No.** No evidence any of the five named competitors offers coverage-gap analysis (life/disability/umbrella/liability vs need, with honest "you're fine" outcomes).
- Insurance-adequacy tooling exists only in niche/obscure places: a UK app's public feature docs (fynla), hackathon/personal projects, and a generic AI-skill template — none are shipping mainstream consumer products competing with Upmore.

Evidence:
- https://github.com/stoff73/fynla/blob/HEAD/appMapping/fynlaFeature.md
- https://github.com/dheera525/retirement-insurance-simulator

### c) Income vs market-pay benchmarking
- **No.** No evidence any of the five named competitors offers salary/market-pay benchmarking, raise-timing guidance, freelance-rate tools, or late-invoice chasing. Salary benchmarking exists as HR/employer software (compensation tools), not inside consumer finance apps.

Evidence:
- https://www.anywherer.com/best-salary-benchmarking-software/ (employer-side tooling; confirms the category lives outside consumer finance apps)

### d) W-4 withholding guidance
- **No.** No evidence any of the five named competitors offers W-4 accuracy checks. The IRS itself ships a free Tax Withholding Estimator (updated March 2026 for the One, Big, Beautiful Bill provisions: no tax on tips/overtime, car-loan interest, senior deduction); a 2026 third-party comparison notes a competitor's tax check-up surfacing the gap between standard 22% withholding and the user's actual situation — implying the incumbents do not do this. Monarch Plus's tax features are business tax-prep organization, not personal withholding.

Evidence:
- https://movies.einnews.com/pr_news/899224785/updated-tax-withholding-estimator-lets-millions-of-taxpayers-take-one-big-beautiful-bill-changes-into-account-when-calculating-their-withholding
- https://investor.wedbush.com/wedbush/article/globeprwire-2026-7-16-wealthfront-vs-empower-vs-edwealth-which-fits-a-high-earner-in-2026

### e) Quarterly estimated-tax guidance
- **No.** No evidence any of the five named competitors computes quarterly estimated taxes for gig/self-employment income. The capability exists in standalone open-source/paid tools (side-gig tax calculator with 1040-ES worksheet lines, an Etsy estimated-tax strategy analyzer covering safe harbor and per-paycheck withholding adjustments) — confirming it is a known unserved need, not a competitor feature.

Evidence:
- https://github.com/jpchip/side-gig-tax-calculator/blob/HEAD/README.md
- https://www.etsy.com/listing/4571675056/estimated-tax-strategy-analyzer?utm_source=OpenGraph&utm_medium=PageTools&utm_campaign=Share
- https://github.com/eagleeyevisionlabz/wayland-m3ta-0s/blob/HEAD/src/process/resources/skills-library/bodies/skills/personal-finance/quarterly-tax-estimator/SKILL.md

---

## 10. Head-to-head: where each side genuinely wins

| Upmore CFO feature | Best competitor | Honest verdict |
|---|---|---|
| Debt sequencing (portfolio-wide avalanche/snowball, refi compare, promo windows, $/mo interest) | YNAB Loan Planner (single-loan what-if) | **Upmore wins** on the CFO question; YNAB wins on budget integration |
| Idle-cash dollar gap | None among named competitors (Edwealth/Rivo adjacent) | **Upmore wins** |
| Tax positioning (W-4, credits, quarterly, HSA/401k timing) | None among named competitors (IRS's own estimator is the reference) | **Upmore wins** |
| Insurance adequacy with "you're fine" outcomes | None found | **Upmore wins** |
| Runway (weeks if income stopped) | None found as a productized feature | **Upmore wins** |
| Income side (pay benchmarks, freelance rates, late invoices, earn routes) | None among named competitors | **Upmore wins** |
| Unclaimed-property workflow | DoNotPay (files claim for you), Credit Karma (free discovery) | **Competitors comparable or better** on done-for-you-ness; Upmore's is one feature among many |
| Investment/retirement portfolio analysis | Empower (Monte Carlo, RMDs, fee analysis), Monarch (allocation, scenarios) | **Competitors win** — Upmore is not a portfolio product |
| Conversational assistant over connected data | Monarch AI Assistant | **Competitor leads** on UX pattern; different job from Upmore's CFO math |
| Authorized real-world execution | Rowan (cancels, negotiates, moves savings) | **Competitor leads** — and Upmore intentionally cannot follow (binding no-money-movement policy) |

## Launch-readiness note (for the reassessment)

Winning a feature checklist does not make Upmore launch-ready. As of 2026-09-26 the open blockers stand: demo/live financial-data ambiguity (authenticated users can still see demo values; SimpleFIN failure can be silently masked; `planData()` uses functional defaults for missing inputs), no real owner-authenticated mobile verification (Vishnu must personally complete Google consent/auth, bank/MFA, and verify identity across splash/Home/Guide/You plus SimpleFIN/Chase through the proxy), no full deterministic transaction-pipeline verification (categories, pending, transfers, refunds, duplicates, balances, 90-day clamp, figure traceability), the 50-agent sweep was incomplete (35 done, 15 errored on 429s and were only locally reproduced), and claim end-to-end testing, accessibility/visual audit, seven-CFO-screen hands-on testing, Guide-path regression, and production-console testing remain open. **Not yet verified launch-ready.**
