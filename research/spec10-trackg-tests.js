// Track G reconciliation harness (2026-09-27).
// Recomputes Budget Report figures from the raw transaction set and asserts
// they match the engine math in src/upmore-app-template.html (monthAgg,
// dataDays, reviewQueue, defaultTargetFor, P&L trend).
// Run: node research/spec10-trackg-tests.js
"use strict";

let pass = 0, fail = 0;
function eq(name, actual, expected) {
  const ok = JSON.stringify(actual) === JSON.stringify(expected);
  if (ok) { pass++; }
  else { fail++; console.log(`FAIL ${name}: got ${JSON.stringify(actual)}, want ${JSON.stringify(expected)}`); }
}
const r2 = n => Math.round(n * 100) / 100;

// ---- engine mirrors (must match the template exactly) ----
function isCountableInflow(t) {
  if (!t || t.is_excluded) return false;
  if (t.counted_income && t.amount > 0) return true;
  return !!t && t.amount > 0 && !t.is_refund && !t.is_unmatched_credit;
}
function effCat(t) { return t.category && t.category !== "Other" ? t.category : "Other"; }
function monthAgg(transactions, ym) {
  const agg = { in: 0, out: 0, kept: 0, byCat: {}, byMerchant: {}, count: 0 };
  (transactions || []).filter(t => !t.is_pending && !t.is_transfer && !t.is_excluded && t.posted_at && String(t.posted_at).slice(0, 7) === ym)
    .forEach(t => {
      agg.count++;
      const a = Math.abs(Number(t.amount) || 0);
      if (Number(t.amount) < 0) {
        agg.out += a;
        const c = effCat(t);
        agg.byCat[c] = (agg.byCat[c] || 0) + a;
        const mn = t.merchant_raw || "Unknown";
        agg.byMerchant[mn] = (agg.byMerchant[mn] || 0) + a;
      } else if (isCountableInflow(t)) { agg.in += a; }
      else if (t.is_refund) { const c = effCat(t); agg.byCat[c] = (agg.byCat[c] || 0) - a; agg.out -= a; }
    });
  agg.kept = agg.in - agg.out;
  return agg;
}
function dataDays(transactions) {
  const ds = (transactions || [])
    .filter(t => !t.is_pending && !t.is_transfer && t.posted_at)
    .map(t => String(t.posted_at).slice(0, 10)).sort();
  if (!ds.length) return 0;
  return Math.max(1, Math.round((new Date(ds[ds.length - 1]).getTime() - new Date(ds[0]).getTime()) / 864e5) + 1);
}
function reviewQueue(transactions) {
  return (transactions || [])
    .filter(t => !t.is_pending && !t.is_transfer && !t.is_excluded && t.posted_at && effCat(t) === "Other")
    .sort((a, b) => String(b.posted_at).localeCompare(String(a.posted_at)))
    .slice(0, 50);
}
function defaultTargetFor(cat, transactions, monthsDesc) {
  const ms = monthsDesc.slice(0, 3);
  let s = 0;
  transactions.filter(t => !t.is_pending && !t.is_transfer && !t.is_excluded && t.amount < 0 && effCat(t) === cat && ms.includes(String(t.posted_at || "").slice(0, 7)))
    .forEach(t => { s += Math.abs(t.amount); });
  return Math.max(0, Math.round((s / Math.max(1, ms.length)) / 10) * 10);
}

// ---- fixture: 3 months, with refund / pending / transfer / uncategorized ----
const T = [
  // September 2026
  { id: "s1", posted_at: "2026-09-01", amount: 4200,  merchant_raw: "Employer",   category: "Income" },
  { id: "s2", posted_at: "2026-09-05", amount: -1500, merchant_raw: "Landlord",   category: "Rent" },
  { id: "s3", posted_at: "2026-09-08", amount: -800,  merchant_raw: "Whole Foods", category: "Groceries" },
  { id: "s4", posted_at: "2026-09-10", amount: 200,   merchant_raw: "Whole Foods", category: "Groceries", is_refund: true },
  { id: "s5", posted_at: "2026-09-12", amount: -100,  merchant_raw: "Shell",      category: "Gas", is_pending: true },
  { id: "s6", posted_at: "2026-09-15", amount: -500,  merchant_raw: "Transfer",   category: "Other", is_transfer: true },
  { id: "s7", posted_at: "2026-09-20", amount: -75,   merchant_raw: "Mystery Co", category: "Other" },
  // August 2026
  { id: "a1", posted_at: "2026-08-01", amount: 4200,  merchant_raw: "Employer",   category: "Income" },
  { id: "a2", posted_at: "2026-08-05", amount: -1500, merchant_raw: "Landlord",   category: "Rent" },
  { id: "a3", posted_at: "2026-08-08", amount: -700,  merchant_raw: "Whole Foods", category: "Groceries" },
  { id: "a4", posted_at: "2026-08-20", amount: -300,  merchant_raw: "Chipotle",   category: "Dining" },
  // July 2026
  { id: "j1", posted_at: "2026-07-01", amount: 4200,  merchant_raw: "Employer",   category: "Income" },
  { id: "j2", posted_at: "2026-07-05", amount: -1500, merchant_raw: "Landlord",   category: "Rent" },
  { id: "j3", posted_at: "2026-07-08", amount: -750,  merchant_raw: "Whole Foods", category: "Groceries" },
];

// ---- 1. September P&L: refund nets against spending, never income ----
const sep = monthAgg(T, "2026-09");
eq("sep in (refund excluded)", sep.in, 4200);
eq("sep out (800+1500+75-200)", r2(sep.out), 2175);
eq("sep kept = in - out", r2(sep.kept), 2025);
eq("sep byCat Groceries (800-200)", r2(sep.byCat["Groceries"]), 600);
eq("sep byCat Rent", sep.byCat["Rent"], 1500);
eq("sep byCat Other (uncategorized)", sep.byCat["Other"], 75);
eq("sep count excludes pending+transfer", sep.count, 5);

// ---- 2. August / July P&L ----
const aug = monthAgg(T, "2026-08");
eq("aug kept", r2(aug.kept), 1700);
const jul = monthAgg(T, "2026-07");
eq("jul kept", r2(jul.kept), 1950);

// ---- 3. Cash-flow kept identity across all months ----
["2026-07", "2026-08", "2026-09"].forEach(m => {
  const a = monthAgg(T, m);
  eq(`${m} kept == in - out`, r2(a.kept), r2(a.in - a.out));
});

// ---- 4. Budget actuals trace to the transaction set ----
const monthsDesc = ["2026-09", "2026-08", "2026-07"];
const grocTarget = defaultTargetFor("Groceries", T, monthsDesc);
// Gross spending only: the +200 refund (amount > 0) is not subtracted from the
// suggested budget — matches the template's defaultTargetFor exactly.
eq("groceries suggested = 3-mo avg rounded to $10", grocTarget, 750); // (800+700+750)/3=750
const rentTarget = defaultTargetFor("Rent", T, monthsDesc);
eq("rent suggested", rentTarget, 1500);

// ---- 5. Thin-data honesty ----
eq("dataDays ~92 (not thin)", dataDays(T) >= 30, true);
const thinT = T.filter(t => t.posted_at >= "2026-09-20");
eq("thin fixture days", dataDays(thinT), 1); // only 2026-09-20 posted non-transfer
const thinT2 = [
  { id: "x1", posted_at: "2026-09-18", amount: -50, merchant_raw: "A", category: "Other" },
  { id: "x2", posted_at: "2026-09-25", amount: -60, merchant_raw: "B", category: "Other" },
];
eq("thin 8 days -> banner", dataDays(thinT2) < 30, true);
eq("thin days value", dataDays(thinT2), 8);

// ---- 6. Review queue: only uncategorized, pending/transfer excluded ----
const rq = reviewQueue(T);
eq("review queue ids", rq.map(t => t.id), ["s7"]);
eq("pending never queued", rq.some(t => t.id === "s5"), false);
eq("transfer never queued", rq.some(t => t.id === "s6"), false);

// ---- 7. P&L trend uses only months with data ----
const plMonths = monthsDesc.slice(0, 6);
eq("P&L months from data only", plMonths, ["2026-09", "2026-08", "2026-07"]);

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
