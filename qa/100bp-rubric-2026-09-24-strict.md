# Upmore 100-Basis-Point Rubric — STRICT re-score 2026-09-24

Re-scored under Vishnu's binary rule: a basis point is awarded ONLY when the
capability is live, repeatable, and production-tested. Prototypes, partial
implementations, and one-off demos earn zero. All 🟡 from the 2026-09-23
scoring collapse to 0 unless they meet the bar.

## Changed since 2026-09-23 (all live in production)

- agent-chat: 3 malformed responses fixed, placeholder scope bug fixed,
  generic provider-word filter expanded (Neevo correctly routes to R9227)
- capabilities.ts: honest TDZ crash fixed
- 424 walkthrough steps carry tap-to-copy profile chips (DB + bundle agree)
- 6 awkward placeholder matches stripped
- Live gigs section in Explore (6 HN contract candidates, 14-day freshness)
- web_agent.py: browser agent smoke-tested end-to-end (fills safe fields,
  skips password/payment, never submits, screenshots, waiting_user handoff)
- Disposable test user + job + profile deleted after testing

## Scores

| Category | 09-23 (with half-credit) | 09-24 strict | Notes |
|----------|--------------------------|--------------|-------|
| A. Live opportunity discovery | 0.0 | 0.0 | Scraper runs, but candidates unverified; no minute cadence, no dedupe, no scam filter, no alerts |
| B. Data freshness | 0.0 | 0.0 | Verified once, not continuously |
| C. Personalization | 1.5 | 0.0 | Foundations exist (progress tracking, app-required labels); none production-tested as adaptive |
| D. Guide agent | 2.0 | 0.0 | Guide works end-to-end (15 real replies), but "any question + cited" not stress-tested; multi-turn, don't-know, and comparison paths unverified |
| E. Subscription & bill control | 0.0 | 0.0 | Specced, not built |
| F. Shopping agent | 0.0 | 0.0 | Specced, not built |
| G. Trust & honesty | 4.0 | 1.0 | #65 zero dark patterns holds (verifiable by inspection). #61/#62/#63/#64/#66 partial, untested. #70 export/delete added but signed-in path untested |
| H. Speed & performance | 2.5 | 1.0 | #74 instant catalog search is live and working. Offline/PWA/guide-latency unmeasured |
| I. Platform & reach | 0.0 | 0.0 | Web only |
| J. Business readiness | 1.0 | 1.0 | #97 privacy policy live (support@upmore.app still provisional — Vishnu to provide real address) |
| **TOTAL** | **11.0** | **3.0 / 100** | |

**3.0 basis points out of 100 (0.03).**

Reading it honestly: the strict score measures what is real today — a deep,
honest, searchable catalog with a working Guide, zero dark patterns, and a
live privacy policy. Everything else is foundation, not capability.

What moved today but earns no points yet (real, but not rubric scenarios or
not yet hardened): the web agent's safe-fill loop (needs server-authorized
URLs, durable sessions, and the interactive handoff before it counts), the HN
gig candidates (need link/scam/availability verification), the 424 walkthrough
chips (UI polish on an already-counted catalog).

Biggest levers remain: A (live discovery), E+F (20 specced features), B
(continuous verification).
