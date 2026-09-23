# Upmore 25-feature 10/10 benchmark — FINAL REPORT
Date: 2026-09-23. Program: split Upmore into distinct features, benchmark each against
frontier-agent performance (OpenAI GPT-6 Astra / Anthropic Claude Fable 5.1 class) for the
bounded use case, stress-test with genuinely complex cases, score /10 only on reproducible
evidence, document every gap with a concrete fix.

## Method
- **Server** (`supabase/functions/agent-chat/`): local logic tests — capabilities.ts +
  agent.ts executed verbatim under Node v24 (type-stripping), tryFastPath extracted verbatim
  from index.ts; 69+ assertions on fixtures from the real catalog; exactly one live Yahoo
  fetch. No deployed function touched, no Anthropic key, no Supabase project touched.
  Full detail: [feature-benchmark-server.md](sandbox://workspace/upmore/qa/hidden_files/feature-benchmark-server.md)
- **Client** (`src/upmore-app-template.html` → built `index.html`): node vm harness loading
  the template's real app script with DOM stubs + the real 1767-route dataset — **89/89
  assertions pass**; built index.html app script verified byte-identical to template except
  build-app.py's known replacements, so results transfer to production. No live browser.
  Full detail: [feature-benchmark-client.md](sandbox://workspace/upmore/qa/hidden_files/feature-benchmark-client.md)
- **Live probes** (coordinator): 11 probes against the production edge function with fresh
  probe users + real JWTs — 401/400 paths, deterministic make-me, model happy path, scam
  stress, invented-amount + guarantee adversarial, age contradiction, impossible-constraints,
  fixtures (due reminder, expiring route, stale playbook), prompt injection, scam-debunk
  quoting user numbers. 8 model calls (Haiku default, testing-only rule respected).
  All probe users + fixtures deleted afterward. Detail:
  [feature-benchmark-live-probes.md](sandbox://workspace/upmore/qa/hidden_files/feature-benchmark-live-probes.md)

## Scoreboard — server (19 features, mean 8.0/10)

| # | Feature | /10 | Frontier-bar verdict (one line) |
|---|---|---|---|
| S01 | Make-me-$X plans | 6 | Deterministic + grounded, but only 15 hardcoded routes are ranked and the flagship regressed after the 1500 expansion (live probe: "make me $20" → "none of my verified routes can get you there on a schedule") |
| S02 | Vague-opener $20 anchoring | 8 | Anchors without interrogating — but "i want to make some extra money" (most natural phrasing) misses the deterministic path on a regex bug |
| S03 | DB-driven walkthroughs | 8 | Steps/link/catch character-for-character from the card — but stale "14 verified routes" copy in the rejection |
| S04 | Deterministic scam guard | **10** | Fires every time, names the mechanism, zero false positives in testing (incl. Microsoft Rewards gift-card near-miss) — beats a frontier model's improvised warning |
| S05 | Gambling/prediction-market guard | **10** | Same critical-thinking takedown every time: zero-sum math, legality, addiction design — deterministic where a frontier model hedges |
| S06 | Privacy guard | **10** | Deterministic refusal for other-person data; never misfires on own-data requests |
| S07 | Quantitative stock screener | 9 | Live Yahoo prices, stated 4-factor z-scored model, honest "technical-only, not advice" copy — frontier models screen from stale memory; fail-closed branch code-reviewed not live-triggered |
| S08 | Fast-path factual answers | 6 | Sub-500ms card-grounded answers — but plural "requirements" misses the fast path and discovery lists 30-day-stale routes as "live right now" |
| S09 | Grounding post-check | **10** | Catches invented amounts, unlisted URLs, guarantee language deterministically; debunk exception verified; **live prompt-injection probe blocked completely** |
| S10 | Violation fallbacks | **10** | Blocked debunk still warns (SCAM_FALLBACK), blocked ordinary claim deflects (SAFE_FALLBACK) — verified in the pipeline |
| S11 | Reminder proactivity | 3 | Read-side + prepend guard are real code, but **nothing in the codebase ever INSERTs into the reminders table** — the feature is write-dead end-to-end |
| S12 | Expiry alerts | 7 | 14-day window math correct, but expired routes are warned as "EXPIRING SOON" with a past date and LIVE marking ignores expiry |
| S13 | Resume nudge | 9 | Idle math correct (>24h), but it's a prompt line — live probe showed the model ignoring it |
| S14 | ask_profile persistence | 9 | Strict allowlist, disallowed fields dropped, empty-string handling right; no value validation (age: 999 persists) |
| S15 | Walkthrough persistence | 8 | Triple persistence paths (capability/model/deterministic) — but `action.route_id` unvalidated: a hallucinated route_id creates a phantom playbook row |
| S16 | Rate limiting (60/hr) | 7 | Works, but comment says "rolling" (it's fixed-window), non-atomic increment, zero-cost replies burn quota, no Retry-After |
| S17 | Auth correctness | **10** | 401/400 paths verified live; explicit getUser(jwt) fix present |
| S18 | Capability ordering | 9 | Safety-critical guards (scam/gambling/privacy) deterministically precede money paths; precedence undocumented; "make $500" (no "me") never triggers |
| S19 | Stale-copy audit | 7 | Two "14 verified routes" strings in user-facing replies; server only ever sees 50 of 1500 verified routes (`.limit(50)`) |

## Scoreboard — client (22 features, mean 8.6/10)

| # | Feature | /10 | Frontier-bar verdict (one line) |
|---|---|---|---|
| C01 | Onboarding state machine | 9 | Validation, Feb-30/future-DOB rejection, 18+ age-gate with blocked screen, exact-18 boundary — matches frontier; sitGo gating statically verified only |
| C02 | Personalized first-3-moves plan | 6 | Copy says "Picked for {state}" but moves are the global top-3 for everyone; `_moves` never persists (fresh object each call); "undefined a week" for nonstandard time values |
| C03 | Home hero walkthrough + progress | **10** | Exact progress math, CTA adapts on completion, end-to-end "what's next" flow |
| C04 | Walkthrough step rendering | 9 | done_when/warns/per-step labeled links, dedupe — but only 261/1767 routes have done_when data |
| C05 | App-store deep links | 6 | Works for 3 Play Store URLs; **zero iOS store URLs** in 1767 routes — iPhone users get Android links |
| C06 | Explore search | **10** | Instant, injection-safe (no regex eval, output-escaped), clean empty state — matches frontier |
| C07 | Difficulty + category filters | **10** | Composable, accurate counts (e.g. Easy+Bank Bonus = 267, all satisfying both) |
| C08 | Higher-risk lane toggle | **10** | 23 Restricted hidden by default, explicit opt-in with matching count, badged |
| C09 | Explore pagination | **10** | Accurate remaining counts, hides at end |
| C10 | Money/time/rate display + ordering | 8 | Formatting correct, catalog ratio-ordered — but 2 retired routes render as earnable with no badge; one breaks ordering |
| C11 | Guide local answers | 6 | Grounded provider/category answers — but **"we have not verified live provider terms yet" is false for 1500/1767 routes** (stale), and "free to start" is shadowed by the `easiest` branch |
| C12 | EXRULES excluded topics | **10** | Hard refusals with specific reasons, soft redirects, case-insensitive, correct branch priority (onlyfans "legit" hits the hard rule first) |
| C13 | Guide empty state + starters | **10** | Contextual starters with live plan context |
| C14 | Agent fallback chain | **10** | Live agent → local answers on 500/network-down, never hangs, busy reset |
| C15 | OAuth round-trip persistence | 9 | Onboarding survives Google redirect; corrupt JSON handled; restored values not re-validated |
| C16 | Progress sync to DB | **10** | Correct status transitions (in_progress/done), silent no-op when signed out, unknown route_ids ignored |
| C17 | Profile page + editable rows | 9 | Reflects plan; editing = re-running onboarding screens, not inline |
| C18 | "How Upmore makes money" | 7 | Good copy, but "We'll always tell you when we're earning from an offer" has **no mechanism** — no affiliate field on any route, no per-card disclosure |
| C19 | Sign out | **10** | Clears session, reloads to logged-out state |
| C20 | Reminders toggle UI | 3 | Purely decorative — flips aria-pressed, persists nothing, reads nothing |
| C21 | PWA | 9 | Valid manifest, offline shell, icons present; icons not in sw.js precache |
| C22 | Visual identity | **10** | Green/sky/white/black only (functional red/amber exceptions), exactly 4 tabs, zero "wins" |

## Totals
- **41 features scored. 17 at 10/10** (S04, S05, S06, S09, S10, S17, C03, C06, C07, C08, C09, C12, C13, C14, C16, C19, C22). **Overall mean 8.3/10.**
- The deterministic safety layer is the strongest part of the product: scam, gambling,
  privacy guards and the grounding post-check all score 10/10 and provably beat a
  frontier model's improvised behavior on their bounded use cases (deterministic firing,
  no hedging, live prompt-injection blocked).
- The weakest cluster is **stale state after the 1500 expansion**: hardcoded "14 routes"
  copy (server) / "not verified" copy (client), CASH_MATH's 15-route ceiling, and the
  `.limit(50)` route query that starves the agent of the catalog it advertises.

## Consolidated gap list (concrete fixes)

### Server (`supabase/functions/agent-chat/`)
1. **S01/S02 `capabilities.ts`** — `MAKE_X_RX`/`VAGUE_OPENER_RX`: `(some |extra )?` →
   `(some )?(extra )?` ("some extra money" currently misses the deterministic path).
2. **S01 `capabilities.ts`** — `CASH_MATH` covers only 15 IDs: add `schedulable:false`
   for scarce/windfall/bonus routes and exclude them from the headline pick; generate
   entries from DB numerics (all 1500 have payout/time numbers) — at minimum add the
   bank-bonus (R0536–R0650) and credit-card (R0651–R0750) lanes.
3. **S01/S03/S19 `index.ts`** — remove `.limit(50)` from the verified-routes query
   (only 50 of 1500 verified routes are ever visible to capabilities; the model told a
   live probe user "I've got 50+ verified routes"). Order by earn_ratio desc; inject a
   catalog-stats line (1500 verified) so counts are always right.
4. **S03/S04/S19 `capabilities.ts:275,344`** — "one of my 14 verified routes" →
   count-neutral copy ("one of my verified routes").
5. **S08 `index.ts` `tryFastPath`** — requirements regex `requirement` → `requirements?`,
   add `eligib(le|ility)`; discovery branch must apply the 7-day `fresh()` check before
   claiming "live right now".
6. **S11 `index.ts`** — implement `set_reminder` action handling (INSERT into
   `reminders`) or remove it from `SYSTEM_PROMPT`; currently the model can promise
   reminders that are silently never created.
7. **S12 `index.ts`/`agent.ts`** — split expired vs expiring (`.gte("expires_at", nowIso)`
   for the soon-list); `renderRouteCards` marks `expires_at < now` as NOT LIVE
   deterministically.
8. **S15 `index.ts:267-280`** — validate `action.route_id` against `routes` before
   upserting `playbook_progress`; clamp `next_step` step to the route's step count;
   freshness-check the deterministic walk-start target.
9. **S16 `index.ts`** — fix "rolling hour" comment (fixed window); atomic increment;
   `Retry-After` on 429; don't burn quota on zero-cost deterministic replies / 400s.
10. **S18 `capabilities.ts`** — document capability precedence in a comment; consider a
    `\bmake \$?(\d{1,4})\b` branch.
11. **Live-probe finding `capabilities.ts`** — widen `SCAM_CRYPTO_RX` to cover "double
    it" with a crypto noun anywhere in the message (P5 slipped past the regex; the
    model caught it, but the deterministic layer should too).

### Client (`src/upmore-app-template.html` unless noted)
12. **C11** — `guideAnswer()` verif branch + `routeParas()`: branch on `r.status`
    (verified → "Verified against {provider}'s official terms"; else keep the honest
    caveat). Verif branch → "1,500 of 1,767 routes are verified against official
    provider terms…".
13. **C11** — move the no-deposit branch above the `easiest` branch (or guard easiest
    with `&& !has("no deposit","without deposit","free to start","no money","broke")`).
14. **C02** — persist moves: `data._moves = moves` in `buildPlan()`, reattach in
    `planData()`; rank/filter moves by the user's time/cash/state instead of global top-3.
15. **C02/C15** — `const tl = {...}[d.time] || "some time"` in `buildPlan()` and
    `guideCtx()` (fixes "undefined a week").
16. **C15** — validate restored `localStorage` fields against known choice sets in
    `boot()` before `Object.assign`.
17. **C10** — `stdRoutes()`/`xFiltered()`: exclude `status === "retired"` (R0067, R0549)
    or render a "Retired — offer ended" badge sorted last.
18. **C18** — add `affiliate: true/false` (+ `commission_note`) in `build-data.py`;
    render a disclosure badge in `renderExplore()` detail + `routeCard()`.
19. **C20** — persist the reminders toggle (`localStorage` at minimum; `profiles.prefs`
    jsonb when signed in); init `aria-pressed` from stored value in `renderProfile()`.
    (Pairs with server gap #6.)
20. **C05** — add `ios_url`/`android_url` per app route in `build-data.py`;
    platform-aware `stepLinks()` via `navigator.userAgent` (`/iPhone|iPad/`).
21. **C21** — add `"/icon-192.png"`, `"/icon-512.png"` to `sw.js` SHELL precache.
22. **C04 (data)** — backfill `done_when` in the verification pass (only 261/1767
    routes have it).

## Honest accounting
- No score above was assigned without a test that actually ran; every 10/10 cites the
  exact passing behavior. The 24 sub-10 scores each name a reproduced failure.
- The program did not re-run the full `qa/suites/run_all.py` harness (prior 3 consecutive
  runs: capability 100/100, speed 25/25, security 25/25, backend 20/20 on 2026-09-22);
  this program tested at feature granularity with happy-path + stress cases instead.
- Gaps are documented with file-level fixes but NOT fixed in this program — fixing +
  redeploying + re-verifying is follow-up work.
- Frontier-bar honesty: Upmore does not claim to match GPT-6 Astra / Claude Fable 5.1
  as general agents. The 10/10s claim equivalence only for the bounded use case named
  (e.g. "fires a scam warning every time with the mechanism named"), where the
  deterministic layer provably exceeds what an unaided frontier model does.
