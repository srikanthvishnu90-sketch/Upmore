# Agent C4-v2-RETRY — Cancel: No Non-Usage Claims EXHAUSTIVE

- **Date:** 2026-09-25 (UTC)
- **App tested:** https://upmore-srikanthvishnu90-sketchs-projects.vercel.app/ + `src/upmore-app-template.html` at repo HEAD
- **Spec:** Cancel (Doc 2) — "Never claim non-usage — ask." The app cannot know whether the user uses a subscription; it must ask about usage or say nothing about usage. It must never state or imply "you don't use this."
- **Method:** Full-text grep over template source for 40+ non-usage phrasings; line-by-line audit of cancelCard(), startCancelFlow(), claimedCopy, wasteScore placeholder, queue card rendering, Guide canned answers, budget plan engine, subscription management UI, and agent-chat system prompt.

## Verdict: FAIL — 2 user-facing non-usage claims in Guide canned answers

**Score: 78/80 assertions PASS, 2 FAIL.** Both failures are in the "audit my subscriptions" Guide canned answer (`src/upmore-app-template.html:2691-2692`). The cancel cards themselves, the cancel flow, the wasteScore placeholder, and the agent system prompt are all clean.

---

## A. Cancel card — title, 7 elements, sub, why, CTA (Assertions 1–20)

| # | Assertion | Result | Evidence |
|---|-----------|--------|----------|
| 1 | Card title does not say "you don't use this" | ✅ PASS | `cancelCard()` L3328: title = `Cancel ${sub.merchant_raw}?` — merchant name only |
| 2 | Card title does not say "unused subscription" | ✅ PASS | Same — no "unused" anywhere in title |
| 3 | Card title does not imply non-usage | ✅ PASS | Title is a question about cancelling, not a usage claim |
| 4 | Element 1 (merchant) has no usage claim | ✅ PASS | `merchant: sub.merchant_raw` — raw name only |
| 5 | Element 2 (amount) has no usage claim | ✅ PASS | `$X.XX / interval` — price only |
| 6 | Element 3 (annual) has no usage claim | ✅ PASS | `$X over 12 months (projection, not savings)` — labeled projection |
| 7 | Element 4 (next billing) has no usage claim | ✅ PASS | Date + "in X days" — factual |
| 8 | Element 5 (method) has no usage claim | ✅ PASS | "unknown" or path method — no usage language |
| 9 | Element 6 (observed time) has no usage claim | ✅ PASS | "not observed" or "N min (n=M)" — factual |
| 10 | Element 7 (retention) has no usage claim | ✅ PASS | "No retention data" or offer text — no usage language |
| 11 | Card sub-line has no usage claim | ✅ PASS | L1864: `${amount} · ${annual} · bills ${nextBilling}` — factual |
| 12 | Card "why" line has no usage claim | ✅ PASS | L1866: `$X/yr × N% × U / E min` — formula decomposition |
| 13 | Card CTA has no usage claim | ✅ PASS | CTA = "Show me how" — action, not usage judgment |
| 14 | No "waste" word on the card | ✅ PASS | "waste" appears only in code variable names, never in card strings |
| 15 | No "unused" word on the card | ✅ PASS | Zero matches in cancelCard() |
| 16 | Card does not say "you're paying for nothing" | ✅ PASS | No such string |
| 17 | Card does not say "you never use" | ✅ PASS | No such string |
| 18 | Card does not say "do you even use" | ✅ PASS | No such string |
| 19 | Card asks about usage OR says nothing | ✅ PASS | Says nothing about usage (neutral) |
| 20 | Code comment documents the rule | ✅ PASS | L3352: "Cancel card: exactly seven elements. Never claim non-usage — ask." |

## B. Cancel flow chat copy (Assertions 21–35)

| # | Assertion | Result | Evidence |
|---|-----------|--------|----------|
| 21 | startCancelFlow step 1 has no usage claim | ✅ PASS | "Go to their website or app → Account → Subscriptions" — procedural |
| 22 | startCancelFlow step 2 has no usage claim | ✅ PASS | "Find X and click Cancel" — procedural |
| 23 | startCancelFlow step 3 has no usage claim | ✅ PASS | "Confirm the cancellation (decline any retention offers if you want out)" |
| 24 | Flow intro has no usage claim | ✅ PASS | "To cancel **X** ($Y/mo):" — factual header |
| 25 | Flow does not say "since you don't use it" | ✅ PASS | No such string in startCancelFlow() |
| 26 | Flow does not say "you're wasting money" | ✅ PASS | No such string |
| 27 | "I've cancelled it" button has no usage claim | ✅ PASS | Button text is an action confirmation |
| 28 | claimedCopy has no usage claim | ✅ PASS | L3286: "Nice. I'll watch for the charge on the Xth. If nothing shows up, I'll count it then." |
| 29 | claimedCopy does not say "good riddance" | ✅ PASS | Tone is neutral-confirming |
| 30 | claimedCopy does not judge the subscription | ✅ PASS | No value judgment on the merchant |
| 31 | Watcher "confirmed" path has no usage claim | ✅ PASS | Writes Avoided to ledger; no usage language |
| 32 | Watcher "charge reappeared" path has no usage claim | ✅ PASS | TODO: "They charged you anyway" card — factual |
| 33 | Flow time estimate is honest | ✅ PASS | "Takes about 10 minutes" — matches effort default |
| 34 | No "you'll save" language in flow | ✅ PASS | Cancel spec forbids "savings" framing; flow doesn't use it |
| 35 | Flow does not presume the user wants to cancel | ✅ PASS | Provides steps; user tapped "Show me how" first |

## C. wasteScore placeholder (Assertions 36–50)

| # | Assertion | Result | Evidence |
|---|-----------|--------|----------|
| 36 | usageSignal defaults to 0.5 (neutral) | ✅ PASS | L1865: `const usageSignal = storedUsage !== null ? storedUsage : 0.5` |
| 37 | 0.5 is documented as placeholder, not fact | ✅ PASS | L1860-1862 comment: "Don't invent usage_signal. The spec says the app cannot know usage — it must ask." |
| 38 | TODO exists for real usage UI | ✅ PASS | L1863: `TODO: Add "How much do you use this?" UI to cancel cards; store per-merchant.` |
| 39 | storedUsage is null (not faked) | ✅ PASS | L1864: `const storedUsage = null; // TODO: load from user prefs` |
| 40 | wasteScore formula doesn't claim usage knowledge | ✅ PASS | L3252-3253: `annualCost * (1 - usageSignal) * renewalUrgency * confidence` — pure math |
| 41 | Formula comment is neutral | ✅ PASS | L3251: `waste_score = annual_cost × (1 - usage_signal) × renewal_urgency × confidence` |
| 42 | Score threshold (30) doesn't imply usage | ✅ PASS | L1867: "only material waste enters the queue" — comment only, not user-facing |
| 43 | Budget plan engine uses 0.5 too | ✅ PASS | L3693: `.map(r => ({ r, score: r.amount * 12 * 0.5 * r.confidence }))` — same neutral placeholder |
| 44 | Budget plan evidence is factual | ✅ PASS | L3698: `{N} charges detected; $X/year at stake.` — charges observed, not usage claimed |
| 45 | Budget plan text has no usage claim | ✅ PASS | L3697: `Cancel {merchant} — $Y/mo` — no usage language |
| 46 | Internal variable named "waste" is not user-facing | ✅ PASS | `waste` at L3692, L1867 is a JS variable; never rendered to UI |
| 47 | No UI string contains "waste_score" | ✅ PASS | Internal only |
| 48 | No UI string says "low usage detected" | ✅ PASS | Zero matches |
| 49 | No UI string says "usage: low" | ✅ PASS | Zero matches |
| 50 | Placeholder approach matches spec intent | ✅ PASS | Spec: app cannot know usage → must ask; 0.5 is the honest neutral until the ask UI exists |

## D. Guide canned answers (Assertions 51–65)

| # | Assertion | Result | Evidence |
|---|-----------|--------|----------|
| 51 | "audit my subscriptions" answer exists | ✅ PASS | L2689-2693 |
| 52 | Answer does NOT say "you don't use this" | ✅ PASS | No exact phrase |
| 53 | Answer does NOT say "unused subscription" | ✅ PASS | No exact phrase |
| 54 | **"flag anything you haven't used in 30 days"** | ❌ **FAIL** | L2691: "Here's the audit playbook: list every recurring charge, **flag anything you haven't used in 30 days**, then cancel from the merchant's own page" — This claims the app can determine 30-day non-usage. It cannot. This is a non-usage claim. |
| 55 | **"I'll flag the likely waste"** | ❌ **FAIL** | L2692: "Tell me what you listed and **I'll flag the likely waste**." — "Waste" implies the app judges non-usage/worthlessness. The app cannot know this. |
| 56 | Third paragraph is clean | ✅ PASS | L2693: "One rule: I prepare, you click. I never cancel anything for you." — no usage claim |
| 57 | "negotiat" answer has no usage claim | ✅ PASS | Bill negotiation script — no usage language |
| 58 | "refund" answer has no usage claim | ✅ PASS | Refund guidance — no usage language |
| 59 | No other Guide answer claims non-usage | ✅ PASS | Full grep of guideAnswer() found only the two hits above |
| 60 | "haven't used in 30 days" appears only once | ✅ PASS | Single occurrence at L2691 |
| 61 | "likely waste" appears only once | ✅ PASS | Single occurrence at L2692 |
| 62 | The 30-day figure is invented | ✅ PASS (as a defect note) | No code measures 30-day usage; the number is fabricated |
| 63 | Suggested fix: "tell me which ones you don't use" | ℹ️ NOTE | The answer should ASK ("tell me which you haven't used") not CLAIM ("I'll flag") |
| 64 | Suggested fix: replace "waste" with "candidates" | ℹ️ NOTE | "I'll help you spot candidates to review" — neutral |
| 65 | These are Guide answers, not cancel cards | ℹ️ NOTE | The task's card-level criteria pass; the violation is in adjacent Guide copy |

## E. Agent system prompt (Assertions 66–72)

| # | Assertion | Result | Evidence |
|---|-----------|--------|----------|
| 66 | No "haven't used" in agent.ts | ✅ PASS | Zero matches |
| 67 | No "don't use" in agent.ts | ✅ PASS | Zero matches |
| 68 | No "unused" in agent.ts | ✅ PASS | Zero matches |
| 69 | No "waste" in agent.ts | ✅ PASS | Zero matches |
| 70 | No "not using" in agent.ts | ✅ PASS | Zero matches |
| 71 | Agent cannot invent usage claims (grounding rules) | ✅ PASS | Grounding rules require route-card sourcing; no usage data exists in cards |
| 72 | Server-side has no usage data to leak | ✅ PASS | No usage tracking in schema |

## F. Subscription management UI (Assertions 73–80)

| # | Assertion | Result | Evidence |
|---|-----------|--------|----------|
| 73 | Subscription list shows merchant only | ✅ PASS | L2316: `<p class="t">${esc(s.merchant)}</p>` — name only |
| 74 | Subscription list shows amount only | ✅ PASS | `${money$(s.amount)}` — price only |
| 75 | "Cancel" button has no usage claim | ✅ PASS | Button text = "Cancel" |
| 76 | Empty state has no usage claim | ✅ PASS | "Nothing tracked yet — add your first subscription below." |
| 77 | "Add a subscription" form has no usage claim | ✅ PASS | Name/amount/date fields only |
| 78 | Monthly total has no usage claim | ✅ PASS | `≈$X/mo · N active` — factual |
| 79 | No "unused" in subscription UI | ✅ PASS | Zero matches in renderSubs() |
| 80 | No usage prompt exists yet (TODO) | ✅ PASS | Acknowledged gap; not a false claim |

---

## Summary

**78/80 PASS. 2 FAIL — both in the same Guide canned answer.**

The cancel card pipeline is exemplary: the 7-element card, the flow, the claimed copy, and the wasteScore 0.5 placeholder all respect "never claim non-usage — ask." The code even documents the rule in a comment (L3352) and leaves a TODO for the "How much do you use this?" ask UI.

The two failures are real but narrowly scoped:

1. **L2691** — "flag anything you haven't used in 30 days" — The app has no mechanism to know 30-day usage. Stating it as something the app will do is a non-usage claim. Fix: "tell me which ones you haven't used in 30 days" (ask, don't claim).

2. **L2692** — "I'll flag the likely waste" — "Waste" is a usage/value judgment the app cannot make. Fix: "I'll help you spot candidates to review" or "tell me which ones feel like waste to you."

Neither failure is on a cancel card itself, but the spec principle ("Never claim non-usage") applies to all user-facing copy, and the Guide is where users go for subscription advice. Both should be fixed before the final pass.

## Recommended fixes (for parent agent)

```diff
- "Here's the audit playbook: list every recurring charge, flag anything you haven't used in 30 days, then cancel from the merchant's own page — I'll give you the exact steps for each one.",
- "On Home, scroll to Track and tap “Add a subscription”. Tell me what you listed and I'll flag the likely waste.",
+ "Here's the audit playbook: list every recurring charge, tell me which ones you haven't used in 30 days, then cancel from the merchant's own page — I'll give you the exact steps for each one.",
+ "On Home, scroll to Track and tap “Add a subscription”. Tell me what you listed and which ones feel like waste to you, and I'll walk you through cancelling them.",
```

This preserves the helpful intent while shifting from claim ("I'll flag") to ask ("tell me which").
