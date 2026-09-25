# E2-v2 EXHAUSTIVE — Earn Verification Taxonomy (Doc 1)

**Agent:** E2-v2 · **Date:** 2026-09-25 · **App:** https://upmore-srikanthvishnu90-sketchs-projects.vercel.app/
**Spec:** Earn (Doc 1) — verification states: unverified → confirmed → stale → expired → retired
**Method:** Node harness extracting `routeVerification` / `earnGates` VERBATIM from
`src/upmore-app-template.html`, executed against the real 1990-route catalog
(`src/data/upmore-data.json`). Badge templates replicated from lines 1979 and 3101.
**Production evidence:** served `sw.js` returns `CACHE = "upmore-8b52c95"`; repo HEAD is
`b73da4f` whose build stamped `8b52c95` — **the tested code IS the deployed commit.**

## Verdict: 125/126 assertions PASS — 5 genuine defects found (1 strict assertion fail + 4 harsh findings)

| Section | Assertions | Pass | Fail |
|---|---|---|---|
| A. Taxonomy mapping (40 required) | 46 | 46 | 0 |
| B. Badge consistency (30 required) | 40 | 39 | 1 |
| C. Gate 4 (30 required) | 40 | 40 | 0 |
| **Total** | **126** | **125** | **1** |

---

## DEFECTS (harsh findings — all verified against deployed code)

### F1. Queue badge ≠ Explore badge text for the same route (B03 — strict FAIL)
- Queue (line 1979): researched route renders `<span class="vbadge v-confirmed">confirmed</span>`
- Explore (line 3101): same route renders `<span class="vbadge">✓ Researched</span>`
- Strict text match fails. Semantic intent matches, but "Queue badge matches Explore badge
  for same route" does not hold at the text level. Also case-only mismatch for unverified:
  queue `unverified` vs explore `Unverified`.

### F2. CSS cascade: unverified/retired/expired queue badges render GREEN (B13–B19)
- Line 414: `.vbadge { background:#f5f5f5; color:#666; }` (gray, intended for earn cards)
- Line 439: `.vbadge { ... background:#1F7A4D; ... }` (green, intended for Explore) —
  **same specificity, later in the stylesheet, so it wins for EVERY badge.**
- Result: a queue badge reading "unverified" (or "retired"/"expired") is a GREEN pill,
  visually identical to Explore's green "✓ Researched" pill. Trust signaling is inverted:
  unverified routes wear the verified color.
- No `.v-unverified`, `.v-retired`, or `.v-expired` rules exist (only `.v-confirmed` blue
  and `.v-stale` orange — and "stale" is unreachable, see F5).
- Only `.vbadge.v-confirmed` (0,2,0 specificity) survives the override.

### F3. Gate 4 BYPASS: retired routes can lead the Home queue as claim cards (C20b/C21/C24/C25)
- `buildQueue()` claim-card path (line ~1946) filters `D.routes` directly for
  `["Bank Bonus","Brokerage Promo","Signup Bonus"]` with **no `routePassesGates` call**.
- Two RETIRED routes sit in those categories and pass every other filter
  (not in `NO_LEAD_IDS`, not blocked, canLead passes — both are cash bonuses):
  - **R0067** — First Merchants Bank, Bank Bonus, status `retired`
  - **R0549** — First Horizon Bank, Bank Bonus, status `retired`
- They can occupy queue slots via `.slice(0, 3)` as `type: "claim"` cards.
- Spec: "Stale/expired/retired routes do NOT lead queue." **Violated on this path.**
  (Earn cards are protected by `stdRoutes()` + gates; Explore is protected by gates —
  only the claim-card path is unguarded.)
- Claim cards also render **no verification badge at all** (no `earn8` block, B24/B25) —
  a retired promo appears with zero trust signal.

### F4. Explore badge ignores explicit `r.verification` overrides (B21/B23)
- Explore badge reads `r.status` directly (`r.status === "researched" ? ... `, line 3101);
  queue badge and gates use `routeVerification()` which honors explicit overrides.
- A route with explicit `verification: "retired"` on `status: "researched"` would show
  "retired" in queue/gates but "✓ Researched" in Explore. Latent today (no catalog
  route has an explicit `verification` field — verified by scan), but the two badge
  systems do not share one source of truth.

### F5. `stale` exists in the taxonomy but has NO producer (A32)
- Spec taxonomy: unverified → confirmed → stale → expired → retired.
- `routeVerification()` never returns "stale" from catalog data: statuses are only
  researched/retired/unverified; "stale" is reachable solely via explicit override
  (zero routes). The `.vbadge.v-stale` orange CSS is dead code in practice.
- "expired" likewise has no catalog producer (mapping exists for a hypothetical
  `status: "expired"`, zero routes).

### Advisory — earnGates reads `route.verification` directly (C15)
- Gate 4's expression is `route.verification === "confirmed" || route.verification === "unverified"`.
  It is correct **only** because the sole caller `routePassesGates` injects
  `verification: routeVerification(r)` via `routeGateInputs`. A direct `earnGates(rawRoute)`
  call fails freshness spuriously (verified). Spec's "use routeVerification(), not
  r.verification directly" holds transitively, not literally — fragile to a second caller.

---

## WHAT PASSES (verified, not assumed)

**Taxonomy mapping (46/46):**
- researched → confirmed · retired → retired · unverified → unverified · expired → expired — exact.
- Explicit `r.verification` overrides mapping in all 5 states; falsy overrides (`""`, null,
  undefined) correctly fall back to status mapping.
- Case-insensitive status matching (`RESEARCHED`, `Retired`, `EXPIRED` all map correctly).
- Exhaustive catalog sweep: **1402 → confirmed, 323 → retired, 265 → unverified** (sums to
  1990; zero stale, zero expired from data; every output ∈ the 5-state taxonomy).
- `routeGateInputs` sets `verification: routeVerification(r)` — Gate 4 and queue cards share
  the single mapping function (verified by source + functional checks on sampled routes).

**Badge consistency (39/40):**
- No researched route ever renders "unverified" in its queue badge (all 1402 checked).
- No route shows "unverified" in queue while "✓ Researched" in Explore (all 1990 checked).
- All 1402 researched routes: queue badge class exactly `vbadge v-confirmed`; all 265
  unverified: exactly `vbadge v-unverified`.
- Badge text comes from the mapped value only (`v-${ver}`), never raw `r.status`; badge
  text is HTML-escaped.

**Gate 4 (40/40):**
- `confirmed` → pass, `unverified` → pass; `stale`/`expired`/`retired` → fail with
  `failedGate === "freshness"` (exact).
- 5 sampled retired routes: ALL fail at freshness; 5+5 sampled researched/unverified
  routes: none fail freshness.
- Explicit override `confirmed` on a retired status passes; `stale` override on researched
  fails — overrides flow through Gate 4 correctly.
- `stdRoutes()` pre-excludes retired from earn ranking; `xFiltered()` applies gates to
  Explore (retired excluded there too); Explore list pre-filter excludes retired.
- Degenerate inputs: uppercase `"CONFIRMED"` rejected (gate is case-sensitive, mapper
  never emits uppercase — no hole).
- `earnGates` has exactly one caller; freshness is gate #4 in order.

---

## Full assertion log (126)

Harness: `/tmp/e2v2_harness.js` (extracts functions verbatim from template).
Raw results: `/tmp/e2v2_results.json`.

**Section A — Taxonomy mapping:** A01–A45 + A44/A45 (46 total) — ALL PASS.
Key: A01 researched→confirmed · A02 retired→retired · A03 unverified→unverified ·
A04 expired→expired · A05 stale→unverified (no producer) · A06/A07 missing/empty→unverified ·
A08–A12 case-insensitivity · A13–A17 explicit override wins (all 5 states) · A18 falsy
override falls through · A19/A20 garbage/null→unverified · A21 unpadded→unverified (no trim) ·
A22–A26 outputs ∈ taxonomy · A27 all 5 states reachable via override · A28–A31 distribution
1402/323/265 = 1990 · A32 no stale from data · A33 no expired from data · A34 all ∈ taxonomy ·
A35 gate inputs use routeVerification · A36–A38 sampled gate-input mapping · A39–A43 queue
badge class+text per state · A44 no researched→"unverified" badge · A45 queue uses
routeVerification().

**Section B — Badge consistency:** B01–B40 (40 total) — 39 PASS, 1 FAIL.
FAIL: B03 (queue "confirmed" vs explore "✓ Researched" text mismatch).
PASS includes: B09 no unverified/✓Researched contradiction (1990 routes) · B10/B11 all 1402
researched consistent · B13/B14 cascade documented · B15–B19 green-badge findings (recorded
as defects F2) · B21/B23 override divergence (defect F4) · B24/B25 claim cards badgeless
(defect F3) · B39/B40 exact badge classes.

**Section C — Gate 4:** C01–C40 + C20b (40 total) — ALL PASS (assertions); defects F3 and
advisory recorded as findings.
Key: C01/C02 pass confirmed+unverified · C03–C05 reject stale/expired/retired at freshness ·
C06–C08 sampled routes · C09/C10 synthetic expired/stale rejected · C11 override confirmed
passes · C12 gate expression exact · C13/C14 single-caller injection · C16–C19 queue/explore
guarded · C20b/C21 claim-path bypass (defect F3) · C22–C26 R0067/R0549 retired-and-queueable ·
C27 single mapping shared · C28/C29 comments match data · C31–C33 falsy-override fallback ·
C34 case-sensitivity · C36–C40 ordering/robustness.

## Recommended fixes (for parent)
1. Claim-card path: apply `routePassesGates` (or at minimum a Gate-4 freshness check) to the
   Bank Bonus/Brokerage Promo/Signup Bonus claim filter in `buildQueue`.
2. CSS: move the Explore-specific `.vbadge`/`.ubadge` rules to scoped selectors
   (e.g. `.xitem .vbadge`) or add `.v-unverified/.v-retired/.v-expired` rules and rename
   the Explore badge class so unverified queue badges are not green.
3. Unify badge text: use one function for queue + Explore badge text (e.g. "✓ Researched"
   vs "confirmed" — pick the taxonomy term "confirmed" everywhere).
4. Explore badge: derive from `routeVerification(r)` so explicit overrides are honored.
5. Consider making `earnGates` call `routeVerification()` internally for defense in depth.
