# agent100 run 2026-09-27T22-37-27 (dry) — 2026-09-27T22:37:27.810Z
Agents: 0/20 pass (0.0%) · Steps: 32/71 (45.1%) · API calls: 0 · 10s

## By lane
- budgeting: 0/10
- tracking: 0/10

## Failures by category
- constraint_ignored: 38
- disclosure_missing: 2

## Failed agents (fix-loop: re-run with --only-failed)

### a021 — Broke college gig worker asks for a budget report with no bank linked [budgeting]
- step 1 (guide):
  - [constraint_ignored] expected /connect/ in: I can look up any of the 1775 routes in the catalog — try a category like bank bonuses, surveys, or cashback, or name a provider like Fetch.

Or ask me what's the catch with any offer, and I'll give i
- step 2 (guide):
  - [constraint_ignored] expected /budget/ in: I can look up any of the 1775 routes in the catalog — try a category like bank bonuses, surveys, or cashback, or name a provider like Fetch.

Or ask me what's the catch with any offer, and I'll give i

### a022 — Single mom on a tight budget asks where her money goes each month [budgeting]
- step 1 (guide):
  - [constraint_ignored] expected /spending|cash flow/ in: I can look up any of the 1775 routes in the catalog — try a category like bank bonuses, surveys, or cashback, or name a provider like Fetch.

Or ask me what's the catch with any offer, and I'll give i
- step 2 (guide):
  - [constraint_ignored] expected /connect|demo|sample|estimate/ in: I can look up any of the 1775 routes in the catalog — try a category like bank bonuses, surveys, or cashback, or name a provider like Fetch.

Or ask me what's the catch with any offer, and I'll give i

### a023 — Manager audits forgotten subscriptions and asks for cancel help [budgeting]
- step 1 (guide):
  - [constraint_ignored] expected /recurring|subscription/ in: I can look up any of the 1775 routes in the catalog — try a category like bank bonuses, surveys, or cashback, or name a provider like Fetch.

Or ask me what's the catch with any offer, and I'll give i
- step 2 (guideThread):
  - [constraint_ignored] expected /recurring|subscription/ in: I can look up any of the 1775 routes in the catalog — try a category like bank bonuses, surveys, or cashback, or name a provider like Fetch.

Or ask me what's the catch with any offer, and I'll give i
- step 3 (guide):
  - [constraint_ignored] expected /approv/ in: Help — Telecom Promo. Published reward: $50 credit for your first referral. $25 credit for each referral after that. Your friends and family get a $25 credit just for signing up with your link.. Catal

### a024 — Retiree who overspent asks what to do — no guilt language allowed [budgeting]
- step 1 (guide):
  - [constraint_ignored] expected /adjust|plan|rollover|budget/ in: I can look up any of the 1775 routes in the catalog — try a category like bank bonuses, surveys, or cashback, or name a provider like Fetch.

Or ask me what's the catch with any offer, and I'll give i

### a025 — Freelancer with swingy income asks about budgeting and rollover [budgeting]
- step 1 (guide):
  - [constraint_ignored] expected /average|irregular|buffer/ in: I can look up any of the 1775 routes in the catalog — try a category like bank bonuses, surveys, or cashback, or name a provider like Fetch.

Or ask me what's the catch with any offer, and I'll give i
- step 2 (guide):
  - [constraint_ignored] expected /rollover|carry/ in: I can look up any of the 1775 routes in the catalog — try a category like bank bonuses, surveys, or cashback, or name a provider like Fetch.

Or ask me what's the catch with any offer, and I'll give i
- step 3 (guide):
  - [constraint_ignored] expected /can't guarantee|no guarantee|not guarantee/ in: I can look up any of the 1775 routes in the catalog — try a category like bank bonuses, surveys, or cashback, or name a provider like Fetch.

Or ask me what's the catch with any offer, and I'll give i

### a026 — New grad checks how he's doing against his first budgets [budgeting]
- step 1 (guide):
  - [constraint_ignored] expected /actual|on track|target/ in: I can look up any of the 1775 routes in the catalog — try a category like bank bonuses, surveys, or cashback, or name a provider like Fetch.

Or ask me what's the catch with any offer, and I'll give i
- step 2 (guideThread):
  - [constraint_ignored] expected /adjust|average|flexib/ in: I can look up any of the 1775 routes in the catalog — try a category like bank bonuses, surveys, or cashback, or name a provider like Fetch.

Or ask me what's the catch with any offer, and I'll give i
- step 3 (static):
  - [disclosure_missing] budgets-vs-actual comparison copy present in the template: op=contains no match in template

### a027 — Small business owner tests extra loan payments against her budget [budgeting]
- step 3 (guide):
  - [constraint_ignored] expected /interest|payoff|month/ in: I can look up any of the 1775 routes in the catalog — try a category like bank bonuses, surveys, or cashback, or name a provider like Fetch.

Or ask me what's the catch with any offer, and I'll give i

### a028 — Dual-income couple tests extra auto-loan payments against their budget [budgeting]
- step 2 (guide):
  - [constraint_ignored] expected /interest|month|budget/ in: More is retired — that offer is no longer available, so I won't walk you through it. Want me to find a live alternative in Card Bonus?
- step 3 (guide):
  - [constraint_ignored] expected /connect|demo|sample|estimate/ in: I can look up any of the 1775 routes in the catalog — try a category like bank bonuses, surveys, or cashback, or name a provider like Fetch.

Or ask me what's the catch with any offer, and I'll give i
- step 4 (static):
  - [disclosure_missing] top merchants surface present in the budget report: op=contains no match in template

### a029 — Teacher who overspent fun money asks without being judged [budgeting]
- step 1 (guide):
  - [constraint_ignored] expected /budget|plan/ in: I can look up any of the 1775 routes in the catalog — try a category like bank bonuses, surveys, or cashback, or name a provider like Fetch.

Or ask me what's the catch with any offer, and I'll give i
- step 2 (guide):
  - [constraint_ignored] expected /connect|demo|sample/ in: The fastest routes in the catalog — check "Cash arrives" on each before you start:

1. Mindswarms — You can receive $10-$50 (and sometimes more) per study, within 24 hours via PayPal.. Who pays: Minds
- step 3 (static):
  - [constraint_ignored] no dark-pattern language in budgeting copy: op=notContains matched in template

### a030 — First-time budgeter wants plain English; net worth calc is demo-labeled [budgeting]
- step 1 (guide):
  - [constraint_ignored] expected /spending|cash flow|budget/ in: I can look up any of the 1775 routes in the catalog — try a category like bank bonuses, surveys, or cashback, or name a provider like Fetch.

Or ask me what's the catch with any offer, and I'll give i
- step 3 (guide):
  - [constraint_ignored] expected /demo|sample|example/ in: I can look up any of the 1775 routes in the catalog — try a category like bank bonuses, surveys, or cashback, or name a provider like Fetch.

Or ask me what's the catch with any offer, and I'll give i

### a031 — Engineer asks for net worth with no accounts linked — demo must be labeled [tracking]
- step 1 (guide):
  - [constraint_ignored] expected /demo|sample|example/ in: The fastest routes in the catalog — check "Cash arrives" on each before you start:

1. Mindswarms — You can receive $10-$50 (and sometimes more) per study, within 24 hours via PayPal.. Who pays: Minds
  - [constraint_ignored] expected /connect/ in: The fastest routes in the catalog — check "Cash arrives" on each before you start:

1. Mindswarms — You can receive $10-$50 (and sometimes more) per study, within 24 hours via PayPal.. Who pays: Minds

### a032 — Landlord hunts repeating charges across personal and rental accounts [tracking]
- step 1 (guide):
  - [constraint_ignored] expected /recurring/ in: Accounts — Referral Bonus. Published reward: You are eligible to receive a $50 bonus for each referral who opens a qualifying checking account (up to 10 referrals – total of $500) in a calendar year..
- step 2 (guideThread):
  - [constraint_ignored] expected /recurring|increase|price/ in: I can look up any of the 1775 routes in the catalog — try a category like bank bonuses, surveys, or cashback, or name a provider like Fetch.

Or ask me what's the catch with any offer, and I'll give i

### a033 — Grad student works through her uncategorized transaction queue [tracking]
- step 2 (guide):
  - [constraint_ignored] expected /recategorize|fix|correct|re-categor/ in: I can look up any of the 1775 routes in the catalog — try a category like bank bonuses, surveys, or cashback, or name a provider like Fetch.

Or ask me what's the catch with any offer, and I'll give i

### a034 — Near-retiree reviews transactions and questions a mystery charge [tracking]
- step 1 (guide):
  - [constraint_ignored] expected /transaction|review/ in: I can look up any of the 1775 routes in the catalog — try a category like bank bonuses, surveys, or cashback, or name a provider like Fetch.

Or ask me what's the catch with any offer, and I'll give i

### a035 — Gig driver asks point-blank whether the app's numbers are real [tracking]
- step 1 (guide):
  - [constraint_ignored] expected /demo|sample|example|connect/ in: I can look up any of the 1775 routes in the catalog — try a category like bank bonuses, surveys, or cashback, or name a provider like Fetch.

Or ask me what's the catch with any offer, and I'll give i
- step 3 (guide):
  - [constraint_ignored] expected /connect|real/ in: I can look up any of the 1775 routes in the catalog — try a category like bank bonuses, surveys, or cashback, or name a provider like Fetch.

Or ask me what's the catch with any offer, and I'll give i

### a036 — Divorced parent tracks whether loan payments are gaining ground [tracking]
- step 2 (guide):
  - [constraint_ignored] expected /balance|progress|payoff|track/ in: I can look up any of the 1775 routes in the catalog — try a category like bank bonuses, surveys, or cashback, or name a provider like Fetch.

Or ask me what's the catch with any offer, and I'll give i
- step 3 (guideThread):
  - [constraint_ignored] expected /interest|month|payoff/ in: More is retired — that offer is no longer available, so I won't walk you through it. Want me to find a live alternative in Card Bonus?

### a037 — Married couple hunts duplicate subscriptions across shared accounts [tracking]
- step 1 (guide):
  - [constraint_ignored] expected /recurring|subscription|duplicat/ in: Accounts — Referral Bonus. Published reward: You are eligible to receive a $50 bonus for each referral who opens a qualifying checking account (up to 10 referrals – total of $500) in a calendar year..
- step 2 (guideThread):
  - [constraint_ignored] expected /duplicat/ in: I can look up any of the 1775 routes in the catalog — try a category like bank bonuses, surveys, or cashback, or name a provider like Fetch.

Or ask me what's the catch with any offer, and I'll give i

### a038 — Retiree asks where the app's numbers came from and if her info is safe [tracking]
- step 1 (guide):
  - [constraint_ignored] expected /demo|sample|example/ in: I can look up any of the 1775 routes in the catalog — try a category like bank bonuses, surveys, or cashback, or name a provider like Fetch.

Or ask me what's the catch with any offer, and I'll give i
- step 3 (guide):
  - [constraint_ignored] expected /read-only|safe|secur|encrypt/ in: Every offer shows its catch before you start — that's the rule. The common ones: rewards paid as points or credit instead of cash, direct-deposit definitions that exclude app transfers, strict deadlin

### a039 — College senior asks why transactions are 'other' and wants them fixed [tracking]
- step 2 (guide):
  - [constraint_ignored] expected /categor|review|confirm/ in: The fastest routes in the catalog — check "Cash arrives" on each before you start:

1. Mindswarms — You can receive $10-$50 (and sometimes more) per study, within 24 hours via PayPal.. Who pays: Minds

### a040 — Contractor with variable income tracks truck-loan payoff progress [tracking]
- step 2 (guide):
  - [constraint_ignored] expected /track|balance|behind|payoff/ in: When money has been negative for months, this isn't a budgeting slip — trimming a subscription won't fix a structural gap. So I'm not going to suggest cuts; here's what actually helps in this spot.

C
- step 3 (guideThread):
  - [constraint_ignored] expected /interest|month|payoff/ in: I can look up any of the 1775 routes in the catalog — try a category like bank bonuses, surveys, or cashback, or name a provider like Fetch.

Or ask me what's the catch with any offer, and I'll give i