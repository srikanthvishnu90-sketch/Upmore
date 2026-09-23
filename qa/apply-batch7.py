#!/usr/bin/env python3
"""Apply gov rebate/incentive verification batch 7 to the DB.
9 verified with federal-expiry reframes and savings-not-income framing.
1 rejected (HEEHRA not obtainable). Writes proof_log audit rows for all 10."""
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
    "R0324": ("Free weatherization services; DOE cites $372+/yr average energy savings (savings, not cash; income at or below 200% federal poverty level)",
              "Weatherization Assistance Program; US, income-restricted"),
    "R0316": ("Federal $2,000 credit EXPIRED 12/31/2025 — do not expect it for new 2026 work. Live money is state/utility rebates (e.g., NY: $700-$1,400 per 10k Btu/h + $1,000 HPWH, funded through 2030); purchase discount, not income",
              "US, state/utility-specific"),
    "R0312": ("National directory (DSIRE) of live utility rebate programs (purchase discounts, vary by utility — savings, not income)",
              "US, utility-specific"),
    "R0313": ("Federal 30% EV-charger credit (up to $1,000) EXPIRED 6/30/2026 — do not expect it for new 2026 installs. State/utility rebates remain; purchase discount, not income",
              "US, state/utility-specific"),
    "R0318": ("Federal insulation credit EXPIRED 12/31/2025. Live channel is utility rebates, typically low hundreds; purchase discount, not income",
              "US, utility-specific"),
    "R0323": ("Bill assistance: official averages $380 heating / $583 cooling, paid to the utility (not cash; income at or below 150% FPL or 60% state median income)",
              "LIHEAP; US, income-restricted"),
    "R0310": ("EPA ENERGY STAR rebate-finder directory of live appliance rebates (purchase discounts on upgrades you're already buying)",
              "US, utility-specific"),
    "R0314": ("EPA WaterSense rebate directory (purchase discounts on water-efficient products)",
              "US, utility-specific"),
    "R0320": ("Federal cooling credit EXPIRED 12/31/2025. Live channel is utility rebates, typically $25-$300; purchase discount, not income",
              "US, utility-specific"),
}

REJECTED = {
    "R0319": "HEEHRA exists on paper (up-to-$8,000/$840 caps) but is not obtainable by an average user today: CA fully reserved/waitlisted since Feb 2026, other states unlaunched, DOE June 2026 guidance bars using restarted rebates to switch fossil->electric — fails C1",
}

now = "2026-09-23T01:55:00+00"
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
