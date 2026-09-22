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
import { tryCapabilities } from "./_shared/capabilities.ts";

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

    // Parallel fetches: profile, playbook, reminders, verified routes, history,
    // expiring. Sequential awaits were ~2s; parallel cuts p50 substantially.
    const nowIso = new Date().toISOString();
    const soonIso = new Date(Date.now() + 14 * 86400000).toISOString();
    const [profRes, playRes, remRes, verRes, histRes, expRes] = await Promise.all([
      supabase.from("profiles").select("*").eq("id", user.id).single(),
      supabase.from("playbook_progress")
        .select("*, routes!inner(*)").eq("user_id", user.id).eq("status", "active")
        .order("updated_at", { ascending: false }).limit(1).maybeSingle(),
      // Due reminders: due_at passed and not yet sent.
      supabase.from("reminders")
        .select("route_id, kind, message, due_at").eq("user_id", user.id)
        .is("sent_at", null).lte("due_at", nowIso)
        .order("due_at", { ascending: true }).limit(3),
      supabase.from("routes")
        .select("*").eq("status", "verified").limit(50),
      supabase.from("agent_messages")
        .select("role, content").eq("thread_id", tid).order("id", { ascending: false }).limit(10),
      supabase.from("routes")
        .select("route_id, name, expires_at").eq("status", "verified")
        .not("expires_at", "is", null).lte("expires_at", soonIso).limit(5),
    ]);
    const profile = profRes.data;
    const playbook = playRes.data;
    const reminders = remRes.data;

    // Candidate routes: active playbook route + verified routes
    // matching the user's state (simple keyword match v1; semantic search later).
    // Capabilities (make-me-$X, walkthroughs) see every verified route;
    // the fast path and the model only see Standard-lane ones.
    let routes: RouteCard[] = [];
    if (playbook?.routes) routes.push(playbook.routes as RouteCard);
    const state = (profile?.state ?? "").toLowerCase();
    const verified = verRes.data;
    for (const r of verified ?? []) {
      if (!routes.some((x) => x.route_id === r.route_id)) routes.push(r as RouteCard);
    }
    const standardRoutes = routes.filter((r) => (r.lane ?? "Standard") === "Standard");

    // Recent history
    const hist = ((histRes.data ?? []).reverse());

    // FAST-PATH: deterministic answers for factual questions about verified
    // routes. Skips the Anthropic call entirely (<500ms vs ~9s). Only triggers
    // for safe factual patterns; everything else goes to the model.
    // CAPABILITY PATHS: deterministic answers that never touch the model —
    // "make me $X" (honest time-to-cash math + full steps + exact links),
    // quantitative stock screen (live market data, transparent factor model),
    // prediction-market/gambling guard (critical-thinking takedown).
    // Deterministic output needs no grounding post-check; persist like fast path.
    const cap = await tryCapabilities(message, routes);
    if (cap) {
      await supabase.from("agent_messages").insert([
        { thread_id: tid, role: "user", content: message },
        { thread_id: tid, role: "assistant", content: cap.reply, meta: { capability: true } },
      ]);
      // Deterministic walkthroughs create playbook progress just like the
      // model's start_walkthrough action does, so the app's Home tab tracks it.
      if (cap.routeId && routes.some((r) => r.route_id === cap.routeId)) {
        await supabase.from("playbook_progress").upsert({
          user_id: user.id, route_id: cap.routeId, current_step: 0,
          status: "active", updated_at: new Date().toISOString(),
        }, { onConflict: "user_id,route_id" });
      }
      return json({ thread_id: tid, reply: cap.reply, action: null });
    }

    const fastReply = tryFastPath(message, standardRoutes, playbook?.routes as RouteCard | undefined);
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
    // Expiry alerts: verified routes expiring within 14 days (fetched above).
    const expiring = expRes.data;
    const expiryLine = (expiring?.length ?? 0) > 0
      ? `EXPIRING SOON (warn the user before recommending): ` +
        expiring!.map((r: any) => `${r.name ?? r.route_id} expires ${r.expires_at}`).join("; ") + "."
      : "No verified routes expiring within 14 days.";

    const system = SYSTEM_PROMPT + "\n\n" + profileLine + "\n" + playbookLine + "\n" + resumeLine + "\n" + reminderLine + "\n" + expiryLine +
      `\nVerified LIVE route cards available to you right now: ${standardRoutes.length}. ` +
      (standardRoutes.length === 0
        ? "You have ZERO verified routes. Never claim you have verified routes to walk through. Say new routes are being verified and you'll have them soon."
        : "Only present routes marked LIVE below as offers.") +
      "\n\nROUTE CARDS (only source of truth):\n" + renderRouteCards(standardRoutes);

    const systemStatic = SYSTEM_PROMPT; // stable: cacheable
    const systemDynamic = "\n\n" + profileLine + "\n" + playbookLine + "\n" + resumeLine + "\n" + reminderLine + "\n" + expiryLine +
      `\nVerified LIVE route cards available to you right now: ${standardRoutes.length}. ` +
      (standardRoutes.length === 0
        ? "You have ZERO verified routes. Never claim you have verified routes to walk through. Say new routes are being verified and you'll have them soon."
        : "Only present routes marked LIVE below as offers.") +
      "\n\nROUTE CARDS (only source of truth):\n" + renderRouteCards(standardRoutes);

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

    // Deterministic walkthrough start: if the user asks to be walked through a
    // verified route step-by-step and has no active playbook for it, create it
    // here (current_step=0). The model sometimes skips its start_walkthrough
    // action; this makes persistence reliable, not model-dependent.
    const walkStart = /\b(walk me through|step by step|get (me )?started with|start.*walkthrough)\b/i.test(message);
    if (walkStart && !playbook) {
      const target = routes.find((r) =>
        message.toLowerCase().includes(r.provider.toLowerCase()) ||
        message.toLowerCase().includes(r.name.toLowerCase()));
      if (target) {
        await supabase.from("playbook_progress").upsert({
          user_id: user.id, route_id: target.route_id, current_step: 0,
          status: "active", updated_at: new Date().toISOString(),
        }, { onConflict: "user_id,route_id" });
      }
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

    // Deterministic scam guard: if the message matches known scam patterns and
    // the model reply lacks any debunk/warning language, prepend a clear
    // warning. Scam defense must be reliable, not model-nondeterministic.
    const SCAM_PATTERNS: Array<[RegExp, string]> = [
      [/recruit.*(friend|people).*pay|pay.*recruit|pyramid/i,
       "That recruit-people-who-pay structure is a pyramid scheme — illegal and it collapses, with the people at the bottom losing money."],
      [/gift\s?card/i,
       "Anyone asking for payment in gift cards is running a scam — legitimate work never asks for gift cards."],
      [/guaranteed.*(income|money|\$)|risk-free/i,
       "There's no such thing as guaranteed or risk-free income — that's the language scams use."],
      [/wire.*back|deposit.*check.*wire|double.*crypto|send.*btc/i,
       "That's a classic scam pattern — don't send money or share bank/crypto details."],
      [/bank\s?log\s?in|bank\s?(password|credential)|share.*(bank|account).*(login|password|credential)|dm me your/i,
       "Never share your bank login or account credentials with anyone — that's a phishing scam, and it's how accounts get drained. No legitimate offer needs your bank login."],
      [/pay.*\$.*(unlock|secret list|fee.*start)|background.check.*fee/i,
       "Legitimate earning routes never charge you upfront to start — upfront fees are a scam red flag."],
    ];
    {
      const rl = finalReply.toLowerCase();
      const hasDebunk = /scam|red flag|pyramid|ponzi|fraud|phishing|too good|stay away|warning|don't (do|send|pay)|never/i.test(rl);
      if (!hasDebunk) {
        for (const [pat, warning] of SCAM_PATTERNS) {
          if (pat.test(message)) {
            finalReply = `⚠️ ${warning}\n\n` + finalReply;
            break;
          }
        }
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
    // Verification questions about a specific (possibly unknown) provider are
    // NOT discovery — they need the model's honesty judgment, not a list.
    if (/\b(is|are|was)\b[^?.]{0,60}\bverif/i.test(msg) || /\bverif[^?.]{0,40}\b(is|are)\b/i.test(msg)) {
      return null;
    }
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
  // Comprehensive brief: the question asks about 2+ aspects (payout + rules +
  // eligibility). Compose a full deterministic brief from the card — faster
  // and more complete than the model, and every fact is card-grounded.
  const aspects = [
    /\b(payout|paid|pay out|cash out|redeem|minimum|timing|fees?)\b/i,
    /\b(requirement|eligible|qualify|who can join|age|where.*available)\b/i,
    /\b(receipt|rules?|terms|catch|convert|points)\b/i,
  ];
  const aspectHits = aspects.filter((a) => a.test(msg)).length;
  if (aspectHits >= 2) {
    const lines: string[] = [`**${route.provider}** (${route.name}) — verified ✓ (route ${route.route_id})`, ""];
    lines.push(`**Payout:** ${route.payout_text ?? "see official terms"}${route.payout_timing ? ` — ${route.payout_timing}` : ""}`);
    const who: string[] = [];
    if (route.min_age != null) who.push(`age ${route.min_age}+`);
    if (route.geo_notes) who.push(route.geo_notes);
    if (who.length) lines.push(`**Who can join:** ${who.join(", ")}`);
    if (catches.length) lines.push(`**Key rules:** ${catches.join("; ")}`);
    if (route.exclusions) lines.push(`**Exclusions:** ${route.exclusions}`);
    if (route.provider_url) lines.push(`**Official link:** ${route.provider_url}`);
    lines.push("", "Want me to walk you through it step by step?");
    return lines.join("\n");
  }
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
  // "how do I get paid" / "payout" / "cash out" / "how much per receipt"
  if (/\b(payout|paid|pay out|cash out|redeem|withdraw|\bpay\b.*receipt|per receipt)\b/i.test(msg)) {
    return `${route.name} payout (route ${route.route_id}):\n` +
      `• ${route.payout_text ?? "See the official terms for payout details."}\n` +
      `• Timing: ${route.payout_timing ?? "varies"}\n` +
      `• Honest read: actual pay per receipt varies and depends on the receipt and retailer — ` +
      `treat any figure as roughly that, not a guaranteed amount.`;
  }
  // "is X available in [country]" / "does X work in [place]"
  if (/\b(available in|work in|offered in|support.*in)\b/i.test(msg)) {
    return `${route.name} availability (route ${route.route_id}): ${route.geo_notes ?? "see official terms"}.`;
  }
  // General eligibility: "I'm 25, can I use X?" / "Can I use X in Texas?"
  // Combines age + geo from the card. Deterministic and fast.
  if (/\b(can i (use|join)|am i eligible|do i qualify)\b/i.test(msg)) {
    const parts: string[] = [];
    if (route.min_age != null) parts.push(`Age ${route.min_age}+`);
    if (route.geo_notes) parts.push(route.geo_notes);
    if (route.exclusions) parts.push(`Exclusions: ${route.exclusions}`);
    if (!parts.length) return null;
    // If the user stated their age, give a direct yes/no.
    const ageMatch = msg.match(/\b(i'm|i am|age)\s*(\d{1,3})\b/i) || msg.match(/\b(\d{1,3})\s*(-|\s)?years?\s*(-|\s)?old\b/i);
    let verdict = `Here's who can use ${route.name} (route ${route.route_id}):`;
    if (ageMatch && route.min_age != null) {
      const age = parseInt(ageMatch[2] ?? ageMatch[1], 10);
      if (!isNaN(age)) {
        verdict = age >= route.min_age
          ? `Yes, you're good to go — at ${age} you meet the age requirement for ${route.name} (route ${route.route_id}):`
          : `Not yet — ${route.name} needs age ${route.min_age}+ (route ${route.route_id}), so at ${age} you can't join solo:`;
      }
    } else {
      verdict = `Here's who can use ${route.name} (route ${route.route_id}):`;
    }
    const payoutLine = [route.payout_text, route.payout_timing].filter(Boolean).join(" — ");
    return verdict + "\n" +
      parts.map((p) => `• ${p}`).join("\n") +
      (payoutLine ? `\n• Payout: ${payoutLine}` : "");
  }
  // Rules/catches: "what happens if I stop using" / "how long do I have" / "fees" / "what's the catch"
  if (/\b(expire|inactive|stop using|how long.*(upload|submit)|fee|charge|catch|downside|fine print)\b/i.test(msg) && catches.length) {
    return `${route.name} rules to know (route ${route.route_id}):\n` +
      catches.map((c) => `• ${c}`).join("\n");
  }
  if (/\b(\d+\s*(-|\s)?year\s*(-|\s)?old|how old|age (limit|requirement))\b/i.test(msg)) {
    const parts: string[] = [];
    if (route.min_age != null) parts.push(`Minimum age: ${route.min_age}`);
    if (route.geo_notes && /under 18|parent|guardian/i.test(route.geo_notes))
      parts.push(`Under 18 needs a parent/guardian (${route.geo_notes})`);
    else if (route.geo_notes) parts.push(route.geo_notes);
    if (!parts.length) return null;
    return `${route.name} age rules (route ${route.route_id}):\n` +
      parts.map((p) => `• ${p}`).join("\n");
  }
  // "link" / "where do I sign up" / "download"
  if (/\b(link|sign up|signup|download|where.*(start|app|site))\b/i.test(msg)) {
    const steps = route.steps.slice(0, 4).map((s, i) => `${i + 1}. ${s.text}`).join("\n");
    const stepsBlock = steps
      ? `\n\nExact steps to start earning:\n${steps}\n\nCheck the official site if anything looks different — steps change over time.`
      : `\n\nStart at Step 1: ${route.steps[0]?.text ?? "follow the on-screen steps"}.`;
    return `Here's the official site for ${route.name} (route ${route.route_id}):\n${route.provider_url}${stepsBlock}`;
  }
  return null;
}
