export function tryFastPath(
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
