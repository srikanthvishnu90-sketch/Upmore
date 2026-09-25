// SimpleFIN proxy Edge Function (Upmore Track spec).
// Server-side only: reads the vaulted Access URL, calls the Bridge,
// returns sanitized accounts/transactions. The secret never reaches the client.
//
// Rules: read-only, ≤24 req/day, ≤90 day windows, surface errlist,
// pending excluded from totals, transfers excluded from spending,
// refunds netted (client-side), delete data on disconnect.
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

const VAULT_KEY = "simplefin_access_url";

async function getAccessUrl(supabaseUrl: string, serviceKey: string): Promise<string | null> {
  // Read from Vault via the secrets API (service_role only)
  const res = await fetch(`${supabaseUrl}/rest/v1/vault_secrets?select=secret&name=eq.${VAULT_KEY}`, {
    headers: {
      "apikey": serviceKey,
      "Authorization": `Bearer ${serviceKey}`,
    },
  });
  if (!res.ok) return null;
  const rows = await res.json();
  return rows?.[0]?.secret || null;
}

serve(async (req) => {
  const cors = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  };
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });

  try {
    const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
    const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
    
    const accessUrl = await getAccessUrl(supabaseUrl, serviceKey);
    if (!accessUrl) {
      return new Response(JSON.stringify({ error: "SimpleFIN not connected" }), {
        status: 404, headers: { ...cors, "Content-Type": "application/json" }
      });
    }

    // Parse the Access URL to extract Basic auth credentials
    const url = new URL(accessUrl);
    const username = decodeURIComponent(url.username);
    const password = decodeURIComponent(url.password);
    const bridgeBase = `${url.protocol}//${url.host}`;
    const accountsPath = url.pathname; // e.g. /simplefin/accounts

    // Parse request body for date range (default: last 90 days)
    let startDate: string | null = null;
    let endDate: string | null = null;
    try {
      const body = await req.json();
      startDate = body.startDate || null;
      endDate = body.endDate || null;
    } catch {}

    // Build the accounts URL with date range
    let fetchUrl = `${bridgeBase}${accountsPath}?version=2`;
    if (startDate) fetchUrl += `&start-date=${startDate}`;
    if (endDate) fetchUrl += `&end-date=${endDate}`;

    const auth = btoa(`${username}:${password}`);
    const bridgeRes = await fetch(fetchUrl, {
      headers: { "Authorization": `Basic ${auth}` },
    });

    if (!bridgeRes.ok) {
      return new Response(JSON.stringify({ 
        error: `Bridge error: ${bridgeRes.status}`,
        errlist: [`HTTP ${bridgeRes.status} from SimpleFIN Bridge`]
      }), {
        status: 502, headers: { ...cors, "Content-Type": "application/json" }
      });
    }

    const data = await bridgeRes.json();
    
    // Sanitize: strip any credential material, return only account/tx data
    // Surface the errlist per spec
    const result = {
      accounts: (data.accounts || []).map((a: any) => ({
        id: a.id,
        name: a.name,
        currency: a.currency,
        balance: a.balance,
        available_balance: a["available-balance"],
        balance_date: a["balance-date"],
      })),
      transactions: [],
      errlist: data.errlist || [],
    };

    // Flatten transactions from all accounts
    (data.accounts || []).forEach((a: any) => {
      (a.transactions || []).forEach((t: any) => {
        result.transactions.push({
          id: t.id,
          account_id: a.id,
          posted_at: t.posted ? new Date(t.posted * 1000).toISOString().slice(0, 10) : null,
          amount: t.amount, // negative = outflow, positive = inflow
          merchant_raw: t.description || t.memo || "Unknown",
          is_pending: !!t.pending,
          // SimpleFIN doesn't flag transfers explicitly; client infers from description
        });
      });
    });

    // Sort by date descending
    result.transactions.sort((a: any, b: any) => 
      (b.posted_at || "").localeCompare(a.posted_at || "")
    );

    return new Response(JSON.stringify(result), {
      headers: { ...cors, "Content-Type": "application/json" }
    });

  } catch (e) {
    return new Response(JSON.stringify({ error: String(e) }), {
      status: 500, headers: { ...cors, "Content-Type": "application/json" }
    });
  }
});
