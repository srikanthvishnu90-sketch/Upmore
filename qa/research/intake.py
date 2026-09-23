#!/usr/bin/env python3
"""Upmore offer research intake v1.

DISCOVER + DEDUPE stage of the research pipeline (see SYSTEM.md).

Usage:
    python3 intake.py --source doctor-of-credit-bank-bonuses   # run one watcher (scaffold)
    python3 intake.py --add --provider "Wells Fargo" --method "Everyday Checking bonus" \
        --payout "$400" --url "https://..." --origin "manual"

What v1 does:
  - Loads the 535-route catalog and builds a dedupe key per route
    (normalized provider + method).
  - --add inserts a candidate into qa/research/candidates.jsonl unless it
    fuzzy-matches an existing route (then it reports the match so the operator
    updates the route's promo terms instead).
  - --source is a scaffold: it prints the fetch plan for the source. Live page
    extraction runs through a subagent (browser) that outputs candidate JSON,
    which is then piped through --add for dedupe.

v2: live fetch + extraction wired directly; candidates move to a DB table.
"""
import argparse, csv, json, os, re, sys
from difflib import SequenceMatcher

BASE = os.path.dirname(os.path.abspath(__file__))
CATALOG = os.path.expanduser("~/workspace/upmore/src/data/upmore-data.json")
CANDIDATES = os.path.join(BASE, "candidates.jsonl")


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def load_catalog():
    d = json.load(open(CATALOG))
    routes = d["routes"]
    keys = []
    for r in routes:
        keys.append((r["id"], norm(r.get("provider")) + " " + norm(r.get("method"))))
    return keys


def match(candidate_key, catalog_keys, threshold=0.82):
    best, score = None, 0.0
    for rid, ck in catalog_keys:
        s = SequenceMatcher(None, candidate_key, ck).ratio()
        if s > score:
            best, score = rid, s
    return (best, score) if score >= threshold else (None, score)


def add_candidate(provider, method, payout, url, origin, notes=""):
    keys = load_catalog()
    ckey = norm(provider) + " " + norm(method)
    rid, score = match(ckey, keys)
    if rid:
        print(f"DUPLICATE of {rid} (score {score:.2f}) — update that route's terms instead.")
        return
    from datetime import datetime, timezone
    obj = {
        "spotted_at": datetime.now(timezone.utc).isoformat(),
        "source": origin,
        "provider": provider,
        "method": method,
        "headline_payout": payout,
        "official_url": url,
        "status": "new",
        "route_id": None,
        "notes": notes,
    }
    with open(CANDIDATES, "a") as f:
        f.write(json.dumps(obj) + "\n")
    print(f"ADDED candidate: {provider} — {method} ({payout})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--add", action="store_true")
    ap.add_argument("--provider", default="")
    ap.add_argument("--method", default="")
    ap.add_argument("--payout", default="")
    ap.add_argument("--url", default="")
    ap.add_argument("--origin", default="manual")
    ap.add_argument("--notes", default="")
    ap.add_argument("--source", default="")
    a = ap.parse_args()
    if a.add:
        if not (a.provider and a.method):
            sys.exit("--add needs --provider and --method")
        add_candidate(a.provider, a.method, a.payout, a.url, a.origin, a.notes)
    elif a.source:
        print(f"[{a.source}] v1 scaffold: fetch the source URL from sources.yaml via a")
        print("browser subagent, extract candidates as JSON, and pipe each through:")
        print("  python3 intake.py --add --provider ... --method ... --payout ... --url ...")
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
