
## RUN 1 (2026-09-24, build dbb4578) — AGENT 20: FAIL (7 fails)
Phone-fit test. PASS: sign-in (x2, one env session-drop recovered), all 3 tabs no horizontal overflow (caveat: no viewport-resize API; checks done against the app's phone column), walkthrough open/resume/advance/stuck-help, promo sheet open/close/"Start promo"->Guide prefill, "Show more" +60 cards, search filter 1632->427, Track disclosures expand/collapse, export download, delete-confirm gating, sign-out/re-sign-in, Guide chat controls, "Open jmbullion.com" new tab, all sheets closable.
FAIL:
1. Subscription Save -> "Couldn't save - check your connection and try again." (x2, form retained values)
2. Deadline Save -> same error.
3. Money log "Log it" -> same error; log stayed $0.00.
4. Bank-sync "Notify me" -> "Something went wrong - try again."
5. Guide header "History" button dead (3 taps, no response). CONFIRMED real: button had no click handler in source.
6. Offer card body text clipped mid-word at right edge ("...verified. / Orde", "...first 4 mon"). CONFIRMED real: .chat is flex-column; .msg flex items lacked min-width:0/overflow-wrap, so long unbreakable strings overflowed the phone column and were cut by an ancestor's overflow:hidden.
7. Deadline "Kind" combobox squeezed ("Bill re..."). CONFIRMED real: 44px right padding for the custom caret inside a half-width grid cell.
Minor copy: promo fine print "advance notice.,Only ACAT transfers qualify" — CONFIRMED real: catches stored as JSON arrays; template rendered them via implicit Array.toString() (bare-comma join).
DIAGNOSIS on fails 1-4: NOT reproduced as product bugs. Same spawn batch as agent 15r (which definitively received the stale pre-dbb4578 build via the cache-first service worker); the old error strings appear only when (a) on the stale build while signed out, or (b) the shared test profile's concurrent sign-in/out churn invalidated this agent's token mid-run while the in-memory session stayed non-null. Agents 21r/22r saved successfully in the same window, so no DB/RLS outage. Fixes: (i) service worker now network-first for the app shell + per-build cache versioning (kills stale-build class); (ii) rerun agent 20 SEQUENTIALLY (no concurrent agents) against the fresh build.
FIXES (same day, unreleased): removed dead Guide History button (chat has no persistent history; dead button worse than none); .msg min-width:0 + overflow-wrap:break-word; .f min-width:0; select right padding 44px->34px, caret 18px->13px; build-app.py normalizes array catches to "; "-joined strings.
Cleanup: done — all saves failed, Track empty, money log $0.00; left signed in as qa20@upmore.app on Guide tab.

## Rerun 2 (2026-09-24, build 00826d2, account qa20r@upmore.app) — RESULT: FAIL (1 defect, since fixed)
Fresh-build protocol PASS (no History button). Phone fit PASS on all 3 tabs (no overflow at 390px; Kind select unclipped).
Write paths ALL PASS: Fit20 sub saved + queue showed exact "$119.88/yr" (cents preserved); D20 deadline "Renews in 26 days"; $20 M20 money-log entry; bank-sync waitlist join. No save errors.
Regression: walkthrough + "I'm stuck" PASS; profile name "qa20r" PASS (Friend bug fixed); export PASS; delete sheet DELETE-gate PASS.
Sign-out/re-sign-in PASS: Fit20, D20, M20 survived; name still "qa20r" (no session mismatch).
Cleanup PASS: sub cancelled, D20 done, M20 reversed, Track empty, log $0.00, signed out.
DEFECT (confirmed, real): SoFi Invest promo sheet truncated reward mid-word at 390px ("...requires moving EX", no ellipsis) — promoSheetMeta sliced to 80 chars. The fine-print moment must not clip.
Secondary observation (intentional by design, not a defect): cancelling a subscription routes to Guide with a "confirm it's really cancelled" walkthrough — marking cancelled in-app doesn't cancel with the merchant, so the hand-off serves the intent.
FIX deployed as 2d55442: promo sheet now shows the FULL reward text + a "Watch out:" catches line (overflow-wrap:anywhere); short() truncates at word boundaries with ellipsis; queue claim subtitles use short(r.reward, 90). Production probe confirms full text renders ("...earns $0") with catches shown, no overflow.
Retrospective: the phone experience serves its intent — dead-simple money page, thumb-navigable, writes persist. The one defect hit the worst possible spot (offer fine print) and is now fixed.

## Rerun 3 (2026-09-25 ~00:19 UTC, build 0e4651c, signed-out) — RESULT: PASS
Targeted check of the 2d55442 promo-sheet truncation fix at 390px. Freshness gate PASS (no Guide History button).
- SoFi Invest promo sheet: reward shown IN FULL, word-boundary wrapping — the old "...requires moving EX" defect is fixed. Labeled "The catch:" line present (US; ACAT transfers must remain 5 years; early-withdrawal fee). No horizontal overflow, nothing clipped at the right edge. Tail reads: "...an ordinary user with no other brokerage earns $0 · Weeks to months" — the catalog data itself is honest about the $0 case, which validates the blocked() filter's rationale.
- Robinhood promo: full 105-char reward text, "The catch:" line present (targeted offer; 7-day window; 1-year lock), no overflow.
- VERDICT: AGENT 20 RERUN 3: PASS. No test data created; nothing to clean.

## RERUN 3 — final suite (build 968ece1, 2026-09-25)
Signed-out scenario (no account created).
Fresh-build gate: PASS.
(a) Reward not cut mid-word — PASS (full text renders; mid-word fragments were accessibility-tree truncation, not app rendering).
(b) "Watch out:" catches line — PASS ("The catch: US; Qualifying transfers must remain ... for five (5) years ... early-withdrawal fee ...").
(c) No 390px overflow — PASS.
(d) Payout = $50–$400 tier — NOT A BUG: wrong expectation. The SoFi Invest card (R0018) correctly shows its own terms: "1% ACAT match up to $50,000" (payout 0/50000 correct — 1% of transferred assets). The $50–$400 direct-deposit tier is the separate R0096 SoFi fintech card (already fixed to 50/400). R0018 is ACAT-gated (NEEDS_EXISTING_IDS, blocked for cash <$10k) so it can't lead for beginners.
AGENT 20 FINAL RESULT: PASS (promo-sheet truncation fix verified)
