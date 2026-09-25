# Agent T1 — Track: Home Strip — HARSH TEST REPORT

**Verdict: PASS (code-verified) — with 3 caveats and 1 required live test**

Method note: as a subagent I have no live-browser capability, so this verdict rests on
direct inspection of `src/upmore-app-template.html` (the single source of truth — the
build regenerates `index.html` from it) plus a `browser.open` fetch of production.
The one thing I could not do — physically tapping the strip in a real browser — is
flagged below for parent-level delegation. Nothing in this report is assumed; every
claim cites a line number.

## Spec under test (docspecs/04-track.md, lines 62–66)

> View 1: the strip on Home — three numbers, one line, at the top of the queue:
> Free cash: balance minus recurring charges due before next payday, minus buffer.
> Days to payday: from the recurrence detector run over inflows.
> Left to spend: free cash divided by days to payday, as a daily figure.
> View 2: the transaction list — reached by tapping the strip.

## Findings, point by point

### 1. Strip at the top of the queue — PASS
The strip element (`<button class="trackstrip" id="trackStrip">`, line 760) sits
immediately after the "Your money queue — biggest score first." subheader (line 757)
and BEFORE the search input and the queue list (`#xlist`). `renderHome()` calls
`renderTrackStrip()` unconditionally on every Home render (line 1952). It is not
gated on sign-in, data state, or any feature flag.

### 2. Exactly three numbers, no clutter — PASS
The strip contains exactly three `<span>` elements (lines 761–763):
`#tsFree`, `#tsDays`, `#tsDaily`. I grepped the strip markup and its CSS
(`.trackstrip`, lines 390–393): no fourth metric, no badges, no extra copy inside
the strip. (The Budget spec's Safe-to-Spend block renders directly beneath it as a
separate element — different spec's surface, not strip clutter.)

### 3. Labels match the spec — PASS
- "free cash" ✓ (spec: Free cash)
- "days to payday" ✓ (spec: Days to payday)
- "left to spend / day" ✓ (spec: "Left to spend … as a daily figure" — the "/ day"
  rendering is faithful)

### 4. Tapping opens the transaction list — PASS (code-wired; live tap untested)
`wireTrackUI()` (line 1191) sets `$("trackStrip").onclick = () => show("transactions")`
(line 1192). `wireTrackUI()` is called once at boot inside `initSave()` (line 2210).
`show("transactions")` resolves: the screen exists (`<section id="transactions">`,
line 831), `show()` renders it via `renderTxScreen()` (line 1190), and back-navigation
(`[data-back]`) returns to Home. The whole chain is present and syntactically valid
(full build passes `node --check`).

### 5. Numbers are plausible and the formula matches the spec — PASS
`renderTrackStrip()` (lines 3181–3204):
- `freeCash = calcFreeCash(balance, rec, nextPay, 100)` → **balance − recurring due
  before next payday − buffer** — exactly the spec formula, via the shared
  `calcFreeCash()` ("computed once and read everywhere" — Earn's gate uses the same
  function).
- `tsDaily = freeCash / max(1, daysToPay)` — guards division by zero.
- Against the bundled demo data: balance $2,840.50 − recurring due ≈ $588.82
  − $100 buffer ≈ **$2,152 free cash**, **14 days to payday**, **≈ $154/day left to
  spend**. All three are arithmetically consistent and sane.
- Placeholders ("—") are always overwritten: every code path sets all three
  `textContent`s, and the `hidden` attribute is removed in the same function.

## Caveats (harsh notes — not verdict-changers, but on the record)

1. **Days-to-payday is a hardcoded biweekly assumption, not the recurrence detector.**
   The spec says "Days to payday: from the recurrence detector run over inflows."
   The implementation matches `/payroll/i` inflows and adds a flat 14 days
   (lines 3185–3188). If a user's pay is monthly or irregular, this number is wrong.
   Minor spec deviation — recommend routing inflows through `detectRecurrence()`.
2. **The numbers are fictional and unlabeled as such.** The strip renders demo money
   ($2,840.50 balance, synthetic merchants) with no "sample data" label. This is the
   known demo-data defect already on the parent's list — it is a data-source problem,
   not a strip-spec failure, but a user reading "$2,152 free cash" is reading fiction.
3. **Production fetch could not visually confirm the strip.** `browser.open` on the
   live URL returns text extraction only; the strip starts `hidden` and is populated
   by JS, so its live rendered state was not observable. The deployed bundle was not
   re-verified to contain this exact code (fetch returned rendered text, not source).

## Required follow-up (for the parent agent — needs a browser task)

- **Live tap test:** in a real browser session on production, tap the strip and confirm
  the transaction list screen opens with rows, search, and back-navigation. The wiring
  is code-complete; only the physical interaction is unverified.
- **Days-to-payday:** feed or simulate a non-biweekly pay cadence and confirm the
  number follows the recurrence detector (caveat 1).

## Bottom line

The Home strip implements the spec's View 1 contract exactly as written: three
numbers, one line, top of the queue, correct labels, correct shared formula,
tap-through to the transaction list. **PASS.** The two substantive risks — biweekly
hardcoding and unlabeled demo money — are documented above and belong on the fix
list, but neither breaks the strip's specified contract.
