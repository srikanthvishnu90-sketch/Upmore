# X1 — Cross-Spec Integration (HARSH)

**Date:** 2026-09-25 (UTC)
**Target:** production commit `7c0c795` (verified live — sw.js cache stamp `upmore-7c0c795`)
**Method note:** As a generic subagent I cannot operate a live browser. I did something
stronger instead: a line-by-line audit of the exact template source that builds the
deployed app (`src/upmore-app-template.html`, the only file `build-app.py` compiles).
Every finding cites file + line. Nothing below is inferred from UI screenshots.

**Verdict: FAIL — 9 findings, 3 of them critical. Do not ship "all done" on this.**

---

## What actually passes

- **Exactly 3 tabs.** `TABS` (line 1146) = Home, Guide, You ("profile"). Every
  `<nav data-nav>` renders from that one array (line 1155). `transactions` and
  `monthview` are sub-screens with back buttons, not tabs. Track stays
  infrastructure. **PASS.**
- **Queue formula mechanics.** `qScore(dollars, conf, urg, eff) = dollars × conf × urg / eff`
  (line 1693); every card gets `.score` and the queue sorts desc (line 1897).
  Matches the spec formula. **PASS** (the inputs are disputed — see F6/F7/F8).
- **Track → Cancel is really wired.** `buildQueue()` calls `loadTrackData()` →
  `detectRecurrence()` → `wasteScore()` → `cancelCard()` → queue cards (lines
  1729–1745). Not decoration. **PASS** (the data is fake — see F1).
- **wasteScore formula** matches spec: `annualCost × (1 − usageSignal) × renewalUrgency × confidence`
  (line 3059). **PASS** (the usage input is invented — see F8).
- **Cancel card element 3** says `$X over 12 months (projection, not savings)` (line 3092).
  The spec's exact wording requirement is met. **PASS.**
- **Budget's 4 required elements** all render: total, daily pace, buffer on its own
  line, cycle-end date (`stsTotal`, `stsSub`, lines 3219–3223). **PASS** (computed
  from fake data — see F1).
- **Month-view coverage** states its window: `From X to Y — every aggregate states
  its coverage` (line 1207). **PASS.**
- **Track strip mechanics**: 3 numbers (free cash, days to payday, left to spend),
  tap opens the transaction list (line 1211). **PASS** (numbers are fiction — F1).

---

## FAIL findings

### F1 — CRITICAL: every money number in production is fabricated
`loadTrackData()` (line 3195): `if (!trackData) trackData = TransactionSource.demo();`
— unconditional. The demo source (line 3353) invents: a **$2,840.50** checking
balance, **$2,400** biweekly "Employer Payroll", 90 days of Whole Foods / Netflix /
Spotify / ComEd transactions. No string anywhere in the UI says demo, sample, or
example. The Home strip, Safe to Spend, transaction list, month view, cancel
detection, and monitor output all present invented figures as the user's own money.
Meanwhile: `hasLiveBank = false; // TODO: true when Plaid/SimpleFIN connected`
(line 3227), SimpleFIN exists only in comments, and the Plaid connect surface is a
stub. The vaulted SimpleFIN Access URL is never read by anything. **This one fact
invalidates every cross-spec money claim in production.** Nothing downstream can be
trusted until a live source replaces `demo()`.

### F2 — CRITICAL: Earn gates run on fictional inputs
`buildQueue()` hardcodes (line 1724):
`gateUser = { age: 19, state: "IL", free_cash: 5000, free_minutes: 60, accounts: [] }`.
Two lines above, the same function already fetched `planData()` (line 1430), which
carries the user's **real** state, free-time minutes, and cash-available from
onboarding/dbProfile (lines 1432–1436). The gates ignore all of it. Worse: onboarding
collects name, state, hours/week, paycheck status, cash-to-park (line 986) — **age is
never collected**, so Gate 1 (age) can never be evaluated against a real value for any
user. Every gate decision in production is computed against fiction.

### F3 — Capital suppression is dead code
`capitalSuppressed(freeCash, overdraftsLast60d)` (line 3143) has **zero callers**.
The Guide chat path that fires on "what should I invest in" (line 2854) carries a
comment — `// Suppress entirely if free cash negative or recent overdrafts (spec).` —
and then calls `capitalRefusal()` unconditionally. An overdrawn user gets the Capital
refusal instead of the total suppression the spec requires.

### F4 — CRITICAL: the verification system never verifies
- No route in the catalog carries a `verification` field (grep over the whole file:
  only code references, zero data). Every Earn badge therefore renders the fallback
  `"unverified"`.
- `verifyRoute()` (line 3131) has **zero callers**. Nothing is ever promoted to
  confirmed or demoted to stale; the 30-day rule and terms-hash rule never execute.
- The freshness gate explicitly **passes** unverified routes
  (`route.verification === "confirmed" || route.verification === "unverified"`,
  line 3118), so unverified routes can lead the queue and enter walkthrough plans.
- Card element 8 (verification **date/age**) is absent — the badge shows a state word
  with no date. The spec's 8-element card is really a 7.5-element card.

### F5 — Cancel "Show me how" is a toast
Detected-subscription cancel cards wire their CTA to
`() => toast("Cancel path: " + s.merchant_raw)` (line 1743). There is no cancellation
path library: `cancelCard(s, null)` is always called with `null`, so the 7-element
card permanently renders **"unknown"** (method), **"not observed"** (observed time),
**"No retention data"** (retention) — 3 of 7 elements are stubs. No claimed-state
persistence, no charge watch, no Avoided ledger write, no reversal on re-charge.

### F6 — Earn urgency is not `urgency(days_to_deadline)`
Spec formula: `urgency(days_to_deadline)`. Implementation (line 1728):
`r.speed === "today" ? 2 : r.speed === "days" ? 1.5 : 1`. A route with a hard deadline
2 days out and one with a 60-day deadline both score urg=1 when neither is tagged
"today"/"days". The deadline-driven urgency the spec requires does not exist for Earn.

### F7 — Scoring invents a number for variable rewards
`qDollars = r => Number(r.payout_max ?? r.payout_min ?? 0)` (line 1706). A
"$50–$500 variable" route **scores as $500**, outranking fixed routes it should lose
to. The spec says show ranges and never invent a single number; ranking on the max is
inventing a number where it matters most — order.

### F8 — `usage_signal` is invented, not asked
`buildQueue` passes a hardcoded `0.5` as usage_signal into `wasteScore` (line 1735).
The spec is explicit: the app cannot know usage — it must ask, never claim. The card
copy correctly avoids claiming non-usage, but the ranking silently assumes every user
uses every subscription exactly half. (Secondary: `renewalUrgency` decays to 0.3 at
30+ days, line 3066; the spec says 60+.)

### F9 — Claimed-copy ordinal bug
`claimedCopy` (line 3101): `` `on the ${new Date(sub.next_date).getDate()}th` ``
renders "on the 1th", "on the 2th", "on the 3th". Small, real, user-visible.

---

## Observations (not FAILs, but harsh notes)

- The queue mixes **8 card types** (earn, cancel, continue, claim, duplicate, spike,
  renewal, deadline). The 4 specs describe Earn + Cancel. The extras are legacy
  features that predate the specs — defensible to keep, but "very very very simple
  complexity" is strained by an 8-type queue.
- `qConf` = 0.7 if a "researched" flag is set else 0.4 (line 1707) — arbitrary
  constants, not verification-derived. The spec doesn't fix confidence values, so this
  is a smell, not a violation.
- Home is dense (track strip + safe-to-spend + queue + explore + tracker). The tab
  count and single-queue structure are the simplicity wins; the Home surface is where
  "very very very simple" is most at risk.

---

## Bottom line

The integration **skeleton** is correct: one ranked queue, the spec formulas, Track
feeding Cancel, Budget reading Track, 3 tabs, no fourth Track tab. But the skeleton
is carrying **fictional blood**: fake money (F1), fake gate inputs (F2), a
verification system that never verifies (F4). F1 alone means no honest "all done" is
possible — the app currently shows every user someone else's invented finances as
their own, with no label. Fix order: F1 → F2 → F4 → F3 → F5 → F6/F7/F8 → F9.
