# X1-v2: Cross-Spec Integration EXHAUSTIVE — 200 assertions

**Agent:** X1-v2 (Cross-Spec Integration EXHAUSTIVE)
**Date:** 2026-09-25 ~04:50 UTC (2026-09-24 23:50 CDT)
**Target:** https://upmore-srikanthvishnu90-sketchs-projects.vercel.app/
**Build under test:** production serves `sw.js` cache stamp `upmore-8b52c95` (commit `8b52c95`, HTTP 200 verified this run). Local HEAD is `b73da4f` ("Rebuild sw.js with cache stamp 8b52c95") with one uncommitted local-only change: working-tree `sw.js` re-stamped to `upmore-b73da4f` (not yet committed/pushed — does not affect production evidence; production still serves `8b52c95`, which contains all X1-F1/F7/F8 fixes).
**Method:** Static analysis of `src/upmore-app-template.html` (the single source of truth; `index.html` is generated), empirical Node.js checks against `src/data/upmore-data.json` (1990 catalog routes), and live production `sw.js`/HTTP probing. No live browser available to this agent; no DOM execution — pure functions replicated verbatim from cited template lines for the math checks.
**Overall verdict: FAIL** — F2 gate-user hardcodes survive (age 19 / IL / $5,000 / 60 min in both `buildQueue` and `xFiltered`); `isLive` flag is set but never consumed; Home connect card hardcodes `hasLiveBank = false` so it always prompts to connect even with live data; `connGmail`/`connPlaid` connect-sheet divs are empty placeholders with zero JS wiring; demo flashes before live data resolves (async race). F6/F7/queue-formula/tabs pass.

---

## F1 — Fabricated data (40 tests)

Source lines: `initLiveTrackData` at template L3430–L3465; call site L3140; `loadTrackData` L3422–L3425; `TransactionSource.demo()` L3627–L3730; `simplefin-proxy` at `supabase/functions/simplefin-proxy/index.ts`; connect card L3493–L3502; connect sheet L925–L931.

| # | Assertion | Result | Evidence |
|---|-----------|--------|----------|
| F1-01 | `initLiveTrackData()` function exists | PASS | Defined L3430 `async function initLiveTrackData()` |
| F1-02 | `initLiveTrackData` is called on app load | PASS | L3140 `try { initLiveTrackData(); } catch (e) {}` at top-level script flow after `initExplore()` |
| F1-03 | Call is guarded so failure can't break boot | PASS | Wrapped in try/catch at L3140 |
| F1-04 | Function body has its own try/catch | PASS | L3431 `try {` … L3462 `} catch (e) {` |
| F1-05 | Tries SimpleFIN proxy before settling on demo | PASS | Invokes `supa.functions.invoke("simplefin-proxy", …)` L3436; demo is only the lazy fallback in `loadTrackData` (L3423) |
| F1-06 | Proxy invocation passes empty body (no credentials client-side) | PASS | L3436–L3438 `body: {}`; auth via Supabase JWT session |
| F1-07 | Requires signed-in session before calling proxy | PASS | L3433–L3435: returns early if `!session \|\| !supa` or no Supabase session |
| F1-08 | Only replaces data when proxy returns non-empty accounts | PASS | L3440 `if (!live \|\| !live.accounts \|\| live.accounts.length === 0) return;` |
| F1-09 | `trackData.isLive` flag is set when live data loads | PASS | L3456 `isLive: true, // flag: this is real user data, not demo` |
| F1-10 | Live transactions are mapped to the app's tx schema | PASS | L3443–L3454: maps `id/posted_at/amount/merchant_raw/merchant_id/category/is_pending/is_transfer/provider_id` |
| F1-11 | Live mapping preserves pending flags | PASS | L3451 `is_pending: t.is_pending` |
| F1-12 | Live mapping detects transfers | PASS | L3452 `is_transfer: /transfer/i.test(t.merchant_raw \|\| "")` |
| F1-13 | UI re-renders when live data arrives | PASS | L3458–L3459 re-calls `renderTrackStrip()` if defined |
| F1-14 | `simplefin-proxy` Edge Function exists in repo | PASS | `supabase/functions/simplefin-proxy/index.ts` present |
| F1-15 | Proxy reads Access URL server-side from Vault | PASS | `getAccessUrl()` queries `vault_secrets` with service_role key; header comment: "The secret never reaches the client" |
| F1-16 | Proxy is read-only by design | PASS | Header comment L2–L3: "Server-side only… returns sanitized accounts/transactions" |
| F1-17 | Proxy documents ≤24 req/day rule | PASS | Header comment: "read-only, ≤24 req/day, ≤90 day windows" |
| F1-18 | Proxy documents ≤90-day windows | PASS | Same header comment |
| F1-19 | Proxy documents pending-excluded-from-totals rule | PASS | Same header comment |
| F1-20 | Proxy documents transfers-excluded-from-spending rule | PASS | Same header comment |
| F1-21 | Proxy documents refund netting | PASS | Same header comment ("refunds netted (client-side)") |
| F1-22 | Proxy documents delete-on-disconnect | PASS | Same header comment |
| F1-23 | Proxy returns 404 "SimpleFIN not connected" when no secret | PASS | `index.ts`: `status: 404, { error: "SimpleFIN not connected" }` |
| F1-24 | Demo tx ids are namespaced `demo-` | PASS | L3655 `id: "demo-" + (id++)`; recurring `demo-rec-`, pending `demo-pending-1`, transfer `demo-transfer-1`, refund `demo-refund-1`, pay `demo-pay-` |
| F1-25 | Demo account id is namespaced | PASS | L3728 `id: "demo-chk"` |
| F1-26 | Demo source is documented as temporary | PASS | L3626 "Demo source provides sample data until a live connection exists." |
| F1-27 | Demo fallback comment states it is a fallback, not the default | PASS | L3428 "The demo is a fallback, not the default." |
| F1-28 | Demo clearly marked **in code** | PASS | F1-24 through F1-27 |
| F1-29 | Demo clearly marked **in the user-visible UI** | FAIL | No "demo"/"sample" label rendered anywhere in Track UI; a signed-out user sees demo balances ($2,840.50 checking) presented as their money |
| F1-30 | Live data replaces demo without touching features | PASS | L3629 comment: "A live source (SimpleFIN proxy) replaces this without touching features." — assignment swaps the same `trackData` shape |
| F1-31 | `isLive` flag is consumed anywhere (UI or logic) | FAIL | `grep isLive` → exactly one hit: the assignment at L3456. Nothing reads it. Dead flag. |
| F1-32 | Home connect card hides when live bank connected | FAIL | L3495 `const hasLiveBank = false; // TODO: true when Plaid/SimpleFIN connected` — hardcoded; `$("connectCard").hidden = hasLiveBank` never hides |
| F1-33 | Connect card reflects actual connection state | FAIL | Follows from F1-31/F1-32: with live SimpleFIN data loaded, the card still says "Connect your bank" |
| F1-34 | `connPlaid` div is wired to a real Plaid flow | FAIL | `connPlaid` appears only at L930 (empty `<div id="connPlaid"></div>`); zero JS references |
| F1-35 | `connGmail` div is wired to a real Gmail flow | FAIL | `connGmail` appears only at L929; zero JS references |
| F1-36 | Connect sheet offers a working connection action | FAIL | Sheet body = two empty divs + fine print; no buttons, no Link, no OAuth |
| F1-37 | Home "Connect bank" button leads somewhere real | FAIL | L3498–L3501: opens Guide + unhides the empty connectSheet (F1-36) |
| F1-38 | bankSheet "Notify me" is an honest waitlist (not a fake connect) | PASS | L908–L919: labeled "Real bank connections are in private beta… Email for your invite… Notify me" — does not pretend to connect |
| F1-39 | No demo flash before live data resolves | FAIL | `initLiveTrackData` is async and un-awaited at L3140; first `renderTrackStrip` (on `show("home")`) runs against demo, then re-renders — demo balances flash first |
| F1-40 | Built `index.html` contains the F1 code (deployed build matches source) | PASS | `grep -c "initLiveTrackData\|isLive: true"` on `index.html` = 7 hits; production serves the `8b52c95` build containing commit `8b52c95` (X1-F1) |

**F1 score: 30/40 PASS.** Critical integration gaps: dead `isLive` flag, hardcoded `hasLiveBank=false`, empty connect-sheet divs, no user-visible demo label, demo flash on load.

---

## F2 — Gates: gateUser must NOT be hardcoded (30 tests)

Source: `buildQueue` gateUser L1806–L1816; `xFiltered` gateUser L3080–L3086; `routePassesGates` L3406–L3417; `routeGateInputs` L3360–L3403.

| # | Assertion | Result | Evidence |
|---|-----------|--------|----------|
| F2-01 | `buildQueue`: `age` comes from user profile/Track data | FAIL | L1809 `age: 19, // TODO: from user profile` — hardcoded |
| F2-02 | `buildQueue`: `state` comes from user onboarding | FAIL | L1810 `state: "IL", // TODO: from user onboarding` — hardcoded |
| F2-03 | `buildQueue`: `free_cash` derived from real Track balance/recurring | FAIL | L1811–L1813: `calcFreeCash(5000, [], "2099-01-01", 100)` when data exists else `5000` — both branches are the literal 5000; the `// TODO: use real balance/recurring` admits it |
| F2-04 | `buildQueue`: `free_minutes` comes from user-stated free time | FAIL | L1814 `free_minutes: 60, // TODO: from user-stated free time` — hardcoded |
| F2-05 | `buildQueue`: `accounts` reflects connected banks | PASS | L1815 `accounts: hasConnectedBank ? ["bank_account"] : []`, where `hasConnectedBank` = `trackData.accounts.length > 0` (L1806) — real Track data |
| F2-06 | `buildQueue`: reads Track data at all | PASS | L1806 `const trackData = loadTrackData()` before building gateUser |
| F2-07 | `buildQueue`: hardcodes are at least disclosed via TODO | PASS | L1808–L1810 comment block documents each TODO |
| F2-08 | `xFiltered`: `age` comes from user profile/Track data | FAIL | L3083 `age: 19` — hardcoded, no TODO |
| F2-09 | `xFiltered`: `state` comes from user onboarding | FAIL | L3083 `state: "IL"` — hardcoded, no TODO |
| F2-10 | `xFiltered`: `free_cash` derived from real Track data | FAIL | L3084 `free_cash: 5000` — hardcoded, no TODO |
| F2-11 | `xFiltered`: `free_minutes` comes from user-stated free time | FAIL | L3084 `free_minutes: 60` — hardcoded, no TODO |
| F2-12 | `xFiltered`: `accounts` reflects connected banks | PASS | L3085 `accounts: hasConnectedBank ? ["bank_account"] : []` from `loadTrackData()` (L3081) |
| F2-13 | `xFiltered` comment "same gateUser as buildQueue" is value-accurate | PASS | Values are effectively identical (19/IL/5000/60); both hardcoded the same way |
| F2-14 | Gates applied to Explore/Search, not just the queue | PASS | L3076–L3088: `xFiltered` filters by `routePassesGates(r, gateUser).pass` |
| F2-15 | Gates applied to the "Up next" queue | PASS | L1819 `.filter(r => routePassesGates(r, gateUser).pass)` |
| F2-16 | `routePassesGates` merges completed_routes from user progress | PASS | L3411 `completed_routes: user.completed_routes \|\| []` (Gate 8 cooldown) |
| F2-17 | `routePassesGates` default `free_cash` when unknown is documented | PASS | L3413 `free_cash: user.free_cash !== undefined ? user.free_cash : 10000, // default if unknown` |
| F2-18 | Default `free_cash` 10000 doesn't silently pass capital gates | NOTE | Documented default; callers always pass 5000 so the default never fires in practice — masking, not measuring |
| F2-19 | `calcFreeCash` in `buildQueue` receives the real balance | FAIL | First arg is the literal `5000` (L1812) |
| F2-20 | `calcFreeCash` in `buildQueue` receives real recurring charges | FAIL | Second arg is the literal `[]` (L1812) |
| F2-21 | `calcFreeCash` in `buildQueue` receives the real next-payday | FAIL | Third arg is the literal `"2099-01-01"` (L1812) |
| F2-22 | B5 distress check uses real free cash | FAIL | L1764 `calcFreeCash(5000, [], "2099-01-01", 100)` — same hardcoded triple; `isDistressed` can never be true from real data |
| F2-23 | Profile screen collects state but gates read it | FAIL | Profile renders `d.state` (L3148) from `planData()`; gateUser ignores `planData()` entirely |
| F2-24 | Onboarding "time" screen value feeds `free_minutes` | FAIL | Onboarding collects time (screen `id="time"`, L647); gateUser uses literal 60 |
| F2-25 | Gate 1 (age) input comes from the route, not the user | PASS | `routeGateInputs` parses `min_age` from `who_qualifies` (L3363–L3374) — route side is data-driven |
| F2-26 | Gate 9 (prerequisite) bank-account need is data-driven | PASS | L3390–L3391: `needsAccount` parsed from `requirements` text; matched against `user.accounts` |
| F2-27 | Gate 5/6 (capital) uses parsed upfront cost, not a constant | PASS | L3380–L3381: `upfront` parsed from `costs_and_unpaid_time`; `cannotLose` logic distinguishes mandatory vs optional |
| F2-28 | A user with a real connected bank passes Gate 9 bank-account routes | PASS | F2-05 + F2-26 chain: `accounts: ["bank_account"]` satisfies the prerequisite |
| F2-29 | A signed-out user with demo data gets `accounts: ["bank_account"]` | NOTE | Demo ships `accounts: [{id:"demo-chk"…}]` (L3728), so `hasConnectedBank` is TRUE on demo — gates treat demo as a connected bank. Demo/non-demo conflation (ties to F1-29). |
| F2-30 | Any gate input reads `trackData.isLive` | FAIL | Nothing reads `isLive` (F1-31); gates can't distinguish live from demo |

**F2 score: 11/30 PASS (2 NOTE).** The F2 requirement — "gateUser NOT hardcoded in buildQueue, uses Track data" — is **not met**: 4 of 5 fields are literals in both call sites; only `accounts` is data-driven. The earlier commit message claiming "Use real user data, not hardcoded values" (FIX E1) is overstated.

---

## F6 — Urgency: catalog has no deadline field (20 tests)

Source: `routeGateInputs` L3395; data file `src/data/upmore-data.json` (1990 routes); queue comment L1712.

Empirical check (Node, all 1990 routes): **0 routes contain a `deadline` key**; route key set has no deadline-like field (`deadline`, `due_date`, `expires`, `expiry` all absent).

| # | Assertion | Result | Evidence |
|---|-----------|--------|----------|
| F6-01 | Zero catalog routes carry a `deadline` field | PASS | Empirical: 0/1990 routes have the key |
| F6-02 | No `due_date`/`expires`/`expiry` field either | PASS | Empirical scan of full key set — absent |
| F6-03 | Code explicitly marks deadline undefined with a reason | PASS | L3395 `deadline: undefined, // no deadlines in catalog` |
| F6-04 | Limitation is documented at the gate-input layer | PASS | F6-03 — the single place deadlines would enter gates |
| F6-05 | Queue urgency does not pretend to use catalog deadlines | PASS | Earn-card urgency comes from `r.speed` (L1823: today→2, days→1.5, else 1), not from a deadline |
| F6-06 | `qUrgency(days)` only fires on real user-entered deadlines | PASS | Used for save_renewals/save_claims rows (L1933: `qUrgency(qDaysUntil(c.deadline))`) — user data, not catalog |
| F6-07 | Renewal/claim deadline engine reads user tables, not catalog | PASS | L1921–L1939: `save_renewals` + `save_claims` |
| F6-08 | Queue formula comment names `urgency(days_to_deadline)` honestly | PASS | L1712 comment; for catalog routes the input degrades to the speed-based proxy (F6-05), which is disclosed by the `why` strings ("pays fast" only when `speed==="today"`) |
| F6-09 | Deadline-driven cards (renewals/claims) carry `days` from real dates | PASS | L1932 `const days = Math.max(0, …(new Date(s.next_date)…))`; L1933 `qDaysUntil(c.deadline)` |
| F6-10 | No earn card fabricates a deadline to inflate urgency | PASS | Earn cards use only the 3-tier speed multiplier; no synthetic dates |
| F6-11 | `routeMeta`/card copy doesn't claim deadlines catalog lacks | PASS | Card sub-lines use payout/timing text from data fields |
| F6-12 | "Never miss a renewal, claim deadline, or return window" refers to user-entered items | PASS | L809 onboarding copy sits above the deadlineList (L830) fed by user rows |
| F6-13 | Empty deadline state is honest | PASS | L2053 "No deadlines tracked - add renewals and claims below." |
| F6-14 | Guide answers about deadlines cite the user's plan, not catalog | PASS | L2555 comment: Guide "knows your plan" — deadlines from user data |
| F6-15 | Urgency tiers for speed are fixed and auditable | PASS | L1823 single expression; no hidden weights |
| F6-16 | `qUrgency` day-buckets are monotonic | PASS | L1717–L1723: ≤1→5, ≤3→4, ≤7→3, ≤30→2, else 1 |
| F6-17 | Null/NaN days degrade to urgency 1, not 0 or crash | PASS | L1717 `if (days == null \|\| isNaN(days)) return 1;` |
| F6-18 | Overdue deadlines show "overdue" text, not negative urgency | PASS | L1729–L1732 `qDueText`; urgency capped at 5 for ≤1 day |
| F6-19 | Catalog `time_to_first` is display-only, not an urgency input | PASS | Used in card footers (L3118); never fed to `qScore` |
| F6-20 | F6 limitation is noted in exactly one canonical place | PASS | L3395 — single source; no contradictory deadline claims elsewhere in the earn pipeline |

**F6 score: 20/20 PASS.**

---

## F7 — Scoring: qDollars uses payout MIN (20 tests)

Source: L1749 `const qDollars = r => Number(r.payout_min ?? r.payout_max ?? 0) || 0;` + FIX comment L1747–L1748.

Empirical check (Node): 352 variable routes (`payout_min > 0`, `payout_max > payout_min`); tested first 20 — all rank by min. Exact "$50–$500" style route exists: **R2508** (`payout_min: 50`, `payout_max: 500`).

| # | Assertion | Result | Evidence |
|---|-----------|--------|----------|
| F7-01 | `qDollars` reads `payout_min` first | PASS | L1749 `r.payout_min ?? r.payout_max ?? 0` |
| F7-02 | `qDollars` never reads `payout_max` when min exists | PASS | `??` chain short-circuits on any non-nullish min (including 0 → falls to `\|\| 0` guard, still never max) |
| F7-03 | FIX comment documents the min-not-max rule | PASS | L1747–L1748: "Use payout MIN for ranking, not MAX… Conservative = honest." |
| F7-04…F7-13 | 10 variable routes rank by min, not max | PASS | Empirical: R8323 (1000 not 50000), R0633 (150 not 350), R0264 (4000 not 10000), R8329 (200 not 5000), R5538 (25 not 1000), R3365 (250 not 750), R5785 (50 not 5000), R1061 (30 not 3000), R0536 (1000 not 2000), R3782 (400 not 2500) |
| F7-14 | "$50–$500" route R2508 ranks by $50 | PASS | Empirical: `qDollars(R2508) === 50` |
| F7-15 | Fixed-payout routes unaffected (min==max) | PASS | 1040 fixed routes: `qDollars` returns the single value |
| F7-16 | Unknown-payout routes score 0 dollars, not NaN | PASS | 406 zero/unknown routes → `\|\| 0`; earn-card `why` falls back to "Payout varies - researched NN%" (L1826–L1827) |
| F7-17 | Zero-min routes don't crash ranking | PASS | `Number(0) ?? …` → `0 \|\| 0` → 0; `qScore` handles 0 dollars |
| F7-18 | Queue `dollars` for earn cards comes from `qDollars` | PASS | L1822 `const dollars = qDollars(r)` |
| F7-19 | Continue cards also use `qDollars` | PASS | L1868 `const dollars = qDollars(cont.r)` |
| F7-20 | Built `index.html` contains the min-based `qDollars` | PASS | `grep qDollars index.html` hits; production build is `8b52c95` which includes commit `0efbb3e` (X1-F7) |

**F7 score: 20/20 PASS.**

---

## F8 — Usage: usage_signal is a documented placeholder (20 tests)

Source: L1842–L1848 (FIX X1-F8); `wasteScore` L3190–L3192; cancel card comment L3291.

| # | Assertion | Result | Evidence |
|---|-----------|--------|----------|
| F8-01 | `usage_signal` is not invented from thin air | PASS | L1842–L1844: "Don't invent usage_signal. The spec says the app cannot know usage — it must ask." |
| F8-02 | Placeholder value is documented | PASS | L1843–L1844: "Use stored user input if available, else 0.5 as a neutral placeholder" |
| F8-03 | Placeholder is the neutral 0.5, not 0 (max waste) or 1 (no waste) | PASS | L1847 `const usageSignal = storedUsage !== null ? storedUsage : 0.5;` |
| F8-04 | TODO for the user-prompt UI exists | PASS | L1845 `TODO: Add "How much do you use this?" UI to cancel cards; store per-merchant.` |
| F8-05 | TODO for loading stored per-merchant usage exists | PASS | L1846 `const storedUsage = null; // TODO: load from user prefs per merchant_id` |
| F8-06 | `wasteScore` formula matches spec | PASS | L3192 `annualCost * (1 - usageSignal) * renewalUrgency * confidence` vs L3190 comment `waste_score = annual_cost × (1 - usage_signal) × renewal_urgency × confidence` |
| F8-07 | Cancel card never claims non-usage | PASS | L3291 "Cancel card: exactly seven elements. Never claim non-usage — ask." |
| F8-08 | Score threshold prevents trivial waste entering queue | PASS | L1849 `if (score < 30) return; // only material waste enters the queue` |
| F8-09 | Cancel card `why` shows the math | PASS | L1853 `why: \`$${annual}/yr × ${conf}% × ${urgency} / ${effort} min\`` |
| F8-10 | The promised in-card usage prompt actually exists | FAIL | The L1842 comment says "AND prompt the user on the card" — but no "How much do you use this?" UI exists anywhere (grep: zero hits). The TODO is the only trace. |
| F8-11 | `storedUsage` has a real prefs backing | FAIL | Hardcoded `null` (L1846); nothing ever writes per-merchant usage |
| F8-12 | Placeholder 0.5 is distinguishable from a real 0.5 answer | FAIL | No provenance flag; a future real "half the time" answer is indistinguishable from the placeholder |
| F8-13 | Waste ranking still functions with the placeholder | PASS | 0.5 is a valid input; ranking degrades gracefully to annual×0.5×urgency×confidence |
| F8-14 | Renewal urgency input is real (days to next billing) | PASS | L1837 `renewalUrgency(days)` from `s.next_date` — detected, not invented |
| F8-15 | Confidence input is real (detector confidence) | PASS | L1848 `s.confidence` from `detectRecurrence` |
| F8-16 | Annual cost input is real (detected amount × interval) | PASS | L1838 `s.amount * (monthly?12:yearly?1:52)` |
| F8-17 | `usage_signal` placeholder doesn't leak into other specs | PASS | `grep usage_signal` → only L1842 comment, L1847–L1848, L3190–L3192 — contained in cancel pipeline |
| F8-18 | No second invented usage signal elsewhere | PASS | Same grep: no other usage-signal variables |
| F8-19 | Distressed users skip cancel cards entirely (B5 interplay) | PASS | L1833 `if (!isDistressed)` guard around the cancel-card block |
| F8-20 | Built `index.html` contains the F8 fix | PASS | Production build `8b52c95` includes commit `0efbb3e` (X1-F8); FIX comment present in `index.html` |

**F8 score: 17/20 PASS.** The placeholder is honestly documented with TODOs, but the comment's "AND prompt the user on the card" is aspirational — no prompt UI and no prefs backing exist.

---

## Queue formula — score = dollars × confidence × urgency ÷ effort (30 tests)

Source: `qScore` L1715–L1717; scoring call sites L1955–L1956; earn-card inputs L1822–L1827.

`qScore(dollars, conf, urg, eff) = (Number(dollars) || 0) * conf * urg / Math.max(Number(eff) || 1, 1)` — exactly the spec formula with a divide-by-zero guard.

Empirical check (Node, verbatim function bodies from the template): 30 catalog cards scored; every card's `qScore` output equals the hand-computed `dollars × conf × urg / eff`; the sorted list is strictly non-increasing. Full table (sorted):

| # | Card | dollars (min) | conf | urg | eff | score |
|---|------|---------------|------|-----|-----|-------|
| Q-01 | R0780 | 16000 | 0.7 | 1 | 32.5 | 344.6154 ✓ |
| Q-02 | R3570 | 1000 | 0.7 | 1 | 10 | 70.0000 ✓ |
| Q-03 | R0751 | 1300 | 0.7 | 2 | 32.5 | 56.0000 ✓ |
| Q-04 | R0099 | 1000 | 0.7 | 1.5 | 30 | 35.0000 ✓ |
| Q-05 | R8323 | 1000 | 0.7 | 1.5 | 32.5 | 32.3077 ✓ |
| Q-06 | R3365 | 250 | 0.7 | 1.5 | 10 | 26.2500 ✓ |
| Q-07 | R0264 | 4000 | 0.7 | 1 | 120 | 23.3333 ✓ |
| Q-08 | R0115 | 1000 | 0.7 | 1 | 30 | 23.3333 ✓ |
| Q-09 | R0890 | 1000 | 0.7 | 1 | 32.5 | 21.5385 ✓ |
| Q-10 | R0495 | 1163 | 0.7 | 1 | 40 | 20.3525 ✓ |
| Q-11 | R4317 | 275 | 0.7 | 1 | 10 | 19.2500 ✓ |
| Q-12 | R0536 | 1000 | 0.7 | 1 | 45 | 15.5556 ✓ |
| Q-13 | R5595 | 1000 | 0.7 | 1 | 75 | 9.3333 ✓ |
| Q-14 | R0071 | 450 | 0.7 | 1 | 45 | 7.0000 ✓ |
| Q-15 | R0569 | 400 | 0.7 | 1 | 45 | 6.2222 ✓ |
| Q-16 | R3782 | 400 | 0.7 | 1 | 45 | 6.2222 ✓ |
| Q-17 | R0568 | 400 | 0.7 | 1 | 45 | 6.2222 ✓ |
| Q-18 | R0069 | 300 | 0.7 | 1 | 45 | 4.6667 ✓ |
| Q-19 | R8329 | 200 | 0.7 | 1.5 | 45 | 4.6667 ✓ |
| Q-20 | R7437 | 100 | 0.7 | 1.5 | 22.5 | 4.6667 ✓ |
| Q-21 | R2508 ($50–$500 → $50) | 50 | 0.7 | 1 | 10 | 3.5000 ✓ |
| Q-22 | R3939 | 50 | 0.7 | 1 | 10 | 3.5000 ✓ |
| Q-23 | R3950 | 50 | 0.7 | 1 | 10 | 3.5000 ✓ |
| Q-24 | R0633 | 150 | 0.7 | 1 | 45 | 2.3333 ✓ |
| Q-25 | R5538 | 25 | 0.7 | 1 | 10 | 1.7500 ✓ |
| Q-26 | R3949 | 25 | 0.7 | 1 | 10 | 1.7500 ✓ |
| Q-27 | R8320 | 50 | 0.7 | 1.5 | 32.5 | 1.6154 ✓ |
| Q-28 | R0031 | 100 | 0.7 | 1 | 45 | 1.5556 ✓ |
| Q-29 | R5785 / R1061 (bottom) | 50 / 30 | 0.7 | 1 | 45 | 0.7778 / 0.4667 ✓ |

Each ✓ = `|qScore(...) − dollars×conf×urg/eff| < 1e-9` (28 individual assertions Q-01–Q-28, Q-29 covers the final two cards).

| # | Assertion | Result | Evidence |
|---|-----------|--------|----------|
| Q-30 | Queue is sorted descending by score | PASS | L1955 `cards.forEach(c => { c.score = qScore(c.dollars, c.conf, c.urg, c.eff); });` L1956 `cards.sort((a, b) => b.score - a.score);` — empirical: 30/30 non-increasing (344.62 → 0.47) |

Additional structural checks folded into the 30: `qScore` guards `eff ≤ 0` via `Math.max(…|| 1, 1)`; `dollars` coerced via `(Number(dollars) || 0)` so null payouts can't NaN the sort; every card gets `.score` before sorting (no undefined scores); ties keep stable relative order. Notably R2508 ($50–$500, ranked by the $50 min per F7) lands at #21 — the min-based ranking composes correctly with the formula.

**Queue score: 30/30 PASS.**

---

## 3 tabs — exactly Home, Guide, You; no 4th tab (20 tests)

Source: `TABS` L1167–L1171; `renderNav` L1174–L1182; `show()` L1184–L1200; comment L3182.

| # | Assertion | Result | Evidence |
|---|-----------|--------|----------|
| T-01 | `TABS` array has exactly 3 entries | PASS | L1167–L1171: home, guide, profile |
| T-02 | Tab 1 is Home | PASS | L1168 `{ id: "home", label: "Home", … }` |
| T-03 | Tab 2 is Guide | PASS | L1169 `{ id: "guide", label: "Guide", … }` |
| T-04 | Tab 3 is You | PASS | L1170 `{ id: "profile", label: "You", … }` |
| T-05 | No 4th entry in TABS | PASS | Array closes at L1171 with 3 objects |
| T-06 | All tab bars render from the single TABS source | PASS | L1174–L1182 `renderNav()` maps TABS into every `nav[data-nav]` — "so tabs can never drift out of sync again" |
| T-07 | 7 `nav[data-nav]` slots all get the same 3 tabs | PASS | 7 `data-nav` occurrences; all populated by `renderNav()` |
| T-08 | No hardcoded extra tab button in HTML | PASS | No static `<button class="tab"` in markup; tabs are JS-rendered from TABS |
| T-09 | `show()` routes only home/guide/profile as tab screens | PASS | L1193–L1197 handle `home`, `guide`, `profile` (+ non-tab screens: splash, transactions, monthview) |
| T-10 | Track is explicitly not a tab | PASS | L3182 "Track is infrastructure, not a destination. No Track tab." |
| T-11 | Transactions screen is a drill-down, not a tab | PASS | `id="transactions"` screen exists (L852) but has no TABS entry; reached via `show("transactions")` |
| T-12 | Month view is a drill-down, not a tab | PASS | `id="monthview"` (L864), no TABS entry |
| T-13 | Legacy tab names redirect to Home, not a 4th tab | PASS | L1166 `LEGACY_TABS = { money: "home", save: "home", explore: "home" }` |
| T-14 | Hash routing only admits known screens | PASS | L3885–L3886: hash parsed, restricted to `["home","guide","profile"]`, else `"home"` |
| T-15 | Tab buttons carry `role="tab"` + `aria-selected` | PASS | L1179–L1180; L1192 updates `aria-selected` on switch |
| T-16 | Tapping a tab calls `show()` with its id | PASS | L1180 `b.onclick = () => show(b.dataset.tab)` |
| T-17 | No "Earn"/"Save"/"Track" tab labels anywhere | PASS | Labels in TABS are exactly Home/Guide/You; grep of rendered labels confirms |
| T-18 | Guide screen contains the connect sheet but no extra tab | PASS | `connectSheet` (L925) lives inside the Guide section; it's a sheet, not a nav destination |
| T-19 | Home screen hosts the 5 things without new tabs | PASS | Connect card + track strip + queue + deadlines + ledger all render inside `id="home"` (L753) |
| T-20 | Built `index.html` preserves the 3-tab structure | PASS | Same TABS block present in `index.html`; production build `8b52c95` |

**Tabs score: 20/20 PASS.**

---

## X — Cross-spec interaction extras (20 tests)

| # | Assertion | Result | Evidence |
|---|-----------|--------|----------|
| X-01 | Track demo accounts make Earn gates believe a bank is connected | FAIL | Demo ships `accounts:[{id:"demo-chk",…}]` (L3728) → `hasConnectedBank=true` (L1806) → `accounts:["bank_account"]` — Gate 9 passes on fabricated data (compounds F1-29 × F2-05) |
| X-02 | Live-data arrival re-runs anything gate-dependent | FAIL | L3458–L3459 re-renders only `renderTrackStrip`; the queue/gates are not rebuilt when live data lands |
| X-03 | Cancel waste scores use Track-detected recurrence (spec 02 × 04) | PASS | L1835 `detectRecurrence(transactions)` → `wasteScore` → queue card |
| X-04 | Cancel cards excluded for distressed users (spec 02 × 03) | PASS | L1833 `if (!isDistressed)` — but see F2-22: the distress signal itself is hardcoded |
| X-05 | Pending transactions excluded from Track-derived queue inputs | PASS | T6 fix cited at L3471–L3472; payday detection filters `!t.is_pending && !t.is_transfer` (L3473) |
| X-06 | Demo's synthetic pending/transfer/refund cases are namespaced | PASS | `demo-pending-1`, `demo-transfer-1`, `demo-refund-1` (L3701–L3716) |
| X-07 | Earn pre-flight and Capital wall read the same route object as cards | PASS | Cards carry `route: r` (L1825: "SPEC 01: full route for 8-element card") |
| X-08 | Budget safe-to-spend and queue hardship read the same free-cash path | NOTE | Both call `calcFreeCash` — but both pass hardcoded args (F2-22); shared stub, shared gap |
| X-09 | Guide "knows your plan" from user tables, not catalog | PASS | L2555–L2562 comment; deadline/ledger answers cite `save_*` rows |
| X-10 | No spec's UI claims another spec's data is live when it isn't | FAIL | Track strip shows demo balances as live (F1-29); gates treat demo as connected bank (X-01) |
| X-11 | Sign-out clears session-gated live path | PASS | `initLiveTrackData` early-returns without session (L3433–L3435); sign-out nulls `session` (L3159) |
| X-12 | Production serves the exact tested build | PASS | Live `sw.js` → `upmore-8b52c95`; HTTP 200 on `/` this run; `index.html` contains all cited fixes |
| X-13 | Local working tree matches production | NOTE | Uncommitted local change: working-tree `sw.js` re-stamped `upmore-b73da4f` (2-line diff, comment + const only). Production unaffected. Recommend commit or revert before next deploy to avoid stamp confusion. |
| X-14 | No raw SimpleFIN secret in client bundle | PASS | Client only calls `supa.functions.invoke("simplefin-proxy")`; Vault read is server-side |
| X-15 | `supabase/functions/simplefin-proxy` is the only SimpleFIN caller | PASS | Single `functions.invoke("simplefin-proxy")` call site (L3436) |
| X-16 | Demo transactions can't leak into SimpleFIN proxy responses | PASS | Proxy returns only Bridge data; demo lives purely client-side in `TransactionSource.demo()` |
| X-17 | Queue `why` strings expose inputs for every card type | PASS | Earn (L1824–L1827), cancel (L1853), duplicate/spike (L1883, L1891), deadline (L1936) all carry `why` |
| X-18 | All 4 specs render inside the 3-tab shell | PASS | Earn/Cancel/Budget cards → Home queue; Track strip → Home; Guide chat; You profile/ledger — no 4th tab (Tabs T-01–T-20) |
| X-19 | Service worker can't serve a stale pre-fix shell as "current" | PASS | Per-deploy cache stamp (`upmore-8b52c95`); `skipWaiting` on install |
| X-20 | The 25-agent round's identical-commit requirement is satisfiable now | NOTE | Production is provably on `8b52c95` (served `sw.js` verified this run). Any agent run from this point forward tests one identical commit — provided no new push lands mid-round. |

**X score: 13/20 PASS (3 NOTE, 4 FAIL).**

---

## Tally

| Section | Tests | Pass | Fail | Note |
|---------|-------|------|------|------|
| F1 Fabricated data | 40 | 30 | 10 | 0 |
| F2 Gates hardcoding | 30 | 11 | 17 | 2 |
| F6 Urgency/deadlines | 20 | 20 | 0 | 0 |
| F7 Scoring (payout min) | 20 | 20 | 0 | 0 |
| F8 Usage placeholder | 20 | 17 | 3 | 0 |
| Queue formula | 30 | 30 | 0 | 0 |
| 3 tabs | 20 | 20 | 0 | 0 |
| X integration extras | 20 | 13 | 4 | 3 |
| **Total** | **200** | **161** | **34** | **5** |

## Verdict: FAIL (34 failures) — do not mark X1-v2 passed

### Must-fix before the identical-commit rerun
1. **F2 gateUser hardcodes (F2-01–04, F2-08–11, F2-19–21):** `age: 19`, `state: "IL"`, `free_cash: 5000` (both ternary branches), `free_minutes: 60` in `buildQueue` (L1808–L1816) and `xFiltered` (L3082–L3086). Wire to `planData()`/profile/Track or gate honestly on "unknown". The FIX (E1) comment claiming "real user data" is overstated.
2. **Dead `isLive` flag (F1-31):** set at L3456, read nowhere. Either consume it (connect card, gates, demo label) or remove it.
3. **Connect card hardcoded (F1-32/33):** `const hasLiveBank = false` (L3495) — always prompts "Connect your bank" even with live SimpleFIN data. Should read `trackData.isLive`.
4. **Empty connect sheet (F1-34–37):** `connGmail`/`connPlaid` are unpopulated divs; "Connect bank" opens a dead sheet. Either implement the SimpleFIN/Plaid connect action or replace with the honest waitlist everywhere.
5. **No user-visible demo label (F1-29):** demo balances ($2,840.50 checking) present as the user's money when signed out. Add a "Sample data — connect your bank" marker.
6. **Demo ⇒ fake connected bank (X-01):** demo accounts make `hasConnectedBank` true, so Gate 9 passes on fabricated data. Demo accounts must not satisfy the bank-account prerequisite.
7. **Demo flash on load (F1-39):** async `initLiveTrackData` resolves after first render. Defer first Track render or render a loading state until the proxy resolves/fails.
8. **Usage prompt UI missing (F8-10/11):** the "AND prompt the user on the card" promise and per-merchant prefs backing don't exist — only TODOs.
9. **Hardcoded distress signal (F2-22):** B5 hardship path can never trigger from real data (`calcFreeCash(5000, [], "2099-01-01", 100)` is constant).
10. **Local sw.js drift (X-13):** commit or revert the working-tree `upmore-b73da4f` re-stamp before the next deploy.

### Clean passes (no action)
- F6 (20/20): catalog genuinely has no deadline field; limitation documented once at L3395; urgency degrades to the speed proxy honestly.
- F7 (20/20): `qDollars` uses `payout_min`; R2508 ($50–$500) ranks by $50; verified on 20 variable routes.
- Queue formula (30/30): `qScore` = dollars × conf × urg / eff on all 30 cards; sorted strictly descending.
- Tabs (20/20): exactly Home/Guide/You from the single TABS source; Track/transactions/monthview are drill-downs, not tabs.
- F1 proxy plumbing (F1-01–28, F1-30, F1-38, F1-40): init-on-load, JWT-gated proxy call, Vault-server-side secret, demo namespacing, honest waitlist copy — all present in the production `8b52c95` build.

*Report: `~/workspace/upmore/qa/spec-test/v2-x1-integration-exhaustive.md`*
