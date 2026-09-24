# Beta agent 15 - output

## Scenario
AUTH STATES. On the You tab sign out. Assert signed-out states render correctly (Track shows a sign-in prompt, ledger shows a sign-in prompt, no crashes). Sign back in; assert data returns.

## FINAL-BUILD run (2026-09-24, build 654ab68)
AGENT: 15 — Auth states. RESULT: PASS (8/8).
- [PASS] Signed in via #login with qa15@upmore.app — redirected to #home; You tab showed "Sign out".
- [PASS] Added test subscription AuthTest15 / $9.99 / Monthly — Track showed "~$9.99/mo · 1 active" with AuthTest15 listed.
- [PASS] Signed out via You tab — redirected to #splash with "Get started"/"Log in".
- [PASS] Signed-out Track renders a proper sign-in prompt ("Stop the leaks, keep the cash", "Sign in with Google to track", privacy note) — not a crash or dead screen.
- [PASS] Signed-out Money log renders a proper sign-in prompt ("Sign in to keep your money log.") — not a crash or dead screen.
- [PASS] Signed-out save attempt NOT silently swallowed: "+ Log a result", $25 + note, "Log it" -> error banner "Couldn't save - check your connection and try again." Nothing persisted (log stayed empty). NOTE: the message misattributes the cause (connection vs. sign-in), but it is not a silent no-op.
- [PASS] Signed back in — redirected to #home; AuthTest15 returned ("~$9.99/mo · 1 active").
- [PASS] Cleanup: cancelled AuthTest15 via "Cancel subscription" — Track shows "Nothing tracked yet"; money log $0.00, no entries. No test data remains.
Retrospective: intent served — signed-out users get explicit sign-in prompts, save attempts surface instead of vanishing, data survives sign-out/sign-in. Friction: (1) the failed-save error blames the connection instead of saying sign-in is required, and the banner persisted/stuck across navigation and even after re-signing in; (2) You tab still shows a "Sign out" button while signed out; (3) profile header shows generic "Friend" even when signed in; (4) "Cancel subscription" routes into Guide chat with a prefilled draft rather than inline removal (draft never sent; subscription was removed from tracking).
Cleanup: done.
FIX (same day, unreleased): (1) save handlers now check sign-in FIRST and show "Sign in to save — your stuff only lives in your account." instead of the connection error; (2) toast banners now auto-dismiss after 4s and clear on navigation; (3) "Sign out" button hidden when signed out; (4) profile header shows the user's actual first name when signed in. Pending rebuild + redeploy, then rerun agent 15's signed-out-save probe.

## RERUN 1 (2026-09-24, build dbb4578 — STALE RESULT, see diagnosis)
AGENT: 15 — Signed-out save rerun. RESULT: FAIL (5/5) — **diagnosed as a stale service-worker cache, NOT a product-code failure.**
- (1a/b/c) All three signed-out save paths showed the OLD "Couldn't save - check your connection" message.
- (2) The error toast persisted across navigation and never auto-dismissed.
- (3) "Sign out" button visible while signed out.
- (4) Profile header showed "Friend" after sign-in (and oddly showed a cached "Vish" while signed out — stale localStorage from the shared test profile, not a product bug).
Diagnosis: the app's service worker used a CONSTANT cache name ("upmore-v3") with a CACHE-FIRST fetch handler for "/" and "/index.html" — it served the previous build's HTML immediately while updating in the background. This agent's browser loaded the pre-fix build; agents 16r/18r (same batch, loaded moments later) got the fixed build and PASSED. The dbb4578 fixes were verified live via curl (needSignIn x5, pays-fast marker present).
FIX (same day, unreleased): (1) sw.js cache name is now stamped per build by src/build-app.py (short git hash), so every deploy gets a fresh cache version and old caches are purged on activate; (2) the fetch handler is now NETWORK-FIRST for "/" and "/index.html" (always serve the latest deployed build; cache only as offline fallback), cache-first retained for icons/manifest. Pending rebuild + redeploy, then rerun agent 15 against a guaranteed-fresh build.
Cleanup: done — nothing persisted (all saves failed on the stale build; Track/Deadlines/Money log all empty).

## RERUN 2 (2026-09-24, build fb84f4c — AGENT VERDICT: FAIL, under adjudication)
AGENT: 15 — Signed-out save rerun with fresh-build protocol + re-sign-in persistence. Agent-reported result: FAIL.
- Fresh-build protocol PASS (5s wait + reload; Guide header had no History button).
- Signed-in saves PASS: So15 $9.99/mo tracked ("Cancel So15 — Keep $119.88/yr"); D15 2026-10-15 deadline ("renews in 21 days"); $25 M15 money-log entry ("Logged").
- Sign-out PASS (reached Welcome).
- Signed-out money-log save PASS: exact toast "Sign in to save — your stuff only lives in your account.", nothing persisted. Sub/deadline signed-out saves could not be attempted (forms intentionally hidden while signed out).
- Toast auto-dismiss: agent FAIL — claimed toast lingered 14s+ in screenshots (described as "small white pill, bottom-left").
- Signed-out profile PASS: no Sign out button.
- Re-sign-in: agent FAIL (2 assertions) — (1) profile showed "Friend" not a real name; (2) So15/D15/$25 M15 all gone after sign-out/sign-in ("Nothing tracked yet", $0.00).
- Cleanup: trivially satisfied (nothing to delete).
Agent retrospective: signed-out gating works; claimed defects were (1) toast not auto-dismissing, (2) data not surviving sign-out/sign-in + "Friend" profile name.

## ADJUDICATION (2026-09-24, clean-profile Playwright probes, then fix 00826d2)
Three claims investigated with independent Playwright probes (fresh Chromium profile, CONNECT-relay egress, 390px viewport) against production:
1. Toast auto-dismiss — CLAIM REJECTED. Probe triggered the real gating toast ("Sign in to save — your stuff only lives in your account."), sampled #upmoreToast opacity: 1 at 2.1s, 0 at 4.1s/6.2s/8.2s/10.2s. The 2200ms fade timer works. The agent's "small white pill, bottom-left" matches NO element in the app (the toast is a dark centered pill) — it was observing something else. VERDICT: PASS, no code change.
2. Data loss across sign-out/sign-in — CLAIM REJECTED as product bug. Clean-profile probe: saved "PWTest" $1/mo, signed out (via You > Sign out, which reloads), signed back in — PWTest SURVIVED. Direct REST check (qa15 JWT) confirmed 0 rows under qa15's uid from the agent's session: the agent's step-1 saves never reached the DB under qa15's identity — its in-memory session in the SHARED managed-browser profile did not match the qa15 login (known shared-profile localStorage contamination; all 25 beta tasks share one leased Chromium profile). Product behavior verified correct. VERDICT: PASS, no code change. Standing rule reinforced: never treat managed-browser session anomalies as product bugs without a clean-profile reproduction.
3. Profile shows "Friend" while signed in — CLAIM CONFIRMED, real product bug, reproduced in clean profile. Root cause: saveProfile() wrote display_name="Friend" into the profiles table on first sign-in when no name was known; planData() then baked it into d.name; the dbb4578 email-prefix fallback in renderProfile() was dead code because d.name was always truthy. FIX (committed 00826d2, deployed + verified live): saveProfile() now falls back to the account's email prefix instead of "Friend"; renderProfile() treats a stored "Friend" as absent so already-baked rows self-repair. Production probe after deploy: profile shows "qa15", avatar "Q". VERDICT: was FAIL, now FIXED and verified.
Cleanup: probe test subscription PWTest deleted via REST; qa15 tables empty; profiles row retains display_name="Friend" in DB but renders as "qa15" (self-repair verified).
RERUN 2 adjusted verdict: PASS on 5 of 7 agent assertions; the 2 FAILs split into 1 agent-observation error (toast), 1 environment artifact (data), 1 real bug (name — now fixed in 00826d2).
Next: rerun 15r3 (full scenario) against 00826d2 with hardened protocol (verify signed-in identity matches the login email before saving; no reliance on shared-profile localStorage across the sign-out reload).
