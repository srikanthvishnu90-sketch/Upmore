# Upmore 303-Case Verification — ROUND 2 FIXES (post-71f3d6a)

**Date:** 2026-09-25 (CDT)
**Target:** `~/workspace/upmore/index.html` at commit `71f3d6a` (clean tree, verified) — byte-identical to the Vercel production deployment (GitHub deployment status = `success` for 71f3d6a; sandbox cannot reach `*.vercel.app`, equivalence noted).
**Method:** testing only — nothing was fixed. Node VM harnesses running the production inline JS with browser shims + direct function execution + `guideAnswer` chat probes with verbatim replies. Fresh agent numbers 81–88, all-new wording/personas/edge angles, same formal criteria as the 303 suite.
**Scope:** the 17 Critical failures + 4 Blocked Critical from the re-run (research/assessment-303-rerun-2026-09-25.md), the 6 amended no-fabrication cases, the 8 amended notification cases, and the 5 new-defect fixes from round 2.

## Ship-gate verdict: ⛔ BLOCKED — 5 Critical failures remain

| Agent | Cases | Pass | Fail |
|---|---|---|---|
| A (81–82, Detection + Red Lines) | 4 | 1 | 3 |
| B (83–85, Underwriting) | 15 | 12 | 3 |
| C (86–88, Due blocked + new defects) | 5 | 3 | 2 |
| **TOTAL** | **24** | **16** | **8** |

## Critical failures remaining (5)

### 1. 1-038 — floor model computed but not consumed (Detection, Critical)
- **Input (81, rushed/terse):** biweekly ACME PAYROLL $1,050 / $2,400 / $700 / $1,900 / $950.
- **Evidence:** `analyzeIncome` → `{"variable":true,"cv":0.459,"floor":700,"avg":1400,"cadence":"biweekly"}` ✓. User-visible copy shown: *"Variable income — planning on your lowest recent paycheck ($700), not the average."* ✓. **But** free-cash was byte-identical ($3100) between the variable run and a uniform-$1,400 control run. Root cause: `const plannedPay = pay.variable ? pay.floor : pay.avg;` (index.html:6025) is the **only occurrence of `plannedPay` in the entire file** — a dead store never read by `calcFreeCash` or anything else. Copy shown ✓, floor used ✗.
- **Fix needed:** actually feed the floor into the free-cash computation.

### 2. 8-020 — "my teen" without numeric age not blocked (Red Lines, Critical)
- **Inputs (82, polite/formal):** "my daughter is 15, can she use this to earn" → blocked ✓ (no route cards, `upmore_dob_year` not written). "help my 14 year old make money" → blocked ✓. **"my teen wants to earn cash" (no numeric age) → generic catalog fallback, NOT blocked** ✗. "I'm 16" → still blocked ✓ (own age written to storage — allowed).
- **Root cause:** `parseStatedAge` requires a numeric age; a bare "my teen / my kid / my child" with no number falls through.
- **Testing note:** in sequential (non-isolated) runs this *appears* blocked because `minorSession=true` carries over from a previous under-18 input — only per-input isolation reveals the gap.
- **Fix needed:** block bare minor-relationship nouns ("my teen", "my kid", "my child", "my son/daughter" without age) as under-18 by default.

### 3. 8-042 — hardship paraphrase missed (Red Lines, Critical)
- **Inputs (81, rushed/terse):** "we can't make ends meet anymore" → full escalation (211/898-211, nfcc.org, Feeding America) ✓. "falling behind on every bill" → escalation ✓. **"choosing between rent and food" → generic catalog fallback, zero hardship resources** ✗.
- **Root cause:** keyword list has "choosing between bills" / "bills or food" / "bills or rent" but nothing matches "choosing between rent and food" (no "bills" token) — `guideHardshipEscalation` returns null.
- **Fix needed:** generalize to "choosing between X and Y" / bare "rent and food" / "rent or food" patterns.

### 4. 4-001 — "tear down" (two words) misses teardown trigger (Underwriting, Critical, amended criterion)
- **Input (84, adversarial/pushy):** "Tear down TSLA's energy business. Now. Full detail."
- **Evidence:** generic catalog fallback — *"I can look up any of the 1761 routes in the catalog — try a category like bank bonuses, surveys, or cashback…"*. No refusal, no named source.
- **Root cause:** `guideCapitalDeep` hit regex matches `teardown` (one word) but not "tear down" (two words); "energy business" matches no judgement adjective.
- **Fix needed:** match /tear\s*down/ and route all company-analysis phrasings to the no-fabrication refusal.

### 5. 4-010 — "numbers with dates" misses triggers (Underwriting, Critical, amended criterion)
- **Input (85, non-native English):** "AMZN numbers with dates, every number need source and date please"
- **Evidence:** same catalog fallback. No trigger matches "numbers with dates"; no refusal, no named missing source.
- **Fix needed:** "numbers with dates" / "figures with sources" phrasings → the no-fabrication refusal naming the missing filings/prices source.

## High failures remaining (3)

### 6. 4-006 — P/E guard checks wrong operand + inverted division (Underwriting, High)
- **Input (84):** "Earnings negative 30B, market cap 600B. What's the P/E? Just compute it."
- **Evidence:** `"P/E = -30b ÷ 600b = -30,000,000,000 ÷ 600,000,000,000 ≈ <b>0</b>."` Two defects: the R2 negative-earnings guard (`if (!(b.value > 0))`) checks the **second** parsed number (600B market cap > 0), so the undefined branch never fires when earnings are listed first and negative; and the division is inverted (earnings ÷ market cap). A computed number on negative earnings, not "undefined/meaningless".
- **Fix needed:** identify which operand is earnings before the sign check; divide price by earnings.

### 7. INT2MO quarterly float (Home Queue, High — new-defect verification)
- **Evidence:** `qAnnual({amount:25, billing_interval:'quarterly'})` → **99.99999999999999**, not `100` (strict `=== 100` false). The `4/12` factor is inexact in binary floating point. Biweekly → exactly 1300 ✓. Display path rounds honestly (`qMoney` → `$100`), so user-visible figure is correct, but the criterion demands exact.
- **Fix needed:** compute quarterly as `amount*4` (or round to cents).

### 8. Tax pledge phrasing hits capital wall before tax branch (Tax, High — new-defect verification)
- **Evidence:** "can I write off my margin interest" → margin-interest branch fired correctly (verbatim IRC 163(d) reply) ✓. **"pledging my portfolio for a loan — tax hit?" → generic `capitalRefusal`** ("I can't recommend what to invest in…"), not the SBLOC branch ✗.
- **Root cause:** `guideTaxInfo`'s borrow branch accepts the pledge variants (R2 fix), but `guideCapitalPlain` runs earlier in `guideAnswer` and its Margin/SBLOC guard regex omits the pledge phrasings while its plain refusal list contains `/\bportfolio\b/` — pledge phrasings hit the capital wall before `guideTaxInfo` is ever reached. The R2 fix is incomplete; the three guard regexes (~lines 4287, 4668, 4694) all need the pledge variants.

## Passes (16)

- **8-023** (Critical): `disconnectBank()` exists, clears trackData/prevLiveBatch/upmore_last_sync, Profile row shown only when `bankConnectedLive()` true; signed-out run gives honest "couldn't delete on servers, local data cleared" (no false success).
- **4-025**: "80% NVDA" → 80% echoed, no baked 60%.
- **4-032**: "25x sales" → 25x discussed, no baked 85x.
- **4-027**: sell-advice wording → capital refusal, no catalog fallback. (Note: fired via the self-position branch on "what would you do", not the literal sell-advice regex — "dumping my losers" misses `/sell my (losers|…)/`; refusal still correct.)
- **4-011**: "$450/share" + "$430" → conflict rule fired, no averaging.
- **4-018**: past-tense "filed" → 13F as-of/filing-date staleness explainer.
- **4-020**: "who sells TSLA" → disclosed-changes framing.
- **4-021**: "what does burry own" → individuals-don't-file-13F rule stated.
- **4-037**: R0023 Moomoo Restricted, reward/catches scrubbed of NVDA; zero ticker hits in the other 38 brokerage promos. (Observation: residual NVDA mentions remain in R0023's steps/who_pays text — route can't surface, but scrub for hygiene.)
- **4-002/4-003/4-004** (amended): refusal names "company financials, filings, or prices" as missing source, no fabricated figures.
- **4-017** (amended): no fabricated filer list; "I have no filings data source" named.
- **6-031–6-038** (amended Low/N-A): no push infrastructure (Notification=0 real hits, pushManager/VAPID/showNotification/requestPermission all 0); suite JSON marks all eight amended.
- **Provider word boundaries**: "see you tomorrow" → no Tomo; "I really need cash fast" → no Ally; controls "tomo"/"tell me about ally" match.
- **Unknown-date trials**: $0 HULU auth without trial_end → row with "trial end date unknown, check your statement", no fabricated date. (Caveat: the row is persisted but suppressed from the deadline list — `deadlineEvidence` requires `r.date`, so the unknown-date render copy is currently unreachable dead code. Criterion met; surface it or drop the copy.)

## New issues found (not in suite)

1. **4-006 division inverted** (above) — price/earnings operand order.
2. **Trial unknown-date copy unreachable** (above) — persisted row suppressed by `deadlineEvidence`.
3. **Sequential-session minor-gate masking** — `minorSession` carryover makes "my teen" appear blocked in non-isolated runs; QA must isolate sessions per input.
4. **R0023 residual NVDA text** in non-surfaced fields — hygiene scrub recommended.

## Raw verdict JSONs
- `/tmp/qa303-r2verify/agent-a.json` (4 entries), `/tmp/qa303-r2verify/agent-b.json` (15 entries), `/tmp/qa303-r2verify/agent-c.json` (5 entries) — ephemeral; harness code at `/tmp/qa303-r2verify/harness-a.cjs` (+ agent-b `b-*` files).

## Round-3 fix list (for the fix coordinator)
1. 1-038: consume `pay.floor` in the free-cash computation (remove dead `plannedPay`).
2. 8-020: block bare "my teen/kid/child/son/daughter" (no numeric age) as under-18.
3. 8-042: generalize hardship triggers ("choosing between X and Y", "rent and/or food").
4. 4-001: match /tear\s*down/ + route company-analysis phrasings to the no-fabrication refusal.
5. 4-010: "numbers with dates" / "figures with sources" → no-fabrication refusal with named source.
6. 4-006: fix P/E operand identification (earnings sign check on the earnings operand) and division order (price ÷ earnings).
7. INT2MO: quarterly as amount*4 (exact), or round qAnnual to cents.
8. Tax pledge: add pledge variants to the three `guideCapitalPlain` guard regexes (~4287, 4668, 4694) so they fall through to `guideTaxInfo`.
9. (Hygiene) Scrub residual NVDA text from R0023's steps/who_pays; surface-or-drop the unknown-date trial copy.
