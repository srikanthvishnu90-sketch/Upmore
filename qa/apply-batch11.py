#!/usr/bin/env python3
"""Apply app-referral verification batch 11 to the DB.
7 verified (all with headline corrections), 2 rejected. proof_log audit rows for all 9."""
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
    "R0328": ("MILESTONE stock rewards, NOT $200/referral: $50 at 1 referral, $150 at 3, $800 at 10, $4,000 at 50, $10,000 at 200; $15K/yr cap; friend must fund settled deposit >$0; claim within 60 days; sell after 3 trading days; cash withdrawable after 60 days",
              "Robinhood; US", None),
    "R0330": ("Friend guaranteed $100; YOUR amount varies by active offer — no fixed $200 exists. Friend: $200+ qualifying direct deposit within 45 days + physical card activation within 14 days; 10 referrals/yr cap",
              "Chime; US", None),
    "R0329": ("Referrer $75 default / $100 only with SoFi Plus, eligible direct deposit, or $5K+ recent deposits; recipient $50; optional SoFi Plus bonus excluded (costs friend $10/mo). Friend: first SoFi product + $500 within 21 days; $10K/yr cap",
              "SoFi; US", "2026-09-30"),
    "R0331": ("$50 per referral (not $40), unlimited referrals; friend: $50 qualifying Cash Back purchases within 90 days; paid ~60 days after; returns/non-Cash-Back purchases void it",
              "Rakuten; US", "2026-09-30"),
    "R0325": ("Friend gets $15 (send $5+ within 14 days of code entry); INVITER'S amount is not published — shown in-app only. Do not treat $15 as the referrer payout",
              "Cash App; US", None),
    "R0326": ("$10 each — VENMO DEBIT CARD referral only: friend must get/use the debit card and spend $50+ on purchases within 30 days (P2P/ATM excluded); referrer needs in-app invite; 10 rewards ($100) cap",
              "Venmo; US", None),
    "R0327": ("1,000 Rewards points per side (redeemable for $10 cash back), NOT $10 cash; friend: $5+ spend within 30 days of signup; 10-friend ($100) cap",
              "PayPal; US", None),
}

REJECTED = {
    "R0332": "no official Ibotta page obtainable names a concrete current referrer amount; third-party consensus ~$10 contradicts route's $20 — fails C1",
    "R0334": "official terms pay 15c/gallon first-purchase bonus + 10c per friend purchase over $5 — no $15 flat bonus exists — fails C1",
}

now = "2026-09-23T01:20:00+00"
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
    note = ("Amount CORRECTED from catalog at verification. Evidence: " +
            (d.get("payout_quote") or "")[:180] + " | Catch: " +
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
