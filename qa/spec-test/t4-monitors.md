# Agent T4 — Track: Monitors — HARSH REPORT

**Verdict: FAIL** (multiple critical defects; the monitor subsystem is non-functional)

**Method note:** I could not operate a live browser (subagents cannot launch browser tasks), so this is a code-level adversarial audit. Every finding is grounded in the exact JavaScript production serves — verified by fetching https://upmore-srikanthvishnu90-sketchs-projects.vercel.app/ and confirming the served page contains both `"omitted for brevity"` and `"2840.50"`. The verdicts do not depend on rendering; a browser pass would only confirm what the code proves.

**Spec baseline** (docspecs/04-track.md, "The monitors"): seven deterministic monitors run after every refresh, each emitting at most one card: new recurring charge, price increase, trial conversion, category spike, low balance ahead, duplicate charge, payday landed. Rules: evidence mandatory ("ComEd charged $184.20, up from $89.10 last month. Based on 3 months of Chase checking …4471"), one card per finding ever, dismissal permanent, silence is valid, never fire on pending, never state a behavioural conclusion, coverage window on every aggregate.

---

## FAIL 1 — 4 of 7 monitors do not exist (critical)

`src/upmore-app-template.html`, in the `TrackMonitors` object (line ~3460):

```js
// lowBalance, duplicateCharge, trialConversion, paydayLanded omitted for brevity —
// they follow the same evidence-mandatory, one-card-per-finding pattern.
```

Four of the seven required monitors — **low balance ahead, duplicate charge, trial conversion, payday landed** — are not implemented. "Omitted for brevity" is not a spec defense; it is an admission. The spec says "all seven together are a few hundred lines" — the lines were not written.

## FAIL 2 — The 3 implemented monitors are dead code: zero call sites (critical)

`TrackMonitors.newRecurringCharge`, `.priceIncrease`, and `.categorySpike` are defined but **never invoked anywhere in the app**. `grep "TrackMonitors\."` returns only the definition lines. No post-refresh pipeline calls them. They cannot fire, ever. They are decorative.

## FAIL 3 — No monitor output ever reaches the user (critical)

Because the monitors never run, no monitor cards are ever created or rendered. The spec's core value proposition — "A monitor finds something and pushes it into the queue" — does not happen. The cancel cards visible in the queue come from a separate ad-hoc path (`detectRecurrence` → `cancelCard` directly inside `buildQueue`), which is the Cancel spec's recurrence detection, not the Track monitor set. Conflating the two does not satisfy the spec.

## FAIL 4 — All monitors would operate on fabricated financial data (critical)

```js
function loadTrackData() {
  if (!trackData) trackData = TransactionSource.demo();
  return trackData;
}
```

The only data source is `TransactionSource.demo()`: 90 days of invented transactions (Netflix $15.99, Spotify $10.99, ComEd $89.10, Whole Foods $85.40…), a **fabricated checking balance of $2,840.50**, and fabricated $2,400 biweekly "Employer Payroll" inflows. The comment says "Plaid first, SimpleFIN fallback" and "Demo source provides sample data until a live connection exists" — but there is no live code path: `const hasLiveBank = false; // TODO: true when Plaid/SimpleFIN connected`, hardcoded. No Plaid Link token flow, no SimpleFIN proxy call in the client. The "Connect bank" button opens a sheet, but nothing behind it can produce a live connection.

Worse: the fabricated data is presented with **zero demo/sample labeling**. The Home strip shows the demo-derived "free cash" as if it were the user's real money; the transaction list renders invented purchases as the user's history; the month view aggregates invented spending. A user cannot tell any of this is fake. The spec's entire positioning is honesty; showing invented bank balances as real is the exact breach the spec's data-quality section exists to prevent.

## FAIL 5 — Implemented monitor output violates the format and evidence rules

Even hypothetically invoked, the three monitors emit cards with `title` + `body` + `evidence` — multiple sentences and multiple numbers per card — and **no timestamp field at all**. The spec's evidence rule requires the card to state what it was computed from *including the account and coverage window* ("Based on 3 months of Chase checking …4471"). The implemented evidence strings (e.g. `"Detected from transaction history (3 charges, 95% confidence)."`) name no account and no coverage window. Hard-never #3 — "Never show an aggregate without its coverage window" — is violated by construction.

## FAIL 6 — Duplicate charge: spec version not implemented

The spec's duplicate-charge monitor is: **same merchant, same amount, within 3 days → claim card**, evaluated on transactions. What exists is a pre-spec "detector 1" in `buildQueue` that groups *manually user-entered* `save_subscriptions` rows by merchant name alone — no same-amount check, no 3-day window, not on bank transactions. It does not satisfy the spec.

## FAIL 7 — Trial conversion, low-balance-ahead, payday-landed: absent entirely

- **Trial converting** ($0 charge from a new merchant + known trial length → deadline card): no such logic exists anywhere.
- **Low balance ahead** (projected balance before next payday falls below buffer → budget_alert card): `calcFreeCash` computes a number for the strip, but no monitor pushes a card into the queue.
- **Payday landed** (inflow matching detected pay pattern → budget_alert card): `renderTrackStrip` detects payday from demo payroll rows but emits no card.

## PASS 1 — No false "last checked today" claim

The spec doc itself called out this exact failure mode: *"The Money tab says 'Your AI money agent watches this daily' and 'Last checked today' … Until these monitors exist, that copy has to come out."* Grep of the full template for `last checked|checked today|lastChecked` returns **nothing**. The dishonest claim was removed. Credit where due.

## PASS 2 (trivial) — Silence is valid, and silence is all we get

Nothing fires, so the queue is monitor-silent. Consistent with "silence is a valid output," but for the wrong reason (dead code, not clean data on a quiet night).

---

## What must be fixed before this can pass

1. **Implement all seven monitors** — lowBalance, duplicateCharge, trialConversion, paydayLanded are not optional.
2. **Wire them into a real post-refresh pipeline** so they actually execute and push cards into the queue. Dead code is not a feature.
3. **Never present demo data as the user's money.** Until a live Plaid/SimpleFIN connection exists, Track surfaces must be gated or honestly labeled (e.g. "Connect your bank to turn on monitoring — figures shown are samples"). Fabricated balances in production are a trust-destroying defect.
4. **Every monitor card needs:** evidence naming the account and coverage window, exactly one card per finding with permanent dismissal, a computed timestamp, and exclusion of pending transactions.
5. **Implement the spec versions** of duplicate charge (same merchant + same amount + within 3 days, on transactions), trial conversion ($0 + trial length → deadline card), low-balance-ahead (projected balance < buffer → budget_alert), and payday-landed (pay-pattern inflow → budget_alert).

**Bottom line:** The Track monitors are 3-of-7 written, 0-of-7 running, 0-of-7 on real data. This is not a partial implementation; it is a non-functional subsystem wearing the spec's clothes.
