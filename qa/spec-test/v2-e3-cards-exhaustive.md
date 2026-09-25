# Agent E3-v2-RETRY — Earn: 8-Element Cards EXHAUSTIVE — HARSH REPORT

**Verdict: FAIL** — 436/475 assertions pass. 39 failures, including 3 systematic defects that affect all (or many) Earn cards: element-8 ordering violation (25/25), "≈null min" time rendering (273/1,990 routes), and verification age/date absent (1,990/1,990 routes — catalog data gap).

**Tested:** `src/upmore-app-template.html` at local HEAD `8a6598f` (post E6-v2 fixes: $/min removed, class-badge mapping, headline fix). The `earn8` 8-element card block renders in exactly ONE place — `renderQueue()` (~line 2018). No live browser available; the render path is a single deterministic template literal, so the functions were replicated EXACTLY in Node (`/tmp/e3test.js`) and executed against 25 stratified catalog routes. Code-path-exact testing.

**Spec under test** (docspecs/01-earn.md, "The Earn card: exactly eight ordered elements"):
1. Provider / description
2. Exact terms-stated reward
3. Class badge
4. Requirement checklist
5. Honest catch
6. Active minutes
7. Payout timing (observed median, or clearly labelled advertised)
8. Plain verification age / date

**Sample (25 routes):** 3 bank-bonus, 4 variable-payout, 3 fixed-payout, 3 speculative-class, 4 missing-time, 2 unverified, 2 retired, 2 array-catches, 2 researched filler.

---

## SCOREBOARD: 475 assertions — 436 PASS / 39 FAIL

| Element | Assertions | Pass | Fail |
|---|---|---|---|
| E1 Provider exact | 50 | 50 | 0 |
| E2 Reward exact / variable range | 50 | 49 | 1 |
| E3 Class badge (exactly one, spec set) | 75 | 75 | 0 |
| E4 Requirements verbatim | 50 | 50 | 0 |
| E5 Catch present & sane | 50 | 50 | 0 |
| E6 Active minutes (min-max, no null) | 50 | 44 | 6 |
| E7 Payout timing | 25 | 25 | 0 |
| E8 Verification badge (routeVerification + age/date) | 75 | 68 | 7 |
| ORDER: spec sequence | 25 | 25 | 0 |
| ORDER: verification badge LAST | 25 | 0 | 25 |
| WHY line: no projections | 25 | 25 | 0 |

---

## DEFECT 1 [CRITICAL, systematic]: Element 8 is not last — ordering violation on 25/25 cards

Spec order: 1,2,3,4,5,6,7,8. Actual DOM order in `.earn8`: **1,2,3,8,4,5,6,7**.

The verification badge (`<span class="vbadge">`) renders immediately after the class badge, BEFORE requirements/catch/time:

```html
<div class="earn8">
  <span class="ebadge">…</span>      <!-- element 3 ✓ -->
  <span class="vbadge v-confirmed">…</span>  <!-- element 8 ✗ WRONG POSITION -->
  <p class="ereq">…</p>              <!-- element 4 -->
  <p class="ecatch">…</p>            <!-- element 5 -->
  <p class="emeta">…</p>             <!-- elements 6+7 -->
</div>
```

Measured character offsets on all 25 sample cards confirm: `vbadge` position < `emeta` position on every card (e.g. R0069: vbadge@392, emeta@2205).

**Fix:** in `src/upmore-app-template.html` (~line 2019–2023), move the `<span class="vbadge …">` line to AFTER the `<p class="emeta">` line.

---

## DEFECT 2 [HIGH, 273 routes]: Element 6 renders "≈null min active"

273/1,990 catalog routes (13.7%) have `time_min_minutes = null` AND `time_max_minutes = null`. The template:

```js
${r.time_min_minutes === r.time_max_minutes ? `≈${r.time_max_minutes} min` : `≈${r.time_min_minutes}–${r.time_max_minutes} min`} active
```

`null === null` is `true`, so it takes the single-value branch and interpolates `null`:

> `≈null min active · Cashback credited in near real time…` (R7930 Moneylion — actual rendered output, confirmed in Node)

6 of the 25 sample routes hit this (R7930, R7940, R7941, R7942, R0365, R0370). The Active-minutes element is visibly broken — a user sees the literal word "null".

**Fix:** guard the time segment — if both are null, render `Time varies` or omit the segment:
```js
${r.time_max_minutes == null ? `Time varies` : r.time_min_minutes === r.time_max_minutes ? `≈${r.time_max_minutes} min` : `≈${r.time_min_minutes}–${r.time_max_minutes} min`} active
```

---

## DEFECT 3 [HIGH, all 1,990 routes]: Element 8 has no verification age/date — catalog data gap

Spec element 8: "Plain verification age / date." The badge renders only the state word (`confirmed` / `unverified` / `retired`). Verified across the full catalog: **zero routes** have any verification-date field (`verified_at`, `verification_date`, `researched_at`, `confirmed_at`, `last_verified` — all 0/1,990).

This cannot be fixed in the card template alone without inventing dates (forbidden). Options for the owner:
- (a) add `verified_at` per route in the catalog (data work), or
- (b) render the catalog-level stamp ("Catalog verified 2026-09-24") as the age, clearly labelled.

7 of 25 sample assertions flagged this directly; the remaining 18 passed only because digits elsewhere in the card (requirements text) satisfied a weak substring check — in reality **25/25 badges carry no age/date**.

---

## DEFECT 4 [MEDIUM, data]: Element 2 — variable range missing on R8323

R8323 (JM Bullion): `payout_min=1000`, `payout_max=50000`, but `reward` text is "Payment is typically issued in 1-3 business days from the time your items have been…" — no amount range anywhere in the text. The card renders it verbatim, so the user never learns the reward is $1,000–$50,000. Per the task criterion ("Reward: exact, with range if variable"), this fails. Root cause is catalog data (reward text missing the range), not card code. Suggested: data fix, or append the numeric range on the card for variable routes (payout_min/max are terms-stated catalog figures — the walkthrough intro already shows `≈$min–$max` via `earnLine()`).

---

## DEFECT 5 [LOW, cosmetic]: Element 5 — array `catches` comma-joined without space

1,729/1,990 routes store `catches` as an array. The template does `esc(r.catches)` → `String(array)` → comma-joined with NO space: `"Minimum sell amount is $1,000 - smaller holdings don't qualify.,Price lock expires in 10 minutes."` Readable but sloppy. **Fix:** `${esc(Array.isArray(r.catches) ? r.catches.join("; ") : (r.catches || "—"))}`.

---

## What PASSES (436 assertions)

- **E1 (50/50):** `<h4>` title is exactly `{provider} — {method}` on all 25 cards; provider name verbatim.
- **E2 (49/50):** `routeMeta()` renders `r.reward` verbatim + `time_to_first`; no invented single numbers, no collapsed ranges (except Defect 4, a data issue).
- **E3 (75/75):** Exactly ONE `ebadge` per card on all 25; every badge is in the spec set (`Fixed reward` / `Variable`) after the E6-v2 G8 mapping fix. (v1: 0% compliant. Now 100%.)
- **E4 (50/50):** `ereq` block present on all cards; requirements rendered verbatim.
- **E5 (50/50):** `ecatch` block present on all cards; no `[object Object]`; honest downside text from catalog.
- **E6 (44/50):** min–max ranges render correctly where data exists (`≈20–45 min`); only null-data routes fail (Defect 2).
- **E7 (25/25):** payout timing present via `payout_timing || time_to_first` on every card. (Note: it is advertised timing from terms, not labelled "advertised" vs "observed median" — spec asks for the label; minor.)
- **E8 badge source (68/75):** badge text always equals `routeVerification(r)` output — derived from the single mapping function, never hardcoded; `researched→confirmed`, `retired→retired`, `unverified→unverified`, explicit override wins.
- **Order 1–6 (25/25):** provider → reward → class badge → requirements → catch → time all in spec sequence.
- **WHY line (25/25):** no "you'll earn $X" projections; only the spec-mandated ranking decomposition (`$d × c% × u / eff min`).
- **Gate 4:** retired routes cannot reach the queue (`routeGateInputs` sets `verification: routeVerification(r)`; gate requires confirmed/unverified).

## Observations (not failures, for the owner)

1. **Explore badge inconsistency:** Explore rows use `r.status === "researched" ? "✓ Researched" : "Unverified"` directly, NOT `routeVerification()`. A retired route viewed under a lane filter shows "Unverified" in Explore but "retired" in the queue. Recommend using `routeVerification()` in `renderExplore()` too.
2. **Other Earn surfaces are condensed, not 8-element:** onboarding "moves" cards (line ~1478), agent `routeCard()` (~2515), and Explore rows (~3165) show title/meta only. If the spec's "exactly eight" applies to ALL Earn presentations, these fail too; scoped here to the queue card as the canonical Earn card.
3. **Unverified routes CAN appear on the queue** (Gate 4 allows confirmed OR unverified) — per spec, correct behavior; their badge honestly says "unverified".
4. **E7 labelling:** payout timing is terms-advertised but not labelled "advertised" vs "observed median" as the spec parenthetical asks.

---

## Reproduction

- Test script: `/tmp/e3test.js` (replicates `routeTitle`, `routeMeta`, `routeVerification`, class mapping, and the exact `earn8` template literal from `renderQueue()`; runs 475 assertions over 25 stratified routes from `src/data/upmore-data.json`).
- Null-time render confirmed: `node -e` shows `"≈null min active"` for `{time_min_minutes: null, time_max_minutes: null}`.
- Catalog date-field audit: 0/1,990 routes have any verification-date key.

## Required fixes (for parent)

1. Move `vbadge` span after `emeta` in `renderQueue()` (~line 2019–2023) — fixes Defect 1.
2. Null-guard the time segment — fixes Defect 2 (273 routes).
3. Owner call on verification age/date: add `verified_at` to catalog or render catalog-level stamp — fixes Defect 3.
4. R8323 reward text: add the $1,000–$50,000 range to catalog data (or append numeric range on card) — fixes Defect 4.
5. `Array.isArray(r.catches) ? r.catches.join("; ") : …` — fixes Defect 5.
6. (Optional) Use `routeVerification()` for the Explore `researchedBadge`.
