// SPEC 09g tests: RMD arithmetic (IRS Uniform Lifetime Table).
const fs = require("fs");
eval(fs.readFileSync("/tmp/rmd-fns.js", "utf8"));
let pass = 0, fail = 0;
const t = (n, c, x) => { c ? pass++ : (fail++, console.log("FAIL:", n, x || "")); };
t("rmd 73", rmdFor(73, 265000) === 10000, rmdFor(73, 265000));
t("rmd 80", rmdFor(80, 202000) === 10000, rmdFor(80, 202000));
t("rmd under 73", rmdFor(72, 500000) === null);
t("rmd no balance", rmdFor(75, 0) === null);
t("rmd caps at 90", rmdFor(95, 122000) === 10000, rmdFor(95, 122000));
t("rmd table spot", RMD_TABLE[73] === 26.5 && RMD_TABLE[90] === 12.2);
console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
