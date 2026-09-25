# Beta agent 01 - output (FINAL run, build 2a9d29b, 2026-09-25)

Account: qa01@upmore.app. Fresh-build gate PASS (no History button). Session PASS (email verified). Signed out at end; no test data ($0.00, 0 entries).

## Scenario: HOME QUEUE RENDER
1. Exactly one "Up next" section, >=1 card, top card complete — PASS. 9 queue cards. Top card: "Mindswarms — Focus Group"; sub-line "You can receive $10-$50 (and sometimes more) per study, within 24 hours via PayPal. · Minutes to hours"; why-line "$50 x 70% x 2 / 4 min - pays fast"; CTA "Walk me through it".
2. Scoring attributes on every card — PASS. All 9 carry data-dollar, data-conf, data-urg, data-eff, data-score: Mindswarms 50/0.7/2/4/17.50; Gaultenergy — Energy Switching 150/0.7/2/22.5/9.33; Blazecu — Bank bonus 250/0.7/2/45/7.78; BOK Financial 450/0.7/1/45/7.00; Nymcu 350/0.7/1/45/5.44; Old National Bank 300/0.7/1/45/4.67; Pampers Club — Receipt/Loyalty 10/0.7/2/10/1.40; Adobe Creative Cloud Student 19/0.7/2/30/0.89; Lampsplus — Signup Bonus 15/0.7/2/25/0.84.
3. No horizontal overflow at 390px — PASS (visual via screenshots; all cards fit, no horizontal scrollbar).
4. CRITICAL: top card is extractable cash — PASS. "You can receive $10-$50 (and sometimes more) per study, within 24 hours via PayPal." Dollar-denominated, PayPal payout. Not points/XP, not gift cards, not credit, not tax credit, not referral-gated. The pointsMechanism() fix works: no points route leads.

## Retrospective
Queue mechanics work; the top pick is genuinely extractable cash serving "find real extra money". Observation (not a scenario failure): cards 7–9 are non-cash routes scored in dollars — Pampers Club (rewards-catalog store credit), Adobe Creative Cloud Student (labeled "discount on a paid subscription, NOT income"), Lampsplus ("$15 Off $50" coupon). They don't LEAD (standing rule is about leading), and the Adobe card discloses honestly, but a user trusting the queue past the top card drifts from extractable cash. Flagged as an open product judgment call for the owner: whether non-cash routes belong in the "Up next" money queue at all, or should be separated.

RESULT: PASS
