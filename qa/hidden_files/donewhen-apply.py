#!/usr/bin/env python3
"""PATCH updated steps JSONB back to the upmore DB, threaded. Only changed routes."""
import sys, json, os, time, http.client, urllib.parse, urllib.request, threading
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, "/home/hatch/workspace/upmore/qa")
sys.path.insert(0, "/opt/hatch/skills/skill-creator/bin")
from dynamic_credentials import add_surrogate_to_request, read_json_response

REF = "mrwngntwmnaqrqhupvlt"
updates = json.load(open("/home/hatch/workspace/upmore/qa/hidden_files/donewhen-updates.json"))

def svc():
    r = urllib.request.Request("https://api.supabase.com/v1/projects/" + REF + "/api-keys", method="GET")
    add_surrogate_to_request(r, "custom.supabase", allowed_hosts=["api.supabase.com"])
    with urllib.request.urlopen(r, timeout=60) as resp:
        keys = read_json_response(resp)
    return next(k["api_key"] for k in keys if k.get("name") == "service_role")

KEY = svc()
PX = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
PU = urllib.parse.urlparse(PX)
ok = 0; fail = []
lock = threading.Lock()

def patch_one(rid, steps):
    global ok
    body = json.dumps({"steps": steps}).encode()
    path = f"/rest/v1/routes?route_id=eq.{urllib.parse.quote(rid)}"
    for attempt in range(4):
        c = http.client.HTTPSConnection(PU.hostname, PU.port, timeout=45)
        try:
            c.set_tunnel(f"{REF}.supabase.co", 443)
            c.request("PATCH", path, body=body, headers={
                "apikey": KEY, "Authorization": "Bearer " + KEY,
                "Content-Type": "application/json",
                "Host": f"{REF}.supabase.co"})
            resp = c.getresponse()
            out = resp.read()
            c.close()
            if resp.status in (200, 204):
                with lock: ok += 1
                return
        except Exception:
            pass
        time.sleep(2 * (attempt + 1))
    with lock: fail.append(rid)

t0 = time.time()
with ThreadPoolExecutor(max_workers=12) as ex:
    list(ex.map(lambda kv: patch_one(kv[0], kv[1]), updates.items()))
dt = time.time() - t0
print(f"patched_ok={ok} failed={len(fail)} in {dt:.1f}s")
if fail:
    json.dump(fail, open("/home/hatch/workspace/upmore/qa/hidden_files/donewhen-failures.json", "w"))
    print("failures:", fail[:20])
