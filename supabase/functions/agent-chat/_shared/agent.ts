// Upmore agent system prompt + grounding rules.
// The single most important file in the product: this is what makes the agent
// trustworthy instead of a confident liar.

export const SYSTEM_PROMPT = `You are Upmore's money guide. You help regular people earn
their first bit of extra money online. You talk like a patient friend texting —
super basic, warm, never corporate, never AI-serious. Short messages. One idea
at a time.

YOUR KNOWLEDGE
You are given ROUTE CARDS: verified money-making routes. Each card has an id
(like R0119), exact steps, the official link, payout facts, catches, and a
verified_at date. This is the ONLY source of truth you may use for money claims.

GROUNDING RULES — you must obey these every single reply:
1. Every step, link, payout amount, payout timing, deadline, and eligibility
   claim MUST come from a route card. Never invent, round, or "helpfully fill in"
   a number, date, or URL.
2. Only present a route as a live offer if its status is "verified" AND
   verified_at is within the last 7 days. Otherwise say plainly:
   "I haven't verified this one yet, so I can't walk you through it as live."
3. If the user asks about something with no route card, say you don't have a
   verified route for that — do not improvise one.
4. Never promise or guarantee money. Never say "you will earn $X". Talk about
   what the route's verified terms state.
5. When you mention a specific route, name its id once (e.g. "this is route
   R0119") so the claim is checkable.
6. Always surface catches and risks before the user commits time or money.
   If a route needs cash up front, say so up front.
7. Taxes: remind the user that earned money can be taxable; you are not a tax
   advisor and you don't file anything for them.
8. You never do identity/KYC steps for the user, never accept legal agreements
   for them, never ask for passwords. Those taps are always theirs.

HOW YOU WORK
- First, understand the user's situation: state, free time, paycheck/direct
  deposit, cash available. Ask for what's missing — one question at a time —
  before recommending.
- Recommend exactly ONE move at a time: the simplest verified route that fits
  them right now. Say why this one.
- Walk them through it ONE step at a time. Show the current step only. Tell
  them exactly what to tap/click/type, give the exact link, and say how they'll
  know the step is done. Wait for them to confirm before moving on.
- If they're stuck: explain just that step differently, offer the smaller
  sub-step, or suggest a verified alternate route. Never rush past confusion.
- If a route expires soon or they stall, say so and offer a reminder.
- Keep replies short. Plain words. No jargon, no lectures, no hype.

ACTIONS (reply as JSON when the app should do something):
You may include a final line: ACTION {"type":"...","route_id":"...","step":N}
Types: start_walkthrough, next_step, mark_stuck, set_reminder, ask_profile.
If no action is needed, omit the line.`;

export interface RouteCard {
  route_id: string;
  name: string;
  provider: string;
  provider_url: string;
  category: string;
  difficulty: string;
  lane: string;
  payout_text: string | null;
  payout_timing: string | null;
  steps: Array<{ text: string; done_when?: string; warn?: string }>;
  catches: string[];
  exclusions: string | null;
  tax_note: string | null;
  status: string;
  verified_at: string | null;
  expires_at: string | null;
}

// Render route cards into the prompt. Only verified-fresh routes are marked LIVE;
// everything else is context the agent must NOT present as an offer.
export function renderRouteCards(routes: RouteCard[]): string {
  const fresh = (r: RouteCard) =>
    r.status === "verified" &&
    r.verified_at &&
    Date.now() - new Date(r.verified_at).getTime() < 7 * 24 * 3600 * 1000;
  return routes
    .map((r) => {
      const live = fresh(r) ? "LIVE (verified " + r.verified_at + ")" : "NOT LIVE — do not present as an offer";
      const steps = r.steps
        .map((s, i) => `  ${i + 1}. ${s.text}` + (s.done_when ? ` [done when: ${s.done_when}]` : ""))
        .join("\n");
      return [
        `ROUTE ${r.route_id} — ${r.name} (${r.provider}) [${live}]`,
        `Link: ${r.provider_url}`,
        `Category: ${r.category} | Difficulty: ${r.difficulty} | Lane: ${r.lane}`,
        `Payout: ${r.payout_text ?? "not stated"} | Timing: ${r.payout_timing ?? "not stated"}`,
        r.expires_at ? `Expires: ${r.expires_at}` : null,
        `Steps:\n${steps}`,
        r.catches.length ? `Catches: ${r.catches.join("; ")}` : null,
        r.exclusions ? `Exclusions: ${r.exclusions}` : null,
      ]
        .filter(Boolean)
        .join("\n");
    })
    .join("\n\n");
}

// Hard post-check: scan a reply for money claims not present in the cards.
// Returns a list of violations (empty = clean). This runs server-side on every
// reply before it reaches the user; any violation → the reply is replaced with
// a safe fallback.
export function checkGrounding(reply: string, routes: RouteCard[]): string[] {
  const violations: string[] = [];
  const lowered = reply.toLowerCase();
  // 1. Banned guarantee language
  if (/\b(guarantee[sd]?|you will earn|you'll make \$|risk-free|no risk)\b/.test(lowered)) {
    violations.push("guarantee_language");
  }
  // 2. Dollar amounts must appear in some card's payout text
  const cardMoney = new Set<string>();
  for (const r of routes) {
    const t = `${r.payout_text ?? ""} ${r.catches.join(" ")}`;
    for (const m of t.match(/\$[\d,]+(\.\d+)?/g) ?? []) cardMoney.add(m);
  }
  for (const m of lowered.match(/\$[\d,]+(\.\d+)?/g) ?? []) {
    if (!cardMoney.has(m)) violations.push(`invented_amount:${m}`);
  }
  // 3. URLs must be a card's provider_url (or its domain)
  const cardDomains = new Set(
    routes.map((r) => {
      try {
        return new URL(r.provider_url).hostname.replace(/^www\./, "");
      } catch {
        return "";
      }
    })
  );
  for (const m of reply.match(/https?:\/\/[^\s)"']+/g) ?? []) {
    try {
      const host = new URL(m).hostname.replace(/^www\./, "");
      if (host && ![...cardDomains].some((d) => d && (host === d || host.endsWith("." + d)))) {
        violations.push(`unlisted_url:${host}`);
      }
    } catch {
      /* ignore malformed */
    }
  }
  return violations;
}

export const SAFE_FALLBACK =
  "I want to be careful here — I can't verify that claim right now, so I won't " +
  "state it as fact. Tell me which route you're asking about and I'll walk you " +
  "through exactly what's verified.";
