#!/usr/bin/env python3
"""Patch src/data/upmore-data.json with the DB's verified route data (fast client).
Whitelist lives in this file's IDS list."""
import json, sys, re
sys.path.insert(0, "/home/hatch/workspace/upmore/qa")
from db import req

IDS = None  # set below from patch-app-data.py's list
src = open("/home/hatch/workspace/upmore/qa/patch-app-data.py").read()
IDS = re.findall(r'"(R\d{3,4})"', src)
print("whitelist:", len(IDS))

st, rows = req("GET", "/rest/v1/routes?status=eq.verified&select=route_id,status,verified_at,payout_text,payout_timing,catches,steps,provider_url,min_age,geo_notes&limit=1000")
db = {r["route_id"]: r for r in rows if r["route_id"] in IDS}
print("fetched verified in whitelist:", len(db))

path = "/home/hatch/workspace/upmore/src/data/upmore-data.json"
d = json.load(open(path))
n = 0
for r in d["routes"]:
    rid = r["id"]
    if rid in db:
        v = db[rid]
        r["status"] = "verified"
        r["reward"] = v.get("payout_text") or r["reward"]
        r["payout_timing"] = v.get("payout_timing") or r["payout_timing"]
        r["url"] = v.get("provider_url") or r["url"]
        r["catches"] = v.get("catches") or r["catches"]
        r["steps"] = [{"n": i + 1, "text": s.get("text", ""), "who": "Upmore",
                       "done_when": s.get("done_when", ""), "warns": s.get("warn", "")}
                      for i, s in enumerate(v.get("steps") or [])]
        n += 1
json.dump(d, open(path, "w"), indent=1)
print("patched routes:", n)
missing = [i for i in IDS if i not in db]
print("whitelist IDs not verified in DB:", missing)
