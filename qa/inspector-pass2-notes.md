# Inspector pass 2 notes — R2021+ (to be adjudicated after all discovery completes)

Scope: every verify file qa/verification/R2021.json and above.

## Known items to resolve
1. **R2218 (MoneyLion referral) CONFLICT**: G15 verified it; G22 (brokerage/fintech referrals) rejected the same official URL
   (moneylion.com/referrals-terms-and-conditions/) as invite-only ("must receive official invitation"). Reconcile: if the
   program is invite-only/targeted, demote R2218. Check the current official page.
2. **G13 validator flags** (from inspector pass 1): R2026/R2027/R2028/R2036/R2037 had issues; reddit.com DUP group
   (R2027/R2028 are r/forhire and r/DesignJobs — confirm distinct channels, not duplicates).
3. **R2026** (Hacker News threads): official_url is news.ycombinator.com with c1 evidence from /newsguidelines —
   confirm this is adequate "official terms" for the channel.
4. **Cross-wave duplicates**: G22 found R2862/R2866/R2872 duplicated R2213/R2216/R2430/R2438 (already handled by G22 via
   deletion). Check other waves for same-institution referral duplicates (G15 vs G17 vs G22 vs G28 vs G34 vs G39).
5. **Bank waves**: check same-bank/same-account/same-promo duplicates across G14/G16/G21/G27/G33/G38 (and later waves).
   Different account types or genuinely different promo codes = distinct; same offer = demote the weaker file.
6. **Referral payout sanity**: confirm payout_min/max = PER-REFERRAL amount (not cap x amount) on all referral files.
7. **Poll-worker waves (G32/G40)**: confirm each county's pay matches its official election site; reject stale schedules.
8. **Expiring-soon**: flag any route with bonus expiring within 14 days of check.

## Procedure
Same as inspector-brief-1500.md: run qa/validate-1500.py, review every verify file, spot-fetch official URLs,
write demotions to qa/adjudication-1500.json (ADD new entries; do not remove pass-1 entries).
Do NOT edit evidence files.
