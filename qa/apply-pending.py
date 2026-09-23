#!/usr/bin/env python3
"""Consolidated applier for pending verification batches 17/18/19 (fast keep-alive client).
Batch 17: surveys/games (R0156-R0218). Batch 18: cashback/unclaimed/rebates.
Batch 19: other-online part 1 (gig/savings/apps/extensions)."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/upmore/qa")
from db import req

BASE = "/home/hatch/workspace/upmore/qa/verification"
cat = {r["route_id"]: r for r in json.load(open("/home/hatch/workspace/upmore/qa/catalog_dump.json"))}
now = "2026-09-23T02:35:00+00"

def apply_verify(rid):
    d = json.load(open(f"{BASE}/{rid}.json"))
    terms = d.get("terms_url") or d.get("official_url")
    prov = cat.get(rid, {}).get("provider") or ""
    steps = [{"text": s, "done_when": "", "warn": ""} for s in d.get("steps", [])[:8]]
    req("PATCH", f"/rest/v1/routes?route_id=eq.{rid}",
        {"status": "verified", "verified_at": now, "verified_source_url": terms,
         "provider_url": d.get("official_url"),
         "steps": steps, "catches": d.get("catches", []),
         "payout_text": (d.get("payout_quote") or "")[:600],
         "payout_timing": (d.get("timing") or "")[:400],
         "min_age": 18, "geo_notes": prov,
         "expires_at": d.get("expires_at") or d.get("expiry")})
    note = ("Evidence: " + (d.get("payout_quote") or "")[:200] + " | Catch: " + (d.get("biggest_catch") or "")[:180])
    if d.get("notes"):
        note += " | " + str(d.get("notes"))[:120]
    req("POST", "/rest/v1/proof_log", {"route_id": rid, "result": "verified",
        "source_url": terms, "checked_at": now, "notes": note[:500]})
    print(rid, "verified", prov, flush=True)

def log_reject(rid, reason):
    try:
        d = json.load(open(f"{BASE}/{rid}.json"))
        src = d.get("terms_url") or d.get("official_url")
    except FileNotFoundError:
        src = None
    req("POST", "/rest/v1/proof_log", {"route_id": rid, "result": "rejected",
        "source_url": src, "checked_at": now,
        "notes": ("REJECTED per checklist: " + reason)[:500]})
    print(rid, "REJECTED", flush=True)

# ---- batch 17: surveys/games ----
b17v = ["R0156","R0158","R0159","R0164","R0167","R0171","R0172","R0173","R0174","R0186",
        "R0187","R0188","R0189","R0190","R0191","R0192","R0193","R0196","R0198","R0201",
        "R0202","R0204","R0205","R0206","R0208","R0209","R0212","R0214","R0215","R0216"]
b17r = ["R0157","R0160","R0161","R0162","R0163","R0165","R0166","R0168","R0169","R0170",
        "R0175","R0176","R0177","R0178","R0180","R0181","R0182","R0183","R0184","R0185",
        "R0194","R0195","R0197","R0199","R0200","R0203","R0207","R0210","R0211","R0217","R0218","R0179"]
# ---- batch 18: cashback/unclaimed/rebates ----
b18v = ["R0125","R0126","R0134","R0135","R0136","R0144","R0145","R0146","R0148","R0151",
        "R0140","R0292","R0293","R0295","R0302","R0310","R0312","R0313","R0314","R0316",
        "R0318","R0320","R0323","R0324","R0325","R0326","R0327","R0328","R0329","R0330",
        "R0331","R0296","R0298","R0299","R0300","R0301","R0303","R0306","R0307","R0308",
        "R0309","R0315","R0321","R0322"]
b18r = ["R0122","R0123","R0124","R0127","R0128","R0129","R0130","R0131","R0132","R0133",
        "R0137","R0138","R0139","R0141","R0142","R0143","R0147","R0149","R0150","R0153",
        "R0154","R0291","R0294","R0297","R0304","R0305","R0311","R0317","R0319"]
# ---- batch 19: other-online part 1 ----
b19v = ["R0490","R0491","R0492","R0430","R0431","R0432","R0433","R0434","R0435","R0436",
        "R0437","R0452","R0498","R0494","R0451","R0447","R0454","R0455","R0456","R0457",
        "R0461","R0462","R0464","R0465","R0466","R0467"]
b19r = ["R0438","R0439","R0440","R0441","R0448","R0463",  # adjudicated: weak evidence
        "R0469","R0470","R0471","R0473","R0474","R0472","R0475","R0445","R0443","R0444",
        "R0442","R0449","R0450","R0453","R0458","R0459","R0460","R0468","R0478","R0479"]

nv = nr = 0
for rid in b17v + b18v + b19v:
    apply_verify(rid); nv += 1
log_reject("R0152", "catalog duplicate of verified R0355 (same Microsoft Rewards program)"); nr += 1
log_reject("R0155", "Fetch eReceipts is a sub-program of verified R0119 (Fetch); merged, not a separate route"); nr += 1
for rid in b17r + b18r + b19r:
    d = json.load(open(f"{BASE}/{rid}.json"))
    log_reject(rid, d.get("notes") or d.get("biggest_catch") or "no concrete official payout terms"); nr += 1

print(f"DONE: {nv} verified, {nr} rejected")
