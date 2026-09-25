# SimpleFIN Proxy Security Tests — 2026-09-25

**Target:** `simplefin-proxy` Edge Function (v2), Upmore Supabase project `mrwngntwmnaqrqhupvlt`
**Method:** live throwaway-user auth tests + code inspection. No owner data touched; vaulted Access URL never read.

## 🔴 CRITICAL FINDING: owner authentication is broken in production

**Every authenticated call to `simplefin-proxy` returns 401 "Invalid session" — including with a freshly minted, valid JWT** (verified: direct `/auth/v1/user` with the same JWT returns 200; proxy returns 401, 3/3 attempts, consistent).

**Root cause** (`supabase/functions/simplefin-proxy/index.ts:65`):
```ts
const { data: { user }, error: authErr } = await userClient.auth.getUser();
```
`getUser()` is called with **no JWT argument**. Per the @supabase/auth-js source, no-arg `getUser()` resolves the user from the client's *stored session* — a fresh edge-function client has no session, so it throws `AuthSessionMissingError` without ever making an HTTP request. The `Authorization: Bearer <jwt>` global header is never used. **The fix is one line:** `userClient.auth.getUser(jwt)`.

**Corroboration:** `supabase/functions/agent-chat/index.ts:71-82` contains a comment warning about this exact pitfall and passes the token explicitly (`supabase.auth.getUser(authM[1])`) — which is why agent-chat works and simplefin-proxy doesn't.

**Impact:** Vishnu's bank sync through this proxy has never worked — his app gets 401 on every sync. The non-owner 403 test below could not reach the owner check for the same reason. **Fix + redeploy required before any authenticated SimpleFIN test can pass.**

## Per-test results

### 1. Non-owner 403 with zero leakage — BLOCKED (by the auth bug above)
- Throwaway user created via GoTrue admin API, signed in (JWT valid per `/auth/v1/user` → 200).
- Proxy call with valid non-owner JWT → **401 `{"error":"Invalid session"}`**, not the expected 403 `{"error":"No bank connection on this account"}`.
- The 403 owner-check path is currently **unreachable by anyone**; zero-leakage of the 401 body verified (no account/bank/credential terms present), but the intended 403 test must be re-run after the auth fix.
- **Must re-test after fix:** non-owner JWT → expect 403 + zero leakage.

### 2. Budget logic — PASS (inspection + empirical)
- Code order: owner check (403) → budget count check (429 at ≥24/day) → `insert` into `simplefin_requests`. Failed owner checks never reach the insert, so they **never consume budget**.
- Empirically: the throwaway user's calls left **0 rows** in `simplefin_requests` for its user_id.
- 429 path exists with clear copy ("Daily bank-sync budget reached (24/day). Try tomorrow.").

### 3. 90-day clamp — PASS (inspection; not executable without owner JWT)
- `endDate` clamped to today; `startDate` clamped to today−90d; `startDate > endDate` normalized. Defaults to last 90 days. Straightforward and correct.
- Honest note: live execution of the clamp requires an owner JWT, which is impossible until the auth bug is fixed.

### 4. Disconnect flow (client) — PASS (inspection; never executed against the real connection)
- `disconnectBank()` (`index.html` ~L3513): deletes `simplefin_connections` with `.eq("user_id", uid)` — caller-only row, RLS-enforced.
- `clearLocalBankData()`: nulls `trackData`/`prevLiveBatch`, removes `upmore_last_sync`.
- Failure copy is honest (reports backend failure instead of claiming success).
- The Disconnect row only renders when `trackData.isLive` is true.
- Note: the vaulted Access URL persists in the Vault after disconnect (orphaned, service-role-only, unreachable from the client). The sheet copy does not overclaim ("deletes your bank connection on our servers").

### 5. RLS policies — PASS
- `simplefin_connections`: `FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id)` — owner-only.
- `simplefin_requests`: same owner-only policy. Request log is per-user; no cross-user visibility.

## What could NOT be tested
- **Owner-authenticated success** (needs the auth fix + Vishnu's live session): full `/accounts` fetch, errlist surfacing, pending/transfer/refund handling through the proxy.
- **Non-owner 403** (needs the auth fix): must be re-run after redeploy.
- Transfer/refund/pending/categorization are covered separately by the 303 suite against the app's client pipeline (cases 1-024, 1-026, 1-028, 1-029, 1-031 — all Pass).

## Cleanup — COMPLETE
Three throwaway QA users created across test runs (`qa-throwaway-nonowner@`, `qa-debug-jwt@`, `qa-repeat@`, `qa-nonowner-403@`, `qa-debug-jwt@`); **all deleted** via GoTrue admin API, deletion verified (GET → 404 for each). No QA rows remain in `simplefin_requests` (0 rows for all test user_ids). No test data in `simplefin_connections`. No credentials stored anywhere.

## Required follow-up (for parent)
1. Apply the one-line fix (`getUser(jwt)`) to `supabase/functions/simplefin-proxy/index.ts` and redeploy via `sb.py deploy simplefin-proxy`.
2. Re-run: owner-authenticated success (needs Vishnu's session) and non-owner 403 + zero leakage.
3. Then the SimpleFIN checklist is complete.
