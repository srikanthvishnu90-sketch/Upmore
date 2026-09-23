#!/usr/bin/env python3
"""Apply speed-audit decisions to evidence JSONs. Reads /tmp/a1_decisions.json
(decisions computed by apply_a1.py from DECISIONS + weeks_reason rules)."""
import json

QADIR = '/home/hatch/workspace/upmore/qa'
chunk = json.load(open(f'{QADIR}/hidden_files/speed-sweep/chunk_A1.json'))
dec = json.load(open('/tmp/a1_decisions.json'))

# Full content for reclassified routes lives in apply_a1's namespace; re-import it.
import importlib.util
spec = importlib.util.spec_from_file_location('a1', f'{QADIR}/hidden_files/speed-sweep/apply_a1.py')
# apply_a1 runs its triage on import; reuse its decisions dict by re-running logic is fine.
# Instead, we re-declare: read content from the module's TODAY/DAYS dicts.
import types
src = open(f'{QADIR}/hidden_files/speed-sweep/apply_a1.py').read()
mod = types.ModuleType('a1dec')
mod.__dict__['__name__'] = 'a1dec'
# stub out file writes at the end: only exec up to the decisions loop
cut = src.index("json.dump({k: {'new'")
exec(src[:cut], mod.__dict__)
CONTENT = {}
CONTENT.update(mod.TODAY)
CONTENT.update(mod.DAYS)

changed, confirmed = [], []
for rid in chunk:
    p = f'{QADIR}/verification/{rid}.json'
    d = json.load(open(p))
    new = dec[rid]['new']
    rationale = dec[rid]['rationale']
    if rid in CONTENT:
        wca = CONTENT[rid]['wca']
        maximize = CONTENT[rid]['maximize']
    else:
        # weeks routes: recompute via module helpers
        timing = str(d.get('timing') or '')
        catches = str(d.get('catches') or '')
        pq = str(d.get('payout_quote') or '')
        reason = mod.weeks_reason(timing, catches)
        wca = f"Per official terms: {timing} — {reason}."
        maximize = mod.weeks_maximize(timing, catches, pq)
    d['speed'] = new
    d['when_cash_arrives'] = wca
    d['maximize'] = maximize
    hist = d.get('speed_history') or []
    hist.append({"date": "2026-09-23", "from": "weeks", "to": new, "rationale": rationale})
    d['speed_history'] = hist
    json.dump(d, open(p, 'w'), indent=2)
    (changed if new != 'weeks' else confirmed).append(rid)

json.dump(changed, open('/tmp/a1_changed.json', 'w'))
print('evidence updated:', len(chunk), '| changed:', len(changed), '| confirmed weeks:', len(confirmed))
print('changed:', changed)
