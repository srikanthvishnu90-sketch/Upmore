#!/usr/bin/env python3
"""Apply surveys+games verification batch 17 (R0156-R0218 range) to the DB.
Verifies: all files with verdict=verify in range. Rejects: logged to proof_log.
patch DB rows + proof_log rows."""
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
now = "2026-09-23T02:15:00+00"
ver, rej = 0, 0
for n in range(156, 219):
    rid = f"R{n:04d}"
    p = f"{BASE}/{rid}.json"
    try:
        d = json.load(open(p))
    except FileNotFoundError:
        continue
    terms = d.get("terms_url") or d.get("official_url")
    prov = cat.get(rid, {}).get("provider") or d.get("provider") or ""
    if d.get("verdict") == "verify":
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
        ver += 1
        print(rid, "verified", prov, flush=True)
    else:
        notes = ("REJECTED per checklist: " + (d.get("notes") or d.get("biggest_catch") or "no official payout terms"))[:500]
        req("POST", "/rest/v1/proof_log", {"route_id": rid, "result": "rejected",
            "source_url": terms, "checked_at": now, "notes": notes})
        rej += 1
        print(rid, "REJECTED logged", flush=True)

print(f"APPLIED: {ver} verified, {rej} rejected")
