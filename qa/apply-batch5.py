#!/usr/bin/env python3
"""Apply research-platform verification batch 5 to the DB.
6 verified (payout_text uses official RANGES, never the route's ceiling figure).
6 rejected logged (no concrete payout in official terms — Nielsen standard).
Writes proof_log audit rows for all 12."""
import json, sys, time
sys.path.insert(0, "/opt/hatch/skills/skill-creator/bin")
from dynamic_credentials import add_surrogate_to_request, read_json_response
import urllib.request

REF = "mrwngntwmnaqrqhupvlt"
PROJ = f"https://{REF}.supabase.co"

def mgmt_get(path):
    r = urllib.request.Request("https://api.supabase.com/v1" + path, method="GET")
    add_surrogate_to_request(r, "custom.supabase", allowed_hosts=["api.supabase.com"])
    with urllib.request.urlopen(r, timeout=60) as resp:
        return read_json_response(resp)
SVC = next((k["api_key"] for k in mgmt_get(f"/projects/{REF}/api-keys") if k.get("name") == "service_role"), None)

def req(method, path, body=None, tries=5):
    data = json.dumps(body).encode() if body is not None else None
    last = None
    for i in range(tries):
        try:
            r = urllib.request.Request(PROJ + path, data=data, method=method,
                headers={"apikey": SVC, "Authorization": "Bearer " + SVC,
                         "Content-Type": "application/json", "Prefer": "resolution=merge-duplicates"})
            with urllib.request.urlopen(r, timeout=60) as resp:
                return resp.status, json.loads(resp.read() or b"null")
        except Exception as e:
            last = e
            time.sleep(2 * (i + 1))
    raise last

# route_id: (payout_text, geo_notes)
PAYOUT = {
    "R0233": ("$50-$250+ per study (official range; exact amount disclosed before you join)",
              "L&E Research; US"),
    "R0228": ("$200 per hour studies (5% platform fee; must qualify for each study)",
              "Respondent; US"),
    "R0229": ("Average $45+ per study (official ranges $20-$1,500+ online; must qualify per study)",
              "User Interviews; US"),
    "R0227": ("~$1 per minute average per mission (amounts vary, previewed before committing; PayPal payout)",
              "dscout; US"),
    "R0240": ("$10-$25 per test (0-5 invites/month — study volume not guaranteed)",
              "BetaTesting; US"),
    "R0226": ("$5-$9 per 15-minute playtest (no payout threshold; paid per completed test)",
              "PlaytestCloud; US"),
}

REJECTED = {
    "R0231": "official FAQ confirms points mechanics (100 pts = $1, $50 min) but no per-study dollar amount — $300 claim unsupported, fails C1",
    "R0232": "incentives confirmed in concept only; no amount on any official page — fails C1",
    "R0234": "incentives + 2-week timing confirmed officially, but no dollar figure — fails C1",
    "R0235": "no official payout page found; panel appears absorbed into Sago — fails C1",
    "R0236": "no official payout page found (only third-party figures) — fails C1",
    "R0237": "official site now researcher-facing B2B — zero participant pay terms; $50 figure is third-party-only — fails C1",
}

now = "2026-09-23T01:40:00+00"
applied, rejected = [], []
for rid, (pt, geo) in PAYOUT.items():
    d = json.load(open(f"/home/hatch/workspace/upmore/qa/verification/{rid}.json"))
    terms = d.get("terms_url") or d.get("official_url")
    steps = [{"text": s, "done_when": "", "warn": ""} for s in d.get("steps", [])[:8]]
    patch = {"status": "verified", "verified_at": now, "verified_source_url": terms,
             "provider_url": d.get("official_url"),
             "steps": steps, "catches": d.get("catches", []),
             "payout_text": pt, "payout_timing": d.get("timing"),
             "min_age": 18, "geo_notes": geo,
             "expires_at": None}
    st, _ = req("PATCH", f"/rest/v1/routes?route_id=eq.{rid}", patch)
    req("POST", "/rest/v1/proof_log", {"route_id": rid, "result": "verified",
        "source_url": terms, "checked_at": now,
        "notes": (("Evidence: " + (d.get("payout_quote") or "")[:200] + " | Catch: " +
                   (d.get("biggest_catch") or "")))[:500]})
    applied.append((rid, st))
    print(rid, "verified", st, flush=True)

for rid, reason in REJECTED.items():
    d = json.load(open(f"/home/hatch/workspace/upmore/qa/verification/{rid}.json"))
    terms = d.get("terms_url") or d.get("official_url")
    req("POST", "/rest/v1/proof_log", {"route_id": rid, "result": "rejected",
        "source_url": terms, "checked_at": now,
        "notes": ("REJECTED per checklist: " + reason)[:500]})
    rejected.append(rid)
    print(rid, "REJECTED logged", flush=True)

print("APPLIED:", len(applied), "REJECTED:", rejected)
