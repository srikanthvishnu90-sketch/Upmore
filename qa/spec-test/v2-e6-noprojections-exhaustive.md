# Agent E6-v2 — Earn: No Projections EXHAUSTIVE
**Verdict: FAIL** — 3 distinct spec violations live in production, 98 assertions checked across 26 routes.

**Method:** Repo template `src/upmore-app-template.html` + served production HTML fetched 2026-09-25 ~04:50 UTC from `https://upmore-srikanthvishnu90-sketchs-projects.vercel.app/`. Served `sw.js` stamp is `upmore-8b52c95` = repo HEAD `b73da4f` — production matches the tested build. Catalog: 1,990 routes in `src/data/upmore-data.json`. All banned-string greps were run against the served HTML (4.2 MB, code + catalog blob), with catalog-terms hits distinguished from UI-generated copy.

**Notation:** ✅ PASS · ❌ FAIL · ⚠️ FLAG (spec-adjacent / needs owner call) · ℹ️ observation.

---

## A. Global UI-string assertions (G1–G20)

| # | Assertion | Result | Evidence |
|---|-----------|--------|----------|
| G1 | No "you'll earn $X" as Upmore-generated copy | ✅ | 51 matches in served HTML, all inside catalog `reward`/`what`/`catches` provider-terms text (e.g. Robinhood R0328 "You'll earn a bonus stock reward…"). Zero in UI template code. Terms-stated, not projected. |
| G2 | No "potential earnings" | ✅ | 0 matches anywhere. |
| G3 | No "projected" | ✅ | 0 matches anywhere. |
| G4 | No "fast cash" as Upmore copy | ✅ | 4 matches, all inside catalog provider text (SellCell R1599-family "Fast Cash, Never Store Credit", Back Market). None in UI copy. |
| G5 | No derived /hour or /hr rates | ✅ | 0 UI-generated. 230 "hourly"/"per hour" hits are all provider-advertised rates in catalog fields (`reward`, `what_gets_accepted`, `when_cash_arrives`) — terms-stated, e.g. "$75 to $200+ per hour per the listing". |
| G6 | No derived per-minute rate | ❌ | `earnLine()` (template L1105–1114) still computes `rt = …/min` from `earn_ratio` (avg payout ÷ avg time). Served production HTML contains the exact code (`earn_ratio >= 100 ? … /min`). **This is the v1 E6 FAIL, never fixed — now re-confirmed live on the current build.** Renders on every Explore row and every walkthrough intro, e.g. JM Bullion `≈$1,000–$50,000 · ≈20–45 min · ≈785/min`. |
| G7 | Never publicly promise "make extra money" | ❌ | Welcome screen headline, live in production: **"Real ways to make extra money. One at a time."** (served HTML L14; template L635). The spec's hard rule: *Never publicly promise "make extra money."* |
| G8 | Class badge is exactly one of Fixed reward / Paid-if-selected / Variable / Non-cash | ❌ | Catalog's only two `earnings_class` values are **"Count only actual received cash"** (1,967 routes) and **"Speculative — $0 until withdrawn"** (23 routes). The queue card renders `r.earnings_class` verbatim into the badge (`<span class="ebadge">`). No route on the queue carries any of the four spec classes; the `"Fixed reward"` fallback in code never fires because the field is always populated. |
| G9 | Queue headline never invents a single number | ✅ | `sub: routeMeta(r)` renders `r.reward` verbatim (terms text) + `time_to_first`. No number is composed by the UI here. |
| G10 | "Up to $X" as headline | ✅ w/ note | 360 routes' reward text contains "up to" (e.g. R5446 "Earn up to $250,000 USD in bug bounty awards"); rendered verbatim as provider terms, not as Upmore's projection. Fair under "exact terms-stated reward". Note: a user skimming still sees "up to $250,000" as the headline figure — but the spec permits terms-stated phrasing. |
| G11 | Variable rewards show a range, not a single number | ✅ | `earnLine()` shows `≈$min–$max` whenever `payout_min ≠ payout_max` (544 routes). Single `≈$X` only when min == max. No variable route collapses to one number. |
| G12 | Pre-flight/walkthrough completion states payout honestly | ✅ | Walkthrough end: `The payout: ${r.reward} — ${r.payout_timing}` — verbatim terms text, no added projection. Pre-flight `**Cost:**` uses per-route cost disclosure. |
| G13 | Payout timing honest (no "fast cash" framing by Upmore) | ✅ | Guide canned answer (L2781): "Payout timing is per-offer — some pay in days, bank bonuses usually take 2–3 months." Bank cards show e.g. "Bonus credited between the 121st and 140th day" (R0069). Honest, dated, unhurried. |
| G14 | No multi-route summed/route-total projections | ✅ | No code sums routes into "you could earn $X total". The queue "why" line (`$500 × 70% × 1 / 30 min`) decomposes the spec-mandated ranking formula (dollars × confidence × urgency ÷ effort) — required by the spec's own queue design, not a projection. |
| G15 | No annualized/combined/rounded rewards on Earn | ✅ | `/yr` figures appear only on Cancel cards (Cancel spec requires labeled 12-month projection). Earn-side `/min` is the sole derived-rate instance (G6). |
| G16 | No fake scarcity / countdowns | ✅ | 0 matches for countdown/hurry/"only N left"/"ending soon"/"last chance"/"act now"/"limited time" in UI code. |
| G17 | "Guaranteed" never used as a payout promise | ✅ | Matches are the Terms disclaimer ("not a guarantee — payouts come from third-party companies") — a disclaimer, not a promise. |
| G18 | No "you could earn" / "estimated total" UI copy | ✅ | 0 matches. |
| G19 | "Reward:" label format | ℹ️ | The task brief expects `Reward: $X`; the app has **zero** "Reward:" labels — reward renders as the card's unlabeled subtitle (`routeMeta`) and 8-element card meta line. The spec itself doesn't mandate the literal label, so not a FAIL; but the mandated element #2 "Exact terms-stated reward" is present in content, not in label. |
| G20 | `≈` prefix on earnLine ranges | ℹ️ | Ranges render as `≈$min–$max`. The `≈` is a hedge, not an invented number; the bounds are catalog (terms-derived) values. Tolerable, but a maximally strict reading of "never a projection" would drop the `≈`. |

**Global: 14 ✅ / 3 ❌ / 3 ℹ️**

---

## B. Route-level assertions (26 routes × 3 = 78)

For each route: (a) headline shows terms-stated reward, never a projected single number; (b) range-vs-single rendering matches data honestly; (c) class/timing honesty (no implied guarantee).

| # | Route | (a) Reward representation | (b) Range/single | (c) Class & timing honesty |
|---|-------|---------------------------|------------------|---------------------------|
| R1 | R8323 JM Bullion — sell your gold | ✅ range `≈$1,000–$50,000`, no single headline | ✅ min≠max → range | ⚠️ The "$1,000–$50,000" is the **value of the user's own gold**, not earnings; paired with `≈785/min` (G6) it reads as "$785 of earnings per minute." Required-asset liquidation must stay separate per spec. ⚠️ FLAG |
| R2 | R5446 Microsoft bug bounty — up to $250,000 | ✅ verbatim terms text; earnLine `≈$0–$250,000` (range, not a $250k promise) | ✅ min≠max → range | ⚠️ Bug bounties are **paid-if-selected** (acceptance-dependent) but no such class exists in the badge system (G8) — the card implies it's ordinary cash work. ⚠️ FLAG |
| R3 | R0328 Robinhood referral — "You'll earn a bonus stock reward" | ✅ terms-verbatim (the "you'll earn" is the provider's, not Upmore's) | ✅ `≈$0–$15,000` range | ⚠️ Pays in **stock** (non-cash/acceptance-dependent); badge says "Count only actual received cash." Spec keeps non-cash and acceptance-dependent work separate. ⚠️ FLAG |
| R4 | R0018 SoFi Invest — 1% ACAT match up to $50,000 | ✅ verbatim; earnLine `≈$0–$50,000` | ✅ range | ⚠️ Requires moving existing investments — capital-gated (E1 territory); as a no-projection matter the range is honest. |
| R5 | R0780 Mass Save heat-pump — $16,000 | ✅ single fixed `≈$16,000` | ✅ min==max → single | ✅ timing honestly states "Mass Save does not publish a payout timeline for this incentive." |
| R6 | R0840 Tradestation referral — up to $5,000 | ✅ verbatim "Up to $5,000 cash back…"; earnLine `≈$0–$5,000` | ✅ range | ✅ timing "Paid per the promotion's payout schedule" — no speed claim. |
| R7 | R0771 Mass Save partial — up to $8,500 | ✅ verbatim; `≈$0–$8,500` | ✅ range | ✅ same honest no-timeline disclosure as R5. |
| R8 | R0845 Txu referral — $50 bill credit, up to $2,000/yr | ✅ verbatim | ✅ `≈$0–$2,000` range | ⚠️ **Bill credits are non-cash**, but the route sits in the Earn queue badged "Count only actual received cash." Spec: non-cash kept separate from extractable cash. ⚠️ FLAG |
| R9 | R3570 Sunrun referral — "Earn $1,000*" | ✅ verbatim provider text incl. asterisk | ✅ min==max → `≈$1,000` | ⚠️ Referral = acceptance-dependent (friend must buy solar); no Paid-if-selected badge exists (G8). |
| R10 | R7019 CarMax — sell your car | ✅ verbatim ("Get a real offer in minutes…"); earnLine `≈$0–$15,000` | ✅ range | ⚠️ Own-car sale value framed as an Earn figure — required-asset liquidation, same issue as R1. |
| R11 | R7020 Carvana — sell your car | ✅ verbatim; `≈$0–$15,000` | ✅ range | ⚠️ same as R10. Timing honest ("Average complete sale 3-10 days"). |
| R12 | R7021 AutoNation — sell your car | ✅ verbatim; `≈$0–$15,000` | ✅ range | ⚠️ same as R10. |
| R13 | R0069 Old National Bank — $300 bonus | ✅ fixed `≈$300` | ✅ single | ✅ timing exact: "Bonus credited between the 121st and 140th day after account opening." Model honest-payout-timing behavior. |
| R14 | R0071 BOK Financial — $450 bonus | ✅ fixed `≈$450` | ✅ single | ✅ timing "Evaluated 90 days after account opening; bonus credited with[in]…" — honest. |
| R15 | R0633 Nymcu — $150/$250/$350 tiers | ✅ verbatim tier text | ✅ `≈$150–$350` range (tiered → range is the honest collapse) | ✅ timing "Paid per the official payout calendar (runs through 2027-04…)" — dated, honest. |
| R16 | R0264 Mavely creator referrals — commission | ✅ verbatim ("you get the full 10%") | ✅ `≈$4,000–$10,000` range | ⚠️ Referral/commission, acceptance-dependent; badge system can't express it (G8). |
| R17 | R8329 The Pro's Closet — sell your gear | ✅ verbatim; `≈$200–$5,000` | ✅ range | ⚠️ own-gear sale value as Earn figure (same as R1). |
| R18 | R7032 Bob's Watches — sell your watch | ✅ verbatim; `≈$0–$5,000` | ✅ range | ⚠️ own-watch sale value as Earn figure (same as R1). |
| R19 | R0031 Betterment — $100 bonus | ✅ fixed `≈$100` | ✅ single | ✅ timing dated: "$100 bonus paid on or around October 29, 2026." |
| R20 | R5538 Aepenergy referral — up to $1,000 bill credits | ✅ verbatim | ✅ `≈$25–$1,000` range | ⚠️ **Bill credits = non-cash**, badged "Count only actual received cash" (G8). Double violation of the non-cash separation rule. |
| R21 | R0026 E*TRADE — up to $1,000 by deposit tier | ✅ verbatim tier text; `≈$0–$1,000` | ✅ range | ✅ timing "Rewards paid within seven business days following the expir[ation period]" — honest. |
| R22 | R3365 Sfcu referral — $250–$750 | ✅ verbatim "bonuses between $250 and $750" | ✅ `≈$250–$750` range | ✅ matches the task brief's own example format. |
| R23 | R0569 Purduefed — $400 bonus | ✅ fixed `≈$400` | ✅ single | ✅ timing "Bonus paid within ten business days after all conditions are [met]." |
| R24 | R5785 Qtrade — 5% cash back tiers $50–$5,000 | ✅ verbatim tier text | ✅ `≈$50–$5,000` range | ✅ timing dated ("Open by Jan 5, 2027; fund by Feb 5, 2027"). |
| R25 | R0373 GitHub Student Pack — free tools/credits | ✅ verbatim; `≈$100` (min==max) | ✅ single | ⚠️ Non-cash (software credits, Copilot) with badge **"Speculative — $0 until withdrawn"** — the one class value that gestures at non-cash, but it's not the spec's "Non-cash" class and the wording implies a cash figure ($100) that will never be cash. ⚠️ FLAG |
| R26 | R0446 Google Opinion Rewards — up to $1.00 Play credit | ✅ verbatim; `≈$0–$1.00` | ✅ range | ⚠️ **Play Store credit = non-cash**, in the Earn queue badged "Count only actual received cash." Same separation violation as R8/R20. |

**Route-level: 78 assertions — 78 ✅ on (a)+(b) representation mechanics; 11 ⚠️ flags on (c) class/separation honesty, all downstream of the G8 class-badge failure and the asset-liquidation separation rule.**

Note on (c): none of the 26 routes shows a *projected* number — the flags are about *what kind* of value is framed as earnings (own-asset sale value, bill credits, stock, referral-gated payouts), which is the spec's "keep separate" rule rather than a projection per se. E7 (class badges) owns the primary fix.

---

## C. Totals

- **98 assertions: 92 ✅ PASS · 3 ❌ FAIL · 3 ℹ️ observations · 11 ⚠️ flags** (flags ride on the 26 route-level (c) checks; the mechanics themselves pass).
- The three FAILs are independent violations, all live in production on build `b73da4f`:
  1. **G6 — derived `≈785/min` rate still rendered** on Explore rows and walkthrough intros. V1 E6 reported this; the fix was never applied. Harshest instance: JM Bullion's own-asset sale value ÷ shipping time presented as earnings-per-minute.
  2. **G7 — public "make extra money" promise** on the Welcome screen headline.
  3. **G8 — class badge values are not the four spec classes**; 1,967 routes show "Count only actual received cash", 23 show "Speculative — $0 until withdrawn". The entire Fixed/Paid-if-selected/Variable/Non-cash distinction the spec requires is absent from the UI.

## Fixes required (no-projection scope)

1. Remove the `rt` (`/min`) segment from `earnLine()` — template L1112. The `≈$min–$max` and `≈A–B min` segments are terms-derived and may stay.
2. Rewrite the Welcome headline — it must not promise "make extra money" publicly.
3. Replace the `earnings_class` vocabulary with the four spec classes and backfill per route (or derive: single fixed payout → Fixed reward; payout_min≠payout_max or "up to" → Variable; referral/bounty/acceptance language → Paid-if-selected; cash_or_credit ≠ cash / credits/points/stock → Non-cash). The badge must render one of the four, nothing else.
4. Separation follow-through (E7/E1 territory but projection-adjacent): own-asset sale routes (R8323, R7019–R7021, R8329, R7032) and non-cash routes (R0845, R5538, R0328, R0373, R0446) must not be framed as extractable-cash earnings in Earn surfaces.

## What's genuinely clean

No projected totals, no invented single numbers for variable rewards (ranges render correctly on all 544 range routes), no "potential earnings"/"projected"/"fast cash" as Upmore copy, no derived hourly rates, no fake scarcity, no annualized Earn figures, honest payout timing throughout (bank bonuses at 2–3 months / exact day counts), pre-flight and walkthrough completion state verbatim terms, queue "why" line is the spec's own formula decomposition. The *mechanics* of no-projection are sound — the failures are a leftover derived-rate line, a marketing headline, and a badge vocabulary that never matched the spec.
