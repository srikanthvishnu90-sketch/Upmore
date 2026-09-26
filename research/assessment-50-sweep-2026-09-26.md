# 50-Agent Sweep Assessment — 2026-09-26

## Sweep execution

- 50 fixture/code-inspection slices launched via coordinator, 2026-09-26 ~02:50 UTC.
- No credentials, owner session, or live SimpleFIN requests used (sanitized fixtures only).
- **35 slices completed. 15 errored on 429 rate limits** (slices 5–10, 12, 14, 15, 24, 32, 40, 43, 44, 47).
- The coordinator completed without recovering the 15 errored slices.
- Recovery: the confirmed findings (below) were independently re-verified in source
  and catalog on 2026-09-26, and every fix was functionally tested (15/15 checks
  pass against the built app). The errored slices' *coverage areas* were reproduced
  locally rather than re-run as agents.

## Confirmed findings and fixes (commit 5dd7dbb, deployed 2026-09-26)

### 1. HIGH — Credit cards surfaced in Explore (fixed)
`R3562` (Home Depot Consumer Card) and `R3563` (Macy's Card) were only in
`NO_LEAD_IDS` (queue-leadership block), not blocked from Explore.
Fix: `routeIsBlocked()` now blocks credit-card applications everywhere in Earn —
known card-offer IDs plus application-language patterns ("open a new … card",
"cardmember", "Visa accounts") as a backstop for future Standard-lane card offers.
Explore also runs `routePassesGates`, which now calls `routeIsBlocked`.

### 2. HIGH — Fluz (R0535) offered to cash-$0 users (fixed)
Cashback-on-spending routes were not in any needs-spend category; "no cash
needed up front" copy could appear for a spend-to-earn path.
Fix: `needsSpend()` now matches cash-back + shopping/spending language in
method/what. `blocked()` rejects these for cash ≤ 0.

### 3. HIGH — Required deposits not compared to actual cash (fixed)
`R0616` ($100 minimum) was only rejected when cash ≤ 0, so a $25-cash user
could be told they can cover the deposit. `buildQueue`/`xFiltered` also used
fake gate cash ($5,000).
Fix: `NEEDS_DEPOSIT` maps id → actual minimum ($100/$25); `blocked()` compares
real cash; `routeGateInputs` uses the same number for the capital gate; both
gate-user constructions use real `planData().cash`; unknown cash fails closed (0).

### 4. HIGH — State eligibility not enforced (fixed)
`R0616` (MN/WI-only) could surface in any state. `routeGateInputs` hardcoded
`states: undefined`; queue/Explore hardcoded `"IL"`.
Fix: `routeStates()` parses restrictions from `who_qualifies`/`requirements`
(state pairs like MN/WI, "residents only", membership/geo context; conservative
so incidental mentions don't over-block). Enforced in `blocked()` (queue) and
the state gate (all paths). Real user state everywhere; unknown state never blocks.

### 5. MEDIUM — Non-cash discounts as earning routes (fixed)
`R0376` (Adobe student discount, reward literally "NOT income") could lead the queue.
Fix: `nonCashLead()` now flags discount-on-purchase offers, scoped to
reward/method (not fine-print catches) so mixed routes with a real cash primary
(e.g. R3022's $250 bonus) aren't demoted. 15 routes flagged, 0 false positives
in catalog audit.

### 6. MEDIUM — Explore used invented eligibility inputs (fixed)
`xFiltered()` hardcoded `free_cash: 5000`, `free_minutes: 60`, state `"IL"`.
Fix: real `planData()` values.

### 7. MEDIUM — Capital parsing/filtering incomplete (fixed)
`blocked()` didn't inspect `costs_and_unpaid_time`. Now unified via
`NEEDS_DEPOSIT` (see #3).

### 8. NEW (found during fix verification) — Loss gate over-blocked 130+ bank bonuses (fixed)
`routeGateInputs`' loss gate treated "required" + $ as a mandatory loss, and the
own-account rescue only matched "your … account" phrasing. 175 Standard-lane
routes (126 bank bonuses) were killed — e.g. R0616's "Money movement required:
$250 is deposited … when the account is opened".
Fix: own-money movement (deposit/direct deposit/park/move into account/share
balance) is recoverable, never a loss; non-refundable/forfeited deposits stay
losses. Real fees (R7438) and memberships (R0380) still blocked — verified.

### Copy honesty
`whyLine` now names the actual deposit amount ("needs a $100 deposit you can
cover") instead of "a small deposit", and only after `blocked()` guarantees
the user can cover it.

## Verification

15/15 functional checks pass against built `index.html` (extracted real
functions + real catalog data in Node):
cards blocked, Fluz needsSpend + cash-0 block, R0616 states=[MN,WI], R0616
blocked for GA / $25-cash, allowed for MN/$100, Adobe non-cash, WashTrust
still cash-lead, gates fail R0616 for GA/cash-0 and pass for MN/$100, cards
blocked in Explore gates, future card-offer backstop, real fee + membership
routes still killed by loss gate.

Build: `python3 src/build-app.py` clean, inline JS parses. Deployed to
production (verified live: new code served).

## Remaining open gaps (not covered by this sweep)

- Complete post-fix 303-case rerun with fresh formulations.
- Complete post-fix 25-scenario rerun.
- Full Claim validation (federal path, official links, countdowns, persistence,
  45-day check-in, "money landed" → Found, post-find sharing).
- Full visual/accessibility audit (4.5:1 contrast, coral-only-for-failure,
  keyboard/focus/ARIA, requested mobile screens).
- Owner-authenticated SimpleFIN success through the proxy; safe disconnect test.
- Signed-in production-mobile identity + exact-data translation verification.
