// Upmore agent-chat edge function.
// POST /functions/v1/agent-chat  { thread_id?, message }
// Auth: Supabase JWT in Authorization header.
// Flow: load profile + thread + relevant verified routes → Anthropic →
// grounding post-check → save + return reply.

import { serve } from "https://deno.land/std@0.208.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.39.0";
import {
  SYSTEM_PROMPT,
  renderRouteCards,
  checkGrounding,
  isDebunkReply,
  SAFE_FALLBACK,
  SCAM_FALLBACK,
  RouteCard,
} from "./_shared/agent.ts";

const ANTHROPIC_URL = "https://api.anthropic.com/v1/messages";
const MODEL = Deno.env.get("ANTHROPIC_MODEL") ?? "claude-haiku-4-5-20251001";
const MAX_TOKENS = 400; // tight budget: short, basic replies

const cors = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, content-type",
};

serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });
  try {
    // The gateway already verified the JWT signature (verify_jwt=true). Extract
    // the user token and pass it EXPLICITLY: auth.getUser() with no argument
    // reads the client session, which does not exist in an edge function, so it
    // would always return null and every signed-in user would get a 401.
    const authHeader = req.headers.get("Authorization") ?? "";
    const authM = authHeader.match(/^Bearer\s+(.+)$/i);
    if (!authM) return json({ error: "unauthorized" }, 401);
    const supabase = createClient(
      Deno.env.get("SUPABASE_URL")!,
      Deno.env.get("SUPABASE_ANON_KEY")!,
      { global: { headers: { Authorization: authHeader } } }
    );
    const { data: { user } } = await supabase.auth.getUser(authM[1]);
    if (!user) return json({ error: "unauthorized" }, 401);

    // Per-user rate limit: 60 agent replies per rolling hour. This guards the
    // Anthropic spend against abuse; it is generous for real chat use.
    const RATE_LIMIT = 60;
    const nowMs = Date.now();
    const { data: rl } = await supabase
      .from("agent_rate_limits")
      .select("window_start,count")
      .eq("user_id", user.id)
      .maybeSingle();
    if (!rl || nowMs - new Date(rl.window_start).getTime() > 3600_000) {
      await supabase
        .from("agent_rate_limits")
        .upsert({ user_id: user.id, window_start: new Date(nowMs).toISOString(), count: 1 });
    } else if (rl.count >= RATE_LIMIT) {
      return json(
        { error: "rate_limited", message: "Slow down a little — try again in a bit." },
        429
      );
    } else {
      await supabase
        .from("agent_rate_limits")
        .update({ count: rl.count + 1 })
        .eq("user_id", user.id);
    }

    const { thread_id, message } = await req.json();
    if (!message || typeof message !== "string") return json({ error: "message required" }, 400);

    // Thread (create if needed)
    let tid: string = thread_id;
    if (!tid) {
      const { data, error } = await supabase.from("agent_threads")
        .insert({ user_id: user.id, title: message.slice(0, 60) }).select("id").single();
      if (error) throw error;
      tid = data.id;
    }

    // Profile
    const { data: profile } = await supabase.from("profiles").select("*").eq("id", user.id).single();

    // Active playbook (if user is mid-walkthrough, that route is the context)
    const { data: playbook } = await supabase.from("playbook_progress")
      .select("*, routes!inner(*)").eq("user_id", user.id).eq("status", "active")
      .order("updated_at", { ascending: false }).limit(1).maybeSingle();

    // Candidate routes: active playbook route + verified Standard-lane routes
    // matching the user's state (simple keyword match v1; semantic search later)
    let routes: RouteCard[] = [];
    if (playbook?.routes) routes.push(playbook.routes as RouteCard);
    const state = (profile?.state ?? "").toLowerCase();
    const { data: verified } = await supabase.from("routes")
      .select("*").eq("status", "verified").eq("lane", "Standard").limit(12);
    for (const r of verified ?? []) {
      if (!routes.some((x) => x.route_id === r.route_id)) routes.push(r as RouteCard);
    }

    // Recent history
    const { data: history } = await supabase.from("agent_messages")
      .select("role, content").eq("thread_id", tid).order("id", { ascending: false }).limit(10);
    const hist = (history ?? []).reverse();

    const profileLine = profile
      ? `User profile: state=${profile.state ?? "unknown"}, free time=${profile.free_time_hours ?? "?"}h/wk, paycheck=${profile.paycheck_status ?? "?"}, cash available=$${profile.cash_available ?? "?"}.`
      : "User profile: unknown — ask one question at a time to learn state, free time, paycheck status, cash available.";
    const playbookLine = playbook
      ? `Active walkthrough: route ${playbook.route_id}, currently on step ${playbook.current_step + 1}.`
      : "No active walkthrough.";

    const system = SYSTEM_PROMPT + "\n\n" + profileLine + "\n" + playbookLine +
      `\nVerified LIVE route cards available to you right now: ${routes.length}. ` +
      (routes.length === 0
        ? "You have ZERO verified routes. Never claim you have verified routes to walk through. Say new routes are being verified and you'll have them soon."
        : "Only present routes marked LIVE below as offers.") +
      "\n\nROUTE CARDS (only source of truth):\n" + renderRouteCards(routes);

    const anthropicRes = await fetch(ANTHROPIC_URL, {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-api-key": Deno.env.get("ANTHROPIC_API_KEY")!,
        "anthropic-version": "2023-06-01",
      },
      body: JSON.stringify({
        model: MODEL,
        max_tokens: MAX_TOKENS,
        system,
        messages: [...hist.map((m: any) => ({ role: m.role, content: m.content })), { role: "user", content: message }],
      }),
    });
    if (!anthropicRes.ok) {
      const t = await anthropicRes.text();
      console.error("anthropic error", anthropicRes.status, t.slice(0, 300));
      return json({ error: "agent_unavailable" }, 502);
    }
    const aj = await anthropicRes.json();
    let reply: string = aj.content?.map((b: any) => b.text ?? "").join("") ?? "";

    // Grounding post-check: any violation → safe fallback
    const violations = checkGrounding(reply, routes, message);
    let action: any = null;
    const m = reply.match(/ACTION\s+(\{.*\})\s*$/);
    if (m) {
      try { action = JSON.parse(m[1]); } catch { /* ignore */ }
      reply = reply.replace(/ACTION\s+\{.*\}\s*$/, "").trim();
    }
    if (violations.length) {
      console.warn("grounding violations", violations);
      // A blocked debunk still warns: the user asked about a scam, and a
      // generic deflection would leave them unprotected. The scam fallback
      // names the pattern without inventing any amounts or URLs.
      reply = isDebunkReply(reply) ? SCAM_FALLBACK : SAFE_FALLBACK;
      action = null;
    }

    // Persist
    await supabase.from("agent_messages").insert([
      { thread_id: tid, role: "user", content: message },
      { thread_id: tid, role: "assistant", content: reply, meta: { action, violations } },
    ]);
    // Apply walkthrough actions to playbook_progress
    if (action?.type === "start_walkthrough" && action.route_id) {
      await supabase.from("playbook_progress").upsert({
        user_id: user.id, route_id: action.route_id, current_step: 0,
        status: "active", updated_at: new Date().toISOString(),
      }, { onConflict: "user_id,route_id" });
    }

    return json({ thread_id: tid, reply, action });
  } catch (e) {
    console.error(e);
    return json({ error: "internal" }, 500);
  }
});

function json(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), { status, headers: { ...cors, "content-type": "application/json" } });
}
