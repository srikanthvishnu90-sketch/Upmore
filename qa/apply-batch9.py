#!/usr/bin/env python3
"""Apply student-program verification batch 9 to the DB.
9 verified — ALL are savings/discount/credit routes, never income.
Writes proof_log audit rows for all 9. No $X-planner exposure (no CASH_MATH entries)."""
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
    "R0373": ("Free tools/credits for students: GitHub Pro, Copilot Student, JetBrains, $100 Azure credit (18+), $13/mo Heroku x24mo, $50 MongoDB credits (no official $1,000 total exists — value in free tools, not cash)",
              "GitHub Student Developer Pack; student verification required"),
    "R0366": ("Comparison tool for textbook buyback prices (varies per book; BookFinder is not itself a buyer — no fixed $200)",
              "US; quote varies per book"),
    "R0367": ("Chegg no longer buys books (since mid-2022) — selling routes through Valore's marketplace (functional duplicate of R0368)",
              "US; duplicate of ValoreBooks route"),
    "R0368": ("Textbook buyback with prepaid label (ship within 7 days); payment within 14 business days of processing — check 7-14d or PayPal 2-14d; quote varies per book",
              "ValoreBooks; US"),
    "R0369": ("Trade textbooks for Amazon.com gift cards (prepaid label; gift card, NOT cash)",
              "Amazon; US"),
    "R0376": ("Student plan $19.99/mo first year per Adobe terms (discount on a paid subscription, NOT income)",
              "Adobe; student verification required"),
    "R0378": ("100% free for students (Professional tier; over-13 + verification required)",
              "Figma; students/educators/schools"),
    "R0377": ("Free Plus Plan for a one-member workspace (institution email required; K-12 not eligible for the individual offer)",
              "Notion; students with institution email"),
    "R0374": ("6-month free trial then $7.49/mo or $69/yr per Amazon terms (AUTO-CHARGES if not cancelled)",
              "Amazon Prime Student; young adults"),
}

now = "2026-09-23T01:10:00+00"
applied = []
for rid, (pt, geo) in PAYOUT.items():
    d = json.load(open(f"/home/hatch/workspace/upmore/qa/verification/{rid}.json"))
    terms = d.get("terms_url") or d.get("official_url")
    steps = [{"text": s, "done_when": "", "warn": ""} for s in d.get("steps", [])[:8]]
    patch = {"status": "verified", "verified_at": now, "verified_source_url": terms,
             "provider_url": d.get("official_url"),
             "steps": steps, "catches": d.get("catches", []),
             "payout_text": pt, "payout_timing": d.get("timing"),
             "min_age": 18, "geo_notes": geo,
             "expires_at": None}
    st, _ = req("PATCH", f"/rest/v1/routes?route_id=eq.{rid}", patch)
    note = ("SAVINGS route, not income. Evidence: " + (d.get("payout_quote") or "")[:180] +
            " | Catch: " + (d.get("biggest_catch") or ""))
    if rid == "R0367":
        note = "PRODUCT NOTE: functional duplicate of R0368 (Chegg buyback = Valore marketplace since 2022) — consider deduping. | " + note
    req("POST", "/rest/v1/proof_log", {"route_id": rid, "result": "verified",
        "source_url": terms, "checked_at": now, "notes": note[:500]})
    applied.append((rid, st))
    print(rid, "verified", st, flush=True)

print("APPLIED:", len(applied))
