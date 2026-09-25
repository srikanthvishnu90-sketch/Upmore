# Agent B3 — Budget: Plan Engine — HARSH TEST REPORT

**Verdict: FAIL (critical — the plan engine never runs)**

Tested: 2026-09-24 ~23:40 CDT
Commit: 0c2eb30 (production)
Method: Direct source-code audit of `src/upmore-app-template.html` (built `index.html` verified identical) + live page-text fetch of production. Browser-task UI testing was unavailable to this agent (generic subagents cannot spawn browser tasks); the code audit is more definitive than a UI test for the question "does the plan engine execute."

---

## The critical failure: `buildBudgetPlan` is dead code

`buildBudgetPlan(factPack)` is defined at template line 3289. It has **exactly zero callers** in the entire codebase:

```
$ grep -n "buildBudgetPlan(" src/upmore-app-template.html
3289:  function buildBudgetPlan(factPack) {
```

No code anywhere:
- constructs a `factPack` (`grep factPack` returns only the function's own parameter references),
- invokes `buildBudgetPlan`,
- or renders plan actions into any UI surface.

The Budget spec (Doc 3) states: *"Budget here is not a screen with envelopes. It is one number on Home, a set of monitors, and **a plan the agent produces**."* The one number (Safe to Spend) exists on Home. The monitors exist. **The plan does not exist in any user-visible form.** A user asking the Guide for a budget plan gets Earn-route answers (the Guide's "plan" concept is money-making routes, not budget actions) — there is no budget-plan intent in `guideAnswer`, `trackedAnswer`, or the local fallback chain.

The plan engine — which the spec calls *"the feature nobody else has, and the only place in Budget where a model genuinely earns its cost"* and *"the differentiator"* — is a function that never executes. This is not a partial implementation. It is a non-functional one.

## The deterministic function layer is also dead

- `projectBalance` (line 3261): defined, **never called**.
- `feeImpact` (line 3275): defined, **never called**.
- `projectGoal` (line 3269): called exactly once — inside the dead `buildBudgetPlan`.

The spec's build order is explicit: *"The function layer before the plan engine, always. A model that can plan but cannot compute will estimate."* The function layer exists but nothing — neither code nor model — ever calls it. Any plan-like numbers the remote agent backend might produce are therefore unverifiable estimates, which is the exact failure mode the spec exists to prevent.

## What the dead function gets right (credit where due)

Auditing `buildBudgetPlan` as written, the logic is mostly spec-compliant:

| Requirement | Status in code |
|---|---|
| Maximum three actions | ✅ `return actions.slice(0, 3)` — hard-enforced |
| Every action cites evidence | ✅ all three action shapes carry an `evidence` string with checkable figures ("N charges detected", "$X/year at stake", "N overdraft fees in 90 days") |
| No loans / consolidation / earned-wage access / credit cards | ✅ none present; EXRULES exclusion list blocks "credit card churn" and "payday loan" intents |
| Figures from functions | ⚠️ `projectGoal()` used for the goal action; but the waste action uses inline math (`r.amount * 12 * 0.5 * r.confidence`) instead of the spec's `wasteScore()` |
| First action doable today | ⚠️ **VIOLATION in edge case** — if no waste qualifies and fees < 2 but a goal exists, the first (only) action is the goal action with `doableToday: false`. The spec: "Never show a plan whose first step is not concretely actionable today." |

## Architecture deviation (noted, not failed)

The spec describes a model+tools loop: model reads the fact pack, proposes candidates, calls `projectBalance`/`projectGoal`/`feeImpact`, explains results. The implementation is pure hardcoded code (3 fixed action types, no model involvement). This deviates from the spec's letter but not obviously from its user-facing guarantees — *if it ran*. Dead code has no architecture.

## What was NOT found (passed checks)

- No loan, consolidation, earned-wage-access, or credit-card recommendations anywhere in app copy or Guide responses. **PASS.**
- No guilt mechanics in plan code (no streaks/badges/shame in `buildBudgetPlan`). **PASS** (moot — it never runs).
- No plan exceeding 3 actions is constructible from this code. **PASS** (moot).

## Required fixes

1. **Wire the plan engine up or remove the claim.** Either: assemble a real `factPack` from Track data (recurring charges, fee history, goals), call `buildBudgetPlan`, and render the resulting actions in a user-visible surface (Home and/or Guide intent, e.g. "give me a budget plan"); or stop representing Budget as having a plan engine.
2. Fix the goal-only edge case: never emit a plan whose first action has `doableToday: false`. If only the goal action qualifies, either lead with something doable today or decline to show a plan.
3. Route the waste action through the spec's `wasteScore()` instead of inline math, so the ranking is the specified formula.
4. Decide the model-vs-code question explicitly: if the plan stays pure code, the "model proposes, functions compute" tool-use pattern from the spec is unimplemented — say so in the spec or implement it.

---

## Browser-test delegation needed

This agent could not perform the UI-level checks (asking Guide for a budget plan, inspecting Home for plan surfaces) because generic subagents cannot spawn browser tasks. **Parent: please delegate a live-browser confirmation** that no budget plan surface exists in production (Home + Guide), to corroborate the code finding from the user's side of the glass.
