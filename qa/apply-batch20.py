#!/usr/bin/env python3
"""Apply batch 20: remaining catalog verification evidence (R0001-R0535).

Adjudicated overrides (verify->reject) are baked in below.
Idempotent: routes PATCH is a natural upsert; proof_log rows are keyed
on (route_id, checked_at) and skipped if already present.
"""
import json, glob, os, sys, datetime
sys.path.insert(0, "/home/hatch/workspace/upmore/qa")
from db import req

NOW = datetime.datetime.now(datetime.timezone.utc).isoformat()

# Manual adjudications: worker said verify, independent review says reject.
DEMOTE = {
    "R0152": "duplicate of verified R0355 (Microsoft Rewards) — worker-admitted same program",
    "R0155": "sub-feature of verified R0119 (Fetch eReceipts) — not a separate way to make money",
    "R0349": "Phemex Learn & Earn pays a cashback voucher (trading-fee rebate on own trades) — risk-capital, not income",
    "R0352": "Bitget Learn2Earn — rewards are promotional/trading-linked, not fixed income",
    "R0440": "appKarma: no direct official-FAQ evidence; payout details only via third-party reviews quoting the FAQ",
    "R0508": "duplicate of main Swagbucks route — same account, currency and redemption path (worker-admitted)",
    "R0509": "sub-feature of verified R0355 (Microsoft Rewards mobile search) — same program",
    "R0516": "sub-feature of R0441 (FeaturePoints daily check-in is a feature of the same app)",
    "R0523": "Toluna: official toluna.com terms page not fetched — reviews only, insufficient",
    "R0527": "Receipt Hog: official terms not fetched — reviews only, insufficient",
}

def norm_verdict(v):
    v = str(v or "").strip().lower()
    return "verify" if v in ("verify", "verified") else ("reject" if v in ("reject", "rejected") else v)

def mech_payout_text(d):
    bc = str(d.get("biggest_catch") or "").strip()
    return "Variable — no fixed payout. " + bc[:240]

def steps_for_db(d):
    out = []
    for s in d.get("steps") or []:
        t = s if isinstance(s, str) else (s.get("text") or "")
        if t.strip():
            out.append({"text": t.strip(), "warn": "", "done_when": ""})
    return out

def proof_exists(route_id, checked_at):
    st, rows = req("GET", f"/rest/v1/proof_log?select=id&route_id=eq.{route_id}&checked_at=eq.{checked_at}")
    return bool(rows)

def log_proof(route_id, checked_at, result, notes, source_url):
    if proof_exists(route_id, checked_at):
        return False
    st, _ = req("POST", "/rest/v1/proof_log",
                {"route_id": route_id, "checked_at": checked_at, "result": result,
                 "notes": notes[:2000], "source_url": (source_url or "")[:2000]})
    if st not in (200, 201):
        print("PROOF-LOG FAILED", route_id, st)
    return True

st, dbv = req("GET", "/rest/v1/routes?select=route_id,status&limit=1000")
db_status = {r["route_id"]: r["status"] for r in dbv}

applied = rejected = skipped = demoted = 0
for f in sorted(glob.glob("/home/hatch/workspace/upmore/qa/verification/R*.json")):
    rid = os.path.basename(f)[:5]
    if rid >= "R0536":
        continue  # discovery lane handled separately
    d = json.load(open(f))
    v = norm_verdict(d.get("verdict"))
    if rid in DEMOTE:
        v = "reject"
        demote_note = "OVERRIDE (independent review): " + DEMOTE[rid]
    else:
        demote_note = None
    checked = d.get("checked_at") or NOW
    off = d.get("official_url") or d.get("official_source_url") or ""
    if v == "verify":
        pq = (d.get("payout_quote") or "").strip()
        payout_text = pq if pq else mech_payout_text(d)
        patch = {
            "status": "verified",
            "verified_at": NOW,
            "verified_source_url": off[:2000] or None,
            "payout_text": payout_text[:2000],
            "payout_timing": (str(d.get("timing") or "")[:1000] or None),
            "steps": steps_for_db(d),
            "catches": [str(c)[:1000] for c in (d.get("catches") or [])],
        }
        if db_status.get(rid) == "verified":
            skipped += 1  # DB stands; earlier careful corrections preserved
            continue
        st, _ = req("PATCH", f"/rest/v1/routes?route_id=eq.{rid}", patch)
        if st not in (200, 204):
            print("PATCH FAILED", rid, st); continue
        log_proof(rid, checked, "verified",
                  f"Batch 20 verify: {str(d.get('notes') or '')[:400]}", off)
        applied += 1
    else:
        note = demote_note or f"Batch 20 reject: {str(d.get('notes') or '')[:400]}"
        if log_proof(rid, checked, "rejected", note, off):
            rejected += 1
        else:
            skipped += 1

# R0049/R0079 dedupe: same M&T offer — keep R0079, retire R0049
st, rows = req("GET", "/rest/v1/routes?select=status&route_id=eq.R0049")
if rows and rows[0]["status"] == "verified":
    req("PATCH", "/rest/v1/routes?route_id=eq.R0049",
        {"status": "unverified", "verified_at": None, "verified_source_url": None})
    log_proof("R0049", NOW, "rejected",
              "OVERRIDE (independent review): duplicate of verified R0079 — same M&T Bank personal checking promotion; counted once.",
              "")
    print("R0049 retired as duplicate of R0079")

print(f"batch20: applied={applied} rejected={rejected} skipped={skipped} demoted={len(DEMOTE)}")
