
  // ---- Transactions: merchant rules + bulk recategorize (Monarch/YNAB parity) ----
  const TXRULE_LS = "upmore_tx_rules_v1";
  function txRulesGet() { try { return JSON.parse(localStorage.getItem(TXRULE_LS) || "{}"); } catch (e) { return {}; } }
  function txRulesSet(r) { try { localStorage.setItem(TXRULE_LS, JSON.stringify(r)); } catch (e) {} }
  function txRuleFor(t) {
    if (!t) return null;
    const rules = txRulesGet();
    const mid = t.merchant_id || (typeof normalizeMerchant === "function" ? normalizeMerchant(t.merchant_raw || "") : "");
    return rules[mid] || null;
  }
  function setTxRule(merchantRaw, merchantId, cat) {
    const rules = txRulesGet();
    rules[merchantId] = cat;
    txRulesSet(rules);
  }
  // Open the rule picker: pick a category once, apply to every past + future
  // transaction from this merchant.
  function openRuleSheet(merchantRaw, merchantId) {
    const cats = allCats();
    openBudgetSheet(`Rule: ${merchantRaw}`,
      `<p class="psub">Pick a category. Every transaction from ${esc(merchantRaw)} — past and future — goes there automatically. You can still move single ones by hand.</p>
       <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:6px">
        ${cats.map(c => `<button class="ghostbtn" data-rulecat="${esc(c)}" style="margin:0">${esc(c)}</button>`).join("")}
       </div>`);
    $("budgetSheetBody").querySelectorAll("[data-rulecat]").forEach(b => b.onclick = () => {
      const cat = b.dataset.rulecat;
      setTxRule(merchantRaw, merchantId, cat);
      // Apply to all existing matching transactions via overrides.
      const { transactions } = loadTrackData();
      const ov = blsGet(BUDGET_LS.overrides, {}) || {};
      let n = 0;
      (transactions || []).forEach(t => {
        const mid = t.merchant_id || (typeof normalizeMerchant === "function" ? normalizeMerchant(t.merchant_raw || "") : "");
        if (mid === merchantId && t.id != null) { ov[t.id] = cat; n++; }
      });
      blsSet(BUDGET_LS.overrides, ov);
      closeBudgetSheet();
      if (typeof renderTxScreen === "function") renderTxScreen();
      toast(`Rule saved — ${n} transaction${n === 1 ? "" : "s"} moved to ${cat}.`);
    });
  }

  // Bulk select state for the transaction list.
  let txSelectMode = false;
  const txBulkSel = new Set();
  function txBulkBarHtml() {
    if (!txSelectMode) return "";
    return `<div class="bulkbar">
      <b style="font-size:13.5px">${txBulkSel.size} selected</b>
      <div class="sel" style="flex:1"><select id="bulkCat" aria-label="Category for selected">${allCats().map(c => `<option>${esc(c)}</option>`).join("")}</select></div>
      <button class="tgt" id="bulkApply">Move</button>
      <button class="tgt" id="bulkDone">Done</button>
    </div>`;
  }
  function wireBulkBar() {
    const ap = $("bulkApply"), dn = $("bulkDone");
    if (dn) dn.onclick = () => { txSelectMode = false; txBulkSel.clear(); renderTxScreen(); syncTxSelectBtn(); };
    if (ap) ap.onclick = () => {
      const cat = $("bulkCat").value;
      if (!allCats().includes(cat) || !txBulkSel.size) return;
      const ov = blsGet(BUDGET_LS.overrides, {}) || {};
      txBulkSel.forEach(id => { ov[id] = cat; });
      blsSet(BUDGET_LS.overrides, ov);
      toast(`${txBulkSel.size} moved to ${cat}.`);
      txBulkSel.clear(); renderTxScreen();
    };
  }
  function syncTxSelectBtn() {
    const b = $("txSelectBtn");
    if (b) b.textContent = txSelectMode ? "Cancel" : "Select";
  }

  // ---- Net worth: accounts + manual assets − liabilities, monthly snapshots ----
  const NW_LS = { assets: "upmore_nw_assets_v1", liabs: "upmore_nw_liabs_v1", snaps: "upmore_nw_snaps_v1" };
  function nwListGet(k) { try { const v = JSON.parse(localStorage.getItem(k) || "[]"); return Array.isArray(v) ? v : []; } catch (e) { return []; } }
  function nwListSet(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }
  function netWorthCalc() {
    const { accounts } = loadTrackData();
    const bank = (accounts || []).reduce((s, a) => s + (Number(a.balance) || 0), 0);
    const assets = nwListGet(NW_LS.assets).reduce((s, a) => s + Number(a.value || 0), 0);
    const liabs = nwListGet(NW_LS.liabs).reduce((s, a) => s + Number(a.value || 0), 0);
    let debts = 0;
    try { debts = (JSON.parse(localStorage.getItem("cfo_debt_debts") || "[]") || []).reduce((s, x) => s + Number(x.balance || 0), 0); } catch (e) {}
    return { bank, assets, liabs, debts, total: bank + assets - liabs - debts };
  }
  function nwSnapshot(total) {
    const ym = new Date().toISOString().slice(0, 7);
    let snaps = {};
    try { snaps = JSON.parse(localStorage.getItem(NW_LS.snaps) || "{}"); } catch (e) {}
    snaps[ym] = Math.round(total);
    try { localStorage.setItem(NW_LS.snaps, JSON.stringify(snaps)); } catch (e) {}
    return snaps;
  }
  function nwSparkSVG(snaps) {
    const keys = Object.keys(snaps).sort().slice(-12);
    if (keys.length < 2) return `<p class="psub">Two months of history and the trend line appears here.</p>`;
    const vals = keys.map(k => snaps[k]);
    const min = Math.min(...vals), max = Math.max(...vals), rng = Math.max(1, max - min);
    const W = 340, H = 90, P = 10;
    const X = i => P + i / (keys.length - 1) * (W - 2 * P);
    const Y = v => H - P - ((v - min) / rng) * (H - 2 * P);
    const d = vals.map((v, i) => `${i ? "L" : "M"}${X(i).toFixed(1)},${Y(v).toFixed(1)}`).join(" ");
    const chg = vals[vals.length - 1] - vals[0];
    return `<div class="pacewrap" role="img" aria-label="Net worth trend: ${bm0(vals[0])} to ${bm0(vals[vals.length - 1])}">
      <svg viewBox="0 0 ${W} ${H}" preserveAspectRatio="none"><path d="${d}" fill="none" stroke="var(--ink)" stroke-width="2.5"/></svg>
      <div class="pacelegend"><span>${esc(keys[0])}: ${bm0(vals[0])}</span><span>now: ${bm0(vals[vals.length - 1])} (${chg >= 0 ? "+" : "−"}${bm0(Math.abs(chg))})</span></div></div>`;
  }
  function renderNetWorth() {
    const body = $("nwBody"); if (!body) return;
    const nw = netWorthCalc();
    const snaps = nwSnapshot(nw.total);
    const assets = nwListGet(NW_LS.assets), liabs = nwListGet(NW_LS.liabs);
    const row = (a, kind) => `<div class="nwrow"><div><b>${esc(a.name)}</b><br><span class="dim" style="font-size:12px">${esc(a.kind || "")}</span></div>
      <span>${bm0(a.value)} <button class="tgt" data-nwdel="${kind}:${a.id}" aria-label="Remove">✕</button></span></div>`;
    body.innerHTML = `
      <p class="psub">Everything you own minus everything you owe. Bank balances come from your connected accounts; the rest you add once and update when it changes.</p>
      <div class="pcard" style="margin-top:10px"><p class="bsum" style="font-size:22px"><b>${bm0(nw.total)}</b></p>
        <p class="psub" style="margin:6px 0 0">${bm0(nw.bank)} in accounts · ${bm0(nw.assets)} other assets · ${bm0(nw.liabs + nw.debts)} owed</p></div>
      <h2 class="sec">Trend</h2>
      <div class="pcard">${nwSparkSVG(snaps)}</div>
      <h2 class="sec">Other assets (${assets.length})</h2>
      <div class="bcard">${assets.length ? assets.map(a => row(a, "a")).join("") : `<p class="psub">None yet — home, car, crypto, anything with value.</p>`}</div>
      <button class="ghostbtn" id="nwAddA" style="margin-top:8px">+ Add asset</button>
      <h2 class="sec">Debts & liabilities (${liabs.length})</h2>
      <div class="bcard">${liabs.length ? liabs.map(a => row(a, "l")).join("") : `<p class="psub">None added here. Balances from the Debt payoff plan count automatically.</p>`}</div>
      <button class="ghostbtn" id="nwAddL" style="margin-top:8px">+ Add liability</button>
      <div id="nwForm"></div>`;
    body.querySelectorAll("[data-nwdel]").forEach(b => b.onclick = () => {
      const [kind, id] = b.dataset.nwdel.split(":");
      if (kind === "a") nwListSet(NW_LS.assets, nwListGet(NW_LS.assets).filter(x => String(x.id) !== id));
      else nwListSet(NW_LS.liabs, nwListGet(NW_LS.liabs).filter(x => String(x.id) !== id));
      renderNetWorth();
    });
    const form = (kind) => {
      $("nwForm").innerHTML = `<div class="svform" style="margin-top:12px">
        <label class="f"><span>Name</span><input id="nwName" placeholder="${kind === "a" ? "Car, crypto, home…" : "Loan, credit card…"}" autocomplete="off"></label>
        <label class="f"><span>Value ($)</span><input id="nwVal" inputmode="decimal" placeholder="15000" autocomplete="off"></label>
        <button class="go" id="nwSave" style="height:48px">Save</button></div>`;
      $("nwSave").onclick = () => {
        const name = $("nwName").value.trim(), val = parseFloat($("nwVal").value);
        if (!name || !(val >= 0)) { toast("Name and value needed."); return; }
        const key = kind === "a" ? NW_LS.assets : NW_LS.liabs;
        const list = nwListGet(key);
        list.push({ id: "nw" + Date.now(), name, kind: kind === "a" ? "Manual asset" : "Manual liability", value: val });
        nwListSet(key, list); renderNetWorth(); toast("Saved.");
      };
    };
    $("nwAddA").onclick = () => form("a");
    $("nwAddL").onclick = () => form("l");
  }

  // ---- Claim: per-state document checklists + annual re-search reminders ----
  // Portal URLs below are the well-known official filing sites; everything
  // else routes through MissingMoney.com (NAUPA-endorsed). Notarization rules
  // change — every checklist says to confirm on the state site.
  const CLAIM_PORTALS = {
    "California": "https://claimit.ca.gov", "Texas": "https://www.claimittexas.gov",
    "New York": "https://www.osc.ny.gov/unclaimed-funds", "Florida": "https://www.fltreasurehunt.gov",
    "Illinois": "https://icash.illinoistreasurer.gov", "Pennsylvania": "https://www.patreasury.gov/unclaimed-property",
    "Ohio": "https://www.com.ohio.gov/unclaimed", "Michigan": "https://www.michigan.gov/unclaimedproperty",
    "New Jersey": "https://www.unclaimedproperty.nj.gov", "Washington": "https://ucp.dor.wa.gov",
    "Massachusetts": "https://www.findmassmoney.gov", "Virginia": "https://www.vamoneysearch.gov",
  };
  const CLAIM_DOCS = [
    "Government photo ID (driver's license or passport)",
    "Proof of Social Security number",
    "Proof of address tying you to the address on record (old mail, lease, utility bill)",
    "Proof you owned it, if you have it (old statement, pay stub, policy)",
    "Notarization: most states require it for larger claims — the state site says when",
    "Heir claim? You'll also need the death certificate and proof you're the heir",
  ];
  function claimChecklistHtml(state) {
    const portal = CLAIM_PORTALS[state] || CLAIM_SEARCH_URL;
    return `<div class="pcard" style="margin-top:12px"><p class="bsum" style="font-size:14.5px"><b>Claiming in ${esc(state)}</b></p>
      <ul class="chklist">${CLAIM_DOCS.map(d => `<li>${esc(d)}</li>`).join("")}</ul>
      <p class="psub" style="margin-top:10px">File at the official site — never pay anyone to claim for you.</p>
      <button class="ghostbtn" id="cfPortal">Open ${esc(state)}'s official claim site →</button></div>`;
  }

  // ---- CFO: credit factors tool (Credit Karma parity, math not scores) ----
  // We never show or predict a score — only the factors lenders use and the
  // arithmetic on utilization. FICO + Vantage weights labeled.
  function cfoCredit(body) {
    const factors = [
      ["Payment history", "35% of FICO · 40% of VantageScore", "One on-time streak matters more than anything else."],
      ["Amounts owed (utilization)", "30% of FICO · 21% of VantageScore", "Balance ÷ limit across cards. Under 30% is the common line; under 10% is better."],
      ["Length of history", "15% of FICO · 20% of VantageScore", "Average age of accounts. Don't close your oldest card."],
      ["New credit", "10% of FICO · 5% of VantageScore", "Hard inquiries from applications. A few is fine."],
      ["Credit mix", "10% of FICO · 11% of VantageScore", "Cards + installment loans. Don't open accounts just for mix."],
    ];
    body.innerHTML = `
      <p class="psub">Nobody can tell you your exact score without pulling it — but these are the five factors every lender's model uses, and the utilization math is exact.</p>
      <h2 class="sec">The five factors</h2>
      <div class="bcard">${factors.map(f => `<div class="mrow"><div><b>${esc(f[0])}</b><i>${esc(f[1])} — ${esc(f[2])}</i></div></div>`).join("")}</div>
      <h2 class="sec">Utilization calculator</h2>
      <div class="pcard"><div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
        <label class="f"><span>Total card balances ($)</span><input id="crBal" inputmode="decimal" placeholder="1200"></label>
        <label class="f"><span>Total credit limits ($)</span><input id="crLim" inputmode="decimal" placeholder="5000"></label>
        <label class="f"><span>Pay down ($, optional)</span><input id="crPay" inputmode="decimal" placeholder="500"></label>
      </div>
      <button class="go" id="crRun" style="margin-top:10px;height:48px">Do the math</button>
      <div id="crOut" style="margin-top:10px"></div></div>
      <p class="fine" style="margin-top:8px">Weights: FICO Score 35/30/15/10/10; VantageScore 4.0 40/21/20/11/5/3 (the last 3% is "available credit"). This is education, not a score prediction.</p>`;
    $("crRun").onclick = () => {
      const g = id => { const v = parseFloat(($(id) || {}).value); return isNaN(v) ? 0 : v; };
      const bal = Math.max(0, g("crBal")), lim = Math.max(0, g("crLim")), pay = Math.max(0, g("crPay"));
      const out = $("crOut");
      if (!(lim > 0)) { out.innerHTML = `<p class="psub">Enter your total credit limit first.</p>`; return; }
      const u = bal / lim * 100, u2 = Math.max(0, bal - pay) / lim * 100;
      const band = x => x < 10 ? "excellent territory (under 10%)" : x < 30 ? "under the 30% line lenders like" : "above 30% — the factor dragging hardest";
      out.innerHTML = `<div class="bcard"><div class="mrow"><div><b>Now: ${u.toFixed(1)}%</b><i>${band(u)}</i></div><span>${bm0(bal)} / ${bm0(lim)}</span></div>` +
        (pay > 0 ? `<div class="mrow"><div><b>After paying ${bm0(pay)}: ${u2.toFixed(1)}%</b><i>${band(u2)}</i></div><span>${bm0(Math.max(0, bal - pay))} / ${bm0(lim)}</span></div>` : "") +
        `</div><p class="psub" style="margin-top:8px">Paying down balances is the fastest lever you control — no new accounts needed.</p>`;
    };
  }
