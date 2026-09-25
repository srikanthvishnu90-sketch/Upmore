# Agent E6 — Earn: No Projections (forbidden numbers)
**Verdict: FAIL** — one confirmed spec violation, live in production.

## The violation: derived per-minute rate on Earn surfaces

The spec's omit list is explicit: *"projected route totals, **derived hourly rates**, fake scarcity/countdowns, rounded/annualized/combined rewards, unpublished figures."*

The app renders a **derived dollars-per-minute rate** on Earn routes in two places:

1. **Explore/search results** — every route row renders
   `<span class="xearn">≈$1,000–$50,000 · ≈20–45 min · ≈785/min</span>`
   (template `src/upmore-app-template.html` line 2959, via `earnLine()`)
2. **Walkthrough intro** — *"Why this one: ≈$1,000–$50,000 · ≈20–45 min · ≈785/min"*
   (template line 1587, via `earnLine()`)

### Why it's derived, not terms-stated

`earn_ratio` is a precomputed catalog field: **average payout ÷ average time**.
Verified arithmetically — JM Bullion: `(1000 + 50000) / 2 / ((20 + 45) / 2) = 25500 / 32.5 = 784.6154` ✓ matches the stored `784.6154` exactly. 1,713 of 1,990 routes carry one. No terms page states "$785 per minute" — it is model/pipeline arithmetic presented as a reward fact.

### Why it matters (not a nitpick)

JM Bullion is a *sell-your-gold* route: payout $1,000–$50,000 is the **value of the user's own gold**, time 20–45 min is shipping/handling. "≈785/min" implies $785 of earnings per minute of effort — a meaningless, actively misleading figure. This is the exact failure mode the omit list exists to prevent. A per-minute rate is not saved by the spec saying "hourly" — same banned family, finer unit.

### Confirmed live in production

Fetched `https://upmore-srikanthvishnu90-sketchs-projects.vercel.app/` 2026-09-25 ~04:40 UTC: the served HTML contains the `earn_ratio … /min` rendering code. The violation is not dead code — it renders on every route with an `earn_ratio` in Explore results and every walkthrough intro.

### Scope note (what's clean)

The **new 8-element queue cards** do *not* show the rate — they render active minutes and payout timing as separate elements (template line 1904). The violation is confined to the two older `earnLine()` call sites above.

## Fix required

Remove the `rt` (per-minute) segment from `earnLine()` (template line 1091). The payout range (`≈$min–$max`) and time range (`≈A–B min`) are terms-derived and may stay. Then rebuild, redeploy, and re-verify the served HTML no longer contains `/min`.

## Areas checked — PASS

- **Fake scarcity / countdowns:** zero matches in UI code for countdown/hurry/"only N left"/"ending soon"/"last chance"/"act now"/"limited time". Clean.
- **"Guaranteed" payouts:** the only match is the Terms disclaimer stating Upmore is *"not a guarantee — payouts come from third-party companies."* A disclaimer, not a promise. Clean.
- **Projected multi-route totals:** no UI sums routes into "you could earn $X". The queue "why" line (`$500 × 70% × 1 / 30 min`) decomposes the spec-mandated ranking formula (dollars × confidence × urgency ÷ effort) — the spec's own queue design requires this breakdown. Clean.
- **Annualized figures:** `/yr` figures appear only on Cancel-spec cards (duplicate charges, price hikes), where the Cancel spec explicitly requires a labeled 12-month projection. Not Earn surfaces. Clean.
- **"Up to $X" catalog text:** 300 routes contain "up to" language; 136 don't match `payout_max` numerically, but sampled mismatches are unit differences ("up to 25%" cashback, "up to 48" hours, "up to 4%" APY) versus dollar payout fields — terms-stated figures in different units, not invented dollar projections. Not an Earn-card rendering violation.
- **No `/hour` or `/hr` derived rates** anywhere in UI code — the `/min` rate is the sole derived-rate instance.
- **Guide canned responses:** no invented numbers or projections in `guideAnswer` fallbacks.

## Bottom line

One real violation, harshly stated: **the app tells users they earn "≈785/min" selling their gold — a number no terms page states, computed by dividing their own asset value by shipping time.** Remove it. Everything else in the forbidden-numbers list is clean.
