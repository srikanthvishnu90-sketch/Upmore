# Route Hunt Batch 2 — report (2026-09-23)

**Result: 1,077 candidates researched → 45 kept, 1,032 rejected.**
Deliverable: `route-hunt-batch2.json` (45 routes, IDs R8400–R8570, all speed `days`, full 7-answer framework + demand_side + evidence).
No commits, deploys, or production catalog/DB changes made.

## Kept by lane

| Lane | Kept | What survived |
|---|---|---|
| Usability testing / QA | 1 | **Testlio** (R8400) — hourly remote QA test runs, weekly PayPal/Payoneer; honestly framed as supplemental (matching delay) |
| Transcription | 2 | **eScribers** (R8420) — weekly-pay legal transcription, U.S. contractors; **TranscriptionStaff** (R8421) — weekly PayPal, $3 min (≥2 audio hrs/wk to stay active) |
| AI data / annotation | 1 | **Stellar AI** (R8440) — weekly PayPal, $25/hr base; rolling onboarding caveat recorded |
| Fast buyback | 8 | **myGemma** (R8460, luxury, wire ~24h), **Dave & Adam's Card World** (R8461, sports cards, paid 24–36h), **Card Kingdom** (R8462, Magic buylist, PayPal 24h after finalization), **BAM Good Bricks** (R8463, LEGO, paid on verification), **Adorama** (R8464, camera gear, paid ≤48h, direct deposit), **EagleSaver** (R8465, books/media, PayPal 24h), **CashForUsedLaptop** (R8466, PayPal/Venmo 1 biz day), **GreenBuyBack** (R8467, phones, PayPal ~24h). All 8 re-verified by direct official-page fetch. Buyback = asset liquidation, framed as such. |
| Expert calls | 2 | **Codementor** (R8480) — weekly payouts ACH/PayPal/bank, 13–22% fee; **MentorCruise** (R8481) — Stripe payouts within 7 days |
| Localization | 0 | Lane is structurally monthly-pay/invite-only — nothing cleared the bar |
| Live deals | 30 | Real current paid-request posts (R8520–R8549, Threads/IG/FB, posted 2026-09-16…23): video editing 6, UGC 7, VA 6, voiceover 4, data entry 3, design 2, translation 2. Each has post URL, poster, stated pay. **Pay timing/method mostly unstated in posts** — negotiated directly, no escrow; flagged in every card. |
| AI-proof ideas | 1 | Triaged 694 committed/contracted ideas from `ai-proof-1000-ideas.json` → **Atom.com** (R8570) guaranteed naming contests ($100–300/win via PayPal). The file's pay claims were mostly speculative. |

## Notable rejects (why the bar held)

- **PlaybookUX** — "within 8 days" is one day over the ceiling; rule is the rule.
- **Clarity.fm** — withdrawals only 2 weeks after a transaction.
- **Userbrain** — usable cash ≈ 12–17 days (7-day test pend + 5–10 biz-day payout).
- **Smartcat** — payout leg verified (PayPal ≤3 biz days) but no official evidence a new freelancer can win/complete/get approved in a week.
- **MTurk** — 10+ active-day new-worker hold before any transfer.
- **Mercor** — real weekly payouts, but expert-gated hiring marketplace, not ordinary-person work.
- **Neevo** — official terms: paid up to 28 days after approval.
- **Data Annotation** — strongest keep on paper, but already verified route R0270 (dedupe catch).
- **MPB / Bob's Watches / Carvana** — best-evidenced buyback candidates, all catalog duplicates.
- **StickK referee / 7 Cups companion ideas** — fabricated pay claims; both are unpaid volunteer roles.
- **StartPlaying.Games DM-for-hire** — real demand, but cold start means weeks to first paying player.
- **Live-deal scams filtered** — $120/video spam template across 6 accounts; $4,000 voiceover from 10-follower accounts; pay-to-apply "certification exam".

## Caveats before promotion to production

1. Live-deal evidence rests on social-search parsed public-post data, not direct page reads — spot-check URLs before promoting.
2. Live deals are ephemeral by nature; they need an expiry/recheck mechanism, not the standard route lifecycle.
3. Buyback routes are liquidation, not earnings — keep that framing in the UI.
4. Raw lane outputs + per-lane reject lines (1,032 total): `/tmp/upmore-hunt/lane{1-8}.json`, `/tmp/upmore-hunt/lane{1-8}-rejects.txt`.
