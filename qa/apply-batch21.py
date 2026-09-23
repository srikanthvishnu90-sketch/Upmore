#!/usr/bin/env python3
"""Apply 1500-expansion lane: INSERT new routes R0851+ (verified) into DB,
log proof rows (verify + reject from qa/discovery/rejects-g*.txt).
Idempotent: existing route_ids are PATCHed, proof rows keyed on (route_id, checked_at).
Adjudication demotions read from qa/adjudication-1500.json ({route_id: reason}).
"""
import json, glob, os, sys, re, datetime
from urllib.parse import urlparse
sys.path.insert(0, "/home/hatch/workspace/upmore/qa")
from db import req

NOW = datetime.datetime.now(datetime.timezone.utc).isoformat()

try:
    DEMOTE = json.load(open("/home/hatch/workspace/upmore/qa/adjudication-1500.json"))
except Exception:
    DEMOTE = {}

DOMAIN_MAP = {
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
    if 851 <= n <= 960:   return ("Bank Bonus", "Bank bonus", "Easy", "US; state/branch restrictions may apply — see eligibility")
    if 961 <= n <= 1060:  return ("Bank Bonus", "Bank bonus", "Easy", "US; state/branch restrictions may apply — see eligibility")
    if 1061 <= n <= 1140: return ("Brokerage Promo", "Brokerage bonus", "Moderate", "US only")
    if 1141 <= n <= 1190: return ("Insurance/Quote", "Quote reward", "Very Easy", "US only")
    if 1191 <= n <= 1240: return ("Telecom Promo", "ISP signup promo", "Easy", "US only")
    if 1241 <= n <= 1280: return ("Plasma Donation", "Plasma donation", "Moderate", "US; center locations only — see eligibility")
    if 1281 <= n <= 1330: return ("Clinical Trial", "Research study", "Moderate", "US; study site only — see eligibility")
    if 1331 <= n <= 1370: return ("Mock Jury", "Mock jury", "Easy", "US only")
    if 1371 <= n <= 1430: return ("Focus Group", "Focus group", "Easy", "US only")
    if 1431 <= n <= 1480: return ("Microtask", "Microtask", "Easy", "US; some platforms worldwide")
    if 1481 <= n <= 1520: return ("Transcription", "Transcription", "Moderate", "US only")
    if 1521 <= n <= 1560: return ("Receipt/Loyalty", "Receipt app", "Very Easy", "US only")
    if 1561 <= n <= 1610: return ("Buyback", "Buyback", "Easy", "US only")
    if 1611 <= n <= 1640: return ("Recycling", "Recycling payout", "Easy", "State/program specific — see eligibility")
    if 1641 <= n <= 1700: return ("Government", "Civic pay", "Easy", "Jurisdiction specific — see eligibility")
    if 1701 <= n <= 1730: return ("Pet Sitting", "Pet sitting", "Moderate", "US only")
    if 1731 <= n <= 1770: return ("Tutoring", "Tutoring", "Moderate", "US; some platforms worldwide")
    if 1771 <= n <= 1800: return ("Design Market", "Design marketplace", "Moderate", "Worldwide")
    if 1801 <= n <= 1850: return ("Mystery Shopping", "Mystery shopping", "Easy", "US only")
    if 1851 <= n <= 1870: return ("Car Advertising", "Car advertising", "Easy", "US only")
    if 1871 <= n <= 1920: return ("Energy Switching", "Energy switch incentive", "Easy", "State specific — see eligibility")
    if 1921 <= n <= 1970: return ("Store Signup", "Signup bonus", "Very Easy", "US only")
    if 2021 <= n <= 2100: return ("Lead Sourcing", "Lead-sourcing platform", "Moderate", "US; some platforms worldwide")
    if 2101 <= n <= 2200: return ("Bank Bonus", "Bank bonus", "Easy", "US; state/branch restrictions may apply — see eligibility")
    if 2201 <= n <= 2300: return ("Referral Bonus", "Refer-a-friend bonus", "Very Easy", "US only")
    if 2301 <= n <= 2420: return ("Bank Bonus", "Bank bonus", "Easy", "US; state/branch restrictions may apply — see eligibility")
    if 2421 <= n <= 2540: return ("Referral Bonus", "Refer-a-friend bonus", "Very Easy", "US only")
    if 2541 <= n <= 2620: return ("Clinical Trial", "Research study", "Moderate", "US; study site only — see eligibility")
    if 2621 <= n <= 2680: return ("Energy Switching", "Energy switch incentive", "Easy", "State specific — see eligibility")
    if 2681 <= n <= 2740: return ("Fintech Bonus", "Fintech signup bonus", "Easy", "US only")
    if 2741 <= n <= 2860: return ("Bank Bonus", "Bank bonus", "Easy", "US; state/branch restrictions may apply — see eligibility")
    if 2861 <= n <= 2980: return ("Referral Bonus", "Refer-a-friend bonus", "Very Easy", "US only")
    if 2981 <= n <= 3040: return ("Business Banking", "Business bank bonus", "Moderate", "US; business account required")
    if 3041 <= n <= 3100: return ("Research Study", "University research study", "Moderate", "US; study site only — see eligibility")
    if 3101 <= n <= 3129: return ("Freelance Skill", "Translation/voice/proofreading", "Moderate", "US; some platforms worldwide")
    if 3161 <= n <= 3200: return ("Rent Assets", "Rent out your assets", "Moderate", "US; some platforms worldwide")
    if 3201 <= n <= 3320: return ("Bank Bonus", "Bank bonus", "Easy", "US; state/branch restrictions may apply — see eligibility")
    if 3321 <= n <= 3440: return ("Referral Bonus", "Refer-a-friend bonus", "Very Easy", "US only")
    if 3441 <= n <= 3500: return ("Microtask", "Microtask", "Easy", "US; some platforms worldwide")
    if 3501 <= n <= 3518: return ("Competition", "Skill competition", "Moderate", "US; some worldwide")
    if 3561 <= n <= 3620: return ("Signup Bonus", "Signup/matching bonus", "Very Easy", "US only")
    if 3621 <= n <= 3720: return ("Civic Pay", "Poll worker pay", "Easy", "County specific — see eligibility")
    if 3721 <= n <= 3840: return ("Bank Bonus", "Bank bonus", "Easy", "US; state/branch restrictions may apply — see eligibility")
    if 3841 <= n <= 3960: return ("Referral Bonus", "Refer-a-friend bonus", "Very Easy", "US only")
    if 3961 <= n <= 4040: return ("Clinical Trial", "Research study", "Moderate", "US; study site only — see eligibility")
    if 4041 <= n <= 4100: return ("Energy Switching", "Energy switch incentive", "Easy", "State specific — see eligibility")
    if 4101 <= n <= 4160: return ("Business Banking", "Business bank bonus", "Moderate", "US; business account required")
    if 4161 <= n <= 4280: return ("Bank Bonus", "Bank bonus", "Easy", "US; state/branch restrictions may apply — see eligibility")
    if 4281 <= n <= 4400: return ("Referral Bonus", "Refer-a-friend bonus", "Very Easy", "US only")
    if 4401 <= n <= 4500: return ("Civic Pay", "Poll worker pay", "Easy", "County specific — see eligibility")
    if 4501 <= n <= 4560: return ("Research Study", "University research study", "Moderate", "US; study site only — see eligibility")
    if 4561 <= n <= 4640: return ("Clinical Trial", "Research study", "Moderate", "US; study site only — see eligibility")
    if 4641 <= n <= 4760: return ("Bank Bonus", "Bank bonus", "Easy", "US; state/branch restrictions may apply — see eligibility")
    if 4761 <= n <= 4880: return ("Referral Bonus", "Refer-a-friend bonus", "Very Easy", "US only")
    if 4881 <= n <= 4980: return ("Civic Pay", "Poll worker pay", "Easy", "County specific — see eligibility")
    if 4981 <= n <= 5080: return ("Card Bonus", "Credit card welcome offer", "Easy", "US only")
    if 5081 <= n <= 5200: return ("Bank Bonus", "Bank bonus", "Easy", "US; state/branch restrictions may apply — see eligibility")
    if 5201 <= n <= 5320: return ("Referral Bonus", "Refer-a-friend bonus", "Very Easy", "US only")
    if 5321 <= n <= 5420: return ("Card Bonus", "Credit card welcome offer", "Easy", "US only")
    if 5421 <= n <= 5480: return ("Lead Sourcing", "Lead-sourcing platform", "Moderate", "US; some platforms worldwide")
    if 5481 <= n <= 5540: return ("Energy Switching", "Energy switch incentive", "Easy", "State specific — see eligibility")
    if 5541 <= n <= 5660: return ("Bank Bonus", "Bank bonus", "Easy", "US; state/branch restrictions may apply — see eligibility")
    if 5661 <= n <= 5780: return ("Referral Bonus", "Refer-a-friend bonus", "Very Easy", "US only")
    if 5781 <= n <= 5880: return ("Brokerage Promo", "Brokerage/stock-media/rental bonus", "Moderate", "US; some worldwide")
    if 5881 <= n <= 5940: return ("Business Banking", "Business/student/CD-IRA bonus", "Moderate", "US only")
    if 5941 <= n <= 6060: return ("Bank Bonus", "Bank bonus", "Easy", "US; state/branch restrictions may apply — see eligibility")
    if 6061 <= n <= 6180: return ("Referral Bonus", "Refer-a-friend bonus", "Very Easy", "US only")
    if 6181 <= n <= 6280: return ("Civic Pay", "Poll worker pay", "Easy", "County specific — see eligibility")
    if 6281 <= n <= 6340: return ("Energy Switching", "Energy switch incentive", "Easy", "State specific — see eligibility")
    if 6341 <= n <= 6400: return ("Telecom Promo", "ISP signup promo", "Easy", "US only")
    if 6401 <= n <= 6480: return ("Signup Bonus", "Signup/matching bonus", "Very Easy", "US only")
    return ("Other Online", "Offer", "Easy", "US only")  # overflow R1971-R2020

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

st, dbv = req("GET", "/rest/v1/routes?select=route_id&limit=5000")
existing = {r["route_id"] for r in dbv}

ins = upd = rej = 0
for f in sorted(glob.glob("/home/hatch/workspace/upmore/qa/verification/R*.json")):
    rid = os.path.basename(f)[:5]
    if rid < "R0851":
        continue
    try:
        d = json.load(open(f))
    except (FileNotFoundError, json.JSONDecodeError):
        continue
    v = norm_verdict(d.get("verdict"))
    checked = d.get("checked_at") or NOW
    off = d.get("official_url") or d.get("official_source_url") or ""
    if rid in DEMOTE:
        v = "reject"
        note = "OVERRIDE (independent review): " + str(DEMOTE[rid])[:400]
    else:
        note = str(d.get("notes") or "")[:400]
    if v == "reject":
        if log_proof(rid, checked, "rejected", f"Expansion reject: {note}", off):
            rej += 1
        continue
    provider = provider_of(d)
    category, method, difficulty, geo = lane_of(rid)
    pq = (d.get("payout_quote") or "").strip()
    payout_text = pq if pq else ("Variable — no fixed payout. " + str(d.get("biggest_catch") or "")[:240])
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
    log_proof(rid, checked, "verified", f"Expansion verify: {note}", off)

# rejects from worker logs: R####|Provider|checked_at|url|reason
for f in sorted(glob.glob("/home/hatch/workspace/upmore/qa/discovery/rejects-g*.txt")):
    for line in open(f):
        parts = line.rstrip("\n").split("|", 4)
        if len(parts) != 5 or not re.match(r"^R\d{4}$", parts[0]):
            continue
        rid, _prov, checked, url, reason = parts
        if rid < "R0851":
            continue
        if log_proof(rid, checked or NOW, "rejected", f"Expansion reject: {reason[:400]}", url):
            rej += 1

print(f"batch21: inserted={ins} updated={upd} rejected-logged={rej} demoted={len(DEMOTE)}")

# Catalog demotions (adjudication entries below R0851): retire the superseded DB rows.
cat_dem = 0
for rid, reason in DEMOTE.items():
    if rid >= "R0851":
        continue
    st, _ = req("PATCH", f"/rest/v1/routes?route_id=eq.{rid}", {"status": "rejected"})
    if st in (200, 204):
        cat_dem += 1
        log_proof(rid, NOW, "rejected", f"RETIRED (independent review): {str(reason)[:400]}", "")
    else:
        print("CATALOG DEMOTE FAILED", rid, st)
print(f"batch21: catalog_demoted={cat_dem}")
