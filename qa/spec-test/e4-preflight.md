# Agent E4 — Earn Pre-flight Screen: HARSH TEST REPORT

**Verdict: CONDITIONAL FAIL** (pre-flight exists and gates step 1 on every entry path — but one of the four spec-mandated disclosures is missing, and the abandonment assurance is potentially false)

**Tested:** commit `7c0c795` ("Earn pre-flight screen"), template `src/upmore-app-template.html:1565`, built `index.html` contains the pre-flight string (verified by grep). Production rollout of that commit was in flight at test time; I could not live-render (no live browser in this lane), so behavioral claims below are from code-path analysis of every walkthrough entry point, not a clicked-through session. Flagged where live verification is still needed.

## What passes

1. **A pre-flight screen exists and fires BEFORE step 1.** `startWalkthrough()` intercepts fresh starts (`i === 0`), renders the disclosure, appends a "Start walkthrough" button, and `return`s before `renderWalkStep` is ever called. Step 1 is unreachable without the button tap. This is the core requirement and it holds.
2. **No bypass paths.** I enumerated every caller of `startWalkthrough` (app cards L1543, queue earn CTA L1758, guide "Open move" L2366/L2900, `guideAsk` agent actions L2849/2854/2859, `[data-walk]` buttons L2975). All funnel through the single function. `renderWalkStep` is only invoked from inside `startWalkthrough` or by itself (step advance). Resume (`i > 0`) correctly skips pre-flight — resuming is not "before step 1."
3. **Money cost and time cost are disclosed.** `**Cost:**` renders `r.costs_and_unpaid_time`; `**Time:**` renders the active-minutes range. Present and ordered before the CTA.

## FAILURES (harsh)

### F1 — HARD FAIL: "failure risks" disclosure is missing
Spec (`docspecs/01-earn.md:59`) mandates four disclosures: *"money/time cost, **failure risks**, requested personal data, and consequences of abandonment."* The rendered pre-flight contains Cost, Time, "They'll ask for," and abandonment — **failure risks appear nowhere**. Not as a section, not as a sentence. The code comment even claims "disclose cost, **risks**, data, abandonment" — the comment promises what the string doesn't deliver. Examples of what should be there and isn't: "you may not be selected," "the reward can be denied if requirements aren't met exactly," "accounts can be closed for bonus abuse." A user walking into a bank-bonus route with no stated failure mode is exactly the harm this disclosure exists to prevent.

### F2 — The abandonment assurance is potentially false
`"If you stop halfway: nothing is submitted until you complete the final step — you can abandon anytime with no penalty."` This is a blanket claim across all routes. For bank-bonus routes, an intermediate step *is* opening an account — a ChexSystems inquiry and a real financial footprint. That is a consequence, and "no penalty" says otherwise. The claim is unverifiable per-route and likely false for the highest-value routes in the catalog. It should be per-route ("stopping after step N means…") or downgraded to what is actually known.

### F3 — Disclosure fallbacks degrade to nothing
- `costs_and_unpaid_time` empty → **"No upfront cost stated."** This conflates "verified free" with "we don't know." A route with missing cost data gets a reassuring sentence it hasn't earned.
- `requirements` empty → **"They'll ask for: —"** — a literal dash. That is a broken disclosure, not a disclosure. If the data is absent, the pre-flight should say the data is absent, not render punctuation.

### F4 — Inconsistent escaping (minor, sloppiness)
The pre-flight interpolates `${r.provider}`, `${costs}`, `${data}` raw into `addAI()` → `md()`. The resume branch two lines below uses `esc(r.provider)`. Same function, two conventions. Catalog data is operator-owned so exploitability is low, but a harsh read says: the codebase has an escaping convention and this new code ignores it.

### F5 — No dismiss path (minor UX)
The pre-flight offers "Start walkthrough" but no "Not now." A user who gets cold feet must tab away, leaving an orphaned button in chat history. Trivial, but the spec's abandonment theme cuts both ways — abandoning the *pre-flight* should be a first-class action.

## Live-verification gap (not a code finding)
I verified the pre-flight string is in the pushed build. I did **not** click through a walkthrough in production (no live-browser lane available to this agent). Parent should confirm visually: Home → queue → earn card → "Walk me through it" → pre-flight renders with all four disclosures (after F1 is fixed).

## Required fixes before PASS
1. Add an explicit **failure-risks** disclosure to the pre-flight string (per-route where data exists, e.g. from `catches`/requirements; honest generic fallback where it doesn't — never silence).
2. Replace the blanket "no penalty" abandonment claim with a per-route-accurate statement, or scope it to what is actually true ("Upmore itself submits nothing; anything you submit on the provider's site is yours").
3. Fix the fallbacks: distinguish "verified no cost" from "cost unknown"; never render "They'll ask for: —".
4. Use `esc()` consistently in the pre-flight interpolations.
