// SPEC 08 brokerage-max deterministic tests (2026-09-27).
// Mirrors the portfolioSummary math in src/upmore-app-template.html.
// Run: node research/spec08-brokerage-max-tests.js
"use strict";

let pass = 0, fail = 0;
function eq(name, actual, expected) {
  const ok = JSON.stringify(actual) === JSON.stringify(expected);
  if (ok) { pass++; }
  else { fail++; console.log(`FAIL ${name}: got ${JSON.stringify(actual)}, want ${JSON.stringify(expected)}`); }
}

// --- engine mirror: dividend income, sectors, losers ---
function summarize(holdings) {
  const total = holdings.reduce((s, h) => s + (h.value || 0), 0);
  let divAnnual = 0, divKnown = 0;
  const bySector = {};
  const losers = [];
  holdings.forEach(h => {
    const y = Number(h.dividend_yield);
    if (y > 0) { divAnnual += (h.value || 0) * y; divKnown++; }
    const sec = (h.sector && h.sector !== "\u2014") ? h.sector : null;
    if (sec) bySector[sec] = (bySector[sec] || 0) + (h.value || 0);
    if (h.cost_basis != null && h.cost_basis > 0 && (h.value || 0) < h.cost_basis) losers.push(h.symbol);
  });
  return { total, divAnnual, divKnown, bySector, losers,
           portYield: total > 0 ? divAnnual / total * 100 : 0 };
}

// --- meta-merge mirror: device-local notes on read-only holdings ---
function mergeMeta(holdings, meta) {
  return holdings.map(h => {
    const o = meta[h.id];
    if (!o) return h;
    return { ...h, sector: o.sector || h.sector || null,
             dividend_yield: o.dividend_yield != null ? o.dividend_yield : h.dividend_yield,
             meta_note: true };
  });
}

// --- drift mirror ---
function drift(actualPct, targetPct) { return actualPct - targetPct; }

const H = [
  { id: "m1", symbol: "VTI",  value: 2800, dividend_yield: 0.01,   sector: "US stocks",  cost_basis: 2500 },
  { id: "m2", symbol: "AAPL", value: 900,  dividend_yield: 0.0044, sector: "Technology", cost_basis: 1000 },
  { id: "m3", symbol: "XYZ",  value: 800,  dividend_yield: null,   sector: "Energy",     cost_basis: 1000 },
  { id: "m4", symbol: "CASH", value: 0,    dividend_yield: null,   sector: null,         cost_basis: 0 },
];

const s = summarize(H);
eq("total", s.total, 4500);
eq("divAnnual ~31.96", Math.round(s.divAnnual * 100) / 100, 31.96);
eq("divKnown", s.divKnown, 2);
eq("portYield ~0.71", Math.round(s.portYield * 100) / 100, 0.71);
eq("bySector", s.bySector, { "US stocks": 2800, "Technology": 900, "Energy": 800 });
eq("losers (below cost basis)", s.losers, ["AAPL", "XYZ"]);

// zero / missing data states
const z = summarize([]);
eq("empty total", z.total, 0);
eq("empty divAnnual", z.divAnnual, 0);
eq("empty losers", z.losers, []);
eq("empty portYield", z.portYield, 0);
const nz = summarize([{ id: "x", symbol: "Q", value: 500, dividend_yield: null, sector: null, cost_basis: null }]);
eq("no-yield divKnown", nz.divKnown, 0);
eq("no-sector bySector", nz.bySector, {});
eq("no-cost-basis losers", nz.losers, []);

// mixed manual + plaid sources
const mixed = summarize([
  { id: "p1", symbol: "VTI", value: 2800, dividend_yield: null, sector: null, source: "plaid", cost_basis: null },
  { id: "m1", symbol: "BND", value: 1200, dividend_yield: 0.03, sector: "Bonds", source: "manual", cost_basis: 1200 },
]);
eq("mixed divAnnual", mixed.divAnnual, 36);
eq("mixed divKnown", mixed.divKnown, 1);

// meta merge: plaid holding gains sector/yield notes without mutation
const plaid = [{ id: "p1", symbol: "VTI", value: 2800, source: "plaid" }];
const merged = mergeMeta(plaid, { p1: { sector: "US stocks", dividend_yield: 0.01 } });
eq("meta sector", merged[0].sector, "US stocks");
eq("meta yield", merged[0].dividend_yield, 0.01);
eq("meta flag", merged[0].meta_note, true);
eq("orig unmutated", plaid[0].sector, undefined);
const sm = summarize(merged);
eq("meta feeds dividends", Math.round(sm.divAnnual), 28);

// drift: signed percentage-point deltas
eq("drift over", Math.round(drift(62.2, 60) * 10) / 10, 2.2);
eq("drift under", Math.round(drift(20, 30) * 10) / 10, -10);
eq("drift zero", drift(10, 10), 0);

// benchmark constants (facts-only context, Sept 2026)
const SP500_DIV_YIELD_PCT = 1.0, SP500_DIV_ASOF = "Sept 2026", SP500_INDEX_FEE_PCT = 0.03;
eq("spx yield const", SP500_DIV_YIELD_PCT, 1.0);
eq("spx asof const", SP500_DIV_ASOF, "Sept 2026");
eq("spx fee const", SP500_INDEX_FEE_PCT, 0.03);

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
