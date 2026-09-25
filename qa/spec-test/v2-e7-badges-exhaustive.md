# Agent E7-v2 (Earn: Class Badges EXHAUSTIVE) — HARSH REPORT

**Verdict: FAIL — critical, unchanged since v1**

**Method.** Static analysis of the template (`src/upmore-app-template.html`), the built bundle (`index.html`), the catalog (`src/data/upmore-data.json`), and the production-served bundle. As a subagent I have no live-browser capability; the badge render path is a single deterministic template literal, so the code-path evidence is conclusive. Production bundle verified byte-identical to local build (md5 `74132629406d80cbadc08cd5130db1c6` on both), and served `sw.js` stamp `upmore-8b52c95` matches local HEAD build — the tested code is exactly what production serves.

**Spec under test** (Doc 1, Earn): every route carries **exactly one** class badge, from the fixed set: **Fixed reward, Paid-if-selected, Variable, Non-cash**. No route without a badge; no route with two.

**Note on the task's badge list.** The task brief named "Fixed reward, Variable, Bank bonus, Cashback, etc." as the fixed set. That does not match the spec. "Bank bonus" and "Cashback" are catalog *category* names (75 categories exist), not classes. Judgment below is against the spec's four classes. (G9 confirms no category name leaks into any badge.)

---

## Headline results

| Scope | Assertions | Pass | Fail |
|---|---|---|---|
| Per-route (30 routes × 5) | 150 | 90 | 60 |
| Global | 15 | 10 | 5 |
| **Total** | **165** | **100** | **65** |

- **Badge spec-compliance: 0 / 1,990 routes (0%).** The v1 FAIL was not fixed.
- Badge *count* per card: exactly 1 everywhere — the only passing dimension.

## The defect (unchanged from v1)

`src/upmore-app-template.html:1974` is byte-identical to the v1 finding:

```js
const cls = r.earnings_class || "Fixed reward";
…
<span class="ebadge">${esc(cls)}</span>
```

It renders the raw catalog string verbatim. No `specClass()` mapping was implemented. Catalog `earnings_class` distribution (all 1,990 routes):

| Catalog value | Routes | In spec set? |
|---|---|---|
| `"Count only actual received cash"` | 1,967 | No |
| `"Speculative — $0 until withdrawn"` | 23 | No |

A user sees "Count only actual received cash" — an internal accounting note, meaningless as a class label — on every queue card. The `"Fixed reward"` fallback is dead code: 0 routes lack the field.

## Per-route assertions (30 routes, stratified across 25 categories + all 23 Restricted)

A1 = badge present (non-empty `earnings_class`) · A2 = single-valued (scalar, not list) · A3 = badge ∈ spec set · A4 = badge is a spec label, not an invented phrase · A5 = card renders exactly one `.ebadge` (static block analysis of the `earn8` render block: 1 `ebadge` span, 1 `vbadge` span)

| # | Route | Category | Rendered badge | Correct class¹ | A1 | A2 | A3 | A4 | A5 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | R0014 Kraken | Prediction Market | Speculative — $0 until withdrawn | Non-cash | ✅ | ✅ | ❌ | ❌ | ✅ |
| 2 | R0013 Coinbase Advanced | Prediction Market | Speculative — $0 until withdrawn | Non-cash | ✅ | ✅ | ❌ | ❌ | ✅ |
| 3 | R0373 GitHub Student Dev Pack | Student Program | Speculative — $0 until withdrawn | Non-cash | ✅ | ✅ | ❌ | ❌ | ✅ |
| 4 | R0012 Coinbase | Prediction Market | Speculative — $0 until withdrawn | Non-cash | ✅ | ✅ | ❌ | ❌ | ✅ |
| 5 | R0010 Smarkets | Prediction Market | Speculative — $0 until withdrawn | Non-cash | ✅ | ✅ | ❌ | ❌ | ✅ |
| 6 | R0273 Scale AI | AI Training | Count only actual received cash | Fixed reward | ✅ | ✅ | ❌ | ❌ | ✅ |
| 7 | R9103 Knowbility | Accessibility | Count only actual received cash | Variable | ✅ | ✅ | ❌ | ❌ | ✅ |
| 8 | R0330 Chime Referral | App Referral | Count only actual received cash | Fixed reward | ✅ | ✅ | ❌ | ❌ | ✅ |
| 9 | R3788 Axosbank | Bank Bonus | Count only actual received cash | Variable | ✅ | ✅ | ❌ | ❌ | ✅ |
| 10 | R0411 ErliBird | Beta Testing | Count only actual received cash | Fixed reward | ✅ | ✅ | ❌ | ❌ | ✅ |
| 11 | R0429 Meta Campus Ambassador | Brand Ambassador | Count only actual received cash | Fixed reward | ✅ | ✅ | ❌ | ❌ | ✅ |
| 12 | R1066 Sofi | Brokerage Promo | Count only actual received cash | Variable | ✅ | ✅ | ❌ | ❌ | ✅ |
| 13 | R4118 Key | Business Banking | Count only actual received cash | Fixed reward | ✅ | ✅ | ❌ | ❌ | ✅ |
| 14 | R1597 Buybackboss | Buyback | Count only actual received cash | Variable | ✅ | ✅ | ❌ | ❌ | ✅ |
| 15 | R7029 KEH Camera (mail-in) | Buyback/Resale | Count only actual received cash | Variable | ✅ | ✅ | ❌ | ❌ | ✅ |
| 16 | R9220 3PlayMedia | Captioning | Count only actual received cash | Variable | ✅ | ✅ | ❌ | ❌ | ✅ |
| 17 | R1851 Wrapify | Car Advertising | Count only actual received cash | Variable | ✅ | ✅ | ❌ | ❌ | ✅ |
| 18 | R5412 Card | Card Bonus | Count only actual received cash | Paid-if-selected | ✅ | ✅ | ❌ | ❌ | ✅ |
| 19 | R7302 Mr. Rebates | Cashback | Count only actual received cash | Fixed reward | ✅ | ✅ | ❌ | ❌ | ✅ |
| 20 | R0142 SendEarnings | Cashback/Shopping | Count only actual received cash | Fixed reward | ✅ | ✅ | ❌ | ❌ | ✅ |
| 21 | R3640 Fresnocountyca | Civic Pay | Count only actual received cash | Variable | ✅ | ✅ | ❌ | ❌ | ✅ |
| 22 | R4561 Cc | Clinical Trial | Count only actual received cash | Variable | ✅ | ✅ | ❌ | ❌ | ✅ |
| 23 | R8242 HackenProof | Code Bounties | Count only actual received cash | Paid-if-selected | ✅ | ✅ | ❌ | ❌ | ✅ |
| 24 | R3503 Zindi | Competition | Count only actual received cash | Variable | ✅ | ✅ | ❌ | ❌ | ✅ |
| 25 | R9100 WriterAccess | Content Writing | Count only actual received cash | Variable | ✅ | ✅ | ❌ | ❌ | ✅ |
| 26 | R0684 Capital One, N.A. | Credit Card Bonus | Count only actual received cash | Paid-if-selected | ✅ | ✅ | ❌ | ❌ | ✅ |
| 27 | R0354 Gemini Crypto Earn | Crypto Reward | Count only actual received cash | Fixed reward | ✅ | ✅ | ❌ | ❌ | ✅ |
| 28 | R9222 Concentrix | Customer Service | Count only actual received cash | Variable | ✅ | ✅ | ❌ | ❌ | ✅ |
| 29 | R9183 Alignerr | Data Annotation | Count only actual received cash | Variable | ✅ | ✅ | ❌ | ❌ | ✅ |
| 30 | R7609 Lyft | Delivery | Count only actual received cash | Variable | ✅ | ✅ | ❌ | ❌ | ✅ |

¹ "Correct class" uses the mapping proposed in the v1 report (Restricted credit → Non-cash; payout_min≠payout_max → Variable; selection/acceptance language in requirements → Paid-if-selected; else Fixed reward). It is shown to demonstrate *how* wrong the badge is per route; the pass/fail judgment rests only on A3/A4 (membership in the spec's fixed set), which is definitive regardless of mapping details.

**Per-route totals: 90 pass / 60 fail.** Every route passes A1/A2/A5 (badge exists, single, one per card) and fails A3/A4 (0/30 spec-compliant).

## Global assertions

| # | Check | Result |
|---|---|---|
| G1 | Exactly one class-badge render site in template (`:1974` → `:1978`) | ✅ |
| G2 | Exactly one render site in built `index.html` (3 `ebadge` hits = 2 CSS + 1 render) | ✅ |
| G3 | Local `index.html` byte-identical to production-served bundle (md5 match) | ✅ |
| G4 | Served `sw.js` stamp `upmore-8b52c95` matches local HEAD build | ✅ |
| G5 | Catalog badge values in spec set: **0/1,990** | ❌ |
| G6 | Routes missing `earnings_class` (fallback reachability): 0 | ✅ |
| G7 | Routes with multi-valued `earnings_class`: 0 | ✅ |
| G8 | Explore/detail view renders no class badge (no second, conflicting badge surface) | ✅ |
| G9 | "Bank bonus"/"Cashback"/category names rendered as badge text: none | ✅ |
| G10 | `cash_or_credit = "Restricted credit"` routes (23) carry **Non-cash**: 0/23 | ❌ |
| G11 | `payout_min ≠ payout_max` routes (544) carry **Variable**: 0/544 | ❌ |
| G12 | Routes with selection/acceptance language (143, heuristic) carry **Paid-if-selected**: 0/143 | ❌ |
| G13 | Queue card carries exactly one *class* badge (the adjacent `.vbadge` pill is the verification-state element, spec card element #8 — see nuance below) | ✅ |
| G14 | v1 required fix (`specClass()` catalog→spec mapping) implemented | ❌ — line 1974 unchanged |
| G15 | No alternate class fields or badge render paths (`category` + `earnings_class` are the only class-ish fields; `earnings_class` referenced once) | ✅ |

**Global totals: 10 pass / 5 fail.**

## Harsh notes

1. **The v1 FAIL was ignored, not fixed.** The v1 report prescribed the exact mapping; the code at `:1974` is untouched. This is a repeat finding, which is worse than a new one.
2. **Misleading precision.** 544 routes display a variable payout range via `earnLine()` (`≈$min–$max`) while their badge reads "Count only actual received cash" — the card's number says variable, the card's badge says fixed-ish. The class signal contradicts the reward signal on more than a quarter of the catalog.
3. **Paid-if-selected is invisible.** Spec: "the card must say so plainly." 143 routes carry acceptance/selection language in their requirements; zero cards say so. A user cannot distinguish guaranteed rewards from maybe-rewards.
4. **Non-cash has no representation.** The 23 restricted-credit routes sit in the `Restricted` lane and never enter the queue — exclusion satisfies "never lead the queue," but no Earn surface anywhere shows a `Non-cash` badge, so the class exists in spec only.
5. **Nuance — two pills per card (G13).** Every earn card renders two pill-styled spans: `.ebadge` (class) and `.vbadge` (verification state: confirmed/unverified/stale/expired/retired). Under a hyper-literal "not 2 badges" reading this flags; under the spec it is compliant because the 8-element card mandates both a class badge (element #3) and verification age/date (element #8). Recorded as PASS with the ambiguity noted — the verification pill is not a second *class* badge.
6. **No invented category badges.** Despite the task brief's loose list, no route renders "Bank bonus," "Cashback," or any other category name as a badge. The failure is the opposite: badges are non-spec internal phrases.

## Required fix (restated from v1, still unapplied)

Implement `specClass(route)` and render it instead of the raw catalog string at `:1974`:
- `cash_or_credit === "Restricted credit"` → `Non-cash`
- `payout_min !== payout_max` (or reward text matches /up to|varies/i) → `Variable`
- requirements/what matches /selected|chosen|approved|accepted/i → `Paid-if-selected`
- else → `Fixed reward`

Then re-run this exact 165-assertion battery against the redeployed identical commit.

## Production evidence

- `https://upmore-srikanthvishnu90-sketchs-projects.vercel.app/` → HTTP 200
- Served `index.html` md5 `74132629406d80cbadc08cd5130db1c6` = local built `index.html`
- Served `sw.js` = `upmore-8b52c95`, matching local HEAD (`b73da4f` rebuild stamping `8b52c95`)
- Render code in served bundle: `r.earnings_class || "Fixed reward"` — identical to local
