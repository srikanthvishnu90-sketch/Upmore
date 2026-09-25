# Agent 20 — Rerun 3 (targeted): promo-sheet truncation fix verification

Build under test: 0e4651c (contains 2d55442's promo-sheet fix). Production:
https://upmore-srikanthvishnu90-sketchs-projects.vercel.app/

Viewport: 390x844 phone.

## Fresh-build gate (mandatory, do first)
Load the site, wait 5s, reload, wait 3s. This build does NOT have a Guide
"History" button (it was removed). Confirm absence of a History button in the
Guide header as your freshness signal. If a History button IS present, the
build is stale: wait 30s, reload once, re-check; if still present, STOP and
report STALE BUILD.

## Task (signed-out; do NOT sign in; create no data)
Rerun 2 found a real defect: the SoFi Invest promo sheet truncated its reward
mid-word at 390px ("...requires moving EX", no ellipsis). The fix: the promo
sheet now shows the FULL reward text plus a "Watch out:" catches line, with
overflow-wrap:anywhere; queue claim subtitles truncate at word boundaries.

1. Complete the short onboarding as a signed-out beginner (any nickname,
   any answers; e.g. cash "$100").
2. On Home, use catalog search to find "SoFi". Open the SoFi Invest promo
   sheet (tap the card / "Claim" affordance that opens the detail sheet).
3. Read the FULL reward text in the sheet. Assert:
   a. The reward is NOT cut off mid-word — no dangling fragment like
      "...moving EX". Word-boundary truncation with "..." is acceptable
      ONLY if the sheet also offers the full text (it should show it all).
   b. A "Watch out:" (or similarly labeled) catches line is present.
   c. No horizontal overflow at 390px; no text clipped at the right edge.
   d. Quote the first 120 characters and the last 120 characters of the
      reward text as shown.
4. Repeat for ONE more long-reward promo of your choice from search
   (e.g. "Moomoo" or "Robinhood") — same assertions a–c.
5. Close the sheets. Done — no cleanup needed (nothing was saved).

## Verdict
"AGENT 20 RERUN 3: PASS" if 3a–3d hold for both promos, else
"AGENT 20 RERUN 3: FAIL" naming the promo and quoting the clipped text.
