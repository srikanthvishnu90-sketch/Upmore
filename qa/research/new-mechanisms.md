# 3 new earning mechanisms (2026-09-22)

Criteria: easy or almost guaranteed. Each becomes a route candidate, verified against
official terms before the app ever promises it.

## 1. HYSA interest capture — move idle cash to a high-yield savings account

- **Mechanism:** Big-bank checking/savings pays ~0.03% APY. Top online HYSAs pay ~4% APY
  (FDIC-insured, same protection). Moving idle cash is a one-time 20-minute transfer.
- **Honest math:** $5,000 idle × (4.00% − 0.03%) ≈ **~$200/year** for 20 minutes of work.
  $10,000 ≈ ~$400/year. Scales with cash on hand; $0 if the user has no savings.
- **Why almost guaranteed:** interest is contractual, paid by the bank, FDIC-insured.
  The only variable is the rate (banks can adjust APY — the route must quote the
  current rate and note it floats).
- **Time:** ~20 min once, then $0 ongoing.
- **Verification plan:** pin current APY + minimums + fees on the provider's official
  page (SoFi/Marcus/Ally). Re-verify rate monthly — this is what the reverify
  scheduler is for.
- **Why Meta won't:** unsexy, zero AI novelty, requires maintaining current-rate data
  per provider. Pure ops.

## 2. Subscription & bill audit — stop money that's already leaving

- **Mechanism:** guided flow — list every recurring charge, cancel what's unused,
  negotiate what isn't (cable/internet/phone bills negotiate down with one call and
  a competitor quote; insurance re-shops yearly).
- **Honest math:** routinely surfaces **$100–300/year** in forgotten subscriptions plus
  one-time bill reductions of $10–40/month. This is found money, not earned money —
  frame it that way.
- **Why almost guaranteed:** you're not creating income, you're plugging leaks. Anyone
  with 3+ subscriptions who hasn't audited in a year almost certainly finds something.
- **Time:** ~30 min guided audit, then ~10 min per negotiation call.
- **Verification plan:** this is a method route (like R0302), not a single provider —
  verify the playbook steps (where to find recurring charges in each major bank app,
  cancellation links for top subscription services, negotiation scripts). No payout
  promise per step; promise the method.
- **Why Meta won't:** it's a checklist + scripts product, not an intelligence product.
  v2 (bank-connection auto-detect) needs Plaid-style access they'd never scope to this.

## 3. Plasma donation — the most reliable $/hour in the catalog

- **Mechanism:** licensed plasma centers (CSL Plasma, BioLife, Octapharma) pay per
  donation; up to 2×/week. New-donor promotions commonly pay **$500–700 across the
  first month** (typically 8 donations); regular donors get ~$50–75/session by weight.
- **Honest math:** eligible donor ≈ **$400–600/month** for ~8–10 hours/month at the
  center. The per-session rate is posted by each center — contractual, not variable.
- **Why almost guaranteed:** if you pass the health screening (18+, weight minimum,
  basic vitals), they pay every time you donate. The only uncertainty is eligibility.
- **Time:** ~90 min first visit (screening), ~45–60 min per donation after.
- **Catches (say them plainly):** needles, time at the center, eligibility screening,
  donation frequency limits exist for health reasons. Local availability varies —
  needs a ZIP-based center finder.
- **Verification plan:** verify per-center new-donor promo terms on official sites
  (they change quarterly — perfect reverify-scheduler customer), plus a ZIP lookup
  for the 3 national chains.
- **Why Meta won't:** bodily, local, unglamorous, needs geo data and quarterly
  promo monitoring. Zero horizontal reuse.
