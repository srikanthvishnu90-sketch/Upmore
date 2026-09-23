#!/usr/bin/env python3
"""Speed-sweep chunk C: apply reclassifications + document fastest honest path for all routes."""
import json, os, sys

QA = '/home/hatch/workspace/upmore/qa'
ids = json.load(open(f'{QA}/hidden_files/speed-sweep/chunk_C.json'))

MOVES = {
 'R5512': ('today',
   'Credit on account applied at signup.',
   "Hidden fast path: Gault Energy's new-customer offer is given 'as a credit on account upon sign up' (gaultenergy.com/joingault, verified live 2026-09-23) — no waiting period, no delivery timeline. $150 off Bioheat/heating oil for new whole-home-heat automatic delivery + auto-pay customers; $50 off propane for other new auto delivery/autopay signup. Honest framing: it is a one-time account credit (fuel savings), not cash, and only for new customers in Fairfield County CT / parts of Westchester NY."),
 'R0815': ('today',
   'Fee-free trading benefit applies immediately once the friend\'s first bitcoin purchase completes.',
   "Hidden fast path: Strike's official FAQ (strike.me, verified live 2026-09-23): 'Your fee-free benefit applies immediately to your next $500 worth of bitcoin trades' once a friend joins with your code and completes their first bitcoin purchase — usable in-app the same day. Honest framing: this is NOT $500 cash; it is $500 of waived trading fees, worth only a few dollars of fees saved at ~1% per trade."),
 'R0817': ('days',
   'Promo code emailed 24-48 hours after the friend completes their first service.',
   "Hidden fast path: Rover's official help center (support-ca.rover.com, verified live 2026-09-23): 'Once your friend completes their first service, you'll be emailed a $20 promo code within 24-48 hours' — upload to your account for your next booking. Honest framing: Rover credit for future bookings, not cash; the friend must sign up via your link AND complete their first service first."),
 'R0811': ('days',
   'Rewards deposited to MoneyLion Spend accounts within 14 days of completing the stipulated actions.',
   "Hidden fast path: official MoneyLion referral terms (moneylion.com/referrals-terms-and-conditions/): the $5 tier is cash credited to each side's MoneyLion Spend account 'within fourteen (14) days of completing the stipulated action(s)' — account opening alone qualifies. The full $55 per side needs the friend to route real payroll ($100+ twice) within 60 days; that half stays slow."),
 'R6358': ('days',
   '$25 renewal credit appears in the account 15 days after the friend\'s activation.',
   "Hidden fast path: Ultra Mobile's official refer page (ultramobile.com/refer/): both sides get $25 toward plan renewal once a referred friend activates and purchases a plan, with the referrer's credit appearing '15 days after the friend's activation' — no 60/90-day good-standing tail. Honest framing: renewal credit only (not cash), capped at $100/year, friend must stay active."),
 'R6359': ('days',
   'Friend\'s $20 credit lands at activation/port-in; referrer\'s $20 within 1-7 business days of friend activation.',
   "Hidden fast path: H2O Wireless official blog (h2owireless.com, verified live 2026-09-23): 'When your referred friend activates their H2O Wireless service, your rewards credit will be received within 1-7 business days.' Friend's $20 lands at activation/port-in. Honest framing: H2O Rewards credit for refills only, not cash."),
}

BLOCKERS = {
 'energy': ("Structural blocker: the provider's terms set a good-standing / active-service waiting period "
   "(days to months of bills/deliveries) before any reward posts — enrolling faster never shortens that window. "
   "Watch for forfeiture: missed payment or cancellation during the window kills both sides."),
 'rebate': ("Structural blocker: utility rebate processing + check/card delivery timelines are set by the program "
   "(typically 4-8 weeks; some publish 'up to 30 days'); an online claim is the fastest path and still lands inside "
   "that window. Where the evidence notes an instant in-store / point-of-sale discount alternative, that is same-day "
   "savings on the purchase (not cash) — it cannot be stacked with the mail-in rebate."),
 'telecom': ("Structural blocker: telecom promos require an active-service waiting period (30-90 days of good "
   "standing) and pay as bill credits, prepaid cards, or long-term credit spreads per provider terms; nothing you "
   "do at signup shortens the waiting period."),
 'referral': ("Structural blocker: the reward unlocks only after the referred friend completes the qualifying action "
   "(purchase, account opening, service completion), and payout follows the program's stated timeline after that trigger."),
 'directory': ("Structural blocker: this route is a directory of offers, not a single payment. Actual rebates pay per "
   "program: typically 4-8 weeks mail-in/online, or instant point-of-sale discounts in-store. These are purchase discounts "
   "(savings on planned spending), not cash income."),
 'assistance': ("Structural blocker: assistance/income-qualified programs pay the vendor directly or as bill credits on "
   "their own schedule — there is no cash acceleration path; these are not income."),
}

def cluster(rid):
    if rid.startswith('R03'): return 'directory'
    if rid in ('R0323',) : return 'assistance'
    if rid.startswith('R075') or rid.startswith('R076') or rid.startswith('R077') or (rid.startswith('R078') and rid not in ('R0781','R0786','R0787','R0788','R0794')): return 'rebate'
    if rid in ('R0323','R0777','R0779','R0778','R0781'): return 'assistance'
    if rid.startswith('R119') or rid.startswith('R634') or rid.startswith('R635') or rid.startswith('R636') or rid.startswith('R637') or rid.startswith('R638') or rid.startswith('R639'): return 'telecom'
    return 'referral'

# rebate range fixups: telecom-typed rows in R078x
TELECOM_IN_REBATE = {'R0786','R0787','R0788','R0794'}
for t in list(ids):
    pass

stats = {'moved': 0, 'kept': 0, 'missing': []}
for rid in ids:
    path = f'{QA}/verification/{rid}.json'
    if not os.path.exists(path):
        stats['missing'].append(rid); continue
    e = json.load(open(path))
    timing = (e.get('timing') or '').replace('\n',' ').strip()
    if rid in MOVES:
        new, when, rationale = MOVES[rid]
        e['speed'] = new
        e['when_cash_arrives'] = when
        e['maximize'] = rationale
        hist = e.get('speed_history') or []
        hist.append({"date":"2026-09-23","from":"weeks","to":new,"rationale":rationale})
        e['speed_history'] = hist
        stats['moved'] += 1
    else:
        cl = cluster(rid)
        if rid in TELECOM_IN_REBATE: cl = 'telecom'
        if rid in ('R0777','R0779','R0781','R0778'): cl = 'assistance'
        e['speed'] = 'weeks'
        e['when_cash_arrives'] = timing if timing else 'Per verified official terms; no payout timeline published.'
        fastest = timing if timing else 'No payout timeline published in official terms.'
        e['maximize'] = f"Fastest honest path: {fastest} {BLOCKERS[cl]}"
        stats['kept'] += 1
    json.dump(e, open(path,'w'), indent=1, ensure_ascii=False)

print(stats)
