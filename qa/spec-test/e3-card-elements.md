# Agent E3 — Earn 8-Element Cards: HARSH AUDIT

**Verdict: FAIL** — 4 hard spec violations, 3 warnings.

**Method note:** As a subagent I cannot launch live browser tasks, so this is a
deterministic static audit of `src/upmore-app-template.html` (the exact code that
builds to production) plus `src/data/upmore-data.json` (1,990 routes). Every claim
below cites a line number or a data query. Code doesn't lie about what it renders.

**Card under test:** the queue Earn card rendered by `renderQueue()` (~line 1890).

---

## Element-by-element (spec order: 1–8)

| # | Spec element | Implementation | Verdict |
|---|---|---|---|
| 1 | Provider / description | `<h4>` = `routeTitle(r)` = "Provider — method" | **PASS** |
| 2 | Exact terms-stated reward | `<p class="qm">` = `routeMeta(r)` = raw `r.reward` string, verbatim, unmodified | **PASS** (code) — but see data warning W2 |
| 3 | Class badge | `<span class="ebadge">` shows `r.earnings_class` | **FAIL (hard)** |
| 4 | Requirement checklist | `<p class="ereq">` "Requires:" + `r.requirements` | **PASS** |
| 5 | Honest catch | `<p class="ecatch">` "The catch:" + `r.catches` | **PASS** (content is genuinely honest, not fluff — e.g. Microsoft bug bounty: "most hunters earn nothing per report"; JM Bullion: "this is liquidation of an asset, not earnings from nothing") |
| 6 | Active minutes | Merged into `<p class="emeta">`: "≈20–45 min active" | **PASS with warning** (see W1) |
| 7 | Payout timing, observed median or clearly labelled advertised | Same merged `<p class="emeta">` line, raw `r.payout_timing` with **no observed/advertised label** | **FAIL (hard)** |
| 8 | Plain verification date/age | `<span class="vbadge">` shows the **state** "unverified" — not a date, not an age | **FAIL (hard)** |

## Hard fails

**F1 — Element 3 uses the wrong taxonomy.** The spec's four classes are Fixed
reward / Paid-if-selected / Variable / Non-cash. The data's `earnings_class`
values are `Count only actual received cash` (1,967 routes) and
`Speculative — $0 until withdrawn` (23 routes). The badge renders these
verbatim, so no card ever shows a spec-compliant class. Additionally, the
fallback `r.earnings_class || "Fixed reward"` (~line 1897) would *invent* a
class for any route missing the field.

**F2 — Element 8 shows a state, not a date/age.** The spec demands "plain
verification date/age" (e.g. "verified 12 days ago"). The badge shows the
static string "unverified". Worse: **zero routes** in the catalog carry any
verification field, date field, or capture-date field (queried all keys —
nothing date-ish exists). Element 8 is unimplementable from current data; the
badge is decorative.

**F3 — Element 7 has no observed/advertised distinction.** `r.payout_timing`
(e.g. "Match paid in cash within 5 business days…") is rendered raw with no
label. The spec requires "observed median **or clearly labelled advertised**".
Every payout timing shown is implicitly presented as fact with no provenance.

**F4 — Elements are out of order.** Rendered visual order is 1, 2, 3, **8**, 4,
5, 6+7: the verification badge (`vbadge`) sits second inside the `.earn8` div
(~line 1901), *before* Requires / Catch / Meta. The spec says "exactly eight
**ordered** elements". The card does not follow the order.

## Warnings

**W1 — Elements 6 and 7 are merged** into one `<p class="emeta">` line
("≈20–45 min active · <timing>"). Two spec elements share one visual row. Minor,
but "exactly eight ordered elements" suggests eight distinct rows.

**W2 — Element 2 data quality.** The reward string is verbatim (good — nothing
invented), but some `reward` fields contain no reward figure at all. Example:
JM Bullion's "reward" is *"Payment is typically issued in 1-3 business days
from the time your items have been verified…"* — that's payout-timing text
sitting in the reward slot. The card faithfully shows it, which means element 2
sometimes displays non-reward text *as* the reward.

**W3 — Queue why-line reads like a promise on "up to" offers.**
`$250000 x 30% x 1 / 165 min` (Microsoft bug bounty, "Earn up to $250,000")
uses `qDollars = payout_max` for ranking math. The format is the spec-mandated
score decomposition, so this is not a code violation — but on variable/up-to
offers the leading max figure scans as a projected total, which the spec's omit
list is trying to prevent.

## Forbidden-element sweep

- **Projected route totals:** none rendered as promises in the queue card. (W3 aside.)
- **Derived hourly rates:** **VIOLATION on adjacent surfaces.** `earnLine()`
(~line 1091) computes `≈X/min` from `earn_ratio` and renders it in the Explore
search cards (~line 2959: `<span class="xearn">`) and the walkthrough intro
(~line 1587: "Why this one: … · ≈Z/min"). A per-minute derived rate is the same
species as the banned derived hourly rate. The 8-element queue card itself does
not show it — but the ban is on the Earn card family, and two of three Earn
surfaces break it.
- **Fake scarcity / countdowns:** none in templates. Reward strings containing
real deadlines ("ends Sept 30, 2026") are verbatim terms text, not invented
urgency. **PASS.**
- **Rounded/annualised/combined reward figures:** element 2 is verbatim, not
rounded. **PASS** for the card. (The `≈` prefix appears only on active-minutes
ranges.)

## Data-taxonomy issue (upstream of the card)

The Robinhood Referral route pays in **stock** (not cash, 3-day sale lock, 60-day
withdrawal lock) yet is classified `Count only actual received cash`. Per the
spec that is **Non-cash**: "kept separate from extractable cash and never
allowed to lead the queue." The card renders the badge it's given, so this is a
catalog misclassification — but it means a non-cash route can currently lead the
queue wearing a cash badge.

## Required fixes (priority order)

1. Map the catalog's two `earnings_class` values onto the spec's four classes
   (or add a proper `class` field) — F1. Every card's badge is wrong today.
2. Move the verification badge to position 8 and render a real date/age once
   verification data exists; until then label it honestly, e.g. "not yet
   verified — no check date" — F2, F4.
3. Label every payout timing as observed-median or advertised — F3.
4. Remove `≈X/min` from `earnLine()` (or restrict `earnLine` to never show the
   rate component) — derived-rate ban.
5. Split `.emeta` into two rows (active minutes / payout timing) — W1.
6. Fix `reward`-slot data for routes whose reward text isn't a reward (W2) and
   reclassify stock/crypto-paying routes as Non-cash (taxonomy issue).
