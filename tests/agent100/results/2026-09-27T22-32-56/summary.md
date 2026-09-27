# agent100 run 2026-09-27T22-32-56 (dry) — 2026-09-27T22:32:56.474Z
Agents: 18/20 pass (90.0%) · Steps: 64/66 (97.0%) · API calls: 0 · 6s

## By lane
- cfo: 10/10
- edge: 8/10

## Failures by category
- numeric_mismatch: 2

## Failed agents (fix-loop: re-run with --only-failed)

### a091 — Age 16: earning routes refused at the age gate [edge]
- step 2 (calc):
  - [numeric_mismatch] paras.0 not a finite number

### a092 — Age 17: age gate wins over the contest refusal [edge]
- step 3 (calc):
  - [numeric_mismatch] paras.0 not a finite number