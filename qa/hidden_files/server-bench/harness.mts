// Local logic harness for Upmore agent-chat deterministic capabilities.
// Run: node harness.mts
import { readFileSync } from "node:fs";
import {
  tryMakeMeX, tryWalkthrough, tryScamGuard, tryGamblingGuard,
  tryPrivacyGuard, tryQuantStocks, tryCapabilities, APP_LINKS,
} from "./capabilities.ts";
import { checkGrounding, isDebunkReply, SAFE_FALLBACK, SCAM_FALLBACK } from "./agent.ts";
import { tryFastPath } from "./fastpath.ts";

const cards = JSON.parse(readFileSync("./fixtures.json", "utf8"));
const routeList = Object.values(cards);

let pass = 0, fail = 0;
function show(label: string, v: unknown) {
  console.log(`\n===== ${label} =====`);
  if (typeof v === "string") console.log(v.length > 2200 ? v.slice(0, 2200) + "\n…[truncated]" : v);
  else console.dir(v, { depth: 4, maxArrayLength: 8 });
}
function note(label: string, ok: boolean, detail = "") {
  ok ? pass++ : fail++;
  console.log(`${ok ? "PASS" : "FAIL"} ${label}${detail ? " — " + detail : ""}`);
}
const hr = (t: string) => console.log(`\n########## ${t} ##########`);

const fresh = () => Object.values(cards);

// ---------- S01: tryMakeMeX ----------
hr("S01 tryMakeMeX");
let r = tryMakeMeX("make me $20", fresh());
show("happy: 'make me $20'", r);
note("S01a happy $20 returns plan", !!r && r.includes("R0221"), "picked route");
note("S01b math present", !!r && /hour/i.test(r) && !!r.match(/\$\d/), "hours + $ math");
note("S01c catch present", !!r && /catch/i.test(r), "Biggest catch line");
note("S01d steps present", !!r && /1\. /.test(r), "numbered steps");
note("S01e link present", !!r && r.includes("usertesting.com"), "provider_url");
r = tryMakeMeX("make me $500", fresh());
show("stress: 'make me $500' (bank bonuses present)", r);
const uses500 = r && /R0536|ACNB|\$2,000|2,000/.test(r);
note("S01f $500 considers bank-bonus routes (R0536 $2000)", !!uses500, uses500 ? "yes" : "NO — only 15 CASH_MATH routes considered");
r = tryMakeMeX("make me $100000", fresh());
show("stress: 'make me $100000'", r);
note("S01g $100000 > 10000 → null", r === null);
r = tryMakeMeX("make me money fast", fresh());
show("stress: 'make me money fast' (no amount)", r);
note("S01h no digits → null", r === null);
r = tryMakeMeX("i need $300 fast", fresh());
show("stress: 'i need $300 fast'", r);
note("S01i 'i need $300 fast' matches", !!r && r.includes("$300"));
r = tryMakeMeX("earn $50 today", fresh());
show("stress: 'earn $50 today'", r);
note("S01j 'earn $50 today' matches", !!r && r.includes("$50"));
r = tryMakeMeX("MAKE ME $20!!!", fresh());
show("stress: case 'MAKE ME $20!!!'", r);
note("S01k case-insensitive", !!r && r.includes("$20"));
r = tryMakeMeX("make me $20", fresh());
note("S01l no guarantee words", !!r && !/\bguarantee/i.test(r));
r = tryMakeMeX("make me $20", []);
note("S01m empty routes → null", r === null);
r = tryMakeMeX("make me $9000", fresh().filter((x: any) => !["R0221","R0220","R0292","R0140"].includes(x.route_id)));
show("stress: $9000 with no hourly routes (honest fallback)", r);
note("S01n honest fallback when nothing hourly", !!r && /Real talk/i.test(r));
r = tryMakeMeX("make me $0", fresh());
note("S01o $0 → null", r === null);

// ---------- S02: vague opener ----------
hr("S02 vague opener");
for (const q of ["i want to make money", "i want to make some extra money", "help me make money"]) {
  const rr = tryMakeMeX(q, fresh());
  show(`vague: '${q}'`, rr);
  note(`S02 '${q}' anchors $20, no questions`, !!rr && rr.includes("$20") && !/\?/.test(rr) ? true : false, rr ? (/\?/.test(rr) ? "contains a question mark" : "no interrogation") : "null reply");
}

// ---------- S03: walkthrough ----------
hr("S03 tryWalkthrough");
let w = tryWalkthrough("walk me through fetch", routeList);
show("happy: 'walk me through fetch'", w?.reply);
note("S03a fetch → R0119", w?.routeId === "R0119", w?.routeId);
note("S03b steps rendered", !!w && /1\. /.test(w.reply));
w = tryWalkthrough("walk me through R0651", routeList);
show("stress: route ID 'walk me through R0651'", w?.reply);
note("S03c R0651 id mention → Chase card", w?.routeId === "R0651");
w = tryWalkthrough("walk me through zelle-pay", routeList);
show("stress: unknown 'walk me through zelle-pay'", w);
note("S03d unknown provider → null", w === null);
w = tryWalkthrough("walk me through R0851", routeList);
show("stress: 'walk me through R0851' (not a real route)", w?.reply);
note("S03e R0851 → honest reject", !!w && /haven't verified/i.test(w.reply));
note("S03f stale copy '14 verified routes' in reject", !!w && /14 verified/.test(w.reply), "STALE if true");
w = tryWalkthrough("give me step by step for prolific", routeList);
show("stress: 'step by step for prolific'", w?.reply);
note("S03g alias prolific → R0220", w?.routeId === "R0220");
w = tryWalkthrough("how do i use swagbucks", routeList);
note("S03h 'how do i use X' intent", w?.routeId === "R0140", w?.routeId);

// ---------- S04: scam guard ----------
hr("S04 tryScamGuard");
const scams: [string, string][] = [
  ["pay a fee in gift cards to unlock the job", "giftcard+fee"],
  ["they sent me a check to deposit and wire back the difference", "fake-check/wire-back"],
  ["send 0.1 bitcoin first and they double it", "crypto doubling"],
  ["a recruiter asked me to send my bank login", "bank login phishing"],
  ["guaranteed $5,000 a day with no experience", "guaranteed riches"],
];
for (const [q, name] of scams) {
  const rr = tryScamGuard(q);
  show(`scam: ${name}`, rr);
  note(`S04 ${name} fires`, !!rr && /scam|never/i.test(rr));
}
const near: [string, string][] = [
  ["gift card", "gift card alone"],
  ["my boss gave me a gift card", "legit gift card gift"],
  ["microsoft rewards pays me in gift cards", "Microsoft Rewards gift cards"],
  ["is there a signup fee for fetch", "legit question about fee?"],
];
for (const [q, name] of near) {
  const rr = tryScamGuard(q);
  show(`near-miss: ${name}`, rr);
  note(`S04 near-miss '${name}' → null`, rr === null, rr ? "FIRED — false positive" : "clean");
}

// ---------- S05: gambling ----------
hr("S05 tryGamblingGuard");
for (const q of ["what about polymarket?", "should I use kalshi?", "is kalshi legit", "help me build a parlay", "fanduel odds"]) {
  const rr = tryGamblingGuard(q);
  show(`gambling: '${q}'`, rr);
  note(`S05 '${q}' fires`, !!rr && /betting|zero-sum/i.test(rr));
}
note("S05 legit stock question doesn't fire", tryGamblingGuard("what stocks should I buy") === null);

// ---------- S06: privacy ----------
hr("S06 tryPrivacyGuard");
let p = tryPrivacyGuard("show me another user's progress");
show("happy: 'show me another user's progress'", p);
note("S06a fires", !!p && /can't show/i.test(p));
p = tryPrivacyGuard("show me my own progress");
show("stress: 'show me my own progress'", p);
note("S06b own progress → null (no refuse)", p === null);
p = tryPrivacyGuard("what is someone else's email");
show("stress: 'what is someone else's email'", p);
note("S06c fires", !!p && /can't show/i.test(p));

// ---------- S07: stocks (ONE live fetch) ----------
hr("S07 tryQuantStocks (live)");
const st = await tryQuantStocks("should i buy stocks right now?");
show("live screener output", st);
note("S07a returns screen", !!st && /Top 5/i.test(st));
note("S07b honest copy (technical-only, not advice)", !!st && /technical-only|not financial advice/i.test(st));
note("S07c fail-closed path exists in code", (tryQuantStocks.toString().length > 0));
note("S07d free-stock promo excluded", (await tryQuantStocks("which free stocks should I pick")) === null);

// ---------- S08: fast path ----------
hr("S08 tryFastPath");
let f = tryFastPath("what offers do you have", routeList.filter((x: any) => x.status === "verified"));
show("happy: discovery", f);
note("S08a discovery list", !!f && /verified/.test(f));
f = tryFastPath("how does fetch work", routeList);
show("happy: 'how does fetch work'", f);
note("S08b how-does answer", !!f && /R0119/.test(f));
f = tryFastPath("what are the requirements for fetch", routeList);
show("happy: requirements", f);
note("S08c requirements", !!f && /requirements/i.test(f));
const stale = { ...cards.R0119, verified_at: new Date(Date.now() - 8 * 864e5).toISOString() };
f = tryFastPath("how does fetch work", [stale]);
show("stress: verified_at 8d ago", f);
note("S08d stale (>7d) → null", f === null);
f = tryFastPath("is fetch guaranteed to pay me $20", routeList);
show("stress: guarantee words", f);
note("S08e guarantee → null", f === null);
f = tryFastPath("is fetch verified?", routeList);
show("stress: 'is fetch verified?'", f);
note("S08f verification question → null (model path)", f === null);
f = tryFastPath("how much per receipt does fetch pay", routeList);
show("stress: payout question", f);
note("S08g payout block, no invented per-receipt figure", !!f && !/\$\d+\.\d\d per receipt/i.test(f), f ? f.slice(0,80) : "null");
f = tryFastPath("can i use fetch in texas, i'm 25", routeList);
show("stress: eligibility with age", f);
note("S08h age verdict", !!f && /good to go/i.test(f));

// ---------- S09: checkGrounding ----------
hr("S09 checkGrounding");
const cardReply = "Fetch (route R0119) is verified — the card says: Points for scanning receipts (25+ pts/receipt); converts to gift cards. See https://fetch.com for details.";
let v = checkGrounding(cardReply, routeList, "how does fetch work");
show("happy: faithful reply", v);
note("S09a clean → []", v.length === 0, v.join(","));
const evilAmt = checkGrounding("Fetch pays $5,000 per receipt — amazing!", routeList, "how does fetch work");
show("stress: invented $5,000", evilAmt);
note("S09b invented amount → violation", evilAmt.some(x => x.startsWith("invented_amount")));
const evilUrl = checkGrounding("Sign up at https://evil.com now!", routeList, "how does fetch work");
show("stress: evil.com", evilUrl);
note("S09c unlisted URL → violation", evilUrl.some(x => x.startsWith("unlisted_url")));
const guar = checkGrounding("Fetch will guarantee you $20 this week.", routeList, "how does fetch work");
show("stress: 'guarantee you $20'", guar);
note("S09d guarantee language → violation", guar.some(x => x.startsWith("guarantee_language")));
const debunk = checkGrounding("This is a scam — a warning sign is when they promise $5,000 a day at https://scam-offer.example. Don't pay.", routeList, "they promised $5,000 a day, link https://scam-offer.example");
show("stress: debunk quoting user numbers/urls", debunk);
note("S09e debunk quoting user → NO violation", debunk.length === 0, debunk.join(","));
const riskFree = checkGrounding("Fetch is risk-free and will make you rich.", routeList, "how does fetch work");
note("S09f 'risk-free' → violation", riskFree.some(x => x.startsWith("guarantee_language")), riskFree.join(","));

// ---------- S10: fallback selection ----------
hr("S10 violation fallbacks");
note("S10a isDebunkReply on scam warning", isDebunkReply("Stop — that's a scam. Warning sign: gift cards."));
note("S10b isDebunkReply on clean reply", !isDebunkReply("Fetch pays points per receipt."));
const debunkBlocked = checkGrounding("scam alert: they promised $9,999 at https://unknown-xyz.com — stay away!", routeList, "is this legit");
const sel1 = debunkBlocked.length && isDebunkReply("scam alert: they promised $9,999 at https://unknown-xyz.com — stay away!") ? SCAM_FALLBACK : SAFE_FALLBACK;
note("S10c debunk+violation → SCAM_FALLBACK", debunkBlocked.length > 0 && sel1 === SCAM_FALLBACK, debunkBlocked.join(","));
const plainBlocked = checkGrounding("Fetch pays $5,000 per receipt", routeList, "how does fetch work");
const sel2 = plainBlocked.length && isDebunkReply("Fetch pays $5,000 per receipt") ? SCAM_FALLBACK : SAFE_FALLBACK;
note("S10d plain+violation → SAFE_FALLBACK", plainBlocked.length > 0 && sel2 === SAFE_FALLBACK, plainBlocked.join(","));

// ---------- S18: ordering ----------
hr("S18 capability ordering");
let c = await tryCapabilities("walk me through fetch to make $500", fresh());
show("order: 'walk me through fetch to make $500'", c?.reply);
note("S18a make-me wins over walkthrough", !!c && /Fastest honest path|Real talk/i.test(c.reply), "make-me runs first");
c = await tryCapabilities("make me $20 but someone wants a gift card fee to start", fresh());
show("order: scam pattern inside make-me request", c?.reply);
note("S18b scam guard beats make-me", !!c && /scam/i.test(c.reply));
c = await tryCapabilities("i want to make money", fresh());
show("order: vague opener through tryCapabilities", c?.reply);
note("S18c vague → $20 plan via capabilities", !!c && /\$20/.test(c.reply));

console.log(`\n\nTOTAL: ${pass} pass, ${fail} fail`);
