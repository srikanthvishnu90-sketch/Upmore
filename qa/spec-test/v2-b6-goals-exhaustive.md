# Agent B6-v2 — Budget: Goals EXHAUSTIVE — Harsh Test Report

**App:** https://upmore-srikanthvishnu90-sketchs-projects.vercel.app/
**Spec:** Budget (Doc 3) — Goals: user-set target, computed progress (never user-entered)
**Date:** 2026-09-25 ~04:50 UTC
**Method:** Source inspection of HEAD (`b73da4f`), built `index.html`, git archaeology, production `sw.js`, live Supabase query of `public.finance_goals`, node unit test of `projectGoal()`

## VERDICT: FAIL — the Goals feature does not exist in the shipped app

The entire Goals UI was **deleted** in commit `5ef487f` ("Honest rebuild: 3 tabs, ranked queue, real detectors, researched catalog", 2026-09-24 15:36 CDT). The deletion was intentional and principled: the old Money tab displayed demo-seeded rows (`$1,000 emergency fund`, `$340` current) from `finance_goals` as if they were the user's real progress — a fabricated-money facade. What remains is dead CSS (`goalcard`, `goaltrack`, `goalfill`, template lines 336–341) with zero DOM elements, zero JS references, and zero client reads/writes of `finance_goals`. Production (`sw.js` = `upmore-8b52c95`, one commit behind HEAD, and `5ef487f` is an ancestor of it) therefore has **no Goals UI at all**.

The deletion was the honest fix for a real honesty bug, but it leaves the Doc 3 Goals requirement 0% implemented. Until the feature is rebuilt honestly, every assertion below about Goals UI presence, target entry, computed progress display, and persistence fails.

---

## A. Goals UI existence (must not be dead code)

| # | Assertion | Verdict | Evidence |
|---|-----------|---------|----------|
| A1 | A Goals section renders somewhere in the app | FAIL | No goal-related DOM in template or built `index.html`; fetched live app text shows none |
| A2 | A `renderGoals`/`renderMoneyGoals` function exists and is called | FAIL | `git log -S renderMoneyGoals` shows only creation (`391db51`) and deletion (`5ef487f`); no such function at HEAD |
| A3 | The `.goalcard` CSS is attached to real DOM | FAIL | CSS exists (lines 336–341) but grep finds zero JS/DOM references — pure dead code |
| A4 | The `.goaltrack`/`.goalfill` progress bar renders on screen | FAIL | Never instantiated; no element with those classes is ever created |
| A5 | A "New goal" / "+ New goal" button exists | FAIL | Deleted with the form; `$("goalAdd")` references gone |
| A6 | A goal creation form exists (name + target inputs) | FAIL | `goalName`, `goalTarget`, `goalSave`, `goalCancel`, `goalForm` IDs absent from HEAD |
| A7 | Goal cards show name, `$X of $Y`, and a progress bar | FAIL | Old `renderMoneyGoals` did this pre-deletion; nothing at HEAD |
| A8 | An empty state tells the user how to set a goal | FAIL | Old text "No goals yet — set one and your agent tracks it from your real balances." deleted |
| A9 | Goals are reachable within the 3-tab structure (Home/Guide/You) | FAIL | Old goals lived on the deleted Money tab; nothing in Home, Guide, or You at HEAD |
| A10 | Guide chat can create or discuss a goal ("set a savings goal") | FAIL | No `has(...)` intent branch mentions goals; query falls through to the default catalog answer |
| A11 | Clicking anything labeled "goal" produces any visible response | FAIL | Nothing labeled goal exists to click |
| A12 | The Guide's "Knows your plan" surface mentions goals | FAIL | Live Guide shows only catalog/default answers |
| A13 | A goal detail view exists (pace, projection, created_at) | FAIL | Never existed; no detail view in old implementation either |
| A14 | Goal edit/rename flow exists | FAIL | Spec doesn't require edit, but nothing exists at all |
| A15 | Goal delete/abandon flow exists (status → abandoned) | FAIL | No UI; spec status `abandoned` can't be set anywhere |
| A16 | Goal "reached" state is displayed when target is hit | FAIL | Spec status `reached` not even in the DB CHECK constraint |
| A17 | Goals UI is not gated behind sign-in in a dead-end way | FAIL | N/A — no UI to gate; nothing renders for signed-in or signed-out users |
| A18 | The progress bar width is driven by JS, not hardcoded | FAIL | Old version computed `width:${pct}%`; no bar at HEAD |
| A19 | No stale goal fragments remain in the built bundle | FAIL | Dead `.goalcard`/`.goaltrack`/`.goalfill` CSS ships in `index.html` — dead code |
| A20 | `index.html` matches template on goals (build consistency) | PASS | Both lack the UI; build pipeline is consistent, just consistently missing |

## B. Target amount: user-set, never progress

| # | Assertion | Verdict | Evidence |
|---|-----------|---------|----------|
| B1 | User can set a target amount for a goal | FAIL | No input, no form, no Guide path |
| B2 | User sets the **amount** (`target_amount`), not a progress % | FAIL (design ok, absent) | Old form took only name + target $; that part matched spec before deletion |
| B3 | Target input is numeric with sensible validation (min > 0) | FAIL | Old form used `type="number" min="1"`; gone |
| B4 | Empty name or non-positive target is rejected with a clear message | FAIL | Old code toasted "Give your goal a name and a target amount"; gone |
| B5 | Target of $0 or negative is impossible | PASS (schema) | `CHECK (target_amount > 0)` on `finance_goals` still enforced at DB level |
| B6 | A goal is created with `current_amount = 0` (not user-entered) | FAIL (client) | Old `goalSave` inserted `current_amount: 0`; DB default is `0` — but no client path exists now |
| B7 | The user is never asked "how far along are you?" | PASS (vacuous) | Nothing asks the user anything — no UI |
| B8 | Creating a goal persists it (DB insert) | FAIL | `finance_goals` has RLS `own_finance_goals` and the table exists, but zero client writes |
| B9 | Duplicate/rapid double-tap goal creation is guarded | N/A | No creation path |
| B10 | Target survives sign-out/sign-in (server persistence) | FAIL | Rows exist in DB for other users but the signed-in user has no client path to create any |
| B11 | Goal name uses the user's own words | FAIL (was ok) | Old form stored `$("goalName").value.trim()` verbatim; deleted |
| B12 | Name length is bounded | FAIL | Old `maxlength="60"` on the input; gone with the form |
| B13 | Target supports decimals/cents | N/A | `numeric` column; old form `step="1"` truncated to whole dollars — a design wart that died with the form |
| B14 | One active goal by default (spec: multiple split attention) | FAIL | No UI, no default; DB has no active-goal-limit enforcement |
| B15 | A second goal is possible but not encouraged | FAIL | Old UI allowed unlimited goals with no discouragement copy; current: impossible |

## C. Progress: computed from transaction data, never user-entered

| # | Assertion | Verdict | Evidence |
|---|-----------|---------|----------|
| C1 | Progress % is computed, never typed by the user | FAIL (was FAIL before deletion too) | Old `renderMoneyGoals` displayed the **stored** `current_amount` — never recomputed from balances or transactions. The demo seed row (`$340`) rendered as 34% progress without any real data behind it |
| C2 | Progress ties to a designated account balance | FAIL | Old insert set `current_amount: 0` and nothing ever updated it from any account |
| C3 | Or: progress = Received + Avoided from the ledger since `created_at` | FAIL | No ledger linkage ever implemented; `save_ledger` exists but goals never read it |
| C4 | Progress bar % = `current / target`, capped at 100 | PASS (logic, deleted) | Old: `Math.min(100, Math.round(100 * current / (target || 1)))` — correct formula, but fed static stored data |
| C5 | Progress recomputes on new transactions | FAIL | No recompute trigger exists; spec's "recompute on every new transaction" unmet |
| C6 | The demo-seeded `$340 of $1,000` is not presented as the user's real progress | FAIL (historical) | This exact fabrication is why `5ef487f` deleted the UI; the seed row still sits in production DB (see D-section) |
| C7 | `projectGoal(goal, monthlyDelta)` computes weeks-to-target | PASS (pure function, verified) | node test: target 1000/current 340/delta 56 → **52 weeks**; `Math.ceil(remaining / monthlyDelta * 4.33)` |
| C8 | `projectGoal` returns 0 when goal is reached | PASS | Verified: remaining ≤ 0 → 0 |
| C9 | `projectGoal` returns Infinity at zero/negative monthly delta | PASS | Verified: `monthlyDelta <= 0` → Infinity; Guide renders "no progress at current rate" |
| C10 | `projectGoal` handles target 0 without NaN | PASS | remaining = 0 → returns 0 before any division |
| C11 | The plan engine's goal projection is reachable | FAIL | `buildBudgetPlan` line 3610 checks `factPack.goals[0]`, but the Guide passes `goals: [] // TODO: load user goals` (line 2812) — the branch is dead code |
| C12 | Model never estimates projection itself (function computes, model explains) | FAIL (vacuous) | Function exists and is honest; but it's never called with real data |
| C13 | Progress uses `created_at` for pace | FAIL | `created_at` column exists and defaults to `now()`; nothing reads it |
| C14 | Status transitions (active → reached/abandoned) are computed | FAIL | No transition logic; spec statuses `reached`/`abandoned` aren't even in the DB constraint (`active`/`done`/`archived`) |
| C15 | Multiple goals each get independent progress | FAIL | No UI; DB can hold multiple rows but nothing displays them |
| C16 | Negative or missing amounts don't crash the renderer | PASS (was) | Old renderer used `Number(g.current_amount || 0)` and `target || 1` guards |
| C17 | `deadline` field doesn't leak into progress math | PASS (vacuous) | `deadline` column exists; nothing uses it |
| C18 | Progress display updates without page reload | FAIL | No display |
| C19 | Spec example math reproduces ($1,000 fund, $190 + $56/mo) | PARTIAL | `projectGoal` math is correct and unit-verified; the spec's exact numbers flow through Guide evidence formatting that can never trigger |
| C20 | "Never require the user to update a goal" (spec hard-never #2) | PASS (vacuous) | Nothing requires it — because nothing exists |

## D. Persistence (localStorage or DB)

| # | Assertion | Verdict | Evidence |
|---|-----------|---------|----------|
| D1 | Goals persist across sessions | FAIL | No client read/write of `finance_goals`; no localStorage keys |
| D2 | `finance_goals` table exists in production | PASS | Queried live: table present, RLS enabled |
| D3 | RLS restricts rows to the owning user | PASS | Policy `own_finance_goals`: `auth.uid() = user_id`, FOR ALL |
| D4 | Client reads `finance_goals` | FAIL | Zero `finance_goals` references in template or `index.html` |
| D5 | Client writes `finance_goals` | FAIL | Zero references; old `saveInsert("finance_goals", ...)` deleted in `5ef487f` |
| D6 | Schema matches spec fields (name, target_amount, current_amount, created_at, status) | PASS | All columns exist, plus `deadline` and `id`/`user_id` |
| D7 | Status CHECK matches spec (`active`, `reached`, `abandoned`) | FAIL | DB constraint is `('active','done','archived')` — spec's `reached`/`abandoned` are **rejected** by the DB |
| D8 | Demo seed row is clearly marked and quarantined | FAIL (data) | Row `d1111111-...` ("$1,000 emergency fund", 1000, 340, active) for `demo@upmore.app` still in **production**; harmless only because no client reads it |
| D9 | QA residue is cleaned up | FAIL (data) | Row `f4d01089-...` ("Test goal", 500, 0, active) — left by an earlier test agent — still in production DB for the demo user |
| D10 | localStorage goal keys exist as fallback | FAIL | No `upmore-goal*` keys; localStorage used only for onboarding/prefs/cancel records |
| D11 | Deleting a goal removes it (no zombie rows) | N/A | No delete path; nothing to test |
| D12 | `target_amount > 0` enforced | PASS | Schema CHECK intact |
| D13 | `current_amount` defaults to 0, not NULL | PASS | `DEFAULT 0` intact |
| D14 | Goal rows reference a real user profile (FK) | PASS | `user_id REFERENCES public.profiles(id) ON DELETE CASCADE` |
| D15 | No goal data leaks to other users | PASS | RLS `auth.uid() = user_id` on all operations |

## E. Spec rule compliance

| # | Assertion | Verdict | Evidence |
|---|-----------|---------|----------|
| E1 | Goals exist to give the plan engine something to optimise toward | FAIL | Plan engine receives `goals: []`; goals can't steer any plan |
| E2 | Projection is a function call, always | PARTIAL | `projectGoal()` is a real function and its math is unit-verified; never invoked on real data |
| E3 | The model explains; the model never estimates | PARTIAL | Evidence string format exists (`Goal: $X of $Y.`); unreachable |
| E4 | Plans cap at three actions | PASS | `buildBudgetPlan` max-3 logic intact (goal-independent) |
| E5 | Every plan step names its evidence | PASS | Goal evidence line exists in code (unreachable) |
| E6 | Goals are never suggested by Upmore (spec hard-never #8) | PASS (vacuous) | Nothing suggests anything about goals |
| E7 | No guilt/streaks/badges around goals (spec #6) | PASS (vacuous) | Old UI had none either — just a neutral progress bar |
| E8 | No comparison to other users | PASS | No goal data displayed at all |
| E9 | `created_at` recorded for pace | PASS (schema) | `DEFAULT now()` |
| E10 | Goal name is the user's words, shown back verbatim | FAIL | Old UI did this correctly (`esc(g.name)`); deleted |
| E11 | Guide `has()` covers goal-setting intents | FAIL | No intent branches for "goal", "savings goal", "emergency fund" |
| E12 | Deleting the user's account wipes their goals | PASS (schema) | FK `ON DELETE CASCADE` |

## F. Design (each task: 4 function + 1 design)

| # | Assertion | Verdict | Evidence |
|---|-----------|---------|----------|
| F1 | `.goalcard` styling is used by real UI | FAIL | Dead CSS; design points can't be earned by unused styles |
| F2 | The design meets "very very simple pages" | N/A | No goals page to judge |
| F3 | Progress bar is glanceable (single bar, no clutter) | FAIL (was PASS) | Old `.goaltrack`/`.goalfill` was appropriately minimal; deleted |
| F4 | Old goal form matched the app's input style | FAIL (was PASS) | Old form used standard inputs; deleted |
| F5 | No design regressions from deletion | PASS | Dead CSS is 6 lines; harmless but should be removed for cleanliness |
| F6 | Mobile layout for goals | N/A | No UI |
| F7 | Accessibility (labels, not placeholder-only) | FAIL (was PARTIAL) | Old form relied on `placeholder` with no `<label>`; deleted anyway |
| F8 | Design point claimable | NO | Cannot award the design point — there is no user-visible goals output |

## G. What the old (deleted) implementation got right vs wrong

**Right (worth preserving in the rebuild):**
- User entered name + target amount only; progress was never user-entered (spec-conformant input model)
- Progress-bar formula correct and capped at 100
- Neutral tone, no guilt mechanics
- Minimal design

**Wrong (the reasons it failed spec, beyond the demo-data honesty bug):**
1. `current_amount` was **stored static** (`0` on create) and never recomputed from a designated account or from Received+Avoided ledger entries since `created_at` — the core spec requirement was never implemented
2. Demo seed (`$340`) rendered as real 34% progress — fabricated progress for a demo user
3. Guide fact pack hardcodes `goals: []` — plan-engine goal projection unreachable
4. DB status values (`done`/`archived`) reject the spec's (`reached`/`abandoned`)
5. Unlimited goals, no "one active goal by default" nudge
6. No Guide chat path to set a goal

## Score

- **Function (4 pts): 0/4** — feature absent; only the unreachable `projectGoal()` math and the orphaned DB table are correct
- **Design (1 pt): 0/1** — no user-visible output; dead CSS only
- **Total: 0/5 — FAIL**

## Required fixes (for the parent agent)

1. Rebuild Goals UI honestly on one of the three tabs (or in Guide): name + target amount input; **progress computed** from a designated account balance or Received+Avoided ledger since `created_at`
2. Client must read/write `finance_goals` (RLS policy already correct)
3. Wire the Guide fact pack: replace `goals: [] // TODO` with a real load so `buildBudgetPlan`'s goal branch fires
4. Align DB status CHECK with spec: `('active','reached','abandoned')`
5. Remove dead `.goalcard`/`.goaltrack`/`.goalfill` CSS or reattach it to real UI
6. Delete QA residue row `f4d01089-0edb-4081-94a8-70a90b7ffcb5` ("Test goal") from production
7. Keep the honest deletion's lesson: never render seeded/demo goal rows as user data — gate the demo seed behind the demo account or remove it
8. Enforce "one active goal by default" in UI copy
