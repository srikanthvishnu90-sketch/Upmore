#!/usr/bin/env python3
"""Patch src/data/upmore-data.json with the DB's verified route data,
so the app bundle (Explore badges, route cards) reflects verification."""
import json, subprocess

REF = "mrwngntwmnaqrqhupvlt"
SB = "/home/hatch/workspace/skills/supabase/bin/sb.py"

IDS = ["R0036","R0096","R0098","R0116","R0118","R0119","R0140",
       "R0220","R0221","R0292","R0295","R0302","R0355","R0446","R0037","R0039","R0040","R0041","R0043","R0045","R0048","R0051","R0056","R0052","R0053","R0054","R0059","R0047","R0050","R0055","R0057","R0060","R0062","R0063","R0026","R0020","R0016","R0103","R0115","R0100","R0233","R0228","R0229","R0227","R0240","R0226","R0285","R0286","R0290","R0293","R0196","R0190","R0189","R0188","R0324","R0316","R0312","R0313","R0318","R0323","R0310","R0314","R0320","R0066","R0067","R0069","R0070","R0071","R0074","R0373","R0366","R0367","R0368","R0369","R0376","R0378","R0377","R0374","R0245","R0246","R0247","R0267","R0328","R0330","R0329","R0331","R0325","R0326","R0327","R0381","R0380","R0385","R0383","R0386","R0387","R0495","R0403","R0404","R0405","R0409","R0390","R0391","R0392","R0393","R0394","R0396","R0397","R0005","R0004","R0010","R0011","R0013","R0015","R0018","R0019","R0021","R0023","R0024","R0025","R0027","R0030","R0031","R0032","R0035","R0099","R0109","R0110","R0111","R0083","R0085","R0088","R0089","R0091","R0046","R0049","R0079","R0086","R0038","R0156","R0158","R0159","R0164","R0167","R0171","R0172","R0173","R0174","R0186","R0187","R0191","R0192","R0193","R0198","R0201","R0202","R0204","R0205","R0206","R0208","R0209","R0212","R0214","R0215","R0216","R0125","R0126","R0134","R0135","R0136","R0144","R0145","R0146","R0148","R0151","R0296","R0298","R0299","R0300","R0301","R0303","R0306","R0307","R0308","R0309","R0315","R0321","R0322","R0490","R0491","R0492","R0430","R0431","R0432","R0433","R0434","R0435","R0436","R0437","R0452","R0498","R0494","R0451","R0447","R0454","R0455","R0456","R0457","R0461","R0462","R0464","R0465","R0466","R0467"]
db = {}
for rid in IDS:
    p = subprocess.run([SB, "query",
        f"SELECT route_id, name, status, verified_at, payout_text, payout_timing, catches, steps, provider_url, min_age, geo_notes FROM routes WHERE route_id='{rid}';"],
        capture_output=True, text=True, timeout=120)
    try:
        out = json.loads(p.stdout)
        rows = out["result"] if isinstance(out, dict) else []
        if rows: db[rid] = rows[0]
    except Exception as e:
        print("FAILED", rid, p.stdout[:200]); raise
print("fetched:", len(db))

path = "/home/hatch/workspace/upmore/src/data/upmore-data.json"
d = json.load(open(path))
n = 0
for r in d["routes"]:
    rid = r["id"]
    if rid in db:
        v = db[rid]
        r["status"] = "verified"
        r["reward"] = v.get("payout_text") or r["reward"]
        r["payout_timing"] = v.get("payout_timing") or r["payout_timing"]
        r["url"] = v.get("provider_url") or r["url"]
        r["catches"] = v.get("catches") or r["catches"]
        # map DB steps {text,done_when,warn} to the app's step shape
        r["steps"] = [{"n": i + 1, "text": s.get("text", ""), "who": "Upmore",
                       "done_when": s.get("done_when", ""), "warns": s.get("warn", "")}
                      for i, s in enumerate(v.get("steps") or [])]
        n += 1
json.dump(d, open(path, "w"), indent=1)
print("patched routes:", n)
