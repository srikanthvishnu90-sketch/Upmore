# Agent T5 — Track: Categories — HARSH REPORT

**Commit tested:** `0c2eb30` (template `src/upmore-app-template.html` + built `index.html`, the deployed artifact)
**Method:** Source-code inspection of the exact deployed build. (Browser tasks are unavailable to this agent; for this task — counting categories, checking for add-category UI, checking for uncategorized paths — code inspection is definitive. A visual pass can confirm, but cannot contradict these findings.)
**Date:** 2026-09-25

## Verdict: CONDITIONAL PASS — the 12-category set is spec-perfect on paper and unenforced in practice

---

## What the spec demands (04-track.md, "What categories to use")

> "Few, and fixed. Ten to twelve, not forty. Housing, Transport, Groceries, Dining, Subscriptions, Utilities, Health, Shopping, Entertainment, Debt, Transfers, Other."

Plus: no user-added categories; enriched names are display-only with the underlying category key fixed; the transaction list must let the user recategorise on tap.

## Finding 1: The declared set is exactly right — 12/12, verbatim, in spec order ✅

`TRACK_CATS` (template line 3321, present identically in built `index.html`):

```
["Housing","Transport","Groceries","Dining","Subscriptions","Utilities","Health","Shopping","Entertainment","Debt","Transfers","Other"]
```

Count: 12. Names: exact spec match, including the deliberate top-level `Subscriptions`. **PASS.**

## Finding 2: You cannot add a custom category — because you cannot do anything with categories at all ✅/⚠️

- Zero `<select>`, input, or picker elements reference categories anywhere in the app. The only selects in the codebase are for state, subscription interval, deadline kind, and ledger type.
- Zero occurrences of "uncategorized"/"Uncategorized" in template or built file.
- So: no custom categories possible. **PASS on the letter of the requirement.**

## Finding 3: `TRACK_CATS` is DEAD CODE — referenced exactly once (its own declaration) ❌

`grep -c TRACK_CATS` on the built `index.html`: **1** — the declaration itself. It is:

- Not used by the transaction list (`renderTxList` just renders `t.category` raw).
- Not used by the month view (`renderMonthView` / `categorySpike` build keys from whatever `t.category` happens to be).
- Not used by search/filter (filter matches `t.category` as free text).
- Not used anywhere else.

The "fixed set" is fixed only in the trivial sense that no code path can violate it — because **no code path references it**.

## Finding 4: The spec-required recategorise UI does not exist ❌

Spec: *"Tapping a transaction lets the user recategorise, mark it as a transfer, or flag it as wrong."*

Reality: template line 3208 is a code comment — `// Tapping opens recategorize / mark-transfer / flag-wrong.` — with **no click handler** on `.txrow` (only CSS classes at lines 400–404 and the row renderer at 3216). Tapping a transaction does nothing. The entire correction loop the spec describes (recategorise → applies to merchant → global correction table, `category_source` enum) is absent: no `category_source` field, no layer-2/3 rules, no enriched-name handling.

This means the "no user-added categories" constraint is currently satisfied **by absence of the feature**, not by enforcement. The moment a recategorise UI is built, there is no constant backing it — whoever builds it will likely hardcode a new list or, worse, free-text.

## Finding 5: No provider→12 normalization layer exists ⚠️

Demo transactions use 8 of the 12 (Dining, Entertainment, Groceries, Health, Shopping, Subscriptions, Transport, Utilities) — all within the set, none outside. But month view and the tx list key directly off `t.category`. When live SimpleFIN/Plaid data arrives (Plaid has dozens of enriched categories), any 13th category will render raw in the UI with nothing mapping it to the fixed 12. The spec's "provider-supplied, then overridden" column design has no corresponding code.

## Answers to the four mission questions

1. **How many categories?** Exactly 12, verbatim spec match. ✅
2. **Can you add a custom category?** No — no UI exists for it. ✅ (vacuously)
3. **Are transactions assigned to the 12, or are there uncategorized/custom?** All assigned transactions are within the 12; no "uncategorized" exists. ✅
4. **Are the names sensible and fixed?** Names match spec. "Fixed" is **not enforced** — the constant is unreferenced dead code and there is no normalization layer. ⚠️

## Required fixes (for parent to queue)

1. **Wire `TRACK_CATS` into the recategorise UI when it is built** — the picker must offer exactly these 12, no free text, no "add new."
2. **Add a provider-category → 12 mapping layer** before live data ships, or the first Plaid/SimpleFIN sync will display categories outside the fixed set.
3. **Build the tap-to-recategorise / mark-transfer / flag-wrong interaction** — currently a comment; the spec requires it, and T2 will fail on it independently.
4. Consider asserting in `renderMonthView`/`renderTxList` that `t.category` is in the 12 and falling back to `Other` — cheap enforcement until the real layer exists.

## Bottom line

The category list itself is a 12/12 spec match — the one thing this agent was asked to count. But it survives as a decorative constant: unreferenced, unenforced, with no UI behind it and no normalization in front of it. **Conditional pass** — correct declaration, missing machinery. Do not let "12 categories, spec match" be quoted as a clean bill of health for Track categorisation.
