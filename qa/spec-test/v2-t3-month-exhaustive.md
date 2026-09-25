# T3-v2 — Track: Month View — EXHAUSTIVE TEST REPORT (107 assertions)

**Verdict: FAIL** — 3 spec violations, 2 functional bugs, 5 nits. The month-view *mechanics*
(list, rows, sorting, exclusions, coverage) pass; the **spike pipeline is non-functional end to end**.

**Production tested:** https://upmore-srikanthvishnu90-sketchs-projects.vercel.app/
HTTP 200 · `sw.js` cache stamp `upmore-8b52c95` · served `index.html` 7,075,124 bytes.
Commit lineage: `b73da4f` (HEAD, pushed; `git ls-remote` matches).

**Method:** No live browser available to this agent. Instead of clicking, I extracted
`renderMonthView`, `renderMonthScreen`, `categorySpike`, and `TransactionSource.demo()`
**verbatim from the served production HTML** and executed them in Node against controlled
datasets, plus static assertions on the served markup/CSS/wiring. This tests the exact code
users receive — stronger than testing the template. Harness: `/tmp/t3harness.js`,
`/tmp/demorun.js` (kept for re-runs; not user-facing).

**Result: 107/107 harness assertions pass** — i.e. the code behaves exactly as analyzed below.
The FAILs are defects in the product, proven by the passing assertions, not harness noise.

**Round-1 regression** (`t3-month-view.md`, tested `0c2eb30` lineage):
- FIXED: delta-zero sign (`+$0` now consistent sign; class still contradicts — F6).
- FIXED: month set derived from filtered transactions (T6 fix present and verified).
- PERSISTS: no >40% flag in month view; empty-state "From undefined to undefined";
  meta-copy coverage line; demo-as-default data.
- WORSE THAN ROUND 1 REPORTED: round 1 believed a queue spike monitor existed but was
  unreachable on demo data. It does not exist as a runnable path at all — `TrackMonitors`
  is defined once and invoked **zero** times (F2). The monitor is dead code, not dormant code.

---

## Requirement-by-requirement (the 5 spec requirements)

### R1. Spending by category (12 fixed categories) — PASS (with notes)
- `TRACK_CATS` = exactly the 12 spec categories in spec order:
  Housing, Transport, Groceries, Dining, Subscriptions, Utilities, Health, Shopping,
  Entertainment, Debt, Transfers, Other. (D.17 ✓)
- The view renders whatever categories transactions carry, escaped via `esc()`.
  XSS probe `<img src=x onerror=alert(1)>` renders as `&lt;img…` — no injection. (B10 ✓)
- **Gap:** the demo's synthetic transfer uses category `"Transfer"` (singular), which is not
  in the 12 fixed categories. Cosmetic, but the "fixed" taxonomy is not enforced. (D.18)
- **Gap:** with live SimpleFIN data, the mapper hardcodes `category: "Other"`
  (`// TODO: proper categorization`). On live data the entire month view collapses to a
  single meaningless "Other" row. The month view is unusable on real connections until
  categorization exists.

### R2. This month vs 3-month average — PASS (math verified)
- Current month = most recent month in the filtered set; average = exactly the 3 prior
  months; missing months count as $0; single-month history → `avg $0/mo` (div-by-zero
  guarded by `Math.max(1, prev.length)`). Verified: B1 (200/100/+100), B8.01–B8.06,
  including the 6-month case where months 4–6 back are correctly ignored. (D.23–D.26)
- Rounding is display-only (`toFixed(0)`); thresholds in the monitor use unrounded values.
  Display edges: +49.6 → `+$50`; −0.4 → `−$0` (vanishes); 99.5 → `$100`. (B7)

### R3. Each row: category, this month, average, delta with direction — PASS (1 nit)
- Row markup: `<b>Category</b><i>avg $N/mo</i>` … `$N <em class="up|dn">±$N</em>`.
  Increase = red (`#b3261e`), decrease = green (`#2e7d4f`). Sorted descending by this
  month's spend. Plain `.mrow` divs — **no pie chart anywhere** (no `<canvas>`, no chart
  lib, no "pie" string in the 7 MB file). (B1.11–B1.15, D.15–D.16)
- **Nit (F6):** zero delta renders `+$0` in **green** (`class="dn"`). The round-1 sign bug
  was fixed (`+$0` not `+$0`-with-minus) but sign and color still contradict: "+" means
  "up", green means "down". Should be `$0` with a neutral style.

### R4. Category >40% above average (min $50) → spike card — **FAIL** (F1/F2/F3)
Three compounding defects; the spike path is non-functional end to end:
- **F1.** The month view gives no visual distinction to >40% categories. Proven on the
  shipped demo data: Dining is **$126 vs $84 avg (+50%)** and renders as an ordinary red
  `+$42` row — identical in kind to Groceries at +15%. The code comment above
  `renderMonthView` promises "Category >40% above average (min $50) becomes a spike card",
  but the view contains no spike flag, badge, or callout of any kind (B1.16, D.03/D.04).
- **F2. The monitor is dead code.** `TrackMonitors.categorySpike` (spec: ">40% above
  3-month average, min $50") is defined exactly once and invoked **zero** times anywhere
  in the served file (D.01). There is no `runMonitors`, no scheduler, no queue wiring —
  no spike card can ever reach the queue. The "spike" cards that *do* exist in `buildQueue`
  are Cancel-spec subscription bill-increase cards, a different feature.
- **F3. The monitor's "this month" is the max month, not the current month.**
  `const vals = Object.values(months).sort((a,b) => b - a); const thisMonth = vals[0]`
  sorts *values* descending and takes the maximum as "this month". Proven: months
  [500, 100, 100, 100] with the $500 spike **3 months old** and the current month at $100
  still fires, and its body claims **"$500 this month"** — factually false (C.16, C.17).
  Even if F2 were fixed, the monitor would fire on stale spikes and mislabel them.
  Threshold edges otherwise behave per spec: exactly 1.4× does not fire (strict `>`),
  1.405× fires; $49 over does not fire, $50 over fires (C.10–C.13).

### R5. Month set from filtered transactions (no pending) — PASS
- T6 fix verified: `months` derives from transactions filtered to `!is_pending &&
  !is_transfer`. A pending-only future month does **not** become the current month; a
  pending −$500 in the current month does not inflate this month's figure (B2.01, B2.02).
- **Defect (F7):** the *coverage window* is derived from **unfiltered** transactions
  (`transactions.map(t => t.posted_at).sort()`), so a pending transaction dated later than
  any settled transaction extends the stated "From X to Y" window without contributing a
  cent to the aggregates (B12.03). Window and math disagree about what the data covers.
- **Bug (F5):** empty transaction set → coverage reads **"From undefined to undefined"**
  (B12.04, D.29). No guard; round-1 nit persists.

### R6. Coverage stated: "From X to Y" — PASS (weak)
- `renderMonthScreen` sets `#monthCov` to `From 2026-07-10 to 2026-09-20`-style text
  (B12.01). On demo data: "From 2026-06-01 to 2026-09-25".
- **Nit:** the trailing clause "— every aggregate states its coverage." is spec-talking-to-
  itself meta-copy; it informs the user of nothing (B12.02, round-1 nit persists).

### R7. Spec navigation: "reached by tapping a month label" — PASS (weak)
- Path exists: Home → track strip (`#trackStrip` → `show("transactions")`) → transactions
  list → **"View month vs average →"** (`#txMonthBtn` → `show("monthview")`) →
  `renderMonthScreen`. Deep-linkable via `#monthview` hash. Back button returns Home.
  (D.08–D.10, D.14, D.35)
- **Nit:** the spec says "a month label"; the app has a ghost button *below* the
  transaction list (up to 100 rows), not a month label. Reachable but low-discoverability.
- Not a tab: `TABS` = exactly Home, Guide, You; month view is a plain screen section.
  (D.11, D.12)

### R8. Exclusion rules in the month math — PASS (1 spec gap)
- Pending excluded from spend, averages, and month set ✓ (B2). Transfers excluded ✓ (B3).
  Income excluded ✓ (B5). Amounts via `Math.abs` on negatives ✓ (D.25).
- **Spec gap (F4): refunds are not netted.** The synthetic `Amazon Refund +$42.99`
  (category Shopping) is excluded from spend — so it is *not* counted as income ✓ — but it
  is **not netted against the original** either: Shopping shows gross $606, not net $563.
  Spec: "Refunds: positive amount at a spending merchant — net against the original,
  never count as income." Half honored. (B4.02; proven on shipped demo data.)
  Note the demo refund also carries a *different* `merchant_id` (`amazon-refund` vs
  `amazon`), so even merchant-based netting would miss this fixture.

### R9. No behavioural conclusions — PASS
- Copy is numeric only ("+$98", "−$21"); no "spending too much" language in the month
  path (D.34). The red/green delta coloring is directional, not editorial.

### R10. Design (the 1 point) — PASS with nits
- The view is a deliberately boring simple list, sorted by size, honoring "No pie chart"
  and the "very very simple" directive. Live demo render: 8 clean rows.
- Deductions available for: `+$0`-in-green (F6), meta-copy coverage line (R6 nit),
  "From undefined to undefined" empty state (F5).

---

## Defect list (for the fix pass)

| ID | Severity | Defect | Evidence |
|---|---|---|---|
| F1 | Spec violation | Month view flags nothing at >40%; +50% Dining looks like +15% Groceries | B1.16, demo run |
| F2 | Spec violation | `TrackMonitors.categorySpike` defined once, invoked zero times; no runner, no schedule — spike cards can never reach the queue | D.01, D.02 |
| F3 | Logic bug | Monitor takes max-month as "this month" (`vals.sort desc; vals[0]`); fires on 3-month-old spikes, body claims "$500 this month" falsely | C.16, C.17, D.33 |
| F4 | Spec gap | Refunds not netted against originals; month shows gross spend (Shopping $606 not $563) | B4.02, demo run |
| F5 | Bug | Empty state: coverage reads "From undefined to undefined" | B12.04, D.29 |
| F6 | Defect | Zero delta shows `+$0` in green — sign says up, color says down | B1.07–B1.08, B6.04 |
| F7 | Defect | Coverage window uses unfiltered transactions (pending extends "From X to Y"); view math uses filtered — window and aggregates disagree | B12.03, D.28 |
| N1 | Nit | Coverage meta-copy "— every aggregate states its coverage." | B12.02 |
| N2 | Nit | "Month label" per spec is a ghost button below up to 100 rows | R7 |
| N3 | Nit | Demo transfer category `"Transfer"` ∉ 12 fixed categories | D.18 |
| N4 | Nit | Live SimpleFIN mapping hardcodes `category: "Other"` — month view collapses to one row on real connections | code `initLiveTrackData` |
| N5 | Nit | Display rounding can show `−$0` for a −$0.40 delta | B7.02 |

**Not re-litigated here (known, tracked elsewhere):** `loadTrackData()` still defaults to
`TransactionSource.demo()` for every unsigned-in user, so the month view's figures are
fabricated balances/transactions presented as the user's own (D.05). The SimpleFIN live
path only replaces demo when signed in *and* the proxy returns accounts (D.06, D.07).
Also: `demo()` spans 4 months (2026-06→2026-09, 210 tx) — adequate for the view's 3-month
average, but irrelevant to F2 since nothing invokes the monitor.

## What the view gets right (keep)
Plain-list rendering; exact 4-element rows; correct current-month/3-prior-month math with
$0-filled gaps; descending sort; pending/transfer/income exclusion from spend *and* from
the month set; HTML-escaped categories; stated coverage window; zero chart code; three-tab
structure intact; no judgemental copy; hash-routable; back button.

## Recommended fix order
1. Wire `categorySpike` into the queue (or delete it and the lying comment) — F2.
2. Fix "this month" to the chronological current month in the monitor — F3.
3. Decide the >40% inline treatment in the month view (badge vs queue-only) — F1.
4. Net refunds against originals in month math — F4.
5. Guard empty state; derive coverage from the same filtered set as the math — F5, F7.
6. Neutral `$0` rendering for zero delta — F6.
7. Live-data categorization before claiming the month view works on real connections — N4.

## Reproduction
- Harness (107 assertions, all passing): `/tmp/t3harness.js` → `node /tmp/t3harness.js`
- Live demo-data run: `/tmp/demorun.js` → `node /tmp/demorun.js`
- Key code sites in served HTML: `renderMonthView` (~offset 7041900), `renderMonthScreen`
  (~6916250), `TrackMonitors.categorySpike` (~7056100), `TransactionSource.demo()`,
  `initLiveTrackData` (~7039000), `#monthview` markup, `#txMonthBtn`.
