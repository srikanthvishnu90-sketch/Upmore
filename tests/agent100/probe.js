// Scratch probe for agent repairs: print real guide replies for candidate prompts.
// Usage: node probe.js <age> <prompt...>  (each prompt separated by " ;; ")
const { loadApp } = require("./harness/extract.js");
const args = process.argv.slice(2);
const age = parseInt(args[0], 10);
const prompts = args.slice(1).map((s) => s.trim()).filter(Boolean);
const app = loadApp();
app.setLS("upmore_dob_year", String(2026 - age));
app.setLS("agent100_persona", "probe");
for (const q of prompts) {
  const r = app.guide(q);
  console.log("Q:", q);
  console.log("A:", r.text.slice(0, 320).replace(/\n/g, " | "));
  console.log("---");
}
