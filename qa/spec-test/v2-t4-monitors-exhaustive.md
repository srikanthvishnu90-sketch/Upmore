# T4-v2 — Track Monitors EXHAUSTIVE (140 assertions, 20 per monitor)

**Agent:** T4-v2 · **Date:** 2026-09-24 (CDT) · **Build tested:** production commit `b73da4f`
**Production URL:** https://upmore-srikanthvishnu90-sketchs-projects.vercel.app/
**Spec:** Doc 4 (Track), "The monitors" section — seven monitors that fire after every data refresh.

## Production evidence chain

1. Production `/sw.js` serves cache stamp `upmore-8b52c95` (fetched live via browser.open).
2. Local HEAD is `b73da4f` ("Rebuild sw.js with cache stamp 8b52c95", pushed, `main` == `origin/main`) — the committed build stamps the pre-commit HEAD `8b52c95`. **Production == committed code.**
3. `diff` of the monitor section between `src/upmore-app-template.html` and built `index.html`: **identical.**
4. Method: extracted the EXACT monitor functions from the template via balanced-brace parsing (no re-implementation) and ran 140 scenario assertions in Node. Inline detector conditions for M4/M5/M6 are exact ports of the boolean guards in `buildQueue` (source lines cited); M7 asserts on absence.

## HEADLINE VERDICT: ❌ FAIL — the seven-monitor system does not exist in production

Of the spec's seven monitors (`newRecurringCharge`, `priceIncrease`, `trialConversion`, `categorySpike`, `lowBalance`, `duplicateCharge`, `paydayLanded`):

- **3 are implemented as functions — and are 100% dead code.** `TrackMonitors.newRecurringCharge`, `.priceIncrease`, `.categorySpike` (template lines ~3812–3855) have **zero call sites** anywhere in the app — no direct calls, no `TrackMonitors[k]` dynamic dispatch, no nightly job, no refresh hook. They can never fire.
- **4 are not implemented at all.** The code admits it: line 3856 — `// lowBalance, duplicateCharge, trialConversion, paydayLanded omitted for brevity — they follow the same evidence-mandatory, one-card-per-finding pattern.` They do not follow the pattern; they do not exist.
- There is **no nightly job and no scheduler** (client-only app; spec build order says days 29–35). Nothing "runs after every data refresh."
- The only monitor-like behavior in the live queue operates on **user-entered** data (`save_subscriptions`, `save_renewals`, `save_claims`) — not on transactions. Spec's transaction-pipeline monitors are absent.
- Spec hard-never #5 ("Never claim a monitor ran if no job exists") is currently not violated in user copy — the old Money tab's "watches this daily / Last checked today" copy is gone from the current 3-tab build — but the code comment at line 3184 ("Seven deterministic monitors push into the queue") is false, and `.alertcard` CSS ships unused.

**Scorecard: 140 assertions run — 93 confirm spec-compliant behavior, 47 document defects/deviations/gaps.**

---

## M1 — New recurring charge detected (TrackMonitors.newRecurringCharge) — ❌ FAIL (dead code + 3 defects)

Source: template lines 3813–3820. Never called.

| # | Assertion | Result |
|---|-----------|--------|
| M1-01 | Fires for a merchant_id not in seenIds | ✅ PASS |
| M1-02 | Does not fire for a seen merchant_id | ✅ PASS |
| M1-03 | Multiple new merchants → one card each | ✅ PASS |
| M1-04 | Card kind is `cancel` (spec: emits cancel card) | ✅ PASS |
| M1-05 | Title names the merchant: "New recurring charge: Netflix" | ✅ PASS |
| M1-06 | Body carries amount, interval, occurrence count | ✅ PASS |
| M1-07 | Evidence mandatory: occurrences + confidence % ("Detected from transaction history (5 charges, 95% confidence).") | ✅ PASS |
| M1-08 | dollars = amount × 12 for monthly | ✅ PASS ($191.88) |
| M1-09 | Confidence passed through from detector | ✅ PASS |
| M1-10 | Deterministic urgency 0.7, effort 5 | ✅ PASS |
| M1-11 | Fires at minimum 2 occurrences | ✅ PASS |
| M1-12 | Weekly interval fires, interval named in body | ✅ PASS |
| M1-13 | **DEFECT — yearly annualization: $100/yr subscription scores dollars = 1200** (`r.amount * 12` unconditional, line 3818). A yearly $100 charge enters the queue as a $1,200 opportunity — 12× overstated. | ❌ FAIL |
| M1-14 | Silence valid: empty recurrences → no cards | ✅ PASS |
| M1-15 | **DEFECT — merchant_id matched case-sensitively.** seenIds {"netflix"} does not suppress merchant_id "Netflix" → spurious refire. No normalization at the comparison point. | ❌ FAIL |
| M1-16 | **DEFECT — no dedupe:** two identical recurrence rows for one merchant → two cards. Violates "one card per finding, ever." | ❌ FAIL |
| M1-17 | Low confidence 0.6 still fires (detector's call) | ✅ PASS |
| M1-18 | No behavioural judgement in copy | ✅ PASS |
| M1-19 | Evidence names transaction-history detection | ✅ PASS |
| M1-20 | **CRITICAL — dead code.** Zero call sites in the entire app (verified: no `TrackMonitors.newRecurringCharge(` outside its definition, no bracket dispatch). The monitor **never fires in production.** | ❌ FAIL |

Design: where cards would render, copy is factual with mandatory evidence. But nothing renders — design points moot.

---

## M2 — Price hike on recurring (TrackMonitors.priceIncrease) — ❌ FAIL (dead code + 2 defects)

Source: template lines 3821–3832. Guard: `prev && r.amount > prev * 1.05`. Never called.

| # | Assertion | Result |
|---|-----------|--------|
| M2-01 | Fires on 20% increase ($10 → $12) | ✅ PASS |
| M2-02 | No fire at exactly 5% ($10 → $10.50; strict `>`) | ✅ PASS |
| M2-03 | No fire below 5% ($10 → $10.40) | ✅ PASS |
| M2-04 | No fire on price decrease | ✅ PASS |
| M2-05 | No fire without a previous-amount record | ✅ PASS |
| M2-06 | No fire on unchanged amount | ✅ PASS |
| M2-07 | Title: "Price increase: Netflix" | ✅ PASS |
| M2-08 | Body shows old → new with 2 decimals | ✅ PASS |
| M2-09 | Evidence names the 5% threshold + charge count | ✅ PASS |
| M2-10 | dollars = monthly delta × 12 ($24) | ✅ PASS |
| M2-11 | Deterministic confidence 0.9, urgency 0.8, effort 5 | ✅ PASS |
| M2-12 | 200% increase → $240/yr delta | ✅ PASS |
| M2-13 | Just-over-threshold $100 → $105.01 fires | ✅ PASS |
| M2-14 | **DEFECT — weekly annualization: $2/wk hike scores $24 instead of $104.** Same unconditional `* 12` (line 3830). | ❌ FAIL |
| M2-15 | **DEFECT — yearly annualization: $10/yr hike scores $120 instead of $10.** | ❌ FAIL |
| M2-16 | prev = 0 (free trial → paid): no fire (falsy guard) — trial conversion belongs to the missing trialConversion monitor | ✅ PASS |
| M2-17 | Multiple hikes → one card each | ✅ PASS |
| M2-18 | Silence valid when no hikes | ✅ PASS |
| M2-19 | Card kind is `cancel` (spec) | ✅ PASS |
| M2-20 | **CRITICAL — dead code.** Zero call sites. Never fires in production. | ❌ FAIL |

Note: the live queue's *separate* user-entered bill-spike detector (detector 2, line ~1892) works on `previous_amount` the user typed — it is not the spec's transaction-based price-increase monitor and was not counted here.

---

## M3 — Category spike >40%, min $50 (TrackMonitors.categorySpike) — ❌ FAIL (dead code + 2 serious logic defects)

Source: template lines 3833–3855. Exclusions verified: pending ✓, transfers ✓, inflows ✓ (amount < 0). Never called.

| # | Assertion | Result |
|---|-----------|--------|
| M3-01 | Fires: $200 vs $100 avg (100% over, $100 delta) | ✅ PASS |
| M3-02 | No fire at exactly 40% (strict `>`) | ✅ PASS |
| M3-03 | Fires at +50% with exactly $50 delta (boundary `>= 50`) | ✅ PASS |
| M3-04 | No fire when +49% but only $49 over (min-absolute gate works) | ✅ PASS |
| M3-05 | Pending transactions excluded ($5,000 pending Dining → no fire) | ✅ PASS |
| M3-06 | Transfers excluded | ✅ PASS |
| M3-07 | Inflows (positive amounts) excluded | ✅ PASS |
| M3-08 | Silence with only 3 months history (needs ≥ 4 month-keys) | ✅ PASS |
| M3-09 | Two spiking categories → two cards | ✅ PASS |
| M3-10 | Non-spiking category → silence | ✅ PASS |
| M3-11 | **DEFECT (serious) — FALSE POSITIVE: "this month" is the MAXIMUM month, not the current month.** Code sorts month totals descending and takes `vals[0]` (line ~3843). A $500 Dining month from 3 months ago still fires today. | ❌ FAIL |
| M3-12 | **DEFECT — evidence mislabeled:** card says "This month $500.00 vs 3-month average $106.67" when the $500 was months ago. Fabricated recency — violates "Evidence is mandatory" (false evidence is worse than none). | ❌ FAIL |
| M3-13 | **DEFECT — masks genuine current-month spikes:** with months [1000, 100, 100, 200], the current month's real 2× spike never gets its own card — the card fires on the old $1000 month instead. | ❌ FAIL |
| M3-14 | Evidence carries both numbers with 2 decimals | ✅ PASS |
| M3-15 | No behavioural judgement ("Dining is $200 this month vs $100 average — $100 over." — factual) | ✅ PASS |
| M3-16 | Empty transactions → silence | ✅ PASS |
| M3-17 | Refunds (positive) not counted as spending | ✅ PASS |
| M3-18 | Month keying by `posted_at.slice(0,7)` | ✅ PASS |
| M3-19 | Card kind is `spike` | ✅ PASS |
| M3-20 | **CRITICAL — dead code.** Zero call sites. Never fires in production. | ❌ FAIL |

Design: copy discipline is good (facts only, mandatory evidence). The defects are logic-level, not copy-level.

---

## M4 — Upcoming renewal (within 7 days) — ⚠️ PARTIAL (fires, but wrong window + wrong source)

Two separate user-entered-data paths exist. Neither is the spec's transaction-based trial/renewal detection.

**Path A — entered subscriptions** (template ~line 1902): `bd = qDaysUntil(x.next_billing_date); if (bd != null && bd <= 14)`.
**Path B — entered renewals** (template ~line 1922): `rens.filter(r => r.status === "upcoming")` — **no date filter at all**.

| # | Assertion | Result |
|---|-----------|--------|
| M4-01 | Subscription renewal in 3 days fires | ✅ PASS |
| M4-02 | Renewal today fires | ✅ PASS |
| M4-03 | Renewal in exactly 7 days fires (task window) | ✅ PASS |
| M4-04 | **DEVIATION — renewals 8–14 days out also fire.** Code uses `bd <= 14`; the task specifies "within 7 days." Input label even advertises "renewal reminder when it's within 14 days." | ⚠️ DEVIATION |
| M4-05 | Renewal in 15 days → silence | ✅ PASS |
| M4-06 | Overdue renewal fires (bd < 0 ≤ 14) | ✅ PASS |
| M4-07 | Overdue copy reads "3 days overdue" | ✅ PASS |
| M4-08 | No next_billing_date → silence | ✅ PASS |
| M4-09 | Cancelled subscription excluded | ✅ PASS |
| M4-10 | Card shows amount, "Review" CTA, urgency from qUrgency | ✅ PASS |
| M4-11 | Urgency scales: 1 day → 5 | ✅ PASS |
| M4-12 | Entered renewal (save_renewals) in 5 days fires | ✅ PASS |
| M4-13 | status ≠ upcoming → silence | ✅ PASS |
| M4-14 | **DEVIATION — renewal 400 days out still fires on path B (no date gate).** An "upcoming renewal" card for something 13 months away is noise. | ⚠️ DEVIATION |
| M4-15 | Overdue entered renewal fires with "overdue" copy | ✅ PASS |
| M4-16 | No date → fires with empty due text (no crash) | ✅ PASS |
| M4-17 | Card id unique per renewal (`renewal-` + id) | ✅ PASS |
| M4-18 | **GAP — spec's "trial converting" monitor ($0 charge + known trial length → deadline card) is not implemented anywhere.** | ❌ GAP |
| M4-19 | **GAP — no transaction-based renewal detection.** Both paths require manual user entry; the spec's detector-driven renewal alerts don't exist. | ❌ GAP |
| M4-20 | Verdict: the 7-day case fires, but the window is 14 days (A) / unbounded (B) | ⚠️ PARTIAL |

---

## M5 — Upcoming deadline — ⚠️ PARTIAL (fires, but with NO upcoming-only gate)

Source: template ~line 1931: `claims.filter(c => c.status === "open")` — **no date filter whatsoever.**

| # | Assertion | Result |
|---|-----------|--------|
| M5-01 | Open claim due in 5 days fires | ✅ PASS |
| M5-02 | Title names merchant + kind ("Amex - claim") | ✅ PASS |
| M5-03 | Copy: "due in 5 days" | ✅ PASS |
| M5-04 | Overdue claim fires with "overdue" copy | ✅ PASS |
| M5-05 | **DEVIATION — deadline 2 years out still fires.** No upcoming-only gate. | ⚠️ DEVIATION |
| M5-06 | **DEVIATION — open claim with NO deadline still fires** (sub: "due "). A deadline card with no deadline. | ⚠️ DEVIATION |
| M5-07 | Closed ("claimed") claim → silence | ✅ PASS |
| M5-08 | CTA "Mark claimed", conf 0.9, eff 15 | ✅ PASS |
| M5-09 | Urgency scales: 1 day → 5 | ✅ PASS |
| M5-10 | dollars = claim amount | ✅ PASS |
| M5-11 | Steps/notes shown in card | ✅ PASS |
| M5-12 | $0 claim still fires | ✅ PASS |
| M5-13 | No merchant → title is kind only | ✅ PASS |
| M5-14 | Card id unique per claim (`claim-` + id) | ✅ PASS |
| M5-15 | "due today" copy for today | ✅ PASS |
| M5-16 | **GAP — no transaction-derived deadlines** (return windows, trial ends) — user must hand-enter everything | ❌ GAP |
| M5-17 | Renewal + claim fire independently | ✅ PASS |
| M5-18 | Engine fires ALL open claims incl. dateless and far-future — "upcoming deadline" misnomer | ⚠️ DEVIATION |
| M5-19 | 30-day deadline → urgency 2 | ✅ PASS |
| M5-20 | Verdict: fires, but unbounded | ⚠️ PARTIAL |

One-card-per-finding: marking claimed flips status → card stops (deadlineDone). Dismissal-persistence for non-terminal dismiss does not exist anywhere in the app (no dismiss mechanism at all).

---

## M6 — Duplicate charge — ⚠️ PARTIAL (user-entry detector exists; spec's transaction monitor missing)

Implemented detector (template ~line 1878, "detector 1"): groups **user-entered subscriptions** by `normMerch`; fires when `g.length >= 2`. The spec's monitor — "same merchant, same amount, within 3 days" on **transactions** — does not exist.

| # | Assertion | Result |
|---|-----------|--------|
| M6-01 | Two same-merchant, same-amount entries → fires | ✅ PASS |
| M6-02 | Title "Possible duplicate: Netflix" (hedged, not asserted) | ✅ PASS |
| M6-03 | dollars = annual of the extra charge ($191.88) | ✅ PASS |
| M6-04 | **DEVIATION — same merchant, DIFFERENT amounts also fires.** Spec requires "same merchant, same amount." No amount comparison in code. | ⚠️ DEVIATION |
| M6-05 | Single subscription → silence | ✅ PASS |
| M6-06 | Cancelled + active same merchant → silence | ✅ PASS |
| M6-07 | Three same-merchant → one card, dollars = sum of extras ($240) | ✅ PASS |
| M6-08 | Case-insensitive grouping | ✅ PASS |
| M6-09 | Different merchants → silence | ✅ PASS |
| M6-10 | **FALSE-POSITIVE RISK — two legitimately distinct plans from one merchant (e.g., two Apple subscriptions, $9.99 + $2.99) are flagged as duplicates.** No amount/date/plan disambiguation. | ❌ DEFECT |
| M6-11 | Empty list → silence | ✅ PASS |
| M6-12 | Deterministic id `dup-` + normalized merchant | ✅ PASS |
| M6-13 | conf 0.8, urg 1.5, eff 3 | ✅ PASS |
| M6-14 | Yearly extra: dollars = amount (INT2MO math correct here) | ✅ PASS |
| M6-15 | Sub names the charge count | ✅ PASS |
| M6-16 | Whitespace/case variants grouped | ✅ PASS |
| M6-17 | Detector runs on user-entered subscriptions only — no transaction input | ⚠️ NOTED |
| M6-18 | **GAP — spec's transaction duplicate monitor (same merchant + same amount within 3 days) is not implemented.** The string "within 3 days" appears nowhere in the codebase. A real double-charge on a card would never be flagged. | ❌ GAP |
| M6-19 | No pending-transaction duplicate logic (consistent with absence) | ⚠️ NOTED |
| M6-20 | Verdict: user-entry duplicate detector exists; spec monitor missing | ⚠️ PARTIAL |

Design: the duplicate side-by-side sheet (line ~2370) lists every matching charge with per-row Cancel buttons — good evidence-first UX where it exists.

---

## M7 — Overdraft/fee detected — ❌ FAIL (entirely absent, 0/20 functional)

| # | Assertion | Result |
|---|-----------|--------|
| M7-01 | No overdraft/fee function in TrackMonitors | ❌ ABSENT |
| M7-02 | Fee detection is a bare TODO: `fees: [], // TODO: detect overdraft/late fees` (line ~2811) | ❌ ABSENT |
| M7-03 | No "overdraft" card type pushed to the queue | ❌ ABSENT |
| M7-04 | No "fee" card type pushed to the queue | ❌ ABSENT |
| M7-05 | Overdraft regex exists ONLY for Capital suppression (line ~2961: `/overdraft\|insufficient/i`), never surfaced to the user | ❌ NOT A MONITOR |
| M7-06 | $35 "OVERDRAFT FEE" in transactions → no card | ❌ FAIL |
| M7-07 | "INSUFFICIENT FUNDS FEE" → no card | ❌ FAIL |
| M7-08 | Merchant late fee → no card | ❌ FAIL |
| M7-09 | Repeated overdraft pattern → no cross-finding reasoning (the spec's "model reasons across findings" has nothing to read) | ❌ FAIL |
| M7-10 | No pending-aware fee logic | ❌ ABSENT |
| M7-11 | No fee threshold/pattern logic | ❌ ABSENT |
| M7-12 | No fee evidence formatting | ❌ ABSENT |
| M7-13 | No one-card-per-finding dedupe for fees | ❌ VACUOUS |
| M7-14 | No silence logic (nothing runs) | ❌ VACUOUS |
| M7-15 | Budget fact pack hardcodes `fees: []` | ❌ CONFIRMED |
| M7-16 | Budget plan therefore can never emit low-balance/fee alerts from real data | ❌ FAIL |
| M7-17 | Related spec monitor "low balance ahead" also missing (admitted in the omission comment) | ❌ GAP |
| M7-18 | No nightly job — nothing runs monitors on any schedule | ❌ GAP |
| M7-19 | The suppression regex proves the app *can* recognize fee merchants — it just never tells the user | ⚠️ NOTED |
| M7-20 | Verdict: monitor entirely absent | ❌ FAIL |

---

## Cross-monitor findings (apply to the whole system)

1. **No monitor runs after data refresh.** Spec: monitors "fire after every data refresh." Nothing in `loadTrackData`, `initLiveTrackData`, or `renderTrackStrip` invokes any monitor. The user-entered detectors run inside `buildQueue` on render — not on refresh, not nightly.
2. **"One card per finding, ever. Dismissal is permanent."** — No dismiss mechanism exists in the app at all, so permanence is vacuous. M1-16 shows duplicate findings would produce duplicate cards if the dead code were wired up.
3. **"No monitor fires on pending transactions"** — holds in the dead TrackMonitors code (M3-05 ✅) and in `detectRecurrence`, but is untestable in production since nothing runs.
4. **Silence is valid** — all implemented paths return empty correctly; the app does not manufacture insights. ✅ (The one bright spot.)
5. **No behavioural conclusions in copy** — verified factual tone (M1-18, M3-15 ✅).
6. **Coverage windows** — monitor evidence does not state coverage windows (e.g., "Based on 3 months of Chase checking …4471" from the spec). M1-07's evidence says "Detected from transaction history" with no window, no account. ⚠️
7. **Annualization bugs** (M1-13, M2-14, M2-15): the unconditional `* 12` corrupts every non-monthly figure these monitors would emit. Any future wiring must annualize by interval.
8. **M3's max-month bug** (M3-11/12/13) makes `categorySpike` actively harmful if wired up as-is: false positives on old spikes, false evidence labels, missed genuine spikes.

## What must be fixed (for parent agent's fix pass)

1. Wire `TrackMonitors` into the post-refresh path (or delete it — dead code asserting "seven monitors" is worse than none).
2. Implement the 4 missing monitors (trialConversion, lowBalance, duplicateCharge-tx, paydayLanded) or formally descope them.
3. Fix annualization: multiply by interval (monthly ×12, weekly ×52, yearly ×1, quarterly ×4).
4. Fix `categorySpike`: compare the CURRENT month vs the prior-3-month average, not max-month vs rest.
5. M4: reconcile the 14-day window with the "within 7 days" requirement; add a date gate to the save_renewals path.
6. M5: add an upcoming-only gate (e.g., ≤ 30 days, has deadline).
7. M6: add same-amount check per spec; implement the transaction-level 3-day duplicate monitor.
8. M7: implement fee/overdraft detection (the regex already exists for suppression — reuse it and surface a card).
9. Add the nightly/scheduled job or remove "after every data refresh" claims; the line-3184 comment is false today.
10. Add dismissal persistence if cards become dismissible.

**Bottom line: 93/140 behavior assertions confirm correct micro-behavior where code exists; 47 document defects, deviations, or gaps — including 3 dead-code monitors, 4 unimplemented spec monitors, 1 entirely absent monitor, annualization bugs, and a spike detector that mislabels history as "this month." The Track monitor system as specified is not live in production.**
