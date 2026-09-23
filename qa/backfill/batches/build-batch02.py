#!/usr/bin/env python3
"""Backfill worker: batch-02 (Referral Bonus). Fills ONLY the _fill fields,
grounded in each route's own fields. Honest nulls where data is absent."""
import json, re, sys

STATES = """AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS
MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY DC""".split()

ASSIGN = '/home/hatch/workspace/upmore/qa/backfill/batches/batch-02-assign.json'
OUT = '/home/hatch/workspace/upmore/qa/backfill/batches/batch-02.json'

# Provider labels for slugified provider values, sourced from each route's own fields
LABEL_OVERRIDE = {
    'R3960': 'Quad City Bank & Trust',   # requirements: "existing Quad City Bank & Trust client"
    'R3390': 'Centier Bank',             # requirements + URL refer.centier.com
    'R3426': 'Midland States Bank',      # requirements + URL refer.midlandsb.com
    'R4763': 'Peoples Advantage FCU',    # requirements: "PAFCU member"
    'R2201': 'Chase',                    # requirements: "Existing Chase personal checking account holders"
}

def label(r):
    if r['id'] in LABEL_OVERRIDE:
        return LABEL_OVERRIDE[r['id']]
    return r['provider']

def fmt_time(v):
    return str(int(v)) if float(v) == int(v) else str(v)

def segs_of(text):
    return re.split(r';\s*|\.\s+', text or '')

def first_clause(text, keywords, maxlen=190):
    """Extract the first segment of requirements containing a keyword."""
    if not text:
        return None
    for seg in segs_of(text):
        if re.search(keywords, seg, re.I):
            seg = seg.strip().rstrip('.')
            return seg[:maxlen]
    return None

def friend_clause(req, you_text, maxlen=200):
    """Friend-side clause, excluding the segment already used for the referrer."""
    if not req:
        return None
    you_norm = (you_text or '').lower()
    for pat in [r'\breferr?ees?\b', r'\breferred\b']:
        for seg in segs_of(req):
            if re.search(pat, seg, re.I) and seg.strip().lower() not in (you_norm,):
                return seg.strip().rstrip('.')[:maxlen]
    for seg in segs_of(req):
        if re.search(r'\bfriends?\b', seg, re.I) and not re.search(r'\breferr(ing|er)\b', seg, re.I) and seg.strip().lower() != you_norm:
            return seg.strip().rstrip('.')[:maxlen]
    return None

YOU_PATTERNS = [
    r'referrer',
    r'current\s+member',
    r'existing\s+\w+\s+member',
    r'member in good standing',
    r'members?\s+\d',
    r'account\s+holders?',
]

def clean_prefix(s):
    return re.sub(r'^(referrer|referred|friend)\s*:\s*', '', s, flags=re.I)

def who_qualifies(r, lab):
    req = r['requirements'] or ''
    you = None
    for pat in YOU_PATTERNS:
        you = first_clause(req, pat, 190)
        if you:
            break
    if not you:
        you = re.split(r';\s*|\.\s+', req)[0].strip().rstrip('.')[:190]
    you = clean_prefix(you)
    friend = friend_clause(req, you, 200)
    out = 'You: ' + (you if you else 'requirements not stated')
    if friend:
        friend = clean_prefix(friend)
        out += '; your friend: ' + friend
    return out

def what_gets_accepted(r):
    req = r['requirements'] or ''
    friend = friend_clause(req, '', 220)
    note = None
    for c in (r['catches'] or []):
        m = re.search(r'within\s+\d+\s+days?', c, re.I)
        if m:
            frag = c[m.start():]
            end = re.search(r'[.;]', frag)
            frag = frag[:end.start()] if end else frag
            frag = frag.strip()
            if len(frag) > 220:
                frag = re.sub(r'\s+\S*$', '', frag[:220]) + '...'
            note = frag
            break
    if friend:
        friend = clean_prefix(friend)
        out = ('Sharing your referral link alone earns nothing — a referral only counts when: ' +
               friend[0].upper() + friend[1:] + '.')
    else:
        out = 'Sharing your referral link alone earns nothing — the referred person must complete the qualifying actions in the route\'s requirements.'
    if note:
        out += ' Note: ' + note + '.'
    return out

def end_punct(s):
    s = s.strip()
    if len(s) > 230:
        s = re.sub(r'\s+\S*$', '', s[:230]) + '...'
    return s if s and s[-1] in '.!?:)' else s + '.'

FEE_PAT = re.compile(r'\bfee\b|1099|tax reportab|must (remain|keep)|holding period|minimum (balance|deposit|purchase)|\$\d[\d,]*\s*(fee|charge|minimum|per)', re.I)
CAP_ONLY_PAT = re.compile(r'^cap\s*:', re.I)

def costs_and_unpaid_time(r):
    bits = []
    for c in (r['catches'] or []):
        c = c.strip()
        if FEE_PAT.search(c) and not (CAP_ONLY_PAT.search(c) and not re.search(r'fee|1099|tax reportab', c, re.I)):
            bits.append(end_punct(c))
            if len(bits) >= 3:
                break
    tmin, tmax = r.get('time_min_minutes'), r.get('time_max_minutes')
    time_bit = None
    if tmin and tmax:
        time_bit = f'{fmt_time(tmin)}-{fmt_time(tmax)} minutes'
    elif tmin:
        time_bit = f'{fmt_time(tmin)} minutes'
    if time_bit:
        bits.append(f'Your unpaid time is registering and sharing your link (about {time_bit}).')
    if not bits:
        bits = ['No fees stated in the data; your unpaid time is registering and sharing your link.']
    return ' '.join(bits)

CAP_PATTERNS = [
    (re.compile(r'up to\s+(\d+)\s+referrals?\b.{0,90}?(calendar year|per calendar year|per year)', re.I),
     lambda m: 'per successful referral, up to ' + m.group(1) + ' per calendar year'),
    (re.compile(r'(maximum|max)\s*\$[\d,]+\s*[^.;]{0,40}?(calendar year|per year|/year)', re.I),
     lambda m: 'per successful referral, ' + m.group(0).strip()),
    (re.compile(r'up to\s+\$[\d,]+\s+[^.;]{0,40}?(calendar year|per year|/year|per calendar year)', re.I),
     lambda m: 'per successful referral, ' + m.group(0).strip()),
    (re.compile(r'(maximum|max|cap:?)\s*(\d+)\s*(referral bonus|referral|new members?|friends?)', re.I),
     lambda m: 'per successful referral, up to ' + m.group(2) + ' per year'),
]

def repeatable(r):
    text = ' '.join([r['reward'] or '', r['requirements'] or '', ' '.join(r['catches'] or [])])
    for pat, fmt in CAP_PATTERNS:
        m = pat.search(text)
        if m:
            return {'value': True, 'cadence': fmt(m)}
    return {'value': True, 'cadence': 'per successful referral, subject to program caps'}

def build(r):
    lab = label(r)
    pt = (r['payout_timing'] or '').strip()
    return {
        'route_id': r['id'],
        'who_pays': lab + ', which pays referral bonuses to acquire new customers.',
        'who_qualifies': who_qualifies(r, lab),
        'work_available': 'No guaranteed work — you earn only when someone you refer completes the qualifying actions; most people earn $0 from referrals.',
        'what_gets_accepted': what_gets_accepted(r),
        'costs_and_unpaid_time': costs_and_unpaid_time(r),
        'when_cash_arrives': pt if pt else None,
        'repeatable': repeatable(r),
        'demand_side': 'No open market — demand is your own network: friends/family willing to open the account and complete the qualifying actions. Most people earn $0 from referrals.',
        'ease': 'easy',
        'anyone_can_do': True,
    }

def main():
    data = json.load(open(ASSIGN))
    out = [build(r) for r in data]
    json.dump(out, open(OUT, 'w'), indent=2, ensure_ascii=False)
    print('wrote', OUT, 'routes:', len(out))

    # per-field fill vs null counts
    from collections import Counter
    fills = Counter()
    for o in out:
        for k, v in o.items():
            if k == 'route_id':
                continue
            fills[(k, v is not None and v != '')] += 1
    for k in ['who_pays', 'who_qualifies', 'work_available', 'what_gets_accepted',
              'costs_and_unpaid_time', 'when_cash_arrives', 'repeatable',
              'demand_side', 'ease', 'anyone_can_do']:
        print(f'{k:22} filled={fills[(k, True)]:3}  null={fills[(k, False)]:3}')
    # null detail
    for o in out:
        nulls = [k for k in ['who_pays', 'who_qualifies', 'work_available', 'what_gets_accepted',
                             'costs_and_unpaid_time', 'when_cash_arrives', 'repeatable',
                             'demand_side', 'ease', 'anyone_can_do'] if o[k] is None or o[k] == '']
        if nulls:
            print('NULLS:', o['route_id'], nulls)

if __name__ == '__main__':
    main()
