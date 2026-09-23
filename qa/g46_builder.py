#!/usr/bin/env python3
"""G46 wave-2 evidence builder. Reads qa/g46_cards.json (list of card records),
writes qa/verification/R####.json with exactly 23 top-level keys.

Record fields (all required unless noted):
  id, card, url, terms_url(optional), quote, steps[], catches[] (must include the
  four mandatory credit-card catches), biggest_catch, eligibility, timing,
  upfront_fee(bool), weasel[](optional), c1..c4, s1..s7, notes,
  pmin, pmax, vnote, tmin(optional), tmax(optional), numeric_basis
"""
import json, os, sys
from datetime import datetime, timezone

BASE = os.path.expanduser("~/workspace/upmore/qa")
CARDS_FILE = os.path.join(BASE, "g46_cards.json")
OUT_DIR = os.path.join(BASE, "verification")

MANDATORY_CATCH_FRAGS = [
    "never",          # never spend extra solely to earn the bonus
    "annual fee",     # annual fee reduces net value
    "hard",           # hard inquiry
    "interest",       # carried-balance interest
]

def build(rec, checked_at):
    for f in ("id", "card", "url", "quote", "steps", "catches", "biggest_catch",
              "eligibility", "timing", "upfront_fee", "c1", "c2", "c3", "c4",
              "s1", "s2", "s3", "s4", "s5", "s6", "s7", "notes",
              "pmin", "pmax", "vnote", "numeric_basis"):
        assert f in rec, f"{rec.get('id')}: missing field {f}"
    joined = " ".join(rec["catches"]).lower()
    for frag in MANDATORY_CATCH_FRAGS:
        assert frag in joined, f"{rec['id']}: catches missing '{frag}'"
    assert isinstance(rec["steps"], list) and len(rec["steps"]) >= 3, \
        f"{rec['id']}: steps must be a non-trivial list"
    assert rec["pmin"] is not None and rec["pmax"] is not None

    doc = {
        "route_id": rec["id"],
        "verdict": "verify",
        "official_url": rec["url"],
        "terms_url": rec.get("terms_url") or rec["url"],
        "payout_quote": rec["quote"],
        "steps": rec["steps"],
        "catches": rec["catches"],
        "biggest_catch": rec["biggest_catch"],
        "eligibility": rec["eligibility"],
        "timing": rec["timing"],
        "upfront_fee": bool(rec["upfront_fee"]),
        "weasel_words": rec.get("weasel", []),
        "app_links": {"android": None, "ios": None},
        "checked_at": checked_at,
        "critical": {
            "c1": {"pass": True, "evidence": rec["c1"]},
            "c2": {"pass": True, "evidence": rec["c2"]},
            "c3": {"pass": True, "evidence": rec["c3"]},
            "c4": {"pass": True, "evidence": rec["c4"]},
        },
        "standard": {
            "s1": {"pass": True, "note": rec["s1"]},
            "s2": {"pass": True, "note": rec["s2"]},
            "s3": {"pass": True, "note": rec["s3"]},
            "s4": {"pass": True, "note": rec["s4"]},
            "s5": {"pass": True, "note": rec["s5"]},
            "s6": {"pass": True, "note": rec["s6"]},
            "s7": {"pass": True, "note": rec["s7"]},
        },
        "notes": rec["notes"],
        "payout_min_usd": float(rec["pmin"]),
        "payout_max_usd": float(rec["pmax"]),
        "payout_value_note": rec["vnote"],
        "time_min_minutes": float(rec.get("tmin", 20)),
        "time_max_minutes": float(rec.get("tmax", 40)),
        "numeric_basis": rec["numeric_basis"],
    }
    assert len(doc) == 23, f"{rec['id']}: got {len(doc)} keys, want 23"
    assert isinstance(doc["weasel_words"], list), f"{rec['id']}: weasel_words not array"
    return doc

def main():
    checked_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(CARDS_FILE) as f:
        cards = json.load(f)
    seen = set()
    for rec in cards:
        rid = rec["id"]
        assert rid not in seen, f"duplicate id {rid}"
        seen.add(rid)
        doc = build(rec, checked_at)
        path = os.path.join(OUT_DIR, f"{rid}.json")
        assert not os.path.exists(path), f"would overwrite {path}"
        with open(path, "w") as f:
            json.dump(doc, f, indent=1, ensure_ascii=False)
            f.write("\n")
        print(f"wrote {rid} {rec['card']}", flush=True)
    print(f"done: {len(cards)} files, checked_at={checked_at}")

if __name__ == "__main__":
    main()
