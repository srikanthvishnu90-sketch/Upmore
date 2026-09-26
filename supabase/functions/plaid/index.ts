// Upmore plaid edge function — server-side Plaid integration (read-only).
// Actions via POST JSON {action, ...}:
//   status      -> {plaid_configured, connected}
//   link_token  -> {link_token} (503 honest error if PLAID_CLIENT_ID/PLAID_SECRET missing)
//   exchange    -> {public_token} -> stores access token in Vault -> {connected: true}
//   holdings    -> sanitized {accounts, holdings, securities}; 202 {retry:true} if PRODUCT_NOT_READY
//   disconnect  -> deletes the vault token -> {connected: false}
//
// Security model:
// - Caller must present a valid Supabase JWT (401 otherwise).
// - Vault token name is exec_cred_<user.id>_plaid. NOTE: the existing
//   exec_vault_store / exec_vault_delete RPCs enforce the exec_cred_% prefix,
//   so a literal "plaid_access_token_<id>" name is rejected by the RPC — the
//   exec_cred_<user.id>_plaid name follows the established vault convention.
// - The access token never reaches the client; holdings are sanitized.
// - CORS restricted to the Upmore origins (no wildcard).
// - Rate budget: 24 requests/day/user (public.plaid_requests).
// - Read-only: only Plaid Investments product (holdings, balances). Upmore
//   never moves money.
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.39.0";

const ALLOWED_ORIGINS = [
  "https://upmore-srikanthvishnu90-sketchs-projects.vercel.app",
  "http://localhost:8901",
  "http://127.0.0.1:8901",
];
const DAILY_BUDGET = 24;
const PLAID_HOSTS: Record<string, string> = {
  production: "https://production.plaid.com",
  development: "https://development.plaid.com",
  sandbox: "https://sandbox.plaid.com",
};

function corsFor(req: Request) {
  const origin = req.headers.get("origin") || "";
  const allow = ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0];
  return {
    "Access-Control-Allow-Origin": allow,
    "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Vary": "Origin",
  };
}

const vaultName = (userId: string) => `exec_cred_${userId}_plaid`;

async function getVaultSecret(supabaseUrl: string, serviceKey: string, name: string): Promise<string | null> {
  const res = await fetch(`${supabaseUrl}/rest/v1/vault_secrets?select=secret&name=eq.${name}`, {
    headers: { "apikey": serviceKey, "Authorization": `Bearer ${serviceKey}` },
  });
  if (!res.ok) return null;
  const rows = await res.json().catch(() => null);
  const s = rows?.[0]?.secret;
  return (typeof s === "string" && s.length > 0) ? s : null;
}

async function plaidCall(host: string, clientId: string, secret: string, path: string, body: Record<string, unknown>) {
  const res = await fetch(`${host}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ client_id: clientId, secret, ...body }),
  });
  const data = await res.json().catch(() => ({}));
  return { ok: res.ok, status: res.status, data };
}

serve(async (req) => {
  const cors = corsFor(req);
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });
  const json = (body: unknown, status = 200) =>
    new Response(JSON.stringify(body), { status, headers: { ...cors, "Content-Type": "application/json" } });

  try {
    const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
    const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
    const anonKey = Deno.env.get("SUPABASE_ANON_KEY")!;

    // 1. Authenticate: verify the caller's JWT via Auth.
    const jwt = (req.headers.get("authorization") || "").replace(/^Bearer\s+/i, "");
    if (!jwt) return json({ error: "Sign in required" }, 401);
    const userClient = createClient(supabaseUrl, anonKey, {
      global: { headers: { Authorization: `Bearer ${jwt}` } },
    });
    const { data: { user }, error: authErr } = await userClient.auth.getUser(jwt);
    if (authErr || !user) return json({ error: "Invalid session" }, 401);
    const admin = createClient(supabaseUrl, serviceKey);

    const { action, ...params } = await req.json().catch(() => ({}));

    // 2. Rate budget: <=24 requests/day per user.
    const dayAgo = new Date(Date.now() - 864e5).toISOString();
    const { count } = await admin.from("plaid_requests")
      .select("id", { count: "exact", head: true })
      .eq("user_id", user.id).gte("requested_at", dayAgo);
    if ((count || 0) >= DAILY_BUDGET) {
      return json({ error: "Daily Plaid budget reached (24/day). Try tomorrow." }, 429);
    }
    await admin.from("plaid_requests").insert({ user_id: user.id });

    const clientId = Deno.env.get("PLAID_CLIENT_ID") || "";
    const plaidSecret = Deno.env.get("PLAID_SECRET") || "";
    const plaidEnv = (Deno.env.get("PLAID_ENV") || "production").toLowerCase();
    const host = PLAID_HOSTS[plaidEnv] || PLAID_HOSTS.production;
    const plaidConfigured = !!(clientId && plaidSecret);
    const name = vaultName(user.id);

    if (action === "status") {
      const token = await getVaultSecret(supabaseUrl, serviceKey, name);
      return json({ plaid_configured: plaidConfigured, connected: !!token });
    }

    if (action === "link_token") {
      if (!plaidConfigured) return json({ error: "Plaid not configured yet", plaid_configured: false }, 503);
      const { ok, data } = await plaidCall(host, clientId, plaidSecret, "/link/token/create", {
        client_name: "Upmore",
        products: ["investments"],
        country_codes: ["US"],
        language: "en",
        user: { client_user_id: user.id },
      });
      if (!ok || !data.link_token) {
        return json({ error: data?.error_message || data?.error_code || "Link token creation failed" }, 502);
      }
      return json({ link_token: data.link_token });
    }

    if (action === "exchange") {
      if (!plaidConfigured) return json({ error: "Plaid not configured yet", plaid_configured: false }, 503);
      const publicToken = String(params.public_token || "");
      if (!publicToken) return json({ error: "public_token required" }, 400);
      const { ok, data } = await plaidCall(host, clientId, plaidSecret, "/item/public_token/exchange", {
        public_token: publicToken,
      });
      if (!ok || !data.access_token) {
        return json({ error: data?.error_message || data?.error_code || "Token exchange failed" }, 502);
      }
      const { error: verr } = await admin.rpc("exec_vault_store", {
        p_name: name,
        p_secret: String(data.access_token),
      });
      if (verr) return json({ error: "Could not save connection" }, 500);
      return json({ connected: true });
    }

    if (action === "holdings") {
      if (!plaidConfigured) return json({ error: "Plaid not configured yet", plaid_configured: false }, 503);
      const accessToken = await getVaultSecret(supabaseUrl, serviceKey, name);
      if (!accessToken) return json({ error: "Plaid not connected" }, 404);
      const { ok, data } = await plaidCall(host, clientId, plaidSecret, "/investments/holdings/get", {
        access_token: accessToken,
      });
      if (!ok) {
        // Holdings not ready yet — not an error; client should retry later.
        if (data?.error_code === "PRODUCT_NOT_READY") return json({ retry: true }, 202);
        return json({ error: data?.error_message || data?.error_code || "Holdings fetch failed" }, 502);
      }
      const accounts = (data.accounts || []).map((a: any) => ({
        id: a.account_id,
        name: a.name,
        type: a.type,
        subtype: a.subtype ?? null,
        balances: {
          current: a.balances?.current ?? null,
          available: a.balances?.available ?? null,
          limit: a.balances?.limit ?? null,
          iso_currency_code: a.balances?.iso_currency_code ?? null,
        },
      }));
      const holdings = (data.holdings || []).map((h: any) => ({
        account_id: h.account_id,
        security_id: h.security_id,
        quantity: h.quantity,
        institution_price: h.institution_price,
        institution_value: h.institution_value,
        cost_basis: h.cost_basis ?? null,
      }));
      const securities = (data.securities || []).map((s: any) => ({
        security_id: s.security_id,
        ticker_symbol: s.ticker_symbol ?? null,
        name: s.name ?? null,
        type: s.type ?? null,
      }));
      return json({ accounts, holdings, securities });
    }

    if (action === "disconnect") {
      const { error: derr } = await admin.rpc("exec_vault_delete", { p_name: name });
      if (derr) return json({ error: "Could not remove connection" }, 500);
      return json({ connected: false });
    }

    return json({ error: "Unknown action" }, 400);
  } catch (e) {
    return json({ error: String((e as any)?.message || e) }, 500);
  }
});
