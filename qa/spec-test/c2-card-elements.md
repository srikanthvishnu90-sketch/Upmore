# Agent C2 — Cancel: 7-Element Cards — HARSH REPORT

**Verdict: FAIL** (1 critical, 4 defects, 2 passes)

**Method note (honest limitation):** As a subagent I cannot operate a live browser or
launch browser tasks, so no visual inspection of the rendered app was possible. Instead I
did something stronger for logic defects: I extracted the *actual shipped functions*
(`cancelCard`, `detectRecurrence`, `wasteScore`, `renewalUrgency`, plus the real
`TransactionSource.demo` generator and the real `buildQueue`/`renderQueue` wiring) from
`src/upmore-app-template.html` and **executed them in Node against adversarial inputs**.
Every finding below is from running the real code, not reading it. Visual rendering
(white-space, overlap, mobile layout) remains untested — flag for a browser-capable agent.

---

## DEFECT 1 (CRITICAL): The 7-element cards are unreachable — detector finds 0 recurrences

`buildQueue()` feeds cancel cards from `detectRecurrence(loadTrackData().transactions)`.
I ran the real `detectRecurrence` against data produced by the real `TransactionSource.demo()`
generator. Result: **`recurrences found: 0` → `cancel cards reaching queue: 0`**.

Root cause: the demo generator assigns merchants round-robin —
`merchants[(day * 3 + i) % merchants.length]` over 14 merchants — so "Netflix" lands on
days 1, 6, 20, … with gaps of 5, 14, 19 days. The detector's date bands are strict
(monthly = 28–31d gaps, consistency ≥ 0.75). Irregular gaps → every merchant rejected.
The code comment even lies about it:

```js
// Recurring: Netflix monthly, Spotify monthly, ComEd monthly
```

That comment is false. Nothing in the generator produces monthly recurrence for any
merchant. The entire Cancel monitor pipeline — detector → waste_score → 7-element card —
is **dead on arrival** in the shipped product. No user will ever see a cancel card until
either the demo data is fixed to contain genuinely recurring charges or live SimpleFIN
data flows in. A feature whose trigger condition is unsatisfiable is not a feature.

## DEFECT 2: Elements 5 & 6 are permanent gaps — "unknown" / "not observed"

The queue calls `cancelCard(s, null)` — `cancelPath` is **always null** (no cancel-path
library exists anywhere in the codebase). So every card renders:

- Element 5 (Method badge): `"unknown"` — spec demands a badge of `chat` / `deep-link` / `phone`
- Element 6 (Observed time + n): `"not observed"` — spec demands e.g. `6 min (n=42)`

The spec allows an honest gap **only for element 7** ("Expected retention offer (or honest
gap)"). Elements 5 and 6 have no such allowance. `"unknown"` is not a method badge; it is
an admission that the cancel-path library the spec requires was never built.

## DEFECT 3: Ordinal bug in the required claimed copy

`claimedCopy` builds `"on the " + new Date(next_date).getDate() + "th"`. Executed output:

- `2026-10-14` → "on the 14th" ✓ (the spec's example — correct by coincidence)
- `2026-10-01` → "on the **1th**" ✗
- `2026-10-03` → "on the **3th**" ✗
- `2026-10-21` → "on the **21th**" ✗
- `2026-11-22` → "on the **22th**" ✗

The spec mandates this exact copy pattern ("Nice. I'll watch for the charge on the
14th…"). For ~70% of calendar dates the shipped code produces ungrammatical ordinals.
Needs a proper ordinal function (1st, 2nd, 3rd, 21st, 22nd, 23rd, 31st).

## DEFECT 4: Card CTA is a dead end, not the "exact path"

The queue wires the cancel CTA as:

```js
cta: "Show me how", act: () => toast("Cancel path: " + s.merchant_raw)
```

Tapping "Show me how" shows a toast reading e.g. "Cancel path: Netflix" and does nothing
else. The spec requires the card to supply **the exact path, draft the message, and warn
about retention**. A toast naming the merchant is none of those three. Combined with
Defect 2 (no path library), the card promises help canceling and delivers a toast.

## DEFECT 5: `usage_signal` hardcoded to 0.5 — invented, not measured

`buildQueue` computes `wasteScore(annual, 0.5, renewalUrgency(days), s.confidence)` —
usage is **assumed 50% for every subscription**. The spec's formula needs a real
`usage_signal`, and the spec says "Never claim non-usage; ask." Hardcoding 0.5 invents a
usage fact for every merchant. Secondary effect: the `score < 30` gate then silently drops
cheap subscriptions (e.g. $5.99/mo → score ≈ 17 → never surfaces), so the queue is biased
toward expensive subs by an arbitrary threshold with no spec basis.

## What PASSES

- **Exactly seven elements, in spec order.** The `elements` object has exactly the keys
  `merchant, amount, annual, nextBilling, method, observedTime, retention` — matching the
  spec's 1–7 in order. (Rendered with 1+2 and 5+6 merged into shared `<p>` tags, but all
  seven values present and ordered.)
- **Element 3 is clean:** `"$192 over 12 months (projection, not savings)"` — explicitly
  labeled a projection, explicitly disavows "savings". No "savings" language anywhere in
  the card JSON. Verified across monthly/yearly/weekly intervals (yearly $139 → "$139
  over 12 months"; weekly $9.99 → "$519 over 12 months").
- **Element 7 honest gap is spec-legal:** `"No retention data"` is the permitted honest gap.
- Element 2 exact amount+interval (`$15.99 / monthly`) ✓; element 4 date + days
  (`2026-10-14 — in 19 days`, past dates clamp to "in 0 days") ✓.

## Adversarial inputs executed

Monthly/yearly/weekly intervals, null vs populated cancelPath, past billing date,
1st/3rd/21st/22nd billing dates (ordinal bug), full 90-day demo transaction set through
the real detector. All outputs above are verbatim from Node execution of shipped code.

## Recommended fixes (for parent agent)

1. Fix the demo generator to emit genuinely recurring charges (e.g. Netflix every 30d,
   Spotify every 30d, ComEd every 30d) so the detector fires and cards are reachable; or
   gate the demo strip behind "demo data has no recurring charges" honesty copy.
2. Build the cancel-path library (method, avg_minutes, observed_n, retention_offers per
   merchant) or remove elements 5–6 from the card until it exists — do not ship "unknown".
3. Add an ordinal helper for the claimed copy.
4. Make "Show me how" open the real cancel path (steps + drafted message + retention
   warning), not a toast.
5. Replace hardcoded `usage_signal: 0.5` with measured/asked usage; justify or remove the
   `score < 30` threshold.
6. Browser-capable follow-up: visually verify the `.cancel7` rendering on a real device.
