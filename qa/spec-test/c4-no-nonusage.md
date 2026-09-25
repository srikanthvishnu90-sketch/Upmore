# Agent C4 Report — Cancel: No Non-Usage Claims

**Verdict: FAIL** — one confirmed spec violation, user-visible, deterministic (not a flaky edge case).

**Method note:** As a subagent I cannot drive the live browser, so I audited the source of truth instead: `src/upmore-app-template.html` and the built `index.html` that ships to production. The offending string is baked into both — this is not a rendering artifact, it is the shipped copy. A browser visit would show the same text in the Guide chat when the user asks to "audit my subscriptions."

## Violation 1 (confirmed) — Guide asserts 30-day non-usage it cannot know

**Location:** `guideAnswer()` deterministic intent for "audit my subscriptions" — `src/upmore-app-template.html:2572` (also present in built `index.html`).

**Exact quote:**
> "Here's the audit playbook: list every recurring charge, **flag anything you haven't used in 30 days**, then cancel from the merchant's own page — I'll give you the exact steps for each one."

**Why this violates the spec:** Doc 2 (Cancel) says: *"Never claim non-usage; ask."* Upmore has no usage telemetry — it sees charges, not whether the user watched, listened, read, or logged in. "You haven't used [X] in 30 days" asserts a fact about the user's behavior that the app cannot observe. This is precisely the claim the spec forbids. The follow-up line ("Tell me what you listed and I'll flag the likely waste," :2573) does not cure it — the damage is done in the first sentence, and "likely waste" inherits the asserted usage premise.

**Required fix:** Rewrite to ask, e.g.: "Here's the audit playbook: list every recurring charge, then tell me which ones you actually use — I'll rank the rest by dollars at stake and give you the exact cancel steps for each." Never state a usage fact; solicit it.

## What passed (checked, clean)

- **`cancelCard()` 7 elements** (:3069–3092): merchant, amount/interval, annual 12-mo projection explicitly labelled "(projection, not savings)", next billing date, method badge, observed time with n, retention offer. Zero usage claims.
- **Monitor-driven cancel cards** in `buildQueue()` (:1764–1780): `wasteScore` is called with a hardcoded neutral `usageSignal = 0.5` — an internal ranking assumption, never rendered as a user-facing fact. The card sub-line shows amount/annual/billing only. Clean.
- **Home Track promo** (:787): "we flag duplicates, price hikes, and renewals from what you enter" — no usage claims. Clean.
- **Subscription detectors** (duplicate charges, bill spike, renewal approaching, :1814–1850): all evidence-based on amounts/dates the user entered or that were detected from charges. No usage assertions. Clean.
- **Code comments** (:3039, :3068) explicitly restate the "Never claim non-usage — ask" rule. The intent is documented; the Guide copy just doesn't follow it.

## Bottom line

The Cancel card pipeline is clean. The single failure is in the Guide's subscription-audit script — one sentence that claims 30-day non-usage as fact. Fix the sentence, re-run this check, and C4 passes. Until then: **FAIL**.
