#!/usr/bin/env python3
"""Apply bank-bonus verification batch 3 to the DB.
11 routes applied (8 verify + 3 stale-but-live corrected to official figures).
4 rejected logged (R0044 no figure, R0058 no amount, R0064 expired, R0076 naming error).
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

# route_id: (payout_text, expires_at ISO or None, geo_notes)
PAYOUT = {
    "R0052": ("Up to $600: $100/month for 6 months ($1,000+ direct deposits each month)",
              "2026-12-15",
              "14 states only (AZ CA CO FL IA IL IN MN NM NV OR UT WA WI); route's old $400 figure was stale"),
    "R0053": ("$400 bonus (Perks Checking; $500+ in direct deposits within 90 days)",
              "2026-09-30",
              "Huntington 22-state footprint only; new customers"),
    "R0054": ("$300 bonus ($1,000+ ACH direct deposits within 90 days)",
              "2026-12-31",
              "Must register for the offer BEFORE opening the account; $25 early-closure fee; route's old $400 figure was stale"),
    "R0059": ("$425 bonus (15 debit transactions + $500 direct deposits in 90 days)",
              "2026-09-30",
              "Iowa residents only; route's old $400 figure was stale"),
    "R0047": ("$350 bonus ($5,000-$7,999.99 in direct deposits within 90 days)",
              "2026-11-10",
              "No U.S. Bank checking in the last 12 months; enroll via the promo page"),
    "R0050": ("$300 bonus (Key Smart Checking; $2,000+ ACH direct deposits within 90 days)",
              "2026-12-11",
              "No KeyBank checking in the last 12 months; ~15-state footprint"),
    "R0055": ("$300 bonus (one direct deposit + $2,000 average daily balance over 90 days)",
              "2026-12-18",
              "Northeast only: NH MA RI CT DE NY NJ PA + select FL counties — worthless elsewhere"),
    "R0057": ("$300 bonus ($1,000/month direct deposits x 3 months, code LANGLEYBONUS2026)",
              None,
              "TARGETED: direct-mail recipients only — no mailer means likely denied; worth $0 to most users"),
    "R0060": ("$100 bonus (15 debit purchases of $10+ within 60 days + eStatements)",
              None,
              "TN-focused; route's old $300 figure was an unconfirmed third-party rumor"),
    "R0062": ("$500 bonus",
              "2026-11-30",
              "Colorado residents only; route's old $300 figure was stale"),
    "R0063": ("$300 tier ($3,000-$5,000 in direct deposits within 90 days)",
              "2026-12-31",
              "New members only; NY/PA/NJ footprint; fall promo code needs re-confirmation before display"),
}

REJECTED = {
    "R0044": "official td.com terms name no concrete dollar figure — fails checklist C1",
    "R0058": "official terms state no bonus amount — fails checklist C1",
    "R0064": "no live offer — last official promo expired ~1/5/2026",
    "R0076": "naming error: no First Citizens bonus exists; the $400 offer belongs to Citizens Bank (R0040)",
}

now = "2026-09-23T01:15:00+00"
applied, rejected = [], []
for rid, (pt, exp, geo) in PAYOUT.items():
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
