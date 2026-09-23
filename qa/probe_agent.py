#!/usr/bin/env python3
"""Production probe for agent-chat v44. Creates a throwaway auth user via the
GoTrue admin API, runs live chat probes with its JWT, then deletes the user.
The service_role key is fetched transiently from the Management API and never
printed or persisted.
Usage: python3 probe_agent.py "message 1" "message 2" ...
"""
import json
import os
import sys
import urllib.request
import uuid

sys.path.insert(0, "/opt/hatch/skills/skill-creator/bin")
from dynamic_credentials import add_surrogate_to_request, read_json_response

REF = "mrwngntwmnaqrqhupvlt"
PROJ_URL = f"https://{REF}.supabase.co"
EMAIL = f"probe-{uuid.uuid4().hex[:8]}@upmore-qa.local"
PASSWORD = "ProbeQa!2026x9"


def mgmt(method, path, body=None, tries=4):
    import time
    last = None
    for i in range(tries):
        try:
            r = urllib.request.Request("https://api.supabase.com/v1" + path, method=method)
            add_surrogate_to_request(r, "custom.supabase", allowed_hosts=["api.supabase.com"])
            if body is not None:
                r.add_header("Content-Type", "application/json")
                r.data = json.dumps(body).encode()
            with urllib.request.urlopen(r, timeout=60) as resp:
                return read_json_response(resp)
        except Exception as e:
            last = e
            time.sleep(2 * (i + 1))
    raise last


def _open(req, timeout=60, tries=4):
    import time
    last = None
    for i in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.status, read_json_response(resp)
        except urllib.error.HTTPError as e:
            try:
                payload = json.loads(e.read().decode() or "{}")
            except Exception:
                payload = {"error": "unparseable"}
            return e.code, payload
        except Exception as e:
            last = e
            time.sleep(2 * (i + 1))
    raise last


def auth(svc_key, method, path, body=None):
    r = urllib.request.Request(PROJ_URL + path, method=method)
    r.add_header("apikey", svc_key)
    r.add_header("Authorization", "Bearer " + svc_key)
    if body is not None:
        r.add_header("Content-Type", "application/json")
        r.data = json.dumps(body).encode()
    return _open(r)


def chat(anon_key, jwt, message):
    r = urllib.request.Request(
        PROJ_URL + "/functions/v1/agent-chat", method="POST")
    r.add_header("Content-Type", "application/json")
    r.add_header("apikey", anon_key)
    r.add_header("Authorization", "Bearer " + jwt)
    r.data = json.dumps({"message": message}).encode()
    return _open(r, timeout=120)


def main():
    # 1. service_role key, transient
    keys = mgmt("GET", f"/projects/{REF}/api-keys")
    svc_key = next(k["api_key"] for k in keys if k["name"] == "service_role")
    anon_key = next(k["api_key"] for k in keys if k["name"] == "anon")

    # 2. create probe user (idempotent: delete any stale one first, verified)
    st, users = auth(svc_key, "GET", "/auth/v1/admin/users?per_page=100")
    for u in users.get("users", []):
        if u.get("email") == EMAIL:
            for _ in range(3):
                auth(svc_key, "DELETE", f"/auth/v1/admin/users/{u['id']}")
                _, chk = auth(svc_key, "GET", "/auth/v1/admin/users?per_page=100")
                if not any(x.get("id") == u["id"] for x in chk.get("users", [])):
                    break
            else:
                print("WARNING: stale probe user would not delete:", u["id"]); sys.exit(1)
    st, user = auth(svc_key, "POST", "/auth/v1/admin/users", {
        "email": EMAIL, "password": PASSWORD, "email_confirm": True,
        "user_metadata": {"probe": True},
    })
    if st not in (200, 201):
        print("user create failed:", st, user); sys.exit(1)
    uid = user["id"]

    # 2b. profile row (the real app upserts this on sign-in; the rate limiter
    # FKs to profiles, so a missing row would 429 every request)
    auth(svc_key, "POST", "/rest/v1/profiles", {"id": uid, "display_name": "PROBE"})

    # 3. sign in -> JWT (retry: admin create can lag replication)
    jwt = None
    for _ in range(6):
        r = urllib.request.Request(PROJ_URL + "/auth/v1/token?grant_type=password", method="POST")
        r.add_header("Content-Type", "application/json")
        r.add_header("apikey", svc_key)
        r.data = json.dumps({"email": EMAIL, "password": PASSWORD}).encode()
        _st, tok = _open(r)
        if isinstance(tok, dict) and tok.get("access_token"):
            jwt = tok["access_token"]
            break
    if not jwt:
        print("sign-in failed:", _st, tok); sys.exit(1)

    # 4. probes
    for msg in sys.argv[1:]:
        st, body = chat(anon_key, jwt, msg)
        reply = body.get("reply", "") if isinstance(body, dict) else body
        snippet = (reply or "")[:400].replace("\n", " ")
        print(f"--- [{st}] {msg}\n{snippet}\n")

    # 5. delete probe user and its rows (threads/messages cascade from the
    # auth user; rate limits + profile need explicit deletes). Verify the
    # auth delete actually took — retry if the user is still listed.
    auth(svc_key, "DELETE", f"/rest/v1/agent_rate_limits?user_id=eq.{uid}")
    auth(svc_key, "DELETE", f"/rest/v1/profiles?id=eq.{uid}")
    deleted = None
    for _ in range(3):
        st, _ = auth(svc_key, "DELETE", f"/auth/v1/admin/users/{uid}")
        deleted = st
        _, users = auth(svc_key, "GET", "/auth/v1/admin/users?per_page=100")
        if not any(u.get("id") == uid for u in users.get("users", [])):
            break
    else:
        print("WARNING: probe user still present after 3 deletes:", uid)
    print("probe user deleted:", deleted)


if __name__ == "__main__":
    main()
