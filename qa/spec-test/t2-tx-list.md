# T2 — Track: Transaction List — HARSH TEST REPORT

**Verdict: FAIL** (3 of 8 requirements pass; the core interaction is a stub)

**Date:** 2026-09-24
**Scope:** Spec 04 (Track) — Transaction list: date, merchant, amount, category. Search and filter. Tapping opens recategorize / mark-transfer / flag-wrong. Deliberately boring.

**Test method note:** This agent could not operate a live browser. Testing was performed by direct static analysis of the shipped implementation (`src/upmore-app-template.html`, which is the source the production build is generated from). Every claim below is grounded in specific line numbers. The gaps found are structural — missing code — and cannot behave differently in a browser than the code shows.

---

## What passes

1. ✅ **List is reachable.** Home strip → click handler wired (`wireTrackUI`, line 1192: `$("trackStrip").onclick = () => show("transactions")`). Tapping the strip opens the `transactions` screen. PASS.
2. ✅ **Row elements present.** Each `.txrow` renders date (`posted_at`), merchant (`merchant_raw`), amount (+/− with `in`/`out` styling), category (renderTxList, lines 3209–3222). All four spec-required elements are present. PASS.
3. ✅ **Search works.** `txq` input re-renders the list filtered by merchant or category (line 1194). Case-insensitive substring match. PASS.

## What FAILS

### 1. ❌ Tapping a transaction does NOTHING — the spec's core interaction is unimplemented

Line 3208 (comment above renderTxList):
> "Tapping opens recategorize / mark-transfer / flag-wrong."

**This comment is false.** Evidence:
- Rows carry `data-tx="demo-N"` (line 3216) — the attribute is **decorative**.
- There is **zero** click handling on `.txrow` anywhere in the file. No `querySelectorAll(".txrow")`, no event delegation on `#txList`, no modal/sheet/action-sheet for transaction editing.
- There is **no recategorize function**, **no mark-transfer function**, **no flag-wrong function** — grep for `recategorize`, `mark.*transfer`, `flag.*wrong`, `tx-edit` returns only the line-3208 comment itself.
- The data model has `is_transfer` and `category_source` fields, so the schema anticipated this feature — but no code writes to them from the UI.

The spec's "deliberately boring" list exists; the interaction that makes the list *correctable* (the whole point of Track's data-quality loop) does not. **This is the single most important requirement of the transaction list, and it is a stub.**

### 2. ❌ No category filter

Spec says "Search **and filter**." Search exists. There is **no** category filter — no `<select>`, no chip row, no filter parameter on `renderTxList` (it takes only a search string). A user cannot view "all Dining transactions." FAIL.

### 3. ❌ No recategorize

Even via hypothetical UI: no code path changes a transaction's `category`. The `category_source` field (which would distinguish "provider" vs "user-corrected") is written in demo data but never set to anything else. FAIL.

### 4. ❌ No mark-as-transfer

`is_transfer: false` is hardcoded in every demo transaction. No UI, no function, no storage to mark one as a transfer. Consequence: the user has no way to exclude a transfer from spending totals — and the month-view/spending code *does* respect `is_transfer` (line 3227), so the exclusion logic exists but is **unreachable by the user**. FAIL.

### 5. ❌ No flag-as-wrong ("this isn't my transaction")

No report path of any kind. No button, no function, no database write. FAIL.

### 6. ❌ No persistence for corrections (even if the UI existed)

`loadTrackData()` (line 3175) builds demo transactions in-memory per session. There is no Supabase table write, no localStorage write, no correction store. Any correction would evaporate on reload. The spec's data-quality lifecycle (corrections must stick) cannot be satisfied by this architecture. FAIL.

### 7. ❌ Fabricated financial data presented as real

The transaction list, the Home strip ("free cash", "days to payday", "left to spend/day"), and the Safe-to-Spend surface all render **demo data** — a hardcoded $2,840.50 checking balance, synthetic Whole Foods/Starbucks/Netflix transactions, synthetic $2,400 biweekly payroll. There is **no "demo", "sample", or "preview" label anywhere in the UI** (grep for demo-label copy returns nothing). A real user opening this app would reasonably believe these are their accounts. The numbers move and compute as if real. This is a trust-critical failure: fabricated money presented as the user's own.

## Minor issues

- **Raw ISO dates.** Rows show `2026-09-24` instead of a friendly date. Readable, but not "deliberately boring" polish. (Not a FAIL on its own.)
- **100-row cap** in `renderTxList` (line 3212: `.slice(0, 100)`) with no pagination or "showing 100 of N" indicator. Fine for demo scale; will silently truncate real accounts.

## Recommended fixes (in order)

1. Implement the tap-to-edit interaction the comment already promises: an action sheet on `.txrow` tap with **Recategorize** (12 fixed categories), **Mark as transfer**, **This isn't my transaction**. Wire to the `category_source` / `is_transfer` fields that already exist.
2. Add a category filter control to the transactions screen.
3. Persist corrections (localStorage at minimum; Supabase `transaction_corrections` table when live data lands).
4. Label the strip/list/month surfaces as demo/sample data until a live connection exists — or hide them behind the connection prompt.
5. Friendly date formatting.

## Bottom line

The list *renders* and *searches* — that is the full extent of what works. Every interaction that makes the list trustworthy (correct, transfer, wrong) is a documented lie in a code comment with no implementation behind it. **FAIL.**
