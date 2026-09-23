#!/usr/bin/env python3
"""Apply brokerage/fintech verification batch 4 to the DB.
6 verified (3 with corrected amounts), 3 rejected logged.
R0097 SoFi Personal Loan: rejected — expired offer; current requires taking a loan (debt cost, fails C3).
R0102 Albert: rejected — $150 program expired; current is a $50 repayable advance, not cash.
R0104 HMBradley: rejected — consumer programs wound down end of 2023; route impossible to complete.
Writes proof_log audit rows for all 9."""
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
    "R0026": ("Up to $1,000 by deposit tier ($200k-$499,999); realistic first tier is $50 for $1k-$4,999",
              "2026-10-31",
              "Headline $1,000 needs a $200k+ deposit; promo code OFFER26"),
    "R0020": ("$50/$150/$325/$1,000 by transfer tier ($5k/$25k/$100k/$250k+; outside-Chase money)",
              None,
              "Route's old $700 figure was stale; realistic outcome is $50 for a $5,000 transfer held 90 days"),
    "R0016": ("$200 targeted tiered incentive ($10,000-$24,999.99 deposited within 7 days of approval)",
              None,
              "Targeted only — must have received the promo; deposit + reward locked 1 year; route's '$10 minimum funding' was wrong"),
    "R0103": ("$200 bonus (open Rewards Checking Preferred + 3 settled debit card transactions in 60 days)",
              None,
              "Requires opening an Upgrade Card: hard credit pull, 14.99-29.99% APR line"),
    "R0115": ("$1,000 statement credit (business-only; apply 9/1-9/30/2026; $4,000 qualifying spend in 30 days)",
              "2026-09-30",
              "Business-only, out of reach for consumers; clawback rights; route's old $200 figure was stale"),
    "R0100": ("$100 (join via referral + $500+ qualifying direct deposits in 45 days)",
              None,
              "Paycheck/pension/gov ACH only — no Venmo/transfers/tax refunds; $200 variant ends 9/30/2026; referrer 5-per-year cap can kill a link"),
}

REJECTED = {
    "R0097": "$500 bonus expired (2021/2022 targeted); current program is $300 referral requiring a funded $5k-$100k loan at ~5.99-18.28%+ APR kept 90 days — unavoidable debt cost, fails C1 and C3",
    "R0102": "$150 program expired; current referral is only a $50 Instant advance (repayable debt), not $150 cash — fails C1",
    "R0104": "consumer deposit and credit card programs wound down end of 2023 per CEO letter — no product exists, route impossible to complete",
}

now = "2026-09-23T01:30:00+00"
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
