# Upmore client-side feature benchmark — 25 features, 10/10 program

**Scope:** client-side only (no live browser). **Method:** (a) static analysis of
`src/upmore-app-template.html`, (b) a node v24 vm harness that loads the template's real
app `<script>` with DOM stubs, injects the real `src/data/upmore-data.json` (1767 routes),
exports internals (`guideAnswer`, `xFiltered`, `buildPlan`, …) and runs 89 assertions,
(c) structural checks on the built `index.html`.
**Harness:** `qa/hidden_files/harness-client.cjs` — **89/89 assertions pass**.
**Build parity:** the built `index.html` app script is byte-identical to the template app
script except for build-app.py's known replacements (route counts 535→1767, CATICON
"Credit Card Bonus" addition) — all harness results transfer to production.

**Score rule used:** score /10 only on reproducible evidence actually run; frontier bar =
what a GPT-6 Astra / Claude Fable 5.1-class agent would produce for the bounded use case.

---

## C01 — Onboarding state machine — **9/10**

**Frontier bar:** adaptive multi-screen flow, inline validation with specific messages,
honest age-gate, no dead ends, progress preserved.

**Happy path (ran):** name "Ava" + DOB 01/01/1990 + state TX → `checkAbout()` enables
`aboutGo` (PASS). Splash auto-advance timer (1800 ms) → `welcome` (PASS, timer captured
and fired manually).

**Stress (ran):** Feb 30 DOB → "Check that date." + stays disabled (PASS); empty name
blocks (PASS); missing state blocks (PASS); future DOB 01/01/2099 rejected (PASS);
17-year-old DOB → `data.minor=true` → `aboutGo` routes to the `blocked` screen
("Upmore is for adults 18 and older… We didn't save anything you typed.") (PASS);
correcting to an adult DOB clears `minor` → `situation` (PASS); exactly-18-today
boundary → adult (PASS).

**Gap:** `sitGo` gating (`paycheck`+`cash` required before plan) verified statically
only — the stub DOM has no `[data-pick]` choice elements, so the click handler couldn't
be exercised dynamically. Minor: `back()` from `blocked` resolves to `splash`
(`order.indexOf("blocked")` is -1), but the blocked screen has no back button (only
Close→reload), so it's unreachable in practice.
**Fix:** none required for ship; for the dynamic test, render choice buttons in the
harness stub. Optional: add `"blocked"` handling in `back()`.

---

## C02 — Personalized "first 3 moves" plan — **6/10**

**Frontier bar:** moves actually derived from the user's inputs — ranked/filtered by
time available, cash, and state eligibility, with the reason tied to the user.

**Happy path (ran):** `buildPlan()` with `{name:Ava, state:TX, time:15, paycheck:no,
cash:0}` → title "Ava, here are your first 3 moves", "Picked for Texas · 15 minutes a
week", moves = top-3 Standard routes by earn ratio (R5446/R0328/R0018) (PASS).
`dbProfile` merge works (display_name/state/free_time_hours→minutes/paycheck/cash) (PASS).

**Stress (ran):** `dbProfile.free_time_hours = 0.5` → `planData().time === "30"` →
`buildPlan()` renders **"Picked for California · undefined a week"** (PASS =
bug reproduced). Same missing fallback in `guideCtx()` (Guide empty-state context
line); `renderProfile()` already has `|| "about an hour"`.

**Gaps:**
1. **Dead personalization hook (real):** `buildPlan()` does `const d = planData();
   d._moves = moves;` — but `planData()` returns a *fresh* object every call, so
   `_moves` is always `undefined` in `renderHome()` and in `guideAnswer()`'s "next
   move" branch (harness: `planData()._moves === undefined` after `buildPlan()`).
   The "Picked for {state}" copy implies per-user picking; moves are the global top-3
   for everyone, and a 15-min/week user gets a 90–240-min bug-bounty as Move 1.
2. **"undefined a week"** for any non-{15,60,180} time value (two spots).

**Fixes** (`src/upmore-app-template.html`): (1) persist on the module `data` object —
in `buildPlan()`: `data._moves = moves;` and in `planData()`: `if (data._moves)
base._moves = data._moves;` — plus actually filter/rank by fit: e.g.
`stdRoutes().filter(r => (r.time_max_minutes||1e9) <= +d.time*4 …).slice(0,3)` or at
minimum exclude routes whose minimum time exceeds the user's weekly time.
(2) `const tl = {...}[d.time] || "some time"` in `buildPlan()` and `guideCtx()`.

---

## C03 — Home hero walkthrough + progress bar — **10/10**

**Frontier bar:** hero reflects the live plan, exact progress, next-step surfacing,
CTA adapts to completion.

**Happy path (ran):** `renderHome()` → hero title "Microsoft — Lead Sourcing" (Move 1),
"0 of 4 steps", bar `0%` (PASS).

**Stress (ran):** `prog[R5446] = [n1, n2]` → bar exactly `50%`, "2 of 4 steps" (PASS);
all steps done → CTA becomes "Ask Guide what's next"; clicking it fires
`guideAsk("What's my next move after this one?")` → local "After this one: …" answer
end-to-end (PASS). Matches frontier.

---

## C04 — Walkthrough step rendering — **9/10**

**Frontier bar:** every step card shows done_when, warns, labeled per-step links
(first step links the official source), dedupe, advance/finish flows.

**Happy path (ran):** `startWalkthrough('R0119')` → "Step 1 of 7" card; per-step links
rendered with host labels + `target="_blank"` (PASS); `stepLinks` puts `route.url`
first on step 1 and dedupes URLs already in step text (PASS); `hostOf` strips `www.`
(PASS); Done marks step n, advances `walk.i` (PASS); finishing step 7 → `walk=null` +
"The payout: …" message (PASS).

**Stress (ran):** route with metadata — `startWalkthrough('R0157')` renders
"You're done when: App downloaded" and "Heads up:" warns (PASS).

**Gap:** only 261/1767 routes have any `done_when` — the renderer is correct; the gap
is data coverage (many walkthroughs show bare step text). **Fix (data):** backfill
`done_when` in the verification evidence pass (`qa/verification/`).

---

## C05 — App-store deep links for core routes — **6/10**

**Frontier bar:** platform-aware store links (iOS→App Store, Android→Play), verified live.

**Happy path (ran):** `stepLinks({text:'Tap install'}, R0208-route, isFirst=true)` →
`links[0] === "https://play.google.com/store/apps/details?id=surveytime.io.surveytime_app&hl=ln"`
(PASS).

**Stress (ran):** data-wide scan: exactly **3** routes carry `play.google.com` URLs
(R0208 SurveyTime, R0446 Google Opinion Rewards, R0510 Google Rewards TV); **zero**
`apps.apple.com` / `itunes.apple.com` URLs in all 1767 routes. Step text for Fetch
says "Apple App Store or Google Play Store" but only a Play link exists.

**Gap:** iPhone users get Android store links; FEATURED core-app cards open
walkthroughs, never a store page.
**Fix:** add `ios_url`/`android_url` per app route in `build-data.py`; in `stepLinks`,
prefer the platform match via `navigator.userAgent` (`/iPhone|iPad/`).

---

## C06 — Explore search — **10/10**

**Frontier bar:** instant, injection-safe (no regex eval, output-escaped), clear empty state.

**Happy path (ran):** `q='fetch'` → R0119 (PASS); `q='bug bounty'` matches reward text →
R5446 (PASS).

**Stress (ran):** `q='<script>alert(1)</script>'` → 0 results, no throw (PASS);
`q='.+*?^()|[]'` → 0 results, no throw — matching uses `String.includes`, not regex,
so no ReDoS class (PASS); `esc('<img src=x onerror=alert(1)>')` →
`&lt;img src=x onerror=alert(1)&gt;` (PASS); empty result → "0 ways to earn, highest
earn rate first…" + Show-more hidden (PASS). Matches frontier.

---

## C07 — Difficulty chips + category filters — **10/10**

**Frontier bar:** composable filters with accurate counts.

**Happy path (ran):** tier `Very Easy` → 496 routes, all `tier==="Very Easy"` (PASS);
category `Bank Bonus` → 327, all matching (PASS).

**Stress (ran):** tier `Easy` + category `Bank Bonus` → 267, every item satisfies both
(PASS); reset to `all`/`all` restores full list. Matches frontier.

---

## C08 — Higher-risk lane toggle — **10/10**

**Frontier bar:** risky content hidden by default, explicit opt-in with count, badged cards.

**Happy path (ran):** default `lane=false` → 1744/1744 Standard, zero Restricted (PASS);
toggle label `(23)` matches data (PASS).

**Stress (ran):** `lane=true` → 1767 total, exactly 23 Restricted (PASS); data cross-check:
23 Restricted, 8 verified — matches the Guide's "23 routes in the higher-risk lane"
copy. Matches frontier.

---

## C09 — Explore pagination — **10/10**

**Frontier bar:** accurate remaining counts, control hides at the end.

**Happy path (ran):** 1744 results, `shown=40` → "Show more (1704 left)", visible (PASS);
click → `shown=100` (PASS).

**Stress (ran):** `shown=5000` → button hidden (PASS). Matches frontier.

---

## C10 — Money/time/rate display + earn-ratio ordering — **8/10**

**Frontier bar:** amounts/time/rates computed from data, readable formatting, catalog
honestly ordered, dead offers excluded or badged.

**Happy path (ran):** `earnLine` fixtures — `{0–0, 30–30min, null}` →
"Varies · ≈30 min"; `{100–400, 30–60min, 5}` → "≈$100–$400 · ≈30–60 min · ≈5.00/min";
`{0–250000, 90–240min, 757.575}` → "≈758/min" (≥100 rounds); `{50, 5–15min, 55.55}` →
"≈55.5/min" (10–100 → 1dp) (all PASS). Explore's first card is R5446, the top
earn-ratio route (PASS).

**Stress (ran):** full-catalog ordering check — exactly **1 inversion**: retired route
R0067 (ratio 111.11) sits after a verified 0.0-ratio route at index 1499/1500.
`xFiltered()` includes **both retired routes (R0067, R0549) with no badge** — dead
offers rendered as earnable (PASS = gap reproduced).

**Gap:** retired offers shown as live.
**Fix:** `stdRoutes()`/`xFiltered()`: `D.routes.filter(r => r.lane === "Standard" &&
r.status !== "retired")` — or render a "Retired — offer ended" badge and sort them last.

---

## C11 — Guide local answers — **6/10**

**Frontier bar:** answers grounded in live catalog data, honest verification status,
correct counts, specific intents win over generic ones.

**Happy path (ran):** provider lookup ("tell me about fetch" → Fetch card) (PASS);
category top-3 ("show me bank bonuses") (PASS); catch → "23 routes in the higher-risk
lane" (PASS); payout, tax ("Usually, yes…"), no-deposit ("costs $0") (PASS);
easiest top-3; starter "What should I do first?" → easiest branch (PASS); next-move →
"After this one: …" (PASS); gibberish → fallback with catalog count (PASS —
"1767" in the built file via build-app.py replacement).

**Stress (ran):** two failures reproduced:
1. **STALE verification copy (confirmed suspect #1):** the verif branch still says
   "we have not verified live provider terms yet", and `routeParas()` appends "we
   haven't verified the live terms on this one yet" to **every** provider answer —
   including the 1500 verified routes (e.g. Fetch R0119, status=verified). False for
   85% of the catalog.
2. **Branch shadowing:** "free to start" contains "start", so the `easiest` branch
   (checked earlier) swallows it — returns "3 easiest routes" instead of the $0
   no-deposit answer. ("i have no money" alone works.)

**Fixes** (`guideAnswer`/`routeParas`): (1) branch on `r.status`:
verified → "Verified against {provider}'s official terms."; unverified → keep the
honest caveat. Verif branch → "1,500 of the 1,767 routes are verified against
official provider terms; the rest are researched but not yet verified — I'll confirm
before you start." (2) move the no-deposit branch above the `easiest` branch, or
guard the easiest branch with `&& !has("no deposit","without deposit","free to
start","no money","broke")`.

---

## C12 — Guide EXRULES excluded-topic handling — **10/10**

**Frontier bar:** hard refusals for disallowed topics with specific reasons, soft
redirects for adjacent-but-out-of-scope, robust to casing/phrasing.

**Happy path (ran):** "how do I do my homework without getting caught" → "We don't
touch that one." + expulsion-risk reason (PASS); "should i start a dropshipping
store" → soft "business model, not a quick earning route" framing (PASS).

**Stress (ran):** "is onlyfans a legit side hustle" → **hard rule fires before** the
"legit" verification branch → refusal + privacy/safety reason (PASS);
"HOW DO I DO MY HOMEWORK?" → case-insensitive match (PASS); "tutor my neighbor's
kid for cash" → soft tutor rule (PASS); all 21 EXRULES indexes valid against
`D.excluded` (PASS). Matches frontier.

---

## C13 — Guide empty state + starter prompts — **10/10**

**Frontier bar:** helpful empty state with contextual starters.

**Happy path (ran):** 4 starters with sublabels ("What should I do first?" /
"Show me bank bonuses" / "What's the catch with these offers?" / "How does Upmore
make money?") (PASS).

**Stress (ran):** empty state renders starters plus live plan context
("Your plan: Texas · direct deposit · about an hour a week") (PASS). (Harness stub
needed real-DOM `#empty` semantics — app logic itself is correct.) Matches frontier.

---

## C14 — Agent fallback chain — **10/10**

**Frontier bar:** tries the live agent, degrades gracefully to local answers, never
hangs or leaks raw errors.

**Happy path (ran):** `agentAsk` → `null` when unsigned in (no token → no fetch)
(PASS); → `null` on HTTP 500 (PASS); → `{reply, thread_id}` on 200 with thread
persistence (PASS).

**Stress (ran):** `guideAsk("what is the catch")` with backend 500 → local
higher-risk-lane answer rendered, `busy` reset (PASS); with `fetch` throwing
(network down) → `.catch` → local verification answer (PASS). Matches frontier.

---

## C15 — Session persistence across OAuth round-trip — **9/10**

**Frontier bar:** onboarding answers survive the Google redirect; corrupt stored data
never breaks boot.

**Happy path (ran):** `googleGo` click persists `data` to `localStorage`
("upmore-onboarding" → `{name:Zed, state:CA, …}`) before `signInWithOAuth` (PASS);
boot restores via `Object.assign(data, JSON.parse(saved))`.

**Stress (ran):** corrupted JSON in the key → `try/catch` swallows, `data` untouched,
no throw (PASS).

**Gap:** restore only runs in `boot()`; no re-validation that restored values are
still well-formed (e.g. a stale `time:"30"` flows into the C02 "undefined a week"
bug). **Fix:** validate restored fields against the known choice sets in `boot()`
before `Object.assign`.

---

## C16 — Playbook progress sync to DB — **10/10**

**Frontier bar:** correct status transitions, loads on sign-in, silent no-op when
signed out.

**Happy path (ran):** `syncProgress('R0119')` with 2/7 steps → upsert
`{user_id, route_id:'R0119', current_step:2, status:'in_progress'}` to
`playbook_progress` (PASS); 7/7 → `status:'done'` (PASS).

**Stress (ran):** signed out → zero writes (PASS); `loadProgress()` maps
`current_step:3` → step n's `[1,2,3]` (PASS); unknown `route_id` ignored (PASS).
Matches frontier.

---

## C17 — Profile page (You tab) + editable rows — **9/10**

**Frontier bar:** profile reflects the plan; rows editable in place.

**Happy path (ran):** `renderProfile()` with `{Ava, TX, 15min, no-DD, $0}` →
" Ava · Texas · 15 minutes a week · No direct deposit · $0 to park" across
`pName/pAva/pLine/pTime/pAbout/pSit` (PASS).

**Stress:** rows are `<button data-go="time|about|situation">` → editing means
re-running the onboarding screens, not inline edit; time choices fixed to
15/60/180. Works, below frontier inline editing.
**Fix:** inline steppers for time/cash on the profile rows (optional; current
pattern is acceptable).

---

## C18 — "How Upmore makes money" disclosure — **7/10**

**Frontier bar:** honest monetization copy *plus* per-offer labeling wherever a cut
is promised.

**Happy path (ran):** `guideAnswer("How does Upmore make money?")` → "Some offers pay
us a small cut… It never comes out of your pocket… We'd rather lose the cut than
push a worse offer on you." (PASS) — good copy.

**Stress (ran):** the answer promises "We'll **always tell you** when we're earning
from an offer" — but **no route in the 1767-card dataset has any affiliate/commission
field**, and neither `routeCard()` nor Explore's detail view renders any paid-placement
disclosure. The promise has no mechanism (PASS = gap reproduced).

**Fix:** add `affiliate: true/false` (+ optional `commission_note`) in `build-data.py`;
render a badge in `renderExplore()`'s `xdetail` and in `routeCard()`:
"Upmore may earn a commission — you still get the full reward."

---

## C19 — Sign out — **10/10**

**Frontier bar:** sign-out clears the session and returns to a logged-out state.

**Happy + stress (ran):** `signOut` click → `supa.auth.signOut()` → `SIGNED_OUT`
handler → `session=null`, `dbProfile=null`, `location.hash=""`, `location.reload()`
(PASS). Matches frontier.

---

## C20 — Reminders toggle UI — **3/10**

**Frontier bar:** toggles persist and do something.

**Happy path (ran):** clicking toggles `aria-pressed` true↔false (static code path;
handler is `document.querySelectorAll(".tgl:not(#laneTgl)")` → flip attribute).

**Stress (ran):** codebase search: **zero** writes to the `reminders` table, zero
`localStorage` keys, zero reads in `boot()`/`loadProfile()`/`renderProfile()` from
the client. The `reminders` table exists server-side (agent-chat reads due
reminders), but the client toggle is purely decorative — a user turning "Payout
reminders" off changes nothing.

**Fix:** persist on toggle — `localStorage.setItem("upmore-prefs", …)` at minimum;
when signed in, upsert to `profiles` (add `prefs jsonb`) or a `reminder_prefs` row;
initialize `aria-pressed` from the stored value in `renderProfile()`.

---

## C21 — PWA — **9/10**

**Frontier bar:** installable, offline shell, correct icons.

**Evidence (ran/static):** `manifest.webmanifest` valid — name "Upmore", short_name,
`icons` 192+512 (both files exist), `start_url:"."`, `display:"standalone"`,
`theme_color` (PASS); `<link rel="manifest">` + `apple-touch-icon` present in
`index.html` (PASS); `sw.js` precaches `/`, `/index.html`, `/manifest.webmanifest`,
runtime-caches same-origin GETs, skips `/rest/` + `/auth/`, registered on window load
(PASS); root `sw.js` published by build-app.py (PASS).

**Gap:** icons are runtime-cached only, not precached — first offline load misses them
(trivial). **Fix:** add `"/icon-192.png", "/icon-512.png"` to `sw.js` SHELL.

---

## C22 — Visual identity — **10/10**

**Frontier bar:** restrained palette, clear tab structure, no gamified "wins".

**Evidence:** exactly **4** distinct tabs (`home/explore/guide/profile`) on all 4
tabbed screens (16 buttons, 4 unique values) (PASS); zero occurrences of "wins"
word-boundary in the template (PASS); palette audit: greens (`#9BD6B6`, `#2F6E50`),
skies (`#A9D4EC`, `#6FB3D6`, `#e2f0f8`), whites/blacks dominate — the only
out-of-family colors are the Google "G" logo brand SVG (`#EA4335/#FBBC05/#4285F4/
#34A853`), form-error red (`#E4806B`), and warn amber (`#fff8e6/#6b5518`) — all
functional, not decorative. Matches frontier.

---

## Scoreboard

| # | Feature | Score |
|---|---------|-------|
| C01 | Onboarding state machine | 9 |
| C02 | Personalized first-3-moves plan | 6 |
| C03 | Home hero + progress bar | 10 |
| C04 | Walkthrough step rendering | 9 |
| C05 | App-store deep links | 6 |
| C06 | Explore search | 10 |
| C07 | Difficulty + category filters | 10 |
| C08 | Higher-risk lane toggle | 10 |
| C09 | Explore pagination | 10 |
| C10 | Money/time/rate display + ordering | 8 |
| C11 | Guide local answers | 6 |
| C12 | EXRULES excluded topics | 10 |
| C13 | Guide empty state + starters | 10 |
| C14 | Agent fallback chain | 10 |
| C15 | OAuth round-trip persistence | 9 |
| C16 | Progress sync to DB | 10 |
| C17 | Profile page + editable rows | 9 |
| C18 | "How Upmore makes money" disclosure | 7 |
| C19 | Sign out | 10 |
| C20 | Reminders toggle UI | 3 |
| C21 | PWA | 9 |
| C22 | Visual identity | 10 |

**10/10 count: 11** (C03, C06, C07, C08, C09, C12, C13, C14, C16, C19, C22).
**Mean: 8.6/10.**

## Full gap list (concrete fixes)

1. **C11/C02 stale verification copy (suspect #1 CONFIRMED):** "we have not verified
   live provider terms yet" is false for 1500/1767 routes. Fix in `routeParas()` +
   `guideAnswer()` verif branch: branch on `r.status` (verified → "Verified against
   {provider}'s official terms"; else keep caveat); verif branch → "1,500 of 1,767
   routes are verified against official provider terms…".
2. **C02 dead `_moves` personalization:** `planData()` returns a fresh object, so
   `d._moves` is always undefined. Fix: `data._moves = moves` in `buildPlan()`,
   reattach in `planData()`; rank/filter moves by the user's time/cash/state.
3. **C02/C15 "undefined a week":** `buildPlan()` + `guideCtx()` lack the fallback
   `renderProfile()` has. Fix: `|| "some time"` on the time-label map.
4. **C11 branch shadowing:** "free to start" swallowed by the `easiest` branch.
   Fix: move the no-deposit branch above `easiest` (or guard it).
5. **C10 retired routes live in Explore:** R0067/R0549 rendered as earnable, no badge;
   R0067 breaks ratio ordering. Fix: exclude `status==="retired"` in
   `stdRoutes()`/`xFiltered()` or badge them.
6. **C18 affiliate promise without mechanism:** no `affiliate` field on any route, no
   per-card disclosure. Fix: add the field in `build-data.py`, badge in
   `renderExplore()` + `routeCard()`.
7. **C20 decorative reminders toggles:** flip `aria-pressed` only; nothing persists,
   nothing reads. Fix: persist to `localStorage` + DB (`profiles.prefs`), init from
   stored value in `renderProfile()`.
8. **C05 no iOS store links:** zero `apps.apple.com` URLs in 1767 routes; iPhone users
   get Play Store links. Fix: `ios_url`/`android_url` per app route, platform-aware
   `stepLinks()`.
9. **C21 icons not precached:** add icon PNGs to `sw.js` SHELL.
10. **C04 data-side:** only 261/1767 routes have `done_when` — backfill in the
    verification pass.

## Known-suspect verdicts

1. **"we have not verified live provider terms yet" — STALE/WRONG, confirmed.**
   Present in production `index.html` (1 occurrence in `routeParas`, 1 in the verif
   branch). 1500 routes carry `status:"verified"` with numeric evidence.
2. **"23 routes in the higher-risk lane" — ACCURATE.** Data: 23 Restricted total,
   8 verified, all hidden from Explore by default; toggle label `(23)` matches.
