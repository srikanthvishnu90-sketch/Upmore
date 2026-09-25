# Agent E4-v2 — Earn Pre-flight EXHAUSTIVE: HARSH TEST REPORT

**Verdict: FAIL** (pre-flight exists and gates every walkthrough start; 3 of the 4 required disclosures are missing or incomplete, abandonment assurance is a blanket claim that is false for high-consequence routes, plus a time-rendering bug on routes with missing time data)

**Tested:** commit `b73da4f` (cache stamp `upmore-b73da4f`), built `index.html` — the pre-flight string `quick pre-flight` confirmed present in the deployed build artifact (grep count 1 in `index.html` at commit b73da4f). Behavioral claims are from exact reconstruction of the `startWalkthrough()` pre-flight string against catalog data for 25 sampled routes (script-level simulation of the template literal, not a clicked session — no live-browser lane available to this lane; parent must confirm the visual render).

**Method:** `startWalkthrough(id)` (`src/upmore-app-template.html:1585`) is the single funnel for all 9 walkthrough entry points (app cards L1564, queue CTA L1826, resume L1872, guide L2444/L3032, agent actions L2981/2986/2991, data-walk buttons L3120). On fresh start (`i === 0`) it renders one fixed pre-flight string then `return`s before `renderWalkStep` — step 1 is unreachable without tapping "Start walkthrough". Resume skips it (correct).

**Sample:** 25 routes from the 1644 walkable (lane Standard, status ≠ retired, has steps): 6 bank-bonus (high consequence), 4 referral/credit, 2 gig/sell, plus 13 random stratified (missing costs ×287 routes, missing time ×258 routes). 10 assertions per route + 5 global code-path assertions = **255 total**.

## SCOREBOARD: 255 assertions — 149 PASS / 106 FAIL

| Disclosure | Pass | Fail | Result |
|---|---|---|---|
| 1. Exact reward + when it arrives | 0/25 | 25/25 | **TOTAL FAIL** — neither `reward` nor `when_cash_arrives` appears in the pre-flight string at all |
| 2. Exact requirements (verbatim) | 50/50 | 0/50 | PASS — `**They'll ask for:**` label present on all 25; requirements rendered verbatim (unescaped) on all 25 |
| 3. The catch (honest downside) | 0/25 | 25/25 | **TOTAL FAIL** — `catches` field exists in catalog (1644/1644 routes populated) but is never used in pre-flight |
| 4. Abandonment assurance | 25/25 label present, **0/25 honest** | 25/25 | label renders; the assurance text is one blanket sentence on every route: "nothing is submitted until you complete the final step — you can abandon anytime with no penalty" |
| Provider name / time line present | 50/50 | 0/50 | PASS |
| Time line renders sane value | 23/25 | 2/25 | FAIL: routes with no time data render **"≈None min active"** (R7930 Moneylion, R0139 MyPoints) |

## Per-route fail detail (sample)

- **D1 reward/absent:** every route. Examples — R0069 Old National Bank ($300 bonus): pre-flight says nothing about the $300 or that the bonus is credited "between the 121st and 140th day" (catalog `when_cash_arrives`). R8121 Sermo (doctor surveys): no mention of the honorarium or that it pays 1–2 days after study completion. R6610 PlaybookUX: no mention of "$30 / 30 minute" or PayPal within 8 days. The card shows reward, but the pre-flight — the last screen before commitment — restates neither amount nor timing. Spec calls pre-flight a money/time disclosure; omitting the exact reward undermines the whole point.
- **D3 catch/absent:** every route. Examples — R0032 Wealthfront (`catches`: "$500 of your own money parked for 30 days" — actually this surfaces under Cost, but the explicit catches content is dropped), R1876 Residential (catch: "$150 early cancellation fee; 12-month term"), R0466 GoCashBack (catch: "ad blockers can break attribution; merchant-side delays"). The honest downside exists in data and is hidden.
- **D4 blanket abandonment (the worst finding):** identical sentence on all 25 routes, and it is false for the highest-stakes routes. Bank-bonus routes (R0069, R3203 Wintrust, R2411 Mypcfcu, R3832 Neighborhood CU): an intermediate step IS opening a bank account — a ChexSystems hard inquiry, a real account footprint, potential minimum-balance/membership consequences. "Nothing is submitted until you complete the final step — no penalty" tells the user there is no footprint before step N, which is verifiably untrue the moment they open the account at step 2 or 3. R1876 Residential ($150 early cancellation fee): if they sign at a mid-step, abandonment has a real penalty. The assurance must be per-route ("if you stop after step N, X already happened") or scoped to what Upmore itself does ("Upmore never submits anything for you — anything you do on the provider's site is real and irreversible").
- **A3 time bug:** R7930 and R0139 render "≈None min active" because `time_min_minutes`/`time_max_minutes` are null for 258/1644 routes and the template interpolates them raw. A nonsense line in the commitment screen.

## Global code-path failures

- **G2 — no failure-risks disclosure.** The spec mandates pre-flight disclose "money/time cost, **failure risks**, requested personal data, and consequences of abandonment." The string has Cost, Time, data, abandonment — failure risks (not selected, reward denied, account closed for bonus abuse, screener rejection) appear nowhere. The code comment even says "disclose cost, risks, data, abandonment" — the comment promises what the string doesn't deliver. Confirmed: F1 from v1 is still open.
- **G3 — `catches` unused in pre-flight** (code grep: `catches` never referenced in the startWalkthrough pre-flight block).
- **G4 — `reward`/`when_cash_arrives` unused in pre-flight** (code grep: neither referenced in the pre-flight block).
- **G5 — no escaping:** the pre-flight interpolates `r.provider`, `costs`, `data` raw into `addAI()`; the resume branch two lines below uses `esc(r.provider)`. Same function, two conventions. Catalog data is operator-owned so risk is low, but the convention exists and this code ignores it. Confirmed: F4 from v1 still open.

## What genuinely passes (harsh credit where due)

1. Pre-flight fires BEFORE step 1 on every entry path — 9 call sites enumerated, all funnel through `startWalkthrough`; `renderWalkStep` is unreachable on a fresh start until the CTA is tapped. No bypass.
2. D2 requirements: verbatim on 25/25 — no paraphrase, no truncation, full list text rendered.
3. Cost disclosure on 1357/1644 routes with data; fallback "No upfront cost stated." on the other 287 — however, this conflates "verified free" with "we don't know" (v1 F3, still open).

## Required fixes before PASS

1. Add reward + when-it-arrives to the pre-flight (exact terms-stated amount, exact arrival window). Restating the card's money facts at the commitment point is the minimum honest disclosure.
2. Add the explicit catch / failure-risks block from `catches` data (per-route where populated; honest "not specified in terms" fallback where it isn't — never silence).
3. Replace the blanket "no penalty" sentence with per-route-accurate abandonment consequences (e.g., for bank routes: "stopping after you open the account leaves the account and its ChexSystems inquiry on your record"), or scope to Upmore's own non-involvement.
4. Fix the time fallback: render "time not stated" instead of "≈None min active" for the 258 routes with null time data.
5. Use `esc()` consistently in the pre-flight interpolations.
6. Distinguish "verified no cost" from "cost not stated" in the fallback.
7. Live visual confirmation in production (Home → queue → earn card → "Walk me through it" → pre-flight) — not done in this lane.

**Note on scope:** 25/1644 walkable routes were simulated (1.5%); the failures are structural (the string is route-invariant except interpolated fields), so they apply to all routes by construction — the per-route failures listed above are representative, not exhaustive.
