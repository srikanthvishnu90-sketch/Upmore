# Spec: Monthly Close v2 + Real-World Execution — 2026-09-26

Vishnu directive: monthly close must end with forward CFO actions, and Upmore needs real-world execution (starting with subscription cancellation). This spec covers both.

## Part 1: Monthly Close v2 — "the close that tells you what to do"

### Current state
90-second screen: in / out / changed / coming. Retention mechanic, backward-looking.

### v2: close ends with actions
After the numbers, the close computes forward actions from the same data:

1. **Idle-cash drift** — checking balance grew vs last month while earning ~0% → "Move $X to HYSA, earn ~$Y/year." One tap: deep link to user's HYSA provider (prefill amount, user confirms transfer — we never move money).
2. **Subscription creep** — new recurring charges detected, price increases, duplicate subscriptions (two Netflix-class), free trials converting in <7 days → each becomes a cancel/keep card.
3. **Debt nudge** — month ended with surplus → "Put $Z extra toward [highest-APR balance], saves $W interest." Sized from actual surplus, pre-filled in the debt sequencer.
4. **Tax nudge** (quarterly months) — gig income detected → quarterly estimate reminder with the computed amount.

Each action card: what, why (dollar figure), one-tap path. Dismissed actions don't nag (no streaks/shame per product rules).

### Data requirements
- 90-day transaction window (already the coverage target)
- Recurring-charge detection (exists: detectRecurrence)
- Trial-conversion detection: NEW — charges preceded by $0/$1 auth holds or "trial" merchant memos, with conversion-date estimation
- Duplicate-subscription detection: NEW — same merchant, 2+ active recurring charges

## Part 2: Real-World Execution — subscription cancellation

### Constraint change (Vishnu-approved 2026-09-26)
Relaxed, scoped to subscription/bill actions only:
- Merchant sessions may be automated ONLY with per-action user approval + full audit trail.
- "Never place calls" still stands → v1 covers merchants with online cancel flows; call-required merchants get scripts + tracking (user calls or skips).
- Money movement stays forbidden forever. Cancellation is not money movement.
- Merchant credentials: Secure Vault only, never in chat/memory/logs. Per-merchant, revocable.

### Tier 1 — Co-pilot (build now, no constraint change needed)
For every detected subscription:
- **One-tap deep link** to the merchant's actual cancellation page (curated URL map for top 100 subscription merchants — Netflix, Spotify, Devin, etc.)
- **Pre-filled chat script** where cancellation is via support chat ("paste this")
- **Step-by-step guide** per merchant (click path, retention-offer warnings: "they'll offer 50% off — only take it if you actually use it")
- **Progress tracking**: started → confirmed cancelled → verified no further charges (watch next 60 days of transactions for zombie charges)

### Tier 2 — Authorized agent (needs the relaxed constraints)
- User taps "Cancel for me" on a subscription card → approval card shows EXACT merchant, plan, amount, billing date → user approves → browser task completes the cancellation in the merchant session → result + proof (confirmation screenshot/email) saved to audit log.
- Audit log: timestamp, merchant, action, approval reference, outcome. Exportable.
- Failure modes: login expired → prompt re-auth (user does it); retention dark patterns → abort and hand to user with notes; ambiguous which subscription → ask, never guess.

### Tier 3 — Human-verified concierge (later, ops team)
Long-tail merchants, call-required cancellations. Out of scope for v1.

### What "cancel" must never do
- Never cancel without per-action approval naming merchant + amount.
- Never cancel a subscription the user marked "keep."
- Never touch: insurance, utilities, anything with a contract penalty — flag for user decision instead (early-termination fees computed and shown).
- Never claim "cancelled" without evidence (confirmation page, email, or 60-day no-charge verification).

## Worked example (real, 2026-09-26)
- Found: Devin Pro (Cognition AI Inc.), $20/mo, srikanthvishnu90@gmail.com, since Aug 25 2026.
- Sep 25 renewal payment FAILED (card ending 2429 declined) — subscription in past-due "update billing" state.
- Usage evidence: none (only marketing emails since signup).
- Correct action: cancel in Devin app (or let lapse by not updating billing — but explicit cancel is cleaner, kills zombie retries).
- Execution path: Tier 2 — needs Devin account access (Secure Vault login or user takeover).

## Build order
1. Trial-conversion + duplicate-subscription detection (Close v2 data layer)
2. Top-100 merchant cancellation URL/script map (Tier 1)
3. Close v2 action cards
4. Tier 2 authorized-agent flow + audit log (behind the relaxed-constraint flag)
5. Zombie-charge verification (60-day watch)
