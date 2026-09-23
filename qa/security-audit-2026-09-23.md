# Upmore Security Audit — 2026-09-23

**Scope:** client SPA (`src/upmore-app-template.html`, built `index.html`), Supabase Postgres RLS, `agent-chat` edge function, service worker, vendored deps, git history for secrets.
**Method:** code review + live DB inspection (`pg_policies`, `pg_tables`, function defs/grants) + live REST probe. No test users created; no writes to prod.
**Verdict:** No criticals. **2 highs** (both in the chat rate limiter — bypassable and cross-user DoS-able), several mediums. Core posture is solid: RLS is correctly scoped everywhere, no XSS sink found unescaped, no secrets in git, JWT enforcement correct.

---

## HIGH

### H1 — Authenticated users can reset their own chat rate limit (rate limiter bypass)
- **Where:** DB policy `rl_agent_rate_limits_own` on `public.agent_rate_limits` — `pg_policies` shows `cmd: ALL`, `roles: {public}`, qual/with_check `(auth.uid() = user_id)`.
- **Impact:** Any signed-in user can run `UPDATE agent_rate_limits SET count = 0 WHERE user_id = <own uuid>` via the REST API and chat without limit. Each `agent-chat` call costs Anthropic input+output tokens, so this is a direct API-cost abuse vector. The migration file's own comment says "The limiter table is service-managed only; no direct client access" — but the shipped policy contradicts that (`ALL` instead of `SELECT`-only or no policy at all).
- **Verified:** yes, from live `pg_policies` + `supabase/migrations/20260923_000001_agent_rate_limits.sql`.
- **Fix (code):** change the policy to `FOR SELECT` only (or drop it — RLS deny-by-default), keeping the `SECURITY DEFINER` `agent_rl_bump` as the sole writer. No user action needed.

### H2 — `agent_rl_bump` RPC lets any authenticated user burn another user's rate-limit quota
- **Where:** `public.agent_rl_bump(p_user uuid, p_limit integer)` is `SECURITY DEFINER` and takes the target user as a **parameter**; migration grants `EXECUTE ... TO authenticated`. Supabase exposes every granted function at `POST /rest/v1/rpc/agent_rl_bump`.
- **Impact:** An attacker with any valid account can call the RPC directly with a victim's UUID ~60 times and lock that victim out of the Guide (429) for the rest of the hour window. The edge function itself always passes `p_user = user.id` from the verified JWT, so this only matters via direct RPC calls. Mitigating factors: attacker needs a real victim UUID (table has FK to `profiles(id)`, so random UUIDs fail; user UUIDs are not enumerable through the API thanks to RLS), and there is no sensitive data at stake — it's availability-only.
- **Verified:** schema + grants verified live; REST exposure confirmed (anon `POST /rest/v1/rpc/agent_rl_bump` returns 401, proving the endpoint exists and anon is correctly blocked). End-to-end authenticated call not executed (would write to prod).
- **Fix (code):** stop taking `p_user` as a parameter — use `auth.uid()` inside the function body. Alternatively `REVOKE EXECUTE ... FROM authenticated` and have the edge function call it with the service_role key (it already holds one server-side). No user action needed.

---

## MEDIUM

### M1 — No Content-Security-Policy anywhere
- **Where:** `src/build-app.py` emits no CSP; `index.html` has no `<meta http-equiv="Content-Security-Policy">`; `vercel.json` sets only `Cache-Control` headers. (The old `src/build.py` referenced in AGENTS.md that emitted CSP script hashes no longer exists in the repo.)
- **Impact:** defense-in-depth only — no XSS sink was found unescaped (see below), but the app renders large amounts of `innerHTML`, so a single future escaping miss becomes fully exploitable script execution instead of being contained.
- **Fix (code):** add CSP via `vercel.json` headers. Complication: the whole app is one giant inline `<script>`, so a strict `script-src 'self'` requires hashing the bundle in the build step (the old build.py did this); the pragmatic interim is `script-src 'self' 'unsafe-inline'` which still blocks inline event handlers and `javascript:` URLs but not injected `<script>` tags. No user action needed.

### M2 — `agent-chat` accepts unbounded message length
- **Where:** `supabase/functions/agent-chat/index.ts` — `const { thread_id, message } = await req.json(); if (!message || typeof message !== "string") return ...` — no maximum length.
- **Impact:** 60 requests/hour × megabyte-size messages = large Anthropic input-token bills; also a cheap way to amplify the H1 bypass. Output is already capped (`MAX_TOKENS = 400`).
- **Fix (code):** reject (400) or truncate messages over ~2,000–4,000 chars. No user action needed.

### M3 — Google Fonts loads contradict the privacy policy's "no third-party trackers" claim
- **Where:** `src/upmore-app-template.html:16-18` — `<link rel="preconnect" href="https://fonts.googleapis.com">`, `<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>`, plus the `css2` stylesheet. These fire on every page load and send IP + user-agent to Google.
- **Impact:** privacy, not code execution (font CSS, not script). But both the in-app privacy sheet (uncommitted, in working tree) and `PRIVACY_POLICY.md` state "no third-party trackers" / "no third-party analytics or ad trackers" — currently inaccurate.
- **Fix (code):** self-host the Schibsted Grotesk woff2 files in the repo (SIL OFL licensed) and drop the three `<link>` tags; then the policy claim becomes true. No user action needed.

### M4 — Vendored supabase-js is ~2 years stale; bundled auth-js is below CVE-2025-48370 fix version
- **Where:** `src/vendor/supabase-js.min.js` — header says built from `@supabase/supabase-js@2.39.0` (Nov 2023); bundled `@supabase/auth-js` ≈ 2.56.0. CVE-2025-48370 (CVSS 2.7 Low): auth-js < 2.70.0 didn't require UUID-shaped ids in admin functions (`getUserById`, `deleteUser`, `updateUserById`, `listFactors`, `deleteFactor`), allowing URL path traversal into unintended admin API calls.
- **Impact in this app: none reachable.** Those are service_role admin functions; the client only ever calls `signInWithOAuth`, `signInWithPassword`, `getSession`, `signOut`, `onAuthStateChange` — none of the vulnerable functions. No other public CVE was found against the bundled version relevant to this usage.
- **Fix (code):** re-vendor a current supabase-js 2.x (latest is 2.116.0 per Snyk) and drop it into `src/vendor/`; rebuild. No user action needed. (The edge function pins `supabase-js@2.39.0` from jsdelivr too — bump that import as well.)

---

## LOW / informational

### L1 — CORS `Access-Control-Allow-Origin: *` on agent-chat
- `supabase/functions/agent-chat/index.ts` (top): preflight and all JSON responses carry `*`. Safe in practice because every non-OPTIONS path requires a valid user JWT (`verify_jwt=true` on the gateway **plus** explicit `getUser(token)` in code), but it lets any website spend the *user's own* rate-limit quota via their browser session. Could tighten to the production origin. Code fix; no user action.

### L2 — Edge-function remote imports have no integrity pinning
- `index.ts` imports `deno.land/std@0.208.0` and `cdn.jsdelivr.net/npm/@supabase/supabase-js@2.39.0/+esm` by version tag, no `deno.lock`. A compromised CDN/tag could inject code into the function at deploy time. Versions are pinned (not ranges), which limits the window. Consider vendoring or adding a lockfile. Code fix; no user action.

### L3 — No `javascript:`-scheme validation on URLs rendered into `href`
- `stepLinks` (template ~line 1320), `r.url` (Explore detail), `s.cancel_url` (Save tab, line 1971) are interpolated as `href="${esc(u)}"`. `esc()` neutralizes quotes but a `javascript:` URL would still execute. Currently all these URLs come from curated/verified catalog data and `cancel_url` is **not** user-editable (the add-subscription form at lines 745–754 only takes merchant/plan/amount/interval/date), so this is defense-in-depth only. The chat markdown renderer (`md()`, line 1733) only linkifies `https?://`, so it is not affected. Code fix: scheme-allowlist helper. No user action.

### L4 — `thread_id` request field is not type-validated
- `index.ts`: `let tid: string = thread_id` with no check. A non-string truthy value causes a DB error → generic 500 (safe, just noisy). Cross-user thread access is still blocked because every `agent_messages` read/insert goes through the `own messages` RLS policy (thread ownership check) on the anon-key client. Code fix: validate `typeof thread_id === "string"`. No user action.

### L5 — Anon key is embedded in the client source (template line 1608)
- By design for Supabase; not a secret. Safe **because** RLS is correctly scoped (verified below). No action.

### L6 — Session JWTs live in localStorage (supabase-js default)
- Standard SPA practice; no custom token handling, no passwords or refresh material beyond the SDK's own session. Would be exposed by an XSS, but no unescaped sink was found. `SIGNED_OUT` correctly clears state and reloads. No action.

---

## VERIFIED GOOD (with evidence)

- **RLS everywhere, correctly scoped.** All 13 public tables (`agent_messages`, `agent_rate_limits`, `agent_threads`, `playbook_progress`, `profiles`, `proof_log`, `reminders`, `routes`, `save_claims`, `save_ledger`, `save_receipts`, `save_renewals`, `save_subscriptions`) have `rowsecurity = true`. No `USING (true)` policy exists. Per-user tables all enforce `auth.uid() = user_id` (or `id`, or thread-ownership EXISTS for `agent_messages`) on both read and write. `routes` and `proof_log` are `SELECT`-only for `authenticated` — intended (public catalog + verification log), and anon (no JWT) gets zero rows from every table.
- **No cross-user read/write path.** `agent_messages` "own messages" policy checks thread ownership via EXISTS on `agent_threads`; the edge function uses the anon key + user JWT (never service_role), so RLS applies to every query it makes.
- **JWT enforcement on agent-chat is correct.** Gateway `verify_jwt: true` confirmed live (function v88, ACTIVE). Code additionally extracts the Bearer token and calls `supabase.auth.getUser(token)` explicitly — the known `getUser()`-with-no-arg 401 footgun is avoided (comment in code references the earlier fix).
- **XSS: no unescaped sink found.** `esc()` (template line 1039) escapes `&<>"` and is applied to route titles/meta/steps/links, the 7-answer fields (`sevenFields`, line 1047), and all user-entered Save-tab data (subscription merchant/plan/waste notes, receipt merchant, claim merchant/steps). User chat messages use `textContent` (`addMe`). AI replies go through `md()` (line 1733) which escapes **first**, then adds `<b>`/`<a>` — the link regex only matches `https?://`, and quote-breaking is neutralized because `"` is already `&quot;` before linkification (verified by tracing). The one unescaped interpolation (`$("based").innerHTML`, line 1199) uses `st` from a hardcoded state-name map and `tl` from a fixed enum — not user-controlled strings.
- **Rate limiting exists and is otherwise sound:** 60 req / fixed 60-min window / user, enforced on every request including deterministic fast paths, via atomic upsert RPC (race fixed in migration `20260923_000001`), 429 with `Retry-After`. The bypass vectors are H1/H2 above, not the algorithm.
- **No secrets in git.** Full `git log -p --all` scan: no `sk-ant-`, `sb_secret_`, GitHub tokens, or service_role values. The only JWT-shaped string in history is the **anon** key (public by design). All `service_role` hits are code that fetches it transiently from the Management API, never a value. No `.env`/credential files ever committed. The Vercel token and Anthropic key pasted in chat did **not** land in the repo (verified).
- **Anthropic key is server-side only** (`Deno.env.get("ANTHROPIC_API_KEY")` in the edge function; client comment explicitly notes it never leaves the server).
- **Error messages are generic** (`unauthorized`, `internal`, `agent_unavailable`); details go to server logs only.
- **OAuth is delegated to supabase-js** (PKCE + state handled by the SDK): `signInWithOAuth({ provider: "google", options: { redirectTo: location.origin + location.pathname } })` — same-origin redirect, no custom state/redirect logic to get wrong. Password login uses `signInWithPassword`; the password is never stored (only in the transient login form field).
- **Service worker is safe:** `src/sw.js` (v3) only handles same-origin GETs, explicitly skips `/rest/` and `/auth/`, never caches non-OK responses; `agent-chat` is POST-only so no authenticated API response is ever cached. Scope is root (intended for the SPA shell). `ignoreSearch: true` on cache match is a minor staleness quirk, not a poisoning vector (same-origin static assets only).
- **Zero external scripts.** The only third-party loads are the Google Fonts CSS/font files (M3). supabase-js is vendored inline by `build-app.py`.
- **Prompt-leakage defenses exist:** `trySyspromptGuard` refuses system-prompt extraction requests deterministically before the model call; a grounding post-check (`checkGrounding`) replaces violating replies with safe fallbacks; scam/gambling/privacy guards run as deterministic pre-filters.
- **Data minimization is reasonable.** `profiles`: display_name, state, free_time_hours, paycheck_status, cash_available, age, prefs — all used by the product. Chat messages are stored (core feature, disclosed in the privacy policy). No payment details, bank credentials, location, or contacts are collected; the Gmail/Plaid connectors are UI stubs ("Not available yet — needs owner setup") holding only local toggle flags in localStorage. `proof_log` holds route-verification audit rows, not user PII. No storage buckets exist.

## Suggested fix order
1. H1 — restrict `agent_rate_limits` RLS to deny client writes (one-policy migration).
2. H2 — switch `agent_rl_bump` to `auth.uid()` internally (same migration).
3. M2 — cap `message` length in `agent-chat`.
4. M3 — self-host the font; then the privacy policy's "no third-party trackers" line is true.
5. M1 — add CSP (hash the inline bundle in `build-app.py`, or interim `unsafe-inline` policy via `vercel.json`).
6. M4 — re-vendor current supabase-js 2.x (client + edge-function import).
7. L1–L4 as hardening when convenient.

All of the above are code fixes — **no user action is required for any finding**. The two HIGHs should land before the beta user starts driving real chat volume, since H1 directly converts chat usage into Anthropic spend.
