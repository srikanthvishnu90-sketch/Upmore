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

rows = []
_offset = 0
while True:
    st, _batch = req("GET", f"/rest/v1/routes?select=*&limit=1000&offset={_offset}")
    if not _batch:
        break
    rows.extend(_batch)
    _offset += 1000
    if len(_batch) < 1000:
        break
dbm = {r["route_id"]: r for r in rows}

try:
    NUMERICS = json.load(open("/home/hatch/workspace/upmore/qa/numerics.json"))
except Exception:
    NUMERICS = {}

path = "/home/hatch/workspace/upmore/src/data/upmore-data.json"
d = json.load(open(path))
cards = {r["id"]: r for r in d["routes"]}

synced = appended = 0
for rid, v in dbm.items():
    c = cards.get(rid)
    if c is None:
        # new discovery card
        evf = f"/home/hatch/workspace/upmore/qa/verification/{rid}.json"
        elig, ev_rep, ev_max = "", None, None
        if os.path.exists(evf):
            try:
                _ev = json.load(open(evf))
                elig = _ev.get("eligibility") or ""
                ev_rep = _ev.get("repeatable")
                ev_max = _ev.get("maximize")
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
            "affiliate": bool(v.get("affiliate_note")),
            "affiliate_note": v.get("affiliate_note") or "",
            "ios_url": v.get("ios_url") or "",
            "android_url": v.get("android_url") or "",
            "cash_or_credit": "Cash or usable value",
            "earnings_class": "Count only actual received cash",
            "lane": v.get("lane") or "Standard",
            "status": v.get("status") or "unverified",
            "steps": app_steps(v.get("steps")),
            "tier": v.get("difficulty") or "Easy",
            "difficulty": v.get("difficulty") or "Easy",
            "time_to_first": time_to_first(v.get("payout_timing")),
            "speed": v.get("speed") if v.get("speed") in ("today", "days", "weeks") else None,
            "repeatable": ev_rep,
            "maximize": ev_max,
            "rank": None,
        }
        d["routes"].append(c)
        cards[rid] = c
        appended += 1
# attach numeric payout/time fields (verified cards only)
    nu = NUMERICS.get(rid) or {}
    for k in ("payout_min", "payout_max", "payout_value_note",
              "time_min_minutes", "time_max_minutes", "earn_ratio", "numeric_basis"):
        c[k] = nu.get(k)
    # sync verified fields + status from DB for every card
    c["status"] = v.get("status") or "unverified"
    if v.get("speed") in ("today", "days", "weeks"):
        c["speed"] = v["speed"]
    # quick-lane pro-tip fields live in the evidence files; refresh on every rebuild
    if rid >= "R6500":
        _evf = f"/home/hatch/workspace/upmore/qa/verification/{rid}.json"
        if os.path.exists(_evf):
            try:
                _ev = json.load(open(_evf))
                if _ev.get("repeatable") is not None:
                    c["repeatable"] = _ev["repeatable"]
                if _ev.get("maximize"):
                    c["maximize"] = _ev["maximize"]
            except Exception:
                pass
    c["affiliate"] = bool(v.get("affiliate_note"))
    c["affiliate_note"] = v.get("affiliate_note") or ""
    c["ios_url"] = v.get("ios_url") or ""
    c["android_url"] = v.get("android_url") or ""
    c["steps"] = app_steps(v.get("steps")) or c["steps"]
    # 7-field quality framework (quick lanes): sync from DB for every card
    for _k in ("who_pays", "who_qualifies", "work_available", "what_gets_accepted",
               "costs_and_unpaid_time", "when_cash_arrives", "demand_side"):
        if v.get(_k):
            c[_k] = v[_k]
    if v.get("repeatable") is not None:
        c["repeatable"] = v["repeatable"]
    if v.get("status") == "verified":
        c["reward"] = v.get("payout_text") or c["reward"]
        c["payout_timing"] = v.get("payout_timing") or c["payout_timing"]
        c["url"] = v.get("provider_url") or c["url"]
        c["catches"] = v.get("catches") or c["catches"]
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

# Order the whole catalog by earn_ratio descending (verified with a ratio first,
# then verified without a ratio, then unverified in stable order); ties break on
# higher payout midpoint first; assign rank 1..N over verified.
def _payout_mid(r):
    a, b = r.get("payout_min"), r.get("payout_max")
    return (a + b) / 2 if a is not None and b is not None else 0

def _sort_key(r):
    if r.get("status") == "verified" and r.get("earn_ratio"):
        return (0, -(r["earn_ratio"] or 0), -_payout_mid(r))
    if r.get("status") == "verified":
        return (1, 0, 0)
    return (2, 0, 0)

d["routes"].sort(key=_sort_key)
rank = 0
for r in d["routes"]:
    if r.get("status") == "verified":
        rank += 1
        r["rank"] = rank
    else:
        r["rank"] = None

d["version"] = f"{n}-route catalog 2026-09-24 ({nv} verified, ranked by earn rate)"

json.dump(d, open(path, "w"), indent=1)
print(f"routes={n} verified={nv} synced={synced} appended={appended}")
