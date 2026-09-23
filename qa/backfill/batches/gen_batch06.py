"""Generate batch-06.json backfill fills for Energy Switching + Telecom Promo routes.
All fills are grounded ONLY in the route's own fields (provider/url, what, reward,
requirements, payout_timing, payout_value_note, catches, steps, difficulty, category).
Never invents payout numbers, client names, availability claims, or guarantees.
"""
import json, re

SUBS = {'www', 'support', 'shopping', 'cms', 'residential', 'eflviewer', 'home', 'help', 'my'}
TLDS = {'com', 'net', 'org', 'io', 'us', 'ca', 'uk', 'co', 'biz', 'info', 'energy'}

def stripq(s):
    s = (s or '').strip()
    if len(s) >= 2 and s[0] == "'" and s[-1] == "'":
        s = s[1:-1].strip()
    if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        s = s[1:-1].strip()
    return s.strip()

def titlecase(p):
    return ' '.join(w.capitalize() for w in p.split())

def disp(r):
    # Provider display name: grounded in url host (fixes slug-only provider values);
    # R1192's "Share" slug -> Cox, grounded in its requirements text.
    if r['id'] == 'R1192':
        return 'Cox'
    u = (r.get('url') or '').strip()
    u = re.sub(r'^official_url\s+', '', u)
    m = re.search(r'https?://([^/\s:]+)', u)
    host = m.group(1) if m else ''
    labels = host.split('.')
    while len(labels) > 1 and labels[-1].lower() in TLDS:
        labels.pop()
    while len(labels) > 1 and labels[0].lower() in SUBS:
        labels.pop(0)
    name = titlecase(' '.join(labels).replace('-', ' ').replace('_', ' '))
    if name:
        return name
    p = (r.get('provider') or '').strip()
    p = re.sub(r'^official_url\s+', '', p).split('/')[0].split(':')[0]
    return titlecase(p.replace('-', ' ').replace('_', ' '))

REF_OVERRIDES = {'R5502', 'R6396', 'R6399'}  # referral mechanics, no "refer" keyword in text

def flavor(r):
    if r['id'] in REF_OVERRIDES:
        return 'referral'
    t = ' '.join([r.get('what') or '', r.get('reward') or '', r.get('requirements') or '']).lower()
    if re.search(r'\brefer', t):
        return 'referral'
    if re.search(r'\bfriend\b', t):
        return 'referral'
    return 'switch'

def recurring(r):
    t = ' '.join([r.get('what') or '', r.get('reward') or '', r.get('payout_timing') or '']).lower()
    return bool(re.search(r'per billing cycle|each billing cycle|monthly bill credit|over the course of|increments', t))

def sentences_from(fields):
    out = []
    for f in fields:
        for c in (f if isinstance(f, list) else [f]):
            if isinstance(c, dict):
                c = c.get('text')
            s = stripq(c)
            if s:
                out.append(s)
    return out

ACCEPT_KW = ['enroll', 'active', 'good standing', 'qualifying', 'activat', 'install',
             'stay', 'remain', 'sign up', 'switch', 'usage', 'deliver', 'new customer',
             'purchas', 'plan of', 'months or longer', 'month agreement', 'bill current',
             'on-time', 'paid-in-full', 'tank filled', 'first delivery', 'service begins',
             'order', 'link', 'code', 'promo', 'referral', 'new users']

REWARDFORM_KW = ['not cash', 'no cash', 'not redeemable', 'never income', 'not income',
                 'savings on planned', 'framed as savings', 'not paid as cash',
                 'not wage income', 'offsets planned']

def what_gets_accepted(r):
    picks = []
    for c in sentences_from([r.get('catches')]):
        cl = c.lower()
        if any(k in cl for k in REWARDFORM_KW):
            continue  # reward-form notes belong in costs_and_unpaid_time
        if len(c) <= 280 and any(k in cl for k in ACCEPT_KW):
            if c not in picks:
                picks.append(c)
        if len(picks) == 2:
            break
    req = stripq(r.get('requirements') or '')
    if req and len(req) <= 320 and req not in picks:
        picks.append(req)
    if picks:
        return '; '.join(picks[:2])
    # fallback: first sentence of reward/what describing the qualifying event
    for f in (r.get('reward'), r.get('what')):
        s = stripq(f)
        if s:
            first = re.split(r'(?<=[.!?])\s', s)[0]
            if len(first) <= 300:
                return first
    return None

COST_KW = ['fee', 'minute', 'hour', 'tax', 'cost', 'charge', 'termination', 'deposit',
           'non-transferable', 'not cash', 'no cash', 'never cash', 'not paid as cash',
           'credit check', 'paperless',
           'auto-pay', 'autopay', 'cannot be combined', 'no other value', 'forfeit',
           'breakage', 'refund', 'approval', 'paid-in-full', 'paper-based',
           'print-and-mail', 'mail-in', 'slower']

def costs_and_unpaid_time(r, accepted_text=''):
    picks = []
    for c in sentences_from([r.get('catches')]):
        cl = c.lower()
        if len(c) <= 240 and any(k in cl for k in COST_KW):
            if c not in picks and c not in accepted_text:
                picks.append(c)
        if len(picks) == 2:
            break
    for s in sentences_from([r.get('steps') or []]):
        sl = s.lower()
        if re.search(r'\d+\s*(minute|hour)', sl) and len(s) <= 200:
            t = s if not s.endswith('.') else s
            if t not in picks:
                picks.append(t)
            break
    return '; '.join(picks) if picks else None

TERRITORY_KW = ['footprint', 'service area', 'service territory', 'coverage area',
                'where available', 'in select', 'govx', 'military', 'first responder',
                'members only', 'invitation-only', 'residents of', 'northern ireland',
                'illinois excluded', 'not applicable to']

def anyone_can_do(r, fl):
    if r['category'] == 'Energy Switching':
        return False  # template default; all need territory residency and/or existing-customer status
    if fl == 'referral':
        return False  # refer-a-friend requires existing-customer status
    t = ' '.join([r.get('requirements') or '', r.get('payout_value_note') or ''] + (r.get('catches') or [])).lower()
    if any(k in t for k in TERRITORY_KW):
        return False
    return True

def repeatable(r, fl, rec):
    txt = ' '.join([r.get('reward') or '', r.get('what') or ''] + (r.get('catches') or []))
    if fl == 'referral':
        if re.search(r'no limit', txt, re.I):
            cad = 'per successful referral, no stated referral limit'
        else:
            m = re.search(r'up to \$[\d,]+ (?:a|per) year', txt, re.I)
            cad = ('per successful referral, capped at ' + m.group(0).split('up to ')[1]) if m else 'per successful referral'
        return {'value': True, 'cadence': cad}
    if rec:
        return {'value': True, 'cadence': 'each qualifying billing cycle while enrolled on the plan'}
    if r['category'] == 'Telecom Promo':
        return {'value': False, 'cadence': 'once per new line/account'}
    return {'value': False, 'cadence': 'once per new customer enrollment'}

def work_available(r, fl, rec):
    if fl == 'referral':
        if r['category'] == 'Energy Switching':
            return ('No guaranteed earnings — you earn only when a referred customer completes '
                    'the qualifying enrollment and stays in good standing; demand is your own network.')
        return ('No guaranteed earnings — you earn only when someone you refer completes the '
                'qualifying application or activation; demand is your own network.')
    if rec:
        return ('Recurring bill credit each qualifying billing cycle while you stay enrolled on the plan — '
                'only in the supplier\'s service territory; a discount on your own bill, not income.')
    if r['category'] == 'Energy Switching':
        return ('One-time bill credit for enrolling your own supply — only available to customers in '
                'the supplier\'s service territory; not ongoing income.')
    return ('One-time per new line/account — you must order the qualifying plan and activate service; '
            'not ongoing work.')

def demand_side(r, fl, d):
    if r['category'] == 'Energy Switching':
        if fl == 'referral':
            return (f"Demand is {d}'s customer-acquisition need in its service territory — it pays referral "
                    f"credits when someone you refer enrolls; the source of referrals is your own network.")
        return (f"Demand is {d}'s need to acquire supply customers in its service territory; the bill credit "
                f"is its acquisition cost, paid as a discount on your own bill.")
    if fl == 'referral':
        return (f"{d} pays referral rewards out of its subscriber-acquisition budget; demand is your own network — "
                f"people willing to sign up or activate through your referral link.")
    return (f"{d} funds the promotion to acquire subscribers; the offer lives on the carrier's official site.")

def who_pays(r, d):
    if r['category'] == 'Energy Switching':
        return f"{d}, an energy supplier paying bill credits for new-customer acquisition."
    return f"{d}, a telecom carrier funding a subscriber-acquisition promotion."

def build(r):
    d = disp(r)
    fl = flavor(r)
    rec = recurring(r)
    fill = r['_fill']
    out = {'route_id': r['id']}
    vals = {
        'who_pays': who_pays(r, d),
        'who_qualifies': stripq(r.get('requirements')) or None,
        'work_available': work_available(r, fl, rec),
        'what_gets_accepted': what_gets_accepted(r),
        'costs_and_unpaid_time': None,
        'when_cash_arrives': stripq(r.get('payout_timing')) or None,
        'repeatable': repeatable(r, fl, rec),
        'demand_side': demand_side(r, fl, d),
        'ease': (r.get('difficulty') or 'Easy').lower(),
        'anyone_can_do': anyone_can_do(r, fl),
    }
    accepted_text = what_gets_accepted(r) or ''
    vals['costs_and_unpaid_time'] = costs_and_unpaid_time(r, accepted_text)
    for f in fill:
        out[f] = vals.get(f)
    return out, (d, fl, rec)

if __name__ == '__main__':
    routes = json.load(open('batch-06-assign.json'))
    out = []
    meta = []
    for r in routes:
        o, m = build(r)
        out.append(o)
        meta.append((r['id'],) + m)
    json.dump(out, open('batch-06.json', 'w'), indent=1, ensure_ascii=False)
    print('wrote', len(out))
    from collections import Counter
    print(Counter((m[2], m[3]) for m in meta))
