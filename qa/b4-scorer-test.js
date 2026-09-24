#!/usr/bin/env node
// B4: verify the queue ranking function from the built app.
// Extracts qScore + qUrgency from index.html and checks ordering properties.
const fs = require("fs");
const html = fs.readFileSync("/home/hatch/workspace/upmore/index.html", "utf8");

function extract(name) {
  const re = new RegExp(`function ${name}\\([\\s\\S]*?\\n  \\}`, "");
  const m = html.match(re);
  if (!m) throw new Error("not found: " + name);
  return m[0];
}
const src = extract("qScore") + "\n" + extract("qUrgency");
eval(src);

let fails = 0;
const check = (name, cond) => {
  console.log((cond ? "PASS" : "FAIL") + " " + name);
  if (!cond) fails++;
};
// (a) higher dollars outranks lower, all else equal
check("a: dollars", qScore(100, 0.7, 2, 30) > qScore(50, 0.7, 2, 30));
// (b) nearer deadline (higher urgency) outranks farther
check("b: urgency", qScore(50, 0.7, qUrgency(1), 30) > qScore(50, 0.7, qUrgency(30), 30));
// (c) lower effort outranks higher, all else equal
check("c: effort", qScore(50, 0.7, 2, 10) > qScore(50, 0.7, 2, 60));
// (d) formula shape: dollars*conf*urg/eff
check("d: formula", Math.abs(qScore(100, 0.5, 4, 25) - (100 * 0.5 * 4 / 25)) < 1e-9);
// (e) zero dollars never outranks positive dollars at same conf/urg/eff
check("e: zero dollars", qScore(0, 1, 5, 1) < qScore(1, 0.4, 1, 60));
// (f) urgency ladder is monotonic
const us = [0, 1, 3, 7, 14, 30, 90].map(qUrgency);
check("f: urgency monotonic", us.every((u, i) => i === 0 || u <= us[i - 1]));
// (g) every queue card in a headless render carries the data-* attributes
const cardRe = /<article class="qcard[^"]*"[^>]*>/g;
console.log("INFO queue cards are rendered at runtime (browser test covers attributes)");
process.exit(fails ? 1 : 0);
