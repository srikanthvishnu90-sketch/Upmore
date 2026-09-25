# Agent E7 (Earn: Class Badges) — HARSH REPORT

**Verdict: FAIL**

## Method
Static analysis of the built production bundle (`index.html`) + catalog data (`src/data/upmore-data.json`) + read-only fetch of the live production page. As a subagent I cannot drive a live browser; the badge-rendering code path is deterministic and fully visible in the bundle, so this is conclusive, not inferential.

## Findings

### 1. Badge values are NOT the four spec classes — CRITICAL FAIL
Spec requires every route to carry exactly one of: **Fixed reward, Paid-if-selected, Variable, Non-cash**.

Catalog `earnings_class` values (1,990 routes):
- `"Count only actual received cash"` — 1,967 routes
- `"Speculative — $0 until withdrawn"` — 23 routes

The render code (`renderQueue`, built `index.html` line ~1921) does:
```js
const cls = r.earnings_class || "Fixed reward";
<span class="ebadge">${esc(cls)}</span>
```
It renders the raw catalog string verbatim. **Zero routes display a spec-compliant badge.** A user sees "Count only actual received cash" — a phrase that appears nowhere in the spec and maps to none of the four required classes. The fallback `"Fixed reward"` is dead code (no route lacks the field).

No mapping from catalog fields to the four spec classes was ever implemented.

### 2. No missing badges — PASS
All 1,990 routes have a non-empty `earnings_class`. The `|| "Fixed reward"` fallback never fires. Every Earn card renders exactly one `.ebadge` span.

### 3. No multiple badges — PASS
One `.ebadge` span per Earn card in the template. No code path renders two.

### 4. Non-cash never leads the queue — PASS (by exclusion, not by ranking)
The 23 non-cash routes (`cash_or_credit: "Restricted credit"`, e.g. Binance.US, Coinbase Advanced, Gemini) all sit in `lane: "Restricted"`. The queue only pulls `lane === "Standard"` (`stdRoutes()`), so restricted routes never enter the queue at all — they cannot lead it. This is stricter than the spec's "never lead" requirement. No violation, but note the spec's Non-cash class has no representation in the queue whatsoever.

### 5. Variable rewards shown as ranges — PASS
394 Standard-lane routes have `payout_min != payout_max`. `earnLine()` renders `≈$min–$max` (e.g. `≈$0–$250,000`). No single invented midpoint. However — the badge on these cards still reads "Count only actual received cash", not "Variable", so the class signal is wrong even where the number format is right.

## Summary
| Check | Result |
|---|---|
| Badge is one of the 4 spec classes | **FAIL** — 0/1990 compliant |
| No missing badges | PASS |
| No multiple badges | PASS |
| Non-cash never leads queue | PASS (excluded by lane) |
| Variable = range, not invented single | PASS |

## Required fix
Implement `specClass(route)` mapping catalog → spec class:
- `cash_or_credit === "Restricted credit"` → `Non-cash`
- `payout_min !== payout_max` (or reward text matches /up to|varies/i) → `Variable`
- Requirements text matches /selected|chosen|approved|accepted/i → `Paid-if-selected`
- Else → `Fixed reward`

Render that — not the raw catalog string. Then re-test.

## Note for parent
The live-browser portion of this task (visually confirming badges on the Home queue) could not be executed from this subagent — no live-browser capability. The code-path evidence above is deterministic and sufficient for the FAIL verdict, but a visual confirmation pass on production is still recommended before closing this item.
