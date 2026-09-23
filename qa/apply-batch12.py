#!/usr/bin/env python3
"""Apply voiceover/audio platform verification batch 12 to the DB.
6 verified with official rate ranges (never quoted as expected earnings), 4 rejected.
upfront_fee encoded on R0380/R0387; zero-guaranteed-bookings catch everywhere. proof_log for all 10."""
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

# route_id: (payout_text, geo_notes, upfront_fee)
PAYOUT = {
    "R0381": ("New voice actors might start at $100-$500 per project; official rate article ranges: $400-$5,000 commercials, $200-$300/hr audiobooks. Keep 100% of earnings, zero deductions — ranges, NEVER expected earnings",
              "Voice123; remote", False),
    "R0380": ("Per-project package prices $70 (Telephone) up to $600 (TV Ad); talent quotes hourly or lump-sum; 'you keep every dollar you earn' (platform covers PayPal fees). Premium membership REQUIRED to respond to jobs — upfront fee, confirm current pricing in-account",
              "Voices.com; remote", True),
    "R0385": ("60-second online commercial from a mid-tier American talent ~$400; profiles show rates starting at $75-$300. Curated pro marketplace, competitive castings",
              "VoiceCrafters; remote", False),
    "R0383": ("Royalty Share: equal share of 20% (legacy) / 25% (new) of audiobook royalties from Audible/Amazon/Apple sales; Pay-for-Production: one-time per-finished-hour fee agreed with rights holder; monthly electronic payments; sub-$50 royalties carried forward. Royalty share pays $0 unless the book SELLS",
              "ACX; remote", False),
    "R0386": ("$100-$150 for up to 5-minute recordings; audiobooks $2,000-$5,000; listed pro prices $75-$869 (client-facing list prices — pro take-home after markup not published). Top-4% acceptance",
              "Bunny Studio; remote", False),
    "R0387": ("Official plans page: 23,000 projects posted in prior 12 months, $350 average project budget, ~1M talents; Pro $495 = 50% of matching projects, Pro $888 = 65%. UPFRONT FEE — pays for invitations, not bookings",
              "Voice123 memberships; remote", True),
}

REJECTED = {
    "R0382": "real platform, no commission per official FAQ, but ZERO concrete pay figures on any official page (only personal asking prices on talent profiles) — fails C1",
    "R0388": "buyer-side service; $80/100 words is the CLIENT price. No public talent program or worker compensation anywhere on official pages — fails C1",
    "R0384": "platform no longer exists standalone: voicebunny.com is an official redirect to Bunny Studio. Talent-side coverage merged into R0386 — fails C1 as standalone",
    "R0389": "no active marketplace or pay terms found via targeted official-domain check; stale route or naming error — fails C1",
}

ZERO_GUARANTEED = "Variable gig work, NOT fixed income: zero guaranteed bookings; you audition against a large talent pool and brands pick who they want."

now = "2026-09-23T01:25:00+00"
applied, rejected = [], []
for rid, (pt, geo, fee) in PAYOUT.items():
    d = json.load(open(f"/home/hatch/workspace/upmore/qa/verification/{rid}.json"))
    terms = d.get("terms_url") or d.get("official_url")
    steps = [{"text": s, "done_when": "", "warn": ""} for s in d.get("steps", [])[:8]]
    catches = d.get("catches", []) + [ZERO_GUARANTEED]
    patch = {"status": "verified", "verified_at": now, "verified_source_url": terms,
             "provider_url": d.get("official_url"),
             "steps": steps, "catches": catches,
             "payout_text": pt, "payout_timing": d.get("timing"),
             "min_age": 18, "geo_notes": geo,
             "expires_at": None}
    st, _ = req("PATCH", f"/rest/v1/routes?route_id=eq.{rid}", patch)
    note = ("Evidence: " + (d.get("payout_quote") or "")[:200] + " | Catch: " +
            (d.get("biggest_catch") or "")[:180])
    if fee:
        note = "UPFRONT FEE route — fee encoded as biggest catch. | " + note
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
