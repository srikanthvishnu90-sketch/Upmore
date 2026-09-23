#!/usr/bin/env python3
"""Validate evidence JSON files for the SAME-DAY FOCUS GROUPS & MOCK JURIES lane."""
import json, sys, glob, os

REQUIRED_TOP = ["route_id","provider","verdict","critical","standard","speed",
    "repeatable","maximize","official_url","terms_url","notes","payout_min_usd",
    "payout_max_usd","payout_quote","time_min_minutes","time_max_minutes",
    "timing","steps","catches","biggest_catch","eligibility","upfront_fee",
    "checked_at","weasel_words"]

def check(path):
    errs = []
    base = os.path.basename(path)
    try:
        with open(path) as f:
            d = json.load(f)
    except Exception as e:
        return [f"{base}: JSON parse error: {e}"]
    for k in REQUIRED_TOP:
        if k not in d:
            errs.append(f"{base}: missing top-level key '{k}'")
    if d.get("route_id") and d["route_id"] != base.replace(".json",""):
        errs.append(f"{base}: route_id {d['route_id']} != filename")
    if d.get("verdict") not in ("verify","reject"):
        errs.append(f"{base}: verdict must be verify|reject, got {d.get('verdict')}")
    crit = d.get("critical", {})
    for c in ("c1","c2","c3","c4"):
        if c not in crit:
            errs.append(f"{base}: critical.{c} missing")
        else:
            if not isinstance(crit[c].get("pass"), bool):
                errs.append(f"{base}: critical.{c}.pass not bool")
            if not crit[c].get("evidence"):
                errs.append(f"{base}: critical.{c}.evidence empty")
    std = d.get("standard", {})
    for i in range(1,8):
        s = f"s{i}"
        if s not in std:
            errs.append(f"{base}: standard.{s} missing")
        else:
            if not isinstance(std[s].get("pass"), bool):
                errs.append(f"{base}: standard.{s}.pass not bool")
            if not std[s].get("note"):
                errs.append(f"{base}: standard.{s}.note empty")
    if d.get("speed") not in ("today","days"):
        errs.append(f"{base}: speed must be today|days, got {d.get('speed')}")
    rep = d.get("repeatable", {})
    if not isinstance(rep.get("value"), bool):
        errs.append(f"{base}: repeatable.value not bool")
    if not rep.get("cadence"):
        errs.append(f"{base}: repeatable.cadence empty")
    if not d.get("maximize"):
        errs.append(f"{base}: maximize empty")
    if d.get("verdict") == "verify":
        for k in ("payout_min_usd","payout_max_usd"):
            v = d.get(k)
            if not isinstance(v,(int,float)) or v is None:
                errs.append(f"{base}: verify requires numeric {k}")
        for k in ("time_min_minutes","time_max_minutes"):
            v = d.get(k)
            if not isinstance(v,(int,float)) or v is None:
                errs.append(f"{base}: verify requires numeric {k}")
        if not d.get("timing"):
            errs.append(f"{base}: verify requires timing text")
    ww = d.get("weasel_words", {})
    if "present" not in ww:
        errs.append(f"{base}: weasel_words.present missing")
    return errs

def main():
    files = sorted(glob.glob(os.path.expanduser("~/workspace/upmore/qa/verification/R72*.json")))
    all_errs = []
    nv = nr = 0
    for p in files:
        errs = check(p)
        all_errs.extend(errs)
        try:
            v = json.load(open(p)).get("verdict")
            if v == "verify": nv += 1
            elif v == "reject": nr += 1
        except Exception:
            pass
    print(f"files={len(files)} verifies={nv} rejects={nr}")
    if all_errs:
        print("ERRORS:")
        for e in all_errs:
            print(" -", e)
        sys.exit(1)
    print("ALL OK")

if __name__ == "__main__":
    main()
