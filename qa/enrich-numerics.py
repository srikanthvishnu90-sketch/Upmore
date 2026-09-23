#!/usr/bin/env python3
"""Enrich verified routes with numeric payout/time fields.

- New worker files (R0851+) carry the 6 numeric keys already: validate + use.
- Old verified cards: estimate payout from DB payout_text/evidence payout_quote and time
  from category defaults (refined by explicit minute mentions in steps); write the numeric
  keys back into the evidence file and append the basis to notes.
- Output: qa/numerics.json {route_id: {...}} + prints exact average active time (mean of
  time_mid across all verified cards, 2 decimals).
"""
import json, glob, os, re, sys
sys.path.insert(0, "/home/hatch/workspace/upmore/qa")
from db import req

NUM_KEYS = ["payout_min_usd", "payout_max_usd", "payout_value_note",
            "time_min_minutes", "time_max_minutes", "numeric_basis"]

TIME_DEFAULTS = {
    "Bank Bonus": (30, 60), "Credit Card Bonus": (20, 40), "Fintech/Neobank": (20, 40),
    "Brokerage Promo": (30, 60), "Survey": (10, 20), "Focus Group": (75, 135),
    "Research Study": (60, 120), "Transcription": (30, 60), "Translation": (30, 60),
    "App Referral": (5, 15), "Cashback/Shopping": (10, 20), "Rebate/Incentive": (20, 45),
    "Unclaimed/Recovery": (15, 30), "Beta Testing": (30, 60), "UGC/Creator": (60, 180),
    "Game/Offerwall": (30, 90), "AI Training": (30, 60), "Media/Music": (20, 40),
    "Student Program": (20, 40), "Brand Ambassador": (60, 120), "Voiceover/Audio": (30, 90),
    "Crypto Reward": (15, 30), "Mock Jury": (60, 240), "Microtask": (15, 45),
    "Plasma Donation": (90, 150), "Clinical Trial": (120, 480), "Receipt/Loyalty": (5, 15),
    "Buyback": (15, 30), "Recycling": (15, 45), "Government": (240, 480),
    "Pet Sitting": (60, 120), "Tutoring": (60, 120), "Design Market": (60, 180),
    "Mystery Shopping": (30, 90), "Car Advertising": (30, 60), "Energy Switching": (20, 40),
    "Store Signup": (5, 15), "Insurance/Quote": (10, 20), "Telecom Promo": (20, 40),
    "Other Online": (20, 60),
}

def amt(x):
    return float(x.replace(",", ""))

BONUS_KWS = ["bonus", "gift", "earn", "reward", "credit", "paid", "payout", "cash back",
             "cashback", "statement credit", "bill credit"]

def _nearest_bonus_amount(t):
    """Pick the $ amount closest to a bonus keyword (avoids balance-requirement misfires)."""
    amts = [(m.start(), amt(m.group(1))) for m in re.finditer(r"\$\s*(\d[\d,]*)\b", t)]
    if not amts:
        return None
    kwpos = [m.start() for kw in BONUS_KWS for m in re.finditer(kw, t, re.I)]
    if not kwpos:
        return amts[0][1]
    best, bestd = amts[0][1], 10 ** 9
    for pos, val in amts:
        dmin = min(abs(pos - k) for k in kwpos)
        # penalize round big numbers that look like balance thresholds
        if val >= 10000 and dmin > 60:
            dmin += 500
        if dmin < bestd:
            best, bestd = val, dmin
    return best

def parse_payout(text):
    """Return (pmin, pmax, note). Best-effort from official payout text."""
    t = (text or "")
    if not t or t.startswith("Variable"):
        return 0.0, 0.0, "no stated amount in official terms; variable"
    # 1) points/miles (allow up to 3 words between number and unit: "125,000 AAdvantage bonus miles")
    pm = re.search(r"(\d[\d,]*)\s+(?:[A-Za-z®™&']+\s+){0,3}(?:points|miles|pts)\b", t, re.I)
    if pm:
        pts = amt(pm.group(1))
        w = re.search(r"(?:worth|~|≈|\()\s*\$?\s*([\d,]+(?:\.\d+)?)", t[pm.start():pm.start() + 120])
        if w and abs(amt(w.group(1)) - pts * 0.01) < pts * 0.01 * 3 + 50:
            return amt(w.group(1)), amt(w.group(1)), "points converted at provider-stated cash value"
        v = round(pts * 0.01, 2)
        return v, v, f"points at assumed 1¢/pt base redemption ({pm.group(1).strip()} pts); provider may vary"
    # 2) explicit "$X bonus/gift/reward/credit" amounts (collect all; tiers -> range)
    explicits = [amt(m.group(1)) for m in
                 re.finditer(r"\$\s*(\d[\d,]*)\s*(?:cash\s+)?(?:bonus|gift|reward|credit|paid out)\b", t, re.I)]
    for m in re.finditer(r"(?:earn|get|receive|qualify for)\s+\$\s*(\d(?:[\d,]*\d)?)\b", t, re.I):
        # reject context amounts like "$10,489 per year on average" (host earnings, not the bonus)
        if re.search(r"per\s+year|on\s+average|\ba\s+year\b|per\s+month", t[m.end():m.end() + 25], re.I):
            continue
        explicits.append(amt(m.group(1)))
    explicits = sorted(set(explicits))
    if explicits:
        if len(explicits) > 1:
            return explicits[0], explicits[-1], "tiered bonus amounts in official terms"
        return explicits[0], explicits[0], "flat bonus amount in official terms"
    # 3) "$X–$Y bonus" ranges
    m = re.search(r"\$\s*(\d[\d,]*)\s*[–—-]\s*\$?\s*(\d[\d,]*)\s*(?:cash\s+)?(?:bonus|gift|reward|credit)\b", t, re.I)
    if m:
        a, b = amt(m.group(1)), amt(m.group(2))
        if a > b:
            a, b = b, a
        return a, b, "range stated in official terms"
    # 4) "up to $X" requires the dollar sign (avoids "up to 90,000 miles" misfire)
    m = re.search(r"up to\s*\$\s*([\d,]+(?:\.\d+)?)", t, re.I)
    if m:
        return 0.0, amt(m.group(1)), "'up to' amount in official terms; floor $0"
    v = _nearest_bonus_amount(t)
    if v is not None:
        if re.search(r"\$\s*" + re.escape(f"{v:g}") + r"\s*(?:or more|\+)", t):
            return v, v, "minimum stated amount in official terms"
        return v, v, "flat amount in official terms"
    return 0.0, 0.0, "no parseable amount; variable"

def parse_time(steps, payout_text, category):
    """Return (tmin, tmax). Prefer explicit task-duration mentions, else category defaults."""
    blob = " ".join(s if isinstance(s, str) else s.get("text", "") for s in (steps or []))
    blob += " " + (payout_text or "")
    # only trust minute mentions phrased as task duration (avoids "500 plan minutes" etc.)
    m = re.search(r"(\d+)\s*[-–]\s*(\d+)\s*minutes?\b", blob)
    if m and int(m.group(2)) <= 480:
        return float(m.group(1)), float(m.group(2)), True
    m = re.search(r"(?:takes?|about|around|approximately|up to|lasts?|complete in|spend)\s*(\d+)\s*minutes?\b", blob, re.I)
    if m and int(m.group(1)) <= 480:
        v = float(m.group(1))
        return v, v, True
    m = re.search(r"\b(\d+)-minute\b", blob, re.I)
    if m and int(m.group(1)) <= 480:
        v = float(m.group(1))
        return v, v, True
    d = TIME_DEFAULTS.get(category, (20, 60))
    return float(d[0]), float(d[1]), False

st, rows = req("GET", "/rest/v1/routes?select=route_id,payout_text,category,steps&limit=5000")
verified = [r for r in rows if True]  # statuses resolved below
st2, allr = req("GET", "/rest/v1/routes?select=route_id,status&limit=5000")
status = {r["route_id"]: r["status"] for r in allr}
by_id = {r["route_id"]: r for r in rows}

numerics = {}
backfilled = worker_ok = worker_bad = no_evidence = 0
warnings = []

for rid, r in sorted(by_id.items()):
    if status.get(rid) != "verified":
        continue
    evf = f"/home/hatch/workspace/upmore/qa/verification/{rid}.json"
    d = None
    if os.path.exists(evf):
        try:
            d = json.load(open(evf))
        except Exception:
            d = None
    if d and all(k in d for k in NUM_KEYS) and not str(d.get("numeric_basis") or "").startswith("backfill:"):
        try:
            pmin = float(d["payout_min_usd"]); pmax = float(d["payout_max_usd"])
            tmin = float(d["time_min_minutes"]); tmax = float(d["time_max_minutes"])
            assert pmin <= pmax and tmin >= 1 and tmax >= tmin and pmin >= 0
            numerics[rid] = {
                "payout_min": pmin, "payout_max": pmax,
                "payout_value_note": str(d.get("payout_value_note") or ""),
                "time_min_minutes": tmin, "time_max_minutes": tmax,
                "numeric_basis": "worker-verified: " + str(d.get("numeric_basis") or "")[:300],
            }
            worker_ok += 1
            continue
        except (AssertionError, TypeError, ValueError):
            warnings.append(f"{rid}: worker numerics insane, re-estimating")
            worker_bad += 1
    # estimate
    payout_text = r.get("payout_text") or ""
    if d and not payout_text:
        payout_text = d.get("payout_quote") or ""
    pmin, pmax, pnote = parse_payout(payout_text)
    steps = r.get("steps") or (d.get("steps") if d else []) or []
    tmin, tmax, explicit = parse_time(steps, payout_text, r.get("category") or "Other Online")
    basis = (f"payout: {pnote}; time: explicit duration in official steps ({tmin:g}-{tmax:g}min)"
             if explicit else
             f"payout: {pnote}; time: category default {r.get('category')} ({tmin:g}-{tmax:g}min active)")
    numerics[rid] = {
        "payout_min": pmin, "payout_max": pmax, "payout_value_note": pnote,
        "time_min_minutes": tmin, "time_max_minutes": tmax,
        "numeric_basis": "backfill: " + basis[:400],
    }
    backfilled += 1
    if d is not None:
        for k, v in [("payout_min_usd", pmin), ("payout_max_usd", pmax),
                     ("payout_value_note", pnote), ("time_min_minutes", tmin),
                     ("time_max_minutes", tmax), ("numeric_basis", "backfill: " + basis[:400])]:
            d[k] = v
        d["notes"] = (d.get("notes") or "") + f" [numeric-backfill 2026-09-24: {basis[:200]}]"
        json.dump(d, open(evf, "w"), indent=2, ensure_ascii=False)
    else:
        no_evidence += 1

# earn ratios + exact average active time
ratios = {}
tots = 0.0
for rid, n in numerics.items():
    pmid = (n["payout_min"] + n["payout_max"]) / 2
    tmid = (n["time_min_minutes"] + n["time_max_minutes"]) / 2
    n["earn_ratio"] = round(pmid / max(1.0, tmid), 4)
    tots += tmid
    ratios[rid] = n["earn_ratio"]

avg_time = tots / len(numerics) if numerics else 0.0
json.dump(numerics, open("/home/hatch/workspace/upmore/qa/numerics.json", "w"), indent=1)
print(f"verified={len(numerics)} worker_ok={worker_ok} worker_bad={worker_bad} "
      f"backfilled={backfilled} no_evidence_file={no_evidence}")
print(f"EXACT_AVG_ACTIVE_MINUTES={avg_time:.2f}")
for w in warnings[:20]:
    print("WARN:", w)
# top/bottom 5 by ratio for sanity
top = sorted(ratios.items(), key=lambda x: -x[1])[:5]
bot = sorted([k for k in ratios if ratios[k] > 0], key=lambda x: ratios[x])[:5]
print("top ratio:", [(k, ratios[k]) for k in [x[0] for x in top]])
print("low ratio:", [(k, round(ratios[k], 3)) for k in bot])
