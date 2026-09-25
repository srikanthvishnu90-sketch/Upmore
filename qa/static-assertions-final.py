#!/usr/bin/env python3
"""Static assertions for the final Upmore build (post-968ece1 fixes).

Proves, against the BUILT index.html:
 1. Bank-bonus queue dollars equal payout, not qualifying deposits.
 2. Locked/non-cash routes cannot lead Home or Guide (canLead + nonCashLead
    evaluated in Node against the real inlined catalog).
 3. R7419 cannot lead and is labeled Price matching.
 4. Tracked-data Guide branch, ledger grand total, local dates present.
 5. Trust copy: delete states account deletion; money answer discloses
    never-sell-data / never-charge; welcome page consistent on commissions.
  6. B1 (no false monitoring claims), B7 (no bank-data fabrication path).
Binary: any failure exits non-zero.
"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
HTML = os.path.join(ROOT, "index.html")

fails = []
def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        fails.append(name + (f": {detail}" if detail else ""))

# --- build first so assertions run on the real artifact ---
r = subprocess.run(["python3", "src/build-app.py"], cwd=ROOT, capture_output=True, text=True)
check("build-app.py runs", r.returncode == 0, r.stderr[:300])
html = open(HTML, encoding="utf-8").read()

# --- 1. payout fields are bonus dollars, not qualifying deposits ---
m = re.search(r"const UPMORE_DATA = (\{.*?\});\n</script>", html, re.S)
check("UPMORE_DATA inlined", bool(m))
data = json.loads(m.group(1))
by_id = {str(r["id"]): r for r in data["routes"]}
# the app script is the <script> block containing the Guide logic
scripts = re.findall(r"<script>(.*?)</script>", html, re.S)
app_js = next(s for s in scripts if "async function guideAsk" in s)
expected_payouts = {
    "R0069": 300, "R0071": 450, "R0633": 350, "R0031": 100, "R0569": 400,
    "R0568": 400, "R0083": 400, "R0639": 350, "R0934": 400, "R0959": 700,
    "R4644": 500, "R3239": 300, "R0579": 100, "R0096": 400, "R0085": 100,
    "R0089": 300, "R0032": 30,
}
for rid, mx in expected_payouts.items():
    got = (by_id.get(rid) or {}).get("payout_max")
    check(f"payout_max {rid} == {mx} (bonus, not deposit)", got == mx, f"got {got}")

# --- 2+3. leadership rules, evaluated in Node against the real catalog ---
block_src = re.search(
    r"const NO_LEAD_IDS = \[.*?\];.*?const canLead = .*?;",
    html, re.S)
check("leadership block extractable", bool(block_src))
node_assertions = """
const byId = id => UPMORE_DATA.routes.find(r => String(r.id) === id);
const A = [];
const t = (name, cond) => A.push([name, !!cond]);
// R7419: price matching, savings not cash
t("R7419 cannot lead", !canLead(byId("R7419")));
t("R7419 labeled Price matching", /price matching/i.test(String(byId("R7419").method || "") + String(byId("R7419").title || "")));
// explicit non-cash payouts
t("R1191 gift card cannot lead", !canLead(byId("R1191")));
t("R0115 statement credit cannot lead", !canLead(byId("R0115")));
t("R6441 tax credit cannot lead", !canLead(byId("R6441")));
t("R2662 account credits cannot lead", !canLead(byId("R2662")));
t("R1567 trade-in credit cannot lead", !canLead(byId("R1567")));
// referral-gated categories
for (const r of UPMORE_DATA.routes) {
  if (["Referral Bonus","Gift Card Resale","App Referral"].includes(r.category) && canLead(r)) {
    t("no referral/gift-card-resale route leads (" + r.id + ")", false);
    break;
  }
}
t("no referral/gift-card-resale route leads", true);
// genuine cash routes still lead
t("R0032 cash bonus can lead", canLead(byId("R0032")));
t("R8329 PayPal cash can lead", canLead(byId("R8329")));
t("R1565 never-store-credit cash can lead", canLead(byId("R1565")));
t("R4105 cash-back-redeemable points cannot lead", !canLead(byId("R4105")));
t("R0519 XP-mechanism route cannot lead", !canLead(byId("R0519")));
t("R5683 points (worth $150) cannot lead", !canLead(byId("R5683")));
t("R3731 'No points. Just real cash.' can lead", canLead(byId("R3731")));
t("R2341 'not ... points-equivalent' can lead", canLead(byId("R2341")));
t("R3825 Point-of-Sale bonus can lead", canLead(byId("R3825")));
t("R0069 bank bonus can lead", canLead(byId("R0069")));
// completed-route exclusion helper exists
t("completed-route exclusion in queue", /doneIds/.test(LEAD_SRC2));
for (const [n, ok] of A) console.log((ok ? "PASS " : "FAIL ") + n);
if (A.some(([n, ok]) => !ok)) process.exit(1);
"""
node_src = (
    "const UPMORE_DATA = " + m.group(1) + ";\n"
    + "const LEAD_SRC2 = " + json.dumps(app_js) + ";\n"
    + block_src.group(0) + "\n"
    + node_assertions
)
open("/tmp/lead_check.js", "w").write(node_src)
r = subprocess.run(["node", "/tmp/lead_check.js"], capture_output=True, text=True)
print(r.stdout.strip())
check("node leadership assertions", r.returncode == 0, r.stderr[:300] or r.stdout[-500:])

# --- 4. tracked-data Guide branch / ledger ---
check("trackedAnswer present", "async function trackedAnswer" in html)
check("Guide routes tracked data before agent", "trackedAnswer(text)" in html)
check("ledger grand total tile", "Total across all buckets" in html)
check("local-date stamps (not UTC)", app_js.count("localISODate()") >= 3 and "new Date().toISOString().slice(0, 10)" not in app_js)
check("renewal insert persists amount", 'saveInsert("save_renewals", { name, renews_on: date, kind: "renewal", prep_notes: notes, status: "upcoming", amount:' in app_js)

# --- 5. trust copy ---
check("delete copy states account deletion", "deletes your account" in html)
check("money answer: never sell data", "never do: sell your data" in html)
check("policy question branch", '"do you sell"' in html)
check("welcome page consistent (no false cut claim)", "No offers pay us anything right now" in html and "Some offers pay us a small cut" not in html)

# --- 6. B1 / B7 ---
check("B1 no false monitoring claims",
      len(re.findall(r"watches this daily|last checked|agent is watching|monitors? (this|your) (daily|account)|we watch|checking daily", html, re.I)) == 0)
check("B7 no bank-data fabrication path",
      html.count("finance_accounts") + html.count("finance_alerts") + html.count("finance_snapshots") + html.count("finance_goals") == 0)

# --- B8 weight (informational; benchmark says 6.7MB) ---
size = os.path.getsize(HTML)
print(f"INFO index.html bytes: {size} ({size/1e6:.2f} MB decimal, {size/2**20:.2f} MiB)")

print()
if fails:
    print(f"{len(fails)} FAILURES:")
    for f in fails:
        print(" -", f)
    sys.exit(1)
print("ALL STATIC ASSERTIONS PASS")
