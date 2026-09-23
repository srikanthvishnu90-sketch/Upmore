#!/usr/bin/env python3
"""Apply bank-bonus verification batch 2 to the DB.
9 verify -> status/verified_at/source + enriched steps/catches/payout/expires_at.
R0042 (HSBC Advance) rejected -> stays unverified, rejection logged.
Stale headlines corrected: R0040 $500->$400, R0048 $400->$500, R0051 $400->$300.
Writes proof_log audit rows for all 10."""
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

# route_id: (payout_text, payout_timing, expires_at ISO or None, geo_notes)
PAYOUT = {
    "R0037": ("$500 checking bonus for new business customers (tiered by new-money deposit)",
              "Deposited within 15 days after completing all requirements", "2026-10-15",
              "Business accounts only — not a personal checking bonus"),
    "R0039": ("$500 or $1,500 by day-45 balance tier ($30k / $200k)",
              "Bonus earned after completing required activities; paid per the offer's key dates", "2026-10-26",
              "US; the $1,500 tier needs $200,000 on deposit at day 45"),
    "R0040": ("$400 checking bonus (personal; $1,000 in direct deposits within 60 days)",
              "Bonus paid by end of day on the payout date in the offer's key-dates table", None,
              "Citizens Bank footprint states; personal offer is $400, not $500"),
    "R0041": ("$1,000-$3,000 by balance tier ($50k-$500k); the $2,000 tier needs $250k held 3+ months",
              "Paid within 8 weeks after all offer requirements are met", "2026-12-31",
              "US; realistic tier for most users is $1,000 (needs $50k parked); $50/month fee if balance drops"),
    "R0043": ("$100-$400; the $400 tier needs Virtual Wallet Performance Select + $5,000 direct deposits in 60 days",
              "Paid after requirements are verified; account must remain open and in good standing", "2027-01-07",
              "US; standard Virtual Wallet pays only $100; one bonus per customer per 24 months"),
    "R0045": ("$400 checking bonus ($1,000 in direct deposits within 90 days)",
              "Deposited within 30 days after completing all requirements", "2026-10-20",
              "US"),
    "R0048": ("$500 checking bonus",
              "Paid within 10 business days after requirements are met and verified", None,
              "Truist footprint states; live offer is $500 (route previously said $400)"),
    "R0051": ("$300 checking bonus ($500 in deposits within 90 days)",
              "Added within 10 business days of making the qualifying deposits", "2026-09-30",
              "Fifth Third footprint states; live offer is $300 (route previously said $400)"),
    "R0056": ("$500 bonus (3 months of $1k+ deposits, 10 card transactions/month, paperless)",
              "Deposited within 30 calendar days after all requirements are met", "2026-09-30",
              "Oregon, California, Idaho only — Rogue Credit Union membership area"),
}

now = "2026-09-23T01:00:00+00"
BATCH = ["R0037", "R0039", "R0040", "R0041", "R0042", "R0043", "R0045", "R0048", "R0051", "R0056"]

applied, rejected = [], []
for rid in BATCH:
    d = json.load(open(f"/home/hatch/workspace/upmore/qa/verification/{rid}.json"))
    terms = d.get("terms_url") or d.get("official_url")
    if d["verdict"] != "verify":
        req("POST", "/rest/v1/proof_log", {"route_id": rid, "result": "rejected",
            "source_url": terms, "checked_at": now,
            "notes": ("REJECTED per checklist: " + (d.get("notes") or ""))[:500]})
        rejected.append(rid)
        print(rid, "REJECTED logged", flush=True)
        continue
    pt, pti, exp, geo = PAYOUT[rid]
    steps = [{"text": s, "done_when": "", "warn": ""} for s in d.get("steps", [])[:8]]
    patch = {"status": "verified", "verified_at": now, "verified_source_url": terms,
             "provider_url": d.get("official_url"),
             "steps": steps, "catches": d.get("catches", []),
             "payout_text": pt, "payout_timing": pti,
             "min_age": 18, "geo_notes": geo,
             "expires_at": exp}
    st, _ = req("PATCH", f"/rest/v1/routes?route_id=eq.{rid}", patch)
    req("POST", "/rest/v1/proof_log", {"route_id": rid, "result": "verified",
        "source_url": terms, "checked_at": now,
        "notes": (("Evidence: " + (d.get("payout_quote") or "")[:250] + " | Catch: " +
                   (d.get("biggest_catch") or "")))[:500]})
    applied.append((rid, st))
    print(rid, "verified", st, flush=True)

print("APPLIED:", len(applied), "REJECTED:", rejected)
