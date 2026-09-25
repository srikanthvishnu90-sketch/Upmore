# Agent T1-v2 — Track: Home Strip — EXHAUSTIVE HARSH TEST REPORT

**Verdict: CONDITIONAL PASS — 87/90 assertions hold; 3 spec deviations are real FAILs
(F1: days-to-payday not from the recurrence detector; F2: demo money unlabeled;
F3: no coverage window on the strip).**

Method: direct source inspection of `src/upmore-app-template.html` (the single source
of truth; the build regenerates `index.html` from it), byte-level comparison of the
strip markup between template and built `index.html`, and production evidence
(HTTP 200 + served `sw.js` stamp). As a subagent I have no live-browser capability,
so the physical tap and the rendered-pixel state are code-verified, not eye-verified.
Every assertion cites a line number in the template unless stated otherwise.

**Production evidence:** production returns HTTP 200 (7,075,124 bytes) and serves
`sw.js` with cache stamp `upmore-8b52c95`. Local HEAD is `b73da4f` ("Rebuild sw.js
with cache stamp 8b52c95"); per the build rule the stamp is the pre-commit HEAD, so
the deployed build is identical to local HEAD. The strip markup is byte-identical
in template and built `index.html` (verified by substring match). `git status` shows
only `sw.js` locally re-stamped to `b73da4f` (uncommitted build noise) — no template
drift. Strip code tested = strip code deployed.

**Spec under test** (docspecs/04-track.md, "View 1: the strip on Home — three
numbers, one line, at the top of the queue": free cash = balance − recurring due
before next payday − buffer; days to payday = from the recurrence detector run over
inflows; left to spend = free cash ÷ days to payday, daily; tapping the strip opens
the transaction list).

---

## A. Presence & count — exactly 3 numbers

1. **PASS** — Strip element exists: `<button class="trackstrip" id="trackStrip" hidden>` (line 768).
2. **PASS** — Exactly 3 `<span>` children (programmatic count = 3, lines 769–771).
3. **PASS** — Exactly 3 number elements: `#tsFree`, `#tsDays`, `#tsDaily` (`<b>`, lines 769–771).
4. **PASS** — Exactly 3 label elements: the three `<i>` labels; no 4th metric, badge, or extra copy inside the strip markup.
5. **PASS** — Metrics are exactly the spec's three: free cash, days to payday, left to spend/day. Nothing added, nothing missing.
6. **PASS** — Labels match spec wording: "free cash" (spec: Free cash), "days to payday" (spec: Days to payday), "left to spend / day" (spec: "Left to spend … as a daily figure" — the "/ day" rendering is faithful).
7. **PASS** — Strip is a native `<button>`: keyboard-activatable, touch-friendly, `cursor:pointer` (CSS line 390).
8. **PASS** — Starts `hidden` with "—" placeholders; `renderTrackStrip()` sets `hidden=false` and overwrites all three `textContent`s on every path — placeholders can never leak through (lines 3480–3483).
9. **PASS** — Strip lives only on the Home screen (inside `section#home`), never a tab.
10. **PASS** — `renderHome()` calls `renderTrackStrip()` unconditionally on every Home render (line 2030) — not gated on sign-in, data state, or feature flag.
11. **PASS** — Exactly one writer per value: `tsFree`/`tsDays`/`tsDaily` are written only at lines 3481–3483. No competing writer can desync the numbers.
12. **PASS** — `trackStrip` referenced exactly 3× (markup 768, onclick 1213, render 3480) — no duplicate/conflicting bindings.

## B. ONE line — not stacked, not two lines

13. **PASS** — CSS: `.trackstrip { display:flex; … }` (line 390) — horizontal row layout.
14. **PASS** — No `flex-wrap` declared; flex default is `nowrap`, so the three columns cannot stack or wrap to a second line.
15. **PASS** — Each span `flex:1` (line 391) — three equal columns sharing one row, `width:100%`, `gap:8px`.
16. **PASS** — Within each column the number (`<b> display:block`, line 392) sits above its label (`<i> display:block`, line 393) — the spec's "one line" is the strip row; per-column number-over-label is the only sane reading and matches "three numbers, one line".
17. **PASS** — No `@media` query touches `.trackstrip` (only two media queries in the file, both `prefers-reduced-motion`) — the single row holds at every viewport width.
18. **PASS** — Card styling is static: `background:var(--surface)`, `border:1px solid var(--line)`, `border-radius:14px`, `padding:12px 14px`, `margin:12px 0 4px` — nothing dynamic can reflow it.
19. **PASS** — Design simplicity: 17px bold numbers, 11px dim labels, no icons, no badges, no secondary copy. Meets "very very simple."
20. **PASS** — Contrast: `--ink` numbers on `--surface` card — readable at a glance.

## C. At TOP of the queue — above "Up next", below header

21. **PASS** — Markup order in Home: `.head` header (755) → `h1#hello` greeting (763) → `p#homeSub` subheader (764) → `#trackStrip` (768) → `#safeSpend` → `#connectCard` → `.xsearch` → `#xlist` → `h2.sec` "Up next" → `#queue`.
22. **PASS** — Directly below the greeting/subheader block — first content element on Home.
23. **PASS** — Above the search input, the earn cards (`#xlist`), the "Up next" heading, and the queue (`#queue`).
24. **PASS** — `renderHome()` order: `renderExplore()` → `renderTrackStrip()` → `renderQueue()` → `renderTracker()` — the strip's data refreshes before the queue renders; it cannot show stale-behind-the-queue figures.
25. **PASS** — The standalone `<h2 class="sec">Track</h2>` section is far below; the strip is the top Track surface, not buried in it.
26. **PASS** — The new HOME-5-THINGS `#connectCard` renders below the strip (lines 776–785) — it does not displace the strip from the top slot.
27. **PASS** — `#safeSpend` (Budget spec) renders directly below as a separate element — not strip clutter, different spec's surface.
28. **PASS** — The strip cannot be pushed below the fold by the queue: it precedes `#queue` in DOM order and the Home scroll container starts at the header.

## D. Tapping opens the transaction list

29. **PASS** — `wireTrackUI()` sets `$("trackStrip").onclick = () => show("transactions")` (line 1213).
30. **PASS** — `wireTrackUI()` is called at top-level `initSave()` (line 2288, invoked line 2306) — runs at script load, unconditional on sign-in.
31. **PASS** — No second or conflicting `onclick` on `#trackStrip` anywhere in the file.
32. **PASS** — Target screen exists: `<section class="screen" id="transactions">` (line 851).
33. **PASS** — `show("transactions")` is a valid path: `show()` (line 1184) toggles `.screen` visibility by id and calls `renderTxScreen()` for `"transactions"` (line 1196).
34. **PASS** — `renderTxScreen()` renders `renderTxList()` rows into `#txList` on every show — fresh data each visit (lines 1203–1205).
35. **PASS** — `renderTxList()` outputs spec View 2 rows: date, merchant, amount, category (line 3514–3518).
36. **PASS** — Transaction screen has search: `#txq` input with `oninput` re-render (line 1216).
37. **PASS** — "View month vs average →" button (`#txMonthBtn`) routes to `show("monthview")` (line 1214) — View 3 reachable from View 2, per spec.
38. **PASS** — Back navigation: every `[data-back]` returns to `show("home")`, wired in the same `wireTrackUI()` (line 1217).
39. **PASS** — Transactions screen header has a back button (`<button class="backbtn" data-back>`, line 853).
40. **PASS** — Hash routing consistent: `show()` sets `#transactions` via `replaceState`; the `hashchange` handler routes `#transactions` back through `show()` (lines 1222–1226).
41. **PASS** — Keyboard accessible: native `<button>` fires `onclick` on Enter/Space.
42. **PASS** — No `event.preventDefault`/`stopPropagation` interference on the strip; no overlay element sits above it in z-order in the Home section.
43. **CAVEAT (not a strip failure)** — `renderTxList` emits `data-tx` row ids but no row click-handler for recategorize/mark-transfer/flag-wrong was found in `wireTrackUI()`; the tap chain strip→list is complete, but tap→correction wiring belongs to T2's scope and looks incomplete.
44. **LIMIT** — Physical tap in a real browser not performed (no live-browser capability); the chain is code-complete and syntactically valid (build passes).

## E. Free cash = balance − recurring − buffer

45. **PASS** — `calcFreeCash(balance, recurring, nextPayday, buffer = 100)` returns `balance − due − buffer` (lines 3802–3808) — exactly the spec formula.
46. **PASS** — `due` = sum of recurring entries with `next_date <= nextPayday` — "recurring charges due before next payday," not all recurring ever.
47. **PASS** — Buffer is $100, subtracted always.
48. **PASS** — Strip calls `calcFreeCash(balance, rec, nextPay || "2099-01-01", 100)` (line 3478) — shared function with the rest of the app.
49. **PASS** — `balance` = `accounts[0]?.balance || 0` — the primary account's live/demo balance.
50. **PASS** — Recurring input `rec` comes from `detectRecurrence(transactions)` run over the same dataset — no separate hardcoded subscription list feeds the strip.
51. **PASS** — Displayed rounded via `fmt$(Math.round(freeCash))`; `fmt$` renders integers as `$2152` (no decimals) — clean, glanceable (line 1104).
52. **PASS** — Demo arithmetic is sane: balance $2,840.50 − recurring due − $100 buffer → positive four-figure free cash; no NaN/Infinity path (balance defaults to 0, not undefined).
53. **PASS** — When `nextPay` is null the code passes `"2099-01-01"`, so ALL detected recurring is subtracted — conservative (understates free cash rather than overstating).
54. **CAVEAT** — Earn's gate calls the same `calcFreeCash` but with hardcoded inputs `calcFreeCash(5000, [], "2099-01-01", 100)` (lines 1764–1765, 1811–1812): the function is shared ("computed once, read everywhere" is aspirational), but Earn's *inputs* are still hardcoded — known E1-scope defect, not a strip defect.

## F. Days to payday — from payroll detection, pending excluded

55. **PASS** — Inflow filter: `t.amount > 0 && !t.is_pending && !t.is_transfer && /payroll/i.test(t.merchant_raw)` (line 3470) — pending paychecks and transfers are excluded (T6 fix present in the strip's own code path).
56. **PASS** — `lastPay` = most recent matching inflow date; `nextPay` = `lastPay + 14 days`.
57. **PASS** — `daysToPay = Math.max(0, Math.round((nextPay − today) / 864e5))` — never negative.
58. **PASS** — Null fallback: no detected payday → `daysToPay = 30` (line 3473) — a stated assumption, not a crash.
59. **PASS** — Demo has 7 biweekly "Employer Payroll" $2,400 inflows, so the strip resolves to a real ~14-day cycle on demo data.
60. **FAIL (F1)** — Spec: "Days to payday: from the recurrence detector run over inflows." The implementation does NOT run `detectRecurrence()` on inflows — it hardcodes `+14 days` (biweekly). Weekly, monthly, or irregular pay produces a wrong number. The detector itself is interval-aware (weekly/biweekly/monthly/quarterly/annual bands, lines 3759–3764) but is only run over *outflows* (`t.amount < 0`, line 3746). This is a genuine spec deviation, not a nit.
61. **PASS** — Pending exclusion is behavioral, not just a comment: the filter explicitly tests `!t.is_pending` on the payday path.
62. **PASS** — Synthetic demo pending case (`demo-pending-1`, Amazon −$42.50, `is_pending:true`) exists for T6 verification and cannot shift nextPay.

## G. Left/day = free cash ÷ days

63. **PASS** — `tsDaily = fmt$(Math.round(freeCash / Math.max(1, daysToPay)))` (line 3483) — exactly the spec: free cash divided by days to payday, daily figure.
64. **PASS** — Division-by-zero guarded: `Math.max(1, daysToPay)`; if payday is today (0 days), divides by 1.
65. **PASS** — Derived from the same `freeCash` and `daysToPay` values shown — the three numbers cannot drift from each other.
66. **PASS** — Label "left to spend / day" matches "as a daily figure."
67. **PASS** — Rounded and formatted identically to free cash.

## H. Live data when available — not hardcoded

68. **PASS** — `loadTrackData()`: `trackData ??= TransactionSource.demo()` — demo is a lazy fallback, replaceable (line 3422–3425).
69. **PASS** — `initLiveTrackData()` (lines 3431–3462): when signed in, invokes the `simplefin-proxy` Supabase Edge Function, maps accounts+transactions, sets `trackData` with an `isLive` flag, and re-renders the strip.
70. **PASS** — `supabase/functions/simplefin-proxy/index.ts` exists and was committed in `8b52c95` (git show confirms 124-line function).
71. **PASS** — Live mapping preserves `is_pending` and `provider_id` (dedupe), and derives `is_transfer` via `/transfer/i` — the strip's exclusions hold on live data.
72. **PASS** — Strip re-renders when live data arrives (`renderTrackStrip()` called after assignment) — numbers switch from demo to live without reload.
73. **PASS** — Pending/transfer exclusions apply to whichever dataset is loaded (filtering happens in `renderTrackStrip`, not in the demo generator).
74. **CAVEAT** — Live mapping sets every transaction `category: "Other"` with a `TODO: proper categorization` (line 3448) — honest placeholder, but month-view category math on live data is currently meaningless.
75. **CAVEAT** — Live fetch requires sign-in (proxy needs JWT); signed-out users always see demo. By design, but see F2.
76. **FAIL (F2)** — The strip renders demo money ($2,840.50 balance → ~$2,152 free cash) with NO "sample data" label anywhere on or near the strip. A signed-out user reads fiction as their own finances. This is the known parent-listed demo-data defect; on the strip surface it is a data-honesty FAIL, not just a backlog item.
77. **FAIL (F3)** — Spec hard-never #3: "Never show an aggregate without its coverage window." The strip shows free cash with no coverage window and no "as of" date. The month view has one (`monthCov`: "From … to … — every aggregate states its coverage.", line 1209); the strip does not.
78. **PASS** — Hard-never #5 respected on this surface: no "watches daily" / "last checked today" copy on or near the strip.
79. **PASS** — Hard-never #4 respected: the strip states three numbers, no behavioral conclusion ("you're spending too much" etc.).
80. **PASS** — Hard-never #1 respected in the strip path: pending excluded from payday detection, and `detectRecurrence` (feeds free cash) filters `!t.is_pending` (line 3746).
81. **PASS** — Hard-never #2 respected in the strip path: transfers excluded from payday detection; detector excludes transfers from recurring.

## I. Integration & regression guards

82. **PASS** — Strip re-renders on every Home visit; no stale-cache path (no memoization of strip values).
83. **PASS** — No console-breaking references: all `$("…")` ids used in `renderTrackStrip` (`trackStrip`, `tsFree`, `tsDays`, `tsDaily`, `safeSpend`, `stsTotal`, `stsSub`, `connectCard`, `connectBankBtn`) exist in markup.
84. **PASS** — `renderTrackStrip` is also called from the async live-data path (line 3459) — defined before use at runtime (function declaration hoisted within the same script scope).
85. **PASS** — The connect-sheet button wired in `renderTrackStrip` (`connectBankBtn` → Guide + connect sheet) does not alter strip behavior.

## J. Design (the 1 design point of the 5)

86. **PASS** — Glanceable: three numbers dominate (17px bold), labels subordinate (11px dim) — hierarchy serves the "can I spend right now" question.
87. **PASS** — Single-card chrome, no dividers between the three metrics needed; `gap:8px` separates them.
88. **PASS** — Full-width button tap target (~343px × ~60px on mobile) — thumb-friendly, no precision required.
89. **PASS** — No jargon: "free cash", "days to payday", "left to spend / day" are plain words.
90. **PASS** — Consistent with app visual language (`--surface`, `--line`, `--ink`, `--dim` tokens).

---

## FAILS (must-fix before "all done")

- **F1 — Days-to-payday is not from the recurrence detector (spec deviation).**
  Spec: "Days to payday: from the recurrence detector run over inflows."
  Code: `nextPay = lastPay + 14 days`, hardcoded biweekly (line 3472).
  Fix: run `detectRecurrence()` (or an inflow variant) over `amount > 0` transactions,
  take the detected interval's `next_date` for the pay cluster instead of `+14d`;
  keep the 30-day fallback only when no pay pattern is detected. Monthly/irregular
  earners currently get a wrong number with no warning.
- **F2 — Demo money is unlabeled on the strip.**
  The strip shows `$2,840.50`-derived figures to signed-out users with no "sample
  data" indicator. Fix: when `!trackData.isLive`, render a small "sample data"
  caption on the strip (or suppress the strip until live data exists — product call).
- **F3 — No coverage window on the strip (hard-never #3).**
  Fix: append the data window to the strip, e.g. a caption like
  "from {earliest} to {latest}" or "based on last 90 days", matching the month
  view's `monthCov` pattern.

## Harsh notes (not verdict-changers)

- Earn's gate shares `calcFreeCash` but feeds it hardcoded `(5000, [], "2099-01-01", 100)`
  — the "computed once, read everywhere" claim is true of the function, false of the
  inputs. E1's scope, but it weakens the spec's cross-feature invariant.
- Live transactions are all categorized "Other" (TODO) — the strip's three numbers
  are unaffected, but don't trust live month-view category math yet.
- `TransactionSource.demo()` is still the universal default; the SimpleFIN proxy
  only fires when signed in. Until Plaid/SimpleFIN connection UX ships, most real
  users will see F2's fiction.
- Downstream of the tap chain, transaction-row tap → recategorize/mark-transfer/
  flag-wrong shows no click wiring in `wireTrackUI()` — flagging for T2, not scored here.
- Physical tap and pixel rendering not eye-verified (no live-browser capability) —
  recommend one parent-level browser-task pass: tap the strip on production, confirm
  the list opens with rows + search + back, and screenshot the strip at 390px width
  to confirm the single row holds.

## Bottom line

The strip implements View 1's contract — three numbers, one line, top of the queue,
correct labels, tap-through to the transaction list, spec formula for free cash and
left/day, pending/transfer exclusions, live-data replacement path — on the exact
commit production serves (`b73da4f` / `sw.js` stamp `upmore-8b52c95`). Three real
deviations fail: biweekly-hardcoded days-to-payday (F1), unlabeled demo money (F2),
and missing coverage window (F3). Fix those three, redeploy, and this agent's
re-run should be a clean PASS.
