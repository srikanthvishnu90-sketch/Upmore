# agent100 — Upmore 100-agent end-to-end test program

100 materially different test agents. Each agent = a persona (18+, varied
income/debt/state/goals) + a scenario script covering real user journeys:
all 5 tabs, every connector, investing X-ray, budgeting, tracking, claiming,
and Guide adversarial probes.

## How it works

Agents run against the **built app's real logic**, extracted from
`~/workspace/upmore/index.html` into a Node sandbox (`harness/extract.js`):
the deterministic Guide engine (`guideAnswer` with all refusal slots), the CFO
calculators (`debtSim`, `marginalRate2026`, …), the investments X-ray
(`portfolioSummary`, `feeFor`, …), and route gating (`routeIsBlocked`,
`earnable`). No network, no mocks of app logic — the assertions test the
actual shipped code. Nothing in the app is modified.

## Modes

### DRY-RUN (default, $0.00)
Tests UI flows, calculators, Guide logic, disclosures, and refusal behavior
with zero API calls and zero network.

```bash
node harness/runner.js --mode dry --all                 # all 100 agents
node harness/runner.js --mode dry --lane guide-adversarial
node harness/runner.js --mode dry --agents a001,a002
```

### LIVE (hard-gated)
Full E2E with real connected accounts. Requires **both**:
1. `--mode live`
2. `--founder-confirm "APPROVE LIVE"` (+ interactive confirmation unless `--yes`)

Without both, the runner **refuses** and exits — nothing executes.

```bash
node harness/runner.js --print-cost --mode live --all   # projected worst case, no execution
node harness/runner.js --mode live --founder-confirm "APPROVE LIVE" --all
```

`backend` steps call the real agent-chat (≤12 calls/agent, hard cap).
`liveBrowser` steps are **never executed by the runner** — they are marked
`deferred` for parent-agent browser delegation (real Playwright sessions).

### LLM judge (optional, budgeted)
Subjective quality only (tone, no-guilt framing), with the written rubric in
`harness/rubric.md`. Off by default; runs on a sample:

```bash
ANTHROPIC_API_KEY=... node harness/runner.js --mode dry --all --judge-sample 5
```

Each judged step = 1 API call, counted against the per-agent cap and the
suite budget. Deterministic facts are never judged — only code asserts those.

## Fix-loop

```bash
node harness/runner.js --mode dry --all --only-failed   # re-run only failures
```

Results land in `results/<timestamp>/` (`agents.json`, `summary.json`,
`summary.md`); `results/latest.json` tracks the newest run. Fix the app,
re-run `--only-failed`, repeat until green.

## Reading results

`summary.md` gives pass rate, per-lane breakdown, failures by category, and the
full list of failed agents with their failing assertions. Failure categories:
`refusal_failure`, `advice_violation`, `guarantee_violation`, `dishonesty`
(includes numbers that don't trace to inputs), `numeric_mismatch`,
`constraint_ignored`, `disclosure_missing`, `static_mismatch`, `crash`,
`timeout`, `budget_exceeded`, `judge_quality`, `deferred`.

## Adding agents

See `AGENT_SPEC.md`. Validate with `node validate-agents.js` (schema +
coverage + template-clone detection; fails any pair with similarity > 0.85).

## Cost model

`harness/budget.js` prints the projected worst-case live cost before any live
run (conservative Sonnet-class pricing assumptions, shown in the output).
Dry-run is always $0. Founder credits are testing-only — the harness is
designed so the full 100-agent dry suite spends nothing.
