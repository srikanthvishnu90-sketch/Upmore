# Agent C5 — Cancel: waste_score Ranking — HARSH TEST REPORT

**Verdict: FAIL** (2 critical/high, 2 medium, 2 low)

**Method note**: As a code-level auditor with full source access, I executed the
shipped implementation (`wasteScore`, `renewalUrgency`, `detectRecurrence`) in
Node against the shipped demo transaction data. This is ground truth — no UI
interpretation needed. Browser-based ranking checks were impossible because,
as Finding #1 shows, no cancel cards can appear at all.

**Spec under test** (Doc 2, Cancel):
`waste_score = annual_cost × (1 - usage_signal) × renewal_urgency × confidence`
Higher waste ranks first. Renewal urgency 1.0 if billing within 7 days,
decaying to 0.3 at 60+ days.

---

## Finding #1 — CRITICAL: The Cancel pipeline never fires. Zero cancel cards, ever.

**Evidence**: Ran `detectRecurrence(TransactionSource.demo().transactions)` —
returns **0 recurring subscriptions**. The monitor loop in `buildQueue`
therefore pushes zero cancel cards. The `wasteScore` ranking code is dead code
in the shipped product.

**Root cause**: The demo transaction generator (`TransactionSource.demo()`)
produces unrealistic billing patterns. Netflix — which should bill ~monthly —
appears on these dates with these gaps:

```
2026-07-02, 2026-07-07, 2026-07-11, 2026-07-16, 2026-07-25, ...
Gaps (days): 5, 4, 5, 9, 14, 5, 5, 4, 5, 9, 14, 5
```

The detector correctly requires ≥75% of gaps in the monthly band (28–31d).
These gaps are 4–14 days — pure noise from the round-robin generator
(`merchants[(day*3+i) % 14]`). The detector is working as specified; the
**data is wrong**.

**Why this is critical**: Every downstream question — "are cards ranked by
waste?", "does tomorrow outrank 60-days-out?", "is low-value clutter
filtered?" — is **untestable**. The feature cannot be validated end-to-end,
by QA or by the user. The spec's own build order demands correctness on
sandbox/demo data before live data; this fails that bar.

**Fix**: Make the demo generator emit realistic recurring charges —
Netflix/Spotify/ComEd on true monthly cadence (±2 days jitter), so the
detector finds 3+ subscriptions and the ranking is exercisable.

---

## Finding #2 — HIGH: `usage_signal` is hardcoded to 0.5. The formula's core term is a constant.

**Evidence** (`src/upmore-app-template.html:1771`):
```js
const score = wasteScore(annual, 0.5, renewalUrgency(days), s.confidence);
```

The spec's entire point of `waste_score` is that an **unused** $15/mo
subscription outranks a **heavily used** one. With `usage_signal = 0.5` for
every subscription, the `(1 - usage_signal)` term is a constant 0.5 — it
contributes nothing to differentiation. A subscription used daily ranks
identically to one never touched, at equal cost and urgency.

**Spec conflict**: Doc 2 says "Never claim non-usage — ask." Hardcoding 0.5
doesn't *claim* non-usage, but it silently discards the question instead of
asking it. The honest implementation asks the user ("Do you still use
Netflix?") and uses the answer; until then the neutral default must be
documented, not buried in a call site.

**Fix**: Prompt for usage on the cancel card (one tap: still using / rarely /
never) and feed it into the score. At minimum, name the constant and its
provisional status in code comments and in the card's "why" line.

---

## Finding #3 — MEDIUM: `waste_score` is computed but never used for ranking.

**Evidence**: The score gates entry (`if (score < 30) return;`) but ordering
comes from the global queue sort:
```js
cards.forEach(c => { c.score = qScore(c.dollars, c.conf, c.urg, c.eff); });
cards.sort((a, b) => b.score - a.score);
```
where `qScore = dollars × conf × urg / eff`.

Today the two orderings happen to be proportional — but **only because**
Finding #2 makes `(1 - usage_signal)` constant across all cards. The moment
usage becomes real, the queue ranking will silently ignore it while the code
*appears* to implement waste-based ranking. This is a latent correctness bug.

**Fix**: Either sort cancel cards by `waste_score` explicitly before the
global interleaving, or fold `(1 - usage_signal)` into the card's `urg`/`conf`
so the global formula respects it. Delete the misleading comment
"Deterministic: detectRecurrence → wasteScore rank" — it does not rank.

---

## Finding #4 — MEDIUM: The `< 30` entry threshold is invented, not in the spec.

**Evidence** (`:1772`): `if (score < 30) return; // only material waste enters the queue`

Doc 2's monitors say "emits at most one card" — no minimum-waste threshold is
specified. Worked example: a $5/mo ($60/yr) subscription, billing in 45 days
(urgency 0.3), confidence 0.95 → `60 × 0.5 × 0.3 × 0.95 = 8.55` → **filtered
out, user never sees it**. A $60/yr leak is exactly the kind of thing this
feature exists to surface.

The threshold may be defensible product judgment, but it is undocumented,
untested against user expectations, and interacts badly with Finding #2
(the 0.5 constant halves every score before the threshold is applied).

**Fix**: Document the threshold rationale, or replace with a spec-grounded
rule (e.g., annual cost > $24). Add a test pinning the boundary behavior.

---

## Finding #5 — LOW: The "why" line does not explain the ranking.

**Evidence**: `why: \`$${annual}/yr × ${conf}% × ${urgency} / ${eff} min\``

Shows four factors but never names `waste_score`, never discloses the 0.5
usage assumption, and never states the score that determined entry. A user
cannot tell *why this card outranks that one*. The spec demands evidence on
every card; the ranking itself is currently unexplained.

---

## Finding #6 — LOW: `renewalUrgency` intermediate bands are invented.

Spec: "1.0 if billing within 7 days, decaying to 0.3 at 60+ days."
Implementation: ≤7d → 1.0, ≤14d → 0.8, ≤30d → 0.6, else 0.3.
The 0.8/0.6 steps are reasonable interpolation but are not in the spec and
are unpinned by any test. Minor; document or test.

---

## Direct answers to the mission questions

| Question | Answer |
|---|---|
| Are cancel cards ranked by waste? | **Unverifiable** — no cards appear (Finding #1). Code computes waste_score but sorts by the global formula (Finding #3). |
| Does billing-tomorrow outrank billing-in-60-days? | **Unverifiable** — no cards. In theory yes: urgency 1.0 vs 0.3 flows into both waste_score and qScore. |
| Does the "why" line show the factors? | **Partially** — shows $/yr, confidence, urgency, effort; omits waste_score and the usage assumption (Finding #5). |
| Are low-value subscriptions cluttering the queue? | **No** — nothing appears. But the `< 30` filter that prevents clutter is arbitrary (Finding #4). |

---

## Required fixes (in order)

1. Fix the demo generator to emit realistic monthly recurring charges so the
   detector finds ≥3 subscriptions and the ranking is exercisable. **Without
   this, the feature is unshippable.**
2. Replace the hardcoded `usage_signal = 0.5` with a user-asked usage input
   (or document the provisional constant and its effect).
3. Make `waste_score` actually drive cancel-card ordering, not just entry
   filtering — or remove the misleading "wasteScore rank" comment.
4. Document and test the `< 30` threshold (or replace with a spec-grounded rule).
5. Name `waste_score` and its inputs in the card's "why" line.

**Re-test after fix**: Re-run `detectRecurrence` on fixed demo data (expect
≥3 subscriptions), verify queue order matches descending waste_score, verify
a tomorrow-billing subscription outranks a 60-day one at equal cost.
