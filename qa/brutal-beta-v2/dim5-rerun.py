#!/usr/bin/env python3
"""DIM5 re-run with a competent multi-turn responder. Merges into results-v21.json."""
import json, sys, time, re, uuid, urllib.request, urllib.error

sys.path.insert(0, "/opt/hatch/skills/skill-creator/bin")
from dynamic_credentials import add_surrogate_to_request, read_json_response

REF = "mrwngntwmnaqrqhupvlt"
PROJ = f"https://{REF}.supabase.co"
ANON = open("/tmp/bb_anon.txt").read().strip()
RESULTS_PATH = "/home/hatch/workspace/upmore/qa/brutal-beta-v2/results-v21.json"
D = json.load(open(RESULTS_PATH))
res = D["results"]

def mgmt_get(path):
    r = urllib.request.Request("https://api.supabase.com/v1" + path, method="GET")
    add_surrogate_to_request(r, "custom.supabase", allowed_hosts=["api.supabase.com"])
    with urllib.request.urlopen(r, timeout=60) as resp:
        return read_json_response(resp)

SVC = next((k["api_key"] for k in mgmt_get(f"/projects/{REF}/api-keys")
            if k.get("name") == "service_role"), None)

def api(method, url, key, body=None, bearer=None, tries=8, prefer=None):
    data = json.dumps(body).encode() if body is not None else None
    for i in range(tries):
        r = urllib.request.Request(url, data=data, method=method)
        r.add_header("apikey", key)
        r.add_header("Authorization", "Bearer " + (bearer or key))
        if data:
            r.add_header("Content-Type", "application/json")
        if prefer:
            r.add_header("Prefer", prefer)
        try:
            with urllib.request.urlopen(r, timeout=45) as resp:
                return resp.status, resp.read().decode()
        except urllib.error.HTTPError as e:
            try:
                return e.code, e.read().decode()
            except Exception:
                return e.code, "{}"
        except Exception as ex:
            print(f'    retry {i+1}: {type(ex).__name__}', flush=True)
            time.sleep(2 * (i + 1))
    return -1, "retries exhausted"

def make_user():
    email = f"bb3g-{uuid.uuid4().hex[:8]}@upmore-qa.local"
    pw = "BbProbe!" + uuid.uuid4().hex[:12]
    st, u = api("POST", PROJ + "/auth/v1/admin/users", SVC,
                {"email": email, "password": pw, "email_confirm": True})
    try:
        uid = json.loads(u).get("id")
    except Exception:
        uid = None
    if not uid:
        time.sleep(3)
        try:
            st2, users_body = api("GET", PROJ + "/auth/v1/admin/users?per_page=100", SVC)
            ms = [x for x in json.loads(users_body).get("users", []) if x.get("email") == email]
            uid = ms[0]["id"] if ms else None
        except Exception:
            uid = None
    assert uid, "user create failed"
    for _ in range(3):
        st, _ = api("POST", PROJ + "/rest/v1/profiles?on_conflict=id", SVC,
                    {"id": uid, "display_name": "BB3G"}, prefer="resolution=merge-duplicates")
        if st in (200, 201, 204):
            break
        time.sleep(3)
    st, tok = api("POST", PROJ + "/auth/v1/token?grant_type=password", ANON,
                  {"email": email, "password": pw})
    assert st == 200, f"signin failed {st}"
    return uid, json.loads(tok)["access_token"]

def del_user(uid):
    for url in (f"/rest/v1/agent_threads?user_id=eq.{uid}",
                f"/rest/v1/agent_rate_limits?user_id=eq.{uid}",
                f"/rest/v1/profiles?id=eq.{uid}",
                f"/auth/v1/admin/users/{uid}"):
        try:
            api("DELETE", PROJ + url, SVC)
        except Exception:
            pass

def answer_for(model_reply):
    rl = model_reply.lower()
    if re.search(r"\b(18\+|how old|your age|age)\b", rl) and "?" in rl:
        return "I am 25."
    if "card" in rl and "?" in rl:
        return "Yes, I have a debit card."
    if ("paypal" in rl or "bank account" in rl) and "?" in rl:
        return "I have PayPal."
    if "smartphone" in rl or "iphone or android" in rl:
        return "iPhone."
    if any(w in rl for w in ["where are you", "what state", "located", "which country", "based"]) and "?" in rl:
        return "I'm in Texas."
    if "free time" in rl or ("hours" in rl and "week" in rl):
        return "About 5 hours a week."
    if any(w in rl for w in ["ready", "shall we", "let's go", "move forward", "sound good"]):
        return "Yes, let's go."
    return "Yes."

def claim_ok(reply, markers):
    rl = reply.lower()
    return any(m.lower() in rl for m in markers)

users = []
for n in range(2):
    for attempt in range(4):
        try:
            users.append(make_user())
            print(f"user {n+1}/2 ready", flush=True)
            break
        except Exception as e:
            print(f"user {n+1} attempt {attempt+1} failed: {type(e).__name__}", flush=True)
            time.sleep(5)
    else:
        raise RuntimeError("could not create probe users")
latencies = []

def chat(msg, uid_jwt, thread_id=None):
    body_in = {"message": msg}
    if thread_id:
        body_in["thread_id"] = thread_id
    t0 = time.time()
    st, body = api("POST", PROJ + "/functions/v1/agent-chat", ANON, body_in, bearer=uid_jwt[1])
    ms = int((time.time() - t0) * 1000)
    latencies.append(ms)
    try:
        bj = json.loads(body)
        return st, ms, bj.get("reply", "") or "", bj.get("thread_id")
    except Exception:
        return st, ms, "", None

DIM5 = [
    ("Fetch", "Walk me through getting started with Fetch step by step.", ["fetch.com", "14", "$10"]),
    ("Ibotta", "Walk me through getting started with Ibotta step by step.", ["ibotta.com", "$20", "offer"]),
    ("Rakuten", "Walk me through getting started with Rakuten step by step.", ["rakuten.com", "quarterly", "card"]),
    ("Swagbucks", "Walk me through getting started with Swagbucks step by step.", ["swagbucks.com", "100", "SB"]),
]
for idx, (provider, q, markers) in enumerate(DIM5):
    uid_jwt = users[idx % len(users)]
    st, ms, r1, tid = chat(q, uid_jwt)
    assert r1.strip() and st == 200, f"DIM5 {provider} turn1 empty"
    transcript = r1
    for turn in range(7):
        if not tid or all(claim_ok(transcript, [m]) for m in markers):
            break
        st2, ms2, r2, tid = chat(answer_for(transcript), uid_jwt, tid)
        if not r2.strip():
            break
        transcript += "\n" + r2
    hits = [claim_ok(transcript, [m]) for m in markers]
    res["dim5"][idx] = {"provider": provider, "hits": hits, "ms": ms, "reply": transcript[:1500]}
    print(f"D5 {provider}: {sum(hits)}/{len(hits)}", flush=True)

for uid, _ in users:
    try:
        del_user(uid)
    except Exception:
        pass
print("users cleaned", flush=True)

s5 = round(10 * (sum(sum(r["hits"]) / len(r["hits"]) for r in res["dim5"]) / len(res["dim5"])), 1)
lat = sorted(latencies)
p50 = lat[len(lat) // 2] if lat else D.get("p50_ms", 0)
s8 = 2.5 if p50 <= 3000 else 0
D["dims"]["guide_quality_10"] = s5
D["dims"]["speed_5"] = s8
D["score"] = round(sum(D["dims"].values()), 1)
D["p50_ms_d5"] = p50
D["results"] = res
json.dump(D, open(RESULTS_PATH, "w"), indent=1)
print(json.dumps({"score": D["score"], "guide_quality_10": s5, "p50_d5_ms": p50}, indent=1))
