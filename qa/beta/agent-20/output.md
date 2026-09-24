
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
