# Agent E1: Earn 9-Gates — HARSH TEST REPORT

**Verdict: FAIL** (6 distinct defects, 2 critical)

**Method**: Direct code audit of `earnGates()`, `routeGateInputs()`, `routePassesGates()` in `src/upmore-app-template.html` (lines 3094-3171) plus catalog data analysis (1990 routes, 1644 Standard non-retired). No browser needed — the defects are in the logic itself.

---

## CRITICAL 1: Gate 1 (Age) regex matches dollar amounts, not ages

**Location**: `routeGateInputs()`, line 3135: `q.match(/(\d{2})\+/)`

The regex matches ANY two digits followed by `+`, including:
- Staples: "spent **$30+** on ink/toner" → parsed as age 30 → **incorrectly filtered**
- Forwardenergy: "250+-gal" (gallons) → parsed as age 50 → **incorrectly filtered**
- T-Mobile: "$90+" (dollar amount) → parsed as age 90 → **incorrectly filtered**

**Impact**: 12 routes fail Gate 1. At least 9 are false positives (dollar amounts, gallons, not ages). Legitimate routes are hidden from the user.

**Spec violation**: Gate 1 should check "The user meets the route's minimum age." A dollar amount is not an age requirement.

---

## CRITICAL 2: Gate 5 (Loss) conflates "mentions fee" with "can lose money"

**Location**: `routeGateInputs()`, line 3140: `cannotLose = !/deposit|fee|pay \$|upfront/i.test(costs) || upfront === 0`

**Impact**: 346 routes fail Gate 5, most incorrectly:
- **JM Bullion**: "No seller fees; insured shipping provided; **optional $25 wire** fee" → FAILS. But the text says "No seller fees" and the $25 is OPTIONAL (free options exist). The user CANNOT lose money.
- **Bank bonuses** (Old National, E*TRADE, etc.): "must move/park ~$3,500" → FAILS. But moving money into your own bank account is NOT losing money — it's a capital requirement (Gate 6's job, not Gate 5).

**Spec violation**: Gate 5: "The route cannot lose the user money. Any route where the user can end up worse off is excluded, full stop." An optional fee with free alternatives does NOT make the user worse off. A deposit into your own account is NOT a loss.

**Additional bug**: The dollar regex `\$(\d+)` doesn't handle commas: "$3,500" parses as $3, not $3500.

---

## HIGH 1: Gate 9 uses hardcoded empty accounts — 243 bank bonuses incorrectly filtered

**Location**: `buildQueue()`, line 1748: `const gateUser = { ..., accounts: [] }`

243 routes require "bank account" or "checking account" (all bank bonuses). They ALL fail Gate 9 because `accounts` is hardcoded to `[]`.

**Reality**: The user HAS a bank account (Chase, connected via SimpleFIN — verified live 2026-09-25 with 2 accounts). The gate doesn't know this.

**Spec violation**: Gate 9: "The user holds (or can get) any required account or status." The user HOLDS a bank account. The gate should check the user's actual connected accounts, not a hardcoded empty array.

---

## HIGH 2: Gates use HARDCODED user values, not the user's real data

**Location**: `buildQueue()`, line 1748:
```js
const gateUser = { age: 19, state: "IL", free_cash: 5000, free_minutes: 60, accounts: [] };
```

- **Age 19**: Hardcoded. Not from user's profile.
- **State "IL"**: Hardcoded. Not from user's onboarding (user is in Rome, Italy per memory — though US state may be IL).
- **free_cash 5000**: Hardcoded. Not from Track's `calcFreeCash()` (which exists but isn't wired here).
- **free_minutes 60**: Hardcoded. Not from user's stated free time.
- **accounts []**: Hardcoded empty. (See HIGH 1.)

**Spec violation**: The gates are supposed to filter based on THE USER's actual situation. Hardcoded values mean the gates are testing a fictional user, not Vishnu.

---

## HIGH 3: Gates bypassed entirely in Explore/Search list

**Location**: `xFiltered()` (line 2935) — used by `renderExplore()` for the search/browse list.

The 9 gates are ONLY applied in `buildQueue()` for the "Up next" queue cards. The Explore/Search list (`xFiltered()`) shows ALL routes with NO gate filtering.

**Spec violation**: "A route surfaces only if it passes all nine, in this order. A gate that fails ends evaluation immediately — no partial credit, no 'close enough.'" The Explore list is a surface. A 21+ route, a route requiring $10,000 capital, or a route the user already completed can appear in search results.

---

## MEDIUM: Freshness gate (Gate 4) is a no-op; unverified routes lead the queue

**Location**: `routeGateInputs()`, line 3144: `verification: r.verification || "unverified"`

- Zero routes in the catalog have a `verification` field.
- All 1644 routes default to "unverified" → all PASS Gate 4.
- The gate never filters anything.

**Spec concern**: "Stale routes may be visible with age but may never lead or enter an agent-proposed plan." By extension, UNVERIFIED routes (which is all of them) should not lead either. The spec says: "An honestly small catalog is preferred over a large unverifiable one." Letting 1644 unverified routes lead the queue violates the spirit of the verification system.

---

## What actually works

- **Gate order**: Correct (age → state → deadline → freshness → loss → capital → time → cooldown → prerequisite).
- **Short-circuit**: Correct — `for` loop returns on first failure.
- **Gate 8 (cooldown)**: Correctly uses `completed_routes` (though the data comes from hardcoded user, the logic is right).
- **Gate 7 (time)**: Logic is correct (108 routes with >60min correctly filtered, given the hardcoded 60min limit).

---

## Summary

The 9-gate STRUCTURE exists and the ORDER is correct, but the IMPLEMENTATION has critical data-mapping defects:

| Gate | Status | Issue |
|------|--------|-------|
| 1. Age | **FAIL** | Regex matches $ amounts, not ages |
| 2. State | NO-OP | Always passes (no data) |
| 3. Deadline | NO-OP | Always passes (no data) |
| 4. Freshness | NO-OP | Always passes (no data); unverified leads |
| 5. Loss | **FAIL** | Over-aggressive; conflates fees with loss |
| 6. Capital | OK | Logic correct, but hardcoded free_cash |
| 7. Time | OK | Logic correct, but hardcoded free_minutes |
| 8. Cooldown | OK | Logic correct |
| 9. Prerequisite | **FAIL** | Hardcoded empty accounts |

**Plus**: Gates bypassed in Explore/Search; all user values hardcoded.

**Recommendation**: Do not ship. Fix the regexes, wire real user data, apply gates to all surfaces.
