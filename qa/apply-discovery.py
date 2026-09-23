#!/usr/bin/env python3
"""Apply discovery lane: INSERT new routes R0536+ (verified) into DB,
log proof rows (verify + reject), and collect cards for the app bundle.
Idempotent: existing route_ids are PATCHed, proof rows keyed on (route_id, checked_at).
"""
import json, glob, os, sys, re, datetime
from urllib.parse import urlparse
sys.path.insert(0, "/home/hatch/workspace/upmore/qa")
from db import req

NOW = datetime.datetime.now(datetime.timezone.utc).isoformat()
DEMOTE = {"R0657": "duplicate evidence of R0656 — same Chase Ink $750 page assigned to two IDs; counted once"}

DOMAIN_MAP = {
    "help.twitch.tv": "Twitch", "twitch.tv": "Twitch",
    "support.patreon.com": "Patreon", "patreon.com": "Patreon",
    "ko-fi.com": "Ko-fi", "kofi.com": "Ko-fi",
    "buymeacoffee.com": "Buy Me a Coffee",
    "support.substack.com": "Substack", "substack.com": "Substack",
    "gumroad.com": "Gumroad",
    "etsy.com": "Etsy",
    "creativemarket.com": "Creative Market",
    "help.inboxdollars.com": "InboxDollars", "inboxdollars.com": "InboxDollars",
    "blog.mypoints.com": "MyPoints", "mypoints.com": "MyPoints",
    "help.swagbucks.com": "Swagbucks", "swagbucks.com": "Swagbucks",
    "microsoft.com": "Microsoft Rewards",
    "play.google.com": None,  # resolved via c2 text
    "support.idle-empire.com": "Idle-Empire", "idle-empire.com": "Idle-Empire",
    "ysense.com": "ySense", "www.ysense.com": "ySense",
    "joinpogo.com": "Pogo", "www.joinpogo.com": "Pogo",
    "go.proz.com": "ProZ", "proz.com": "ProZ",
    "creditcards.chase.com": "Chase", "chase.com": "Chase",
    "americanexpress.com": "American Express", "www.americanexpress.com": "American Express",
    "t-mobile.com": "T-Mobile", "www.t-mobile.com": "T-Mobile",
    "verizon.com": "Verizon", "www.verizon.com": "Verizon",
    "coned.com": "Con Edison", "www.coned.com": "Con Edison",
}

def host(url):
    try:
        h = urlparse(url).netloc.lower()
        return h[4:] if h.startswith("www.") else h
    except Exception:
        return ""

def provider_of(d):
    off = d.get("official_url") or d.get("official_source_url") or ""
    h = host(off)
    if h in DOMAIN_MAP and DOMAIN_MAP[h]:
        return DOMAIN_MAP[h]
    c1 = ""
    try:
        c1 = d["critical"]["c1"]["evidence"] or ""
    except Exception:
        pass
    for sep in ["\u2014", "\u2013"]:
        if sep in c1:
            cand = c1.split(sep)[0].strip()
            # reject sentence-like candidates
            if 2 <= len(cand) <= 50 and not re.search(r"\bis\b|\bare\b|\bwas\b", cand):
                return cand
            break
    if h:
        core = h.split(".")[0]
        return core.replace("-", " ").title()
    return "Unknown"

def norm_verdict(v):
    v = str(v or "").strip().lower()
    return "verify" if v in ("verify", "verified") else "reject"

def lane_of(rid):
    n = int(rid[1:])
    if 536 <= n <= 650: return ("Bank Bonus", "Bank bonus", "Easy", "US; state/branch restrictions may apply — see eligibility")
    if 651 <= n <= 750: return ("Credit Card Bonus", "Credit card welcome offer", "Moderate", "US only")
    if 751 <= n <= 830: return ("Rebate/Incentive", "Utility/energy rebate", "Easy", "Provider service territory only — see eligibility")
    return ("App Referral", "Referral bonus", "Very Easy", "US only")

def mech_text(d):
    bc = str(d.get("biggest_catch") or "").strip()
    return "Variable — no fixed payout. " + bc[:240]

def proof_exists(route_id, checked_at):
    st, rows = req("GET", f"/rest/v1/proof_log?select=id&route_id=eq.{route_id}&checked_at=eq.{checked_at}")
    return bool(rows)

def log_proof(route_id, checked_at, result, notes, source_url):
    if proof_exists(route_id, checked_at):
        return False
    st, _ = req("POST", "/rest/v1/proof_log",
                {"route_id": route_id, "checked_at": checked_at, "result": result,
                 "notes": notes[:2000], "source_url": (source_url or "")[:2000]})
    return st in (200, 201)

st, dbv = req("GET", "/rest/v1/routes?select=route_id&limit=1200")
existing = {r["route_id"] for r in dbv}

ins = upd = rej = 0
cards = []
for f in sorted(glob.glob("/home/hatch/workspace/upmore/qa/verification/R*.json")):
    rid = os.path.basename(f)[:5]
    if rid < "R0536":
        continue
    try:
        d = json.load(open(f))
    except (FileNotFoundError, json.JSONDecodeError):
        continue  # worker rewriting the file; picked up on next pass
    v = norm_verdict(d.get("verdict"))
    checked = d.get("checked_at") or NOW
    off = d.get("official_url") or d.get("official_source_url") or ""
    if rid in DEMOTE:
        v = "reject"
        note = "OVERRIDE (independent review): " + DEMOTE[rid]
    else:
        note = str(d.get("notes") or "")[:400]
    if v == "reject":
        if log_proof(rid, checked, "rejected", f"Discovery reject: {note}", off):
            rej += 1
        continue
    provider = provider_of(d)
    category, method, difficulty, geo = lane_of(rid)
    pq = (d.get("payout_quote") or "").strip()
    payout_text = pq if pq else mech_text(d)
    steps = [{"text": (s if isinstance(s, str) else s.get("text", "")).strip(), "warn": "", "done_when": ""}
             for s in (d.get("steps") or [])]
    steps = [s for s in steps if s["text"]]
    h = host(off)
    provider_url = f"https://{h}" if h else None
    row = {
        "route_id": rid,
        "name": f"{provider} — {method.lower()}",
        "provider": provider,
        "provider_url": provider_url,
        "category": category,
        "difficulty": difficulty,
        "lane": "Standard",
        "payout_text": payout_text[:2000],
        "payout_timing": (str(d.get("timing") or "")[:1000] or None),
        "steps": steps,
        "catches": [str(c)[:1000] for c in (d.get("catches") or [])],
        "exclusions": None,
        "tax_note": None,
        "affiliate_note": None,
        "min_age": 18,
        "geo_notes": geo,
        "status": "verified",
        "verified_at": NOW,
        "verified_source_url": off[:2000] or None,
        "expires_at": None,
    }
    if rid in existing:
        st, _ = req("PATCH", f"/rest/v1/routes?route_id=eq.{rid}", row)
        upd += 1
    else:
        st, _ = req("POST", "/rest/v1/routes", row)
        if st in (200, 201):
            ins += 1
            existing.add(rid)
        else:
            print("INSERT FAILED", rid, st); continue
    log_proof(rid, checked, "verified", f"Discovery verify: {note}", off)
    cards.append((rid, row, d))

json.dump([{"route_id": r, "row": row} for r, row, _ in cards],
          open("/home/hatch/workspace/upmore/qa/discovery-cards.json", "w"), indent=1)
print(f"discovery: inserted={ins} updated={upd} rejected-logged={rej} demoted={len(DEMOTE)}")
