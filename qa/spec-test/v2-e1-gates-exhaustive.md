# E1-v2 Report: Earn Nine-Gates EXHAUSTIVE (214 assertions)

**Verdict: FAIL** — 135 pass / 79 fail across 214 assertions. The nine-gate pipeline has the right shape (order, short-circuit, queue+Explore coverage) but fails adversarially in every gate family that was stress-tested, and all user-data wiring is hardcoded.

## Method (why this evidence is production-valid)

- Extracted the **actual** functions `earnGates`, `routeGateInputs`, `routePassesGates`, `routeVerification` from `src/upmore-app-template.html` and executed them in Node against 214 hand-built adversarial cases + a full sweep of all 1,667 live (non-retired) catalog routes.
- Downloaded production `index.html` (HTTP 200, 7,075,124 bytes) and verified **byte-identical** gate functions vs the template, plus identical occurrence counts for every wiring block (`age: 19 // TODO`, `free_cash: 5000, free_minutes: 60`, `hasConnectedBank`, `calcFreeCash(5000, [], "2099-01-01", 100)`, the fail-open catch, the `10000` default). **Every finding below applies to production as served.**
- Harness: `/tmp/e1_harness.js` (kept for re-runs).

## Scorecard

| Section | Tests | Pass | Fail |
|---|---|---|---|
| A. Gate 1 Age parsing (30) + age gate behavior (20) | 50 | 37 | 13 |
| B. Gate 5 Loss (55) | 55 | 34 | 21 |
| C. Gate 9 Prerequisite (32) | 32 | 22 | 10 |
| D. Bypass / order / other gates (30) | 30 | 21 | 9 |
| E. User-data wiring (22) | 22 | 4 | 18 |
| F. Live-catalog sweep (24) | 24 | 16 | 8 |
| **Total** | **214** | **135** | **79** |

## Critical findings

### Gate 1 (Age) — false negatives hide eligible routes; false positives invent age gates; common phrasings missed
Parser = three regexes over `who_qualifies`, first match wins, no age-context requirement on the third pattern.

**False negatives (eligible users hidden) — LIVE catalog impact:**
- **F24 / A14**: R0789 (T-Mobile, researched/live): "eligible phone **90+ days** on a device payment plan" → `min_age=90`. A 19-year-old fails the age gate on a route with no age requirement. **Live bug.**
- **F23 / F01**: R6801 (FanDuel Sportsbook, researched/live): "18+ in DC/KY/PR/WY, **21+ in AZ, AR, CO, CT, IL**, …" → parser takes first match → `min_age=18`. A **19-year-old in Illinois is SHOWN a gambling route that requires 21+ in Illinois**. State-specific age requirements are not handled, and the state gate is dead code (see D09/D26), so nothing else catches it. **Live safety bug.**
- A16/A17/A47: "lift 50+ lbs", "50+ countries" → `min_age=50`; a 19-year-old is hidden from no-age-gate routes (synthetic proofs; the retired R7700/R6709 carry the same real text).

**False positives (no age gate invented):** A27 "spend 18+ dollars" → 18; A28 "21+ ways to earn" → 21; A30 "earn 18+ points per survey" → 18. Any "NN+" not preceded by `$`/digit is treated as an age gate — quantities, counts, and point values included.

**Missed phrasings (under-18 users NOT gated):** A25 "You must be 18 or older" → 0; A26 "Must be 21 or older" → 0; A34 "ages 18-65" → 0; A37 "Must be at least 21 years of age" → 0. The parser only understands the `+` suffix forms.

Dollar-amount guards work where tested: A13 "$30+ on ink" → 0, A15 "250+-gal" → 0, A18 "$50+ in purchases" → 0, A29 "$18+ cash back" → 0, A39 "$1,000 of gold" → 0, F02/F03 (R1621, R4053) → 0, F08 (no live route has an age parsed from a `$`-prefixed amount).

### Gate 5 (Loss) — both directions broken at scale
`cannot_lose` = keyword heuristic (`mandatory|required|non-refundable|you will|must pay|lose`) + first-`$`-amount only + `optional`-anywhere veto + own-account-deposit exception.

**False negatives — routes that CAN lose the user money but PASS (live catalog, all researched):**
- R4777 (Wealthcu): "**$100 fee** for closing the account within 6 months" → passes.
- R4120 (Centralbank): "**$5–$8.95 monthly fee** may apply" → passes.
- R0576 (Trustonefinancial): "**$10 monthly fee** … **$5 monthly fee**" → passes.
- R2234 (Traviscu): "one-time **$5 membership fee**" → passes.
- R0074 (Commerce Bank): "**$12 monthly fee**" → passes.
- R6367: "**nonrefundable**" (no hyphen) → passes.
- 16 live routes match the "bare `$N` fee with no trigger keyword" pattern and pass.
- Structural misses (B07/B08/B09/B10/B24/B25/B26/B35/B36/B39/B41/B42/B43/B51/B52/B53/B54): "you'll pay $20", "there is a $30 application fee", "shipping costs $30", "requires a $50 deposit", "costs $10", "you pay $10/month", "must pay $10" (no "you"), "nonrefundable"/"non refundable", "lose $10 in fees", "$25–$50 in fees may apply", "entry fee $10", "a $75 charge applies", "$75 will be charged", "membership costs $99/year", "free trial then $15/mo unless cancelled".

**False positives — legitimate routes WRONGLY hidden at the loss gate:**
- R0606: "must move/park ~$500 (**…are required** — smaller deposits do not count.)" → the word "required" (about direct deposits, not a fee) trips the heuristic. This is nearly the spec's own canonical passing example ("must move/park $3,500 in your account → PASSES") and it FAILS.
- R3778/R0016/R0922: "$10,000 **deposit required**" into the user's own new bank account → flagged as a loss. A required deposit into your own account is not a loss (spec's own logic), but the own-account exception needs literal "your … account"/"in your" phrasing.
- R4105: "Branch visit **required**" — "required" attaches to a non-monetary requirement while `$15,000` (capital lockup, not a fee) supplies the amount → fails.
- 48 of 243 bank-prereq routes fail at loss before ever reaching the prereq gate; heuristic estimate ~103 deposit-like routes wrongly hidden catalog-wide.

**Structural defects:** B12 only the FIRST `$` amount is read ("$0 to start, then $50/month mandatory" → passes); B13/B21 the word "optional" ANYWHERE vetoes all mandatory detection ("optional $25 wire fee; mandatory $10 account fee" → passes); B14 the own-account exception swallows a real mandatory fee ("mandatory $50 non-refundable fee to park $3,500 in your bank account" → passes). B46–B49: "$3,500" → 3500 comma parsing is correct.

### Gate 9 (Prerequisite) — narrow patterns + app-level bypass
Unit-level `bank account|checking account` works (C01–C07, C15–C22, C24–C30 pass), but:
- **C08**: "requires a **savings** account" → not detected → shown to bankless users.
- **C09/C10/C11**: "requires **PayPal** account", "requires **Venmo**", "requires a **debit card**" → not detected.
- **C12/C13**: "requires bank **acct**", "requires a **bank-account**" (hyphen) → not detected.
- **C14/C23**: a bank requirement stated ONLY in `who_qualifies` is never read (gate reads `requirements` only).
- **C31/C32**: "requires an existing Chase account", "must have direct deposit set up" → not detected.
- **App-level (E06/E07)**: `TransactionSource.demo()` **always** returns `accounts: [{id:"demo-chk", balance:2840.50}]`, and `hasConnectedBank = trackData.accounts.length > 0` reads `loadTrackData()` = demo by default. **Gate 9 can never fail for any signed-out/demo user — everyone is treated as bank-connected.** Correct per-route behavior verified for 195/243 live bank-prereq routes in isolation; 48 short-circuit earlier at the loss gate (correct order, but includes the R0606-class false positives above).

### Gate bypass / ordering
- **D07**: no sibling-route concept — completing R1 does not block R2 (same action, different id). Spec requires sibling completion to fail gate 8.
- **D09/D10/D26/D27**: `routeGateInputs` **unconditionally overwrites** `states` and `deadline` with `undefined`, so gates 2 and 3 are dead code — no route can ever fail them, and any catalog state/deadline restriction is silently discarded.
- **D12**: catalog `status:"stale"` maps to verification `"unverified"` → passes freshness → stale routes **can lead the queue**, violating "stale … may never lead the queue".
- **D13**: 265 `unverified` catalog routes pass the freshness gate and can lead the queue / enter plans. Spec: only `confirmed` (operator-verified exact terms) leads.
- **D25**: Explore's `catch (e) { /* gates unavailable, show unfiltered */ }` **fails open** — any exception in the gate path shows all routes ungated.
- Correct: gate order age→…→prerequisite (D08), short-circuit returns first failed gate (D23), both queue and Explore apply `routePassesGates` (D18/D19), slice-after-filter (D24), non-cash exclusion via `canLead` in `rankMoves` (D20), `researched→confirmed` mapping (D21), override precedence (D22). D29 is robustness-only: `earnGates` called standalone without a `verification` field fails freshness — not reachable via `routePassesGates`.

### User-data wiring — all hardcoded (E01–E05, E08–E10, E14, E17, E20, E22)
Production serves, verbatim:
- `gateUser = { age: 19, state: "IL", free_cash: calcFreeCash(5000, [], "2099-01-01", 100), free_minutes: 60, accounts: hasConnectedBank ? ["bank_account"] : [] }` (buildQueue) and `{ age: 19, state: "IL", free_cash: 5000, free_minutes: 60, … }` (Explore).
- A `profiles` table with `state`, `free_time_hours`, `cash_available` exists and `planData()` uses it — **the gates ignore it entirely** (E11–E13, E21). There is **no age/DOB column** anywhere, so Gate 1 cannot be personalized even for signed-in users.
- `routePassesGates` invents defaults: `free_cash: 10000`, `free_minutes: 60` when unknown (E09/E10/E22) — a user with unknown cash is treated as having $10,000.
- The hardship/distress check also uses `calcFreeCash(5000, [], "2099-01-01", 100)` (E20).
- `initLiveTrackData` (SimpleFIN) exists but only re-renders the track strip — **the queue is never re-gated after live bank data arrives** (E19).
- E15 passes: production gate functions are byte-identical to the template (this report's findings are production findings). E16/E18 pass as documentation of the hardcoded/live-path state.

## Failing case numbers (complete)

A14, A16, A17, A23, A24, A25, A26, A27, A28, A30, A34, A37, A47,
B07, B08, B09, B10, B12, B13, B14, B21, B24, B25, B26, B35, B36, B39, B41, B42, B43, B51, B52, B53, B54,
C08, C09, C10, C11, C12, C13, C14, C23, C31, C32,
D07, D09, D10, D12, D13, D25, D26, D27, D29,
E01, E02, E03, E04, E05, E06, E07, E08, E09, E10, E11, E12, E13, E14, E17, E19, E20, E22,
F01, F05, F06, F12, F13, F21, F23, F24.

(Notes: D29 is robustness-only, not production-reachable. F12/F13 as strictly asserted are over-strict — corrected analysis: 195/243 bank-prereq routes behave perfectly in isolation; 48 short-circuit at the loss gate first, which is correct ordering but surfaces the B-class false positives. F05/F06 routes R7700/R6709 are retired, so the "50+"-as-age false negative is parser-live but not currently user-visible; R0789/F24 is live.)

## What is correct (135 passes — credit where due)

All nine gates exist in spec order with short-circuit; all five spec loss examples behave exactly as specified (B01–B05); comma parsing "$3,500"→3500 (B46–B48); gates enforced on both queue and Explore; queue slices after gating; non-cash never leads (canLead); no age parsed from `$`-amounts anywhere in the live catalog (F08); all 21+ catalog routes except R6801 are hidden from a 19-year-old (F14 modulo F01); no bank-prereq route is ever shown to a bankless user when reached at gate 9; capital gate math correct in isolation (D03–D05, F21 modulo loss-short-circuits); cooldown works for exact ids (D06); time gate works (D16/D17); expired/retired correctly fail freshness (D14/D15).

## Bottom line for the parent

Do not treat the gates as done. The highest-severity items: (1) **R6801 shows a 21+-in-Illinois gambling route to 19-year-olds** (state-specific ages + dead state gate); (2) **loss gate shows routes with real fees** (R4777 $100, R4120/R0576/R0074 monthly fees) **and hides legitimate bank bonuses** (R0606/R3778/R0016/R0922/R4105); (3) **R0789 hidden from eligible users** via "90+ days"→age 90; (4) **all user inputs hardcoded** — age 19, IL, $5,000, 60 min, demo bank always "connected"; (5) **stale/unverified routes can lead the queue** (265 unverified live); (6) **Explore fails open** on any gate exception. Recommended: replace keyword heuristics with per-route structured gate fields at catalog-build time (age_min, states[], fee schedule), wire gateUser to the profiles table + live SimpleFIN snapshot, add an age column to profiles, and re-gate the queue when live data arrives.
