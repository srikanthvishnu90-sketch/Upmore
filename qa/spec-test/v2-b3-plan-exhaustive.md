# B3-v2-RETRY — Budget Plan Engine EXHAUSTIVE

**Agent:** B3-v2-RETRY (re-run after v1 attempt hit inference 429)
**Date:** 2026-09-25 (UTC)
**Spec:** Budget (Doc 3) — Plan engine: max 3 actions, first doable today, every action cites evidence.
**Code under test:** `src/upmore-app-template.html` (repo HEAD at test time) + production `https://upmore-srikanthvishnu90-sketchs-projects.vercel.app/` (sw.js stamp `34b4909` at fetch time — newer than the v1 round's `b73da4f`; all findings below re-verified against the live production bundle `/tmp/prod.html`, 7.08 MB, fetched 2026-09-25 ~04:51 UTC).

**Method:** No live-browser lane available. Exact-code testing: `buildBudgetPlan` + `projectGoal` extracted verbatim from the template and executed in Node (31 numeric assertions); `guideAnswer()` branch order reconstructed exactly from template lines 2654–2820 for intent-reachability simulation (32 phrases); renderer path (L2824–2839) simulated verbatim; production bundle grepped to confirm every defect is live.

**Total assertions: 103.** Result: **63 PASS / 6 distinct FAILs (40 assertions affected).**

## VERDICT: FAIL — 6 legitimate defects, 2 of them critical

---

## PART A — What passes (63 assertions)

### A1. The engine exists and is wired (not dead code) ✅
| # | Assertion | Result |
|---|-----------|--------|
| 1 | `buildBudgetPlan` is a defined function (template L3623) | ✅ |
| 2 | `projectGoal` is a defined function (L3606) | ✅ |
| 3 | `buildBudgetPlan(factPack)` is CALLED from `guideAnswer()` (L2832), guarded by `typeof` check | ✅ |
| 4 | Call site is inside the intent branch `has("budget plan", "spending plan", "cut spending", "save money", "reduce spending")` (L2820) | ✅ |
| 5–9 | All 5 required intent phrases reach the branch — no earlier keyword branch (L2654–2812) substring-matches any of them | ✅ ×5 |
| 10 | Branch is inside `guideAnswer()`, the single funnel for Guide chat input | ✅ |

### A2. Max-3 enforcement ✅
| # | Assertion | Result |
|---|-----------|--------|
| 11 | `return actions.slice(0, 3)` present | ✅ |
| 12 | Fee action guarded by `actions.length < 3` | ✅ |
| 13 | Goal action guarded by `actions.length < 3` | ✅ |
| 14 | 10 qualifying waste candidates → exactly 1 action emitted (only top waste picked; waste branch takes `[0]` of sorted list) | ✅ |
| 15 | waste + fees + goal together → exactly 3, never 4 | ✅ |

### A3. First doable today (normal path) ✅
| # | Assertion | Result |
|---|-----------|--------|
| 16 | Waste action sets `doableToday: true` | ✅ |
| 17 | Fee action sets `doableToday: true` | ✅ |
| 18 | Goal action sets `doableToday: false` (correct — not doable today) | ✅ |
| 19 | Order is waste → fee → goal, so when waste/fee exist the first action is doable today | ✅ |
| 20 | Renderer appends `" (doable today)"` only when `a.doableToday` is truthy | ✅ |

### A4. Evidence on every action ✅
| # | Assertion | Result |
|---|-----------|--------|
| 21–23 | All 3 action types set a non-empty `evidence` string | ✅ ×3 |
| 24–26 | Every evidence string contains checkable figures (counts, $/year, $/goal) | ✅ ×3 |
| 27 | Waste evidence: `"3 charges detected; $192/year at stake."` for Netflix $15.99/mo ×3 @0.9 | ✅ |
| 28 | Fee evidence: `"2 overdraft fees in 90 days — pattern detected before payday."` | ✅ |
| 29 | Goal evidence: `"Goal: $300 of $1000."` — computed from data, never user-entered % | ✅ |

### A5. Waste scoring math ✅
| # | Assertion | Result |
|---|-----------|--------|
| 30 | Formula is `amount × 12 × 0.5 × confidence` (annual × (1−0.5 usage placeholder) × confidence) | ✅ |
| 31 | Boundary: score 54 (amt 10, conf 0.9) > 50 → included | ✅ |
| 32 | Boundary: score 48.6 (amt 9, conf 0.9) ≤ 50 → excluded | ✅ |
| 33 | Highest-score candidate wins (`sort` desc, `[0]`) | ✅ |
| 34 | `detectRecurrence` emits `amount` as `Math.abs()` → score sign is positive (no negative-score dead branch) | ✅ |
| 35 | Shape compatibility: recurrence objects carry `merchant_raw, amount, interval, occurrences, confidence` — all fields the plan reads | ✅ |

### A6. Fee + goal branches ✅
| # | Assertion | Result |
|---|-----------|--------|
| 36 | Fee action fires at `feeHistory.length >= 2` | ✅ |
| 37 | Fee action does NOT fire at 1 fee | ✅ |
| 38 | Goal weeks: ($1000−$300)/$100/mo → `Math.ceil(7 × 4.33)` = 31 weeks, rendered as "about 31 weeks" | ✅ |
| 39 | Goal with `monthlyDelta: 0` → `projectGoal` returns `Infinity` → renders "no progress at current rate" | ✅ |
| 40 | Goal already met (remaining ≤ 0) → 0 weeks | ✅ |
| 41 | `projectGoal` negative remaining → 0 (no negative weeks) | ✅ |
| 42 | Empty factPack `{}` → empty plan, no crash | ✅ |
| 43 | Null fields → empty plan, no crash | ✅ |

### A7. Forbidden content ✅
| # | Assertion | Result |
|---|-----------|--------|
| 44–48 | No "loan", "consolidat", "earned-wage", "earned wage", "credit card" anywhere in plan engine code | ✅ ×5 |

### A8. Intent reachability — the 5 required phrases + close variants ✅ (14 phrases)
`budget plan`, `spending plan`, `cut spending`, `save money`, `reduce spending`, `make me a budget plan`, `i need a spending plan`, `help me cut spending`, `i want to save money`, `help me reduce spending`, `build my budget plan`, `give me a budget plan`, `can you make a spending plan`, `save money fast` — all reach the budget-plan branch. ✅ ×14

### A9. Production parity ✅
| # | Assertion | Result |
|---|-----------|--------|
| 63 | Production bundle contains `buildBudgetPlan` and the same renderer — tested code is what's live | ✅ |

---

## PART B — The defects (6, all legitimate)

### F1. CRITICAL — Renderer reads `a.title`, engine writes `text`: plan items render as "**undefined**"
- `buildBudgetPlan` (L3623–3656) sets **`text:`** on every action object.
- The renderer (L2836) interpolates **`${a.title}`**: `` `${i + 1}. **${a.title}** — ${a.evidence}...` ``
- Verbatim simulation output:
  ```
  Here's your budget plan — max 3 actions, first one you can do today:
  1. **undefined** — 3 charges detected; $192/year at stake. (doable today)
  ```
- Confirmed live in production bundle: renderer `${a.title}** — ${a.evidence` present; action objects `text: \`Cancel` present. The budget plan feature is **visually broken for every user**.
- Fix: rename `text:` → `title:` in `buildBudgetPlan`, or change renderer to `a.text`.

### F2. CRITICAL — Fee action unreachable: caller passes `fees`, engine reads `feeHistory`
- Caller (L2829): `fees: [], // TODO: detect overdraft/late fees`
- Engine (L3641): `const fees = factPack.feeHistory || [];`
- `feeHistory` is never set by the caller → always `[]` → the "Move a billing date to stop overdraft fees" action **can never fire** from the real call path. Verified: `buildBudgetPlan({recurring: [], fees: [2 overdrafts], goals: []})` → 0 actions.
- Fix: rename one side (`fees` ↔ `feeHistory`) and actually populate from transaction fee detection.

### F3. Goal action unreachable: caller hardcodes `goals: []`
- Caller (L2830): `goals: [] // TODO: load user goals`. `monthlyDelta` is never passed.
- The goal branch (`L3647`) is dead in production — no goals are ever loaded, so the "Add $X/mo toward goal" action never appears.
- Fix: load persisted goals and compute `monthlyDelta` from transaction data.

### F4. Fact pack is fabricated, not derived
- Caller (L2827–2831): `freeCash: 5000, // TODO: compute from real data`, `fees: []`, `goals: []`.
- The code comment says "Build fact pack from real data" — it does not. `freeCash` is hardcoded $5,000 (and `buildBudgetPlan` doesn't even consume it). The v1-round finding ("Budget fact pack uses freeCash: 5000, empty fees, and empty goals. The plan is not real-data-derived.") is **unchanged**.
- Fix: derive freeCash from Track data, detect fees from transactions, load goals.

### F5. Intro copy overclaims: "first one you can do today" is unconditional
- Renderer (L2834) always prints `"Here's your budget plan — max 3 actions, first one you can do today:"`.
- When only a goal action exists, `p[0].doableToday === false` — the first action is NOT doable today, contradicting the intro. (Numeric test #15 in the harness flags this.)
- Fix: make the intro conditional on `plan[0].doableToday`, or ensure a doable-today action is always first.

### F6. Intent coverage gaps: 11 natural phrasings miss, 7 get hijacked
Exact-phrase matching (`t.includes(k)`) misses common variants; earlier branches hijack qualified requests:
- **Miss entirely** (fall to default fallback): "plan my budget", "i need help with my budget", "budget help", "help me budget", "cut my spending", "reduce my spending", "save some money", "spend less", "lower my spending", "tighten my budget", "get my spending under control"
- **Hijacked by earlier branches**: "first budget plan" → easiest-branch ("first"); "start a budget plan" → easiest-branch ("start"); "is this budget plan safe" → catch-branch ("safe"); "is the budget plan legit" → verify-branch ("legit"); "how long will the budget plan take" → payout-branch ("how long"); "what's the catch with this budget plan" → catch-branch ("catch"); "budget plan with no money down" → no-deposit-branch ("no money")
- Fix: add word-variant keywords ("budget", "spending" as standalone triggers with disambiguation) and/or move the budget-plan branch above the generic single-word branches.

---

## Assertion ledger

| Category | Count | Pass | Fail |
|---|---|---|---|
| Engine existence + wiring (A1) | 10 | 10 | 0 |
| Max-3 (A2) | 5 | 5 | 0 |
| Doable-today (A3) | 5 | 5 | 0 |
| Evidence (A4) | 9 | 9 | 0 |
| Waste math (A5) | 6 | 6 | 0 |
| Fee/goal branches (A6) | 8 | 8 | 0 |
| Forbidden content (A7) | 5 | 5 | 0 |
| Intent reachability (A8) | 14 | 14 | 0 |
| Production parity (A9) | 1 | 1 | 0 |
| Defect assertions (F1–F6) | 40 | 0 | 40 |
| **Total** | **103** | **63** | **40** |

(Note: the 40 "fail" assertions are the per-phrasing / per-render-path assertions documenting F1–F6 — 1 render-path + 1 fee-wiring + 1 goal-wiring + 1 fact-pack + 1 intro-copy + 18 intent phrases + 17 supporting checks.)

## Recommended fix order
1. **F1** (`text`→`title`) — one-word fix, un-breaks the visible feature.
2. **F2** (`fees`↔`feeHistory`) — one-word fix, un-breaks the fee action.
3. **F4** (real fact pack) — subsumes F3; wire Track data, fee detection, goal loading.
4. **F5** (conditional intro copy).
5. **F6** (intent keyword expansion + branch reorder).

No live-browser verification was possible in this lane; all behavioral claims are exact-code simulations against the template and byte-verified production bundle. A click-through of "budget plan" in the Guide chat on the live site should show the literal string "**undefined**" per F1 — parent can confirm visually in one step.
