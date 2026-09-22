#!/usr/bin/env python3
"""Apply the 15-route verification findings to the DB.
14 verify -> status/verified_at/source + enriched steps/catches/payout.
R0213 (Nielsen) rejected -> left unverified, as the checklist requires.
Writes proof_log audit rows for all 15."""
import json, glob, sys
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

def req(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(PROJ + path, data=data, method=method,
        headers={"apikey": SVC, "Authorization": "Bearer " + SVC,
                 "Content-Type": "application/json", "Prefer": "resolution=merge-duplicates"})
    with urllib.request.urlopen(r, timeout=60) as resp:
        return resp.status, json.loads(resp.read() or b"null")

# Concise, quote-faithful payout text per newly verified route.
PAYOUT = {
    "R0036": ("$400 checking bonus for new customers", "Deposited within 15 days after completing all offer requirements", 18,
              "New Chase checking customers only; not for existing customers or accounts closed within 90 days"),
    "R0096": ("$50-$400 bonus by direct-deposit tier ($1k-$5k+)", "Within 7 business days of completing requirements", 18,
              "Members who have never set up direct deposit with SoFi; one bonus per member"),
    "R0098": ("Referral bonus: your friend gets $100, you earn a bonus", "After all three qualifying steps complete", 18,
              "New Chime customers signing up via a referral link"),
    "R0220": ("At least $8/hr — researchers must pay a minimum of \u00a36/$8 per hour", "Paid after researcher approves; cash out from $6/\u00a36 via PayPal", 18,
              "18+, verified account, resident in a supported (mostly OECD) country"),
    "R0221": ("$10 per 15-20 min test; $4 short tests; $30-$120 live interviews", "PayPal, usually 14 days after the test; no minimum", None,
              "Working microphone, verified PayPal; must pass the practice test"),
    "R0292": ("Typically $30-$350 per case; terms state you are told the payment per case upfront", "Per case; timing not stated in terms", 18,
              "18+, US citizen living in the venue where the case is tried"),
    "R0295": ("Varies by claim; average claim about $2,080", "Weeks to months depending on the state", None,
              "49 states + DC + Puerto Rico + Alberta participate; Hawaii does not"),
    "R0302": ("Varies by settlement", "Typically months after final court approval", None,
              "Must fall inside the court-defined class for the settlement"),
    "R0355": ("5 pts per Bing search, 150/day cap; gift cards from 1,600 pts", "Redeem when you hit the point thresholds", None,
              "Microsoft account required; available in listed markets only"),
    "R0446": ("Up to $1.00 in Google Play credit per survey", "Credit added when the survey is completed", None,
              "Google account required; survey availability varies by region"),
}

now = "2026-09-22T23:30:00+00"
applied, rejected = [], []
for f in sorted(glob.glob("/home/hatch/workspace/upmore/qa/verification/R*.json")):
    d = json.load(open(f))
    rid = d["route_id"]
    terms = d.get("terms_url") or d.get("official_url")
    if d["verdict"] != "verify":
        req("POST", "/rest/v1/proof_log", {"route_id": rid, "result": "rejected",
            "source_url": terms, "checked_at": now,
            "notes": "REJECTED per checklist: " + (d.get("notes") or "")[:400]})
        rejected.append(rid)
        print(rid, "REJECTED logged", flush=True)
        continue
    steps = [{"text": s, "done_when": "", "warn": ""} for s in d.get("steps", [])[:8]]
    patch = {"status": "verified", "verified_at": now, "verified_source_url": terms,
             "provider_url": d.get("official_url"),
             "steps": steps, "catches": d.get("catches", [])}
    if rid in PAYOUT:
        pt, pti, age, geo = PAYOUT[rid]
        patch["payout_text"] = pt
        patch["payout_timing"] = pti
        if age: patch["min_age"] = age
        if geo: patch["geo_notes"] = geo
    st, _ = req("PATCH", f"/rest/v1/routes?route_id=eq.{rid}", patch)
    req("POST", "/rest/v1/proof_log", {"route_id": rid, "result": "verified",
        "source_url": terms, "checked_at": now,
        "notes": ("Evidence: " + (d.get("payout_quote") or "")[:300] + " | Catch: " + (d.get("biggest_catch") or ""))[:500]})
    applied.append((rid, st))
    print(rid, "verified", st, flush=True)

print("APPLIED:", len(applied), "REJECTED:", rejected)
