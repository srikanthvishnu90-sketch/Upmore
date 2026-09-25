# Agent C3 (Cancel: State Machine) — HARSH TEST REPORT

**Date**: 2026-09-25
**App**: https://upmore-srikanthvishnu90-sketchs-projects.vercel.app/
**Spec**: Cancel (Doc 2) — State machine & confirmation rule
**Verdict**: **FAIL** — The state machine is dead code. The confirmation rule is not enforced.

---

## Method Note

As a generic subagent I cannot operate a live browser. This is a static code audit of `src/upmore-app-template.html` (the source of truth; `index.html` is generated). Every finding below is grounded in the actual code. A live-browser test would be needed to confirm the user-visible behavior, but the code paths are unambiguous.

---

## Finding 1 (CRITICAL): CancelState is dead code — the state machine is not wired to anything

**Spec requires** (Doc 2, "The confirmation rule"):
> A subscription passes through four states, and only one of them counts:
> - active → cancel_started → cancel_claimed → cancel_confirmed

**What exists**: `CancelState` is defined at lines 3052–3066 with `ACTIVE`, `STARTED`, `CLAIMED`, `CONFIRMED`, a `next()` transition function, and `mayWriteAvoided()`.

**What's broken**: `CancelState` is **never referenced anywhere else in the codebase**. Zero call sites. The object is constructed and then abandoned. The four states exist as string constants in a vacuum.

**The actual subscription flow** uses `save_subscriptions.status` with the value `"cancelled"` (line 2339: `update({ status: "cancelled" })`). This is a single boolean-like flag, not the four-state machine. There is no `cancel_started`, no `cancel_claimed`, no `cancel_confirmed` in the database layer or UI.

**Impact**: The spec's core trust mechanism — "Upmore does not mark a subscription cancelled until the next billing date passes with no charge" — has no implementation. The state machine was written but never connected.

---

## Finding 2 (CRITICAL): The required claimed copy is never shown to the user

**Spec requires** (Doc 2):
> cancel_claimed writes nothing to the ledger. Not a provisional figure, not a pending total, nothing. The app says so explicitly: "Nice. I'll watch for the charge on the 14th. If nothing shows up, I'll count it then."

**What exists**: `claimedCopy` is defined at line 3085:
```js
claimedCopy: `Nice. I'll watch for the charge on the ${new Date(sub.next_date).getDate()}th. If nothing shows up, I'll count it then.`,
```

**What's broken**: `claimedCopy` is **never rendered, never displayed, never referenced** outside its definition. A grep for `claimedCopy` across both the template and built `index.html` returns only the definition line. The string is dead data.

**The actual cancel card action** (line 1773–1779):
```js
cta: "Show me how", act: () => toast("Cancel path: " + s.merchant_raw),
```
Clicking the cancel card shows a toast saying "Cancel path: [merchant]". There is no claimed flow, no copy, no state transition.

**The existing subscription cancel flow** (`cancelSubById`, line 2334):
- Marks `status: "cancelled"` in the database immediately
- Does NOT show the required copy
- Sends the user to Guide with a message about "confirming it's really cancelled" — but this is not the spec's required wording

**Impact**: The user never sees the explicit promise that nothing is counted yet. The spec's exact wording requirement is unmet.

---

## Finding 3 (CRITICAL): mayWriteAvoided is dead code — no confirmation watcher exists

**Spec requires** (Doc 2):
> On the expected date plus a 2-day grace, the detector re-runs. No charge, it confirms and the ledger records Avoided.

**What exists**: `mayWriteAvoided(state, expectedBillingDate, chargesSince)` at lines 3060–3066 correctly implements:
- State must be `CONFIRMED`
- Current date must be ≥ billing date + 2 days
- No charges since the billing date

**What's broken**: `mayWriteAvoided` is **never called**. There is no confirmation watcher, no scheduled job, no billing-date check. The 2-day grace logic is correct but unreachable.

**Impact**: Even if a user claimed a cancellation, nothing would ever confirm it. The Avoided entry would never be written automatically.

---

## Finding 4 (HIGH): No reversal logic for reappearing charges

**Spec requires** (Doc 2):
> A charge appears, the card returns to the top of the queue with an honest message: "They charged you $14.99 on the 14th anyway. That happens — usually the cancellation didn't go through, or it was queued for period end. Want to check?"
> Reversals subtract. A subscription that reappears removes its Avoided entry and the card returns to the queue.

**What exists**: The ledger has a `reversed` flag (line 2043: `update({ reversed: true })`), but this is for manual ledger entries.

**What's broken**: There is no automatic detection of reappearing charges. No code checks "did the charge come back after we marked it cancelled." No card-return-to-queue logic. No Avoided subtraction.

**Impact**: If a cancellation fails silently (the exact case the spec is designed to catch), the app has no mechanism to detect or correct it.

---

## Finding 5 (MEDIUM): The ledger is manual — no guardrails against premature Avoided logging

**What exists**: Users manually log ledger entries via a form (line 868). They select "Avoided" from a dropdown (`lgType`).

**The problem**: There is nothing preventing a user from logging "Avoided" immediately after clicking "cancel" on a subscription. The app does not:
- Warn "don't log this yet — wait for the billing date"
- Track the subscription's claimed state
- Suggest when it's safe to log

**Spec intent**: The app should actively guide the user to wait. The required copy ("I'll count it then") implies the app is watching and will tell them when. Since the app isn't watching, the user is left to guess.

**This is not a direct spec violation** (the spec doesn't forbid manual logging), but it defeats the purpose of the confirmation rule. The honest-ledger positioning requires the app to enforce the wait, not just avoid auto-writing.

---

## Finding 6 (LOW): The claimedCopy date logic is correct but untestable

The dynamic date in `claimedCopy`:
```js
new Date(sub.next_date).getDate()
```
This correctly extracts the day-of-month from the next billing date. If the billing date is the 14th, it renders "14th". This matches the spec's example ("on the 14th").

However, there's an edge case: for dates like the 1st, 2nd, 3rd, 21st, 22nd, 23rd, 31st, the ordinal should be "1st", "2nd", "3rd", not "1th", "2th", "3th". The code always appends "th". This is a minor copy bug, but it's in dead code so it has zero user impact.

---

## Summary of Violations

| # | Requirement | Status | Severity |
|---|-------------|--------|----------|
| 1 | Four-state machine (active→started→claimed→confirmed) | **FAIL** — dead code, not wired | CRITICAL |
| 2 | Required claimed copy shown to user | **FAIL** — defined but never rendered | CRITICAL |
| 3 | Confirmation watcher (billing date + 2-day grace) | **FAIL** — dead code, never called | CRITICAL |
| 4 | Reappearing charge → card returns + Avoided reversed | **FAIL** — not implemented | HIGH |
| 5 | Guardrails against premature Avoided logging | **FAIL** — manual ledger has no guidance | MEDIUM |
| 6 | Ordinal suffix in claimed copy (1st/2nd/3rd) | **FAIL** — always "th", but dead code | LOW |

---

## What Would Fix This

1. **Wire CancelState to the subscription UI**: When user clicks "Show me how" on a monitor-driven cancel card, transition to `cancel_started`. When they confirm they cancelled, transition to `cancel_claimed` and **display the claimedCopy**.
2. **Implement the confirmation watcher**: A function that runs on app load (or via the existing monitor pattern) checking all `cancel_claimed` subscriptions: if billing date + 2 days has passed, check transactions. No charge → `cancel_confirmed` + write Avoided. Charge found → return card to queue with the honest message + reverse Avoided if written.
3. **Store the state**: The `save_subscriptions` table needs a `cancel_state` column (or use the existing `status` with the four values instead of just "cancelled").
4. **Fix the ordinal**: Use proper 1st/2nd/3rd suffixes.

---

## Browser Testing Needed

The following cannot be verified by static analysis and require live browser testing by an eligible agent:
- Can a user actually mark a subscription as "claimed" via the UI? (The monitor-driven cards only show a toast; the manual subscription flow marks "cancelled" immediately)
- Does the toast "Cancel path: [merchant]" appear? (This is the only user-visible behavior of the new cancel cards)
- Is there any UI for the 7-element cancel card details? (The card renders elements, but the "Show me how" action is just a toast)

---

**Final verdict**: **FAIL**. The Cancel state machine is a textbook case of "written but not wired." The logic is correct in isolation, but it has zero connection to the user interface, the database, or the ledger. The spec's most important paragraph — the confirmation rule — is not implemented in any working form.
