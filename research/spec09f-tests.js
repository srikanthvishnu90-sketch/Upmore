// SPEC 09f tests: reconciliation pipeline — pending->posted, refunds,
// duplicate preservation. Extracted from the shipped bundle.
const fs = require("fs");
eval(fs.readFileSync("/tmp/recon-fns.js", "utf8"));

let pass = 0, fail = 0;
const t = (n, c, x) => { c ? pass++ : (fail++, console.log("FAIL:", n, x || "")); };

// --- matchRefunds ---
const charge = { id: "c1", merchant_raw: "Amazon", amount: -52.10, posted_at: "2026-09-01", is_pending: false };
const refund = { id: "r1", merchant_raw: "Amazon Refund", amount: 52.10, posted_at: "2026-09-10", is_pending: false };
const payroll = { id: "p1", merchant_raw: "Payroll ACME", amount: 3000, posted_at: "2026-09-05", is_pending: false };
const mystery = { id: "m1", merchant_raw: "Unknown Credit", amount: 25, posted_at: "2026-09-06", is_pending: false };
matchRefunds([charge, refund, payroll, mystery]);
t("refund matched", refund.is_refund === true && refund.refunded_tx === "c1");
t("payroll not refund", !payroll.is_refund && !payroll.is_unmatched_credit);
t("unmatched flagged", mystery.is_unmatched_credit === true);
t("charge untouched", !charge.is_refund);

// refund outside 90-day window -> unmatched
const old = { id: "c2", merchant_raw: "Store", amount: -20, posted_at: "2026-01-01" };
const late = { id: "r2", merchant_raw: "Store Refund", amount: 20, posted_at: "2026-09-10" };
matchRefunds([old, late]);
t("stale refund unmatched", late.is_unmatched_credit === true);

// --- isCountableInflow ---
t("refund excluded from income", isCountableInflow(refund) === false);
t("unmatched excluded from income", isCountableInflow(mystery) === false);
t("payroll counts", isCountableInflow(payroll) === true);

// --- reconcileTransactions: pending -> posted ---
const hold = { id: "h1", provider_id: "p-h1", merchant_raw: "Shell", amount: -40, posted_at: "2026-09-10", is_pending: true };
const settled = { id: "s1", provider_id: "p-s1", merchant_raw: "Shell", amount: -42.50, posted_at: "2026-09-12", is_pending: false };
let merged = reconcileTransactions([], [hold]);
merged = reconcileTransactions(merged, [settled]);
t("pending replaced by posted", merged.length === 1 && merged[0].id === "s1" && !merged[0].is_pending);

// same provider_id twice -> one row
const a = { id: "a1", provider_id: "dup", merchant_raw: "X", amount: -5, posted_at: "2026-09-01" };
const b = { id: "a2", provider_id: "dup", merchant_raw: "X", amount: -5, posted_at: "2026-09-01" };
merged = reconcileTransactions([], [a, b]);
t("provider dedupe", merged.length === 1);

// genuine duplicates (different provider ids, same merchant/amount) NEVER merged
const g1 = { id: "g1", provider_id: "p1", merchant_raw: "Starbucks", amount: -6.50, posted_at: "2026-09-10" };
const g2 = { id: "g2", provider_id: "p2", merchant_raw: "Starbucks", amount: -6.50, posted_at: "2026-09-10" };
merged = reconcileTransactions([], [g1, g2]);
t("real duplicates preserved", merged.length === 2);

// pending hold + posted same provider_id -> replaced, not duplicated
const hp = { id: "hp", provider_id: "same", merchant_raw: "Hotel", amount: -200, posted_at: "2026-09-01", is_pending: true };
const sp = { id: "sp", provider_id: "same", merchant_raw: "Hotel", amount: -200, posted_at: "2026-09-03", is_pending: false };
merged = reconcileTransactions([hp], [sp]);
t("same-id settlement replaces", merged.length === 1 && merged[0].id === "sp");

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
