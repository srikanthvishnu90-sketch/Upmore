// SPEC 09b tests: net-worth explanations, tx review queue.
const fns = require("fs").readFileSync("/tmp/spec09b-fns.js", "utf8");
const store = {};
global.localStorage = {
  getItem: k => (k in store ? store[k] : null),
  setItem: (k, v) => { store[k] = String(v); },
  removeItem: k => { delete store[k]; },
};
eval(fns);

let pass = 0, fail = 0;
const t = (name, cond, extra) => { cond ? pass++ : (fail++, console.log("FAIL:", name, extra || "")); };

// nwSnapNorm backward compat
t("snapNorm number", nwSnapNorm(5000).total === 5000 && nwSnapNorm(5000).partial === true);
t("snapNorm object", nwSnapNorm({ total: 1, bank: 2 }).bank === 2 && !nwSnapNorm({ total: 1 }).partial);

// nwChangeExplain
const snaps = {
  "2026-07": { total: 10000, bank: 8000, assets: 5000, liabs: 2000, debts: 1000 },
  "2026-08": { total: 11500, bank: 9000, assets: 5000, liabs: 2000, debts: 500 },
};
const ex = nwChangeExplain(snaps);
t("explain direction", ex.includes("Up") && ex.includes("$1,500"));
t("explain bank", ex.includes("accounts up"));
t("explain debts", ex.includes("what you owe down"));
t("explain old-format silent", nwChangeExplain({ "2026-07": 10000, "2026-08": 11500 }) === "");
t("explain single month", nwChangeExplain({ "2026-08": 11500 }) === "");

// txReviewItems
const old = new Date(Date.now() - 10 * 864e5).toISOString().slice(0, 10);
const txns = [
  { id: "p1", merchant_raw: "Gas Station", amount: -40, posted_at: old, is_pending: true },
  { id: "c1", merchant_raw: "Refund Co", amount: 25, posted_at: "2026-09-01", is_unmatched_credit: true },
  { id: "r1", merchant_raw: "Store", amount: 15, posted_at: "2026-09-01", is_refund: true, refunded_tx: "x" },
  { id: "ok1", merchant_raw: "Grocery", amount: -50, posted_at: "2026-09-20" },
  { id: "fresh", merchant_raw: "Coffee", amount: -5, posted_at: new Date().toISOString().slice(0, 10), is_pending: true },
];
const items = txReviewItems(txns);
t("review finds 3", items.length === 3, JSON.stringify(items.map(i => i.kind)));
t("review kinds", items.some(i => i.kind === "pending") && items.some(i => i.kind === "credit") && items.some(i => i.kind === "refund"));
t("review skips fresh pending", !items.some(i => i.id === "fresh"));
t("review skips clean", !items.some(i => i.id === "ok1"));
// acknowledge persists
store["upmore_tx_reviewed_v1"] = JSON.stringify(["p1"]);
t("review respects ack", txReviewItems(txns).length === 2);

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
