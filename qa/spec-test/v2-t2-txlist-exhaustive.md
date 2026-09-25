# T2-v2 — Track Transaction List EXHAUSTIVE (252 assertions)

**Agent:** T2-v2 · **Date:** 2026-09-25 ~04:45 UTC · **App:** https://upmore-srikanthvishnu90-sketchs-projects.vercel.app/
**Spec:** Track (Doc 4) — Transaction list: date, merchant, amount, category.

## Method (harsh by design)

I did NOT eyeball screenshots. I extracted the **actual production functions** — `renderTxList()` (line 3507) and `TransactionSource.demo()` (line 3633) — verbatim from `src/upmore-app-template.html` with a brace-aware parser, executed them in Node, and ran assertions against the real rendered HTML. Then I verified the tested code is what's actually live:

- Production `index.html` md5 `74132629406d80cbadc08cd5130db1c6` == repo `index.html` md5 — **byte-identical**, so every assertion below describes production behavior exactly.
- Production returns HTTP 200; served `sw.js` stamp `upmore-8b52c95`.
- Demo dataset: **210 transactions** (90 days), 1 account (`demo-chk`, Checking, **$2,840.50**).

## Result: 244 PASS / 8 FAIL — VERDICT: FAIL

| Cluster | Assertions | Result |
|---|---|---|
| Row anatomy (30 rows × 8 checks: merchant, date·category, YYYY-MM-DD date, non-empty category, amount span, sign+$X.XX format, out/in class match) | 240 | 240 PASS |
| Pending badge | 3 | 3 PASS |
| Search (merchant, category, recurring, no-match, case-insensitive, income rows, amount-not-searched) | 8 | 8 PASS |
| Tap → recategorize / mark-transfer / flag-wrong | 5 | **5 FAIL** |
| Refund as +income (green) | 2 | **1 FAIL** |
| Amount colors (out=red, in=green) | 4 | **1 FAIL** |
| Demo-data labeling | 4 | **1 FAIL** |
| Wiring / coverage / live path | 10+ | all PASS |

## The 8 failures (defects, in severity order)

### F1–F5. Tapping a transaction does NOTHING — recategorize / mark-transfer / flag-wrong are vapor
- `TAP001`: zero click/tap handler bound to `.txrow` anywhere in the codebase.
- `TAP002`: the word "recategorize" appears **exactly once** — in a code comment (`// Tapping opens recategorize / mark-transfer / flag-wrong.`). No implementation, no dialog, no UI.
- `TAP003`: no mark-transfer action exists. `is_transfer` is only a filter flag in aggregation code; the user has no way to mark a transfer.
- `TAP004`: no flag-wrong / report-wrong-transaction code at all.
- The spec-mandated correction workflow (persistent recategorization, transfer marking, wrong-transaction reporting) is **entirely unimplemented** behind a comment that promises it. This is the single largest Track-list gap.

### F6. Refund rendered as green "+income" — `RF002`
- `demo-refund-1`: merchant "Amazon Refund", amount +$42.99, category "Shopping" → renders `<span class="in">+$42.99</span>` — **green, with a plus sign, indistinguishable from income**.
- Spec (and the SimpleFIN read-only rules): refunds must be netted against originals and **never shown as "+income" green**. The exclusion logic exists in aggregation code (`!t.is_pending && !t.is_transfer` filters) but the *list display* contradicts it.
- Same hole in the live path: `initLiveTrackData()` maps live transactions with no refund detection, so a real Chase refund would also render green.

### F7. Outgoing amounts are NOT red — `CSS003`
- Task spec: `−$X.XX (out, red)`. Actual CSS: `.txrow .out { color: var(--ink); }` — near-black, identical weight treatment to body text. Debits and credits differ only by sign character and green-on-credits; the red debit convention is missing.

### F8. Demo data presented as the user's own money — `D003`
- An anonymous production visitor sees 210 fabricated transactions and a $2,840.50 "Checking" balance with **no "demo"/"sample" label anywhere in the list HTML**.
- X1-F1 (`simplefin-proxy` edge function + `initLiveTrackData()`) only replaces demo with live data when the user is **signed in AND the proxy returns accounts**. Everyone else gets fabricated finances presented as fact. Until a live connection exists, the list must be labeled as sample data.

## What actually passes (verified, not assumed)

- All 30 sampled rows (most recent 30 of 100 rendered): every row shows merchant, `YYYY-MM-DD · Category`, and a correctly signed, two-decimal amount; negative→`out`, positive→`in`, 100% consistent.
- Minus sign is U+2212 (`−`), matching the spec's `−$X.XX` glyph exactly.
- Pending badge: `demo-pending-1` (Amazon −$42.50) renders `<span class="pending-badge">pending</span>` — orange badge, correct row, full row data intact.
- Search: `amazon` → merchant match (excludes Whole Foods); `shopping` → category match (excludes Chipotle); `netflix` → recurring rows; gibberish → empty; case-insensitive (`AMAZON` works); matches paycheck rows (`employer`); amounts are NOT searched (correct per merchant/category spec).
- Income row: "Employer Payroll" renders `<span class="in">+$2400.00</span>` green.
- Transfer row exists and renders (`Chase Transfer to Savings`).
- HTML escaping via `esc()` applied to merchant/date/category.
- ≥60 distinct dates over 90-day coverage; home strip → transactions screen wiring present; `txq` search input wired on input.

## Recommended fixes (parent: do NOT mark T2 done until)

1. Implement row-tap sheet: recategorize (persistent), mark-as-transfer, flag-wrong-transaction — the full correction workflow from the Track spec.
2. Refunds: detect (negative-amount originals / "refund" merchant / provider reversal codes), net against originals, and never render `class="in"` green `+$` for them.
3. `.txrow .out` → red (`#c0392b` or equivalent).
4. Label demo data as sample until a live bank connection replaces it (anonymous users must never see unlabeled fabricated finances).

**Files:** harness at `/tmp/t2v2-harness.js` (extracts + executes the real functions; re-runnable).
