#!/usr/bin/env python3
"""Dedupe helper for discovery workers: print existing catalog hits for a provider name."""
import json, sys, glob, re

q = " ".join(sys.argv[1:]).lower().strip()
if not q:
    print("usage: dedupe-check.py <provider name>"); sys.exit(1)

d = json.load(open("/home/hatch/workspace/upmore/src/data/upmore-data.json"))
hits = [r for r in d["routes"]
        if q in r["provider"].lower() or r["provider"].lower() in q or q in r.get("method", "").lower()]
for r in hits[:30]:
    print(f'{r["id"]} | {r["provider"]} | {r["category"]} | {r["method"]} | {r["status"]}')
print(f"-- {len(hits)} catalog hits")

ev = []
for f in glob.glob("/home/hatch/workspace/upmore/qa/verification/R*.json"):
    try:
        j = json.load(open(f))
    except Exception:
        continue
    c1 = ""
    try:
        c1 = j["critical"]["c1"]["evidence"] or ""
    except Exception:
        pass
    if q in c1.lower() or q in (j.get("official_url") or "").lower():
        ev.append((j.get("route_id"), j.get("verdict"), (j.get("official_url") or "")[:80]))
for rid, v, u in sorted(ev)[:20]:
    print(f"evidence {rid} verdict={v} {u}")
print(f"-- {len(ev)} evidence-file hits")
