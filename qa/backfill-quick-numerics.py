#!/usr/bin/env python3
"""Backfill qa/numerics.json for the quick-expansion lanes R6600-R7899.
Reads payout_min_usd/payout_max_usd/time_min_minutes/time_max_minutes (and
numeric_basis/payout_value_note where present) from the evidence files.
earn_ratio = payout_mid / max(1, time_mid), matching the catalog convention.
Idempotent: overwrites entries for these lanes only.
"""
import json, glob, os

NUM_PATH = "/home/hatch/workspace/upmore/qa/numerics.json"
VER_DIR = "/home/hatch/workspace/upmore/qa/verification"

num = json.load(open(NUM_PATH))
added = 0
for f in sorted(glob.glob(os.path.join(VER_DIR, "R*.json"))):
    rid = os.path.basename(f)[:5]
    if not ("R6600" <= rid < "R7900") and not ("R8000" <= rid <= "R8399"):
        continue
    d = json.load(open(f))
    if d.get("verdict") != "verify":
        continue
    pmin = d.get("payout_min_usd")
    pmax = d.get("payout_max_usd")
    tmin = d.get("time_min_minutes")
    tmax = d.get("time_max_minutes")
    if pmin is None or pmax is None or tmin is None or tmax is None:
        print("SKIP (missing numerics):", rid)
        continue
    pmin, pmax, tmin, tmax = float(pmin), float(pmax), float(tmin), float(tmax)
    pmid = (pmin + pmax) / 2
    tmid = (tmin + tmax) / 2
    ratio = pmid / max(1.0, tmid)
    basis = (d.get("numeric_basis") or "").strip()
    if not basis:
        q = (d.get("payout_quote") or "").strip()[:120]
        basis = f"quick-lane evidence {rid}: payout {pmin:g}-{pmax:g} USD, active time {tmin:g}-{tmax:g} min" + (f"; quote: {q}" if q else "")
    num[rid] = {
        "payout_min": pmin,
        "payout_max": pmax,
        "payout_value_note": (d.get("payout_value_note") or "").strip() or None,
        "time_min_minutes": tmin,
        "time_max_minutes": tmax,
        "numeric_basis": basis,
        "earn_ratio": round(ratio, 4),
    }
    added += 1

json.dump(num, open(NUM_PATH, "w"), indent=1)
print(f"numerics: entries={len(num)} added/updated={added}")
