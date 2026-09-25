# Agent B1 — Budget: Safe to Spend — HARSH TEST REPORT

**Verdict: FAIL** (3 defects, all fixable)

**Method note:** This subagent cannot launch a live browser (depth-1 subagent constraint).
Testing was performed as a harsh line-by-line code audit of `src/upmore-app-template.html`
against Doc 3 (Budget spec). A live-browser visual confirmation is still required —
flagged as an open item for the parent to delegate.

---

## What passes

1. **One number on Home.** The `.safetospend` box renders a single total (`#stsTotal`)
   with a sub-line. It is not a dashboard. PASS.
2. **Total shown.** `#stsTotal` = `fmt$(Math.round(sts.total))`. PASS.
3. **Daily pace shown.** Sub-line reads `≈$X/day until <date>`. PASS.
4. **Cycle-end date stated every time.** `sts.cycleEnd` is interpolated into the sub-line
   on every render; `calcSafeToSpend` requires `cycleEnd` as a parameter. PASS.
5. **No negative-shame.** Negative totals render via `fmt$` as e.g. `$-50` — plain,
   no "you're overspending", no red inaction language, no commentary in the render
   path. PASS (code-level; visual tone still needs a browser check).

## Defect 1 (FAIL): Buffer is NOT on a separate line — spec rule 3 violated

Spec: *"show the buffer as a separate line, so the user knows it exists and can change it."*

Implementation (`renderTrackStrip`, ~line 3204):
```js
$("stsSub").textContent = `≈${fmt$(Math.round(sts.daily))}/day until ${sts.cycleEnd} · $${sts.buffer} buffer`;
```
The buffer is appended inline to the daily-pace line (`· $100 buffer`). It is not a
separate line. A user scanning the box sees one sub-line, not a distinct buffer row.
**Fix:** render the buffer as its own `<div>`/line, e.g. `Buffer: $100 (adjustable)`.

## Defect 2 (FAIL): Buffer is NOT adjustable — spec violated

Spec rule 3 continues: *"...so the user knows it exists **and can change it**."*

The buffer is hardcoded: `calcSafeToSpend(balance, fixedRem, 0, 100, cycleEnd)` and
`calcFreeCash(..., 100)`. There is no UI anywhere (searched all `buffer` references)
to view or change it. A hardcoded invisible-until-read-fine-print $100 is exactly
what the spec forbids.
**Fix:** add a buffer control (tap the buffer line → stepper or input), persisted to
prefs/profile.

## Defect 3 (FAIL): `committed_estimate_remaining` hardcoded to 0 — formula incomplete

Spec formula:
`safe_to_spend = current_balance - fixed_remaining_this_cycle - committed_estimate_remaining - buffer`

Call site:
```js
const sts = calcSafeToSpend(balance, fixedRem, 0, 100, cycleEnd);
//                                       ^ always zero
```
The COMMITTED tier (recurring-but-variable: utilities, phone, groceries) is never
estimated or subtracted. The function signature accepts the parameter, but every
caller passes 0. Net effect: **safe-to-spend is systematically overstated** — the
user is told they can spend money that is actually committed to variable recurring
bills. For a product whose positioning is honesty, an overstated "safe" number is
the worst possible direction to be wrong in.
**Fix:** implement the COMMITTED tier estimate (spec: 3-month median of COMMITTED)
and pass it through instead of 0.

## Partial: recompute trigger

Spec rule 2: *"recompute on every new transaction, never on a schedule."*
`renderTrackStrip()` runs on `renderHome()` only. There is no transaction-ingest event
because there is no live pipeline yet (demo data). Acceptable for v1 **only** with a
recorded TODO to wire recompute to the ingest path when SimpleFIN/Plaid goes live.
Not counted as a defect, but must not be forgotten.

## Summary for parent

| Check | Result |
|---|---|
| One number on Home | PASS |
| Total + daily pace + cycle-end date | PASS |
| Buffer as separate line | **FAIL** (inline) |
| Buffer adjustable | **FAIL** (hardcoded 100) |
| Full formula (committed tier) | **FAIL** (hardcoded 0, overstates) |
| No negative-shame | PASS (code-level) |
| Recompute on new transaction | PARTIAL (no live pipeline yet) |
| Live-browser visual confirmation | **NOT DONE** — needs delegation |

**Do not mark B1 complete until Defects 1–3 are fixed and a browser pass confirms
the visual rendering.**
