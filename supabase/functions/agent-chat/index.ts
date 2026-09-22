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

    // Due reminders: surface them so the agent can proactively nudge.
    // Schema: id, user_id, route_id, kind, message, due_at, sent_at, channel.
    // A reminder is "due" when due_at has passed and it hasn't been sent yet.
    const { data: reminders } = await supabase.from("reminders")
      .select("route_id, kind, message, due_at").eq("user_id", user.id)
      .is("sent_at", null)
      .lte("due_at", new Date().toISOString())
      .order("due_at", { ascending: true }).limit(3);

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

    // FAST-PATH: deterministic answers for factual questions about verified
    // routes. Skips the Anthropic call entirely (<500ms vs ~9s). Only triggers
    // for safe factual patterns; everything else goes to the model.
    const fastReply = tryFastPath(message, routes, playbook?.routes as RouteCard | undefined);
    if (fastReply) {
      await supabase.from("agent_messages").insert([
        { thread_id: tid, role: "user", content: message },
        { thread_id: tid, role: "assistant", content: fastReply, meta: { fast_path: true } },
      ]);
      return json({ thread_id: tid, reply: fastReply, action: null });
    }

    const profileLine = profile
      ? `User profile: state=${profile.state ?? "unknown"}, age=${profile.age ?? "unknown"}, free time=${profile.free_time_hours ?? "?"}h/wk, paycheck=${profile.paycheck_status ?? "?"}, cash available=$${profile.cash_available ?? "?"}.`
      : "User profile: unknown — learn it from what the user tells you and save facts with the ask_profile action; never ask for the same fact twice.";
    const playbookLine = playbook
      ? `Active walkthrough: route ${playbook.route_id}, currently on step ${playbook.current_step + 1}.`
      : "No active walkthrough.";
    // Resume nudge: user started a walkthrough but went quiet > 24h.
    let resumeLine = "";
    if (playbook?.updated_at) {
      const idleHrs = (Date.now() - new Date(playbook.updated_at).getTime()) / 3600000;
      if (idleHrs > 24) {
        resumeLine = `PROACTIVE NUDGE: the user started the ${playbook.route_id} walkthrough but hasn't touched it in ${Math.round(idleHrs)} hours. Open with a warm resume offer ("want to pick up where you left off on step ${playbook.current_step + 1}?"), don't just answer and move on.`;
      }
    }
    const reminderLine = (reminders?.length ?? 0) > 0
      ? `Due reminders (be proactive — mention these naturally): ` +
        reminders!.map((r: any) => `${r.message ?? r.route_id} (due ${r.due_at})`).join("; ") + "."
      : "No due reminders.";
    // Expiry alerts: verified routes expiring within 14 days.
    const soon = new Date(Date.now() + 14 * 86400000).toISOString();
    const { data: expiring } = await supabase.from("routes")
      .select("route_id, name, expires_at").eq("status", "verified")
      .not("expires_at", "is", null).lte("expires_at", soon).limit(5);
    const expiryLine = (expiring?.length ?? 0) > 0
      ? `EXPIRING SOON (warn the user before recommending): ` +
        expiring!.map((r: any) => `${r.name ?? r.route_id} expires ${r.expires_at}`).join("; ") + "."
      : "No verified routes expiring within 14 days.";

    const system = SYSTEM_PROMPT + "\n\n" + profileLine + "\n" + playbookLine + "\n" + resumeLine + "\n" + reminderLine + "\n" + expiryLine +
      `\nVerified LIVE route cards available to you right now: ${routes.length}. ` +
      (routes.length === 0
        ? "You have ZERO verified routes. Never claim you have verified routes to walk through. Say new routes are being verified and you'll have them soon."
        : "Only present routes marked LIVE below as offers.") +
      "\n\nROUTE CARDS (only source of truth):\n" + renderRouteCards(routes);

    const systemStatic = SYSTEM_PROMPT; // stable: cacheable
    const systemDynamic = "\n\n" + profileLine + "\n" + playbookLine + "\n" + resumeLine + "\n" + reminderLine + "\n" + expiryLine +
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
        system: [
          { type: "text", text: systemStatic, cache_control: { type: "ephemeral" } },
          { type: "text", text: systemDynamic },
        ],
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

    // Grounding post-check: any violation → safe fallback.
    // Parse the ACTION line FIRST and strip it, so the check only sees the
    // user-facing text (an action's JSON must never trip grounding).
    let action: any = null;
    const m = reply.match(/ACTION\s+(\{.*\})\s*$/);
    if (m) {
      try { action = JSON.parse(m[1]); } catch { /* ignore */ }
      reply = reply.replace(/ACTION\s+\{.*\}\s*$/, "").trim();
    }
    const violations = checkGrounding(reply, routes, message);
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
    if (action?.type === "next_step" && action.route_id) {
      const step = typeof action.step === "number" ? action.step : null;
      if (step !== null) {
        await supabase.from("playbook_progress").upsert({
          user_id: user.id, route_id: action.route_id, current_step: step,
          status: "active", updated_at: new Date().toISOString(),
        }, { onConflict: "user_id,route_id" });
      }
    }
    // ask_profile: the model learned a fact about the user (state, age, ...).
    // Persist it so it is never asked for again, across turns and sessions.
    if (action?.type === "ask_profile" && action.fields && typeof action.fields === "object") {
      const allowed = ["state", "age", "free_time_hours", "paycheck_status", "cash_available", "display_name"];
      const patch: Record<string, unknown> = {};
      for (const k of allowed) {
        const v = (action.fields as Record<string, unknown>)[k];
        if (v !== undefined && v !== null && v !== "") patch[k] = v;
      }
      if (Object.keys(patch).length) {
        patch.updated_at = new Date().toISOString();
        await supabase.from("profiles").update(patch).eq("id", user.id);
      }
    }

    // Deterministic proactivity guard: if there are due reminders and the
    // model didn't mention them, prepend a natural heads-up. The model
    // sometimes drops reminders on greetings; this makes it reliable.
    let finalReply = reply;
    if (reminders?.length) {
      const rl = reply.toLowerCase();
      const missed = (reminders as any[]).filter((r) => {
        const msg = String(r.message ?? r.route_id ?? "").toLowerCase();
        const keywords = msg.split(/\W+/).filter((w) => w.length > 4).slice(0, 4);
        return keywords.length > 0 && !keywords.some((k) => rl.includes(k));
      });
      if (missed.length) {
        const headsUp = missed
          .map((r) => `Quick heads-up: ${r.message ?? r.route_id}.`)
          .join(" ");
        finalReply = headsUp + "\n\n" + reply;
      }
    }

    return json({ thread_id: tid, reply: finalReply, action });
  } catch (e) {
    console.error(e);
    return json({ error: "internal" }, 500);
  }
});

function json(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), { status, headers: { ...cors, "content-type": "application/json" } });
}

// Deterministic fast-path: answer factual questions about verified routes
// directly from the card, no LLM call. Returns null if the question isn't
// a safe factual pattern (falls through to the model).
function tryFastPath(
  message: string,
  routes: RouteCard[],
  playbookRoute?: RouteCard
): string | null {
  const msg = message.toLowerCase().trim();
  // Never fast-path: guarantees, scams, advice, comparisons, unknowns.
  // These need the model's judgment (honesty dimension).
  if (/\b(guarantee|scam|legit|safe|worth it|should i|best|vs|versus|compare|how much.*(earn|make)|income|tax)\b/i.test(msg)) {
    return null;
  }
  // Discovery: "what offers do you have" / "what should I try" with no named
  // provider -> deterministic list of verified routes. Reliable (no model
  // nondeterminism), fast, and honest (only verified routes, marked as such).
  if (/\b(what.*(offers?|have|available)|show me|list.*offers?|what should i (try|do)|recommend|which.*(offers?|apps?))\b/i.test(msg)) {
    const namesProvider = routes.some((r) =>
      msg.includes(r.provider.toLowerCase()) || msg.includes(r.name.toLowerCase()));
    if (namesProvider) return null; // let the specific-route path answer
    const live = routes.filter((r) => r.status === "verified");
    if (live.length > 0) {
      const lines = live.slice(0, 6).map(
        (r) => `• ${r.provider} (${r.name}) — verified ✓ — ${r.payout_text ?? "see terms"}`
      );
      return `Here are the offers I've personally verified and have live right now:\n\n` +
        lines.join("\n") +
        `\n\nWant me to walk you through any of these step by step? Just name one.`;
    }
    return null;
  }
  // Find which verified route the question is about.
  // Priority: explicit provider/name in the message beats the active playbook.
  // (A user mid-Fetch-walkthrough asking about Rakuten must get Rakuten.)
  const named = routes.find((r) =>
    msg.includes(r.provider.toLowerCase()) || msg.includes(r.name.toLowerCase())
  );
  const route = named ?? playbookRoute;
  if (!route) return null;
  const fresh =
    route.status === "verified" && route.verified_at &&
    Date.now() - new Date(route.verified_at).getTime() < 7 * 24 * 3600 * 1000;
  if (!fresh) return null;

  const catches = Array.isArray(route.catches) ? route.catches : route.catches ? [String(route.catches)] : [];
  // "how does X work" / "what is X" / "tell me about X"
  if (/\b(how does|what is|tell me about|explain)\b/i.test(msg)) {
    const steps = route.steps.slice(0, 3).map((s, i) => `${i + 1}. ${s.text}`).join("\n");
    return `${route.name} (${route.provider}) — route ${route.route_id}.\n\n` +
      `Here's how it works:\n${steps}\n\n` +
      `Payout: ${route.payout_text ?? "see terms"} (${route.payout_timing ?? "timing varies"}).\n` +
      (catches.length ? `\nHeads up: ${catches[0]}` : "") +
      `\n\nWant me to walk you through it step by step?`;
  }
  // "requirements" / "do I need" / "eligible"
  if (/\b(requirement|eligible|do i need|what do i need|qualify)\b/i.test(msg)) {
    const parts: string[] = [];
    if (route.min_age != null) parts.push(`Age ${route.min_age}+`);
    if (route.geo_notes) parts.push(route.geo_notes);
    if (route.exclusions) parts.push(`Exclusions: ${route.exclusions}`);
    if (!parts.length) return null;
    return `${route.name} requirements (route ${route.route_id}):\n` +
      parts.map((p) => `• ${p}`).join("\n");
  }
  // "how do I get paid" / "payout" / "cash out"
  if (/\b(payout|paid|pay out|cash out|redeem|withdraw)\b/i.test(msg)) {
    return `${route.name} payout (route ${route.route_id}):\n` +
      `• ${route.payout_text ?? "See the official terms for payout details."}\n` +
      `• Timing: ${route.payout_timing ?? "varies"}`;
  }
  // "link" / "where do I sign up" / "download"
  if (/\b(link|sign up|signup|download|where.*(start|app|site))\b/i.test(msg)) {
    return `Here's the official ${route.name} link (route ${route.route_id}):\n${route.provider_url}\n\n` +
      `Start at Step 1: ${route.steps[0]?.text ?? "follow the on-screen steps"}.`;
  }
  return null;
}
