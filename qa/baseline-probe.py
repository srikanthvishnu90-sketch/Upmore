#!/usr/bin/env python3
"""Baseline capability probes: honest BEFORE snapshot of the 4 key questions."""
import json, sys, time, uuid, subprocess, tempfile, os, urllib.request
sys.path.insert(0, "/opt/hatch/skills/skill-creator/bin")
from dynamic_credentials import add_surrogate_to_request, read_json_response

REF = "mrwngntwmnaqrqhupvlt"
PROJ = f"https://{REF}.supabase.co"
ANON = open("/tmp/bb_anon.txt").read().strip()

def mgmt_get(path):
    r = urllib.request.Request("https://api.supabase.com/v1" + path, method="GET")
    add_surrogate_to_request(r, "custom.supabase", allowed_hosts=["api.supabase.com"])
    with urllib.request.urlopen(r, timeout=60) as resp:
        return read_json_response(resp)
SVC = next((k["api_key"] for k in mgmt_get(f"/projects/{REF}/api-keys") if k.get("name") == "service_role"), None)

def api(method, url, key, body=None, bearer=None, tries=6):
    payload = json.dumps(body) if body is not None else None
    for i in range(tries):
        tmp = tempfile.mktemp(prefix="base_")
        cmd = ["curl", "-s", "-o", tmp, "-w", "%{http_code}", "-X", method, url,
               "--max-time", "60", "-H", "apikey: " + key,
               "-H", "Authorization: Bearer " + (bearer or key)]
        if payload:
            cmd += ["-H", "Content-Type: application/json", "-d", payload]
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=70)
            code = int(p.stdout.strip()) if p.stdout.strip().isdigit() else 0
            resp_body = open(tmp, encoding="utf-8", errors="replace").read() if os.path.exists(tmp) else ""
            try: os.unlink(tmp)
            except Exception: pass
            if code: return code, resp_body
        except Exception:
            pass
        time.sleep(2 * (i + 1))
    return -1, "retries exhausted"

def make_user():
    email = f"base-{uuid.uuid4().hex[:8]}@upmore-qa.local"
    pw = "BbProbe!" + uuid.uuid4().hex[:12]
    st, u = api("POST", PROJ + "/auth/v1/admin/users", SVC,
                {"email": email, "password": pw, "email_confirm": True})
    uid = json.loads(u).get("id")
    api("POST", PROJ + "/rest/v1/profiles?on_conflict=id", SVC,
        {"id": uid, "display_name": "BASE"}, )
    st, tok = api("POST", PROJ + "/auth/v1/token?grant_type=password", ANON,
                  {"email": email, "password": pw})
    return uid, json.loads(tok)["access_token"]

def chat(jwt, msg, thread_id=None):
    body_in = {"message": msg}
    if thread_id: body_in["thread_id"] = thread_id
    t0 = time.time()
    st, body = api("POST", PROJ + "/functions/v1/agent-chat", ANON, body_in, bearer=jwt)
    ms = int((time.time() - t0) * 1000)
    try:
        bj = json.loads(body)
        return st, ms, bj.get("reply", ""), bj.get("thread_id")
    except Exception:
        return st, ms, body[:500], None

def del_user(uid):
    for url in (f"/rest/v1/agent_threads?user_id=eq.{uid}",
                f"/rest/v1/playbook_progress?user_id=eq.{uid}",
                f"/rest/v1/reminders?user_id=eq.{uid}",
                f"/rest/v1/agent_rate_limits?user_id=eq.{uid}",
                f"/rest/v1/profiles?id=eq.{uid}",
                f"/auth/v1/admin/users/{uid}"):
        try: api("DELETE", PROJ + url, SVC)
        except Exception: pass

uid, jwt = make_user()
print("probe user", uid[:8], flush=True)
out = []
tests = [
    ("make20", ["make me $20"]),
    ("stocks", ["what are some good stocks you think i should invest in, and why"]),
    ("polymarket", ["can I make money on polymarket? is it a good way to make extra cash?"]),
    ("fetch_walk", ["walk me through the Fetch rewards app, how do I actually make money with it?"]),
    ("twenty_fast_2turn", ["i need to make $20 fast", "which one is the fastest?"]),
]
for name, turns in tests:
    tid = None
    for t in turns:
        st, ms, reply, tid = chat(jwt, t, tid)
        out.append({"test": name, "turn": t, "status": st, "ms": ms, "reply": reply})
        print(f"  {name}: {st} {ms}ms ({len(reply)} chars)", flush=True)
        time.sleep(1)

json.dump(out, open("/home/hatch/workspace/upmore/qa/baseline-capability.json", "w"), indent=1)
del_user(uid)
print("saved + cleaned", flush=True)
