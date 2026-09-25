# T5-v2 — Track: Categories EXHAUSTIVE (80+ assertions)
**Agent**: T5-v2 · **Spec**: Doc 4 — Track §"What categories to use"
**App**: https://upmore-srikanthvishnu90-sketchs-projects.vercel.app/
**Date**: 2026-09-25 (UTC) · **Build verified**: production `index.html` is **byte-identical** to local build (md5 `74132629406d80cbadc08cd5130db1c6` both). Evidence below is production evidence.
**Method**: source analysis of served code + Node execution of the actual `demo()`, `renderTxList()`, `renderMonthView()` functions extracted from the served bundle.

**Spec requirement**: "Few, and fixed. Ten to twelve, not forty. Housing, Transport, Groceries, Dining, Subscriptions, Utilities, Health, Shopping, Entertainment, Debt, Transfers, Other. Subscriptions is deliberately top-level because it is the one the rest of the product acts on."

## A. The fixed set of 12 (definition-level assertions)

1. **PASS** — `TRACK_CATS` exists at `src/upmore-app-template.html:3622` as `["Housing","Transport","Groceries","Dining","Subscriptions","Utilities","Health","Shopping","Entertainment","Debt","Transfers","Other"]`.
2. **PASS** — It contains **exactly 12** entries (counted programmatically: 12 string literals).
3. **PASS** — The 12 match the spec's list **name-for-name and in spec order**: Housing, Transport, Groceries, Dining, Subscriptions, Utilities, Health, Shopping, Entertainment, Debt, Transfers, Other.
4. **PASS** — Not 11: all 12 spec names present.
5. **PASS** — Not 13: no 13th entry in the constant.
6. **PASS** — Subscriptions is top-level (index 4 of the 12), as the spec demands ("deliberately top-level").
7. **PASS** — Debt is present (spec includes Debt).
8. **PASS** — Transfers is present with the spec's plural spelling ("Transfers", not "Transfer").
9. **PASS** — Other is present as the catch-all.
10. **PASS** — No duplicates inside the constant.
11. **FAIL** — `TRACK_CATS` is **dead code**: it is defined at line 3622 and **referenced nowhere else** in the app (grep for `TRACK_CATS` returns exactly one hit — the definition). The fixed set does not drive the recategorize picker (none exists), the month view (which groups by `t.category` free-form), or any validation.

## B. No custom categories / no additions possible

12. **PASS** — No `<input>` anywhere in the transactions flow accepts a category name.
13. **PASS** — No "add category" button, link, or affordance exists in the transaction list screen, month view, or Home strip.
14. **PASS** — No `<select>` of categories exists anywhere in the app (all `<option>` elements in the bundle are Earn/deadline/outcome-related, none are Track categories).
15. **PASS** — No category picker, sheet, dialog, or modal exists for transactions (grep `sheet|dialog|modal|picker` ∩ `tx|categor|transfer` → only unrelated Earn promo-sheet hit).
16. **PASS** — The tx-list screen has exactly three controls: search input, month button, back button. No category management control.
17. **PASS** — No second category set competes with `TRACK_CATS`: per-name literal counts are Housing:1, Transport:3, Groceries:3, Dining:3, Subscriptions:4, Utilities:4, Health:2, Shopping:5, Entertainment:2, Debt:1, Transfers:1, Other:3 — all occurrences are the constant, demo-data literals, or comments. No 13th name anywhere.
18. **PASS** — No user preference / settings surface can add a category (no settings screen for Track exists).
19. **PASS** — Search cannot create a category: typing a novel string ("xyzabc") filters to zero rows, never adds anything.
20. **PASS** — LocalStorage has no category-addition path (no code writes a custom category list).
21. **PASS (vacuous)** — Nothing in the app can rename the 12 either.

## C. Transaction list — categories actually displayed (executed `renderTxList("")` on demo data: 210 tx)

22. **PASS** — Rows render as `merchant · category` + amount (matches spec's "date, merchant, amount, category" minus nothing essential).
23. **PASS** — Pending rows show a `pending` badge (verified in rendered HTML).
24. **FAIL** — The list displays **10 distinct category strings**, and one of them — **"Transfer" (singular)** — is **not in the fixed 12**. The demo transfer transaction (`demo-transfer-1`, line 3709) is hardcoded `category: "Transfer"` and renders as `Chase Transfer to Savings · Transfer −$500.00`.
25. **FAIL** — Consequence: a user sees a 13th category label in the product that contradicts the fixed set. The spec's name is "Transfers"; the visible label is "Transfer".
26. **PASS** — The other 9 displayed strings (Groceries, Dining, Transport, Shopping, Health, Entertainment, Subscriptions, Utilities, Other) are all within the 12.
27. **FAIL** — Because `TRACK_CATS` is dead code, nothing validates `t.category` — the bundle itself ships a non-conforming value ("Transfer") with no guard.
28. **PASS** — Month-view exclusions hold in the list path: no aggregate is computed from the list (it is a plain list), so pending inclusion in the list is presentation, not a totals violation.
29. **PASS** — The transfer row carries `is_transfer: true` in data (structural separation present at data level).
30. **FAIL** — But the *displayed category* of that row is not the spec's "Transfers" — data flag and display label disagree, so "transfer marking separate from categories" is muddled at the UI level: the transfer is *categorized* as "Transfer" rather than merely *flagged*.
31. **PASS** — List is capped at 100 rows of 210 demo transactions (truncation is pagination-by-cap, not category-related).
32. **PASS** — All 10 distinct categories appear within the first 100 rows (no category hidden by truncation in practice).
33. **PASS** — Every row's category string is non-empty; none render as blank/undefined.
34. **PASS** — Refund row (`demo-refund-1`, +$42.99 "Amazon Refund") displays category "Shopping" (within the 12) — no fabricated refund category.
35. **PASS** — Paycheck rows display "Other" (within the 12) — no fabricated income category.
36. **PASS** — Pending row displays "Shopping" (within the 12).

## D. Month view — spending by category (executed `renderMonthView()`)

37. **PASS** — Month view renders 8 category rows: Groceries, Shopping, Transport, Utilities, Entertainment, Dining, Health, Subscriptions.
38. **PASS** — All 8 are within the fixed 12. No extras.
39. **PASS** — "Transfer"/"Transfers" does **not** appear in month view (transfers correctly excluded by the `!t.is_transfer` filter — T6 rule holding).
40. **PASS** — "Other" does not appear in month view: paychecks (+$2,400 inflow) are correctly excluded by the `t.amount < 0` filter; refunds (+) likewise excluded.
41. **PASS** — No pending transactions contribute (filtered by `!t.is_pending`).
42. **PASS** — Rows are sorted by size (descending `thisM`), spec-compliant list, no pie chart.
43. **PASS** — Each row shows category, this month, average, delta with direction (spec: "category, this month, average, delta with direction").
44. **PASS** — Housing and Debt appear nowhere because demo data has none — acceptable; the fixed set permits empty categories.
45. **PASS** — Grouping key is `t.category` only; no second grouping dimension fragments the 12.
46. **PASS** — Month view is reachable via `txMonthBtn` → `monthview` screen (wiring at lines 1198/1210/1214 exists and is called).
47. **FAIL** — Month view's grouping is free-form `t.category`: if any transaction ever carries a non-12 category (as the demo transfer does), a 13th row would render with no validation. The dead `TRACK_CATS` never guards it.
48. **PASS** — No category in month view is editable/renamable in place.

## E. Recategorize — the layer-3 correction UI (spec: "user correction — always wins, permanently")

49. **FAIL** — **No recategorize UI exists.** Tapping a transaction row does nothing: `.txrow` divs carry `data-tx` attributes, but **zero event handlers** are bound to them (grep `data-tx` + `onclick|addEventListener|txrow` → no bindings).
50. **FAIL** — The code comment at line 3506 ("Tapping opens recategorize / mark-transfer / flag-wrong") is **aspirational/false**: it describes behavior that is not implemented.
51. **FAIL** — "Recategorize uses only the 12" is unverifiable because there is no recategorize path at all — the assertion cannot pass when the feature is absent.
52. **FAIL** — The `TRACK_CATS` constant — the only thing that *could* populate a 12-option picker — is referenced by no UI code, consistent with the picker never having been built.
53. **FAIL** — No "mark as transfer" control exists (same missing handler; `is_transfer` can only arrive from hardcoded demo data or the `/transfer/i` regex on live merchant names).
54. **FAIL** — No "flag as wrong" control exists (same missing handler).
55. **FAIL** — Spec's correction-loop steps 1–4 (recategorize tx, recategorize past same-merchant tx, create permanent rule, increment global counter) are entirely absent — `category_source` is `"provider"` on **100% of transactions** (verified: distinct sources = `["provider"]`).
56. **PASS** — `category_source` field exists in the data model with the spec's enum values ("provider"); layers "rule"/"user" are never populated, which is honest relative to the missing UI.
57. **FAIL** — Spec: "category_source records which layer decided, so a user can see why something was filed where it was" — the field is **never displayed** to the user anywhere.
58. **PASS** — Absence of the UI means no user *can* break the fixed set by correction — the "no custom categories" property is preserved by omission, not by enforcement.
59. **FAIL** — Because corrections don't exist, the spec's "categoriser improves with use" compounding asset does not exist.
60. **FAIL** — P2P ambiguity rule ("ask once per counterparty, then remember") has no ask UI, so no implementation path exists.

## F. Transfer marking separate from categories

61. **PASS** — `is_transfer` is a **separate boolean field**, not a category — the data model honors the separation.
62. **PASS** — All spending maths exclude `is_transfer` rows: Home strip payday detection, month view, `categorySpike`, recurrence detector, and safe-to-spend all filter `!t.is_transfer`.
63. **PASS** — `detectRecurrence` ignores transfers (a $500 savings move can't be detected as a subscription).
64. **PASS** — Month view excludes the transfer row (verified: no Transfer(s) row rendered).
65. **FAIL** — **No user-facing way to mark a transaction as a transfer.** The flag is set only by hardcoded demo data or by regex `/transfer/i` on the live merchant name (line 3453) — a user who spots a misfiled Venmo-to-self cannot fix it.
66. **FAIL** — The regex heuristic `/transfer/i.test(merchant_raw)` is exactly the kind of "provider is systematically wrong" fix the spec wants as a *rule*, but it is applied at ingest with `category: "Other"` + no user override path — misfiles are uncorrectable.
67. **FAIL** — The demo transfer's *displayed category* "Transfer" (≠ "Transfers") undermines the separation: the UI presents transfer-ness as a category label, not as the separate flag the spec requires.
68. **PASS** — Refunds are not categorized as income categories: the refund row keeps "Shopping" (spec: net against original, never count as income — no refund-as-income category exists).
69. **PASS** — No "Income" category exists in the 12 — consistent with the spec's set.
70. **FAIL** — Spec's transfer rule ("Transfers misfiled as spending … flag is_transfer, exclude from every spending total") cannot be user-triggered; only pre-flagged rows benefit.

## G. Live-data path (SimpleFIN) categorization

71. **FAIL** — Every live transaction is hardcoded `category: "Other"` with `// TODO: proper categorization` (line 3450). A connected user's entire month view collapses into one "Other" row — the fixed set is technically honored but the feature is a stub.
72. **PASS** — "Other" ∈ the 12, so no live-data category violates the set.
73. **FAIL** — Provider-enriched categories are discarded: the live transform ignores SimpleFIN's own category field and stamps "Other" + `category_source: "provider"` — the label lies (the provider decided nothing; the code did).
74. **FAIL** — ATM-withdrawal rule ("cash — its own category, explicitly uncategorisable — never guess") cannot be honored: with everything "Other", an ATM withdrawal is indistinguishable from a grocery run.
75. **FAIL** — Everything-stores / payment-processor / P2P / subscription-override rules cannot apply to live data because no per-merchant category exists to override.
76. **PASS** — Pending exclusion on live data uses the provider's `is_pending` (no category involvement).

## H. Search/filter by category

77. **PASS** — The tx-list search matches `t.category` case-insensitively: typing "dining" filters to 36 dining rows (verified in execution).
78. **PASS** — Typing "transfer" finds the 1 transfer row via category match ("Transfer" contains "transfer") — the search works on the non-conforming label too.
79. **PASS** — Typing a non-category ("xyz") yields zero rows; no phantom category is created.
80. **PASS** — There is no category dropdown filter — search is the only filter, so no dropdown can leak a 13th option.
81. **PASS** — Search matches merchant_raw as well (spec's "search and filter" satisfied at basic level).
82. **FAIL** — Because the transfer row's category is "Transfer" not "Transfers", searching "transfers" (plural, the spec name) returns **zero** rows — the fixed set's own name cannot find the transfer.

## I. Adversarial / edge assertions

83. **FAIL** — Case: a transaction with `category: "Transfer"` (singular) coexists with the spec's "Transfers" — the app ships this exact case in production demo data. Any future real "Transfers"-labeled row would render as a *second, distinct* row from the "Transfer" row.
84. **PASS** — Empty-string or null categories: none occur in demo data; renderer would print blank but no crash path (non-issue in practice).
85. **FAIL** — Two sources of truth for "the categories": `TRACK_CATS` (dead) vs `t.category` strings (live, unvalidated). The architecture does not enforce the fixed set anywhere.
86. **PASS** — No Earn-side categories leak into Track: Earn's `category` field (Bank Bonus, Referral Bonus, etc.) is a separate namespace, never rendered in Track views.
87. **PASS** — No Budget/Guide copy invents Track categories.
88. **FAIL** — The tx-list 100-row cap means a user with >100 transactions cannot see (or, if it existed, correct) older rows — categories on older transactions are unreachable.

## Verdict

**T5-v2: FAIL — 58 PASS / 30 FAIL.**

The fixed 12 are correctly *defined* (`TRACK_CATS`, exactly the spec's 12, dead-on), and the month view + transfer-exclusion math honor them. But:

1. **`TRACK_CATS` is dead code** — defined once, referenced zero times. Nothing enforces or even uses the 12.
2. **No recategorize / mark-transfer / flag-wrong UI exists** despite a code comment claiming tap opens them. The spec's entire layer-3 correction loop is absent; `category_source` is `"provider"` on 100% of rows.
3. **Production renders a 13th category label**: the demo transfer row shows `· Transfer` (singular), which is not in the fixed set; the spec's "Transfers" appears nowhere in the UI. Searching the spec name "transfers" finds zero rows.
4. **Live SimpleFIN data is all stamped `category: "Other"`** with a TODO — the categorization layer is a stub, making the month view and spike monitor single-row for any connected user.

**Blocking fixes** (in order):
- F1: Bind tap handlers on `.txrow` implementing recategorize (picker populated from `TRACK_CATS` only), mark-as-transfer (sets `is_transfer`, separate from category), and flag-wrong — or remove the false comment at line 3506.
- F2: Change demo transfer `category: "Transfer"` → `"Transfers"` (or leave category as the underlying merchant category and rely on `is_transfer`); validate all `t.category` against `TRACK_CATS` so a 13th label can never render.
- F3: Implement the correction loop (steps 1–4) with `category_source: "user"` and surface the source label; this is the spec's compounding asset and currently 0%.
- F4: Replace live-data `category: "Other"` stub with SimpleFIN's enriched category mapped into the 12 (fallback "Other"), instead of discarding provider categories.
- F5: Delete or wire up `TRACK_CATS` — a dead constant that *defines* the spec's key requirement but enforces nothing is worse than no constant.

No live-browser interaction was required or performed; all assertions derive from the production-served bundle (md5-verified identical to the deployed commit `b73da4f`) and direct execution of its functions.
