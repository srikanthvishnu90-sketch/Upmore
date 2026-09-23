#!/usr/bin/env python3
"""Apply UGC/creator-platform verification batch 10 to the DB.
4 verified with official rate ranges/minimums (NOT fixed guarantees), 5 rejected.
Variable-work catch disclosed on every route. Writes proof_log audit rows."""
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
    "R0245": ("$100+ per social post, $60+ per video, $15+ per image (minimums, not guarantees); paid via PayPal on approval; platform fee 20% free / 15% Creator Pro $10/mo; 18+, USA/UK/DE/AU/CA",
              "JoinBrands; US/UK/DE/AU/CA, 18+"),
    "R0246": ("Each task shows its set, non-negotiable payout before you apply (NO published per-video rate); paid twice monthly via PayPal; 'average creator earns $500/mo' is a platform claim, not a promise",
              "Billo; US creators"),
    "R0247": ("UGC videos start at $20 per video (brand-side floor, NOT creator take-home); official pages contradict on commission (10% vs 20% — confirm in your creator agreement); payout timing unpublished",
              "Influee; variable by brief"),
    "R0267": ("Typically pricing begins at $250 per asset (brand-set; pay may be PRODUCT-ONLY); paid by client no earlier than 30 days after campaign end; creator bears 2.9% PayPal fees; Cohley disclaims liability if client doesn't pay",
              "Cohley; US creators"),
}

REJECTED = {
    "R0248": "official pages publish ZERO dollar figures for creator pay; escrow-style payment safety only, per-campaign negotiation — fails C1",
    "R0249": "brand-facing site; no creator pay figures anywhere (hiring costs are brand-side 'credits'); curated network, 15K+ waitlist — fails C1",
    "R0250": "official help: pay is 'up to you to negotiate' per brief; $250M+ paid is an aggregate, not a rate — fails C1",
    "R0253": "rates AI-negotiated per campaign, never published — no official rate, range, or minimum exists — fails C1",
    "R0254": "official policy is literally 'you set your price' — opposite of a stated payout; 3k+ followers required — fails C1",
}

VAR_WORK = "Variable gig work, NOT fixed income: zero guaranteed campaigns, brands select which creators they accept, and content-rights terms vary per brief."

now = "2026-09-23T01:15:00+00"
applied, rejected = [], []
for rid, (pt, geo) in PAYOUT.items():
    d = json.load(open(f"/home/hatch/workspace/upmore/qa/verification/{rid}.json"))
    terms = d.get("terms_url") or d.get("official_url")
    steps = [{"text": s, "done_when": "", "warn": ""} for s in d.get("steps", [])[:8]]
    catches = d.get("catches", []) + [VAR_WORK]
    patch = {"status": "verified", "verified_at": now, "verified_source_url": terms,
             "provider_url": d.get("official_url"),
             "steps": steps, "catches": catches,
             "payout_text": pt, "payout_timing": d.get("timing"),
             "min_age": 18, "geo_notes": geo,
             "expires_at": None}
    st, _ = req("PATCH", f"/rest/v1/routes?route_id=eq.{rid}", patch)
    note = ("Evidence: " + (d.get("payout_quote") or "")[:200] + " | Catch: " +
            (d.get("biggest_catch") or "")[:180])
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
