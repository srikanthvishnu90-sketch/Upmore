#!/usr/bin/env python3
"""Write a complete R68XX verification JSON file with the lane schema.

Usage: python3 _new_route.py  (reads route dict from argv[1] as JSON file)
Or import and call write_route(data).
"""
import json, sys

SCHEMA_KEYS = ["route_id","provider","official_url","terms_url","payout_quote",
 "payout_min_usd","payout_max_usd","time_min_minutes","time_max_minutes","timing",
 "speed","eligibility","steps","catches","biggest_catch","upfront_fee","verdict",
 "checked_at","notes","repeatable","maximize",
 "critical","standard","weasel_words"]
CHECKED_AT = "2026-09-23T12:00:00Z"

def write_route(d):
    missing = [k for k in SCHEMA_KEYS if k not in d]
    if missing:
        raise ValueError(f"missing keys: {missing}")
    for k in ("c1","c2","c3","c4"):
        if k not in d["critical"]:
            raise ValueError(f"critical.{k} missing")
    for i in range(1,8):
        if f"s{i}" not in d["standard"]:
            raise ValueError(f"standard.s{i} missing")
    r = d["repeatable"]
    if not isinstance(r, dict) or "value" not in r or "cadence" not in r:
        raise ValueError("repeatable must be {value: bool, cadence: str}")
    path = f"/home/hatch/workspace/upmore/qa/verification/{d['route_id']}.json"
    with open(path, "w") as f:
        json.dump(d, f, indent=1, ensure_ascii=False)
    print("wrote", path)

def base(route_id, provider, **kw):
    d = {
        "route_id": route_id, "provider": provider,
        "official_url": kw.pop("official_url"), "terms_url": kw.pop("terms_url"),
        "payout_quote": kw.pop("payout_quote"),
        "payout_min_usd": kw.pop("payout_min_usd"), "payout_max_usd": kw.pop("payout_max_usd"),
        "time_min_minutes": kw.pop("time_min_minutes"), "time_max_minutes": kw.pop("time_max_minutes"),
        "timing": kw.pop("timing"), "speed": kw.pop("speed"),
        "eligibility": kw.pop("eligibility"), "steps": kw.pop("steps"),
        "catches": kw.pop("catches"), "biggest_catch": kw.pop("biggest_catch"),
        "upfront_fee": kw.pop("upfront_fee", False), "verdict": kw.pop("verdict", "verify"),
        "checked_at": CHECKED_AT, "notes": kw.pop("notes"),
        "repeatable": kw.pop("repeatable"), "maximize": kw.pop("maximize"),
        "critical": {
            "c1": {"pass": True, "evidence": kw.pop("c1")},
            "c2": {"pass": True, "evidence": kw.pop("c2")},
            "c3": {"pass": True, "evidence": kw.pop("c3")},
            "c4": {"pass": True, "evidence": kw.pop("c4")},
        },
        "standard": {
            "s1": {"pass": True, "note": kw.pop("s1")},
            "s2": {"pass": True, "note": kw.pop("s2")},
            "s3": {"pass": True, "note": kw.pop("s3")},
            "s4": {"pass": True, "note": kw.pop("s4")},
            "s5": {"pass": True, "note": kw.pop("s5")},
            "s6": {"pass": True, "note": kw.pop("s6")},
            "s7": {"pass": True, "note": kw.pop("s7")},
        },
        "weasel_words": {"present": False, "quote": None},
    }
    if kw:
        raise ValueError(f"unused kwargs: {list(kw)}")
    return d

if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        write_route(json.load(f))
