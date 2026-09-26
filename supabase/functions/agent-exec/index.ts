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
  // Manual redirect: automatic following hides intermediate Set-Cookie
  // headers from the jar. Callers that expect redirects must loop.
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

// GET following redirects (up to 5), keeping the jar.
async function fetchFollow(jar: Jar, url: string): Promise<{ res: Response; text: string }> {
  let res = await fetchWithJar(jar, url);
  for (let i = 0; i < 5; i++) {
    const loc = res.headers.get("location");
    if (!loc || (res.status !== 301 && res.status !== 302 && res.status !== 303 && res.status !== 307 && res.status !== 308)) break;
    res = await fetchWithJar(jar, new URL(loc, url).toString());
  }
  return { res, text: await res.text() };
}

// ---- merchant playbooks ----
const playbooks: Record<string, (ctx: ExecContext) => Promise<ExecResult>> = {
  // Devin (Cognition AI) — implemented from auth recon 2026-09-26.
  "devin": playbookDevin,
};

async function playbookDevin(ctx: ExecContext): Promise<ExecResult> {
  // Adaptive playbook: probes the live login page, detects the auth
  // mechanism, and either executes the cancellation or fails with a
  // precise reason (e.g. needs_browser for OAuth/magic-link). Never fakes.
  const ev: Record<string, unknown> = { merchant: "devin" };
  const jar = new Jar();
  try {
    // 1. Fetch login page (following redirects), detect auth mechanism.
    let lp = await fetchWithJar(jar, "https://app.devin.ai/auth/login?redirect=/&reauth=true");
    for (let i = 0; i < 5; i++) {
      const loc = lp.headers.get("location");
      if (!loc || (lp.status !== 301 && lp.status !== 302 && lp.status !== 303 && lp.status !== 307 && lp.status !== 308)) break;
      lp = await fetchWithJar(jar, new URL(loc, "https://app.devin.ai").toString());
    }
    const html = await lp.text();
    ev.login_page_status = lp.status;
    ev.login_page_bytes = html.length;
    const lower = html.toLowerCase();
    const hasPassword = /type=["']password["']/i.test(html);
    const hasGoogle = /continue with google|accounts\.google\.com/i.test(html);
    const hasMagicLink = /magic link|send.*link.*email|check your email/i.test(html) && !hasPassword;
    const hasGithub = /continue with github|github\.com\/login\/oauth/i.test(html);
    // Devin ships a JS SPA shell: no server-rendered form. Their bundle
    // (verified 2026-09-26) uses Auth0 SPA (loginWithRedirect) + a React
    // billing UI with an interactive cancel dialog on private APIs.
    const isSpaShell = /<div id=["']root["']><\/div>|__vite__|rolldown-runtime/i.test(html) && !hasPassword;
    ev.auth_detected = { password_form: hasPassword, google_oauth: hasGoogle, magic_link: hasMagicLink, github_oauth: hasGithub, spa_shell: isSpaShell };

    if (!hasPassword) {
      ev.stage = "auth_unsupported";
      const which = isSpaShell
        ? "a JavaScript SPA login (Auth0 redirect flow — verified from their shipped bundle)"
        : hasGoogle ? "Google OAuth" : hasMagicLink ? "email magic link" : hasGithub ? "GitHub OAuth" : "unknown";
      return { ok: false, evidence: ev, error: `Devin sign-in uses ${which} — needs a real browser session. (needs_browser)` };
    }

    // 2. Password form: parse action + fields, submit.
    ev.stage = "login_attempt";
    const formMatch = html.match(/<form[^>]*action=["']([^"']*)["'][^>]*>/i);
    let action = formMatch ? formMatch[1] : "";
    if (action && !action.startsWith("http")) {
      action = new URL(action, "https://app.devin.ai").toString();
    }
    if (!action) action = "https://app.devin.ai/auth/login?redirect=/&reauth=true";
    ev.login_action = action;
    // Collect hidden inputs (CSRF etc.)
    const hidden: Record<string, string> = {};
    const re = /<input[^>]*type=["']hidden["'][^>]*>/gi;
    let m: RegExpExecArray | null;
    while ((m = re.exec(html))) {
      const nm = m[0].match(/name=["']([^"']+)["']/i);
      const vv = m[0].match(/value=["']([^"']*)["']/i);
      if (nm) hidden[nm[1]] = vv ? vv[1] : "";
    }
    // Guess credential field names from the HTML.
    const emailName = (html.match(/<input[^>]*type=["']email["'][^>]*name=["']([^"']+)["']/i) || [])[1]
      || (html.match(/<input[^>]*name=["']([^"']*email[^"']*)["'][^>]*type=["'](?:email|text)["']/i) || [])[1]
      || "email";
    const passName = (html.match(/<input[^>]*type=["']password["'][^>]*name=["']([^"']+)["']/i) || [])[1] || "password";
    const body = new URLSearchParams({ ...hidden, [emailName]: ctx.username, [passName]: ctx.password });
    const loginRes = await fetchWithJar(jar, action, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: body.toString(),
    });
    ev.login_status = loginRes.status;
    // Follow redirects manually to keep the jar.
    let cur = loginRes;
    for (let i = 0; i < 5; i++) {
      const loc = cur.headers.get("location");
      if (!loc || (cur.status !== 301 && cur.status !== 302 && cur.status !== 303 && cur.status !== 307 && cur.status !== 308)) break;
      const next = new URL(loc, "https://app.devin.ai").toString();
      cur = await fetchWithJar(jar, next);
    }
    const afterLogin = await cur.text();
    ev.after_login_bytes = afterLogin.length;
    const loggedIn = !/auth\/login|sign in/i.test(afterLogin.slice(0, 5000)) || jar.header().length > 0;
    ev.logged_in_guess = loggedIn;
    if (!loggedIn && !jar.header()) {
      ev.stage = "login_failed";
      return { ok: false, evidence: ev, error: "Devin login did not produce a session — check the saved login." };
    }

    // 3. Find billing/subscription management.
    ev.stage = "find_billing";
    const billingPaths = ["/settings/billing", "/settings/subscription", "/account/billing", "/settings", "/account"];
    let billingHtml = "";
    let billingUrl = "";
    for (const p of billingPaths) {
      const { res: r, text: t } = await fetchFollow(jar, "https://app.devin.ai" + p);
      if (r.ok && /cancel|subscription|billing|plan/i.test(t)) { billingHtml = t; billingUrl = p; break; }
    }
    // Also scan for a billing link on the main page.
    if (!billingHtml) {
      const { text: mainT } = await fetchFollow(jar, "https://app.devin.ai/");
      const linkM = mainT.match(/href=["']([^"']*(?:billing|subscription|settings)[^"']*)["']/i);
      if (linkM) {
        billingUrl = new URL(linkM[1], "https://app.devin.ai").toString();
        const { text } = await fetchFollow(jar, billingUrl);
        billingHtml = text;
      }
    }
    ev.billing_url = billingUrl || null;
    if (!billingHtml) {
      ev.stage = "billing_not_found";
      return { ok: false, evidence: ev, error: "Signed in, but could not locate Devin's billing page." };
    }

    // 4. Find and submit the cancel action.
    ev.stage = "cancel_attempt";
    // Look for cancel forms/links.
    const cancelForm = billingHtml.match(/<form[^>]*(?:action=["']([^"']*)["'])?[^>]*>(?:(?!<\/form>).)*cancell(?:ation|ing|ed)?(?:(?!<\/form>).)*<\/form>/is);
    const cancelLink = billingHtml.match(/href=["']([^"']*)["'][^>]*>[^<]*cancell/i);
    if (cancelForm) {
      let cAction = cancelForm[1] || billingUrl;
      if (cAction && !cAction.startsWith("http")) cAction = new URL(cAction, "https://app.devin.ai").toString();
      const cHidden: Record<string, string> = {};
      const cre = /<input[^>]*type=["']hidden["'][^>]*>/gi;
      let cm: RegExpExecArray | null;
      const formHtml = cancelForm[0];
      while ((cm = cre.exec(formHtml))) {
        const nm = cm[0].match(/name=["']([^"']+)["']/i);
        const vv = cm[0].match(/value=["']([^"']*)["']/i);
        if (nm) cHidden[nm[1]] = vv ? vv[1] : "";
      }
      const cRes = await fetchWithJar(jar, cAction, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams(cHidden).toString(),
      });
      const cText = await cRes.text();
      ev.cancel_status = cRes.status;
      const confirmed = /cancell?ed|cancellation (confirmed|scheduled)|subscription (will )?(end|cancel)|no longer be billed/i.test(cText);
      ev.cancel_confirmed_guess = confirmed;
      if (confirmed) {
        ev.stage = "done";
        ev.note = "Devin subscription cancellation submitted and confirmation detected.";
        return { ok: true, evidence: ev };
      }
      ev.stage = "cancel_unconfirmed";
      return { ok: false, evidence: ev, error: "Cancel submitted but no confirmation detected — check Devin dashboard before retrying." };
    }
    if (cancelLink) {
      ev.cancel_link = cancelLink[1];
      ev.stage = "cancel_link_found";
      return { ok: false, evidence: ev, error: "Found a cancel link but it needs an interactive step (confirmation dialog/JS). Needs a real browser. (needs_browser)" };
    }
    ev.stage = "cancel_not_found";
    return { ok: false, evidence: ev, error: "Signed in and found billing, but no cancel action detected on the page." };
  } catch (e) {
    ev.stage = "exception";
    return { ok: false, evidence: ev, error: String(e?.message || e) };
  }
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
