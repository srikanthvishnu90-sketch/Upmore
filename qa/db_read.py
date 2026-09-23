#!/usr/bin/env python3
"""Read-only catalog dump for discovery/dedupe work.
Usage: python3 qa/db_read.py           -> JSON: list of {route_id,name,provider,category,status,max_usd}
       python3 qa/db_read.py R0369     -> JSON: full row for one route
Writes to stdout only. Never writes to the DB."""
import sys, json, time, urllib.request
sys.path.insert(0, "/opt/hatch/skills/skill-creator/bin")
from dynamic_credentials import add_surrogate_to_request, read_json_response

REF = "mrwngntwmnaqrqhupvlt"
PROJ = f"https://{REF}.supabase.co"

def svc():
    r = urllib.request.Request("https://api.supabase.com/v1/projects/" + REF + "/api-keys", method="GET")
    add_surrogate_to_request(r, "custom.supabase", allowed_hosts=["api.supabase.com"])
    with urllib.request.urlopen(r, timeout=60) as resp:
        keys = read_json_response(resp)
    return next(k["api_key"] for k in keys if k.get("name") == "service_role")

def fetch(path, key, tries=5):
    last = None
    for i in range(tries):
        try:
            r = urllib.request.Request(PROJ + path, headers={"apikey": key, "Authorization": "Bearer " + key})
            with urllib.request.urlopen(r, timeout=90) as resp:
                return json.loads(resp.read())
        except Exception as e:
            last = e
            time.sleep(4)
    raise last

key = svc()
if len(sys.argv) > 1:
    rid = sys.argv[1]
    print(json.dumps(fetch(f"/rest/v1/routes?route_id=eq.{rid}&select=*", key)))
else:
    rows, off = [], 0
    while True:
        page = fetch(f"/rest/v1/routes?select=route_id,name,provider,category,status,payout_text&limit=500&offset={off}", key)
        if not page:
            break
        rows += page
        off += len(page)
    print(json.dumps(rows))
