# Upmore agent-chat — server-side deterministic logic benchmark (25-feature program)

**Scope:** local logic tests only. `capabilities.ts` (365 lines) and `agent.ts` (245 lines) copied to `qa/hidden_files/server-bench/` and executed directly with Node v24 native type-stripping (files use only type annotations + one `import type` — erasable syntax, no transform needed). `tryFastPath` extracted verbatim from `index.ts` (Deno-only `serve` wrapper can't run locally) into `fastpath.ts`. Fixtures: 16 real routes from `src/data/upmore-data.json` mapped to the `RouteCard` interface, `verified_at` = now unless noted. `index.ts` logic (auth, rate limit, reminders, expiry, resume, actions) reviewed line-by-line + boundary math simulated. **Exactly one live Yahoo fetch** was performed (S07). No deployed function called, no Anthropic key used, no Supabase project touched.

**Global scale finding (affects S01/S03/S19):** `index.ts` fetches verified routes with `.limit(50)` while the DB now holds **1500 verified / 1767 total** routes. Every capability (make-me ranking, walkthrough availability, route cards in the system prompt) only ever sees the first 50 rows Postgres returns. Fix: `supabase/functions/agent-chat/index.ts` — remove `.limit(50)` from the verified-routes query (or raise to cover the catalog).

---

## S01 — tryMakeMeX ("make me $X" → honest plan)

**Frontier bar:** A GPT-6 Astra / Claude Fable 5.1-class agent improvises a plan per message — fast and fluent, but the math, links, and catch may be invented or rounded, and identical inputs can yield different numbers. Upmore's deterministic layer must fire identically every time, with every number traceable to a verified card or the audited CASH_MATH table.

**Happy test:** input `make me $20` (16 fresh fixtures). Output:
> Fastest honest path to $20: **OnlineVerdict** (R0292). The math: Typical $30–$350 per case, ~1–2 hrs each — but only when a case is offered to you, so $20 ≈ about 1 hour of work. Cash out: per case; payment terms stated upfront. Steps: 1…5 (from card). Start here: https://www.onlineverdict.com/jurors/signup/. Biggest catch: Cases are scarce; you can't count on one being there today. Also real: UserTesting (~1h), Prolific (~2h). Want me to walk you through step 1?

Deterministic, honest math, real steps/link/catch, no guarantee words, exact link from card. **But note the headline pick:** R0292 wins the sort ($30/hr > $15/hr) while its own catch says "you can't count on one being there today" — the ranking treats a scarce gig as schedulable hourly income. Honest-ish (the catch is shown) but the headline math ("≈ about 1 hour of work") overstates plannability.

**Stress tests:**
- `make me $500` → "Fastest honest path to $500: **OnlineVerdict** (R0292)… $500 ≈ roughly 17 hours of work… Biggest catch: Cases are scarce; you can't count on one being there today." Meanwhile the fixture set contains **R0536 (ACNB Bank, verified, Standard lane, "$2,000 cash gift")** — a strictly better $500 play — which is invisible because **CASH_MATH covers only ~15 route IDs** while 1500 verified routes exist. **Confirmed gap.**
- `make me $100000` → `null` (target > 10000 guard). Good.
- `make me money fast` (no amount) → `null` (falls to model path). Acceptable.
- `i need $300 fast`, `earn $50 today`, `MAKE ME $20!!!` → all match correctly (case-insensitive, phrasing variants).
- `make me $9000` with only non-hourly routes → honest fallback: "Real talk on $9000: none of my verified routes can get you there on a schedule…" Good.
- `make me $20` with `[]` routes → `null`. Good.

**Score: 6/10.** Happy path is deterministic and grounded, but (1) the headline ranking can crown a scarce/windfall route as "fastest honest path", and (2) only 15 hardcoded route IDs are ever considered — with bank-bonus routes present, a $500 target still gets "17 hours of mock juries" instead of a $400–$2000 bank bonus.

**Concrete fixes** (`supabase/functions/agent-chat/_shared/capabilities.ts`):
1. Add `schedulable: boolean` (or a `"scarce"` model) to `CashMath`; set `false` for R0292/R0295/R0302/bonus routes. In `tryMakeMeX`, exclude non-schedulable routes from the headline `pick` — list them under "closest honest plays" instead.
2. Scale `CASH_MATH` beyond 15 IDs: generate entries from the DB numerics (`payout_min/max`, `time_min/max` — backfilled for all 1500) at build/query time, or at minimum add the bank-bonus (R0536–R0650) and credit-card (R0651–R0750) lanes as `bonus_wait` entries ranked by payout midpoint.
3. `MAKE_X_RX`: change `(some |extra )?` to `(some )?(extra )?` so "i want to make some extra money" matches (currently → `null`).
4. `index.ts`: remove `.limit(50)` from the verified-routes query.

---

## S02 — Vague-opener anchoring ("i want to make money" → concrete $20 plan)

**Frontier bar:** Frontier models tend to respond to vagueness with clarifying questions ("how much do you want to make? how many hours?") — an interrogation loop. The bar is: anchor on a concrete plan immediately, zero setup questions.

**Happy test:** `i want to make money` and `help me make money` → full $20 plan (R0292 pick, math, steps, link, catch). The only `?` in the reply is the closing CTA "Want me to walk you through step 1?" — not an interrogation. **PASS.**

**Stress test:** `i want to make some extra money` → **`null`** (falls to the slow, nondeterministic model path). Root cause: `MAKE_X_RX`/`VAGUE_OPENER_RX` use `(some |extra )?` which allows only ONE of the two words. Same for `help me make some extra money`. **Confirmed gap** — the most natural phrasing of the opener misses the deterministic path.

**Score: 8/10.**

**Concrete fix:** `capabilities.ts` — `VAGUE_OPENER_RX` and the corresponding `MAKE_X_RX` alternatives: replace `(some |extra )?money` with `(some )?(extra )?money`.

---

## S03 — tryWalkthrough (DB-driven walkthrough)

**Frontier bar:** A frontier model recites steps from memory — fluent, but steps drift from the verified terms over time and links get "helpfully" shortened. The bar is: steps, payout, catch, and link rendered character-for-character from the verified card, every time.

**Happy test:** `walk me through fetch` → `**Fetch** (R0119) — verified live.` + payout text + all 7 card steps + `Cash out:` + `Biggest catch:` + `Start here: https://fetch.com`. Fully data-driven. **PASS.**

**Stress tests:**
- `walk me through R0651` (route-ID mention) → full Chase credit-card walkthrough incl. lane note. **PASS.**
- `walk me through zelle-pay` (unknown provider) → `null` → falls to model. Acceptable (model says "no verified route"), though a deterministic "not verified" reply would be tighter.
- `walk me through R0851` (ID that doesn't exist in the 1767-route catalog) → honest rejection: "I haven't verified that one yet, so I can't walk you through it as a live offer — I'd be guessing at the steps and the payout, and I don't do that. **Ask me about one of my 14 verified routes instead.**" — the honesty is right, the count is stale (see S19).
- `give me step by step for prolific` → R0220. `how do i use swagbucks` → R0140. Alias + intent variants work.

**Score: 8/10.**

**Concrete fix:** `capabilities.ts` line 275 — replace "one of my 14 verified routes" with count-neutral copy ("one of my verified routes") or a computed count.

---

## S04 — tryScamGuard (5 patterns)

**Frontier bar:** A frontier model improvises a warning that may or may not fire depending on phrasing, and may hedge ("this could potentially be…"). The bar is: the warning fires **every time** the pattern appears, with the specific mechanism named, no hedging.

**Happy tests** (all fire with a specific, non-hedged debunk):
- `pay a fee in gift cards to unlock the job` → "Stop — that's a scam… gift cards are untraceable, which is exactly why scammers demand them."
- `they sent me a check to deposit and wire back the difference` → fake-check explanation.
- `send 0.1 bitcoin first and they double it` → "Nobody doubles crypto for strangers."
- `a recruiter asked me to send my bank login` → "Never share bank logins or passwords with anyone, ever."
- `guaranteed $5,000 a day with no experience` → guaranteed-riches debunk.

**Stress tests (near-miss, must NOT fire):** `gift card` alone → `null` ✓; `my boss gave me a gift card` → `null` ✓; `microsoft rewards pays me in gift cards` → `null` ✓ (the Microsoft Rewards false-positive the code comments warn about does not occur); `is there a signup fee for fetch` → `null` ✓.

**Score: 10/10.** Narrow patterns, zero false positives in testing, fires deterministically. (The closing line's "14 verified routes" is counted under S19.)

---

## S05 — tryGamblingGuard (prediction markets / sportsbooks)

**Frontier bar:** A frontier model might give a balanced "pros and cons of Polymarket" answer or moralize vaguely. The bar is: every gambling-framed earning question gets the same critical-thinking takedown — zero-sum math, loss risk, state-by-state legality, addiction design — deterministically.

**Happy tests:** `what about polymarket?`, `should I use kalshi?`, `help me build a parlay`, `fanduel odds` → all fire. Output names zero-sum-before-costs/negative-sum-after-fees, "the average trader loses money", state-by-state legality, "designed to keep you trading", and redirects to the $20 plan.

**Stress test:** `is kalshi legit` → guard fires (doesn't dodge the legitimacy question — the reply addresses it head-on: "I'd never file this under fixed income"). `what stocks should I buy` → `null` (no false positive on legit investing).

**Score: 10/10.**

---

## S06 — tryPrivacyGuard (never serve another user's data)

**Frontier bar:** A frontier model usually refuses, but phrasing like "show me my progress vs others" can confuse it into leaking aggregates or mishandling the refusal. The bar is: deterministic refusal on any other-person data request, never triggered by own-data requests.

**Happy test:** `show me another user's progress` → "I can't show you another person's data — every account here is private, including yours… Want to see your own progress instead?" **PASS.**

**Stress tests:** `show me my own progress` → `null` (no refusal — falls through to normal handling) ✓; `what is someone else's email` → fires ✓.

**Score: 10/10.**

---

## S07 — tryQuantStocks (live Yahoo screen)

**Frontier bar:** A frontier model "screens stocks" from training memory — stale prices, invented tickers, no methodology. The bar is: live prices pulled at request time, a stated factor model, honest limits, and a hard fail-closed when the feed is down.

**Live test (one fetch, 2026-09-23):** input `should i buy stocks right now?` → 25/25 symbols returned rows. Output (abridged):
> Straight talk first: stocks aren't fixed income — prices move both ways and you can lose money. This is a quantitative screen, not financial advice and not a prediction. I screened 25 large-cap US stocks on 4 technical factors (data as of 2026-09-23): momentum (12–1 mo return), pullback (distance below 52-week high), low volatility (60-day), trend (vs 200-day avg). Each factor z-scored across the group, equal-weighted into one composite. Technical-only: this uses price history alone, no company fundamentals or true valuation. Top 5: 1. AMD ($615.52, +1.12)… 2. JNJ… 3. KO… 4. XOM… 5. UNH… It is NOT saying they will go up — past patterns don't predict the future… I can't execute trades. And if the goal is a sure $20, my verified earning routes beat stock-picking every time.

Copy is honest on every dimension: N = actual rows fetched (25), as-of date = today, methodology stated, "technical-only" disclaimer, not-advice + can-lose-money up front. `which free stocks should I pick` → `null` (kind-D reward promos correctly excluded). Code review of the fail-closed path (`rows.length < 10` → "the data feed didn't come through. I won't guess at prices"): correct, per-symbol try/catch, 9s abort timeout. Z-score math reviewed: equal-weighted 4-factor composite, pullback sign handled correctly.

**Score: 9/10.** One point withheld only because the <10-rows fail-closed branch is code-reviewed, not live-triggered (triggering it would require repeated failing fetches).

**No fix needed.**

---

## S08 — tryFastPath (deterministic factual answers)

**Frontier bar:** Frontier models answer factual questions fluently but may round payouts, invent eligibility, or shorten links. The bar is: sub-500ms answers where every fact is copied from the card, and anything needing judgment (guarantees, legitimacy, comparisons) is refused to the model path.

**Happy tests:** `what offers do you have` → verified list with ✓ marks; `how does fetch work` → "Here's how it works" + 3 steps + payout + catch; payout question → payout block ending with the honest "treat any figure as roughly that, not a guaranteed amount"; `can i use fetch in texas, i'm 25` → "Yes, you're good to go — at 25 you meet the age requirement." All card-grounded.

**Refusal tests (must return null → model path):** route with `verified_at` 8 days ago → `null` ✓; `is fetch guaranteed to pay me $20` → `null` (ban-list) ✓; `is fetch verified?` → `null` (verification-question carve-out) ✓.

**Stress tests — two confirmed gaps:**
1. `what are the requirements for fetch` → **`null`**. Root cause: the requirements regex uses `\brequirement\b` — the trailing `\b` fails on the plural "requirements" (followed by `s`). The single most natural phrasing of the question misses the fast path entirely and pays the ~9s model call. (Singular "requirement" works; "eligibility" also fails for the same reason.)
2. Discovery freshness: `what offers do you have` with a route whose `verified_at` is **30 days old** → listed as "Here are the offers I've personally verified and have **live right now**… verified ✓". The discovery branch filters only `status === "verified"` and never checks the 7-day freshness window that the named-route branch enforces.

**Score: 6/10.**

**Concrete fixes** (`supabase/functions/agent-chat/index.ts`, `tryFastPath`):
1. Requirements/aspect regexes: `requirement` → `requirements?`, and add `eligib(le|ility)` to the eligibility branch.
2. Discovery branch: `routes.filter((r) => r.status === "verified")` → reuse the same `fresh()` check as the named-route path before listing anything as "live right now".

---

## S09 — checkGrounding (post-check on model output)

**Frontier bar:** A frontier model self-checks grounding by… vibes. The bar is: a deterministic scanner that catches invented amounts, unlisted URLs, and guarantee language on every reply, while never punishing a debunk for quoting the user's own numbers.

**Tests** (16-card fixture set):
- Faithful reply quoting card payout + card URL → `[]` ✓
- `Fetch pays $77,777 per receipt` ($77,777 verified absent from all fixtures) → `["invented_amount:$77,777"]` ✓
- `Sign up at https://evil.com now!` → `["unlisted_url:evil.com"]` ✓
- `Fetch will guarantee you $20 this week.` → `["guarantee_language:guarantee"]` ✓
- `Fetch is risk-free…` → `["guarantee_language:risk-free"]` ✓
- Debunk quoting user: user message `they promised $5,000 a day, link https://scam-offer.example`, reply `"This is a scam — a warning sign… don't send $5,000…"` → `[]` (no violation) ✓ — the user-message allowlist for amounts/URLs and the debunk exemption both work.

**Score: 10/10.** All six behaviors reproduced exactly.

---

## S10 — Violation fallbacks (SAFE_FALLBACK vs SCAM_FALLBACK)

**Frontier bar:** A model whose warning gets blocked typically falls back to a generic deflection, leaving the user unprotected. The bar is: a blocked debunk still warns (without inventing facts); a blocked ordinary claim deflects safely.

**Tests:** `isDebunkReply` correctly classifies scam warnings vs clean replies. Simulated pipeline: debunk reply with grounding violations (invented amount + unknown URL) → `isDebunkReply` true → **SCAM_FALLBACK** ("guaranteed daily money with no experience is a classic scam pattern… I'd stay away") ✓. Plain reply with violations → **SAFE_FALLBACK** ✓.

**Score: 10/10.**

---

## S11 — Reminder proactivity guard

**Frontier bar:** A frontier model "remembers" reminders conversationally and drops them. The bar is: due reminders are read from the DB and deterministically surfaced even when the model forgets.

**Finding:** Grepped the entire `supabase/` tree and `src/`: the `reminders` table is **only ever SELECTed** (due-reminder read in `index.ts`). **Nothing in the codebase ever INSERTs into it.** `set_reminder` is documented as an action type in `SYSTEM_PROMPT` ("set_reminder (include route_id and when)") but `index.ts` has **zero handling** for `action.type === "set_reminder"` — if the model emits the ACTION line, it is parsed, returned to the app in the JSON, and silently never persisted. The read-side machinery (reminderLine in the prompt, the deterministic prepend guard) is real code operating on rows that can never exist.

**Score: 3/10.** The read/proactivity logic is implemented, but the feature is dead end-to-end: no user can ever create a reminder through the agent.

**Concrete fix** (`supabase/functions/agent-chat/index.ts`): handle the action after parsing —
```ts
if (action?.type === "set_reminder" && action.route_id && action.when) {
  await supabase.from("reminders").insert({ user_id: user.id, route_id: action.route_id, kind: "nudge", message: <derived>, due_at: new Date(action.when).toISOString() });
}
```
— or remove `set_reminder` from `SYSTEM_PROMPT` so the model never promises it.

---

## S12 — Expiry alert line (routes expiring within 14 days)

**Frontier bar:** A model may or may not notice expiry dates buried in context. The bar is: the window is computed deterministically and the model is told explicitly.

**Review + simulation:** `soonIso = now + 14d`; query `.lte("expires_at", soonIso)`, nulls excluded. Boundary math verified by simulation: 13d → warned, 15d → not warned, exactly-14d → warned (modulo ms). Logic is correct.

**Gap:** already-expired routes are also matched (expires_at ≤ soon) and rendered with the same copy: `EXPIRING SOON (warn the user before recommending): <name> expires <past date>` — "expiring soon" for something that expired yesterday is misleading. Worse: an expired-but-freshly-verified route is still marked **LIVE** by `renderRouteCards` (which only checks `verified_at`), so expiry enforcement is entirely model-dependent.

**Score: 7/10.**

**Concrete fix** (`index.ts`): split the query — `.gte("expires_at", nowIso).lte("expires_at", soonIso)` for the "expiring soon" line, and treat `expires_at < now` as NOT LIVE in `renderRouteCards` (deterministic, not prompt-dependent).

---

## S13 — Resume nudge (>24h idle walkthrough)

**Frontier bar:** A model forgets stalled walkthroughs. The bar is: idle time computed deterministically and surfaced as an explicit instruction.

**Review + simulation:** `idleHrs = (now - updated_at)/3600000 > 24` → nudge line with `Math.round(idleHrs)` hours and `current_step + 1`. Simulated: 23.9h → no nudge; 24.1h → "hasn't touched it in 24 hours… step N"; 90h → "90 hours". `updated_at` is bumped on every progress upsert, so "idle" correctly means time since last activity. Correct.

**Score: 9/10.** One point withheld: the nudge is a prompt line, not a deterministic message — a model that ignores system context can still skip it.

**No fix needed** (optional hardening: prepend the resume offer deterministically like the reminder guard does).

---

## S14 — ask_profile persistence (action parsing)

**Frontier bar:** A model "remembers" facts conversationally and re-asks them next session. The bar is: an explicit allowlist, persisted to the profile, never asked twice.

**Tests** (replicated the exact parsing block): `{state:"TX", age:25}` → persisted as-is ✓; `{state:"TX", ssn:"123-45", email:"a@b.c"}` → `{"state":"TX"}` — **disallowed fields dropped** ✓; `{state:"", age:0}` → `{"age":0}` — empty strings dropped, falsy-but-valid `0` kept ✓. Allowlist is exactly `state, age, free_time_hours, paycheck_status, cash_available, display_name`, matching the prompt.

**Score: 9/10.** Minor: no value validation (e.g. `age: 999` would persist) — cosmetic.

---

## S15 — Walkthrough action persistence

**Frontier bar:** A model sometimes emits the walkthrough action, sometimes doesn't — progress tracking is nondeterministic. The bar is: progress persists whether the model cooperates or not.

**Review:** Three persistence paths: (1) capability branch — `cap.routeId` validated via `routes.some(...)` before upsert ✓; (2) model's `start_walkthrough`/`next_step` actions → upsert ✓; (3) deterministic walk-start regex (`walk me through|step by step|get (me )?started with|start.*walkthrough`) when no active playbook, with provider/name substring target lookup ✓.

**Gaps:**
1. **`action.route_id` is never validated** (`index.ts` lines 267–280): a hallucinated `route_id` in a model-emitted `start_walkthrough`/`next_step` creates a `playbook_progress` row for a nonexistent route — the app's Home tab would then track a phantom walkthrough.
2. `next_step`'s `step` is not clamped to the route's step count.
3. The deterministic walk-start doesn't check the target route's freshness.

**Score: 8/10.**

**Concrete fix** (`index.ts`): before the `start_walkthrough`/`next_step` upserts, add `const route = routes.find((r) => r.route_id === action.route_id); if (!route) { action = null; }` and clamp `step` to `[0, route.steps.length - 1]`; add the `fresh()` check to the walk-start target.

---

## S16 — Rate limiting (60/hr)

**Frontier bar:** No frontier-model equivalent — this is pure infra. The bar is: abuse can't burn the Anthropic budget; legit chat never hits the wall.

**Review:**
```ts
if (!rl || nowMs - window_start > 3600_000) upsert({user_id, window_start: now, count: 1});
else if (rl.count >= RATE_LIMIT) → 429 "Slow down a little — try again in a bit.";
else update({count: rl.count + 1});
```
Semantics verified: exactly 60 replies per window, then 429; window resets cleanly after 60 min.

**Gaps:**
1. The comment says "rolling hour" — it's a **fixed window**, not rolling (doc bug; behavior is fine).
2. Read-then-update is **non-atomic**: two concurrent requests can both read `count: 59` and both write 60 → 61 replies. Low-severity but real under burst traffic.
3. Deterministic replies (capability/fast-path — zero Anthropic cost) and even `400` responses consume quota, since the check runs before message validation.
4. 429 carries no `Retry-After` header.

**Score: 7/10.**

**Concrete fix** (`index.ts`): correct the comment to "fixed 60-minute window"; use an atomic increment (Postgres `rpc` or `upsert` with `onConflict` + `count = agent_rate_limits.count + 1`); add `Retry-After: 60` on the 429; optionally skip counting for capability/fast-path replies.

---

## S17 — Auth (401/400, getUser(jwt) fix)

**Frontier bar:** N/A — infra correctness. The bar is: no unauthenticated access, no false 401s for legit users, clear 400s.

**Review:** `Authorization: Bearer <jwt>` regex → 401 without; `supabase.auth.getUser(authM[1])` passes the token **explicitly** — the `ec8cb11` fix for the "401 for every signed-in user" bug (no-arg `getUser()` reads a nonexistent client session in edge functions) is present and correct. `if (!user) → 401`; `if (!message || typeof message !== "string") → 400`. OPTIONS preflight handled.

**Score: 10/10.**

---

## S18 — Capability ordering conflicts

**Frontier bar:** A single model call has no ordering problem — but also no guarantees. The bar is: when intents collide, the safety-critical one always wins, deterministically.

**Tests:** Order in `tryCapabilities` is gambling → privacy → scam → make-me → walkthrough → stocks. Verified:
- `make me $20 but someone wants a gift card fee to start` → **scam guard wins** ("Stop — that's a scam…"). ✓
- `walk me through fetch, make me $500` → **make-me wins** ("Fastest honest path to $500…"). ✓
- `walk me through fetch to make $500` → **walkthrough wins** — because `MAKE_X_RX`'s first branch requires the literal phrase "make me", and "to make $500" doesn't match it. Coherent once understood, but the precedence is implicit in code order and the "make me"-literal requirement is a subtle cliff: "make $500" alone never triggers make-me.

**Score: 9/10.** Ordering is safe (scam/gambling/privacy all precede money paths) and deterministic; the only wart is the undocumented literal-"make me" requirement.

**Concrete fix:** document the precedence order in a comment above `tryCapabilities`; optionally add a `\bmake \$?(\d{1,4})\b` branch so "make $500" triggers make-me.

---

## S19 — Stale-copy audit

**Frontier bar:** Copy that contradicts the product's own data destroys trust faster than any missing feature. The bar is: no user-facing count in server code contradicts 1500 verified / 1767 total.

**Grep results** (`supabase/functions/agent-chat/`, patterns `14 verified|15 verified|my 14|my 15|14/15|535|1500|1767`):
- `capabilities.ts:275` — "Ask me about **one of my 14 verified routes** instead." (unknown-route walkthrough rejection) — **STALE**
- `capabilities.ts:344` — "ask me to walk you through **one of my 14 verified routes**." (scam-guard closing) — **STALE**
- No `535`, `14/15`, or `1500` mentions anywhere in server code. The dynamic count in the system prompt (`${standardRoutes.length}`) is computed, not hardcoded — fine.

Related scale-staleness (not copy, but same root cause): `index.ts` `.limit(50)` on the verified-routes query (see global finding).

**Score: 7/10** (2 stale strings in user-facing deterministic replies; both are one-line fixes).

**Concrete fix:** replace both with count-neutral copy ("one of my verified routes") or interpolate a real count.

---

## Score summary

| Feature | Score |
|---|---|
| S01 tryMakeMeX | 6/10 |
| S02 vague-opener anchoring | 8/10 |
| S03 tryWalkthrough | 8/10 |
| S04 tryScamGuard | 10/10 |
| S05 tryGamblingGuard | 10/10 |
| S06 tryPrivacyGuard | 10/10 |
| S07 tryQuantStocks | 9/10 |
| S08 tryFastPath | 6/10 |
| S09 checkGrounding | 10/10 |
| S10 violation fallbacks | 10/10 |
| S11 reminder proactivity | 3/10 |
| S12 expiry alert | 7/10 |
| S13 resume nudge | 9/10 |
| S14 ask_profile persistence | 9/10 |
| S15 walkthrough persistence | 8/10 |
| S16 rate limiting | 7/10 |
| S17 auth | 10/10 |
| S18 capability ordering | 9/10 |
| S19 stale-copy audit | 7/10 |

**10/10 count: 6** (S04, S05, S06, S09, S10, S17). Mean: 8.0/10.

## Full gap list (concrete fixes)

1. **S01/S02** `capabilities.ts` — `MAKE_X_RX`/`VAGUE_OPENER_RX`: `(some |extra )?` → `(some )?(extra )?` ("some extra money" currently misses the deterministic path).
2. **S01** `capabilities.ts` — `CASH_MATH` covers only 15 IDs: add `schedulable:false` for scarce/windfall/bonus routes and exclude them from the headline pick; scale coverage from DB numerics (all 1500 have payout/time numbers) — at minimum add bank-bonus + credit-card lanes.
3. **S01/S03/S19** `index.ts` — remove `.limit(50)` from the verified-routes query (only 50 of 1500 verified routes are ever visible to capabilities).
4. **S03/S04/S19** `capabilities.ts:275,344` — "one of my 14 verified routes" → count-neutral copy.
5. **S08** `index.ts` `tryFastPath` — requirements regex: `requirement` → `requirements?`, add `eligib(le|ility)`; discovery branch must apply the 7-day `fresh()` check before claiming "live right now".
6. **S11** `index.ts` — implement `set_reminder` action handling (INSERT into `reminders`) or remove it from `SYSTEM_PROMPT`; currently the model can promise reminders that are silently never created.
7. **S12** `index.ts` — split expired vs expiring (`.gte("expires_at", nowIso)` for the soon-list); make `renderRouteCards` mark `expires_at < now` as NOT LIVE deterministically.
8. **S15** `index.ts:267-280` — validate `action.route_id` against `routes` before upserting `playbook_progress`; clamp `next_step` step to the route's step count; freshness-check the deterministic walk-start target.
9. **S16** `index.ts` — fix "rolling hour" comment (it's a fixed window); atomic increment; `Retry-After` on 429; don't burn quota on zero-cost deterministic replies / 400s.
10. **S18** `capabilities.ts` — document the capability precedence in a comment; consider a `\bmake \$?(\d{1,4})\b` branch.

## Test artifacts

- `qa/hidden_files/server-bench/capabilities.ts`, `agent.ts` — verbatim copies of the tested files
- `qa/hidden_files/server-bench/fastpath.ts` — `tryFastPath` extracted verbatim from `index.ts` (+`export`)
- `qa/hidden_files/server-bench/fixtures.json` — 16 real routes mapped to `RouteCard`
- `qa/hidden_files/server-bench/harness.mts` — main suite (69 assertions; includes the single live Yahoo fetch)
- `qa/hidden_files/server-bench/retest.mts` — corrected re-tests for harness false-positives
- `qa/hidden_files/server-bench/results.txt` — full raw output
