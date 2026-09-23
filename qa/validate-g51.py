#!/usr/bin/env python3
"""Focused validator for Upmore G51 checkpoint: evidence files R5481-R5540."""
import json, glob, os, re
from urllib.parse import urlparse

AGG = {"doctofcredit.com", "nerdwallet.com", "bankrate.com", "thepennyhoarder.com",
       "wallethacks.com", "clark.com", "dollarsprout.com", "reddit.com", "forbes.com",
       "investopedia.com", "creditcards.com", "thepointsguy.com", "upgradedpoints.com",
       "mybanktracker.com", "depositaccounts.com", "youtube.com", "tiktok.com",
       "facebook.com", "bankbonuses.com", "everybankbonus.com", "moneyunder30.com",
       "fool.com", "usnews.com", "cnn.com", "kiplinger.com", "powertochoose.org",
       "electricityrates.com", "callmepower.com", "knoji.com", "moneysavingexpert.com"}

KEYS23 = ["route_id", "verdict", "official_url", "terms_url", "payout_quote", "steps",
          "catches", "biggest_catch", "eligibility", "timing", "upfront_fee",
          "weasel_words", "app_links", "checked_at", "critical", "standard", "notes",
          "payout_min_usd", "payout_max_usd", "payout_value_note",
          "time_min_minutes", "time_max_minutes", "numeric_basis"]

def host(u):
    try:
        h = urlparse(u or "").netloc.lower()
        return h[4:] if h.startswith("www.") else h
    except Exception:
        return ""

issues = []
ok_files = []
lo, hi = 5481, 5540
for n in range(lo, hi + 1):
    rid = f"R{n:04d}"
    p = f"/home/hatch/workspace/upmore/qa/verification/{rid}.json"
    if not os.path.exists(p):
        continue  # assigned-ID reject or unconsumed; handled by caller
    try:
        j = json.load(open(p))
    except Exception as e:
        issues.append((rid, f"unparseable: {e}"))
        continue
    if len(j) != 23:
        issues.append((rid, f"key count {len(j)} != 23; extra/missing: {sorted(set(j) ^ set(KEYS23))}"))
    missing = [k for k in KEYS23 if k not in j]
    if missing:
        issues.append((rid, f"missing keys {missing}"))
    if j.get("route_id") != rid:
        issues.append((rid, f"route_id {j.get('route_id')!r} != filename"))
    if j.get("verdict") != "verify":
        issues.append((rid, f"verdict {j.get('verdict')!r}"))
    # critical c1-c4
    crit = j.get("critical") or {}
    for c in ["c1", "c2", "c3", "c4"]:
        if c not in crit:
            issues.append((rid, f"critical.{c} missing"))
        elif not isinstance(crit[c], dict) or "pass" not in crit[c] or "evidence" not in crit[c]:
            issues.append((rid, f"critical.{c} bad shape"))
    # standard s1-s7
    std = j.get("standard") or {}
    for s in ["s1", "s2", "s3", "s4", "s5", "s6", "s7"]:
        if s not in std:
            issues.append((rid, f"standard.{s} missing"))
    # urls
    h = host(j.get("official_url"))
    if not h:
        issues.append((rid, "official_url empty/unparseable"))
    elif h in AGG:
        issues.append((rid, f"official_url on aggregator host {h}"))
    if not j.get("terms_url"):
        issues.append((rid, "terms_url empty"))
    # quote
    if not j.get("payout_quote"):
        issues.append((rid, "payout_quote empty"))
    # steps/catches
    if not isinstance(j.get("steps"), list) or not j.get("steps"):
        issues.append((rid, "steps empty/not list"))
    if not isinstance(j.get("catches"), list) or not j.get("catches"):
        issues.append((rid, "catches empty/not list"))
    if not j.get("biggest_catch"):
        issues.append((rid, "biggest_catch empty"))
    if not isinstance(j.get("upfront_fee"), bool):
        issues.append((rid, f"upfront_fee not bool: {j.get('upfront_fee')!r}"))
    if not isinstance(j.get("weasel_words"), list):
        issues.append((rid, "weasel_words not list"))
    al = j.get("app_links")
    if not isinstance(al, dict) or set(al.keys()) != {"android", "ios"}:
        issues.append((rid, f"app_links shape bad: {al!r}"))
    if not re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$", str(j.get("checked_at") or "")):
        issues.append((rid, f"checked_at bad: {j.get('checked_at')!r}"))
    # numerics
    for k in ["payout_min_usd", "payout_max_usd"]:
        v = j.get(k)
        if not isinstance(v, (int, float)) or isinstance(v, bool):
            issues.append((rid, f"{k} not number: {v!r}"))
    mn, mx = j.get("payout_min_usd"), j.get("payout_max_usd")
    if isinstance(mn, (int, float)) and isinstance(mx, (int, float)) and mn > mx:
        issues.append((rid, f"payout_min {mn} > payout_max {mx}"))
    for k in ["time_min_minutes", "time_max_minutes"]:
        v = j.get(k)
        if not isinstance(v, (int, float)) or isinstance(v, bool) or v < 1:
            issues.append((rid, f"{k} bad: {v!r}"))
    tmn, tmx = j.get("time_min_minutes"), j.get("time_max_minutes")
    if isinstance(tmn, (int, float)) and isinstance(tmx, (int, float)) and tmn > tmx:
        issues.append((rid, f"time_min {tmn} > time_max {tmx}"))
    if tmn not in (5, 15) or tmx not in (15, 30):
        issues.append((rid, f"time range {tmn}-{tmx} not in allowed referral(5-15)/signup(15-30) bands"))
    if not j.get("payout_value_note"):
        issues.append((rid, "payout_value_note empty"))
    if not j.get("numeric_basis"):
        issues.append((rid, "numeric_basis empty"))
    if not j.get("eligibility"):
        issues.append((rid, "eligibility empty"))
    if not j.get("timing"):
        issues.append((rid, "timing empty"))
    if not j.get("notes"):
        issues.append((rid, "notes empty"))
    ok_files.append(rid)

print(f"files present: {len(ok_files)}")
print(f"issues: {len(issues)}")
for rid, msg in issues:
    print(f"  {rid}: {msg}")
print("present IDs:", " ".join(ok_files))
