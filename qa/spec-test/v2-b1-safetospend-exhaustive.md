# B1-v2-RETRY — Budget: Safe to Spend EXHAUSTIVE — HARSH REPORT

**Verdict: FAIL** — 3 spec violations, all carried over from v1 unfixed.

- **Date:** 2026-09-25 (UTC)
- **App tested:** https://upmore-srikanthvishnu90-sketchs-projects.vercel.app/
- **Code tested:** `src/upmore-app-template.html` at HEAD `006ab43` (re-extracted and re-run after parent's concurrent edits; identical result)
- **Built artifact:** `index.html` verified to contain the same render code (line 3545)
- **Spec:** `docspecs/03-budget.md` — Safe to Spend section (lines 62-64)
- **Method:** 105 numbered assertions executed in Node against the verbatim-extracted `calcSafeToSpend`, `fmt$`, `renderTrackStrip` render strings, HTML markup, and CSS from the template. No live browser available to this agent (depth-1 subagent constraint); the render path is a single deterministic template literal, so code-path evidence is conclusive for all non-visual claims. Visual tone (exact pixel rendering) is flagged for parent browser confirmation.

**Scoreboard: 105 assertions — 103 PASS / 2 FAIL**, where the 2 FAILs are test-regex artifacts (see §H), not product defects. The 3 product defects below are confirmed by PASSING assertions that verify the defective state exists.

---

## Spec under test (docspecs/03-budget.md, verbatim)

> `safe_to_spend = current_balance - fixed_remaining_this_cycle - committed_estimate_remaining - buffer.`
> Displayed as total and daily: "$190 left, or about $13 a day until the 27th."
> Four rules: (1) never negative-shame — if negative, say so plainly and the queue surfaces actions, not commentary; (2) recompute on every new transaction, never on a schedule; (3) show the buffer as a separate line, so the user knows it exists and can change it; (4) state the cycle end date every time.

Task requirements: ONE number on Home; formula as above; four elements shown (total, daily pace, buffer, cycle-end date); daily = total/days_remaining; buffer = $100 (or configured); cycle-end = next payday; negative renders without shame.

---

## DEFECT 1 (FAIL): Buffer is NOT on a separate line — spec rule 3 violated

Spec rule 3: *"show the buffer as a separate line, so the user knows it exists and can change it."*

Implementation (`renderTrackStrip`, template line ~3541, built `index.html` line 3545):

```js
$("stsSub").textContent = `≈${fmt$(Math.round(sts.daily))}/day until ${sts.cycleEnd} · $${sts.buffer} buffer`;
```

The buffer (`· $100 buffer`) is appended inline to the single `#stsSub` sub-line, after the daily pace and cycle-end date. There is exactly one `#stsSub` element in the document (assertion D9) and no `stsBuffer`/`stsBuf`/buffer-line element exists anywhere (assertion D7). A user scanning the box sees one sub-line, not a distinct buffer row. This is byte-identical to the v1 finding — **not fixed**.

**Fix:** render the buffer as its own line, e.g. `<div class="sts-sub" id="stsBuf">Buffer: $100 (tap to change)</div>`.

Assertions: D7, D8, D9 confirm the defective state.

## DEFECT 2 (FAIL): Buffer is NOT adjustable — spec rule 3 violated

Spec rule 3 continues: *"...so the user knows it exists **and can change it**."*

- Call site: `calcSafeToSpend(balance, fixedRem, 0, 100, cycleEnd)` — buffer hardcoded `100` (assertion B3).
- `calcFreeCash(balance, recurring, nextPayday, buffer = 100)` — default hardcoded `100` (assertion E3).
- No `setBuffer`/`changeBuffer`/`bufferInput`/`adjustBuffer` function exists (E1).
- No buffer control element in HTML (E2).
- Buffer not persisted to localStorage (E4) or user profile (E5).
- No click handler, no "tap to change" affordance text (E7, E9).

A hardcoded, invisible-until-you-read-the-fine-print $100 is exactly what the spec forbids. **Not fixed since v1.**

**Fix:** add a buffer control (tap the buffer line → stepper/input), persisted to prefs.

Assertions: E1–E9 confirm the defective state.

## DEFECT 3 (FAIL): `committed_estimate_remaining` hardcoded to 0 — formula incomplete

Spec formula: `safe_to_spend = current_balance - fixed_remaining_this_cycle - committed_estimate_remaining - buffer`

Call site:

```js
const sts = calcSafeToSpend(balance, fixedRem, 0, 100, cycleEnd);
//                                          ^ always zero
```

The COMMITTED tier (recurring-but-variable: utilities, phone, groceries — the spec's own examples of what "committed estimate" covers) is never estimated or subtracted. The function signature accepts `committedRemaining` (assertion B7) and the arithmetic is correct when fed (assertions A6, A17), but every caller passes 0 (assertion B2). Net effect: **safe-to-spend is systematically overstated** — the user is told they can spend money that is actually committed to variable recurring bills. **Not fixed since v1.**

**Fix:** estimate the committed tier (e.g. average of variable-recurring categories over 3 months, or a defined heuristic) and pass it instead of 0.

Assertions: B2, B6-note confirm the defective state.

---

## What passes (103 assertions)

### A. Formula function is correct (20/20)
`calcSafeToSpend(balance, fixedRemaining, committedRemaining, buffer, cycleEnd)`:
- `total = balance - fixedRemaining - committedRemaining - buffer` — verified exact across 8 numeric cases including fractional inputs (1234.56 − 78.9 − 12.34 − 100 = 1043.32 exact), zero deductions, large balances, and negative balances (−500 − 100 − 50 − 100 = −750).
- `daily = total / days`; `days = max(1, round((cycleEnd − now)/864e5))` — floors at 1 for past cycle-ends (no division by zero, no negative days).
- Returns `{ total, daily, buffer, cycleEnd, days }` — all five keys, buffer and cycleEnd passed through.
- Deterministic: same input → same output.

### B. Call-site wiring (8/10 — 2 regex artifacts, see §H)
- Call site exists in `renderTrackStrip`; `fixedRemaining` fed from recurrence-derived `fixedRem`; `cycleEnd` variable passed.

### C. ONE number on Home (15/15)
- Exactly one `#stsTotal` element, a single `<b>` (22px hero) inside `.safetospend`.
- Renders `fmt$(Math.round(sts.total))` — a single rounded dollar figure, not a range, not a sum of two numbers.
- Not a dashboard; the box contains one number + one sub-line.
- Rendered on Home via `renderTrackStrip()` (called in the Home render path).

### D. Four elements shown (18/20 — D7/D8 confirm defects 1)
- **Total:** `#stsTotal` ✅
- **Daily pace:** `≈$X/day` in `#stsSub`, rounded, prefixed with ≈ (approximation honesty) ✅
- **Buffer:** `$100 buffer` word present — visible but inline, not separate line ❌ (defect 1)
- **Cycle-end date:** `until YYYY-MM-DD` interpolated every render ✅ (spec rule 4)
- Code comment documents the 4-element requirement.

### E. Buffer visibility (partial — adjustability absent, defect 2)
- Buffer value and the word "buffer" are shown; nothing hidden. But no way to change it.

### F. Negative rendering — no shame (15/15)
- `fmt$(-50)` → `"$-50"` — plain minus, no accounting parentheses, no cents for integers.
- Negative total → negative daily (never clamped at 0 — reality is not hidden; assertion F8/F9).
- No red in `.safetospend`/`.sts-top` CSS (F3); `.sts-top b` has no color override, inherits neutral `--ink` (F13).
- Zero matches for "overspending", "you're overspending", "bad with money", "shame", "guilt", "warning" in app code (F4–F7, F11, F12).
- No conditional red on negative (F10); no inline red style on `#stsTotal` (F14).
- Spec rule 1 ("if negative, say so plainly") satisfied at code level. Visual pixel-tone still needs a live-browser confirm (F15).

### G. Cycle-end = next payday (10/10)
- `cycleEnd = nextPay || +30 days` — payday preferred, 30-day fallback (G1–G3).
- `nextPay = lastPay + 14 days` from payroll-detected `payDates` (G4, G7).
- Payday detection excludes pending AND transfers (T6 fixes verified: G5, G6).
- `daysToPay` floored at 0 (G9); `cycleEnd` formatted `YYYY-MM-DD` (G10).

### H. No-guilt cross-check — B2-v2 fix verified present (5/5)
- `.mrow em.up { color:#5f6368 }` — the month-view red-on-spending-above-average flagged by B2-v2 is **fixed** in this build; both deltas render neutral gray.
- No `#b3261e` and no `color:red` anywhere in the template.

---

## Notes for the parent

1. **V1 defects carried over.** The parent's summary states "Fix all v1 agent findings" was completed, but B1's three v1 defects (buffer separate line, buffer adjustable, committed estimate) are byte-identical to the v1 report at HEAD `006ab43`. Either they were intentionally deferred or the B1 fixes were missed. Flagging honestly per the harsh-tester mandate.
2. **Test artifacts (not product defects):** assertions B6 and E6 in the raw run "failed" due to over-broad test regexes (B6's pattern matched the formula *comment* `// - committed_estimate_remaining - buffer`; E6's `/, 100,/g` didn't match the actual `, 0, 100,` / `, 100)` call-site shapes). The underlying product facts they were probing are confirmed by the passing assertions B2, B3, and E3.
3. **Rule 2 (recompute on every transaction, never on schedule):** `renderTrackStrip()` runs in the Home render path and re-runs when live SimpleFIN data arrives (`initLiveTrackData`). No `setInterval`/cron recompute of safe-to-spend was found. There is no transaction-ingest hook that recomputes on *every* new transaction — recompute happens on Home render. Whether that satisfies "on every new transaction" depends on whether Home re-renders after each ingest; the ingest path was out of scope for this agent.
4. **Spec example phrasing:** the spec's display example is "$190 left, or about $13 a day until the 27th." The implementation renders "≈$13/day until 2026-10-08 · $100 buffer" — daily-first rather than total-first, and a full ISO date rather than "the 27th". The total *is* the hero number above the sub-line, so total-first ordering is preserved visually. Not flagged as a defect.
5. **Live-browser confirmation still open:** exact pixel rendering of the `.safetospend` box (spacing, the single sub-line, negative-number color) needs one browser screenshot per the v1 note. Everything else is code-path conclusive.

## Reproduction

```bash
cd ~/workspace/upmore
python3 -c "
import re
html = open('src/upmore-app-template.html').read()
open('/tmp/b1-test-src.js','w').write(re.search(r'<script>(.*?)</script>', html, re.S).group(1))"
node /tmp/b1-exhaustive.js   # test script at /tmp/b1-exhaustive.js
```

## Files

- Report: [v2-b1-safetospend-exhaustive.md](sandbox://workspace/upmore/qa/spec-test/v2-b1-safetospend-exhaustive.md)
- Test script: `/tmp/b1-exhaustive.js` (ephemeral; re-generate via Reproduction above)
- Spec: `~/workspace/upmore/docspecs/03-budget.md` (lines 62–64)
