// Upmore agent-exec edge function.
// The real-world execution agent. POST /functions/v1/agent-exec  { approval_id }
// Auth: Supabase JWT in Authorization header.
// Flow: verify approval (owned by caller, status approved) -> load vaulted
// merchant credential -> run merchant playbook -> record evidence -> done/failed.
//
// Safety: only acts on approvals the user explicitly approved. Every run is
// written to exec_runs with evidence. Never moves money.

import { serve } from "https://deno.land/std@0.208.0/http/server.ts";
import { createClient } from "https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.117.1/+esm";

const ALLOWED_ORIGINS = new Set([
  "https://upmore-srikanthvishnu90-sketchs-projects.vercel.app",
  "http://localhost:3000",
  "http://localhost:8000",
  "http://localhost:8080",
  "http://127.0.0.1:8000",
  "http://127.0.0.1:8080",
]);
function corsFor(req: Request): Record<string, string> {
  const origin = req.headers.get("Origin") ?? "";
  const h: Record<string, string> = {
    "Access-Control-Allow-Headers": "authorization, content-type",
    "Vary": "Origin",
  };
  if (ALLOWED_ORIGINS.has(origin)) h["Access-Control-Allow-Origin"] = origin;
  return h;
}

type ExecContext = {
  username: string;
  password: string;
  approval: Record<string, unknown>;
  admin: ReturnType<typeof createClient>;
};

type ExecResult = {
  ok: boolean;
  evidence: Record<string, unknown>;
  error?: string;
};

// ---- cookie jar for HTTP playbooks ----
class Jar {
  private cookies = new Map<string, string>();
  ingest(setCookies: string[] | null, domain: string) {
    if (!setCookies) return;
    for (const sc of setCookies) {
      const pair = sc.split(";")[0];
      const eq = pair.indexOf("=");
      if (eq > 0) this.cookies.set(pair.slice(0, eq).trim(), pair.slice(eq + 1).trim());
    }
  }
  header(): string {
    return [...this.cookies.entries()].map(([k, v]) => `${k}=${v}`).join("; ");
  }
}

async function fetchWithJar(jar: Jar, url: string, init: RequestInit = {}): Promise<Response> {
  const headers = new Headers(init.headers);
  const ch = jar.header();
  if (ch) headers.set("Cookie", ch);
  if (!headers.has("User-Agent")) {
    headers.set("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36");
  }
  const res = await fetch(url, { ...init, headers, redirect: "manual" });
  const sc = res.headers.getSetCookie?.() ?? [];
  try {
    const u = new URL(url);
    jar.ingest(sc.length ? sc : null, u.hostname);
  } catch { /* ignore */ }
  return res;
}

// ---- merchant playbooks ----
const playbooks: Record<string, (ctx: ExecContext) => Promise<ExecResult>> = {
  // Devin (Cognition AI) — implemented from auth recon 2026-09-26.
  "devin": playbookDevin,
};

async function playbookDevin(ctx: ExecContext): Promise<ExecResult> {
  // NOTE: filled in from recon. If Devin auth turns out to need a real
  // browser (OAuth / magic link), this returns a clear needs_browser error
  // and the run is marked failed with that reason — never faked.
  return {
    ok: false,
    evidence: { merchant: "devin", stage: "not_implemented" },
    error: "Devin playbook pending auth recon",
  };
}

// ---- main ----
serve(async (req) => {
  const cors = corsFor(req);
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });
  const json = (body: unknown, status = 200) =>
    new Response(JSON.stringify(body), { status, headers: { ...cors, "Content-Type": "application/json" } });

  try {
    const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
    const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
    const anonKey = Deno.env.get("SUPABASE_ANON_KEY")!;

    const jwt = (req.headers.get("authorization") || "").replace(/^Bearer\s+/i, "");
    if (!jwt) return json({ error: "Sign in required" }, 401);
    const userClient = createClient(supabaseUrl, anonKey, {
      global: { headers: { Authorization: `Bearer ${jwt}` } },
    });
    const { data: { user }, error: authErr } = await userClient.auth.getUser(jwt);
    if (authErr || !user) return json({ error: "Invalid session" }, 401);
    const admin = createClient(supabaseUrl, serviceKey);

    const { approval_id } = await req.json().catch(() => ({}));
    if (!approval_id) return json({ error: "approval_id required" }, 400);

    // Load + verify approval. Must be owned by caller and in approved state.
    const { data: approval } = await admin.from("exec_approvals")
      .select("*").eq("id", approval_id).maybeSingle();
    if (!approval || approval.user_id !== user.id) {
      return json({ error: "Approval not found" }, 404);
    }
    if (approval.status !== "approved") {
      return json({ error: `Approval is ${approval.status}, not approved` }, 409);
    }
    if (approval.action !== "cancel_subscription") {
      return json({ error: `Unsupported action ${approval.action}` }, 400);
    }
    const playbook = playbooks[approval.merchant_key];
    if (!playbook) {
      return json({ error: `No playbook for ${approval.merchant_key}` }, 400);
    }

    // Load vaulted credential.
    const { data: credRef } = await admin.from("exec_credential_refs")
      .select("*").eq("user_id", user.id).eq("merchant_key", approval.merchant_key).maybeSingle();
    if (!credRef) {
      return json({ error: "No saved login for this merchant. Connect it in the app first." }, 409);
    }
    const vres = await fetch(
      `${supabaseUrl}/rest/v1/vault_secrets?select=secret&name=eq.${encodeURIComponent(credRef.vault_name)}`,
      { headers: { "apikey": serviceKey, "Authorization": `Bearer ${serviceKey}` } },
    );
    if (!vres.ok) return json({ error: "Could not read saved login" }, 500);
    const vrows = await vres.json();
    let cred: { username?: string; password?: string } = {};
    try { cred = JSON.parse(vrows?.[0]?.secret || "{}"); } catch { /* ignore */ }
    if (!cred.username || !cred.password) {
      return json({ error: "Saved login is incomplete. Reconnect it in the app." }, 409);
    }

    // Mark executing + open run row.
    await admin.from("exec_approvals").update({ status: "executing" }).eq("id", approval.id);
    const { data: run } = await admin.from("exec_runs")
      .insert({ approval_id: approval.id, user_id: user.id, status: "started", evidence: {} })
      .select("id").single();

    let result: ExecResult;
    try {
      result = await playbook({ username: cred.username, password: cred.password, approval, admin });
    } catch (e) {
      result = { ok: false, evidence: { merchant: approval.merchant_key, stage: "exception" }, error: String(e?.message || e) };
    }

    const finalStatus = result.ok ? "done" : "failed";
    await admin.from("exec_runs").update({
      status: finalStatus,
      evidence: result.evidence,
      error: result.error || null,
      finished_at: new Date().toISOString(),
    }).eq("id", run.id);
    await admin.from("exec_approvals").update({
      status: finalStatus,
      decided_at: new Date().toISOString(),
    }).eq("id", approval.id);

    return json({ ok: result.ok, status: finalStatus, evidence: result.evidence, error: result.error || null });
  } catch (e) {
    return json({ error: String(e?.message || e) }, 500);
  }
});
