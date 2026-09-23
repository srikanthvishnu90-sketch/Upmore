#!/usr/bin/env python3
"""Apply quick-income expansion lanes: INSERT new routes R6500+ (verified) into DB,
log proof rows, including the speed field. Idempotent: existing route_ids PATCHed.
"""
import json, glob, os, sys, datetime
from urllib.parse import urlparse
sys.path.insert(0, "/home/hatch/workspace/upmore/qa")
from db import req

NOW = datetime.datetime.now(datetime.timezone.utc).isoformat()

def host(url):
    try:
        h = urlparse(url).netloc.lower()
        return h[4:] if h.startswith("www.") else h
    except Exception:
        return ""

def provider_of(d):
    off = d.get("official_url") or ""
    h = host(off)
    if h:
        core = h.split(".")[0]
        return core.replace("-", " ").title()
    return d.get("provider") or "Unknown"

def norm_verdict(v):
    v = str(v or "").strip().lower()
    return "verify" if v in ("verify", "verified") else "reject"

def lane_of(rid):
    n = int(rid[1:])
    if 6500 <= n <= 6599: return ("UGC Video", "UGC video task", "Easy", "US only — see eligibility")
    if 6600 <= n <= 6699: return ("User Testing", "Paid user test", "Easy", "US only — see eligibility")
    if 6700 <= n <= 6799: return ("Microtask", "Instant-pay microtask", "Easy", "US only — see eligibility")
    if 6800 <= n <= 6899: return ("Promo Arbitrage", "Signup/deposit promo", "Moderate", "US; state restrictions may apply — see eligibility")
    if 6900 <= n <= 6999: return ("Referral Bonus", "Referral bonus", "Very Easy", "US only — see eligibility")
    if 7000 <= n <= 7099: return ("Buyback/Resale", "Sell/buyback", "Easy", "US only — see eligibility")
    if 7100 <= n <= 7199: return ("Mystery Shopping", "Mystery shop / local task", "Easy", "US only — see eligibility")
    return ("Other Online", "Other", "Easy", "US only")

def proof_exists(route_id, checked_at):
    st, rows = req("GET", f"/rest/v1/proof_log?select=id&route_id=eq.{route_id}&checked_at=eq.{checked_at}")
    return bool(rows)

def log_proof(route_id, checked_at, result, notes, source_url):
    if proof_exists(route_id, checked_at):
        return False
    st, _ = req("POST", "/rest/v1/proof_log",
                {"route_id": route_id, "checked_at": checked_at, "result": result,
                 "notes": notes[:2000], "source_url": (source_url or "")[:2000]})
    return st in (200, 201)

st, dbv = req("GET", "/rest/v1/routes?select=route_id&limit=3000")
existing = {r["route_id"] for r in dbv}

ins = upd = rej = 0
for f in sorted(glob.glob("/home/hatch/workspace/upmore/qa/verification/R*.json")):
    rid = os.path.basename(f)[:5]
    if rid < "R6500":
        continue
    try:
        d = json.load(open(f))
    except (FileNotFoundError, json.JSONDecodeError):
        continue
    v = norm_verdict(d.get("verdict"))
    checked = d.get("checked_at") or NOW
    off = d.get("official_url") or ""
    if v == "reject":
        if log_proof(rid, checked, "rejected",
                     "Quick-lane reject: " + str(d.get("notes") or "")[:400], off):
            rej += 1
        continue
    provider = d.get("provider") or provider_of(d)
    category, method, difficulty, geo = lane_of(rid)
    pq = (d.get("payout_quote") or "").strip()
    payout_text = pq if pq else str(d.get("biggest_catch") or "")[:300]
    steps = [{"text": (s if isinstance(s, str) else s.get("text", "")).strip(),
              "warn": "", "done_when": ""}
             for s in (d.get("steps") or [])]
    steps = [s for s in steps if s["text"]]
    h = host(off)
    provider_url = f"https://{h}" if h else None
    speed = d.get("speed") if d.get("speed") in ("today", "days", "weeks") else "days"
    row = {
        "route_id": rid,
        "name": f"{provider} — {method.lower()}",
        "provider": provider,
        "provider_url": provider_url,
        "category": category,
        "difficulty": difficulty,
        "lane": "Standard",
        "payout_text": payout_text[:2000],
        "payout_timing": (str(d.get("timing") or "")[:1000] or None),
        "steps": steps,
        "catches": [str(c)[:1000] for c in (d.get("catches") or [])],
        "exclusions": None,
        "tax_note": None,
        "affiliate_note": None,
        "min_age": 18,
        "geo_notes": str(d.get("eligibility") or geo)[:500],
        "status": "verified",
        "speed": speed,
        "verified_at": NOW,
        "verified_source_url": off[:2000] or None,
        "expires_at": None,
    }
    if rid in existing:
        st, _ = req("PATCH", f"/rest/v1/routes?route_id=eq.{rid}", row)
        upd += 1
    else:
        st, _ = req("POST", "/rest/v1/routes", row)
        if st in (200, 201):
            ins += 1
            existing.add(rid)
        else:
            print("INSERT FAILED", rid, st); continue
    log_proof(rid, checked, "verified",
              "Quick-lane verify: " + str(d.get("notes") or "")[:400], off)

print(f"quick-lanes: inserted={ins} updated={upd} rejected-logged={rej}")
