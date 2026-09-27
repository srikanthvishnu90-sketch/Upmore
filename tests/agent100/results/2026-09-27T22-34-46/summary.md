# agent100 run 2026-09-27T22-34-46 (dry) — 2026-09-27T22:34:46.426Z
Agents: 1/2 pass (50.0%) · Steps: 5/6 (83.3%) · API calls: 0 · 1s

## By lane
- guide-adversarial: 1/1
- investing: 0/1

## Failures by category
- numeric_mismatch: 1

## Failed agents (fix-loop: re-run with --only-failed)

### a015 — 25% concentration flagged; Guide refuses the sell-half ask [investing]
- step 1 (calc):
  - [numeric_mismatch] concentrated.length=2, expected 1 (tol 0.01)