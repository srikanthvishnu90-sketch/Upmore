# Agent C1 Report: Cancel Recurrence Detection — FAIL

**Verdict: FAIL** (detector logic: PASS; feature as deployed: FAIL)

## Summary

The `detectRecurrence()` implementation is **correct per spec**. The feature is **broken in practice** because the demo transaction data it runs against produces zero detections, making Cancel cards invisible in the app.

## What I Tested

I am a generic subagent without live-browser access. I audited the implementation source (`src/upmore-app-template.html`) and executed the detector against both the app's demo data and synthetic realistic data via Node.

## Detector Logic: PASS

Against realistic subscription data, the detector is correct:

| Test | Result |
|------|--------|
| Netflix $15.99 monthly ×4 | ✅ Detected: monthly, conf 0.95, n=4 |
| Spotify $10.99 monthly ×3 | ✅ Detected: monthly, conf 0.80, n=3 |
| Amazon one-time $42.99 | ✅ Correctly excluded |
| Pending Netflix charge | ✅ Correctly excluded (pending never enters) |
| 3% price increase ($15.99→$16.50) | ✅ Detected as same subscription (within 5% tolerance) |
| 25% price increase ($15.99→$19.99) | ✅ Split into 2 clusters (correct) |
| Recurring transfers ($500/mo) | ✅ Correctly excluded (transfers ≠ spending) |

Spec compliance:
- ✅ Date bands match exactly: weekly 6–8d, biweekly 13–15d, monthly 28–31d, quarterly 88–92d, annual 360–370d
- ✅ Amount tolerance: 5% or $1 minimum (`Math.max(c.amount * 0.05, 1)`)
- ✅ Pending and transfer exclusion before grouping
- ✅ Merchant normalization via `normalizeMerchant()`
- ✅ Confidence tiers: n≥4→0.95, n=3→0.80, n=2→0.60
- ✅ 75% band-consistency threshold

## Feature as Deployed: FAIL

**Critical: Zero detections on demo data.** I ran the detector against the app's `TransactionSource.demo()` output (180 transactions, 90 days, 14 merchants). Result: **0 recurring charges detected.**

Root cause: the demo data generator cycles merchants pseudo-randomly (`(day * 3 + i) % 14`). Netflix appears 13 times with gaps of 5,4,5,9,14,5,5,4,5,9,14,5 days — irregular, matching no band at 75% consistency. A human looking at "Netflix" in the transaction list expects it to be flagged as a subscription. The detector correctly rejects it because the data is unrealistic.

**Consequences:**
1. The Cancel monitor integration in `buildQueue()` (line 1764) never fires — no cancel cards ever appear in the Home queue.
2. `wasteScore` ranking is untestable — no inputs.
3. The 7-element `cancelCard()` is dead code in production.
4. A user demoing the app sees **zero** Cancel functionality.

## Additional Issues Found

1. **Hardcoded `usage_signal = 0.5`** (line 1771): `wasteScore(annual, 0.5, renewalUrgency(days), s.confidence)`. The spec defines `waste_score = annual_cost × (1 - usage_signal) × renewal_urgency × confidence` where usage_signal should derive from observed usage. Hardcoding 0.5 means every subscription is assumed half-used. Not spec-compliant.

2. **Arbitrary score threshold**: `if (score < 30) return;` — no basis in spec. A $15.99/mo subscription at 0.6 confidence with urgency 0.3 scores `191.88 × 0.5 × 0.3 × 0.6 = 17.27` and is silently dropped.

3. **Cancel action is a stub**: `act: () => toast("Cancel path: " + s.merchant_raw)` — tapping "Show me how" shows a toast, not the cancel-path library. The spec requires exact steps, direct links, and retention warnings.

4. **No cancel-path library**: `cancelCard(s, null)` passes null — method shows "unknown", observed time "not observed". The spec requires observed time with sample size and retention offers.

5. **Monthly `next_date` drifts**: uses fixed 30-day increments instead of calendar months. A Jan 15 billing projects to Feb 14, not Feb 15. Minor but wrong.

## Where Cancel Cards Appear

Nowhere. The queue integration exists but the detector returns empty on demo data. With live SimpleFIN data (real subscriptions on fixed schedules), the detector would work correctly.

## Recommendations

1. **Fix demo data**: generate realistic subscriptions (e.g., Netflix $15.99 on the 15th monthly ×3, Spotify $10.99 on the 3rd ×3) so the feature is visible and testable.
2. **Derive usage_signal** from transaction/category data or mark as unknown instead of hardcoding 0.5.
3. **Remove or justify the score<30 threshold.**
4. **Implement the cancel-path library** (even a minimal one with method + observed minutes for top merchants).
5. **Wire the cancel CTA** to a real flow, not a toast.

## Files
- Detector: `src/upmore-app-template.html` line 3394 (`detectRecurrence`)
- Integration: line 1764 (`buildQueue` monitor block)
- waste_score: line 3040; `renewalUrgency`: line 3043
- Demo data: `TransactionSource.demo()` (~line 3300)
