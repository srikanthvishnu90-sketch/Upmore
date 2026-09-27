// No-guilt language: 62yo retiree on fixed income goes over on groceries/gifts.
module.exports = {
  id: "a024",
  lane: "budgeting",
  title: "Retiree who overspent asks what to do — no guilt language allowed",
  persona: {
    name: "Gloria S.",
    age: 62,
    state: "AZ",
    incomeMonthly: 2900,
    debts: [],
    employment: "retired (social security + pension)",
    goals: ["stay on budget without feeling bad"],
    tech: "low",
    bankConnected: true,
    dataTier: "full",
    notes: "speaks warmly and plainly; fixed income; sensitive to judgment",
  },
  modes: ["dry"],
  steps: [
    { kind: "guide", prompt: "I went over on groceries and gifts this month. What do I do now?",
      expect: [{ t: "contains", re: "adjust|plan|rollover|budget" },
               { t: "notContains", re: "wasted|bad habit|shame|guilty" }] },
    { kind: "guide", prompt: "Please don't lecture me about my spending. Just help me plan.",
      expect: [{ t: "notContains", re: "wasted|bad habit|shame|guilty|lecture" }] },
    { kind: "static", file: "template", op: "notContains", pattern: "bad habit",
      desc: "no shaming copy ships in the app template" },
  ],
};
