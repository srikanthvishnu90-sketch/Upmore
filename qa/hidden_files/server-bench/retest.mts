// Re-tests with corrected checks (no live network calls).
import { readFileSync } from "node:fs";
import { tryMakeMeX, tryCapabilities } from "./capabilities.ts";
import { checkGrounding, isDebunkReply, SAFE_FALLBACK, SCAM_FALLBACK } from "./agent.ts";
import { tryFastPath } from "./fastpath.ts";

const cards = JSON.parse(readFileSync("./fixtures.json", "utf8"));
const routeList = Object.values(cards);
const fresh = () => routeList;
let pass = 0, fail = 0;
function note(label, ok, detail = "") { ok ? pass++ : fail++; console.log(`${ok ? "PASS" : "FAIL"} ${label}${detail ? " — " + detail : ""}`); }

// S01 corrected
let r = tryMakeMeX("make me $20", fresh());
note("S01a happy $20 → deterministic plan", !!r && /Fastest honest path to \$20/.test(r), r ? r.split("\n")[0] : "null");
note("S01e link present (any URL)", !!r && /https?:\/\//.test(r));

// S02 corrected: allow the known closing CTA question
for (const q of ["i want to make money", "help me make money"]) {
  const rr = tryMakeMeX(q, fresh());
  const stripped = rr ? rr.replace(/Want me to walk you through step 1\?/g, "") : "";
  note(`S02 '${q}' anchors $20, no interrogation`, !!rr && rr.includes("$20") && !stripped.includes("?"), rr ? "CTA-only question" : "null");
}
const sExtra = tryMakeMeX("i want to make some extra money", fresh());
note("S02 'i want to make some extra money' → NULL (BUG)", sExtra === null, "regex (some |extra )? allows only one");
const hExtra = tryMakeMeX("help me make some extra money", fresh());
note("S02 'help me make some extra money' → NULL (BUG)", hExtra === null);

// S09b / S10d corrected with $77,777 (verified absent from fixtures)
const evilAmt = checkGrounding("Fetch pays $77,777 per receipt — amazing!", routeList, "how does fetch work");
note("S09b invented $77,777 → violation", evilAmt.some(x => x.startsWith("invented_amount")), evilAmt.join(","));
const plainBlocked = checkGrounding("Fetch pays $77,777 per receipt", routeList, "how does fetch work");
const sel2 = plainBlocked.length && isDebunkReply("Fetch pays $77,777 per receipt") ? SCAM_FALLBACK : SAFE_FALLBACK;
note("S10d plain+violation → SAFE_FALLBACK", plainBlocked.length > 0 && sel2 === SAFE_FALLBACK && sel2 === SAFE_FALLBACK);

// S08c documented bug retest
const reqc = tryFastPath("what are the requirements for fetch", routeList);
note("S08c plural 'requirements' → NULL (BUG)", reqc === null);

// S18 ordering nuance
const c1 = await tryCapabilities("walk me through fetch to make $500", fresh());
note("S18 '...to make $500' → walkthrough wins (no literal 'make me')", !!c1 && c1.reply.includes("verified live"), c1.reply.split("\n")[0].slice(0,60));
const c2 = await tryCapabilities("walk me through fetch, make me $500", fresh());
note("S18 '..., make me $500' → make-me wins (order: makeMe before walk)", !!c2 && /Fastest honest path|Real talk/.test(c2.reply), c2.reply.split("\n")[0].slice(0,60));

console.log(`\nTOTAL: ${pass} pass, ${fail} fail`);
