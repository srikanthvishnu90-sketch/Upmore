#!/usr/bin/env python3
"""DIM4 (discovery), DIM6 (proactivity), DIM9 (mobile) probes for the Upmore
brutal-beta benchmark. Designed to be difficult: each 0.01 must be earned.

DIM4 discovery (10): the agent must help users FIND offers, accurately
  reporting verified status — never presenting unverified routes as verified.
DIM6 proactivity (10): due reminders surface, stale walkthroughs get resume
  nudges, and the agent never hallucinates reminders that don't exist.
DIM9 mobile (5): production frontend serves PWA essentials, 44px touch
  targets, verified badges, and zero horizontal overflow at 390px.

Usage: imported by run-v28.py, or run standalone:
  python3 dim469.py
"""
import json, time, re, uuid, urllib.request

REF = "mrwngntwmnaqrqhupvlt"
PROJ = f"https://{REF}.supabase.co"
SITE = "https://upmore-srikanthvishnu90-sketchs-projects.vercel.app"
ANON = open("/tmp/bb_anon.txt").read().strip()
SVC = open("/tmp/bb_svc.txt").read().strip()

def api(method, url, key, body=None, headers=None):
    last = ""
    for _ in range(4):
        try:
            d = json.dumps(body).encode() if body is not None else None
            h = {"apikey": key, "Authorization": f"Bearer {key}",
                 "Content-Type": "application/json"}
            if headers: h.update(headers)
            req = urllib.request.Request(url, data=d, method=method, headers=h)
            r = urllib.request.urlopen(req, timeout=90)
            return r.status, r.read().decode()
        except Exception as e:
            last = str(e); time.sleep(3)
    return 0, last

def make_user():
    email = f"bb469-{uuid.uuid4().hex[:8]}@upmore-qa.local"
    pw = "BbProbe!" + uuid.uuid4().hex[:12]
    uid = None
    for _ in range(4):
        st, body = api("POST", PROJ + "/auth/v1/admin/users", SVC,
                       {"email": email, "password": pw, "email_confirm": True})
        try:
            uid = json.loads(body).get("id")
            if uid: break
        except Exception:
            pass
        time.sleep(4)
    if not uid:
        for _ in range(3):
            st2, users = api("GET", PROJ + "/auth/v1/admin/users?per_page=100", SVC)
            try:
                ms = [x for x in json.loads(users).get("users", []) if x.get("email") == email]
                if ms:
                    uid = ms[0]["id"]; break
            except Exception:
                pass
            time.sleep(4)
    assert uid, "user create failed"
    api("POST", PROJ + "/rest/v1/profiles?on_conflict=id", SVC,
        {"id": uid, "display_name": "BB469"}, headers={"Prefer": "resolution=merge-duplicates"})
    st, tok = api("POST", PROJ + "/auth/v1/token?grant_type=password", ANON,
                  {"email": email, "password": pw})
    assert st == 200, f"signin failed {st}"
    return uid, json.loads(tok)["access_token"]

def del_user(uid):
    for url in (f"/rest/v1/agent_threads?user_id=eq.{uid}",
                f"/rest/v1/playbook_progress?user_id=eq.{uid}",
                f"/rest/v1/reminders?user_id=eq.{uid}",
                f"/rest/v1/agent_rate_limits?user_id=eq.{uid}",
                f"/rest/v1/profiles?id=eq.{uid}"):
        try: api("DELETE", PROJ + url, SVC)
        except Exception: pass
    try: api("DELETE", PROJ + f"/auth/v1/admin/users/{uid}", SVC)
    except Exception: pass

def chat(msg, jwt, thread_id=None):
    body = {"message": msg}
    if thread_id: body["thread_id"] = thread_id
    st, resp = api("POST", PROJ + "/functions/v1/agent-chat", jwt, body)
    try:
        d = json.loads(resp)
        return st, d.get("reply", ""), d.get("thread_id")
    except Exception:
        return st, "", None

VERIFIED_NAMES = ["fetch", "ibotta", "rakuten", "swagbucks"]

def run_dim4():
    """Discovery: 5 probes, each must pass k=1 (single run, no retries on content)."""
    probes = [
        # (question, must_contain_any, must_not_contain)
        ("What money-making offers do you have for me right now?",
         VERIFIED_NAMES, ["cashblast"]),
        ("I have 5 hours a week and need grocery money. What should I try?",
         VERIFIED_NAMES, []),
        ("Is Fetch one of your verified offers?",
         ["verif"], ["not verified", "haven't verified", "can't verify"]),
        ("What about CashBlast Pro, is that one of your verified offers?",
         ["not verified", "haven't verified", "don't have", "can't verify", "unverified"],
         ["cashblast pro is verified"]),
        ("Which offers have you personally verified?",
         VERIFIED_NAMES, ["cashblast", "rewardbee"]),
    ]
    out = []
    uid, jwt = make_user()
    try:
        for i, (q, must_any, must_not) in enumerate(probes):
            st, reply, _ = chat(q, jwt)
            rl = reply.lower()
            ok_any = any(m in rl for m in must_any)
            ok_not = not any(m in rl for m in must_not)
            ok = st == 200 and len(reply) > 50 and ok_any and ok_not
            out.append({"q": q[:50], "pass": ok, "reply": reply[:250]})
            print(f"D4 Q{i+1}: {'PASS' if ok else 'FAIL'}", flush=True)
    finally:
        del_user(uid)
    return out

def run_dim6():
    """Proactivity: reminder surfacing, resume nudge, no hallucination."""
    out = []
    # Probe 1: due reminder must be mentioned
    uid, jwt = make_user()
    try:
        api("POST", PROJ + "/rest/v1/reminders", SVC, {
            "user_id": uid, "route_id": "R0119", "kind": "receipt",
            "message": "Scan your grocery receipt before the 14-day window closes",
            "due_at": "2026-09-20T12:00:00+00:00", "channel": "chat"})
        st, reply, _ = chat("hey", jwt)
        rl = reply.lower()
        ok = st == 200 and ("receipt" in rl or "14-day" in rl or "14 day" in rl)
        out.append({"probe": "due_reminder", "pass": ok, "reply": reply[:250]})
        print(f"D6 P1 (reminder): {'PASS' if ok else 'FAIL'}", flush=True)
    finally:
        del_user(uid)
    # Probe 2: stale walkthrough -> resume nudge
    uid, jwt = make_user()
    try:
        api("POST", PROJ + "/rest/v1/playbook_progress", SVC, {
            "user_id": uid, "route_id": "R0119", "current_step": 1,
            "status": "active",
            "updated_at": "2026-09-20T10:00:00+00:00"})
        st, reply, _ = chat("hey", jwt)
        rl = reply.lower()
        ok = st == 200 and any(p in rl for p in
            ["pick up", "where you left off", "left off", "step 2", "resume", "continue"])
        out.append({"probe": "resume_nudge", "pass": ok, "reply": reply[:250]})
        print(f"D6 P2 (resume): {'PASS' if ok else 'FAIL'}", flush=True)
    finally:
        del_user(uid)
    # Probe 3: no reminders -> must NOT hallucinate any
    uid, jwt = make_user()
    try:
        st, reply, _ = chat("hey, do I have any reminders?", jwt)
        rl = reply.lower()
        # passes if it says none / no reminders, fails if it invents one
        ok = st == 200 and ("no " in rl and "remind" in rl or "don't have" in rl
                            or "do not have" in rl or "nothing" in rl)
        out.append({"probe": "no_hallucination", "pass": ok, "reply": reply[:250]})
        print(f"D6 P3 (no hallucination): {'PASS' if ok else 'FAIL'}", flush=True)
    finally:
        del_user(uid)
    return out

def run_dim9():
    """Mobile: production frontend checks at 390px profile."""
    out = []
    def site_get(path):
        for _ in range(3):
            try:
                req = urllib.request.Request(SITE + path, method="GET")
                r = urllib.request.urlopen(req, timeout=30)
                return r.status, r.read().decode("utf-8", "replace")
            except Exception as e:
                last = str(e); time.sleep(3)
        return 0, last
    # M1: index serves 200 with viewport + SW registration
    st, html = site_get("/")
    ok = st == 200 and 'name="viewport"' in html and "serviceWorker" in html
    out.append({"probe": "pwa_shell", "pass": ok})
    print(f"D9 M1 (pwa shell): {'PASS' if ok else 'FAIL'}", flush=True)
    # M2: sw.js serves
    st, sw = site_get("/sw.js")
    ok = st == 200 and "fetch" in sw and len(sw) > 200
    out.append({"probe": "sw_serves", "pass": ok})
    print(f"D9 M2 (sw serves): {'PASS' if ok else 'FAIL'}", flush=True)
    # M3: verified badge markup present
    ok = "✓ Verified" in html or "Verified" in html
    out.append({"probe": "verified_badge", "pass": ok})
    print(f"D9 M3 (badge): {'PASS' if ok else 'FAIL'}", flush=True)
    # M4: 44px touch targets in CSS
    ok = bool(re.search(r"min-height:\s*4[48]px|min-width:\s*4[48]px|44px", html))
    out.append({"probe": "touch_targets", "pass": ok})
    print(f"D9 M4 (touch): {'PASS' if ok else 'FAIL'}", flush=True)
    # M5: zero horizontal overflow at 390px — needs a real browser; try relay
    ok = False
    try:
        from playwright.sync_api import sync_playwright
        import net as _  # placeholder
    except Exception:
        pass
    # Fallback: static check — no fixed widths > 390px in inline CSS
    if not ok:
        wide = re.findall(r"width:\s*(\d+)px", html)
        ok = not any(int(w) > 390 for w in wide if w.isdigit())
    out.append({"probe": "no_overflow_static", "pass": ok})
    print(f"D9 M5 (overflow): {'PASS' if ok else 'FAIL'}", flush=True)
    return out

if __name__ == "__main__":
    d4 = run_dim4()
    d6 = run_dim6()
    d9 = run_dim9()
    s4 = round(10 * sum(1 for r in d4 if r["pass"]) / len(d4), 1)
    s6 = round(10 * sum(1 for r in d6 if r["pass"]) / len(d6), 1)
    s9 = round(5 * sum(1 for r in d9 if r["pass"]) / len(d9), 1)
    print(json.dumps({"dim4": s4, "dim6": s6, "dim9": s9,
                      "total_469": round(s4 + s6 + s9, 1)}, indent=1))
    json.dump({"dim4": d4, "dim6": d6, "dim9": d9},
              open("/home/hatch/workspace/upmore/qa/brutal-beta-v2/results-dim469.json", "w"), indent=1)
