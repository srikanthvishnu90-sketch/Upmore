# Agent B5 — Budget: Hardship Escalation — HARSH TEST REPORT

**Verdict: FAIL (critical — spec requirement entirely unimplemented)**

## Spec requirement (Doc 3, "Wellbeing constraints")

> Escalate, don't optimise. If free cash is persistently negative, the product stops
> suggesting trims and says the real thing: hardship programs, utility assistance,
> income-driven repayment. A user in genuine distress being shown a plan to cancel
> Netflix is being failed.

## Method

Live-browser testing was **not available** at my depth (generic subagent: no
`browser.spawn_task` delegation). Instead I performed a full code-level audit of the
shipped implementation — which is decisive here, because the feature does not
exist in code at all. No browser session could pass a test for a code path that
was never written.

Searched: `src/upmore-app-template.html` (full client), `supabase/functions/agent-chat/index.ts`,
`supabase/functions/_shared/agent.ts` (agent system prompt).

## Findings

### 1. Zero hardship content anywhere — FAIL
Case-insensitive search for `hardship`, `utility assist`, `income-driven`,
`income driven`, `assistance program`, `211`, `liheap`, `snap`, `food bank`,
`can't afford`, `struggling` across client code and both edge-function files:
**zero hits** (the single "negative" hit in the client is a Capital-wall comment
about suppressing investment content — unrelated).

There is no copy, no card, no chat branch, no system-prompt instruction that
mentions hardship programs, utility assistance, or income-driven repayment.
The escalation path the spec mandates was never built.

### 2. `buildBudgetPlan` has no negative-free-cash guard — FAIL (exact spec failure mode)
`buildBudgetPlan(factPack)` (`src/upmore-app-template.html:3289`) unconditionally
picks the highest-waste recurring charge and proposes `Cancel {merchant}` as
action #1. There is no check on `factPack.freeCash`, no early return, no
alternate branch. If this function were ever called for a user with persistently
negative free cash, it would produce precisely the outcome the spec forbids:
a distressed user being told to cancel a subscription.

### 3. `buildBudgetPlan` is dead code — FAIL
`buildBudgetPlan` is defined once and **called zero times** anywhere in the
template. The "plan engine" does not reach any UI surface. So even the
non-escalation plan path is unshipped; the escalation path doubly so.

### 4. Queue would still push trims to a distressed user — FAIL
`buildQueue()` injects monitor-driven cancel cards from `detectRecurrence()` for
any subscription with `wasteScore > 30`, with no free-cash gate. A user with
negative free cash sees the same "Cancel Netflix?"-style cards as everyone
else. Nothing in the queue pipeline checks distress.

### 5. Safe-to-spend negative rendering — PASS (narrowly)
`renderTrackStrip()` renders a negative safe-to-spend number plainly via `fmt$`
with no shaming copy ("you're overspending", red badges, etc.). This satisfies
the "never negative-shame" rule, but it is the absence of a violation, not the
presence of the required escalation.

### 6. Agent system prompt — FAIL
`SYSTEM_PROMPT` (`supabase/functions/_shared/agent.ts`) is entirely Earn-route
focused. It contains no instruction for detecting financial distress, no
hardship-program knowledge, and no directive to stop optimizing trims when the
user can't cover basics. A user telling the Guide "I can't pay rent" gets the
route-recommendation machinery, not escalation.

## What "persistently negative" detection would require (not present)
- A free-cash time series or consecutive-negative-cycle counter: absent.
- A threshold/branch in `buildBudgetPlan` or `buildQueue`: absent.
- Escalation copy (hardship programs, utility assistance, income-driven
  repayment): absent everywhere.

## Recommendation for the fix
1. Add a `isDistressed(freeCashHistory)` check (e.g., free cash negative for 2+
   consecutive cycles or below -$X) computed alongside `calcFreeCash`.
2. When distressed: suppress trim/cancel cards in `buildQueue`, and render a
   dedicated escalation card naming hardship programs, utility assistance
   (e.g., LIHEAP), and income-driven repayment — plain, no shame, no trims.
3. Add the same branch to the agent system prompt so the Guide escalates in chat.
4. Wire `buildBudgetPlan` into a real surface or delete it; dead code that
   contradicts the spec is worse than no code.

## Bottom line
The spec's most morally load-bearing requirement — *don't show a drowning user
a plan to cancel Netflix* — is 0% implemented. Not partially, not buggy:
absent. This is a **FAIL** requiring implementation, not a tweak.
