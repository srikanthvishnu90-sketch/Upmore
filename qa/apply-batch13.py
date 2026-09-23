#!/usr/bin/env python3
"""Apply high-value-leftovers verification batch 13 to the DB.
1 verified (HealthyWage, heavily corrected: own-money wager, no fixed $500), 3 rejected,
1 deferred (Fiverr — reassign). proof_log audit rows for all 4."""
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

REJECTED = {
    "R0477": "YouTube Shorts Fund permanently retired Feb 2023 per official YouTube Help; replaced by YPP Shorts ad revenue sharing (45% of Creator Pool, requires 10M+ Shorts views/90d). No fund, no $10,000 — fails C2/C4",
    "R0076": "no checking bonus on firstcitizens.com; catalog's $400 almost certainly confuses First Citizens Bank with Citizens Bank (different bank, verified $400 offer 7/1/26-9/30/26). Re-verify as Citizens, not First Citizens — fails C1",
    "R0042": "no verifiable current official HSBC Advance bonus; route's $600 matches nothing official; third-party trackers show only $200-$240 expired offers; HSBC sold US retail branches 2021-22 — fails C1",
}

now = "2026-09-23T01:35:00+00"

# R0495 HealthyWage — verified with heavy corrections
d = json.load(open("/home/hatch/workspace/upmore/qa/verification/R0495.json"))
terms = d.get("terms_url") or d.get("official_url")
steps = [{"text": s, "done_when": "", "warn": ""} for s in d.get("steps", [])[:8]]
payout_text = ("NO fixed $500: prize is algorithm-calculated from your goal, bet, timeframe, BMI "
               "(official page shows real winner prizes $1,163-$10,984). You bet YOUR OWN money "
               "(one-time or monthly); prize paid only after verified video weigh-ins + referee certification. "
               "Absolutely NO refunds or cancellations — miss the goal, lose the wager")
catches = d.get("catches", [])
patch = {"status": "verified", "verified_at": now, "verified_source_url": terms,
         "provider_url": d.get("official_url"),
         "steps": steps, "catches": catches,
         "payout_text": payout_text, "payout_timing": d.get("timing"),
         "min_age": 18, "geo_notes": "HealthyWage; US, 18+",
         "expires_at": None}
st, _ = req("PATCH", "/rest/v1/routes?route_id=eq.R0495", patch)
note = ("Amount CORRECTED: no fixed $500 — algorithm-calculated prize. Own money at risk. "
        "Evidence: " + (d.get("payout_quote") or "")[:150] + " | Catch: " +
        (d.get("biggest_catch") or "")[:150])
req("POST", "/rest/v1/proof_log", {"route_id": "R0495", "result": "verified",
    "source_url": terms, "checked_at": now, "notes": note[:500]})
print("R0495 verified", st, flush=True)

for rid, reason in REJECTED.items():
    f = json.load(open(f"/home/hatch/workspace/upmore/qa/verification/{rid}.json"))
    req("POST", "/rest/v1/proof_log", {"route_id": rid, "result": "rejected",
        "source_url": f.get("terms_url") or f.get("official_url"), "checked_at": now,
        "notes": ("REJECTED per checklist: " + reason)[:500]})
    print(rid, "REJECTED logged", flush=True)

print("APPLIED: 1 verified (R0495), REJECTED:", list(REJECTED.keys()), "| R0490 Fiverr deferred")
