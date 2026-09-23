#!/usr/bin/env python3
"""Apply cashback/surveys/unclaimed/rebates verification batch 18 to the DB.
23 NEW verified + 21 re-verified updates + 29 rejects + 2 duplicate logs (R0152->R0355, R0155->R0119)."""
import json, sys, time
sys.path.insert(0, "/opt/hatch/skills/skill-creator/bin")
from dynamic_credentials import add_surrogate_to_request, read_json_response
import urllib.request

REF = "mrwngntwmnaqrqhupvlt"
PROJ = f"https://{REF}.supabase.co"
BASE = "/home/hatch/workspace/upmore/qa/verification"

def mgmt_get(path):
    r = urllib.request.Request("https://api.supabase.com/v1" + path, method="GET")
    add_surrogate_to_request(r, "custom.supabase", allowed_hosts=["api.supabase.com"])
    with urllib.request.urlopen(r, timeout=60) as resp:
        return read_json_response(resp)
SVC = next((k["api_key"] for k in mgmt_get(f"/projects/{REF}/api-keys") if k.get("name") == "service_role"), None)

def req(method, path, body=None, tries=6):
    data = json.dumps(body).encode() if body is not None else None
    last = None
    for i in range(tries):
        try:
            r = urllib.request.Request(PROJ + path, data=data, method=method,
                headers={"apikey": SVC, "Authorization": "Bearer " + SVC,
                         "Content-Type": "application/json", "Prefer": "resolution=merge-duplicates"})
            with urllib.request.urlopen(r, timeout=90) as resp:
                return resp.status, json.loads(resp.read() or b"null")
        except Exception as e:
            last = e
            time.sleep(3 * (i + 1))
    raise last

cat = {r["route_id"]: r for r in json.load(open("/home/hatch/workspace/upmore/qa/catalog_dump.json"))}
now = "2026-09-23T02:25:00+00"

NEW = ["R0125","R0126","R0134","R0135","R0136","R0144","R0145","R0146","R0148","R0151",
       "R0296","R0298","R0299","R0300","R0301","R0303","R0306","R0307","R0308","R0309",
       "R0315","R0321","R0322"]
UPD = ["R0140","R0292","R0293","R0295","R0302","R0310","R0312","R0313","R0314","R0316",
       "R0318","R0320","R0323","R0324","R0325","R0326","R0327","R0328","R0329","R0330","R0331"]
REJ = ["R0122","R0123","R0124","R0127","R0128","R0129","R0130","R0131","R0132","R0133",
       "R0137","R0138","R0139","R0141","R0142","R0143","R0147","R0149","R0150","R0153",
       "R0154","R0291","R0294","R0297","R0304","R0305","R0311","R0317","R0319"]

def apply_verify(rid, is_new):
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
         "min_age": 18, "geo_notes": prov})
    note = ("Evidence: " + (d.get("payout_quote") or "")[:200] + " | Catch: " + (d.get("biggest_catch") or "")[:180])
    req("POST", "/rest/v1/proof_log", {"route_id": rid, "result": "verified",
        "source_url": terms, "checked_at": now, "notes": note[:500]})
    print(rid, "verified" if is_new else "updated", prov, flush=True)

def log_reject(rid, reason):
    d = json.load(open(f"{BASE}/{rid}.json"))
    req("POST", "/rest/v1/proof_log", {"route_id": rid, "result": "rejected",
        "source_url": d.get("terms_url") or d.get("official_url"), "checked_at": now,
        "notes": ("REJECTED per checklist: " + reason)[:500]})
    print(rid, "REJECTED logged", flush=True)

for rid in NEW:
    apply_verify(rid, True)
for rid in UPD:
    apply_verify(rid, False)

log_reject("R0152", "catalog duplicate of verified R0355 (same Microsoft Rewards program)")
log_reject("R0155", "Fetch eReceipts is a sub-program of verified R0119 (Fetch); merged, not a separate route")
for rid in REJ:
    d = json.load(open(f"{BASE}/{rid}.json"))
    log_reject(rid, d.get("notes") or d.get("biggest_catch") or "no official payout terms")

print(f"APPLIED: {len(NEW)} new verified, {len(UPD)} updated, {len(REJ)+2} rejected")
