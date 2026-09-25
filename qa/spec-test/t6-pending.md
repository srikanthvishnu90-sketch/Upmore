# Agent T6 — Track: Pending / Transfer / Refund Exclusion — VERDICT: FAIL

**Date:** 2026-09-25 (repo commit `0c2eb30`, template `src/upmore-app-template.html`, 3555 lines)
**Method:** Static code audit of the deployed template. Live-browser verification was NOT possible (no browser-task capability in this subagent). All line numbers refer to `src/upmore-app-template.html` at `0c2eb30`.

The spec's three rules under test:
1. Pending transactions are excluded from all totals.
2. Transfers are excluded from spending.
3. Refunds are netted against originals, never counted as income.

---

## Finding 1 — CRITICAL: Refund netting is not implemented anywhere

There is **zero refund-netting code** in the entire Track implementation. No function matches a refund to its original purchase, no category spend is ever reduced by a refund amount.

What actually happens to a positive non-payroll transaction (e.g. an Amazon refund):
- Month view (line 3227) and the spike monitor (line 3396) filter `t.amount < 0`, so the refund is silently ignored — it neither reduces the category's spending nor appears in any aggregate.
- `renderTxList` (line 3210–3218) renders it as `+$X.XX` with the `"in"` (green/income) CSS class — **visually presented as income**, the exact thing the spec forbids.
- There is no "netted against originals" path at all. Spec requires the refund to reduce the original category spend. Current behavior: it does nothing in sums and looks like income in the list.

**Verdict: FAIL.** Netting is a specified behavior, not an edge case. It's absent.

## Finding 2 — Pending transactions have no "pending" marking in the transaction list

`renderTxList` renders `date · category` + amount. There is **no pending badge, no pending label, no visual distinction** anywhere in the list markup or CSS. If live SimpleFIN/Plaid data arrives tomorrow with `is_pending: true` rows, users will see them rendered identically to posted transactions with no way to tell them apart.

**Verdict: FAIL.** "Are pending transactions marked 'pending'?" — No. There is no such UI.

## Finding 3 — Pending leaks into payday detection (minor but real)

Line 3186:
```js
const payDates = transactions.filter(t => t.amount > 0 && /payroll/i.test(t.merchant_raw))
```
No `!t.is_pending` and no `!t.is_transfer`. A **pending** paycheck (or a pending positive entry matching "payroll") shifts `nextPay`, which cascades into: days-to-payday on the Home strip, free cash (`calcFreeCash`), and the safe-to-spend cycle end date. Payday is not a "total" in the narrow sense, but pending influencing it violates the spirit and can move real numbers on Home.

**Verdict: FAIL (minor).** One-line fix: add `!t.is_pending && !t.is_transfer` to the filter.

## Finding 4 — Pending leaks into the month-window computation (minor but real)

Line 3232:
```js
const months = [...new Set(transactions.map(t => t.posted_at.slice(0, 7)))].sort().reverse();
```
Pending transactions participate in determining `cur` (current month) and the 3-month average window. A pending transaction dated in a future/other month can shift which month is treated as "this month" and distort the comparison window.

**Verdict: FAIL (minor).** The month set should be derived from the same filtered set as the spend aggregation.

## Finding 5 — The exclusion logic is untestable in the live app (testability failure)

The demo `TransactionSource` hardcodes `is_pending: false, is_transfer: false` on **every** transaction (lines 3361, 3373), and the 90-day generated dataset contains **zero pending transactions, zero transfers, zero refunds**. There is no way to verify any of these exclusions by using the app — only by reading the code. Combined with the already-known "fabricated financial data" defect, the demo dataset should include synthetic pending/transfer/refund cases so these rules are behaviorally verifiable.

**Verdict: FAIL (testability).**

---

## What passes (credit where due)

- **Month view spending** (3227): `!t.is_pending && !t.is_transfer && t.amount < 0` ✓
- **categorySpike monitor** (3396): same exclusion filter ✓
- **detectRecurrence** (3484): same exclusion filter ✓ (so recurrence-driven free cash and cancel cards are built on posted-only data)
- **Transfers excluded from spending** wherever spending is summed ✓ (same filters)
- **Refunds not added to spending totals** ✓ — but only by omission of the `amount < 0` filter, not by netting. See Finding 1.
- `calcFreeCash` is balance-based; its recurrence input comes from the filtered detector ✓
- `calcSafeToSpend` inputs derive from filtered recurrence ✓
- The only `amount > 0` transaction usage in the app is the payday filter (Finding 3); `buildBudgetPlan` consumes recurrence/fee/goal data, not transaction income sums ✓

---

## Overall: FAIL

Two outright spec gaps (refund netting absent; no pending marking in the list) and two minor filter holes (payday detection, month window), plus a dataset that makes the whole thing unverifiable in the live app.

## Required fixes

1. Implement refund netting: match positive non-payroll transactions to originals (same merchant, refund after purchase) and reduce the category's spend; never render a refund as bare "+income".
2. Render a "pending" indicator on pending transaction rows in `renderTxList`.
3. Add `!t.is_pending && !t.is_transfer` to the payday filter (line 3186).
4. Derive the month set from the filtered (posted, non-transfer) transaction set (line 3232).
5. Add synthetic pending / transfer / refund cases to the demo dataset so these rules are testable in-app.

## Open item for parent agent

Live-browser verification of pending/transfer/refund behavior was out of scope for this subagent (no browser-task capability). Even with the code fixes, real verification needs either (a) the synthetic dataset cases from fix 5, or (b) live provider data — and a browser task that can inject/inspect such rows.
