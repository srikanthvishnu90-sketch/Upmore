# C5-v2 EXHAUSTIVE — Waste Score Ranking (Cancel, Doc 2)

**Agent:** C5-v2 | **Date:** 2026-09-25 | **Assertions:** 182 (175 PASS / 7 FAIL)
**Spec:** `waste_score = annual_cost × (1 − usage_signal) × renewal_urgency × confidence` (docspecs/02-cancel.md:58)
**Production tested:** https://upmore-srikanthvishnu90-sketchs-projects.vercel.app/
**Production build:** `sw.js` stamp `upmore-8b52c95` (commit `b73da4f`, served HTTP 200, 2026-09-25)
**Code under test:** `src/upmore-app-template.html` — `wasteScore()` (line ~3191), `renewalUrgency()` (line ~3194), cancel branch of `buildQueue()` (line ~1841), `cancelCard()` (line ~3293), global queue sort (line ~1956)

## Method

- Extracted `wasteScore` and `renewalUrgency` verbatim from the template source via regex and `eval`'d them in Node — every numeric assertion runs the real implementation, not a reimplementation.
- Simulated the full cancel pipeline on 8 synthetic subscriptions: coded annual multiplier → `renewalUrgency(days)` → `wasteScore()` → `< 30` gate → global `qScore` sort (line 1956), then compared queue order to pure waste_score-descending order.
- Verified the production-served `index.html` contains byte-identical `wasteScore`, `renewalUrgency`, `qScore`, gate code, and annual expression (production parity assertions all PASS).

## PASS results

1. **Formula exactness (120+ assertions):** `wasteScore` is exactly `annual × (1−usage) × urgency × confidence`. Full grid over annuals {0, 60, 180, 240, 520, 1200} × usages {0, 0.25, 0.5, 0.8, 1} × urgencies {0.3, 0.6, 0.8, 1.0} × conf 0.9, plus edges: usage=1 → 0, usage=0 → full annual, confidence=0 → 0, urgency=0 → 0, annual=0 → 0. Worked example: `wasteScore(180, 0.5, 0.6, 0.9) = 48.6` exactly.
2. **Urgency tiers, low end (10 assertions):** days 0–7 → 1.0; 8–14 → 0.8; 15–30 → 0.6 (boundary values −3, 0, 1, 7, 8, 10, 14, 15, 20, 30 all PASS). Monotone non-increasing over 0–365 PASS.
3. **Annual multipliers:** monthly×12 PASS (15.49→185.88, 9.99→119.88), yearly×1 PASS, weekly×52 PASS. Both code sites (`buildQueue` line 1841, `cancelCard` line 3293) use the identical ternary — card-displayed annual and scored annual cannot diverge.
4. **Gate:** `if (score < 30) return;` present in template AND production. Boundary proven: 29.99/29.9999/29.999999 excluded, exactly 30/30.0001/31/100/5000 admitted — "only score ≥ 30 enters queue" PASS.
5. **Pipeline gate behavior:** simulated subs with waste 28.4, 17.1, 2.2 correctly excluded; 88.3/50.1/216/39.8/131.0 correctly admitted.
6. **`(1−usage)` in gate:** the gate score includes the factor PASS; user levers verified: usage=1 zeroes waste, usage=0 maximizes it.
7. **Production parity:** all 6 parity assertions PASS — production runs the same code I tested.

## FAIL findings (7) — all legitimate, require fixes

### FAIL 1–4: `renewalUrgency` floors at >30 days; no decay across 30–60 days
Expected: urgency stays elevated until ~60 days, then decays to floor. Actual as-coded:
```
days 31 → 0.3, 45 → 0.3, 59 → 0.3, 60 → 0.3, 61 → 0.3, 365 → 0.3
```
A subscription billing in 45 days gets the same 0.3 floor as one billing in a year — the function collapses the 31–60 window instead of decaying through it. Fix: add an intermediate tier (e.g. 31–60 → 0.45) so floor only applies at 60+ days.

### FAIL 5–6: quarterly/biweekly annualization wrong (inflates/deflates waste)
Coded: `amount * (interval === "monthly" ? 12 : interval === "yearly" ? 1 : 52)` — everything non-monthly/non-yearly falls through to ×52.
- quarterly $60 → coded **3120**, correct **240** (13× inflation; spec classifies quarterly at doc 2 line 28 and demands the annual figure be "a twelve-month projection" — line 69)
- biweekly $20 → coded **1040**, correct **520** (2× inflation)
A quarterly $60 subscription scores waste 1560×(1−u)×urg×conf instead of 120×… — it will outrank genuinely wasteful subscriptions. Fix: explicit map `{monthly:12, weekly:52, biweekly:26, quarterly:4, yearly:1}` at both line 1841 and line 3293.

### FAIL 7: cancel cards are NOT sorted by waste_score descending in the rendered queue
The cancel branch computes `score = wasteScore(...)` for the ≥30 gate, but the final render sort (line 1956) is the global earn-style formula `qScore = dollars × conf × urg / effort` — which drops the `(1−usage)` term and divides by effort minutes. Simulated proof:
```
waste order:  gym(216) > stream2(131) > netflix(88.3) > spotify(50.1) > news(39.8)
queue order:  stream2 > netflix > gym > spotify > news
```
Gym has 2.4× Netflix's waste but renders below it because effort 30 min penalizes its qScore (14.4 < 17.7). Spec line 58 says the queue ranks by waste_score; the implementation ranks cancel cards by a different formula. Fix: sort cancel cards by `wasteScore` descending (at minimum within the cancel card set), or fold `(1−usage)` and remove the effort penalty for cancel cards in the global sort.

## Additional observations (not counted as FAIL — spec or task silent)

- **usage_signal is a hardcoded 0.5 placeholder** (`const storedUsage = null; // TODO: load from user prefs per merchant_id`), confirmed by source assertion. The spec requires the one-tap "do you still use this?" on the card (line 62) and says never to present inferred non-usage as fact — the placeholder neither asks nor stores. Every score is mechanically halved by an invented constant. This is already flagged in the main QA tracker (X1-F8); it undermines the ranking the moment real user input exists.
- **Cancel-card `why` string** (`$annual/yr × conf% × urgency / effort min`) documents the qScore formula, not the waste formula — consistent with the code, but it means the UI narrates the wrong ranking math (related to FAIL 7).
- **Demo-data caveat:** `detectRecurrence` runs on `loadTrackData()` which still serves fabricated demo transactions in the default path, so the cancel cards being ranked are not necessarily real subscriptions (known defect #1, X1-F1 partially addressed by the SimpleFIN proxy in this build).

## Design point (4 function + 1 design)

Function: 3/4 — formula core, gate, and multipliers for the common intervals are exact, but the three FAIL clusters (urgency collapse, quarterly/biweekly math, wrong sort) are ranking-correctness defects, so full function credit is withheld. Design: 1/1 — no UI was evaluated beyond the `why` string; nothing user-visible contradicts the simple-complexity bar on this path. **Score: 4/5**, pending the three fixes and a production re-run.

## Verdict

**CONDITIONAL FAIL → 175/182 PASS.** The waste_score formula itself is implemented exactly and the ≥30 gate is exact. Do not mark C5 complete until: (a) `renewalUrgency` decays at 60+ days instead of flooring at 31, (b) quarterly×4 / biweekly×26 annualization, (c) cancel cards sorted by waste_score descending. All three fixes are in `src/upmore-app-template.html`, then rebuild (`python3 src/build-app.py`), commit, push, and re-verify production before re-running this suite.
