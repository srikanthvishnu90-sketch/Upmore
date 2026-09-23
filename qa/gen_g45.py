#!/usr/bin/env python3
"""G45 evidence writer: validates exactly 23 keys (17 canonical + 6 numeric) and writes qa/verification/R####.json."""
import json, sys, os

CANON = ["route_id","verdict","official_url","terms_url","payout_quote","steps","catches",
         "biggest_catch","eligibility","timing","upfront_fee","weasel_words","app_links",
         "checked_at","critical","standard","notes"]
NUMERIC = ["payout_min_usd","payout_max_usd","payout_value_note","time_min_minutes",
           "time_max_minutes","numeric_basis"]

def write_evidence(d):
    keys = list(d.keys())
    if len(keys) != 23 or set(keys) != set(CANON + NUMERIC):
        missing = set(CANON + NUMERIC) - set(keys)
        extra = set(keys) - set(CANON + NUMERIC)
        raise ValueError(f"key count {len(keys)}; missing={missing} extra={extra}")
    for k in ["c1","c2","c3","c4"]:
        assert set(d["critical"][k].keys()) == {"pass","evidence"}, k
    for k in ["s1","s2","s3","s4","s5","s6","s7"]:
        assert set(d["standard"][k].keys()) == {"pass","note"}, k
    assert set(d["app_links"].keys()) == {"android","ios"}
    assert isinstance(d["upfront_fee"], bool)
    assert isinstance(d["steps"], list) and isinstance(d["catches"], list)
    assert isinstance(d["weasel_words"], list)
    for k in ["payout_min_usd","payout_max_usd","time_min_minutes","time_max_minutes"]:
        assert isinstance(d[k], (int, float)), k
    assert d["verdict"] in ("verify","reject")
    path = f"/home/hatch/workspace/upmore/qa/verification/{d['route_id']}.json"
    if os.path.exists(path):
        raise FileExistsError(path)
    with open(path, "w") as f:
        json.dump(d, f, indent=1)
    print("wrote", path)
