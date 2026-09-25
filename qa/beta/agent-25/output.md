# Beta agent 25 - output

## RUN 1 (2026-09-24, build 805587c, signed-out arc + qa25n@upmore.app) — RESULT: FAIL (3 gaps)
1. Home queue recommended moves a first-timer cannot use: JM Bullion buyback
   ($1,000 minimum, paid 3-7 days), SoFi ACAT ("an ordinary user with no other
   brokerage earns $0"), Microsoft bug bounties ("Earn up to $250,000") —
   under copy "Why this one: the best earn rate for your time and budget."
   Root causes: (a) noCash filter used exact category match — "Niche Buyback",
   "Buyback/Resale", "Gift Card Resale" leaked; (b) ACAT transfer promos not
   filtered; (c) 3x same-day multiplier could not beat earn ratios spanning
   orders of magnitude; (d) Guide "easiest" handler used RAW CATALOG ORDER.
2. Guide answer to "I want to make my first $20 online today, where do I
   start?" reframed the same three hard routes as "The 3 easiest routes in the
   whole catalog" — never named who pays / when cash arrives vs "today".
3. Signed-in You tab showed onboarding nickname "QA" with no account
   identifier — signed-in identity unverifiable. (Agent invoked the session-
   mismatch stop rule; login itself had succeeded.)
Verdict: arc is visually simple and avoids guaranteed-money language, but the
recommendations were unachievable for the target first-timer.

## FIXES (shipped 9a82747, verified live 2026-09-24)
- needsSpend predicate: substring-matches buyback/resale/rent-assets + filters
  4 ACAT transfer-promo IDs (R0018, R0023, R5782, R1067) for $0-cash users.
- rankMoves: speed-tier sort (today > days > weeks) replaces the 3x
  multiplier. Node harness on real built code: $0-cash beginner top-6 now all
  speed="today" (Southeastbank, Strike, Reward XP Games, Mindswarms, Blazecu,
  iTHINK Financial); JM Bullion / SoFi / Microsoft all filtered out of top-6.
- Guide "easiest/first/start" now uses rankMoves() (personalized) instead of
  raw catalog order.
- Guide "today" branch: answers from same-day routes with who-pays +
  when-cash-arrives + straight-talk line that work comes first.
- You tab: signed-in account email now shown under the profile name (pMail).

## REVERIFY (2026-09-24/25, build 9a82747) — RESULT: 2 PASS, 1 FAIL (stale-build suspected)
- Check 2 (Guide today answer) PASS: "The fastest routes in the whole catalog —
  these pay out the same day you finish" + Who pays / Cash arrives per route +
  "Straight talk: you do the work first..." No buyback/brokerage/bounty routes.
  Observation (not a fail): Southeastbank's own "Cash arrives" (friend must
  qualify within 60 days) contradicts the "same day you finish" intro; its
  reward is fee-free trading, not cash. → fixed in 0e4651c (softer intro).
- Check 3 (account email) PASS: You tab shows qa25n@upmore.app under the name.
  Note: name showed "QA" (stored from run 1's signed-out onboarding via
  saveProfile on sign-in) — correct behavior, not a bug.
- Check 1 (first moves) FAIL as reported: JM Bullion / Microsoft / Robinhood
  topped the queue. ANALYSIS: impossible on 9a82747 for any cash value —
  node harness on the real built code proves rankMoves filters/tier-sorts
  correctly (top-6 all speed="today" for cash=0; JM Bullion speed="days" can
  never outrank 111 today-routes under tier sort). Check 2's copy proves the
  agent HAD 9a82747 later in the same run → the run straddled a deploy: check 1
  ran on the pre-deploy build (805587c: old ratio sort, exact-match filter).
  Lesson: the History-button freshness gate cannot detect staleness (that
  button never existed). Future runs must canary on a build-specific string.

## FIXES (shipped 0e4651c, verified live 2026-09-25)
- blocked(r, cash): needsSpend && cash<=0; ACAT IDs && cash<10000;
  buyback/resale/rent-assets && cash<1000. rankMoves AND claim cards use it.
- Guide today intro softened: "check Cash arrives on each before you start".
- Node harness (full queue pipeline incl. qScore sort): no buyback /
  brokerage-transfer / bug-bounty in top-3 for cash=0 or cash=100.
- Open catalog gap (not a code bug): speed="today" means "work finishes
  today" on some referral routes while cash arrives in ≤60 days; speed
  semantics need a catalog pass.

## CHECK 1 RERUN (2026-09-25 ~00:13 UTC, build 0e4651c, hardened protocol) — PASS
- Build canary FRESH on first try: Guide "what pays today" answer contained the
  exact "Straight talk:" line. No stale-build straddle this run.
- Signed-out onboarding as "Canary": time "About an hour", cash "$0" CONFIRMED
  visually selected (green highlighted border, aria-pressed) before continuing.
- Home queue first 3 cards (matches the node harness prediction exactly):
  1. Reward XP Games — earn XP playing games, up to $1,000 per game (today tier)
  2. Strike — referral, fee-free trading (today tier)
  3. Southeastbank — referral bonus $50/$100/$150 (today tier)
- None: JM Bullion/buyback, SoFi/Moomoo/Sogotrade/Public transfer promos,
  Microsoft bounties, nothing requiring $1k+ assets. All beginner-actionable.
- "Up next:" header shows the formula components ($1000 x 70% x 2 / 60 min).
- FINAL: agent 25's three gaps are all closed on 0e4651c.
- Remaining product note (open catalog gap, not a check failure): speed="today"
  conflates "your work finishes today" with "cash arrives today" — e.g.
  Southeastbank's payout_timing says the friend must qualify within 60 days;
  Strike's reward is fee-free trading, not cash. Catalog speed semantics need
  a dedicated pass before the final full-suite rerun.

## RERUN — final suite (build 968ece1, 2026-09-25)
Account: qa25n@upmore.app (email-matched gate).
Fresh-build gate: PASS.
1. Export — PASS (upmore-data.json downloaded; contents unverified in-run).
2. Delete copy — PASS on data enumeration ("erases your profile, plan progress, subscriptions, money log, renewals, claims, reminders, and Guide chat history"); FAIL on account fate (never states the account/login itself is deleted). Typed DELETE confirmation required (button disabled until typed) — strong.
3. "How does Upmore make money" — PARTIAL/FAIL: honest ("none of the offers pay us anything") + badge commitment, but silent on data sale and user charges. Follow-up "Do you sell my data, and do you ever charge the user?" was EVADED — misclassified by the refusal rules ("We don't touch that one. Privacy violations...").
4. CONTRADICTION: welcome page "Some offers pay us a small cut" vs Guide "none of the offers pay us anything". Truth: 0 routes have affiliate=true — Guide is right, welcome page is wrong.
FIXES QUEUED (uncommitted, syntax OK):
(a) Delete copy now states the account is deleted too ("you won't be able to sign in with this email afterward").
(b) Money answer adds "Two things we will never do: sell your data, or charge you for Upmore."
(c) New policy-question branch ("do you sell...", "is upmore free") answers directly, placed BEFORE the refusal rules so it can never be misclassified again.
(d) Welcome page corrected to "No offers pay us anything right now — you get every dollar."
AGENT 25 FINAL RESULT: FAIL (assertions); fixes queued for final build
