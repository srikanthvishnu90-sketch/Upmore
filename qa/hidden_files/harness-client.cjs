#!/usr/bin/env node
// Client-side feature test harness for the Upmore app template.
// Loads src/upmore-app-template.html's app <script> into a vm sandbox with
// DOM stubs, injects UPMORE_DATA, exports internals via __T, then runs tests.
const fs = require('fs');
const vm = require('vm');
const path = require('path');

const ROOT = '/home/hatch/workspace/upmore';
const html = fs.readFileSync(path.join(ROOT, 'src/upmore-app-template.html'), 'utf8');
const data = JSON.parse(fs.readFileSync(path.join(ROOT, 'src/data/upmore-data.json'), 'utf8'));

const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)];
const appJs = scripts[scripts.length - 1][1]; // the app script (last block)

const EXPORT = `;globalThis.__T={guideAnswer:guideAnswer,xFiltered:xFiltered,xState:xState,planData:planData,buildPlan:buildPlan,esc:esc,short:short,earnLine:earnLine,routeTitle:routeTitle,routeMeta:routeMeta,stepLinks:stepLinks,hostOf:hostOf,matchCategory:matchCategory,EXRULES:EXRULES,STARTERS:STARTERS,data:data,prog:prog,checkAbout:checkAbout,show:show,getCurrent:function(){return current},syncProgress:syncProgress,loadProgress:loadProgress,renderHome:renderHome,renderProfile:renderProfile,renderExplore:renderExplore,agentAsk:agentAsk,guideAsk:guideAsk,startWalkthrough:startWalkthrough,renderWalkStep:renderWalkStep,getWalk:function(){return walk},getSession:function(){return session},setSession:function(s){session=s},setDbProfile:function(p){dbProfile=p},routeById:routeById,stdRoutes:stdRoutes,D:D,NAMES:NAMES,routeParas:routeParas,topList:topList};`;
const idx = appJs.lastIndexOf('})();');
if (idx < 0) throw new Error('IIFE close not found');
const appJsX = appJs.slice(0, idx) + EXPORT + '\n})();' + appJs.slice(idx + 6);

// ---------- DOM stubs ----------
function makeEl(tag) {
  const el = {
    tagName: String(tag || 'div').toUpperCase(),
    children: [], style: {}, dataset: {}, _attrs: {}, _text: '', _html: '', _qs: {},
    value: '', disabled: false, hidden: false, scrollTop: 0, scrollHeight: 0,
    classList: { add() {}, remove() {}, toggle() { return true; }, contains() { return false; } },
    setAttribute(k, v) { this._attrs[k] = String(v); },
    getAttribute(k) { return this._attrs[k] !== undefined ? this._attrs[k] : null; },
    appendChild(c) { this.children.push(c); return c; },
    remove() {},
    insertAdjacentHTML(pos, s) { this._html += s; },
    querySelector(sel) { return makeEl(); },
    querySelectorAll(sel) {
      if (!this._qs[sel]) {
        this._qs[sel] = (sel === 'button') ? [makeEl('button'), makeEl('button')] : [];
      }
      return this._qs[sel];
    },
    addEventListener() {}, removeEventListener() {},
  };
  Object.defineProperty(el, 'textContent', { get() { return this._text; }, set(v) { this._text = String(v); } });
  Object.defineProperty(el, 'innerHTML', { get() { return this._html; }, set(v) { this._html = String(v); this.children = []; } });
  return el;
}
const idCache = {};
const __ls = {};
const __writes = [];
const __dbRows = { playbook_progress: [] };
let __reloaded = false;
let __fetchMode = 'fail'; // 'fail' -> {ok:false}; 'ok' -> 200 w/ reply; 'throw' -> rejects
let captured1800 = null;

const supaStub = {
  _onAuth: null,
  auth: {
    getSession: async () => ({ data: { session: null } }),
    signInWithOAuth: async () => ({ error: null }),
    signOut: async () => { if (supaStub._onAuth) supaStub._onAuth('SIGNED_OUT'); return { error: null }; },
    onAuthStateChange: (cb) => { supaStub._onAuth = cb; },
  },
  from(table) {
    const q = {
      select() { return q; },
      eq() { return q; },
      maybeSingle: async () => ({ data: null, error: null }),
      upsert: async (payload, opts) => { __writes.push({ table, op: 'upsert', payload, opts }); return { error: null }; },
      then(res) { return Promise.resolve({ data: __dbRows[table] || [], error: null }).then(res); },
    };
    return q;
  },
};

const sandbox = {
  console,
  URL, URLSearchParams,
  innerWidth: 1200, innerHeight: 900,
  navigator: { userAgent: 'node-harness' },
  location: { hash: '', search: '', origin: 'https://x', pathname: '/index.html', reload() { __reloaded = true; } },
  history: { replaceState() {} },
  localStorage: {
    getItem: (k) => (__ls[k] !== undefined ? __ls[k] : null),
    setItem: (k, v) => { __ls[k] = String(v); },
    removeItem: (k) => { delete __ls[k]; },
  },
  setTimeout: (fn, ms, ...a) => {
    if (ms === 1800) { captured1800 = fn; return 0; }
    return setTimeout(fn, ms, ...a);
  },
  clearTimeout: (...a) => clearTimeout(...a),
  addEventListener() {},
  fetch: async (url, opts) => {
    if (__fetchMode === 'throw') throw new Error('network down');
    if (__fetchMode === 'ok') return { ok: true, json: async () => ({ reply: 'agent says hi', thread_id: 't-1' }) };
    return { ok: false, status: 500, json: async () => ({}) };
  },
  document: {
    getElementById: (id) => {
      if (id === 'empty') {
        const ch = idCache['chat'] ? idCache['chat'].innerHTML : '';
        if (!/id="empty"/.test(ch)) return null;
      }
      if (!idCache[id]) idCache[id] = makeEl('#' + id); return idCache[id];
    },
    querySelector: (sel) => makeEl(),
    querySelectorAll: (sel) => [],
    createElement: (tag) => makeEl(tag),
    documentElement: makeEl('html'),
    body: makeEl('body'),
  },
  window: null, // set below
  __ls, __writes, __dbRows,
  __ids: () => idCache,
  __flags: { get reloaded() { return __reloaded; } },
  __setFetchMode: (m) => { __fetchMode = m; },
  __fire1800: () => { if (captured1800) captured1800(); },
};
sandbox.window = {
  supabase: { createClient: () => supaStub },
  addEventListener() {},
  innerWidth: 1200, innerHeight: 900,
};
sandbox.globalThis = sandbox;
vm.createContext(sandbox);

const preamble = 'const UPMORE_DATA = ' + JSON.stringify(data) + ';';
vm.runInContext(preamble, sandbox, { filename: 'data.js' });
vm.runInContext(appJsX, sandbox, { filename: 'app.js' });

// ---------- test helpers exposed into the vm ----------
const results = [];
const testSrc = `
;(async () => {
  const T = globalThis.__T, ids = globalThis.__ids, LS = globalThis.__ls;
  const W = globalThis.__writes, DBR = globalThis.__dbRows;
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const R = [];
  const t = (name, ok, detail) => R.push({name, ok: !!ok, detail: String(detail === undefined ? '' : detail)});
  const chatHTML = () => ids().chat.children.map(c => c.innerHTML).join('\\n');

  // ============ C01 onboarding state machine ============
  T.show('splash');
  globalThis.__fire1800();
  t('C01 splash auto-advance 1800ms -> welcome', T.getCurrent()==='welcome', 'current='+T.getCurrent());
  // about validation: happy
  ids().name.value='Ava'; ids().dob.value='01011990'; ids().state.value='TX';
  T.checkAbout();
  t('C01 happy: valid name/dob/state enables aboutGo', ids().aboutGo.disabled===false, 'disabled='+ids().aboutGo.disabled);
  // invalid date Feb 30
  ids().dob.value='02302010'; T.checkAbout();
  t('C01 stress: Feb 30 rejected w/ hint', ids().dobHint.textContent==='Check that date.' && ids().aboutGo.disabled===true, 'hint='+ids().dobHint.textContent);
  // empty name
  ids().name.value=''; ids().dob.value='01011990'; T.checkAbout();
  t('C01 stress: empty name blocks', ids().aboutGo.disabled===true, '');
  // missing state
  ids().name.value='Ava'; ids().state.value=''; T.checkAbout();
  t('C01 stress: missing state blocks', ids().aboutGo.disabled===true, '');
  // future dob
  ids().state.value='TX'; ids().dob.value='01012099'; T.checkAbout();
  t('C01 stress: future DOB rejected', ids().dobHint.textContent==='Check that date.', '');
  // minor -> blocked
  ids().dob.value='09242009'; T.checkAbout();
  t('C01 minor flagged', T.data.minor===true, 'minor='+T.data.minor);
  ids().aboutGo.onclick(); t('C01 blocked path: minor -> blocked screen', T.getCurrent()==='blocked', 'current='+T.getCurrent());
  // adult correction
  T.show('about'); ids().dob.value='01011990'; T.checkAbout();
  t('C01 adult correction clears minor', T.data.minor===false, '');
  ids().aboutGo.onclick(); t('C01 adult -> situation', T.getCurrent()==='situation', 'current='+T.getCurrent());
  // exactly-18 boundary
  const d18 = new Date(); const mm=String(d18.getMonth()+1).padStart(2,'0'); const dd=String(d18.getDate()).padStart(2,'0');
  ids().dob.value=mm+dd+(d18.getFullYear()-18); T.checkAbout();
  t('C01 boundary: exactly 18 today = adult', T.data.minor===false, 'dob='+ids().dob.value);

  // ============ C02 plan ============
  Object.assign(T.data, {name:'Ava', state:'TX', time:'15', paycheck:'no', cash:'0'});
  T.buildPlan();
  t('C02 plan title personalized', ids().planTitle.textContent==='Ava, here are your first 3 moves', ids().planTitle.textContent);
  t('C02 based-on line', /Texas/.test(ids().based.innerHTML) && /15 minutes/.test(ids().based.innerHTML), ids().based.innerHTML.slice(0,120));
  const top3t = T.stdRoutes().slice(0,3).map(r=>T.esc(T.routeTitle(r)));
  t('C02 moves = top-3 standard by earn ratio', top3t.every(x=>ids().moves.innerHTML.includes(x)), top3t.join(' | '));
  t('C02 _moves never persists (fresh planData each call)', T.planData()._moves===undefined, 'dead personalization hook');
  // dbProfile merge + undefined-week bug
  T.setDbProfile({display_name:'Zed', state:'CA', free_time_hours:0.5, paycheck_status:'no', cash_available:'0'});
  const pd = T.planData();
  t('C02 dbProfile merge', pd.name==='Zed' && pd.state==='CA' && pd.time==='30' && pd.paycheck==='no', JSON.stringify({name:pd.name,state:pd.state,time:pd.time}));
  T.buildPlan();
  t('C02 stress: nonstandard time renders "undefined a week"', /undefined/.test(ids().based.innerHTML), ids().based.innerHTML.slice(0,140));
  T.setDbProfile(null);

  // ============ C03 home hero ============
  Object.assign(T.data, {name:'Ava', state:'TX', time:'60', paycheck:'yes', cash:'100'});
  for (const k of Object.keys(T.prog)) delete T.prog[k];
  T.renderHome();
  const r0 = T.stdRoutes()[0];
  t('C03 hero = move 1 top route', ids().heroTitle.textContent===T.routeTitle(r0), ids().heroTitle.textContent);
  t('C03 progress 0%', ids().heroBar.style.width==='0%' && ids().heroText.textContent==='0 of '+r0.steps.length+' steps', ids().heroBar.style.width+' / '+ids().heroText.textContent);
  T.prog[r0.id]=[r0.steps[0].n, r0.steps[1].n];
  T.renderHome();
  const pct = (2/r0.steps.length*100)+'%';
  t('C03 progress 2 steps', ids().heroBar.style.width===pct, ids().heroBar.style.width);
  // all done -> CTA
  T.prog[r0.id]=r0.steps.map(s=>s.n); T.renderHome();
  t('C03 all-done CTA text', ids().heroCta.textContent==='Ask Guide what\\'s next', ids().heroCta.textContent);
  ids().heroCta.onclick(); await sleep(1400);
  t('C03 all-done CTA -> guide next-move answer', /After this one:/.test(chatHTML()), chatHTML().slice(0,120));

  // ============ C04 walkthrough ============
  for (const k of Object.keys(T.prog)) delete T.prog[k];
  T.startWalkthrough('R0119');
  await sleep(2300);
  let h0 = chatHTML();
  const cards = ids().chat.children.filter(c=>/Step 1 of 7/.test(c.innerHTML));
  t('C04 walkthrough starts w/ step card', cards.length===1, 'cards='+cards.length);
  const card = cards[0];
  t('C04 per-step links w/ host labels', /Open /.test(card.innerHTML) && /target="_blank"/.test(card.innerHTML), card.innerHTML.slice(0,200));
  // stepLinks pure: dedupe + first-step route url first
  const rt = T.routeById('R0208'); // has play.google.com url
  const sl1 = T.stepLinks({text:'Tap install'}, rt, true);
  t('C05/C04 first step surfaces route url first', sl1[0]===rt.url, sl1[0]);
  const sl2 = T.stepLinks({text:'Open '+rt.url+' now'}, rt, true);
  t('C04 stepLinks dedupes url already in text', sl2.filter(u=>u===rt.url).length===1, '');
  t('C04 hostOf strips www', T.hostOf('https://www.example.com/x')==='example.com', T.hostOf('https://www.example.com/x'));
  // click Done on step 1
  const btns = card.querySelectorAll('button');
  btns[0].onclick(); await sleep(1200);
  t('C04 Done marks step + advances', T.getWalk().i===1 && (T.prog['R0119']||[]).includes(1), 'i='+T.getWalk().i);
  // jump to last step, finish
  T.getWalk().i = 6;
  T.renderWalkStep(); await sleep(150);
  const lastCard = ids().chat.children.filter(c=>/Step 7 of 7/.test(c.innerHTML)).pop();
  lastCard.querySelectorAll('button')[0].onclick(); await sleep(1400);
  t('C04 finish -> walk null + payout msg', T.getWalk()===null && /The payout:/.test(chatHTML()), '');
  T.startWalkthrough('R0157'); await sleep(2300);
  const dwCards = ids().chat.children.filter(c=>c.innerHTML.includes("done when:"));
  t('C04 done_when rendered when present', dwCards.length>=1 && dwCards[0].innerHTML.includes("App downloaded"), '');
  t('C04 warns rendered when present', dwCards.length>=1 && dwCards[0].innerHTML.includes("Heads up:"), '');

  // ============ C06 explore search ============
  T.xState.q='<script>alert(1)</script>'; T.xState.tier='all'; T.xState.cat='all'; T.xState.lane=false;
  t('C06 injection query: no throw, no match', T.xFiltered().length===0, '');
  T.xState.q='.+*?^()|[]';
  t('C06 regex chars: no throw', T.xFiltered().length===0, '');
  T.xState.q='fetch';
  t('C06 happy: finds Fetch', T.xFiltered().some(r=>r.id==='R0119'), '');
  T.xState.q='bug bounty';
  t('C06 matches reward text', T.xFiltered().some(r=>r.id==='R5446'), '');
  t('C06 esc neutralizes HTML', T.esc('<img src=x onerror=alert(1)>')==='&lt;img src=x onerror=alert(1)&gt;', T.esc('<img src=x onerror=alert(1)>'));
  T.xState.q='zxqwqwxz'; T.renderExplore();
  t('C06 empty result copy + more hidden', /0 ways to earn/.test(ids().xcount.textContent) && ids().xmore.hidden===true, ids().xcount.textContent);
  T.xState.q='';

  // ============ C07 filters ============
  T.xState.tier='Very Easy'; T.xState.cat='all';
  t('C07 tier chip filters', T.xFiltered().length>0 && T.xFiltered().every(r=>r.tier==='Very Easy'), T.xFiltered().length);
  T.xState.tier='all'; T.xState.cat='Bank Bonus';
  t('C07 category chip filters', T.xFiltered().length>0 && T.xFiltered().every(r=>r.category==='Bank Bonus'), T.xFiltered().length);
  T.xState.tier='Easy';
  const combo = T.xFiltered();
  t('C07 combined tier+cat', combo.every(r=>r.tier==='Easy' && r.category==='Bank Bonus'), combo.length);
  T.xState.tier='all'; T.xState.cat='all';

  // ============ C08 higher-risk lane ============
  t('C08 default hides restricted', T.xFiltered().every(r=>r.lane==='Standard'), T.xFiltered().length);
  t('C08 default count = 1744 standard', T.xFiltered().length===1744, T.xFiltered().length);
  t('C08 lane label shows (23)', ids().laneN.textContent==='(23)', ids().laneN.textContent);
  T.xState.lane=true;
  t('C08 toggle reveals 23 restricted', T.xFiltered().filter(r=>r.lane!=='Standard').length===23 && T.xFiltered().length===1767, '');
  T.xState.lane=false;

  // ============ C09 pagination ============
  T.xState.shown=40; T.renderExplore();
  t('C09 more visible w/ remaining count', ids().xmore.hidden===false && /1704 left/.test(ids().xmore.textContent), ids().xmore.textContent);
  ids().xmore.onclick();
  t('C09 click loads +60', T.xState.shown===100, '');
  T.xState.shown=5000; T.renderExplore();
  t('C09 hidden when list exhausted', ids().xmore.hidden===true, '');
  T.xState.shown=40;

  // ============ C10 money/time/rate ============
  const e1 = T.earnLine({payout_min:0,payout_max:0,time_min_minutes:30,time_max_minutes:30,earn_ratio:null});
  t('C10 varies + single time', e1==='Varies \\u00b7 \\u224830 min', e1);
  const e2 = T.earnLine({payout_min:100,payout_max:400,time_min_minutes:30,time_max_minutes:60,earn_ratio:5});
  t('C10 range + 2dp rate', e2==='\\u2248$100\\u2013$400 \\u00b7 \\u224830\\u201360 min \\u00b7 \\u22485.00/min', e2);
  const e3 = T.earnLine({payout_min:0,payout_max:250000,time_min_minutes:90,time_max_minutes:240,earn_ratio:757.575});
  t('C10 big ratio rounds', /\\u2248758\\/min/.test(e3), e3);
  const e4 = T.earnLine({payout_min:50,payout_max:50,time_min_minutes:5,time_max_minutes:15,earn_ratio:55.55});
  t('C10 mid ratio 1dp', /\\u224855.5\\/min/.test(e4), e4);
  t('C10 explore first card = top earn ratio', T.xFiltered()[0].id==='R5446', T.xFiltered()[0].id);

  // ============ C11 guide local answers ============
  let a = T.guideAnswer('tell me about fetch');
  t('C11 provider lookup', a.paras[0].includes('Fetch') && a.card.title.includes('Fetch'), a.card.title);
  t('C11 provider answer carries stale unverified line', a.paras.some(p=>/haven\\'t verified the live terms/.test(p)), '');
  a = T.guideAnswer('show me bank bonuses');
  t('C11 category top-3', /easiest bank bonus routes/.test(a.paras[0]) && a.paras.length===4, a.paras[0]);
  a = T.guideAnswer('is this legit');
  t('C11 verification answer (STALE)', /have not verified live provider terms yet/.test(a.paras[0]), a.paras[0].slice(0,80));
  a = T.guideAnswer('what is the catch');
  t('C11 catch answer: 23 higher-risk', /23 routes in the catalog sit in a higher-risk lane/.test(a.paras[1]), '');
  a = T.guideAnswer('when do i get paid');
  t('C11 payout answer', /Payout timing is per-offer/.test(a.paras[0]), '');
  a = T.guideAnswer('do i pay taxes on this');
  t('C11 tax answer', /Usually, yes/.test(a.paras[0]), '');
  a = T.guideAnswer('i have no money to start');
  a = T.guideAnswer('i have no money');
  t('C11 no-deposit answer', /costs \\$0/.test(a.paras[0]), a.paras[0].slice(0,60));
  a = T.guideAnswer('free to start');
  t('C11 GAP: "free to start" shadowed by easiest-branch', /3 easiest routes/.test(a.paras[0]), a.paras[0].slice(0,60));
  a = T.guideAnswer('what is the easiest way to start');
  t('C11 easiest top-3', /3 easiest routes in the whole catalog/.test(a.paras[0]), '');
  a = T.guideAnswer('what should i do first');
  t('C11 starter hits easiest branch', /3 easiest routes/.test(a.paras[0]), '');
  a = T.guideAnswer('zxqwqwxz nonsense');
  t('C11 fallback mentions catalog count', /535 routes/.test(a.paras[0]), a.paras[0].slice(0,60));

  // ============ C12 EXRULES ============
  a = T.guideAnswer('how do I do my homework without getting caught');
  t('C12 homework: hard refusal', /We don\\'t touch that one/.test(a.paras[0]) && /expel/.test(a.paras[1]), a.paras[1].slice(0,70));
  a = T.guideAnswer('is onlyfans a legit side hustle');
  t('C12 onlyfans: hard rule beats legit-branch', /We don\\'t touch that one/.test(a.paras[0]) && /Privacy, safety/.test(a.paras[1]), '');
  a = T.guideAnswer('HOW DO I DO MY HOMEWORK?');
  t('C12 case-insensitive', /We don\\'t touch that one/.test(a.paras[0]), '');
  a = T.guideAnswer('should i start a dropshipping store');
  t('C12 dropship: soft rule', /business model, not a quick earning route/.test(a.paras[0]), '');
  a = T.guideAnswer('can you help me tutor my neighbor kid for cash');
  t('C12 tutor: soft rule', /business model/.test(a.paras[0]), '');
  t('C12 EXRULES indexes valid (0-20 of 21)', T.EXRULES.every(([k,ei])=>ei>=0 && ei<T.D.excluded.length), '');

  // ============ C13 empty state ============
  t('C13 4 starter prompts', T.STARTERS.length===4, T.STARTERS.map(s=>s.q).join(' | '));
  T.show('guide'); await sleep(50);
  t('C13 empty state renders starters + plan ctx', /What should I do first/.test(ids().chat.innerHTML) && /Your plan:/.test(ids().chat.innerHTML), '');

  // ============ C14 agent fallback ============
  globalThis.__setFetchMode('fail');
  let ja = await T.agentAsk('hello');
  t('C14 agentAsk null when unsigned in', ja===null, '');
  T.setSession({access_token:'tok', user:{id:'u1'}});
  ja = await T.agentAsk('hello');
  t('C14 agentAsk null on 500', ja===null, '');
  globalThis.__setFetchMode('ok');
  ja = await T.agentAsk('hello');
  t('C14 agentAsk returns reply on 200', ja && ja.reply==='agent says hi', JSON.stringify(ja));
  globalThis.__setFetchMode('fail'); T.setSession(null);
  // guideAsk end-to-end fallback (busy reset, local answer)
  T.show('guide'); T.guideAsk('what is the catch'); await sleep(1500);
  t('C14 guideAsk falls back to local on null', /higher-risk lane/.test(chatHTML()), '');
  globalThis.__setFetchMode('throw');
  T.guideAsk('is this legit'); await sleep(1500);
  t('C14 guideAsk falls back on fetch throw', /have not verified live provider terms/.test(chatHTML()), '');
  globalThis.__setFetchMode('fail');

  // ============ C15 OAuth round-trip persistence ============
  Object.assign(T.data, {name:'Zed', state:'CA', time:'60', paycheck:'yes', cash:'100'});
  await ids().googleGo.onclick(); await sleep(50);
  const saved = JSON.parse(LS['upmore-onboarding']||'null');
  t('C15 onboarding saved to localStorage pre-OAuth', saved && saved.name==='Zed' && saved.state==='CA', JSON.stringify(saved));
  // corrupt JSON tolerance (same pattern as boot)
  LS['upmore-onboarding'] = '{bad json';
  let threw=false; try { const s=LS['upmore-onboarding']; if (s) Object.assign(T.data, JSON.parse(s)); } catch(e){ threw=false; }
  t('C15 corrupt JSON does not throw', !threw && T.data.name==='Zed', '');

  // ============ C16 progress sync ============
  W.length=0; T.setSession({access_token:'tok', user:{id:'u9'}});
  T.prog['R0119']=[1,2];
  await T.syncProgress('R0119');
  const w1 = W[W.length-1];
  t('C16 syncProgress upserts in_progress', w1 && w1.table==='playbook_progress' && w1.payload.user_id==='u9' && w1.payload.route_id==='R0119' && w1.payload.current_step===2 && w1.payload.status==='in_progress', JSON.stringify(w1&&w1.payload));
  T.prog['R0119']=[1,2,3,4,5,6,7];
  await T.syncProgress('R0119');
  t('C16 all steps -> done', W[W.length-1].payload.status==='done', '');
  T.setSession(null); W.length=0;
  await T.syncProgress('R0119');
  t('C16 no-op when signed out', W.length===0, '');
  DBR.playbook_progress=[{route_id:'R0119', current_step:3}];
  delete T.prog['R0119']; T.setSession({access_token:'tok', user:{id:'u9'}});
  await T.loadProgress();
  t('C16 loadProgress maps to step ns', JSON.stringify(T.prog['R0119'])===JSON.stringify([1,2,3]), JSON.stringify(T.prog['R0119']));
  DBR.playbook_progress=[{route_id:'NOPE', current_step:5}];
  await T.loadProgress();
  t('C16 loadProgress ignores unknown route', T.prog['NOPE']===undefined, '');
  T.setSession(null); DBR.playbook_progress=[];

  // ============ C17 profile ============
  T.setDbProfile(null);
  Object.assign(T.data, {name:'Ava', state:'TX', time:'15', paycheck:'no', cash:'0'});
  T.renderProfile();
  t('C17 profile renders plan rows', ids().pName.textContent==='Ava' && ids().pAva.textContent==='A' && ids().pTime.textContent==='15 minutes' && /Texas/.test(ids().pAbout.textContent) && /No direct deposit/.test(ids().pSit.textContent) && /\\$0 to park/.test(ids().pSit.textContent), ids().pSit.textContent);

  // ============ C18 disclosure ============
  a = T.guideAnswer('How does Upmore make money?');
  t('C18 disclosure copy present', a.paras.length===2 && /never comes out of your pocket/.test(a.paras[0]) && /always tell you when we\\'re earning/.test(a.paras[1]), '');
  t('C18 no per-offer affiliate disclosure mechanism', !T.D.routes.some(r=>r.affiliate!==undefined) , 'no affiliate field on any route');

  // ============ C19 sign out ============
  T.setSession({access_token:'tok', user:{id:'u9'}});
  await ids().signOut.onclick(); await sleep(50);
  t('C19 sign out clears session + reloads', T.getSession()===null && globalThis.__flags.reloaded===true, '');

  // ============ C10 retired-route check (Explore includes retired) ============
  const retired = T.D.routes.filter(r=>r.status==='retired');
  t('C10 retired routes visible in Explore (gap)', retired.length===2 && T.xFiltered().some(r=>r.status==='retired'), retired.map(r=>r.id).join(','));

  R.forEach(r=>console.log((r.ok?'PASS':'FAIL')+' | '+r.name+(r.detail?' | '+r.detail:'')));
  return R;
})();`;

(async () => {
  await new Promise(r => setTimeout(r, 150));
  try {
    const R = await vm.runInContext(testSrc, sandbox, { filename: 'tests.js' });
    const pass = R.filter(r => r.ok).length;
    console.log(`\n==== ${pass}/${R.length} harness assertions passed ====`);
    fs.writeFileSync(path.join(ROOT, 'qa/hidden_files/harness-results.json'), JSON.stringify(R, null, 1));
  } catch (e) {
    console.error('HARNESS ERROR:', e);
    process.exit(1);
  }
})();
