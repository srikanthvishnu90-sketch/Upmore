# Route verification sweep — 2026-09-26

Checked all **1,437 earnable routes** (every one had a URL). Method: HTTP HEAD (GET fallback)
for each URL, 10–22s timeouts, one retry pass on timeouts/connection errors, plus
browser-level confirmation on ambiguous cases.

## Results

| Outcome | Count | Share |
|---|---|---|
| Live (HTTP 2xx) | 1,158 | 81% |
| Dead (404/410, offer page gone) | 29 | 2% |
| Bot-blocked (403) | 76 | 5% |
| Timeout / connection error (after retry) | 121 | 8% |
| Other (429/5xx/misc) | 53 | 4% |

## Dispositions applied

- **Retired (1):** R0347 Binance Learn and Earn — binance.us/en/learn-and-earn 404 from
  two independent fetchers; Binance's global Learn & Earn excludes US users.
- **URL fixed (1):** R0215 OneForma — old PDF asset 410'd; repointed to live oneforma.com
  (site verified active, hiring).
- **Hiring-pause warning added (1):** R0393 Scribie — page live but Scribie announces a
  temporary pause on hiring freelance transcribers during migration to Scribie.ai.
- **Moved to unverified (23):** promo/landing-page URLs returning 404 where the campaign
  likely ended — 14 bank/credit-union promos (M&T, Alliant, Bank of America x2, PSECU x2,
  Byline, Cyprus CU, On Tap CU, Media City CU, Liberty Savings, NGF CU, First U.S. CCU,
  Fort Financial), 8 CDN/asset/landing URLs (Addition Financial x2, Mantl CDN x3,
  BND College SAVE, Scalable Capital, CTA auto-quote), 1 mismatched Turo route.
- **Provider names repaired from route text (6):** Addition Financial x2, Bank of North
  Dakota (College SAVE), Scalable Capital, California Teachers Association,
  Media City Credit Union.
- **Confirmed alive despite checker 404 (3):** TXU Energy x2 and Lamps Plus — checker
  404s were bot-handling; verified live via browser fetch.

Earnable routes after sweep: **1,413** (was 1,437).

## Honest limits

- 76 bot-blocked (403) URLs could not be verified either way — not dead, not confirmed.
- ~174 timeout/connection-error/misc URLs are unknown, not dead; many are slow or
  heavily protected bank sites.
- This sweep verified **link liveness**, not offer terms. A live page doesn't guarantee
  the bonus amount/requirements in the catalog are current — bank bonuses in particular
  rotate constantly. Terms-level re-verification of the 305 Bank Bonus routes is the
  natural next pass.
