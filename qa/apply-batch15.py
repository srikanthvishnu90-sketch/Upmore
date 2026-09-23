#!/usr/bin/env python3
"""Apply batches 15 (prediction markets), 16 (brokerage promos), 17 (fintech) to the DB.
21 verified, 26 rejected. Prediction-market 'verifies' are gambling/volatility facts,
not income; R0004/R0010 are fee schedules (costs). proof_log audit rows for all 47."""
import json, sys, time
sys.path.insert(0, "/opt/hatch/skills/skill-creator/bin")
from dynamic_credentials import add_surrogate_to_request, read_json_response
import urllib.request

REF = "mrwngntwmnaqrqhupvlt"
PROJ = f"https://{REF}.supabase.co"

def mgmt_get(path):
    r = urllib.request.Request("https://api.supabase.com/v1" + path, method="GET")
    add_surrogate_to_request(r, "custom.supabase", allowed_hosts=["api.supabase.com"])
    with urllib.request.urlopen(r, timeout=60) as resp:
        return read_json_response(resp)
SVC = next((k["api_key"] for k in mgmt_get(f"/projects/{REF}/api-keys") if k.get("name") == "service_role"), None)

def req(method, path, body=None, tries=5):
    data = json.dumps(body).encode() if body is not None else None
    last = None
    for i in range(tries):
        try:
            r = urllib.request.Request(PROJ + path, data=data, method=method,
                headers={"apikey": SVC, "Authorization": "Bearer " + SVC,
                         "Content-Type": "application/json", "Prefer": "resolution=merge-duplicates"})
            with urllib.request.urlopen(r, timeout=60) as resp:
                return resp.status, json.loads(resp.read() or b"null")
        except Exception as e:
            last = e
            time.sleep(2 * (i + 1))
    raise last

# --- prediction markets / crypto: 6 verified ---
PM = {
    "R0005": ("Manifold", "Mana play-money ONLY: M1,000 free grant; ZERO cash value, cannot be converted or withdrawn. Real-money Sweepcash layer discontinued March 2025", "This is gambling, not income: mana has zero cash value; leaderboard points are not money", None),
    "R0004": ("PredictIt", "FEE SCHEDULE ONLY (costs, not earnings): 10% fee on profitable trades + 5% withdrawal fee per official docs/CFTC filing", "This is gambling, not income: contracts can go to $0; fees eat returns; US-only", None),
    "R0010": ("Smarkets", "FEE SCHEDULE ONLY (costs, not earnings): 2% commission on net winnings per market (UKGC-licensed); zero-sum between users minus commission", "This is betting, not income: exchange bets are zero-sum between users minus commission", None),
    "R0011": ("Binance.US", "Current $SOL First Depositor Bonus (Sept 17-Oct 17, 2026): up to $200 in SOL on $250+ first deposit; deposit locked untouched through Nov 17, 2026 or bonus forfeited. 'Crypto may lose the entire value' per Binance's own terms", "Bonus paid in SOL — highly volatile; Binance's own terms say it is NOT an income guarantee", "2026-10-17"),
    "R0013": ("Coinbase Advanced", "Official new-user referral: $5/$20/$50 in USDC by 14-day trading-volume tiers; requires trading $100+ of YOUR OWN capital (at risk); referral link required", "This is not free money: you must risk your own capital trading within 14 days", None),
    "R0015": ("Gemini", "Current referral: trade >=$100 in 30 days, both sides get 'up to $50' in crypto — maximum, not guaranteed; volatile; program revocable", "The $50 is not free money: requires trading $100 of your own money within 30 days", None),
}
PM_REJ = {
    "R0001": "no stable official $50 credit — only rotating affiliate codes with conflicting variants; polymarket.com blocks US trading — fails C1",
    "R0002": "no stable official $55 — affiliate-code variants conflict ($25 flat, $15-$500 tiers); promo credit is non-withdrawable trading credit — fails C1",
    "R0003": "not a prediction market; social investing network that pays users nothing — category misfire, fails C1",
    "R0006": "no verifiable platform exists; 'Lokai Markets' not found in any search index — recommend catalog removal",
    "R0007": "family-calendar hardware company, not a prediction market; no payout product at all — recommend catalog removal",
    "R0008": "sports betting with negative expected value; no official promo with a concrete payout — fails C1",
    "R0009": "bet-tracking tool that pays users nothing; any 'promo' money comes from third-party sportsbooks — fails C1",
    "R0012": "Coinbase Learning rewards officially discontinued May 27, 2025 — the $3-10/module program is dead — fails C2",
    "R0014": "no official signup/referral promo exists; only current official promo is a one-winner SOL trading contest — fails C1",
}

# --- brokerage promos: 11 verified ---
BR = {
    "R0018": ("SoFi Invest", "1% ACAT match up to $50,000, no minimum, ends Sept 30, 2026 — requires moving EXISTING brokerage assets; 5-year lock; an ordinary user with no other brokerage earns $0", "US", "2026-09-30"),
    "R0019": ("Public.com", "$100 fractional stock/ETF both sides on a $1,000 initial one-time deposit; no fixed deadline; referral link required; cash value locked 12 months (early-withdrawal fee up to $100)", "US", None),
    "R0021": ("Acorns", "$5 of ETF Reward Shares on a $5 investment (NOT cash); referral link required; $3/mo subscription eats the bonus; lands 30-45 days", "US", None),
    "R0023": ("Moomoo", "NVDA stock tiers: $500->$30, $2,000->$100, $10,000->$200, $50,000->$400, $100,000->$1,000; deposits settle by Oct 15, 2026; 60-180 day maintenance locks; ACH/wire only, ACAT excluded", "US", "2026-10-15"),
    "R0024": ("Firstrade", "1 free stock each side, no deposit required. Weakest verification: only official page is the 2019 launch announcement; stock values ($3-$200) from third-party trackers, not official terms", "US", None),
    "R0025": ("tastytrade", "$100 both parties on $1,000 within 60 days; runs through Nov 30, 2026; referral link required; 6-month withdrawal lock; IRAs excluded", "US", "2026-11-30"),
    "R0027": ("Charles Schwab", "$50 of fractional shares (Stock Slices of top 5 S&P 500, split equally); $50 own deposit within 30 days; no fixed deadline. $100-$1,000 referral tiers also exist (needs referral code)", "US", None),
    "R0030": ("Interactive Brokers", "Referral: referrer gets $200 (friend deposits $10k+ within 30 days AND holds $10k for 1 year; referrer needs $2k+ NLV and 1+ trade); friend gets $1 IBKR stock per $300 deposited, max $1,000. Ordinary new user gets ~$1-$4", "US", None),
    "R0031": ("Betterment", "$100 into self-directed account; $2,500 of outside funds by Oct 22, 2026; paid on/around Oct 29, 2026; new clients only", "US", "2026-10-22"),
    "R0032": ("Wealthfront", "$30 into first Cash Account; $500 within 30 days; maintain $500 on day 30; paid within 30 days after; promo-landing-page signup only", "US", None),
    "R0035": ("Vantage", "150% NON-WITHDRAWABLE trading credit on first deposit up to $1,500 (e.g. $50->$75), 25% on later deposits; 6/9/2025-12/31/2026; opt-in first. This is LEVERAGED FOREX/CFD with up to 500:1 leverage — not cash, never withdrawable", "Vantage; high risk", "2026-12-31"),
}
BR_REJ = {
    "R0017": "US promos live in in-app Promotion Center only; no official webull.com page states a concrete current payout — fails C1",
    "R0022": "official terms page is a template with unfilled amount placeholder; concrete promos are targeted/invitation-only — fails C1",
    "R0028": "only official cash offer found is the expired 2022 Starter Pack (ended 12/02/2022); FIDELITY100 live status unconfirmed — fails C1",
    "R0029": "Vanguard pays no new-account bonus at all; only current incentive is a 0.25% Cash Plus APY rate bump, not a payout — fails C1",
    "R0033": "no official public bonus on m1.com; 'up to $500' is affiliate ad copy; referral figures conflict — fails C1",
    "R0034": "official page says 'The cash bonus promotion has ended' (deadline 9/17/2026); live $100 referral is bank-only, not Invest — fails C2",
}

# --- fintech: 4 verified ---
FT = {
    "R0099": ("Current", "$100 referral: new user signs up via referral link/code and completes $200+ in eligible recurring payroll deposits within 45 days; paid within 10 business days; $1,000/year cap per referrer. Limited-time $200 variant expires Oct 1, 2026 ($1,500+ payroll in 35 days)", "US", "2026-10-01"),
    "R0109": ("Cash App", "$15 goes to the NEW USER (enters referral code + sends $5+ within 14 days); inviter's amount shown in-app only, not publicly fixed", "US", None),
    "R0110": ("Venmo", "$10 each — VENMO DEBIT CARD referral specifically: friend spends $50+ on purchases within 30 days; 10-reward/$100 cap", "US", None),
    "R0111": ("PayPal", "1,000 Rewards points per side when referred friend spends $5+ within 30 days; points redeemable for $10 cash back (not $10 cash); 10-friend/$100 cap", "US", None),
}
FT_REJ = {
    "R0097": "no $500 personal-loan bonus in current official terms; expired 2021/2022 targeted offer; borrowing is not making money — fails C1",
    "R0101": "current reward is an ExtraCash advance boost (repayable borrowing capacity), not $50 cash — fails C1",
    "R0102": "current official reward is access to a $50 cash advance you must repay, not $150 cash; $150 program expired — fails C1",
    "R0104": "HMBradley shut down its consumer banking program end of 2023; no account to open, no bonus to earn — fails C2",
    "R0105": "no official lili.co referral terms with a concrete current payout; third-party numbers conflict and look stale — fails C1",
    "R0106": "no official found.com referral terms with a concrete current payout; third-party figures conflict — fails C1",
    "R0107": "official Novo terms publish no bonus amount ('as specified in the offer'); claimed $200 unverifiable — fails C1",
    "R0108": "official Mercury terms publish no fixed $100 — amounts/limits per-account, shown on referral page only — fails C1",
    "R0112": "Zelle pays nothing to sign up; bank-to-bank payment network, not a bonus offer; route itself claims $0 — fails C1",
    "R0113": "no official $50 personal bonus; only official program is influencer-only; standard rewards vary per account — fails C1",
    "R0114": "official terms state reward amounts are unique per referrer, shown only in-app, one-sided program; cited promotion period ended Sept 15, 2026 — fails C1",
}

now = "2026-09-23T01:55:00+00"
n_v, n_r = 0, 0
for rid, (prov, pt, catch, exp) in {**PM, **BR, **FT}.items():
    d = json.load(open(f"/home/hatch/workspace/upmore/qa/verification/{rid}.json"))
    terms = d.get("terms_url") or d.get("official_url")
    steps = [{"text": s, "done_when": "", "warn": ""} for s in d.get("steps", [])[:8]]
    catches = ([catch] if catch else []) + d.get("catches", [])
    patch = {"status": "verified", "verified_at": now, "verified_source_url": terms,
             "provider_url": d.get("official_url"),
             "steps": steps, "catches": catches,
             "payout_text": pt, "payout_timing": d.get("timing"),
             "min_age": 18, "geo_notes": prov,
             "expires_at": exp}
    st, _ = req("PATCH", f"/rest/v1/routes?route_id=eq.{rid}", patch)
    note = ("Evidence: " + (d.get("payout_quote") or "")[:200] + " | Catch: " +
            (d.get("biggest_catch") or "")[:180])
    req("POST", "/rest/v1/proof_log", {"route_id": rid, "result": "verified",
        "source_url": terms, "checked_at": now, "notes": note[:500]})
    n_v += 1
    print(rid, "verified", st, flush=True)

for rid, reason in {**PM_REJ, **BR_REJ, **FT_REJ}.items():
    d = json.load(open(f"/home/hatch/workspace/upmore/qa/verification/{rid}.json"))
    terms = d.get("terms_url") or d.get("official_url")
    req("POST", "/rest/v1/proof_log", {"route_id": rid, "result": "rejected",
        "source_url": terms, "checked_at": now,
        "notes": ("REJECTED per checklist: " + reason)[:500]})
    n_r += 1
    print(rid, "REJECTED logged", flush=True)

print(f"APPLIED: {n_v} verified, {n_r} rejected")
