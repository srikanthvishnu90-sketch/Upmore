#!/usr/bin/env python3
"""Generate a single SQL batch applying the 15 verifications. Run with:
   python3 gen-apply-sql.py > /tmp/apply.sql
   python3 ~/workspace/skills/supabase/bin/sb.py query "$(cat /tmp/apply.sql)"
Idempotent: re-running just refreshes verified_at."""
import json, glob

PAYOUT = {
    "R0036": ("$400 checking bonus for new customers", "Deposited within 15 days after completing all offer requirements", 18,
              "New Chase checking customers only; not for existing customers or accounts closed within 90 days"),
    "R0096": ("$50-$400 bonus by direct-deposit tier ($1k-$5k+)", "Within 7 business days of completing requirements", 18,
              "Members who have never set up direct deposit with SoFi; one bonus per member"),
    "R0098": ("Referral bonus: your friend gets $100, you earn a bonus", "After all three qualifying steps complete", 18,
              "New Chime customers signing up via a referral link"),
    "R0220": ("At least $8/hr — researchers must pay a minimum of £6/$8 per hour", "Paid after researcher approves; cash out from $6/£6 via PayPal", 18,
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

def q(s):
    return "'" + str(s).replace("'", "''") + "'"

now = "2026-09-22T23:30:00+00"
stmts = []
for f in sorted(glob.glob("/home/hatch/workspace/upmore/qa/verification/R*.json")):
    d = json.load(open(f))
    rid = d["route_id"]
    terms = d.get("terms_url") or d.get("official_url") or ""
    if d["verdict"] != "verify":
        notes = ("REJECTED per checklist: " + (d.get("notes") or ""))[:500]
        stmts.append(f"INSERT INTO proof_log (route_id, result, source_url, checked_at, notes) VALUES ({q(rid)}, 'rejected', {q(terms)}, {q(now)}, {q(notes)});")
        continue
    steps = json.dumps([{"text": s, "done_when": "", "warn": ""} for s in d.get("steps", [])[:8]])
    catches = json.dumps(d.get("catches", []))
    cols = [
        "status = 'verified'", f"verified_at = {q(now)}", f"verified_source_url = {q(terms)}",
        f"provider_url = {q(d.get('official_url') or '')}",
        f"steps = {q(steps)}::jsonb", f"catches = {q(catches)}::jsonb",
    ]
    if rid in PAYOUT:
        pt, pti, age, geo = PAYOUT[rid]
        cols += [f"payout_text = {q(pt)}", f"payout_timing = {q(pti)}"]
        if age: cols.append(f"min_age = {age}")
        if geo: cols.append(f"geo_notes = {q(geo)}")
    stmts.append(f"UPDATE routes SET {', '.join(cols)} WHERE route_id = {q(rid)};")
    note = ("Evidence: " + (d.get("payout_quote") or "")[:300] + " | Catch: " + (d.get("biggest_catch") or ""))[:500]
    stmts.append(f"INSERT INTO proof_log (route_id, result, source_url, checked_at, notes) VALUES ({q(rid)}, 'verified', {q(terms)}, {q(now)}, {q(note)});")

stmts.append("SELECT route_id, status, verified_at FROM routes WHERE route_id IN ('R0036','R0096','R0098','R0116','R0118','R0119','R0140','R0213','R0220','R0221','R0292','R0295','R0302','R0355','R0446') ORDER BY route_id;")
print("\n".join(stmts))
