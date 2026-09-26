// SPEC 09 deterministic tests — run: node /tmp/spec09-test.js
// Extracts the real SPEC 09 module from the template and tests it.
const fs = require("fs");
const src = fs.readFileSync("/home/hatch/workspace/upmore/src/upmore-app-template.html", "utf8");
const start = src.indexOf('/* ================= SPEC 09:');
const end = src.indexOf("// Service worker: offline app-shell cache");
if (start < 0 || end < 0) { console.error("anchors not found"); process.exit(1); }
const mod = src.slice(start, end);

// ---- Browser stubs ----
const store = new Map();
global.localStorage = {
  getItem: k => (store.has(k) ? store.get(k) : null),
  setItem: (k, v) => store.set(k, String(v)),
  removeItem: k => store.delete(k),
};
global.document = { getElementById: () => null, querySelectorAll: () => [], createElement: () => ({}) };
global.window = { open: () => {} };
global.$ = () => null;
global.toast = () => {};
global.renderQueue = () => {};
global.renderSubs = () => {};
global.show = () => {};
global.openBudgetSheet = () => {};
global.closeBudgetSheet = () => {};
global.allCats = () => ["Food", "Transport", "Subscriptions", "Other"];
global.blsGet = (k, d) => d;
global.blsSet = () => {};
global.esc = s => String(s);
global.bm0 = n => "$" + Math.round(n);
global.money$ = n => "$" + Number(n).toFixed(2);
global.fmt$ = n => "$" + Math.round(n);
global.normalizeMerchant = s => String(s || "").toLowerCase().replace(/[^a-z0-9]/g, "");
global.CLAIM_SEARCH_URL = "https://www.missingmoney.com/";
global.detectRecurrence = () => [];
global.localSubsGet = () => global.__subs || [];
global.localSubsSet = () => {};
global.loadTrackData = () => ({ transactions: global.__txns || [], accounts: global.__accts || [] });

eval(mod + `
// test hooks: let/const inside eval don't leak, so expose them deliberately
global.__bulkOn = () => { txSelectMode = true; txBulkSel.add("a"); txBulkSel.add("b"); };
global.__bulkOff = () => { txSelectMode = false; txBulkSel.clear(); };
`);

let pass = 0, fail = 0;
function t(name, cond, extra) {
  if (cond) pass++;
  else { fail++; console.error("FAIL:", name, extra === undefined ? "" : JSON.stringify(extra)); }
}
function approx(a, b, tol) { return Math.abs(a - b) <= tol; }

(async () => {
// ---- monteCarlo(o): deterministic, shape, sanity ----
{
  const o = { age: 35, ret: 65, now: 100000, monthly: 500, need: 40000 };
  const a = monteCarlo(o), b = monteCarlo(o);
  t("mc deterministic", a.success === b.success && a.median === b.median && a.target === b.target);
  t("mc shape", typeof a.success === "number" && a.success >= 0 && a.success <= 100 && a.median >= 0 && a.target > 0);
  const rich = monteCarlo({ age: 35, ret: 65, now: 5000000, monthly: 0, need: 10000 });
  t("mc rich = 100% success", rich.success === 100, rich.success);
  const poor = monteCarlo({ age: 64, ret: 65, now: 0, monthly: 0, need: 100000 });
  t("mc poor = low success", poor.success < 50, poor.success);
  t("mc 4% rule target", poor.target > 100000, poor.target); // need inflated 1yr then /0.04
}
// ---- catProjection ----
{
  const now = new Date();
  const ym = now.toISOString().slice(0, 7);
  const dim = new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate();
  const dom = now.getDate();
  t("projection current month", approx(catProjection(100, ym), 100 / dom * dim, 0.01));
  t("projection past month = spent", catProjection(123.45, "2020-01") === 123.45);
  t("projection future month = full-month rate", catProjection(100, "2099-01") === 100 / 31 * 31);
}
// ---- paceChartSVG ----
{
  const txns = [];
  const now = new Date();
  for (let d = 1; d <= Math.min(5, now.getDate()); d++) {
    const dt = new Date(now.getFullYear(), now.getMonth(), d);
    txns.push({ posted_at: dt.toISOString().slice(0, 10), amount: -20, is_pending: false, is_transfer: false });
  }
  const ym = now.toISOString().slice(0, 7);
  const svg = paceChartSVG(txns, ym);
  t("pace svg is svg", svg.includes("<svg") && svg.includes("on pace"));
  const past = paceChartSVG([], "2020-01");
  t("pace svg past month", typeof past === "string" && past.length > 0);
}
// ---- savingsRate ----
{
  t("savings rate 25%", savingsRate({ agg: { in: 4000, kept: 1000 } }) === 25);
  t("savings rate 0 when negative", savingsRate({ agg: { in: 3000, kept: -500 } }) === 0 || savingsRate({ agg: { in: 3000, kept: -500 } }) < 0);
  t("savings rate null no income", savingsRate({ agg: { in: 0, kept: 0 } }) === null);
  t("savings rate null no model", savingsRate(null) === null);
}
// ---- ageOfMoney ----
{
  t("AoM empty = null", ageOfMoney([]) === null);
  t("AoM 30 days", ageOfMoney([
    { posted_at: "2026-09-01", amount: 3000 },
    { posted_at: "2026-10-01", amount: -3000 },
  ]) === 30);
  t("AoM weighted", ageOfMoney([
    { posted_at: "2026-09-01", amount: 2000 },
    { posted_at: "2026-09-11", amount: -1000 },
    { posted_at: "2026-10-01", amount: -1000 },
  ]) === 20);
  t("AoM ignores pending", ageOfMoney([{ posted_at: "2026-10-01", amount: -100, is_pending: true }]) === null);
}
// ---- detectFees ----
{
  const txns = [
    { id: "1", merchant_raw: "CHASE OVERDRAFT FEE", amount: -34, posted_at: "2026-09-01" },
    { id: "2", merchant_raw: "Whole Foods", amount: -50, posted_at: "2026-09-01" },
    { id: "3", merchant_raw: "ATM FEE", amount: -3, posted_at: "2026-09-01" },
    { id: "4", merchant_raw: "Monthly Service Fee", amount: -12, posted_at: "2026-09-01", is_pending: true },
  ];
  const fees = detectFees(txns);
  t("detectFees finds 2, skips pending", fees.length === 2, fees.map(f => f.id));
}
// ---- subDefenseCards: trials, fees, negotiation, research ----
{
  const soon = new Date(); soon.setDate(soon.getDate() + 5);
  const far = new Date(); far.setDate(far.getDate() + 40);
  global.__subs = [
    { id: "t1", merchant: "TrialApp", amount: 9.99, billing_interval: "trial", next_billing_date: soon.toISOString().slice(0, 10), status: "active" },
    { id: "t2", merchant: "FarTrial", amount: 4.99, billing_interval: "trial", next_billing_date: far.toISOString().slice(0, 10), status: "active" },
    { id: "x1", merchant: "Xfinity", amount: 89.99, billing_interval: "monthly", status: "active" },
  ];
  global.__txns = [
    { id: "f1", merchant_raw: "OVERDRAFT FEE", amount: -34, posted_at: "2026-09-01" },
  ];
  const past = new Date(); past.setDate(past.getDate() - 1);
  store.set("claim_research", JSON.stringify({ Texas: past.toISOString().slice(0, 10) }));
  const cards = await subDefenseCards();
  const types = cards.map(c => c.type);
  t("trial warning ≤7d only", types.filter(x => x === "trial").length === 1, types);
  t("trial card dollars annualized", cards.find(c => c.type === "trial").dollars === 9.99 * 12);
  t("fee card", types.includes("fee"));
  t("negotiation card", types.includes("negotiate"));
  t("research card", types.includes("research"));
  t("all cards have cta+why", cards.every(c => c.cta && c.why));
  store.delete("claim_research");
  global.__subs = []; global.__txns = [];
  const none = await subDefenseCards();
  t("no cards when empty", none.length === 0, none.length);
}
// ---- negotiateScript / feeWaiverScript ----
{
  const sc = negotiateScript({ merchant: "Xfinity", amount: 89.99 });
  t("neg script has merchant+amount", sc.includes("Xfinity") && sc.includes("$89.99"));
  const fs2 = feeWaiverScript({ merchant_raw: "OVERDRAFT FEE", amount: -34, posted_at: "2026-09-01" });
  t("fee script has amount", fs2.includes("$34.00") && fs2.includes("OVERDRAFT FEE"));
}
// ---- tx rules ----
{
  setTxRule("Starbucks", "starbucks", "Food");
  t("rule round-trip", txRuleFor({ merchant_id: "starbucks" }) === "Food");
  t("rule via normalizeMerchant", txRuleFor({ merchant_raw: "Starbucks!!" }) === "Food");
  t("rule miss", txRuleFor({ merchant_id: "nope" }) === null);
  t("rule null txn", txRuleFor(null) === null);
}
// ---- bulk bar ----
{
  t("bulk bar hidden when off", txBulkBarHtml() === "");
  global.__bulkOn();
  const h = txBulkBarHtml();
  t("bulk bar shows count", h.includes("2 selected") && h.includes("bulkCat"));
  global.__bulkOff();
}
// ---- net worth ----
{
  global.__accts = [{ balance: 5000 }, { balance: -200 }];
  const nw = netWorthCalc();
  t("net worth bank sum", nw.total === 4800 && nw.bank === 4800, nw.total);
  nwListSet("upmore_nw_assets_v1", [{ id: "1", name: "Car", value: 10000 }]);
  nwListSet("upmore_nw_liabs_v1", [{ id: "2", name: "Loan", value: 3000 }]);
  const nw2 = netWorthCalc();
  t("net worth assets-liabs", nw2.total === 4800 + 10000 - 3000, nw2.total);
  store.set("cfo_debt_debts", JSON.stringify([{ balance: 2000 }]));
  const nw3 = netWorthCalc();
  t("net worth minus cfo debts", nw3.total === 4800 + 10000 - 3000 - 2000, nw3.total);
  store.delete("cfo_debt_debts");
  store.delete("upmore_nw_assets_v1");
  store.delete("upmore_nw_liabs_v1");
  const snaps = nwSnapshot(12345);
  const ym = new Date().toISOString().slice(0, 7);
  t("snapshot stores month", snaps[ym] === 12345);
  t("spark needs 2 months", nwSparkSVG({ [ym]: 1 }).includes("Two months"));
  t("spark draws line", nwSparkSVG({ "2026-07": 1000, "2026-08": 2000 }).includes("<path"));
}
// ---- claim checklist ----
{
  const h = claimChecklistHtml("Texas");
  t("checklist state + portal button", h.includes("Texas") && h.includes("official claim site"));
  t("checklist has docs", h.includes("photo ID") && h.includes("never pay anyone"));
  const h2 = claimChecklistHtml("Alaska");
  t("checklist any state", h2.includes("Alaska") && h2.includes("never pay anyone"));
}
// ---- detectPaydays ----
{
  const txns = [];
  const base = new Date(2026, 7, 7);
  for (let i = 0; i < 4; i++) {
    const d = new Date(base); d.setDate(d.getDate() + 14 * i);
    txns.push({ posted_at: d.toISOString().slice(0, 10), amount: 2000, merchant_raw: "Employer", merchant_id: "employer" });
  }
  const pd = detectPaydays(txns);
  t("payday detected", pd.length === 1 && pd[0].gap === 14 && pd[0].last === "2026-09-18", JSON.stringify(pd).slice(0, 120));
  t("payday needs 2+", detectPaydays([{ posted_at: "2026-09-01", amount: 2000, merchant_id: "x" }]).length === 0);
}
// ---- projectDates ----
{
  const days = projectDates({ interval: "monthly", next_date: "2026-09-15" }, 2026, 9);
  t("projectDates monthly", days.length === 1 && days[0] === 15, days);
  const yrWrong = projectDates({ interval: "yearly", next_date: "2026-09-15" }, 2026, 7);
  t("projectDates yearly wrong month", yrWrong.length === 0);
  const yrRight = projectDates({ interval: "yearly", next_date: "2026-09-15" }, 2026, 8);
  t("projectDates yearly right month", yrRight.length === 1 && yrRight[0] === 15);
}

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
})();
