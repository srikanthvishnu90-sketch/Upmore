# Agent B6 — Budget: Goals — HARSH TEST REPORT

**Verdict: FAIL** — the Goals feature does not exist in the app. It is dead code, dead CSS, and an unread database table.

## What the spec demands (Doc 3: Budget)

- Goals: name (user's words), target_amount (user-set), current_amount (**computed** from a designated account, **not user-entered**), created_at, status (active/reached/abandoned).
- Progress is **computed, not reported**. The user never updates a goal.
- Projection is a function call, always: `projectGoal(goal_id, monthly_delta)`. The model explains it. The model never estimates it.
- One active goal by default. Multiple goals split attention; a second is possible but not encouraged.
- **Goals are never suggested.** Upmore does not tell a user they should be saving for an emergency fund.

## Findings

### 1. No goal creation UI exists (FAIL)
- Searched the full app template for goal-creation surfaces: `set a goal`, `new goal`, `add a goal`, goal name/amount inputs — **zero hits**.
- A user cannot create a goal. The spec's first requirement (user sets name + target) is unimplementable in the UI.

### 2. No goal display exists (FAIL)
- `.goalcard` CSS is defined (template lines 336–341: `.goalcard`, `.grow`, `.t`, `.amt`, `.goaltrack`, `.goalfill`) — but **no JavaScript or HTML ever renders an element with class `goalcard`**. Dead CSS.
- No `renderGoals`, `renderGoalCard`, or equivalent function exists anywhere in the app.

### 3. `projectGoal()` is dead code (FAIL)
- `function projectGoal(goal, monthlyDelta)` is defined (template line 3269) but **never called** by any code path.
- Since the projection function never runs, the spec's "projection is a function call, always" is trivially unmet — there are no projections at all.

### 4. `buildBudgetPlan()` is dead code (FAIL)
- Defined at template line 3289, references `factPack.goals` and calls `projectGoal()` — but **never invoked** anywhere in the app.
- The plan-engine goal action ("Add $X/mo toward ... about N weeks") can never render.

### 5. The database table is written but never read (FAIL)
- `public.finance_goals` exists in Supabase (`supabase/migrations/20260924_000002_finance.sql`, RLS owner-only — schema itself is fine).
- **No app code references `finance_goals`** — zero reads, zero writes from the client. The table is unreachable from the product.

### 6. A goal the user never set is seeded for the demo user (VIOLATION)
- The migration seeds: `('$1,000 emergency fund', target 1000, current_amount 340)` for demo user `1f9b18e5-928c-44ce-9d7e-d77c0e57f396`.
- The spec: **"Goals are never suggested. Upmore does not tell a user they should be saving for an emergency fund."**
- A pre-seeded "$1,000 emergency fund" goal is precisely the app telling a user they should be saving for an emergency fund. This is the same anti-pattern the Track spec already condemned (hardcoded `finance_alerts` seed rows presented as real monitor output). If this row ever becomes visible, it is a spec violation by construction.
- Additionally, the seed writes `current_amount = 340` directly into the table, while the spec requires current_amount to be **computed, never entered** — the schema even permits arbitrary writes to `current_amount` with no designated-account linkage.

### 7. "One active goal by default" — untestable (FAIL)
- With no creation, no display, and no status handling, the single-vs-multiple goal logic does not exist. `status` column supports `active/done/archived` but nothing in the app transitions it.

## What I could NOT verify (no live browser at this depth)

- Visual confirmation that no goal UI appears on Home/Guide/You tabs (code inspection shows none can render — high confidence).
- Whether the seeded demo goal is visible to the demo account in production (the table is unread by the client, so it cannot be — but the seed row should still be removed as a matter of hygiene).

## Harsh summary

This is not a partially-built feature. It is a **spec-shaped hole**: the function names exist (`projectGoal`, `buildBudgetPlan`), the CSS exists (`.goalcard`), the table exists (`finance_goals`) — everything except the feature itself. It reads like the scaffolding was laid and the build stopped. And the one concrete artifact that does exist — the seeded "$1,000 emergency fund" — is the exact thing the spec forbids: a suggested goal.

**To pass**, the app needs: a goal-creation surface (name + target only), computed progress from a designated account or ledger (Received + Avoided since creation), a rendered goal card, `projectGoal()` actually called for projections, one-active-goal default, and deletion of the seeded demo goal.
