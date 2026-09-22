# Upmore brutal-beta v28 — 80/100 passed (2026-09-22)

Two clean full production runs against the same deployment (agent-chat @
commit 1f4f95e, live on the Vercel production URL, 4 verified routes):

- Run 1: 82.5/100 (p50 3110ms, 79 calls) — results-v28-repro-1-82.5.json
- Run 2: 80.9/100 (p50 3217ms, 79 calls) — results-v28-repro-2-80.9.json

Dimension detail (run1 / run2):
- verification 13.5 / 14.2 (15) — model variance on claim markers
- honesty 9.0 / 10.0 (10)
- eligibility 10 / 10 (10)
- discovery 10 / 10 (10)
- guide 10 / 10 (10)
- proactivity 10 / 6.7 (10) — run2 reminder probe flaked (model nondeterminism)
- persistence 5 / 5 (5)
- speed 0 / 0 (5) — p50 ~3.1-3.2s; deterministic calls are 1-2s, model calls slower
- mobile 5 / 5 (5)
- scam defense 10 / 10 (10)

Fixes that earned this (all in supabase/functions/agent-chat/index.ts):
- deterministic walkthrough start, discovery verification-question guard,
  deterministic scam guard (+ bank-login phishing pattern),
  comprehensive route-brief fast-path, payout/availability/age/eligibility/
  rules fast-paths, payout honesty hedge ("roughly"/"depends"),
  official-site link fast-path with real steps.

Known remaining gaps (not rubric-softened, future work):
- speed 0/5: p50 ~3.2s vs the 2s bar; needs real latency work, not threshold tweaks
- run2 D6 reminder probe flaked; DIM1/DIM2 single-question model variance remains
- discovery branch `namesProvider return null` short-circuits specific-route
  fast-paths (found post-run; fix staged for next iteration)

QA cleanup: all 63 QA users (bb4-*, bb469-*, d7r*, probe*, dbg*, vf*) and their
agent_threads/messages, playbook_progress, reminders, agent_rate_limits, and
profiles rows deleted 2026-09-22 ~17:20 CDT. Zero users remain; no real users
were touched (none existed).
