#!/usr/bin/env python3
"""Apply regional bank-bonus verification batch 8 to the DB.
6 verified (3 amount corrections: R0070->up to $600, R0071->$450, R0074->$200;
R0067 business-only reclassify flag). 9 rejected logged.
Writes proof_log audit rows for all 15."""
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

# route_id: (payout_text, geo_notes, expires_at)
PAYOUT = {
    "R0066": ("$300 (promo code STDIG9; two $500+ qualifying direct deposits within 90 days; bonus paid 2027-01-14 — long wait)",
              "S&T Bank; PA region", "2026-09-30"),
    "R0067": ("$300 but BUSINESS checking only (BUS-2026): $5,000 within 7 days, bonus credited in 6th month, $5,000 monthly avg balance or $20/mo fee, clawback + $50 fee if closed within 6 months",
              "First Merchants; business-only", "2026-09-30"),
    "R0069": ("$300 (open 2/3/26-10/30/26 with $50; 3+ direct deposits totaling $3,500 within first 4 months; bonus credited day 121-140; excludes anyone with ONB checking closed/bonused in last 36 months)",
              "Old National Bank footprint", "2026-10-30"),
    "R0070": ("Up to $600 TIERED — $300 needs $1,000-$4,999.99 avg daily balance on days 31-90 ($400 at $5,000-$9,999.99; $600 at $10,000+); opened and funded through 10/31/2026; bonus within 120 days; 12-month clawback",
              "Associated Bank; online in IA, IL, IN, KS, MI, MN, MO, OH, WI", "2026-10-31"),
    "R0071": ("$450 (Access Checking, promo SUMMIT; $3,000 aggregate qualifying direct deposits in 90 days; credited within 30 days after evaluation; COLORADO ONLY)",
              "BOK Financial; Colorado only", "2026-12-31"),
    "R0074": ("$200 (promo 200Digital826; open 8/28/26-10/27/26; 20 debit purchases by 2/1/2027; bonus on or before 3/1/2027)",
              "Commerce Bank", "2026-10-27"),
}

REJECTED = {
    "R0065": "last personal bonus expired 3/30/2026; only live offers are a targeted business bonus (received promo code) and a $50/$100 refer-a-friend — fails C1",
    "R0072": "current offer (up to $225/$525) is mailer-targeted only; public offer is a $50 referral — fails C1",
    "R0073": "no current official bonus; only an expired 2025 business offer — fails C1",
    "R0075": "offer expired 9/14/2026 — fails C1",
    "R0077": "Frost runs no checking bonuses at all (fee-waiver terms only) — fails C1",
    "R0078": "brand merged into First Horizon in 2020; no offer exists — catalog retirement candidate",
    "R0080": "no active offers; last promotions expired 12/5/2025 — fails C1",
    "R0081": "absorbed by Columbia Bank (systems conversion Jan 2026); no offer exists — catalog retirement candidate",
    "R0082": "no official bonus exists (only a long-expired $25 promo) — fails C1",
}

now = "2026-09-23T01:05:00+00"
applied, rejected = [], []
for rid, (pt, geo, exp) in PAYOUT.items():
    d = json.load(open(f"/home/hatch/workspace/upmore/qa/verification/{rid}.json"))
    terms = d.get("terms_url") or d.get("official_url")
    steps = [{"text": s, "done_when": "", "warn": ""} for s in d.get("steps", [])[:8]]
    patch = {"status": "verified", "verified_at": now, "verified_source_url": terms,
             "provider_url": d.get("official_url"),
             "steps": steps, "catches": d.get("catches", []),
             "payout_text": pt, "payout_timing": d.get("timing"),
             "min_age": 18, "geo_notes": geo,
             "expires_at": exp}
    st, _ = req("PATCH", f"/rest/v1/routes?route_id=eq.{rid}", patch)
    note = ("Evidence: " + (d.get("payout_quote") or "")[:200] + " | Catch: " +
            (d.get("biggest_catch") or ""))
    if rid == "R0067":
        note = "PRODUCT NOTE: reclassify — the live $300 offer is BUSINESS checking only; route should not be presented as a personal bonus. | " + note
    if rid in ("R0070", "R0071", "R0074"):
        note = "Amount corrected from catalog at verification time. | " + note
    req("POST", "/rest/v1/proof_log", {"route_id": rid, "result": "verified",
        "source_url": terms, "checked_at": now, "notes": note[:500]})
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
