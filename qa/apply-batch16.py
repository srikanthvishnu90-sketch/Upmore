#!/usr/bin/env python3
"""Apply remaining-bank-bonuses verification batch 16 to the DB.
10 verified (R0049/R0079 same M&T offer, both patched), 9 rejected. proof_log rows all 19."""
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

def req(method, path, body=None, tries=6):
    data = json.dumps(body).encode() if body is not None else None
    last = None
    for i in range(tries):
        try:
            r = urllib.request.Request(PROJ + path, data=data, method=method,
                headers={"apikey": SVC, "Authorization": "Bearer " + SVC,
                         "Content-Type": "application/json", "Prefer": "resolution=merge-duplicates"})
            with urllib.request.urlopen(r, timeout=90) as resp:
                return resp.status, json.loads(resp.read() or b"null")
        except Exception as e:
            last = e
            time.sleep(3 * (i + 1))
    raise last

V = {
    "R0083": ("$400 (above catalog's $300) — code CON600, $1,000/mo recurring direct deposit within 90 days; paid within 95 days; new customers only, FL/GA residents only; excludes anyone who closed a Seacoast account in past 12 months", "Seacoast Bank", "2026-12-31"),
    "R0085": ("$100 (below catalog's $300) — All Access Checking, new to Valley personal checking, $500+ direct deposit; official page states no payout timing", "Valley National Bank", None),
    "R0088": ("$300 — TARGETED ONLY: Amerant At Work — employees of active Amerant commercial-client companies; credited within 45 days", "Amerant Bank", None),
    "R0089": ("$100 Convenience Checking ($2,000 DD/60d) / $300 Bankohana Level I ($3,500 DD/60d); $500 opening deposit; credit within 120 days", "Bank of Hawaii", None),
    "R0091": ("$350 Priority Banking open / $100 upgrade / $50 Pure; $500 DD in 60 days; Sep 1-Dec 31, 2026; HI footprint; Priority has $15-$25/mo fees if not waived", "First Hawaiian Bank", "2026-12-31"),
    "R0046": ("$250 (matches catalog) — code CHECKING250, 2x $500+ direct deposits within 75 days; excludes past Capital One 360/Simply holders; no fixed expiry", "Capital One", None),
    "R0049": ("Up to $300 — $300 on MyChoice checking, $500 DD in 90 days; by Dec 31, 2026; ZIP-variable. NOTE: same offer as R0079 (Manufacturers and Traders Trust = M&T legal name)", "M&T Bank", "2026-12-31"),
    "R0079": ("Up to $300 — $300 on MyChoice checking, $500 DD in 90 days; by Dec 31, 2026; ZIP-variable. NOTE: same offer as R0049 (this is M&T Bank's legal name)", "M&T Bank", "2026-12-31"),
    "R0086": ("$200 (below catalog's $250) — new personal checking, direct-deposited paychecks, $25 opening deposit. ENTITY WARNING: The Washington Trust Company of Westerly RI (washtrust.com), NOT Washington Trust Bank of Spokane WA", "The Washington Trust Company", None),
    "R0038": ("Tiered up to $500 — $100 at $2,000 DD / $300 at $5,000 / $500 at $10,000; open via promo page by Sep 30, 2026", "Bank of America", "2026-09-30"),
}
REJ = {
    "R0084": "offer expired — account-opening window ended 8/31/2026 (C2)",
    "R0087": "no checking bonus anywhere on zionsbank.com; only a money-market rate promo (C2)",
    "R0092": "no promo/offer page anywhere on homestreet.com; all aggregator bonuses expired (C2)",
    "R0093": "bank no longer exists (merged into Banc of California 2023); no bonus (C1/C2)",
    "R0090": "only live bonus is business-checking-only ($400-$1,200); no personal checking bonus (C2)",
    "R0094": "no bonus on official domain or anywhere else (C2)",
    "R0095": "no official personal bonus (aggregator-only business-bonus claim, unverified) (C2)",
    "R0061": "$200 Kasasa offer may exist but official terms unreadable — nothing confirmable (C2/C4)",
    "R0068": "employer-gated bonus publishes no dollar amount — no concrete payout (C4)",
}

now = "2026-09-23T02:10:00+00"
for rid, (pt, prov, exp) in V.items():
    d = json.load(open(f"/home/hatch/workspace/upmore/qa/verification/{rid}.json"))
    terms = d.get("terms_url") or d.get("official_url")
    steps = [{"text": s, "done_when": "", "warn": ""} for s in d.get("steps", [])[:8]]
    catches = d.get("catches", [])
    req("PATCH", f"/rest/v1/routes?route_id=eq.{rid}",
        {"status": "verified", "verified_at": now, "verified_source_url": terms,
         "provider_url": d.get("official_url"),
         "steps": steps, "catches": catches,
         "payout_text": pt, "payout_timing": d.get("timing"),
         "min_age": 18, "geo_notes": prov, "expires_at": exp})
    note = ("Evidence: " + (d.get("payout_quote") or "")[:200] + " | Catch: " + (d.get("biggest_catch") or "")[:180])
    req("POST", "/rest/v1/proof_log", {"route_id": rid, "result": "verified",
        "source_url": terms, "checked_at": now, "notes": note[:500]})
    print(rid, "verified", flush=True)

for rid, reason in REJ.items():
    d = json.load(open(f"/home/hatch/workspace/upmore/qa/verification/{rid}.json"))
    req("POST", "/rest/v1/proof_log", {"route_id": rid, "result": "rejected",
        "source_url": d.get("terms_url") or d.get("official_url"), "checked_at": now,
        "notes": ("REJECTED per checklist: " + reason)[:500]})
    print(rid, "REJECTED logged", flush=True)

print("APPLIED: 10 verified, 9 rejected")
