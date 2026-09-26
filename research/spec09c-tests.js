// SPEC 09c tests: savings goal projection.
const store = {};
global.localStorage = { getItem: k => (k in store ? store[k] : null), setItem: (k, v) => { store[k] = String(v); }, removeItem: k => { delete store[k]; } };
function goalProject(g, avgKept) {
    const remaining = g.target - g.current;
    if (remaining <= 0) return { done: true, weeks: 0 };
    if (!(avgKept > 0)) return { done: false, weeks: Infinity };
    return { done: false, weeks: Math.ceil(remaining / avgKept * 4.33) };
  }
let pass = 0, fail = 0;
const t = (n, c, x) => { c ? pass++ : (fail++, console.log("FAIL:", n, x || "")); };
t("goal done", goalProject({ target: 1000, current: 1000 }, 100).done === true);
t("goal overfunded", goalProject({ target: 1000, current: 1200 }, 100).done === true);
t("goal weeks math", goalProject({ target: 1000, current: 0 }, 100).weeks === 44, goalProject({ target: 1000, current: 0 }, 100).weeks);
t("goal partial", goalProject({ target: 1000, current: 250 }, 100).weeks === 33, goalProject({ target: 1000, current: 250 }, 100).weeks);
t("goal no pace", goalProject({ target: 1000, current: 0 }, 0).weeks === Infinity);
t("goal negative pace", goalProject({ target: 1000, current: 0 }, -50).weeks === Infinity);
console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
