#!/usr/bin/env python3
"""Fast keep-alive Supabase REST client (tunnels through the egress proxy)."""
import sys, json, time, os, http.client, urllib.parse
sys.path.insert(0, "/opt/hatch/skills/skill-creator/bin")
from dynamic_credentials import add_surrogate_to_request, read_json_response
import urllib.request

REF = "mrwngntwmnaqrqhupvlt"
_conn = None
_svc = None

def svc():
    global _svc
    if _svc:
        return _svc
    r = urllib.request.Request("https://api.supabase.com/v1/projects/" + REF + "/api-keys", method="GET")
    add_surrogate_to_request(r, "custom.supabase", allowed_hosts=["api.supabase.com"])
    with urllib.request.urlopen(r, timeout=60) as resp:
        keys = read_json_response(resp)
    _svc = next(k["api_key"] for k in keys if k.get("name") == "service_role")
    return _svc

def conn():
    global _conn
    if _conn:
        return _conn
    px = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    u = urllib.parse.urlparse(px)
    c = http.client.HTTPSConnection(u.hostname, u.port, timeout=45)
    c.set_tunnel(f"{REF}.supabase.co", 443)
    _conn = c
    return c

def req(method, path, body=None, tries=5):
    key = svc()
    data = json.dumps(body).encode() if body is not None else None
    last = None
    for i in range(tries):
        try:
            c = conn()
            c.request(method, path, body=data, headers={
                "apikey": key, "Authorization": "Bearer " + key,
                "Content-Type": "application/json",
                "Prefer": "resolution=merge-duplicates",
                "Host": f"{REF}.supabase.co"})
            resp = c.getresponse()
            out = resp.read()
            return resp.status, json.loads(out or b"null")
        except Exception as e:
            last = e
            global _conn
            try:
                _conn.close()
            except Exception:
                pass
            _conn = None
            time.sleep(2 * (i + 1))
    raise last
