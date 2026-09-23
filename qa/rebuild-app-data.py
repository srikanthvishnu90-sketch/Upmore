#!/usr/bin/env python3
"""Rebuild src/data/upmore-data.json from the DB:
- sync every card's verified fields + status from the DB (no whitelist)
- append newly verified discovery routes as full cards
- recompute categories with counts and step totals
Idempotent: re-running produces the same file.
"""
import json, sys, re, os
sys.path.insert(0, "/home/hatch/workspace/upmore/qa")
from db import req

METHOD = {"Bank Bonus": "Bank bonus", "Credit Card Bonus": "Credit card welcome offer",
          "Rebate/Incentive": "Utility rebate", "App Referral": "Referral bonus"}

def time_to_first(timing):
    t = (timing or "").lower()
    if any(k in t for k in ("instant", "point of sale", "at the register", "minutes", "hours")):
        return "Minutes to hours"
    if "day" in t:
        return "Days to weeks"
    if any(k in t for k in ("week", "month", "90 days", "6-8 weeks")):
        return "Weeks to months"
    return "Weeks to months"

def app_steps(db_steps):
    return [{"n": i + 1, "text": s.get("text", ""), "who": "Upmore",
             "done_when": s.get("done_when", ""), "warns": s.get("warn", "")}
            for i, s in enumerate(db_steps or [])]

st, rows = req("GET", "/rest/v1/routes?select=*&limit=1500")
dbm = {r["route_id"]: r for r in rows}

path = "/home/hatch/workspace/upmore/src/data/upmore-data.json"
d = json.load(open(path))
cards = {r["id"]: r for r in d["routes"]}

synced = appended = 0
for rid, v in dbm.items():
    c = cards.get(rid)
    if c is None:
        # new discovery card
        evf = f"/home/hatch/workspace/upmore/qa/verification/{rid}.json"
        elig = ""
        if os.path.exists(evf):
            try:
                elig = json.load(open(evf)).get("eligibility") or ""
            except Exception:
                pass
        cat = v.get("category") or "Other Online"
        c = {
            "id": rid,
            "category": cat,
            "provider": v.get("provider") or "",
            "method": METHOD.get(cat, cat),
            "what": (v.get("payout_text") or "")[:300],
            "reward": v.get("payout_text") or "",
            "requirements": (elig or v.get("geo_notes") or "")[:500],
            "payout_timing": v.get("payout_timing") or "",
            "catches": v.get("catches") or [],
            "url": v.get("provider_url") or "",
            "cash_or_credit": "Cash or usable value",
            "earnings_class": "Count only actual received cash",
            "lane": v.get("lane") or "Standard",
            "status": v.get("status") or "unverified",
            "steps": app_steps(v.get("steps")),
            "tier": v.get("difficulty") or "Easy",
            "difficulty": v.get("difficulty") or "Easy",
            "time_to_first": time_to_first(v.get("payout_timing")),
            "rank": None,
        }
        d["routes"].append(c)
        cards[rid] = c
        appended += 1
    # sync verified fields + status from DB for every card
    c["status"] = v.get("status") or "unverified"
    if v.get("status") == "verified":
        c["reward"] = v.get("payout_text") or c["reward"]
        c["payout_timing"] = v.get("payout_timing") or c["payout_timing"]
        c["url"] = v.get("provider_url") or c["url"]
        c["catches"] = v.get("catches") or c["catches"]
        c["steps"] = app_steps(v.get("steps")) or c["steps"]
        c["provider"] = v.get("provider") or c["provider"]
        synced += 1

# recompute categories
from collections import Counter
cc = Counter(r["category"] for r in d["routes"])
stepsum = Counter()
for r in d["routes"]:
    stepsum[r["category"]] += len(r.get("steps") or [])
d["categories"] = [{"name": k, "count": cc[k], "steps": stepsum[k]} for k in sorted(cc)]

n = len(d["routes"])
nv = sum(1 for r in d["routes"] if r.get("status") == "verified")
d["version"] = f"{n}-route catalog 2026-09-23 ({nv} verified)"

json.dump(d, open(path, "w"), indent=1)
print(f"routes={n} verified={nv} synced={synced} appended={appended}")
