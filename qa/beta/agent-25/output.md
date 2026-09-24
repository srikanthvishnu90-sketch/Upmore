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
