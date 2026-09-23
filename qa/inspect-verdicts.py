#!/usr/bin/env python3
"""Independent inspection of every verification evidence file.
Normalizes verdict spellings, extracts provider, flags weak verifications
for human review, detects duplicates and conflicts with prior verdicts.
Output: qa/verification-inspection.json
"""
import json, glob, re, sys, os
from collections import Counter, defaultdict
from urllib.parse import urlparse

sys.path.insert(0, "/home/hatch/workspace/upmore/qa")
from db import req

AGGREGATORS = {
    "doctofcredit.com", "nerdwallet.com", "bankrate.com", "thepennyhoarder.com",
    "wallethacks.com", "moneyunder30.com", "clark.com", "sidehustlenation.com",
    "wellkeptwallet.com", "dollarsprout.com", "moneycrashers.com", "swagbucks.com",
    "reddit.com", "youtube.com", "tiktok.com", "facebook.com", "instagram.com",
    "forbes.com", "investopedia.com", "creditcards.com", "thepointsguy.com",
    "upgradedpoints.com", "bankbonuses.com", "everybankbonus.com", "bankbonus.com",
    "mybanktracker.com", "depositaccounts.com", "valuepenguin.com", "fool.com",
    "usnews.com", "cnn.com", "kiplinger.com", "aarp.org", "consumerreports.org",
}

def host(url):
    try:
        h = urlparse(url).netloc.lower()
        return h[4:] if h.startswith("www.") else h
    except Exception:
        return ""

def extract_provider(d):
    """Best-effort provider name from evidence."""
    c1 = ""
    try:
        c1 = d["critical"]["c1"]["evidence"] or ""
    except Exception:
        pass
    # provider usually precedes an em dash / en dash / ' - '
    for sep in ["\u2014", "\u2013", " - ", " \u2014 "]:
        if sep in c1:
            cand = c1.split(sep)[0].strip()
            if 2 <= len(cand) <= 60:
                return cand
            break
    # fallback: from official url domain
    url = d.get("official_url") or d.get("official_source_url") or ""
    h = host(url)
    if h:
        core = h.split(".")[0] if not h.startswith("support.") else h.split(".")[1]
        return core.replace("-", " ").title()
    return "Unknown"

def norm_verdict(v):
    v = str(v or "").strip().lower()
    if v in ("verify", "verified", "pass", "pass_verify"):
        return "verify"
    if v in ("reject", "rejected", "fail"):
        return "reject"
    return v or "?"

files = sorted(glob.glob("/home/hatch/workspace/upmore/qa/verification/R*.json"))
results = {}
by_provider_payout = defaultdict(list)

for f in files:
    rid = os.path.basename(f)[:5]
    try:
        d = json.load(open(f))
    except Exception as e:
        results[rid] = {"ok": False, "flags": [f"unparseable: {e}"]}
        continue
    keys = set(d.keys())
    canon = {"app_links","biggest_catch","catches","checked_at","critical","eligibility",
             "notes","official_url","payout_quote","route_id","standard","steps",
             "terms_url","timing","upfront_fee","verdict","weasel_words"}
    v = norm_verdict(d.get("verdict"))
    flags = []
    if v not in ("verify", "reject"):
        flags.append(f"unknown-verdict:{d.get('verdict')}")
    if d.get("route_id") != rid:
        flags.append(f"route_id-mismatch:{d.get('route_id')}")
    missing = canon - keys
    if missing:
        flags.append(f"missing-keys:{sorted(missing)}")
    off = d.get("official_url") or d.get("official_source_url") or ""
    if v == "verify":
        if not off:
            flags.append("no-official-url")
        else:
            h = host(off)
            if h in AGGREGATORS:
                flags.append(f"aggregator-as-proof:{h}")
        pq = d.get("payout_quote")
        if not pq or not str(pq).strip():
            flags.append("empty-payout_quote")
        elif re.search(r"(up to|as high as)", str(pq), re.I) and not re.search(r"\d", str(pq)):
            flags.append("vague-payout-no-number")
        st = d.get("steps")
        if not st:
            flags.append("empty-steps")
        if not d.get("timing"):
            flags.append("empty-timing")
        ca = d.get("catches")
        if not ca:
            flags.append("empty-catches")
        chk = str(d.get("checked_at") or "")
        if not chk.startswith("2026-09-2"):
            flags.append(f"stale-checked_at:{chk[:16]}")
        el = d.get("eligibility")
        if not el:
            flags.append("empty-eligibility")
        prov = extract_provider(d)
        # weasel-word scan on payout_quote + notes
        text = f"{pq} {d.get('notes','')}".lower()
        weasels = [w for w in ["guaranteed income", "make $", "earn up to $"] if w in text]
        # duplicate key: provider + normalized payout
        normpay = re.sub(r"[^a-z0-9]+", "", str(pq).lower())[:80]
        by_provider_payout[(prov.lower(), normpay)].append(rid)
    else:
        prov = extract_provider(d)
        pq = d.get("payout_quote")
        if pq:
            flags.append("reject-with-payout_quote")
        if d.get("steps"):
            flags.append("reject-with-steps")
    results[rid] = {"ok": not flags, "verdict": v, "provider": prov if v=="verify" else extract_provider(d),
                    "flags": flags, "file": f,
                    "payout": str(d.get("payout_quote"))[:120] if v=="verify" else None,
                    "official": off or None}

# duplicate detection across verify files
for key, rids in by_provider_payout.items():
    if len(rids) > 1:
        for r in rids:
            results[r]["flags"].append(f"possible-duplicate-of:{[x for x in rids if x != r]}")

# prior-verdict conflicts: check DB proof_log for earlier verdicts on same route
st, pl = req("GET", "/rest/v1/proof_log?select=route_id,result,checked_at&limit=2000")
prior = {}
for row in pl:
    rid = row["route_id"]
    res = row["result"]
    if rid not in prior:
        prior[rid] = []
    prior[rid].append(res)
for rid, r in results.items():
    if rid in prior and r["verdict"] == "verify":
        prev = prior[rid]
        if any(p == "rejected" for p in prev):
            r["flags"].append(f"conflict:previously-rejected{prev}")

st, dbv = req("GET", "/rest/v1/routes?select=route_id,status&status=eq.verified&limit=1000")
db_verified = {r["route_id"] for r in dbv}

verify_ids = [rid for rid, r in results.items() if r["verdict"] == "verify"]
reject_ids = [rid for rid, r in results.items() if r["verdict"] == "reject"]
flagged = {rid: r for rid, r in results.items() if r["flags"]}
new_disc = [rid for rid in verify_ids if rid >= "R0536"]
catalog_new = [rid for rid in verify_ids if rid < "R0536" and rid not in db_verified]
catalog_re = [rid for rid in verify_ids if rid < "R0536" and rid in db_verified]

out = {
    "total_files": len(files),
    "verdict_counts": dict(Counter(r["verdict"] for r in results.values())),
    "db_verified_now": len(db_verified),
    "verify_discovery_new_ids": len(new_disc),
    "verify_catalog_not_yet_verified": len(catalog_new),
    "verify_catalog_already_verified": len(catalog_re),
    "flagged_count": len(flagged),
    "flagged": flagged,
    "results": results,
}
json.dump(out, open("/home/hatch/workspace/upmore/qa/verification-inspection.json", "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k not in ("flagged", "results")}, indent=1))
print("\n--- FLAG CATEGORIES ---")
fc = Counter()
for rid, r in flagged.items():
    for f in r["flags"]:
        fc[f.split(":")[0]] += 1
print(json.dumps(dict(fc), indent=1))
