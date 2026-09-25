# Agent E2 — Earn Verification States: VERDICT **FAIL**

**App**: https://upmore-srikanthvishnu90-sketchs-projects.vercel.app/
**Spec**: Earn Doc 1 — verification states `unverified → confirmed → stale → expired → retired`
**Method**: Code audit of `src/upmore-app-template.html` + built `index.html` + catalog `src/data/upmore-data.json`, plus production page-text fetch. (Live-browser task delegation unavailable to this agent; all findings below are from the shipped code and data, which is the stronger evidence — the defects are in the logic, not the rendering.)

## Verdict: FAIL — the verification system is theater. Five defects.

### DEFECT 1 (critical): The badge always lies — every queue card says "unverified"
`src/upmore-app-template.html:1897`: `const ver = r.verification || "unverified";`

The catalog has **no `verification` field on any of its 1990 routes** (verified: zero routes contain the key). The real field is `status`, with values `researched` (1402 routes), `retired` (323), `unverified` (265). Because `r.verification` is always `undefined`, the `vbadge` on every Earn card in the queue renders the literal word "unverified" — including for the 1402 routes the catalog marks `researched`.

Worse, the Explore surface contradicts it: line 2956 renders `✓ Researched` for those same routes. **The same route carries two different trust signals depending on which screen you're on.** A user comparing queue vs. explore sees "unverified" and "✓ Researched" for one offer. That is exactly the kind of unverified-offer presentation the spec exists to prevent.

### DEFECT 2 (critical): `verifyRoute()` is dead code — staleness never happens
`verifyRoute()` (line ~3112) implements the 30-day auto-stale and the terms-hash-changed → stale rule. It has **zero call sites** in the codebase. Nothing ever invokes it — not on load, not on a schedule, not after data refresh. There is no nightly job, no terms-hash fetcher, no refresh pipeline at all (grep for `termsHash|nightly|cron`: only the dead function itself).

Consequence: even if a route were marked `confirmed` tomorrow, it would **never** go stale — the "confirmed becomes stale automatically at 30 days" rule is unenforced, and "nightly terms-hash changes must immediately mark routes stale" is fiction. The state machine has transitions that cannot fire.

### DEFECT 3 (high): Gate 4 (freshness) is a no-op
`routeGateInputs` (line ~3170) maps `verification: r.verification || "unverified"` — always `"unverified"`. Gate 4 passes `confirmed` or `unverified`, so it passes 100% of routes, 100% of the time. It filters nothing and can filter nothing, because the field it reads doesn't exist in the data.

The "stale may never lead or enter a plan" invariant holds today **only vacuously** — the `stale` state is unreachable, not guarded. The gate logic itself (`route.verification === "confirmed" || "unverified"`) is actually correct and *would* filter stale/expired/retired if the field were populated — the data plumbing is what's missing.

### DEFECT 4 (high): No verification age/date anywhere — card element #8 unimplementable
Spec card element #8: "Plain verification age/date." The catalog contains **zero date fields** — no `verified_at`, no capture date, no `updated_at` (full key list audited; the closest matches are `time_to_first` and `time_min_minutes`, which are durations, not dates). The badge renders only the state word. There is no way for any user to see *when* an offer was verified, which makes the freshness story unverifiable by construction.

### DEFECT 5 (medium): `researched` (70% of catalog) has no mapping into the spec taxonomy
The spec taxonomy is `unverified/confirmed/stale/expired/retired`. The catalog's dominant status, `researched` (1402/1990 routes), maps to nothing. The app's *actual* trust system runs on `status` in parallel: `qConf` (line 1727) gives researched routes 0.7 confidence vs 0.4, and Explore badges them "✓ Researched". So there are two trust systems — the spec's (dead) and the legacy `status` one (live but unmapped) — and they disagree on-screen.

Open question for the owner: does `researched` meet the spec's `confirmed` bar (operator-owned exact terms page + verbatim requirements + direct URL + capture date)? The catalog has `url`, `requirements`, `reward` — but no capture date, so the bar cannot be evidenced either way. The honest options are (a) add `verified_at`/capture-date to the catalog and map explicitly, or (b) stop rendering spec-taxonomy badges until the data exists.

## What was checked and passed
- Retired routes cannot lead: `stdRoutes()` filters `r.status !== "retired"` before `rankMoves()` scores, so the 323 retired routes never enter the queue. (This works via the legacy `status` field, not via the verification gate.)
- No `stale`-badged route leads the queue — vacuously (Defect 3).
- The `v-stale`/`v-confirmed` CSS classes exist, so *if* the data were fixed the styling would follow.

## Required fixes (in order)
1. Map catalog `status` → spec verification explicitly, in one place, and render the badge from the mapped value. Retire the contradictory "✓ Researched" badge or unify it with the mapped badge.
2. Either wire `verifyRoute()` into a real refresh path (with `verified_at` dates added to the catalog) or delete it — dead spec machinery is worse than absent machinery because it implies a guarantee that doesn't run.
3. Add `verified_at` / terms-capture date to the catalog so element #8 (verification age/date) can be rendered truthfully.
4. Gate 4 then works as written — no logic change needed, only data.

## Bottom line
The spec's core promise — "the one [app] that doesn't show offers it has not verified" — currently rests on a badge that always prints "unverified" from a field that doesn't exist, a staleness function that never runs, and a gate that never closes. Harsh but accurate: **the verification layer is decorative, not functional.**
