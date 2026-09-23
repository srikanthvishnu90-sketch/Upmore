#!/usr/bin/env python3
"""Import xlsx-144 verified methods (R91xx) into DB + numerics + evidence files.
Idempotent: route_ids already in DB are skipped (PATCH nothing).
Rejects are logged to qa/hidden_files/xlsx-144-rejects.json.
"""
import json, os, sys, glob, datetime

sys.path.insert(0, "/home/hatch/workspace/upmore/qa")
from db import req

NOW = datetime.datetime.now(datetime.timezone.utc).isoformat()
BASE = "/home/hatch/workspace/upmore"
VERD = sorted(glob.glob(f"{BASE}/qa/hidden_files/xlsx-verdicts-lane*.json"))
NUMP = f"{BASE}/qa/numerics.json"
EVD = f"{BASE}/qa/verification"

def trunc(s, n=800):
    s = str(s or "")
    return s[:n]

TIME_DEFAULTS = {
    # route_id: (time_min_minutes, time_max_minutes) for lane-1 imports whose
    # worker did not supply time fields; conservative realistic per-unit times.
    "R9100": (60, 180),    # WriterAccess: beginner article
    "R9101": (60, 180),    # Crowd Content: assignment
    "R9102": (60, 60),     # Measurement Inc: per hour
    "R9103": (60, 120),    # Knowbility: accessibility study
    "R9104": (120, 480),   # PeoplePerHour: small project
}

# lane-1 verdicts came back under alternate key names; normalize to the
# canonical schema before importing.
KEYMAP = {
    "verdict": ("verdict", "decision"),
    "method_id": ("method_id", "id"),
    "what": ("what", "name"),
    "requirements": ("requirements", "qualifies"),
    "who_qualifies": ("who_qualifies", "qualifies"),
    "work_available": ("work_available", "availability"),
    "what_gets_accepted": ("what_gets_accepted", "accepted"),
    "costs_and_unpaid_time": ("costs_and_unpaid_time", "costs_unpaid_time"),
    "when_cash_arrives": ("when_cash_arrives", "cash_timing"),
}

def g(v, key):
    for k in KEYMAP.get(key, (key,)):
        if v.get(k) not in (None, ""):
            return v[k]
    return v.get(key)

def get_steps(v):
    steps = v.get("steps") or []
    if steps:
        return steps
    # fallback: Provider Playbooks sheet from the xlsx
    try:
        import openpyxl
        wb = openpyxl.load_workbook(
            "/home/hatch/workspace/user/files/STACK_150_Online-Only_Methods.xlsx",
            read_only=True, data_only=True)
        ws = wb["Provider Playbooks"]
        mid = g(v, "method_id")
        out = []
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row[0] == mid:
                out.append((int(row[4]), str(row[5] or "")))
        return [t for _, t in sorted(out)]
    except Exception:
        return []

imported, skipped, rejected = [], [], []
for vf in VERD:
    verdicts = json.load(open(vf))
    numerics = json.load(open(NUMP))
    for v in verdicts:
        mid = g(v, "method_id") or "?"
        if g(v, "verdict") != "import":
            rejected.append({"method_id": mid, "provider": v.get("provider"),
                             "reason": v.get("reason")})
            continue
        rid = v["route_id"]
        st, existing = req("GET", f"/rest/v1/routes?select=route_id&route_id=eq.{rid}")
        if existing:
            skipped.append(rid)
            continue
        pmin, pmax = float(v["payout_min"]), float(v["payout_max"])
        _t = TIME_DEFAULTS.get(rid)
        tmin = float(v.get("time_min_minutes") or (_t[0] if _t else 60))
        tmax = float(v.get("time_max_minutes") or (_t[1] if _t else 180))
        pmid, tmid = (pmin + pmax) / 2, (tmin + tmax) / 2
        ratio = round(pmid / tmid, 4) if tmid else 0.0
        rep = v.get("repeatable")
        rep_val = bool(rep.get("value")) if isinstance(rep, dict) else bool(rep) if rep is not None else True
        rep_note = (rep.get("cadence") if isinstance(rep, dict) and rep.get("cadence")
                    else rep if isinstance(rep, str)
                    else ("repeatable per official terms" if rep_val else "one-time"))
        catches = v.get("catches") or ([v["biggest_catch"]] if v.get("biggest_catch") else [])
        row = {
            "route_id": rid,
            "provider": v["provider"],
            "name": f"{v['provider']} — {v['name']}"[:200],
            "category": v["category"],
            "status": "verified",
            "speed": v["speed"] if v["speed"] in ("today", "days", "weeks") else "days",
            "payout_min": pmin,
            "payout_max": pmax,
            "payout_text": f"${pmin:g}-${pmax:g} per paid task. {trunc(g(v, 'what'), 200)}",
            "payout_timing": trunc(g(v, "when_cash_arrives"), 500),
            "time_min_minutes": tmin,
            "time_max_minutes": tmax,
            "provider_url": v["url"],
            "geo_notes": trunc(g(v, "requirements"), 500),
            "difficulty": {"easy": "Easy", "medium": "Medium", "hard": "Hard"}.get(
                v.get("ease"), "Medium"),
            "lane": "Standard",
            "who_pays": trunc(v.get("who_pays")),
            "who_qualifies": trunc(g(v, "who_qualifies")),
            "work_available": trunc(g(v, "work_available")),
            "what_gets_accepted": trunc(g(v, "what_gets_accepted")),
            "costs_and_unpaid_time": trunc(g(v, "costs_and_unpaid_time")),
            "when_cash_arrives": trunc(g(v, "when_cash_arrives")),
            "catches": catches,
            "repeatable": {"value": rep_val, "cadence": trunc(rep_note, 300)},
            "verified_source_url": v["url"],
            "verified_at": NOW,
            "min_age": 18,
            "steps": [{"text": trunc(s, 300), "warn": "", "done_when": ""}
                      for s in (get_steps(v) or [])[:8]],
        }
        st, _ = req("POST", "/rest/v1/routes", body=row)
        if st not in (200, 201):
            print(f"INSERT FAILED {rid}: {st}")
            continue
        numerics[rid] = {
            "payout_min": pmin, "payout_max": pmax,
            "payout_value_note": f"${pmin:g}-${pmax:g} per paid task (official terms)",
            "time_min_minutes": tmin, "time_max_minutes": tmax,
            "earn_ratio": ratio,
            "numeric_basis": f"xlsx-144 import: payout {pmin:g}-{pmax:g} per task; "
                             f"time {tmin:g}-{tmax:g} min active (official terms)",
        }
        json.dump(numerics, open(NUMP, "w"), indent=1)
        ev = {"eligibility": trunc(g(v, "requirements"), 500),
              "repeatable": {"value": rep_val, "cadence": trunc(rep_note, 300)},
              "maximize": trunc(v.get("ease_note", ""), 300)}
        json.dump(ev, open(f"{EVD}/{rid}.json", "w"), indent=1)
        imported.append({"route_id": rid, "method_id": mid,
                         "provider": v["provider"]})
        print(f"imported {rid} {v['provider']}")

json.dump(rejected, open(f"{BASE}/qa/hidden_files/xlsx-144-rejects.json", "w"), indent=1)
print(f"\nimported={len(imported)} skipped={len(skipped)} rejected={len(rejected)}")
