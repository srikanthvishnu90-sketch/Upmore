# Upmore "Nobody Should Win" Build Plan — 2026-09-26

Source: three competitor teardowns in ~/workspace/research/:
- competitor-budget-home-screens.md (Monarch, YNAB, Rocket Money, Copilot, EveryDollar)
- competitor-cancel-claim.md (Rocket Money, DoNotPay, Trim, BillShark, MissingMoney/NAUPA, Credit Karma)
- competitor-tracking-investment-gaps-2026-09-26.md (Monarch, Empower, YNAB, Rocket Money, Credit Karma, Fidelity, Schwab, Kubera)

## Where we already win (keep + extend)
- Dollarized fee analysis ($/year) — only Empower does this; Monarch explicitly doesn't.
- Earn engine (2,100 routes) — no competitor equivalent.
- 7 CFO tools — no competitor equivalent.
- Cancel state machine + "Cancel it for me" execution framework.
- No-guilt design, plain language, no affiliate steering.

## Gaps → build items (this pass)

### SPEC 09 — Subscription defense (vs Rocket Money / Rowan / Trim)
1. Annualized spend on every subscription row + annual total hero ("$X/year on subscriptions") — Rocket Money's framing.
2. Pre-conversion trial countdown warnings (7d + 3d) in the queue — Rowan paywalls this; we do it free.
3. Post-cancel zombie-charge monitoring — nobody does this proactively.
4. Recurring-charge approval queue UI ("Found N repeating charges — confirm") — Monarch-style verification prompt.
5. Bill negotiation call scripts (exact words, pre-filled with bill facts) — free wedge vs 35–60% success fees.
6. Bank-fee waiver scripts from detected fee transactions — DoNotPay-style, free.

### SPEC 07 — Budget report (vs Copilot / Monarch / YNAB / EveryDollar)
7. Spend-pace chart: cumulative actual vs dotted ideal pace (SVG).
8. Projection-colored category bars (on-pace / projected-over / over + pending-recurring outline). No red/green — no-guilt palette.
9. Savings rate card.
10. Age of Money.
11. Committed spending from actual upcoming subscription charges in Safe to Spend (replaces category-average estimate).
12. Month-in-Review auto-summary.
13. Recurring calendar with payday overlay (month grid, 1 tap from Track).

### SPEC 04 — Transactions (vs Monarch / YNAB)
14. Merchant→category rules ("Always put MERCHANT in CATEGORY"), auto-applied to new transactions + apply-to-existing.
15. Bulk recategorize (select mode).

### Net worth — new (vs Monarch / Empower / Kubera)
16. Net worth: bank balances + manual assets (home, vehicle, crypto, other) − liabilities → home hero card + detail screen + monthly snapshots + sparkline.

### SPEC 08 — Investments (vs Empower)
17. Per-holding return % from cost basis.
18. "Trim $X to get back under 25%" rebalance math on concentration flags.
19. Monte Carlo retirement check (analysis-only, labeled assumptions, side-by-side what-if).

### Claim (vs DoNotPay / state sites)
20. Per-state document checklists (51 jurisdictions: notarization threshold, online filing, status URL).
21. Annual re-search reminders when a state is marked searched.

### SPEC 05 — CFO
22. Credit factors tool: factor weights, utilization calculator, what-if math (no score claims).

## Efficiency bar (must be ≤ best competitor)
- Safe to spend: 0 taps (already; keep).
- This month vs last: 0 taps on home (add delta to track strip).
- Budget edit: ≤2 taps inline (Copilot parity).
- Recategorize: 2 taps; rule creation: 3 taps (Monarch parity).
- Recurring calendar: 1 tap from Track.

## Verification
- Existing tests (tests/investments.test.js) stay green.
- Playwright screenshots: home, budget report, investments, claim, transactions, subscriptions.
- Deterministic engine checks for new math (pace chart, age of money, savings rate, Monte Carlo seed).
- Rebuild via src/build-app.py, commit, deploy, verify production HTTP 200.
