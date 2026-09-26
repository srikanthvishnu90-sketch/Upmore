
  /* ================= SPEC 09: "NOBODY SHOULD WIN" (2026-09-26) =================
     Competitive gaps closed vs Monarch / YNAB / Rocket Money / Copilot /
     EveryDollar / Empower / DoNotPay / state programs:
       - subscription defense: trial warnings, approval queue, negotiation
         scripts, fee-waiver scripts, annualized rows (zombie-charge monitoring
         already shipped: the cancel watcher re-queues "They charged you anyway")
       - budget: pace chart, projection colors, savings rate, age of money,
         committed spending from real upcoming charges, recurring calendar
       - transactions: merchant rules, bulk recategorize
       - net worth: assets − liabilities + monthly snapshots + trend
       - investments: per-holding return % (wired into positions), trim math
         (wired into concentration), Monte Carlo retirement check (below)
       - claim: per-state document checklists + annual re-search reminders
       - CFO: credit factors tool
     No red/green anywhere — the no-guilt palette holds for every new element. */

  // ---- Monte Carlo retirement check (SPEC 08 depth, Empower parity) ----
  // Deterministic: mulberry32 seed → identical results every run. Assumptions
  // are disclosed next to the button; analysis only, never a promise.
  function monteCarlo(o) {
    const years = Math.max(1, (o.ret || 65) - (o.age || 19));
    const MEAN = 0.07, SD = 0.15, INFL = 0.025, N = 1000;
    let seed = 20260926;
    const rnd = () => {
      seed |= 0; seed = seed + 0x6D2B79F5 | 0;
      let t = Math.imul(seed ^ seed >>> 15, 1 | seed);
      t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
      return ((t ^ t >>> 14) >>> 0) / 4294967296;
    };
    const needAtRet = (o.need || 50000) * Math.pow(1 + INFL, years);
    const target = needAtRet / 0.04; // 4% rule
    let wins = 0; const finals = new Array(N);
    for (let i = 0; i < N; i++) {
      let v = Math.max(0, o.now || 0);
      for (let y = 0; y < years; y++) {
        const u1 = rnd(), u2 = rnd();
        const z = Math.sqrt(-2 * Math.log(u1 + 1e-12)) * Math.cos(2 * Math.PI * u2);
        v = v * (1 + MEAN + SD * z) + (o.monthly || 0) * 12;
        if (v < 0) v = 0;
      }
      finals[i] = v;
      if (v >= target) wins++;
    }
    finals.sort((a, b) => a - b);
    return { success: Math.round(wins / N * 100), median: Math.round(finals[500]), target: Math.round(target) };
  }

  // ---- Subscription defense: queue cards (SPEC 02 extension) ----
  const NEGOTIATE_FOR = /(at&t|verizon|t-mobile|spectrum|comcast|xfinity|cox|dish|directv|geico|progressive|state farm|allstate|pge|comed|con ?ed|duke energy|national grid|centurylink|lumen|frontier|optimum|charter)/i;
  const FEE_RE = /(overdraft|insufficient fund|late fee|late payment|maintenance fee|monthly service fee|atm fee|foreign transaction fee|returned item|nonsufficient)/i;

  function detectFees(txs) {
    return (txs || []).filter(t => t && t.amount < 0 && !t.is_pending && !t.is_transfer
      && FEE_RE.test(t.merchant_raw || "")).slice(0, 5);
  }

  async function subDefenseCards() {
    const cards = [];
    try {
      const { transactions } = loadTrackData();
      const signed = (typeof getSessionToken === "function") ? !!(await getSessionToken()) : false;
      const rows = signed && typeof saveRows === "function"
        ? await saveRows("save_subscriptions", "created_at", false) : localSubsGet();
      const act = (rows || []).filter(r => r.status !== "cancelled");
      const nowMs = Date.now();
      // (a) Trial conversion warnings ≤ 7 days out. Rocket Money paywalls
      // early warnings; ours are free and fire before the charge.
      act.filter(s => s.billing_interval === "trial" && s.next_billing_date).forEach(s => {
        const days = Math.round((new Date(s.next_billing_date) - nowMs) / 864e5);
        if (days >= 0 && days <= 7) {
          cards.push({
            type: "trial", id: "trialwarn-" + s.id,
            title: `${s.merchant} trial ends in ${days} day${days === 1 ? "" : "s"}`,
            sub: `First charge ${money$(s.amount)} hits ${s.next_billing_date}. Cancel before if you're not keeping it.`,
            dollars: Number(s.amount) * 12, conf: 0.95, urg: 5, eff: 3,
            cta: "How to cancel",
            act: () => { show("guide"); if (typeof guideAsk === "function") guideAsk(`How do I cancel ${s.merchant} before the trial ends on ${s.next_billing_date}?`); },
            why: "Trial converts to a paid charge within 7 days."
          });
        }
      });
      // (b) Recurring-charge approval queue: detected but not tracked yet.
      // Monarch prompts to verify new recurring charges — same idea, one card.
      let recs = [];
      try { recs = (detectRecurrence(transactions || []) || []).filter(r => !r.dormant); } catch (e) {}
      const trackedMids = new Set(act.map(s => normalizeMerchant(s.merchant || "")));
      let dismissed = new Set();
      try { dismissed = new Set(JSON.parse(localStorage.getItem("upmore_rec_dismissed") || "[]")); } catch (e) {}
      const fresh = recs.filter(r => !trackedMids.has(r.merchant_id) && !dismissed.has(r.merchant_id));
      if (fresh.length) {
        cards.push({
          type: "approval", id: "rec-approval",
          title: `Found ${fresh.length} repeating charge${fresh.length === 1 ? "" : "s"}`,
          sub: fresh.slice(0, 3).map(r => `${r.merchant_raw} ${money$(Math.abs(r.amount))}/${r.interval}`).join(" · ") + (fresh.length > 3 ? ` +${fresh.length - 3} more` : ""),
          dollars: fresh.reduce((s, r) => s + Math.abs(r.amount) * 12, 0), conf: 0.9, urg: 3, eff: 2,
          cta: "Review them", act: () => openApprovalQueue(fresh),
          why: "Repeating charges that aren't on your tracked list yet."
        });
      }
      // (c) Bank-fee waiver script from detected fee transactions.
      const fees = detectFees(transactions);
      if (fees.length) {
        const f = fees[0];
        cards.push({
          type: "fee", id: "feewaive-" + f.id,
          title: `A $${Math.abs(f.amount).toFixed(2)} bank fee from ${f.merchant_raw}`,
          sub: "First-time fees get waived when you ask the right way — here's the exact script.",
          dollars: Math.abs(f.amount), conf: 0.9, urg: 3, eff: 4,
          cta: "Get the script", act: () => openFeeSheet(f),
          why: "Bank fee detected — waiver scripts work well on first offenses."
        });
      }
      // (d) Bill negotiation: utility/telecom subs get the exact call script, free.
      const neg = act.find(s => NEGOTIATE_FOR.test(s.merchant || ""));
      if (neg && !dismissed.has("neg-" + neg.id)) {
        cards.push({
          type: "negotiate", id: "neg-" + neg.id,
          title: `Lower your ${neg.merchant} bill`,
          sub: `You're paying ${money$(neg.amount)}/mo. A 5-minute call with this exact script often cuts 10–30%.`,
          dollars: Math.round(Number(neg.amount) * 12 * 0.2), conf: 0.5, urg: 2, eff: 6,
          cta: "Get the script", act: () => openNegotiateSheet(neg),
          cta2: "Not interested", act2: () => { dismissed.add("neg-" + neg.id); try { localStorage.setItem("upmore_rec_dismissed", JSON.stringify([...dismissed])); } catch (e) {} renderQueue(); },
          why: "Utility/telecom bills are negotiable — script included, no fee."
        });
      }
    } catch (e) { /* defense never breaks the queue */ }
    return cards;
  }

  function openApprovalQueue(recs) {
    openBudgetSheet(`Repeating charges (${recs.length})`,
      `<p class="psub">These bill on a schedule but aren't on your tracked list. Track the ones you want to watch — or dismiss the rest.</p>` +
      recs.map(r => `<div class="mrow"><div><b>${esc(r.merchant_raw)}</b><i>${money$(Math.abs(r.amount))} ${esc(r.interval)} · ${r.occurrences} charges seen</i></div>
        <span style="display:flex;gap:6px;flex-shrink:0"><button class="tgt" data-track="${esc(r.merchant_id)}">Track</button><button class="tgt" data-nosub="${esc(r.merchant_id)}">Not a sub</button></span></div>`).join(""));
    const body = $("budgetSheetBody");
    body.querySelectorAll("[data-track]").forEach(b => b.onclick = async () => {
      const r = recs.find(x => x.merchant_id === b.dataset.track);
      if (!r) return;
      const row = { merchant: r.merchant_raw, amount: Math.abs(r.amount), currency: "USD",
        billing_interval: r.interval === "monthly" ? "monthly" : r.interval === "yearly" ? "yearly" : "monthly",
        next_billing_date: r.next_date || null, status: "active", detected_via: "approval_queue" };
      const signed = (typeof getSessionToken === "function") ? !!(await getSessionToken()) : false;
      if (signed && typeof saveInsert === "function") await saveInsert("save_subscriptions", row);
      else { const lr = localSubsGet(); row.id = "local-" + Date.now(); lr.push(row); localSubsSet(lr); }
      toast(`${r.merchant_raw} is now tracked.`);
      closeBudgetSheet(); renderSubs(); renderQueue();
    });
    body.querySelectorAll("[data-nosub]").forEach(b => b.onclick = () => {
      let d = new Set();
      try { d = new Set(JSON.parse(localStorage.getItem("upmore_rec_dismissed") || "[]")); } catch (e) {}
      d.add(b.dataset.nosub);
      try { localStorage.setItem("upmore_rec_dismissed", JSON.stringify([...d])); } catch (e) {}
      b.closest(".mrow").remove();
      renderQueue();
    });
  }

  function negotiateScript(s) {
    const years = "a while";
    return `Call the number on your ${s.merchant} bill (or the "contact us" page in your account). Say exactly this:\n\n"Hi, I've been a customer for ${years} and my bill is ${money$(s.amount)} a month now. I'd like to lower it — can you check what retention or loyalty offers are on my account?"\n\nThen wait. Don't accept the first offer. If they say nothing is available:\n\n"I understand. Before I look at other options, is there a supervisor who can review loyalty pricing?"\n\nNotes that matter:\n• Call mid-month, Tuesday–Thursday mornings — shortest holds.\n• Have your account number ready.\n• If they offer a promo rate, ask: "How long does that rate last, and what does it go to after?"\n• Never agree to a longer contract to get the discount unless you want it.`;
  }

  function openNegotiateSheet(s) {
    openBudgetSheet(`Lower your ${s.merchant} bill`,
      `<p class="psub">Paying ${money$(s.amount)}/mo${s.billing_interval && s.billing_interval !== "monthly" ? ` (${esc(s.billing_interval)})` : ""}. Copy this into the call:</p>
       <div class="scriptbox">${esc(negotiateScript(s))}</div>
       <button class="go" id="negCopy" style="height:48px">Copy script</button>
       <p class="fine" style="margin-top:8px">Bill negotiators charge 25–60% of what they save you. This script is free — the savings are all yours.</p>`);
    const c = $("negCopy");
    if (c) c.onclick = () => {
      const txt = negotiateScript(s);
      if (navigator.clipboard) navigator.clipboard.writeText(txt).then(() => toast("Script copied.")).catch(() => toast("Copy failed — long-press the text."));
      else toast("Long-press the text to copy.");
    };
  }

  function feeWaiverScript(f) {
    return `Call the number on the back of your debit card. Say exactly this:\n\n"Hi, I see a ${money$(Math.abs(f.amount))} ${f.merchant_raw} fee on ${f.posted_at}. This is my first time — can you waive it as a courtesy?"\n\nIf they hesitate:\n\n"I've been a customer in good standing. I'd really appreciate a one-time courtesy waiver."\n\nIf they still say no, ask for a supervisor — supervisors can waive what reps can't.\n\nAfter the call: set up a low-balance alert in your banking app so it doesn't happen again.`;
  }

  function openFeeSheet(f) {
    openBudgetSheet(`Waive the ${money$(Math.abs(f.amount))} fee`,
      `<p class="psub">${esc(f.merchant_raw)} · ${esc(f.posted_at)}. First-time fees are waived more often than not:</p>
       <div class="scriptbox">${esc(feeWaiverScript(f))}</div>
       <button class="go" id="feeCopy" style="height:48px">Copy script</button>`);
    const c = $("feeCopy");
    if (c) c.onclick = () => {
      const txt = feeWaiverScript(f);
      if (navigator.clipboard) navigator.clipboard.writeText(txt).then(() => toast("Script copied.")).catch(() => toast("Copy failed — long-press the text."));
      else toast("Long-press the text to copy.");
    };
  }

  // ---- Budget: pace chart, projections, savings rate, age of money ----
  function paceChartSVG(transactions, ym) {
    const days = new Date(+ym.slice(0, 4), +ym.slice(5, 7), 0).getDate();
    const isCur = ym === new Date().toISOString().slice(0, 7);
    const elapsed = isCur ? Math.min(new Date().getDate(), days) : days;
    const daily = new Array(days + 1).fill(0);
    (transactions || []).filter(t => t && t.amount < 0 && !t.is_pending && !t.is_transfer && String(t.posted_at || "").slice(0, 7) === ym)
      .forEach(t => { const d = Math.min(days, Math.max(1, +String(t.posted_at).slice(8, 10) || 1)); daily[d] += Math.abs(t.amount); });
    const cum = []; let run = 0;
    for (let d = 1; d <= days; d++) { run += daily[d]; cum[d] = run; }
    const spent = cum[elapsed] || 0;
    const proj = elapsed > 0 ? spent / elapsed * days : spent;
    const maxV = Math.max(proj, spent, 1) * 1.08;
    const W = 340, H = 110, P = 8;
    const X = d => P + (d - 1) / (days - 1) * (W - 2 * P);
    const Y = v => H - P - (v / maxV) * (H - 2 * P);
    const line = pts => pts.map((p, i) => `${i ? "L" : "M"}${X(p[0]).toFixed(1)},${Y(p[1]).toFixed(1)}`).join(" ");
    const actual = []; for (let d = 1; d <= elapsed; d++) actual.push([d, cum[d]]);
    const ideal = [[1, proj / days], [days, proj]];
    const todayX = X(Math.max(1, elapsed)).toFixed(1);
    return `<div class="pacewrap" role="img" aria-label="Spending pace: ${bm0(spent)} spent so far, on pace for ${bm0(proj)}">
      <svg viewBox="0 0 ${W} ${H}" preserveAspectRatio="none">
        <line x1="${todayX}" y1="${P}" x2="${todayX}" y2="${H - P}" stroke="var(--muted)" stroke-width="1" stroke-dasharray="2,3"/>
        <path d="${line(ideal)}" fill="none" stroke="var(--muted)" stroke-width="1.5" stroke-dasharray="4,3"/>
        <path d="${line(actual.length ? actual : [[1, 0]])}" fill="none" stroke="var(--ink)" stroke-width="2.5"/>
      </svg>
      <div class="pacelegend"><span><i></i>your spending</span><span><i class="dotted"></i>ideal pace → ${bm0(proj)}</span></div>
    </div>`;
  }

  function catProjection(spent, ym) {
    const days = new Date(+ym.slice(0, 4), +ym.slice(5, 7), 0).getDate();
    const isCur = ym === new Date().toISOString().slice(0, 7);
    const elapsed = isCur ? Math.max(1, Math.min(new Date().getDate(), days)) : days;
    return spent / elapsed * days;
  }

  function savingsRate(model) {
    if (!model || !model.agg || !(model.agg.in > 0)) return null;
    return Math.round(model.agg.kept / model.agg.in * 100);
  }

  // Age of Money (YNAB-style): average days a dollar sits between arriving
  // and being spent. Weighted by outflow amount. Labeled as an estimate.
  function ageOfMoney(txs) {
    const flows = (txs || []).filter(t => t && !t.is_pending && !t.is_transfer && t.posted_at)
      .sort((a, b) => String(a.posted_at).localeCompare(String(b.posted_at)));
    let lastIn = null, wDays = 0, wSum = 0;
    flows.forEach(t => {
      const d = new Date(String(t.posted_at).slice(0, 10) + "T12:00:00");
      if (t.amount > 0) lastIn = d;
      else if (lastIn && d >= lastIn) {
        const days = Math.round((d - lastIn) / 864e5);
        wDays += days * Math.abs(t.amount); wSum += Math.abs(t.amount);
      }
    });
    return wSum > 0 ? Math.round(wDays / wSum) : null;
  }

  // ---- Recurring calendar: bills + payday on one grid ----
  function projectDates(rec, year, month) {
    // Returns day-of-month numbers in (year, month) this recurrence bills.
    const out = [];
    try {
      const iv = rec.interval;
      const step = iv === "weekly" ? 7 : iv === "biweekly" ? 14 : iv === "quarterly" ? null : iv === "yearly" ? null : 30;
      let base = null;
      if (rec.next_date) base = new Date(rec.next_date + "T12:00:00");
      else if (rec.last_date) base = new Date(rec.last_date + "T12:00:00");
      if (!base || isNaN(base)) return out;
      if (iv === "monthly" || step === 30) {
        const dom = base.getDate();
        const dim = new Date(year, month + 1, 0).getDate();
        out.push(Math.min(dom, dim));
      } else if (iv === "yearly") {
        if (base.getMonth() === month) out.push(Math.min(base.getDate(), new Date(year, month + 1, 0).getDate()));
      } else if (iv === "quarterly") {
        if ((month - base.getMonth()) % 3 === 0 && new Date(year, month, 1) >= new Date(base.getFullYear(), base.getMonth(), 1))
          out.push(Math.min(base.getDate(), new Date(year, month + 1, 0).getDate()));
      } else if (step) {
        // walk weekly/biweekly from base
        const first = new Date(year, month, 1), last = new Date(year, month + 1, 0);
        let d = new Date(base);
        while (d < first) d.setDate(d.getDate() + step);
        while (d <= last) { out.push(d.getDate()); d.setDate(d.getDate() + step); }
      }
    } catch (e) {}
    return out;
  }

  function detectPaydays(txs) {
    // Regular large inflows: group by merchant, need ≥2 with a stable gap.
    const byM = {};
    (txs || []).filter(t => t && t.amount > 0 && !t.is_pending && !t.is_transfer)
      .forEach(t => { const mid = t.merchant_id || normalizeMerchant(t.merchant_raw || ""); (byM[mid] = byM[mid] || []).push(t); });
    const out = [];
    Object.values(byM).forEach(ts => {
      if (ts.length < 2) return;
      const ds = ts.map(t => String(t.posted_at).slice(0, 10)).sort();
      const gaps = [];
      for (let i = 1; i < ds.length; i++) gaps.push(Math.round((new Date(ds[i]) - new Date(ds[i - 1])) / 864e5));
      const avg = gaps.reduce((a, b) => a + b, 0) / gaps.length;
      const stable = gaps.every(g => Math.abs(g - avg) <= 3);
      const big = ts.every(t => t.amount >= 200);
      if (stable && big && (avg >= 6 && avg <= 32)) {
        out.push({ merchant: ts[0].merchant_raw, amount: Math.round(ts.reduce((s, t) => s + t.amount, 0) / ts.length), gap: Math.round(avg), last: ds[ds.length - 1] });
      }
    });
    return out.sort((a, b) => b.amount - a.amount).slice(0, 2);
  }

  let recCalMonth = null; // YYYY-MM; null = current
  function renderRecCal() {
    const body = $("reccalBody"); if (!body) return;
    const { transactions } = loadTrackData();
    const now = new Date();
    if (!recCalMonth) recCalMonth = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;
    const [Y, M1] = recCalMonth.split("-").map(Number); const M = M1 - 1;
    let recs = [];
    try { recs = (detectRecurrence(transactions || []) || []).filter(r => !r.dormant); } catch (e) {}
    const paydays = detectPaydays(transactions || []);
    // Map day -> bills
    const bills = {};
    recs.forEach(r => projectDates(r, Y, M).forEach(d => {
      (bills[d] = bills[d] || []).push({ name: r.merchant_raw, amount: Math.abs(r.amount) });
    }));
    const payDays = {};
    paydays.forEach(p => {
      const last = new Date(p.last + "T12:00:00");
      const first = new Date(Y, M, 1), lastD = new Date(Y, M + 1, 0);
      let d = new Date(last);
      while (d < first) d.setDate(d.getDate() + p.gap);
      const seen = new Set();
      while (d <= lastD) { if (!seen.has(d.getDate())) { (payDays[d.getDate()] = payDays[d.getDate()] || []).push(p); seen.add(d.getDate()); } d.setDate(d.getDate() + p.gap); }
    });
    const dim = new Date(Y, M + 1, 0).getDate();
    const lead = new Date(Y, M, 1).getDay();
    const todayStr = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(now.getDate()).padStart(2, "0")}`;
    let cells = "";
    ["S", "M", "T", "W", "T", "F", "S"].forEach(d => cells += `<div class="dow">${d}</div>`);
    for (let i = 0; i < lead; i++) cells += `<div class="day" style="visibility:hidden"></div>`;
    let monthBills = 0;
    for (let d = 1; d <= dim; d++) {
      const ds = `${Y}-${String(M1).padStart(2, "0")}-${String(d).padStart(2, "0")}`;
      const isToday = ds === todayStr;
      let inner = `<span class="dn">${d}</span>`;
      (payDays[d] || []).forEach(p => { inner += `<span class="pay">Payday +${bm0(p.amount)}</span>`; });
      (bills[d] || []).forEach(b => { monthBills += b.amount; inner += `<span class="bill unpaid">${esc(b.name)} ${bm0(b.amount)}</span>`; });
      cells += `<div class="day${isToday ? " today" : ""}">${inner}</div>`;
    }
    const prevM = new Date(Y, M - 1, 1), nextM = new Date(Y, M + 1, 1);
    const fmtM = dt => `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, "0")}`;
    body.innerHTML = `
      <p class="psub">Every bill and every payday, on one grid. Tap a bill's merchant in the list to track it.</p>
      <div class="bmonthnav">
        <button id="rcPrev" aria-label="Previous month">‹</button>
        <b>${monthName(recCalMonth)}</b>
        <button id="rcNext" aria-label="Next month">›</button>
      </div>
      <div class="calgrid">${cells}</div>
      <div class="pcard" style="margin-top:12px"><p class="bsum" style="font-size:14px">${bm0(Math.round(monthBills))} in bills this month${paydays.length ? ` · payday${paydays.length > 1 ? "s" : ""} detected: ${paydays.map(p => esc(p.merchant)).join(", ")}` : ""}.</p></div>
      ${recs.length ? `<h2 class="sec">Bills on autopilot (${recs.length})</h2><div class="bcard">` +
        recs.slice(0, 10).map(r => `<div class="mrow"><div><b>${esc(r.merchant_raw)}</b><i>${esc(r.interval)}${r.next_date ? " · next " + esc(r.next_date) : ""}</i></div><span>${bm0(Math.abs(r.amount))}</span></div>`).join("") + `</div>` : ""}`;
    $("rcPrev").onclick = () => { recCalMonth = fmtM(prevM); renderRecCal(); };
    $("rcNext").onclick = () => { recCalMonth = fmtM(nextM); renderRecCal(); };
  }
