#!/usr/bin/env python3
"""Backfill numerics.json for all 1500 verified routes from evidence files.
Applies adjudicated corrections for 3 known mismatches. Computes earn_ratio.
Writes qa/numerics.json with earn_ratio per route; prints a rank-ordered list.
Idempotent.
"""
import json, os, sys

BASE = "/home/hatch/workspace/upmore"
NUM = f"{BASE}/qa/numerics.json"
VER = f"{BASE}/qa/verification"

sys.path.insert(0, f"{BASE}/qa")
from db import req

# adjudicated corrections: evidence payout (official terms) is authoritative
FIXES = {
    "R0045": (400.0, 400.0, "evidence payout 400 matches DB payout_text $400; was 1000"),
    "R0054": (400.0, 400.0, "evidence payout_quote 'Earn $400' from official Regions terms; was 300"),
    "R0646": (300.0, 300.0, "evidence payout 300 matches DB payout_text $300; was 1000"),
}

# verified IDs from DB (source of truth)
vids = []
_offset = 0
while True:
    st, batch = req("GET", f"/rest/v1/routes?select=route_id&status=eq.verified&limit=1000&offset={_offset}")
    vids.extend(r["route_id"] for r in batch)
    _offset += 1000
    if len(batch) < 1000:
        break
vids = sorted(set(vids))
print("verified in DB:", len(vids))

num = json.load(open(NUM))
added = fixed = 0
problems = []

for rid in vids:
    e = num.get(rid)
    if rid in FIXES:
        if e:
            e["payout_min"], e["payout_max"] = FIXES[rid][0], FIXES[rid][1]
            e["numeric_basis"] = (e.get("numeric_basis") or "") + " | ADJUDICATED: " + FIXES[rid][2]
            fixed += 1
        else:
            problems.append((rid, "fix target missing from numerics"))
        continue
    if e and all(e.get(k) is not None for k in ("payout_min", "payout_max", "time_min_minutes", "time_max_minutes")):
        continue
    p = f"{VER}/{rid}.json"
    if not os.path.exists(p):
        problems.append((rid, "no evidence file and no numerics"))
        continue
    d = json.load(open(p))
    if d.get("verdict") not in ("verify", "verified"):
        problems.append((rid, f"evidence verdict={d.get('verdict')}"))
        continue
    keys = ("payout_min_usd", "payout_max_usd", "time_min_minutes", "time_max_minutes")
    if not all(d.get(k) is not None for k in keys):
        problems.append((rid, "evidence missing numeric keys"))
        continue
    num[rid] = {
        "payout_min": d["payout_min_usd"],
        "payout_max": d["payout_max_usd"],
        "payout_value_note": d.get("payout_value_note"),
        "time_min_minutes": d["time_min_minutes"],
        "time_max_minutes": d["time_max_minutes"],
        "numeric_basis": d.get("numeric_basis"),
    }
    added += 1

print(f"added={added} fixed={fixed} problems={len(problems)}")
for p in problems[:20]:
    print("PROBLEM:", p)

# validate + compute earn_ratio for every verified route
KEYS = ("payout_min", "payout_max", "time_min_minutes", "time_max_minutes")
order = []
for rid in vids:
    e = num.get(rid)
    assert e is not None, f"{rid} missing from numerics"
    for k in KEYS:
        assert e.get(k) is not None, f"{rid}.{k} is null"
        assert isinstance(e[k], (int, float)) and e[k] >= 0, f"{rid}.{k} bad value {e[k]!r}"
    assert e["payout_max"] >= e["payout_min"], f"{rid} payout range inverted"
    assert e["time_max_minutes"] >= e["time_min_minutes"], f"{rid} time range inverted"
    pm = (e["payout_min"] + e["payout_max"]) / 2
    tm = (e["time_min_minutes"] + e["time_max_minutes"]) / 2
    ratio = pm / max(1.0, tm)
    e["earn_ratio"] = ratio
    order.append((rid, ratio, pm, tm))

# rank strictly ratio-descending; ties -> higher payout_mid first
order.sort(key=lambda t: (-t[1], -t[2], t[0]))
ranks = {rid: i + 1 for i, (rid, *_rest) in enumerate(order)}
assert len(set(ranks.values())) == len(vids) == 1500, "rank assignment broken"
json.dump(num, open(NUM, "w"), indent=1)
json.dump(ranks, open(f"{BASE}/qa/hidden_files/ranks-1500.json", "w"), indent=1)

top = order[0]
print(f"top1: {top[0]} ratio={top[1]:.2f} $/min payout_mid={top[2]} time_mid={top[3]}")
bot = order[-1]
print(f"last: {bot[0]} ratio={bot[1]:.4f} $/min payout_mid={bot[2]} time_mid={bot[3]}")
avg_time = sum(t[3] for t in order) / len(order)
print(f"avg time_mid (working): {avg_time:.4f} min")
print("numerics.json written with", len(num), "entries")
