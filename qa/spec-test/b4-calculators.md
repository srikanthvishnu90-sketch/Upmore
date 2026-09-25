# Agent B4 — Budget: Calculators — HARSH REPORT

**Verdict: FAIL (critical)**

**Method note:** I could not launch a live browser (subagents cannot spawn browser tasks). This report is a static code-path analysis of `src/upmore-app-template.html` and `supabase/functions/agent-chat/index.ts` — which is the *stronger* evidence here, because every violation below is structural (dead code, zero call sites, hardcoded estimates), not a rendering flake. Line numbers refer to `src/upmore-app-template.html`.

---

## The spec's rule

Doc 3: `projectBalance(changes[], through_date)`, `projectGoal(goal_id, monthly_delta)`, `feeImpact(change)` — "Code computes; model explains. NEVER estimates these itself." And: "A model that can plan but cannot compute will estimate, and an estimated projection presented as a result is the exact failure mode this whole product exists to avoid."

## Finding 1: projectBalance is dead code — zero call sites (CRITICAL)

- Defined at line 3261. Called **nowhere**. Not from the chat, not from the plan engine, not from any UI.
- "What if I cancel Netflix?" has no handler at all. `grep "what if"` returns zero hits in the client. The question falls through `guideAsk` → `trackedAnswer` (no keyword match) → `agentAsk` (remote model, no tools — see Finding 5) → `guideAnswer` fallback ("I can look up any of the N routes in the catalog…"). No balance projection is ever computed.

## Finding 2: feeImpact is dead code — zero call sites (CRITICAL)

- Defined at line 3275. Called **nowhere**.

## Finding 3: projectGoal is doubly dead (CRITICAL)

- Defined at line 3269. Its only call site is line 3311, inside `buildBudgetPlan`.
- `buildBudgetPlan` (line 3289) itself has **zero call sites**. The entire plan engine is unreachable from any user surface. There is no plan UI, no chat intent, nothing that invokes it.

## Finding 4: "When will I hit $1000 if I save $50/month?" gets a hardcoded estimate, not a computation (CRITICAL)

Trace through `guideAnswer`:
1. The question contains "1000" → matches the hardcoded `$1000` branch (~line 2600) **before** any savings logic is considered.
2. It returns canned Userfeel copy: `"The math, straight: $1,000 means roughly 100 tests."`
3. Problems:
   - **"roughly"** — the literal weasel word the spec forbids before numbers. This is an estimate presented as a result.
   - **It answers the wrong question.** The user asked about *saving* $50/month toward $1,000 (a `projectGoal` question: 1000/50 = 20 months, computable exactly). The app answers about *earning* via Userfeel tests. The `$50/month` savings rate is silently discarded.
   - `projectGoal` is never consulted, even though the inputs (target $1,000, rate $50/mo) are parseable from the question.

## Finding 5: the remote model has no function tools (CRITICAL)

- Signed-in users hit `agentAsk` → `supabase/functions/agent-chat/index.ts`.
- That function calls Anthropic/Claude (8 references) but defines **no tools** — no `projectBalance`, no `projectGoal`, no `feeImpact`, no tool array of any kind.
- So for every scenario question ("What if I cancel these three?", "What if I move rent to the 5th?", "When do I hit $1,000 if I add $50?"), the model can only answer in prose. Every number it produces is an estimate by construction. The spec's tool-use pattern ("the model decides what to compute, a function computes it, the model explains the result") does not exist server-side either.

## Finding 6: shipped copy contains the exact banned failure mode

- Line 2605: `"The math, straight: $1,000 means roughly 100 tests."`
- Line 2663: `` `at ~$${unit} a go, $${goal} means roughly ${Math.ceil(goal / unit)} of these` ``
- Both present estimates as computed results, introduced by "The math, straight:" — which makes the estimate *look* authoritative. This is precisely "an estimated projection presented as a result."

## Finding 7: spec build order violated in the worst way

The spec demands "The function layer before the plan engine, always." What shipped is worse than missing functions: the functions *exist*, which makes the feature look implemented in a code review, but they are unreachable. A reviewer grepping for `projectBalance` finds a definition and moves on. The honest state — "not implemented" — would be less dangerous than this.

## What actually passes

- `calcSafeToSpend` (line 3254) **is** called (line 3201, in `renderTrackStrip`) and renders total/daily/buffer/cycle-end. The Safe-to-Spend number is genuinely computed. This is the only calculator in the spec that is wired up.

## Required fixes

1. Wire `projectGoal` into the `$1000`/savings intents in `guideAnswer` — parse (target, monthly rate), call the function, render its output. Delete the "roughly 100 tests" estimate or route it through the function.
2. Implement the scenario intent: detect "what if I cancel X / move Y" questions, translate to `projectBalance`/`feeImpact` calls, render computed results. Currently zero handling exists.
3. Either call `buildBudgetPlan` from a real surface (chat intent or Home) or delete it — dead plan engines rot.
4. Add `projectBalance`/`projectGoal`/`feeImpact` as tools to the `agent-chat` Edge Function so the remote model *can* compute instead of estimate. Until then, the signed-in path violates the spec on every numeric answer.
5. Grep shipped copy for "roughly", "about", "~$" preceding any number in Guide answers; each one is a spec violation until backed by a function call.
