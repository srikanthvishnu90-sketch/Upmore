#!/usr/bin/env python3
"""Validate R0851+ evidence files: 23-key schema, numeric sanity, aggregator check,
cross-file duplicate detection. Output: qa/validation-1500.json"""
import json, glob, os, re
from urllib.parse import urlparse
from collections import defaultdict

AGG = {"doctofcredit.com", "nerdwallet.com", "bankrate.com", "thepennyhoarder.com",
       "wallethacks.com", "clark.com", "dollarsprout.com", "reddit.com", "forbes.com",
       "investopedia.com", "creditcards.com", "thepointsguy.com", "upgradedpoints.com",
       "mybanktracker.com", "depositaccounts.com", "youtube.com", "tiktok.com",
       "facebook.com", "bankbonuses.com", "everybankbonus.com", "wallethacks.com",
       "moneyunder30.com", "fool.com", "usnews.com", "cnn.com", "kiplinger.com"}

KEYS17 = ["route_id", "verdict", "official_url", "terms_url", "payout_quote", "steps",
          "catches", "biggest_catch", "eligibility", "timing", "upfront_fee",
          "weasel_words", "app_links", "checked_at", "critical", "standard", "notes"]
NUMK = ["payout_min_usd", "payout_max_usd", "payout_value_note",
        "time_min_minutes", "time_max_minutes", "numeric_basis"]

def host(u):
    try:
        h = urlparse(u or "").netloc.lower()
        return h[4:] if h.startswith("www.") else h
    except Exception:
        return ""

# existing catalog providers for dup detection
d = json.load(open("/home/hatch/workspace/upmore/src/data/upmore-data.json"))
catprov = defaultdict(list)
for r in d["routes"]:
    catprov[r["provider"].lower()].append(r["id"])

report = {"files": 0, "verify": 0, "reject": 0, "issues": [], "dup_groups": []}
by_host = defaultdict(list)
by_provider = defaultdict(list)

files = sorted(glob.glob("/home/hatch/workspace/upmore/qa/verification/R*.json"))
for f in files:
    rid = os.path.basename(f)[:5]
    if rid < "R0851":
        continue
    report["files"] += 1
    try:
        j = json.load(open(f))
    except Exception as e:
        report["issues"].append({"id": rid, "issue": f"unparseable: {e}"})
        continue
    v = str(j.get("verdict", "")).strip().lower()
    if v not in ("verify", "verified", "reject"):
        report["issues"].append({"id": rid, "issue": f"bad verdict {j.get('verdict')!r}"})
        continue
    if v == "reject":
        report["reject"] += 1
        continue
    report["verify"] += 1
    missing = [k for k in KEYS17 + NUMK if k not in j]
    if missing:
        report["issues"].append({"id": rid, "issue": f"missing keys {missing}"})
    if j.get("payout_quote") is None:
        report["issues"].append({"id": rid, "issue": "verify with null payout_quote"})
    if not j.get("steps"):
        report["issues"].append({"id": rid, "issue": "verify with empty steps"})
    h = host(j.get("official_url"))
    if h in AGG:
        report["issues"].append({"id": rid, "issue": f"aggregator as official_url: {h}"})
    try:
        pmin = float(j["payout_min_usd"]); pmax = float(j["payout_max_usd"])
        tmin = float(j["time_min_minutes"]); tmax = float(j["time_max_minutes"])
        if not (0 <= pmin <= pmax):
            report["issues"].append({"id": rid, "issue": f"payout range insane {pmin}-{pmax}"})
        if not (1 <= tmin <= tmax <= 10080):
            report["issues"].append({"id": rid, "issue": f"time range insane {tmin}-{tmax}"})
        if pmax > 100000:
            report["issues"].append({"id": rid, "issue": f"suspicious payout_max {pmax}"})
    except (TypeError, ValueError, KeyError):
        report["issues"].append({"id": rid, "issue": "numeric keys not numbers"})
    # provider guess for dup detection
    c1 = ""
    try:
        c1 = j["critical"]["c1"]["evidence"] or ""
    except Exception:
        pass
    prov = ""
    for sep in ["\u2014", "\u2013"]:
        if sep in c1:
            prov = c1.split(sep)[0].strip().lower()
            break
    by_host[h].append(rid)
    if prov:
        by_provider[prov].append(rid)
        if prov in catprov:
            report["issues"].append(
                {"id": rid, "issue": f"possible catalog duplicate of {catprov[prov]} (provider={prov})"})

for h, rids in by_host.items():
    if len(rids) > 1 and h:
        report["dup_groups"].append({"host": h, "ids": sorted(rids)})
for p, rids in by_provider.items():
    if len(rids) > 1:
        report["dup_groups"].append({"provider": p, "ids": sorted(rids)})

json.dump(report, open("/home/hatch/workspace/upmore/qa/validation-1500.json", "w"), indent=1)
print(f"files={report['files']} verify={report['verify']} reject={report['reject']} "
      f"issues={len(report['issues'])} dup_groups={len(report['dup_groups'])}")
for i in report["issues"][:30]:
    print("ISSUE:", i["id"], i["issue"][:110])
for g in report["dup_groups"][:20]:
    print("DUP:", g)
