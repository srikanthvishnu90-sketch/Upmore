#!/usr/bin/env python3
"""PATCH routes table with numeric money/time columns for all 1500 verified routes.
Also fixes R0054 payout_text ($300 -> $400 per verified evidence).
Idempotent (same values re-PATCHed).
"""
import json, sys, time

BASE = "/home/hatch/workspace/upmore"
sys.path.insert(0, f"{BASE}/qa")
from db import req

num = json.load(open(f"{BASE}/qa/numerics.json"))

vids = []
_offset = 0
while True:
    st, batch = req("GET", f"/rest/v1/routes?select=route_id&status=eq.verified&limit=1000&offset={_offset}")
    vids.extend(r["route_id"] for r in batch)
    _offset += 1000
    if len(batch) < 1000:
        break
vids = sorted(set(vids))
print("verified:", len(vids), flush=True)

ok = fail = 0
for i, rid in enumerate(vids):
    e = num[rid]
    body = {
        "payout_min": e["payout_min"],
        "payout_max": e["payout_max"],
        "time_min_minutes": e["time_min_minutes"],
        "time_max_minutes": e["time_max_minutes"],
    }
    st, out = req("PATCH", f"/rest/v1/routes?route_id=eq.{rid}", body)
    if st in (200, 204):
        ok += 1
    else:
        fail += 1
        print("FAIL", rid, st, str(out)[:120])
    if (i + 1) % 250 == 0:
        print(f"patched {i+1}/{len(vids)}", flush=True)

# R0054 payout_text correction: evidence-verified $400 (official Regions terms)
st, out = req("PATCH", "/rest/v1/routes?route_id=eq.R0054",
              {"payout_text": "$400 bonus ($1,000+ ACH direct deposits within 90 days)"})
print("R0054 payout_text fix:", st)
print(f"done ok={ok} fail={fail}")
