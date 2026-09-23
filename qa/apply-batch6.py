#!/usr/bin/env python3
"""Apply focus-group/jury/survey verification batch 6 to the DB.
8 verified (payout_text uses official figures, never the route's ceiling).
5 rejected logged. Writes proof_log audit rows for all 13.
R0286 (L&E, Focus Group dup of verified R0233): verified on L&E's official
participant FAQ evidence (leopinions.com $50-$250+), worker E's reject was a
missed page, not a missing offer — recorded in proof_log."""
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
    "R0285": ("100 points = $1; $50 minimum redemption (per-study incentives vary — route's $300 headline unsupported)",
              "FocusGroup.com; US"),
    "R0286": ("$50-$250+ per study (official participant FAQ; exact amount disclosed before joining)",
              "L&E Research; US — duplicate route of verified R0233, same platform"),
    "R0290": ("$10-$50, sometimes more, per study (paid within 24 hours via PayPal)",
              "Mindswarms; US"),
    "R0293": ("Usually $20-$50 per case, 20-50 min (fee disclosed up front; cases may be unavailable for weeks by geography)",
              "JuryTest; US"),
    "R0196": ("$5 signup bonus; first payment at $15 (official sources disagree on cashout minimum: $15 blog / $30 Terms / $15-then-$10 Help — confirm in-account)",
              "InboxDollars; US"),
    "R0190": ("$5.00 instant cashout minimum (balance in dollars, not points; 'up to $50/day' is a ceiling, not typical)",
              "Eureka Surveys; US"),
    "R0189": ("$5 for every 5 surveys completed (only full completions count)",
              "Five Surveys; US"),
    "R0188": ("Points convert to PayPal cash; reward tiers $1-$100 (official site does NOT promise $5 per survey)",
              "Prime Opinion; US"),
}

REJECTED = {
    "R0287": "official site promises only 'earn incentives', no amount (B2B facilities site) — fails C1",
    "R0288": "official site is dead; brand folded into Sago, live page is B2B-only with no participant pay terms — fails C1",
    "R0289": "official site is B2B recruiting services; no concrete participant payout — fails C1",
    "R0294": "no concrete juror amount; displayed fees are attorney/client fees, not juror pay — fails C1",
    "R0219": "category error: gig marketplace, not a survey route; earnings are sales-dependent freelance income with zero guaranteed payout — fails product's variable-work guardrail",
}

now = "2026-09-23T01:50:00+00"
applied, rejected = [], []
for rid, (pt, geo) in PAYOUT.items():
    d = json.load(open(f"/home/hatch/workspace/upmore/qa/verification/{rid}.json"))
    terms = d.get("terms_url") or d.get("official_url")
    if rid == "R0286":
        d2 = json.load(open("/home/hatch/workspace/upmore/qa/verification/R0233.json"))
        terms = d2.get("terms_url") or d2.get("official_url")
    steps = [{"text": s, "done_when": "", "warn": ""} for s in d.get("steps", [])[:8]]
    patch = {"status": "verified", "verified_at": now, "verified_source_url": terms,
             "provider_url": d.get("official_url"),
             "steps": steps, "catches": d.get("catches", []),
             "payout_text": pt, "payout_timing": d.get("timing"),
             "min_age": 18, "geo_notes": geo,
             "expires_at": None}
    st, _ = req("PATCH", f"/rest/v1/routes?route_id=eq.{rid}", patch)
    note = ("Evidence: " + (d.get("payout_quote") or "")[:200] + " | Catch: " +
            (d.get("biggest_catch") or ""))
    if rid == "R0286":
        note = "Verified on L&E official participant FAQ evidence from R0233 (leopinions.com $50-$250+); worker E missed that page. | " + note
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
