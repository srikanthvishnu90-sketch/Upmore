# Post-Connection Flows: Competitor Research + Upmore Spec (2026-09-27)

Research method: help docs, reviews, and step-level teardowns (notably the BudgetBox
onboarding/core-screens teardowns, researched 2026-07-31 from first-party docs). No signups.
Tap counts are teardown-derived estimates, marked ~.

## 1. Monarch Money (primary)

### Connect → first insight, screen by screen
1. Signup: email + password + continue (~3 taps)
2. 5-slide value carousel (5 swipes; teardown criticizes slides 3–4 as redundant)
3. Jobs-to-be-done: "what are you here for?" — consolidated view / shared / investing / free text (1)
4. Acquisition-source question (1)
5. Profile info — deliberately AFTER motivation questions, escalating commitment (2–3)
6. Trial timeline screen — visual trial start / reminder / charge date (1; best trust screen in class)
7. Directed empty dashboard: real UI rendered degraded, ONLY "Add account" tappable (1)
8. Plaid/MX/Finicity Link per institution (~6–8: search, select, credentials in provider UI, MFA, select accounts, done)
9. Celebration animation on each successful link (0)
10. Manual assets afterward — home (address lookup), car (VIN), crypto — so net worth "starts to look real" (optional, ~3–5)

**~20–25 taps to a populated dashboard. But the budget is NOT auto-generated.**

### What auto-generates vs what's manual
| Auto (0 taps) | Manual (user authors) |
|---|---|
| Transaction auto-categorization | Budget — Flex (one flexible number) or Category (line-by-line), user-created |
| Recurring bills/subscriptions detection + reminders | Goals (save-up / pay-down), accounts linked per goal |
| Month in Review: top categories, cash flow, net-worth changes | Category review: rename/disable/create (help docs: "take a few minutes") |
| Cash-flow reports + future-balance forecast | Transaction rules (created while recategorizing) |
| Net-worth tracking (all accounts + manual assets) | Tags |
| Dashboard widgets populate immediately | Dashboard customization (rearrange/hide) |

### Accuracy honesties / dishonesties
- **Honest:** help docs state "every account pulls in a different amount of historical data… the more complete your accounts are, the more accurate your budget, net worth, and reports will be"; "this step doesn't need to be perfect"; if one account won't connect, "move on… Monarch still works with partial data."
- **Dishonest-by-omission:** no thin-data banner — with 2 weeks of history, Month in Review and "forecasts" render with false confidence; no reconciliation — a manual transaction is NOT auto-removed when the matching bank transaction syncs later (documented), so duplicates silently inflate spending; auto-categorization errors require user rules to fix.
- **Best stealable ideas:** constrained dashboard (only the next correct action tappable), celebration per link, trial timeline, flex-vs-category two-mode budgeting.

## 2. Rocket Money (lighter)

1. Signup (~3) → 3 personalization questions: why signed up / financial goals / how found us (3)
2. Spending info questions — income, expenses, goals (2–4)
3. Link first account via Plaid (~6–8)
4. **Instant analysis on FIRST link, 0 further taps:** detected subscriptions ("here are the 7 subscriptions you're paying for") + savings opportunities. This is the payoff-within-seconds pattern.
5. Budget: user-created afterward (income in, expenses, goals).

Auto: categorization, recurring/subscription detection (free tier too), "left to spend" after bills+goals. Manual: budgets, goals.
**~15 taps to first insight; budget still manual.** Honesty: detection false-positives exist; "left to spend" is only as good as the detected bills.

## 3. Copilot Money (lighter)

1. Demo-first entry — wander a populated fake-data app before connecting (0–1)
2. Value carousel → soft paywall in-flow (3–5)
3. Connect via Plaid, "Not on Plaid?" manual escape hatch (~6–8)
4. **Auto-derived budget: "Your initial budget is based on your historic spend, but you can edit it at any time."** (0 authoring taps) — same for category assignment and income detection
5. Auto-detected recurrings surfaced as a REVIEW list, not data entry
6. Goals last, each linked to an existing account
7. "To Review" queue seeds the habit loop; after ~30 reviewed transactions, Copilot Intelligence predicts categories

**~18–25 taps to a full picture, but ZERO authoring — onboarding is confirmation, not creation.** This is the model to beat. Honesty: the auto-budget framing is explicitly labeled as derived-from-history and editable; thin-data extrapolation is not labeled (weakness shared with Monarch).

## 4. Proposed Upmore post-connection flow

Target: **≤2 taps from Home to the full picture; ≤5 screens in the whole connect→insights journey.**

| Step | Screen | Taps |
|---|---|---|
| 1 | Home → "Connect bank" | 1 |
| 2 | Paste SimpleFIN setup token → confirm (token round-trip is the known friction; credentials stay on SimpleFIN's site) | 1 + paste |
| 3 | Syncing state (honest: "Reading N transactions…") | 0 |
| 4 | Celebration + "Your money picture is ready" → **"See my money"** | 1 |
| 5 | **Money picture** (one screen, enhanced Budget Report) | — |

**Total: ~4 taps, 5 screens.** vs Monarch ~20–25 taps + manual budget (~30+ to a full budget picture), Rocket Money ~15, Copilot ~18–25 with zero authoring.

### The one screen it opens: "Money picture"
Sections, in order (every number traces to posted, non-transfer, non-pending transactions):
1. **Hero:** this month kept = in − out (one number). Thin-data banner here if <30 days.
2. **Budget:** categories vs actual — "Suggested" (3-mo avg, labeled with its basis) vs "Your budget" (user-set wins). Tap to edit.
3. **Profit/loss per month:** last 6 months as in/out/kept bars — explicit "$ kept" per month. *(NEW — gap #1)*
4. **Spending breakdown:** by-category bars, this month vs 3-mo avg.
5. **Cash flow:** in / out / kept this month, plain words.
6. **Top merchants** (5) → tap to merchant transactions.
7. **Recurring charges:** auto-detected (existing detector: amount clustering ±5%/$1, gap bands weekly→annual, 75% consistency, confidence, next-date, dormant) with keep-or-cut + "Cancel it for me."
8. **Net worth mini-trend** → full net-worth screen (monthly snapshots already exist).

What stays OUT of this screen (one tap away, not zero): CFO tools, Investments X-ray, Guide, Explore. The founder's "very very very simple Home" rule holds — Home keeps its single connect/picture button.

## 5. Accuracy invariants (non-negotiable)

1. **Source traceability:** every figure = f(posted, non-transfer, non-pending transactions in the stated month). Pending transactions never shift the current month or any comparison window. Refunds net against their category's spending (never counted as income). Transfers excluded from in/out.
2. **Thin-data honesty:** <30 days of transactions → banner: "N days of data — budgets are rough estimates and will sharpen as more arrives." Suggested budgets labeled "Suggested · based on N days," never presented as fact. No invented precision: round estimates to whole dollars.
3. **Estimates labeled as estimates:** 12-month annualizations = "projection, not savings"; forecasts = "estimate"; dormant/uncertain detections show their confidence or stay hidden.
4. **Manual vs observed:** user-entered figures labeled "entered by you"; detected figures labeled "observed." Never mixed silently.
5. **No false confidence:** with 2 weeks of data, do not render multi-month trends as if complete — show the months that exist, gray the rest, say why.

Upmore today violates invariant 2 (no thin-data messaging; suggested budgets render from whatever history exists without stating the basis). Everything else is already in the code.

## 6. Gap list — what competitors auto-generate that Upmore doesn't yet (ranked by user value ÷ cost)

1. **Multi-month profit/loss trend** (explicit per-month kept bars) — value HIGH (founder asked for it verbatim), cost LOW (`monthAgg` already computes per-month in/out/kept; it's a render job).
2. **First-sync payoff moment** (celebration + "picture ready" + one button) — value HIGH (activation; Monarch/Rocket Money both prove it), cost LOW.
3. **"To Review" categorization queue** (low-confidence/uncategorized transactions as a swipeable habit loop) — value HIGH (accuracy compounds; Monarch mobile + Copilot both do it), cost MEDIUM.
4. **Thin-data honesty layer** (banner + "based on N days" labels per invariant 2) — value HIGH (trust; the "entirely accurate" bar), cost LOW.
5. **Forward cash-flow forecast** (30/60/90-day dated projection from detected recurrings + balances) — value MEDIUM-HIGH, cost MEDIUM (`detectRecurrence` already predicts next dates; needs balance projection).
6. **"Your starter budget is ready" surfacing at connect** — value MEDIUM, cost LOW (suggested budgets exist inside Budget Report; this is a surfacing + copy job, Copilot-style).
7. **Investment performance over time** — value MEDIUM, cost MEDIUM-HIGH (needs holdings history; Plaid production still pending).

## Sources
- Monarch help: https://help.monarch.com/hc/en-us/articles/360048393272-Getting-Started-with-Monarch
- BudgetBox onboarding teardown: https://github.com/krishnarajan7/budgetbox/blob/HEAD/design/research/onboarding.md
- BudgetBox core-screens research: https://github.com/krishnarajan7/budgetbox/blob/HEAD/design/research/core-screens.md
- Reviews: robberger.com/monarch-money-review, fool.com (Monarch, Rocket Money), usatoday.com (Monarch 2026), money.ca, modestmoney.com, clark.com, thebudgetnista.com
