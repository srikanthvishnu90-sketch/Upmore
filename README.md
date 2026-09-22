# Upmore

Muse for making basic online money. Helps regular people make their first bit
of extra money online — one simple, vetted offer at a time with easy steps.

## Layout

- `index.html` — the built app (what Vercel serves). Generated, do not edit directly.
- `vercel.json`, `manifest.webmanifest`, icons, `img/` — static assets.
- `src/` — the real source:
  - `upmore-app-template.html` — app template with a `<!--__UPMORE_DATA__-->` placeholder
  - `data/upmore-data.json` — the 535-route offer catalog (all routes unverified)
  - `build-app.py` — injects the data into the template
  - `build-data.py` — rebuilds the data file from the catalog spreadsheet

## Build

```bash
cd src && python3 build-app.py   # writes src/upmore-app.html
cp src/upmore-app.html ../index.html
```

Edit the template, never `index.html`.

## Backend

Supabase project `upmore` (ref `mrwngntwmnaqrqhupvlt`):
- tables: profiles, routes, proof_log, agent_threads, agent_messages,
  playbook_progress, reminders (RLS on)
- edge function `agent-chat` (Anthropic-powered Guide agent, JWT-gated)

## Product rules

- 4 tabs: Home, Explore, Guide, You. Guide/chat is central.
- Palette: green, sky, white, black only. No corporate/AI-serious language.
- The agent is a max-agency co-pilot: deep links, pre-filled info, step-by-step
  guidance, progress tracking, expiry reminders. The user personally does
  KYC, identity attestations, agreements, and Apple ID/Face ID taps.
- Every offer shows its verification state honestly. Nothing is "vetted"
  until it actually is.
