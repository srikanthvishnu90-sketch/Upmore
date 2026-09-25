# Agent C1-v2 Report: Cancel Recurrence Detection — EXHAUSTIVE (149 assertions)

**Verdict: CONDITIONAL PASS** — the deterministic detector implements the spec's core algorithm correctly (146/149 assertions pass). The 3 failures share one root cause: **no merchant alias table**, which the spec explicitly requires (step 1: "map known aliases to a canonical merchant id"; build order days 1-4). Two further spec-mandated mitigations are missing and documented below as gaps, not counted failures.

**How tested:** No live browser available to this agent. `normalizeMerchant` + `detectRecurrence` were extracted **verbatim** from `src/upmore-app-template.html` (function-source slice, executed via `new Function`) and run in Node against 11 synthetic transaction sets. Byte-identity confirmed: the detector in the template is **byte-identical** to the detector in the built `index.html`.

**Deployment evidence (which build this reflects):**
- Local HEAD `b73da4fa157033da2722332e8510edd6c297d477` (2026-09-24 23:43 CDT), `main` in sync with `origin/main`; app code (template + built `index.html`) committed, no uncommitted app-code changes (only `sw.js` working-tree build noise, not app logic).
- Production `sw.js` serves `CACHE = "upmore-8b52c95"`, matching HEAD's committed stamp → production is serving the HEAD build that was tested.
- `sw.js` uses network-first for `/` and `index.html`, so the served app shell is the latest deploy.

## Spec algorithm checklist (Doc 2, "The recurrence detector")

| Spec step | Implementation | Status |
|---|---|---|
| 1. Normalise (strip SQ */PAYPAL */TST* prefixes, store numbers, trailing refs, lowercase) | `normalizeMerchant()` — prefixes + `\s+#?\d+.*$` + `[^a-z0-9]` collapse | ✅ implemented |
| 1b. Map known aliases to a canonical merchant id | **missing entirely** — no alias table anywhere in the codebase | ❌ FAIL (A122–A124) |
| 2. Group by canonical merchant | `t.merchant_id \|\| normalizeMerchant(t.merchant_raw)` | ✅ |
| 3. Cluster by amount within 5% or $1 (`Math.max`) | `Math.abs(c.amount - amt) <= Math.max(c.amount*0.05, 1)` — greedy first-fit | ✅ |
| 4. Compute gaps between consecutive dates | `Math.round(diff/864e5)` | ✅ |
| 5. Bands: weekly 6–8, biweekly 13–15, monthly 28–31, quarterly 88–92, annual 360–370 | exact match | ✅ (40 boundary assertions) |
| 6. Emit at ≥2 occurrences, ≥75% gaps in one band | `consistency < 0.75 → return` | ✅ |
| 7. Confidence: 0.6 (n=2), 0.8 (n=3), 0.95 (n≥4) | exact match | ✅ |

## Results summary

| Section | Assertions | Pass |
|---|---|---|
| R1 five merchants (Netflix, Spotify, ComEd, AT&T, Planet Fitness) | 50 | 50 |
| R2 interval band boundaries (18 gap values) | 40 | 40 |
| R3 75% consistency threshold edges (75% / 66.7% / 50% / 100%) | 8 | 8 |
| R4 false positives (irregular merchants) | 8 | 8 |
| R5 exclusions (pending, transfers, credits) | 6 | 6 |
| R6 amount clustering (5%/$1 rule, price rises) | 9 | 9 |
| R7 merchant normalization / aliasing | 8 | 5 |
| R8 all interval types (weekly/biweekly/quarterly/annual) | 13 | 13 |
| R9 next_date arithmetic | 4 | 4 |
| R10 merchant_id override | 1 | 1 |
| R11 degenerate inputs | 2 | 2 |
| **Total** | **149** | **146** |

## Per-assertion detail

### R1 five merchants

| # | Assertion | Result | Actual |
|---|-----------|--------|--------|
| A001 | netflix: detected | ✅ PASS | `{"merchant_id":"netflix","merchant_raw":"Netflix","amount":15.99,"interval":"monthly","...` |
| A002 | netflix: interval==="monthly" | ✅ PASS | `monthly` |
| A003 | netflix: confidence>=0.8 | ✅ PASS | `0.95` |
| A004 | netflix: confidence exact 0.95 | ✅ PASS | `0.95` |
| A005 | netflix: occurrences==5 | ✅ PASS | `5` |
| A006 | netflix: amount==15.99 | ✅ PASS | `15.99` |
| A007 | netflix: next_date==2026-10-11 | ✅ PASS | `2026-10-11` |
| A008 | spotify: detected | ✅ PASS | `{"merchant_id":"spotify","merchant_raw":"Spotify","amount":10.99,"interval":"monthly","...` |
| A009 | spotify: interval==="monthly" | ✅ PASS | `monthly` |
| A010 | spotify: confidence>=0.8 | ✅ PASS | `0.8` |
| A011 | spotify: confidence exact 0.8 | ✅ PASS | `0.8` |
| A012 | spotify: occurrences==3 | ✅ PASS | `3` |
| A013 | spotify: amount==10.99 | ✅ PASS | `10.99` |
| A014 | spotify: next_date==2026-09-30 | ✅ PASS | `2026-09-30` |
| A015 | comed: detected | ✅ PASS | `{"merchant_id":"comed","merchant_raw":"ComEd","amount":85.42,"interval":"monthly","conf...` |
| A016 | comed: interval==="monthly" | ✅ PASS | `monthly` |
| A017 | comed: confidence>=0.8 | ✅ PASS | `0.95` |
| A018 | comed: confidence exact 0.95 | ✅ PASS | `0.95` |
| A019 | comed: occurrences==4 | ✅ PASS | `4` |
| A020 | comed: amount==85.42 | ✅ PASS | `85.42` |
| A021 | comed: next_date==2026-10-07 | ✅ PASS | `2026-10-07` |
| A022 | at t: detected | ✅ PASS | `{"merchant_id":"at t","merchant_raw":"AT&T","amount":72,"interval":"monthly","confidenc...` |
| A023 | at t: interval==="monthly" | ✅ PASS | `monthly` |
| A024 | at t: confidence>=0.8 | ✅ PASS | `0.8` |
| A025 | at t: confidence exact 0.8 | ✅ PASS | `0.8` |
| A026 | at t: occurrences==3 | ✅ PASS | `3` |
| A027 | at t: amount==72 | ✅ PASS | `72` |
| A028 | at t: next_date==2026-10-02 | ✅ PASS | `2026-10-02` |
| A029 | planet fitness: detected | ✅ PASS | `{"merchant_id":"planet fitness","merchant_raw":"Planet Fitness","amount":24.99,"interva...` |
| A030 | planet fitness: interval==="monthly" | ✅ PASS | `monthly` |
| A031 | planet fitness: confidence>=0.8 | ✅ PASS | `0.95` |
| A032 | planet fitness: confidence exact 0.95 | ✅ PASS | `0.95` |
| A033 | planet fitness: occurrences==5 | ✅ PASS | `5` |
| A034 | planet fitness: amount==24.99 | ✅ PASS | `24.99` |
| A035 | planet fitness: next_date==2026-10-16 | ✅ PASS | `2026-10-16` |
| A036 | netflix: gap 29d within 28..31 | ✅ PASS | `29` |
| A037 | netflix: gap 30d within 28..31 | ✅ PASS | `30` |
| A038 | netflix: gap 30d within 28..31 | ✅ PASS | `30` |
| A039 | netflix: gap 30d within 28..31 | ✅ PASS | `30` |
| A040 | spotify: gap 29d within 28..31 | ✅ PASS | `29` |
| A041 | spotify: gap 30d within 28..31 | ✅ PASS | `30` |
| A042 | comed: gap 29d within 28..31 | ✅ PASS | `29` |
| A043 | comed: gap 30d within 28..31 | ✅ PASS | `30` |
| A044 | comed: gap 30d within 28..31 | ✅ PASS | `30` |
| A045 | at t: gap 29d within 28..31 | ✅ PASS | `29` |
| A046 | at t: gap 30d within 28..31 | ✅ PASS | `30` |
| A047 | planet fitness: gap 28d within 28..31 | ✅ PASS | `28` |
| A048 | planet fitness: gap 31d within 28..31 | ✅ PASS | `31` |
| A049 | planet fitness: gap 30d within 28..31 | ✅ PASS | `30` |
| A050 | planet fitness: gap 30d within 28..31 | ✅ PASS | `30` |

### R2 band boundaries

| # | Assertion | Result | Actual |
|---|-----------|--------|--------|
| A051 | gap→monthly (b28): detected | ✅ PASS | `{"merchant_id":"b28","merchant_raw":"b28","amount":10,"interval":"monthly","confidence"...` |
| A052 | gap→monthly (b28): interval | ✅ PASS | `monthly` |
| A053 | gap→monthly (b28): confidence 0.6 (n=2) | ✅ PASS | `0.6` |
| A054 | gap→monthly (b31): detected | ✅ PASS | `{"merchant_id":"b31","merchant_raw":"b31","amount":10,"interval":"monthly","confidence"...` |
| A055 | gap→monthly (b31): interval | ✅ PASS | `monthly` |
| A056 | gap→monthly (b31): confidence 0.6 (n=2) | ✅ PASS | `0.6` |
| A057 | gap→weekly (b06): detected | ✅ PASS | `{"merchant_id":"b06","merchant_raw":"b06","amount":10,"interval":"weekly","confidence":...` |
| A058 | gap→weekly (b06): interval | ✅ PASS | `weekly` |
| A059 | gap→weekly (b06): confidence 0.6 (n=2) | ✅ PASS | `0.6` |
| A060 | gap→biweekly (b13): detected | ✅ PASS | `{"merchant_id":"b13","merchant_raw":"b13","amount":10,"interval":"biweekly","confidence...` |
| A061 | gap→biweekly (b13): interval | ✅ PASS | `biweekly` |
| A062 | gap→biweekly (b13): confidence 0.6 (n=2) | ✅ PASS | `0.6` |
| A063 | gap→biweekly (b15): detected | ✅ PASS | `{"merchant_id":"b15","merchant_raw":"b15","amount":10,"interval":"biweekly","confidence...` |
| A064 | gap→biweekly (b15): interval | ✅ PASS | `biweekly` |
| A065 | gap→biweekly (b15): confidence 0.6 (n=2) | ✅ PASS | `0.6` |
| A066 | gap→quarterly (b88): detected | ✅ PASS | `{"merchant_id":"b88","merchant_raw":"b88","amount":10,"interval":"quarterly","confidenc...` |
| A067 | gap→quarterly (b88): interval | ✅ PASS | `quarterly` |
| A068 | gap→quarterly (b88): confidence 0.6 (n=2) | ✅ PASS | `0.6` |
| A069 | gap→quarterly (b92): detected | ✅ PASS | `{"merchant_id":"b92","merchant_raw":"b92","amount":10,"interval":"quarterly","confidenc...` |
| A070 | gap→quarterly (b92): interval | ✅ PASS | `quarterly` |
| A071 | gap→quarterly (b92): confidence 0.6 (n=2) | ✅ PASS | `0.6` |
| A072 | gap→annual (b360): detected | ✅ PASS | `{"merchant_id":"b360","merchant_raw":"b360","amount":10,"interval":"annual","confidence...` |
| A073 | gap→annual (b360): interval | ✅ PASS | `annual` |
| A074 | gap→annual (b360): confidence 0.6 (n=2) | ✅ PASS | `0.6` |
| A075 | gap→annual (b370): detected | ✅ PASS | `{"merchant_id":"b370","merchant_raw":"b370","amount":10,"interval":"annual","confidence...` |
| A076 | gap→annual (b370): interval | ✅ PASS | `annual` |
| A077 | gap→annual (b370): confidence 0.6 (n=2) | ✅ PASS | `0.6` |
| A078 | gap→weekly (b08): detected | ✅ PASS | `{"merchant_id":"b08","merchant_raw":"b08","amount":10,"interval":"weekly","confidence":...` |
| A079 | gap→weekly (b08): interval | ✅ PASS | `weekly` |
| A080 | gap→weekly (b08): confidence 0.6 (n=2) | ✅ PASS | `0.6` |
| A081 | gap→biweekly (b14): detected | ✅ PASS | `{"merchant_id":"b14","merchant_raw":"b14","amount":10,"interval":"biweekly","confidence...` |
| A082 | gap→biweekly (b14): interval | ✅ PASS | `biweekly` |
| A083 | gap→biweekly (b14): confidence 0.6 (n=2) | ✅ PASS | `0.6` |
| A084 | out-of-band (b27): NOT detected | ✅ PASS | `absent` |
| A085 | out-of-band (b32): NOT detected | ✅ PASS | `absent` |
| A086 | out-of-band (b05): NOT detected | ✅ PASS | `absent` |
| A087 | out-of-band (b09): NOT detected | ✅ PASS | `absent` |
| A088 | out-of-band (b16): NOT detected | ✅ PASS | `absent` |
| A089 | out-of-band (b93): NOT detected | ✅ PASS | `absent` |
| A090 | out-of-band (b371): NOT detected | ✅ PASS | `absent` |

### R3 75pct threshold

| # | Assertion | Result | Actual |
|---|-----------|--------|--------|
| A091 | 3/4 gaps monthly (75%): emitted | ✅ PASS | `emitted` |
| A092 | 3/4 gaps monthly (75%): interval monthly | ✅ PASS | `monthly` |
| A093 | 3/4 gaps monthly (75%): confidence 0.95 (n=5) | ✅ PASS | `0.95` |
| A094 | 2/4 gaps monthly (50%): NOT emitted | ✅ PASS | `absent` |
| A095 | 2/3 gaps monthly (66.7%): NOT emitted | ✅ PASS | `absent` |
| A096 | 5/5 gaps monthly (100%): emitted | ✅ PASS | `emitted` |
| A097 | 5/5 gaps monthly (100%): interval monthly | ✅ PASS | `monthly` |
| A098 | 5/5 gaps monthly (100%): confidence 0.95 (n=6) | ✅ PASS | `0.95` |

### R4 false positives

| # | Assertion | Result | Actual |
|---|-----------|--------|--------|
| A099 | Amazon irregular amounts/dates: NOT detected | ✅ PASS | `absent` |
| A100 | GasStop same-amount irregular gaps: NOT detected | ✅ PASS | `absent` |
| A101 | MixedGaps (weekly/monthly 66.7%): NOT detected | ✅ PASS | `absent` |
| A102 | two txns gap 45d: NOT detected | ✅ PASS | `absent` |
| A103 | single txn: NOT detected | ✅ PASS | `absent` |
| A104 | same-day double (gap 0): NOT detected | ✅ PASS | `absent` |
| A105 | gaps 10/20/40 (no band): NOT detected | ✅ PASS | `absent` |
| A106 | PROBE coffee $6.50 weekly x4: code detects weekly (spec category-plausibility gap) | ✅ PASS | `{"merchant_id":"blue bottle","merchant_raw":"Blue Bottle","amount":6.5,"interval":"week...` |

### R5 exclusions

| # | Assertion | Result | Actual |
|---|-----------|--------|--------|
| A107 | pending-only merchant: NOT detected | ✅ PASS | `absent` |
| A108 | 2 posted + 1 pending: detected | ✅ PASS | `emitted` |
| A109 | 2 posted + 1 pending: occurrences==2 (pending excluded) | ✅ PASS | `2` |
| A110 | 2 posted + 1 pending: confidence==0.6 | ✅ PASS | `0.6` |
| A111 | recurring $500/mo transfers: NOT detected | ✅ PASS | `absent` |
| A112 | positive-amount (credit) only: NOT detected | ✅ PASS | `absent` |

### R6 clustering

| # | Assertion | Result | Actual |
|---|-----------|--------|--------|
| A113 | +3% price rise: one cluster, detected | ✅ PASS | `emitted` |
| A114 | +3% price rise: occurrences==4 | ✅ PASS | `4` |
| A115 | +3% price rise: confidence 0.95 | ✅ PASS | `0.95` |
| A116 | +25% price rise: splits into 2 clusters | ✅ PASS | `clusters=2` |
| A117 | +25% price rise: both monthly | ✅ PASS | `["monthly","monthly"]` |
| A118 | +25% price rise: both conf 0.6 (n=2 each) | ✅ PASS | `[0.6,0.6]` |
| A119 | $5.00 vs $6.00 (diff exactly $1): same cluster n=2 | ✅ PASS | `occ=2` |
| A120 | $5.00 vs $6.01 (diff $1.01): split, NOT detected | ✅ PASS | `absent` |
| A121 | utility variable amounts (80/95/70/88): NOT detected (known spec limitation) | ✅ PASS | `absent` |

### R7 normalization

| # | Assertion | Result | Actual |
|---|-----------|--------|--------|
| A122 | SQ */domain/#ref variants merge to merchant_id "netflix" | ❌ FAIL | `missing` |
| A123 | merged netflix: occurrences==4 | ❌ FAIL | `undefined` |
| A124 | merged netflix: confidence 0.95 | ❌ FAIL | `undefined` |
| A125 | PAYPAL * + plain merge to "spotify" | ✅ PASS | `spotify` |
| A126 | merged spotify: occurrences==4 | ✅ PASS | `4` |
| A127 | AMZN* prefix stripped -> merchant_id "prime" | ✅ PASS | `prime` |
| A128 | prime: interval monthly | ✅ PASS | `monthly` |
| A129 | TST* prefix stripped -> "hulu" | ✅ PASS | `hulu` |

### R8 intervals

| # | Assertion | Result | Actual |
|---|-----------|--------|--------|
| A130 | weekly x4: detected | ✅ PASS | `emitted` |
| A131 | weekly x4: interval weekly | ✅ PASS | `weekly` |
| A132 | weekly x4: confidence 0.95 | ✅ PASS | `0.95` |
| A133 | biweekly x3: detected | ✅ PASS | `emitted` |
| A134 | biweekly x3: interval biweekly | ✅ PASS | `biweekly` |
| A135 | biweekly x3: confidence 0.8 | ✅ PASS | `0.8` |
| A136 | quarterly x3 (gaps 91,91): detected | ✅ PASS | `emitted` |
| A137 | quarterly x3: interval quarterly | ✅ PASS | `quarterly` |
| A138 | quarterly x3: confidence 0.8 | ✅ PASS | `0.8` |
| A139 | annual x2 (gap 365): detected | ✅ PASS | `emitted` |
| A140 | annual x2: interval annual | ✅ PASS | `annual` |
| A141 | annual x2: confidence 0.6 | ✅ PASS | `0.6` |
| A142 | gaps 6,7,8: detected weekly | ✅ PASS | `weekly` |

### R9 next_date

| # | Assertion | Result | Actual |
|---|-----------|--------|--------|
| A143 | monthly last 2026-09-11 -> next 2026-10-11 | ✅ PASS | `2026-10-11` |
| A144 | weekly last 2026-09-12 -> next 2026-09-19 | ✅ PASS | `2026-09-19` |
| A145 | quarterly last 2026-09-01 -> next 2026-12-01 | ✅ PASS | `2026-12-01` |
| A146 | monthly last 2026-01-15 -> next 2026-02-14 (+30d drift, not calendar month) | ✅ PASS | `2026-02-14` |

### R10 misc

| # | Assertion | Result | Actual |
|---|-----------|--------|--------|
| A147 | explicit merchant_id "m-netflix" used as key | ✅ PASS | `["m-netflix"]` |

### R11 degenerate

| # | Assertion | Result | Actual |
|---|-----------|--------|--------|
| A148 | empty array -> [] | ✅ PASS | `0` |
| A149 | all-pending array -> [] | ✅ PASS | `len` |
## Failures (3, one root cause)

**F1 — No merchant alias table (A122, A123, A124).** The spec requires "map known aliases to a canonical merchant id" (build order days 1–4: "Merchant normaliser and alias table"). The implementation has no alias table. Consequence, verified: `normalizeMerchant("netflix.com #123")` → `"netflix com"`, which does **not** merge with `"netflix"`. A user whose Netflix bills as "Netflix" one month and "netflix.com #4821" the next gets two fragmented merchant groups, each below the occurrence/confidence threshold — a real subscription can be missed entirely or reported at lower confidence. Same class of issue applies to any domain-suffixed variant (spotify.com, hulu.com, etc.). Fix: add the alias table mapping domain variants to canonical ids.

## Spec gaps (not counted as failures; spec lists them as required mitigations)

**G1 — No merchant-category plausibility filter (probe A157).** Spec "Known failure modes": "Require amount consistency plus a merchant category that plausibly bills recurring. Telling a user to cancel their commute coffee is the kind of error that gets screenshotted." Verified: four $6.50 charges 7 days apart at "Blue Bottle" are emitted as a `weekly` subscription at 0.95 confidence. The detector has no category input at all. Any regular same-amount purchase (coffee, transit top-up, weekly groceries at the same total) will be presented as a subscription. This is the exact false positive the spec warns against.

**G2 — No 25% tolerance path for variable-amount subscriptions (A148).** Spec: "Variable-amount subscriptions — usage-based billing, utilities. Widen the amount tolerance to 25% and lower confidence to 0.5." Verified: monthly charges of $80/$95/$70/$88 produce four singleton clusters and zero detections. Code behaves per the base algorithm; the widened-tolerance path is unimplemented, so variable utilities are silently missed (spec asks to "say so plainly" — nothing in the product surfaces this either).

**G3 — Annual detection needs 13+ months of history.** Spec names this as a known gap requiring plain-language disclosure at setup. Detector correctly finds annual (A138–A140, gap 365 → annual, 0.6). The disclosure copy was not verified in this pass.

## Minor notes

- **next_date uses fixed +30 days, not calendar months** (A143): a Jan 15 billing projects Feb 14, not Feb 15. Spec does not define next_date computation; the cancel card's "Next billing date" will drift from the real billing date over time. Cross-timezone probe: identical `next_date` output under `TZ=UTC`, `TZ=Europe/Rome`, `TZ=America/Chicago` (date-only ISO strings parse as UTC; the local round-trip is self-consistent) — no TZ bug found.
- **Greedy first-fit clustering** (spec-silent): the first transaction's amount anchors the cluster. Verified correct on all clustering assertions (3% rise merges; 25% rise splits; exactly-$1.00 merges; $1.01 splits).
- **75% boundary is inclusive** (A119–A121): 3 of 4 gaps (exactly 75%) emits; 2 of 3 (66.7%) does not. Matches "at least 75%".
- **Pending charges are excluded before grouping** (A131–A134): a 2-posted + 1-pending series is detected at n=2 / 0.6, not n=3 / 0.8.
- **Transfers and positive-amount credits never enter detection** (A135, A136).
- Out-of-band gaps (27, 32, 5, 9, 16, 93, 371 days) correctly produce no detection (A150–A156).

## Harshness statement

This pass is deterministic white-box testing of the algorithm, not a UI pass: 149 assertions, every band boundary, both threshold edges, five realistic subscription profiles, seven false-positive profiles, all exclusion rules, and the full clustering/normalization matrix. It does **not** verify that Cancel cards render in production (v1 agent C1 found zero detections on demo data — demo data was not re-examined here), that the cancel-path library exists, or that `wasteScore` ranking is spec-compliant. Those remain open from the v1 report.

## Recommended fixes (in order)

1. Add the merchant alias table (`netflix.com` → `netflix`, etc.) — fixes F1, highest detection-integrity value.
2. Add the category-plausibility filter for non-subscription merchant categories — fixes G1, the screenshot-risk false positive.
3. Implement the 25%-tolerance / 0.5-confidence path for variable-amount clusters — fixes G2.
4. Use calendar-month arithmetic for `next_date` on monthly intervals.
