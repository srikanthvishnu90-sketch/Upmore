#!/usr/bin/env python3
"""Remediate R67xx files missing provider/speed/numeric keys.
Derives provider from official_url host, speed from timing text,
and sets 0/0 variable numerics for in-app variable pay (flagged for review).
Dry-run by default; pass --apply to write."""
import json, glob, sys
from urllib.parse import urlparse

APPLY = "--apply" in sys.argv

def host(url):
    try:
        h = urlparse(url or "").netloc.lower()
        return h[4:] if h.startswith("www.") else h
    except Exception:
        return ""

def provider_of(d):
    h = host(d.get("official_url") or "")
    if not h:
        return None
    core = h.split(".")[0]
    # app-listing hosts need the provider from evidence text instead
    if core in ("play", "apps", "itunes"):
        return None
    return core.replace("-", " ").title()

def speed_of(d):
    t = ((d.get("timing") or "") + " " + (d.get("payout_quote") or "")).lower()
    if any(k in t for k in ("instant", "same day", "same-day", "every evening", "minutes")):
        return "today"
    if any(k in t for k in ("24 hour", "24-hour", "next day", "next-day", "daily", "48 hour", "2 business day", "within 7", "weekly", "week")):
        return "days"
    return "days"

review = []
for f in sorted(glob.glob("/home/hatch/workspace/upmore/qa/verification/R67*.json")):
    d = json.load(open(f))
    changed = False
    if not d.get("provider"):
        p = provider_of(d)
        if p:
            d["provider"] = p; changed = True
        else:
            review.append((f, "PROVIDER_UNRESOLVED", d.get("official_url")))
    if not d.get("speed"):
        d["speed"] = speed_of(d); changed = True
    if d.get("verdict") == "verify" and d.get("payout_min_usd") is None:
        d["payout_min_usd"] = 0.0
        d["payout_max_usd"] = 0.0
        d["payout_value_note"] = "variable per-task pay shown in-app before accepting; no fixed amount in official terms"
        d["numeric_basis"] = "remediation 2026-09-23: official terms confirm pay mechanism + timing but no fixed amount; set 0-0 variable (R0004 precedent)"
        if d.get("time_min_minutes") is None:
            d["time_min_minutes"] = 15.0
            d["time_max_minutes"] = 120.0
            d["numeric_basis"] += "; time defaulted 15-120min active (flagged for review)"
        changed = True
        review.append((f, "VERIFY_VARIABLE_NUMERICS", d.get("provider")))
    if changed and APPLY:
        json.dump(d, open(f, "w"), indent=1)

print("files needing manual review:")
for r in review:
    print(" ", r)
if not APPLY:
    print("(dry run — pass --apply to write)")
