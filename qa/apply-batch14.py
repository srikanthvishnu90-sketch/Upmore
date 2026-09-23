#!/usr/bin/env python3
"""Apply translation/transcription verification batch 14 to the DB.
11 verified (official rates only; hiring-paused flags where applicable), 9 rejected.
All carry the variable-gig-work catch. proof_log audit rows for all 20."""
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

# route_id: (provider, payout_text, paused_flag)
PAYOUT = {
    "R0403": ("Translate.com", "Post-machine-translation $0.025/word (avg $15-$20/order); copy-edit $0.015/word ($10-$15); document translation $0.02/word ($10-$100); paid once balance exceeds $20 via PayPal/Wise/Revolut/Payoneer", False),
    "R0404": ("ProZ", "MECHANISM ONLY: translators set their own rates, bid, and are paid directly by clients — ProZ NEVER pays anyone; optional ProZ*Pay via Wise/PayPal/Payoneer/Skrill. Catalog's $1,000 is illustrative, not official", False),
    "R0405": ("Translated.com", "MECHANISM ONLY: free to set your own per-word rate; paid at end of month. No earnings floor; only vetted pros get steady work", False),
    "R0409": ("Lionbridge/TELUS", "MECHANISM ONLY: each project invitation includes a specific compensation offer accepted case-by-case; PayPal/wire/ACH/eCheck/SEPA; $10 PayPal / $100 bank minimums; monthly cycle. Catalog's $25 matched no official figure", False),
    "R0390": ("Rev", "$0.40-$1.10 per audio minute (transcription); captioner $0.54-$1.10; weekly PayPal. Paid per AUDIO minute — beginners earn a few real dollars/hour; application waitlist", False),
    "R0391": ("TranscribeMe", "$15-$22 per AUDIO hour (not work hour — ~4h work per audio hour, beginner reality $4-$6/hr); official average $250/month", False),
    "R0392": ("GoTranscript", "Up to $0.60/audio minute (catalog's $1 NOT officially supported); $150/mo average; Friday PayPal/Payoneer, no minimums", False),
    "R0393": ("Scribie", "$5-$20 per audio hour, PayPal, no withdrawal limits — BUT HIRING IS PAUSED per official announcement (migrating to Scribie.ai); NOT actionable now", True),
    "R0394": ("CastingWords", "8.5 cents to ~$1 per audio minute; newcomers only get the lowest tier; rejected work unpaid", False),
    "R0396": ("Speechpad", "$0.25-$1.00/min; weekly Thursday PayPal — BUT APPLICATIONS ARE CLOSED (at capacity); entry-level ~$7.50/hr by their own math; NOT actionable now", True),
    "R0397": ("Daily Transcription", "MECHANISM ONLY: per-assignment rate disclosed upfront, paid weekly by mailed check (US/Canada); 1099 contractor; no rate knowable before joining", False),
}

REJECTED = {
    "R0400": "no published rate anywhere on official pages; only 'income varies' — fails C1",
    "R0401": "brand folded into BLEND; no live official translator-pay page — fails C1",
    "R0402": "no official rate published; catalog's $15 exists only on unofficial sources — fails C1",
    "R0406": "zero worker pay info officially ($4.50/audio-min is the client price); 'very selective' waitlist — fails C1",
    "R0407": "translator site gone — redirects to Acolad/Lia merge notice — fails C1",
    "R0408": "no published rates; per-project compensation only; disclaims guaranteed assignments — fails C1",
    "R0395": "'we currently do not have openings for transcriptionists' + zero official pay info — fails C1",
    "R0398": "only official pay statement is 'paid based on work completed' — no rate, method, or schedule — fails C1",
    "R0399": "requires YOU to pay a $20 background-check fee, with no published pay rate at all — fails C1",
}

GIG_CATCH = "Variable gig work, NOT fixed income: zero guaranteed tasks, qualification tests, variable availability, low effective hourly rates, unpaid entry tests."
PAUSED_CATCH = "NOT ACTIONABLE RIGHT NOW — hiring/applications paused per official site; check back before spending time on it."

now = "2026-09-23T01:50:00+00"
applied, rejected = [], []
for rid, (prov, pt, paused) in PAYOUT.items():
    d = json.load(open(f"/home/hatch/workspace/upmore/qa/verification/{rid}.json"))
    terms = d.get("terms_url") or d.get("official_url")
    steps = [{"text": s, "done_when": "", "warn": ""} for s in d.get("steps", [])[:8]]
    catches = d.get("catches", []) + [GIG_CATCH]
    if paused:
        catches = [PAUSED_CATCH] + catches
    patch = {"status": "verified", "verified_at": now, "verified_source_url": terms,
             "provider_url": d.get("official_url"),
             "steps": steps, "catches": catches,
             "payout_text": pt, "payout_timing": d.get("timing"),
             "min_age": 18, "geo_notes": prov + "; remote",
             "expires_at": None}
    st, _ = req("PATCH", f"/rest/v1/routes?route_id=eq.{rid}", patch)
    note = ("Evidence: " + (d.get("payout_quote") or "")[:200] + " | Catch: " +
            (d.get("biggest_catch") or "")[:180])
    if paused:
        note = "HIRING/APPLICATIONS PAUSED per official site. | " + note
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
