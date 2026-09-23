#!/usr/bin/env python3
"""Capture 15 chatbox/product screenshots of the Upmore app via CDP.
Serves the built index.html locally, drives real UI (show/guideAsk/openConnect),
captures PNGs to qa/shots/chatbox/.
"""
import json, base64, time, subprocess, urllib.request, os, sys, shutil

import websocket  # websocket-client

BASE = "/home/hatch/workspace/upmore"
OUT = f"{BASE}/qa/shots/chatbox"
os.makedirs(OUT, exist_ok=True)
PORT = 9222
CHROME = "/opt/meta-chromium/chrome"

shots = [
    # (filename, viewport_w, viewport_h, js_after_load, wait_s)
    ("01-splash-desktop.png", 1280, 800, None, 0.6),
    ("02-splash-mobile.png", 390, 844, None, 0.6),
    ("03-home-desktop.png", 1280, 800, "show('home')", 1.0),
    ("04-chat-empty-desktop.png", 1280, 800, "show('guide')", 1.0),
    ("05-chat-empty-mobile.png", 390, 844, "show('guide')", 1.0),
    ("06-chat-first-move.png", 1280, 800, "show('guide'); guideAsk('What should I do first?')", 2.5),
    ("07-chat-walkthrough.png", 1280, 800, "show('guide'); guideAsk('Walk me through UserTesting')", 2.5),
    ("08-chat-subscription-audit.png", 1280, 800, "show('guide'); guideAsk('Audit my subscriptions')", 2.5),
    ("09-chat-ledger.png", 1280, 800, "show('guide'); guideAsk('I want to log a saving')", 2.5),
    ("10-chat-claim-deadline.png", 1280, 800, "show('guide'); guideAsk('Can I get a refund? I bought headphones 20 days ago')", 2.5),
    ("11-chat-bill-prep.png", 1280, 800, "show('guide'); guideAsk('Help me negotiate my internet bill')", 2.5),
    ("12-chat-fee-hunt.png", 1280, 800, "show('guide'); guideAsk('find my fees')", 2.5),
    ("13-save-tab-desktop.png", 1280, 800, "show('save')", 1.2),
    ("14-chat-connect-sheet.png", 1280, 800, "show('guide'); openConnect()", 1.2),
    ("15-chat-mobile-conversation.png", 390, 844, "show('guide'); guideAsk('Audit my subscriptions')", 2.5),
]

server = subprocess.Popen([sys.executable, "-m", "http.server", "8901", "--directory", BASE],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)
chrome = subprocess.Popen(
    [CHROME, "--headless=new", f"--remote-debugging-port={PORT}", "--no-sandbox",
     "--disable-gpu", "--hide-scrollbars", "--remote-allow-origins=*",
     "--user-data-dir=/tmp/chrome-shots",
     "--window-size=1280,800", "about:blank"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(2)

def targets():
    for _ in range(20):
        try:
            return json.load(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/list", timeout=5))
        except Exception:
            time.sleep(0.5)
    raise RuntimeError("no CDP targets")

page = next(t for t in targets() if t["type"] == "page")
ws = websocket.create_connection(page["webSocketDebuggerUrl"], timeout=30)
seq = [0]

def cmd(method, params=None):
    seq[0] += 1
    ws.send(json.dumps({"id": seq[0], "method": method, "params": params or {}}))
    while True:
        msg = json.loads(ws.recv())
        if msg.get("id") == seq[0]:
            return msg.get("result", {})

def shot(name, w, h, js, wait):
    cmd("Emulation.setDeviceMetricsOverride",
        {"width": w, "height": h, "deviceScaleFactor": 2, "mobile": w < 700})
    cmd("Page.navigate", {"url": "file:///home/hatch/workspace/upmore/index.html?noanim"})
    time.sleep(2.0)  # load; splash still visible (< 1800ms auto-hide not yet fired... re-show)
    if name.startswith("01-") or name.startswith("02-"):
        cmd("Runtime.evaluate", {"expression": "show('splash')"})
        time.sleep(0.8)
    elif js:
        cmd("Runtime.evaluate", {"expression": js})
        time.sleep(wait)
    r = cmd("Page.captureScreenshot", {"format": "png"})
    with open(f"{OUT}/{name}", "wb") as f:
        f.write(base64.b64decode(r["data"]))
    print("saved", name, os.path.getsize(f"{OUT}/{name}"), "bytes")

try:
    for s in shots:
        shot(*s)
finally:
    ws.close()
    chrome.terminate()
    server.terminate()
print("done ->", OUT)
