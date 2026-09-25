# B4-v2: Budget Calculators EXHAUSTIVE — Test Report

**Agent**: B4-v2 (Budget: Deterministic Calculators)
**Date**: 2026-09-24 ~23:50 CDT
**App**: https://upmore-srikanthvishnu90-sketchs-projects.vercel.app/
**Spec**: Doc 3 — Budget (deterministic functions: `projectBalance`, `feeImpact`, `projectGoal`)

## Method

Extracted the three functions verbatim from `~/workspace/upmore/src/upmore-app-template.html`
(lines ~3562–3590) into an isolated Node harness. Ran **102 assertions** across two
batches against the exact shipped code. No mocks of the functions themselves; harness
only supplies inputs and checks outputs. Also confirmed all three function definitions
are present in the built `index.html` (3/3 match) shipped to production.

## Verdict: 101/102 PASS — 1 genuine defect found

## Summary of results

### projectBalance(currentBalance, changes, throughDate) — 33 assertions, 32 pass
- ✅ Exists, 3-arg signature, returns `number`, synchronous (not a Promise).
- ✅ Pure: input `changes[]` array never mutated (byte-compared before/after); no
  accumulating state across calls; interleaved calls fully independent.
- ✅ Deterministic: identical inputs → identical outputs across 1000 repeated calls.
- ✅ Filters correctly: changes after `throughDate` excluded, changes on
  `throughDate` included, unsorted input sorted internally, order-independent sums.
- ✅ Handles empty changes, zero-amount changes, negative balances, cents precision,
  100-change sequences, large balances (1e12), extra fields on change objects ignored.
- ❌ **DEFECT (PB21)**: ISO datetime strings with time components are compared
  inconsistently. `new Date('2026-10-01T08:00:00')` parses as *local* time while
  `new Date('2026-10-01')` (date-only) parses as *UTC midnight*. Result: a change
  stamped `2026-10-01T08:00:00` is **excluded** from `throughDate='2026-10-01'`
  (verified on VM, TZ=UTC; the same class of bug affects user timezones in the
  opposite direction). Any change on the through-date carrying a time-of-day
  later than 00:00 is silently dropped. Severity: medium — bank data is typically
  date-only so practical impact is limited, but the comparison should be done on
  calendar-day (string slice or normalized date) for determinism across timezones.

### projectGoal(goal, monthlyDelta) — 30 assertions, 30 pass
- ✅ Exists, 2-arg signature, returns `number` (integer when finite), synchronous.
- ✅ Pure: `goal` object never mutated; goal `name`/`deadline` fields ignored (pure math).
- ✅ Deterministic; no randomness, no `Date.now()`, no `fetch`/LLM references in code.
- ✅ Progress derived from data, never user-entered %: verified that
  `weeks = ceil((target_amount − current_amount) / monthlyDelta × 4.33)` matches
  exactly; e.g. $750 remaining at $100/mo → `ceil(7.5 × 4.33)` weeks.
- ✅ Goal reached/overfunded → `0`; zero/negative delta → `Infinity`;
  `remaining ≤ 0` short-circuits before any division (no division-by-zero path).
- ✅ Monotone: bigger delta → fewer weeks; more saved → fewer weeks;
  larger remaining → more weeks.
- ✅ Spec consistency: implementation takes `(goal, monthlyDelta)` rather than the
  spec's `(goal_id, monthly_delta)` — acceptable: it still computes from stored
  goal data; the model explains, never estimates.

### feeImpact(change, feeHistory) — 34 assertions, 34 pass
- ✅ Exists, 2-arg signature, returns object with exactly
  `{fees_avoided, monthly_value, description}`, synchronous.
- ✅ Pure: `feeHistory` never mutated; deterministic across interleaved calls.
- ✅ Matches only `type === 'overdraft'` in history AND `change.type === 'move_billing'`;
  `late_fee` history entries are NOT counted (verified).
- ✅ `monthly_value = total / 3` (90-day window annualized); varied fee amounts
  ($27/$34/$35) summed correctly; single fee → `35/3`.
- ✅ Empty history → `{0, 0, 'No matching fees found'}`; zero-amount overdraft entry
  still counted in `fees_avoided` with `monthly_value` 0 (defensive, reasonable).
- ✅ Case-sensitive type matching (`'Overdraft'` does not match) — consistent and
  predictable; change without `type` → 0 matches.
- ✅ Description text: `'2 overdraft fees in 90 days'` pattern verified.
- ✅ Spec consistency: implementation takes `(change, feeHistory)` vs. spec's
  `feeImpact(change)` — the extra arg is how it receives the fee data; no LLM math.

### Cross-cutting — 5 assertions, 5 pass
- ✅ No `Math.random`, `Date.now()`, `fetch`, or model/AI references in any of the
  three functions — pure deterministic code. "Code computes; model explains" holds.
- ✅ All three definitions present in production `index.html` (built bundle).

## Defect to fix (1)

1. **`projectBalance` timezone-sensitive date comparison.** A change dated
   `'2026-10-01T08:00:00'` (any time-of-day after midnight) is excluded when
   `throughDate = '2026-10-01'` because date-only strings parse as UTC midnight
   while datetime strings parse as local time. Fix: compare on calendar-day
   granularity (e.g. `c.date.slice(0,10) <= throughDate.slice(0,10)`) or normalize
   both to the same zone before comparing.

## Notes / caveats
- These are pure client-side functions; correctness here is independent of the
  demo-vs-live data-source concern (that's a data problem, not a calculator problem).
- Spec's plan example ("$1,000 emergency fund in 11 weeks instead of 26") uses the
  same `4.33` weeks/month factor as `projectGoal` — consistent.
- Batch files: `/tmp/budget_fns.js` (extracted functions), `/tmp/budget_asserts.js`
  (64 assertions), `/tmp/budget_asserts2.js` (38 assertions) — ephemeral; assertions
  are reproducible from the extraction method above.

**B4-v2 verdict: PASS with 1 defect flagged (PB21).** All spec-mandated behaviors —
existence, purity, determinism, correct fee math, data-derived goal progress, and
code-computes/model-explains separation — verified across 102 assertions.
