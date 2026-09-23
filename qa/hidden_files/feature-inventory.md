# Upmore 25-feature 10/10 benchmark — feature inventory (2026-09-23)

## Server (agent-chat edge function, supabase/functions/agent-chat/)
S01. Make-me-$X plans (tryMakeMeX — honest cash math, exact steps, links, catch)
S02. Vague-opener anchoring ("i want to make money" → concrete $20 plan)
S03. DB-driven walkthroughs (tryWalkthrough — full verified steps, link, payout, catch)
S04. Deterministic scam guard (5 patterns + deterministic prepend)
S05. Gambling/prediction-market guard
S06. Privacy guard (never serve another user's data)
S07. Quantitative stock screener (Yahoo, 4 factors, z-scored, honest copy)
S08. Fast-path factual answers (discovery, how-it-works, requirements, payout, availability, eligibility, catches, link)
S09. Grounding post-check (invented amounts, unlisted URLs, guarantee language; debunk exception)
S10. Grounding violation fallbacks (SAFE_FALLBACK / SCAM_FALLBACK selection)
S11. Due-reminder proactivity (deterministic prepend)
S12. Expiry alerts (routes expiring within 14 days)
S13. Resume nudge (walkthrough idle >24h)
S14. ask_profile persistence (facts saved once, never re-asked)
S15. Walkthrough action persistence (start_walkthrough/next_step + deterministic walk-start)
S16. Per-user rate limiting (60/hr)
S17. Auth correctness (explicit getUser(jwt); 401/400 paths)
S18. General model chat path (tone, grounding rules, one-idea-at-a-time coaching)
S19. Stale-copy audit (no "14 verified routes" / "535" in user-facing server copy)

## Client (src/upmore-app-template.html → built index.html)
C01. Onboarding state machine (splash→welcome→time→about→situation→plan→phone/Google)
C02. Personalized "first 3 moves" plan (planData/buildPlan from state/time/cash)
C03. Home hero walkthrough + progress bar
C04. Walkthrough step rendering (done_when, per-step links)
C05. App-store deep links for core routes
C06. Explore search (xFiltered)
C07. Explore difficulty chips + category filters
C08. Higher-risk lane toggle (default hidden)
C09. Explore pagination (xmore)
C10. Money/time/rate display + earn-ratio ordering on cards
C11. Guide local answers (guideAnswer — provider/category/verification/catch/payout/tax/no-deposit/easiest/next-move)
C12. Guide EXRULES excluded-topic handling (hard + soft rules)
C13. Guide empty state + starter prompts
C14. Agent fallback chain (agentAsk → local answers when offline/unsigned)
C15. Session persistence across OAuth round-trip (localStorage)
C16. Playbook progress sync to DB
C17. Profile page (You tab) + editable rows
C18. "How Upmore makes money" disclosure
C19. Sign out
C20. Reminders toggle UI
C21. PWA (manifest, sw.js offline, icons)
C22. Visual identity (green/sky/white/black only; 4 tabs; no wins)

## Cross-cutting checks
X01. 1500-verified catalog integrity in served bundle (already proven by parent)
X02. Live edge-function probes (auth, model happy path, scam stress, adversarial amounts, age contradiction)
X03. Frontier-bar comparison per feature (what GPT-6 Astra / Claude Fable 5.1 class would do for the bounded use case)
