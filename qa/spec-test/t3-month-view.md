# T3 — Track: Month View — HARSH TEST REPORT

**Verdict: CONDITIONAL PASS — 1 FAIL (spec violation), 3 nits**

Tested against production template `src/upmore-app-template.html` (commit `0c2eb30` lineage).
No live browser available to this agent; verification done against the source of truth the
production bundle is built from (`renderMonthView`, `renderMonthScreen`, `show`, `wireTrackUI`).

## Requirement-by-requirement

### 1. Can you reach the month view? — PASS
Path: Home → Track strip button (`#trackStrip`) → Transactions screen → "View month vs average →"
(`#txMonthBtn`) → `#monthview`. Three taps. `show("monthview")` calls `renderMonthScreen()`
(line 1177). Wiring exists and is correct.

### 2. Simple list, not a pie chart — PASS
`renderMonthView()` (line 3224) emits plain `.mrow` divs. No canvas, no SVG, no chart code
anywhere in the month path. No pie chart. This part of the spec is honored.

### 3. Each row: category, this month, average, delta with direction — PASS
Row markup (line 3241-3245):
- Category: `<b>` name, escaped ✓
- This month: `$${r.thisM.toFixed(0)}` ✓
- Average: `avg $${r.avg.toFixed(0)}/mo` ✓
- Delta with direction: `+$Z` / `−$Z` with `up` (red) / `dn` (green) class ✓

### 4. Coverage window stated — PASS (weak)
`renderMonthScreen()` sets `#monthCov` to `From ${dates[0]} to ${dates[dates.length-1]} — every
aggregate states its coverage.` The window IS stated. The trailing clause is self-congratulatory
meta-copy rather than useful information — it reads like the spec talking to itself. Nit.

### 5. Sorted by size — PASS
`.sort((a, b) => b.thisM - a.thisM)` — descending by this month's spend. Correct.

### 6. Category >40% above average becomes a spike card — **FAIL**
The month view does NOT flag >40% categories in any way distinct from any other delta. A
category at +200% looks identical to one at +5% — both are just red `+$Z` text. There is no
spike badge, no callout, no "spike" element in the month view.

The only spike implementation is a *queue* monitor (`buildQueue`, line ~3493):
`if (thisMonth > avg * 1.4 && (thisMonth - avg) >= 50)` — and it requires `vals.length >= 4`
(four months of history). The built-in demo dataset (`TransactionSource.demo()`) spans only
~90 days, so the monitor can NEVER fire on the data any reviewer or new user will see. The
spec requirement is therefore dead code in practice: no spike card appears in the month view,
and the queue spike card cannot fire on the shipped demo data.

This is a spec violation. Fix: surface the >40% flag inline in the month view (badge on the row),
or extend the demo data to ≥4 months so the queue monitor is at least exercisable.

## Nits
1. **Delta-zero sign/class mismatch:** when `delta === 0`, the row renders `+$0` with class `dn`
   (green). Sign says "up", color says "down". Sloppy.
2. **Empty-state crash:** if `transactions` is empty, `dates[0]` is `undefined` → the coverage
   line reads "From undefined to undefined". Guard needed.
3. **`months` for the average is derived from ALL transactions** (including income/transfers/
   pending) while spending is filtered to non-pending, non-transfer negatives. A month with only
   income becomes a zero-spend month in the average — defensible, but the two filters should be
   consistent.

## Out-of-scope but noted
- `TransactionSource.demo()` loads fabricated balances/paychecks/transactions for every user
  (`loadTrackData`, line 3176: `if (!trackData) trackData = TransactionSource.demo()`).
  The month view displays these as real money. Per the project warning, this must never reach
  production as current-user data. The T3 verdict above evaluates the view mechanics only.
- The code admits 4 of 7 monitors are missing ("lowBalance, duplicateCharge, trialConversion,
  paydayLanded omitted for brevity"). Not a month-view item; flagged for T4.

## Reproduction
Read `renderMonthView()` at `src/upmore-app-template.html:3224` and `renderMonthScreen()` at
`:1185`. Trace the click path from `#trackStrip` (line 760) → `#txMonthBtn` (line 839).
