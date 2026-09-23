#!/usr/bin/env python3
"""Chunk E speed audit: apply evidence JSON updates + DB speed sync.

Chunk: 69 routes (Brokerage Promo + Fintech/Neobank + Fintech Bonus + Store
Signup + Student Program + Competition), all speed='weeks' in DB.
Moves: 19 (13 -> days, 6 -> today). Kept: 45 (weeks, fastest-honest-path documented).
Skipped (credit-card offers, hard rule - untouched): R1922, R1923, R1925, R1930, R1931.
"""
import json
import os
import sys

VDIR = "/home/hatch/workspace/upmore/qa/verification"
DATE = "2026-09-23"

# ---------------------------------------------------------------- MOVED ----
# speed, when_cash_arrives, maximize, rationale; timing kept unless noted.
MOVED = {
    "R0016": {
        "speed": "days",
        "when_cash_arrives": "Reward normally credits around day 8 after account approval (allow ~1 more week). The reward cash itself cannot be withdrawn for 1 year \u2014 dropping below the tier's deposit floor can trigger rescission of the reward.",
        "maximize": "Fastest path: get approved, then initiate and settle the qualifying deposit inside the 7-day post-approval window (wire settles fastest); the reward credits ~day 8. Smaller tiers share the same fast clock ($1,000-$4,999.99 \u2192 $25). Blocker: targeted offer only \u2014 no public signup path; deposit and reward locked 1 year.",
        "rationale": "Official Robinhood support article: 'Reward normally credits around day eight, with approximately one additional week allowed' \u2014 the credit lands in days; the 1-year withdrawal lock is disclosed in when_cash_arrives.",
    },
    "R0018": {
        "speed": "days",
        "when_cash_arrives": "1% match paid in cash within 5 business days after the ACAT-transferred funds settle (up to $50,000 match). Funds must stay 5 years to keep the full match.",
        "maximize": "Fastest path: initiate an ACAT transfer of an existing brokerage balance (settles in ~5-7 business days); the cash match posts within 5 business days of settlement. Blocker: requires an existing portfolio to transfer; 5-year maintenance to keep the match.",
        "rationale": "Official SoFi terms: matches 'paid in cash within 5 business days from the date which the funds settle'.",
    },
    "R0019": {
        "speed": "days",
        "when_cash_arrives": "Once qualified, claim the $100 fractional stock/ETF reward \u2014 it is delivered to your account on claim (within days of the $1,000 deposit settling). The cash value cannot be withdrawn for 12 months.",
        "maximize": "Fastest path: open via a funded friend's referral link, deposit $1,000 immediately (settles in days), claim the $100 stock the moment you're cleared. Blocker: needs a referral link from a funded Public user; the reward is stock, not cash; 12-month cash-withdrawal lock.",
        "rationale": "The $100 stock/ETF reward is delivered on claim \u2014 days once the qualifying $1,000 deposit settles; the 12-month cash-withdrawal lock is disclosed.",
    },
    "R0027": {
        "speed": "days",
        "when_cash_arrives": "Once your $50+ deposit settles, Schwab deposits $50 to buy fractional shares of the 5 largest S&P 500 stocks \u2014 days after funding, with a notification when the orders are placed.",
        "maximize": "Fastest path: open the account and fund $50+ immediately (within the 30-day window); the $50 stock bonus follows funding by days. Note: it's $50 of stock slices, not spendable cash \u2014 you put in $50 and end up with ~$100 invested.",
        "rationale": "Official Schwab terms: 'Once funded, Schwab will deposit $50 in your account to purchase your fractional shares.'",
    },
    "R0096": {
        "speed": "days",
        "when_cash_arrives": "Bonus deposited within 7 business days of completing all requirements: $50 for $1,000-$4,999.99 in direct deposits, $400 for $5,000+ within the 25-day window.",
        "maximize": "Fastest path: set up direct deposit immediately \u2014 the 25-day window starts at your first $1+ direct deposit; the bonus posts within 7 business days of hitting the threshold. A $5,000+ payroll deposit in one cycle unlocks the $400 tier.",
        "rationale": "Official SoFi terms: 'Bonus deposited within 7 business days of completing all requirements.'",
    },
    "R0099": {
        "speed": "days",
        "when_cash_arrives": "$100 paid within 10 business days after qualification ($200+ in eligible recurring payroll deposits within 45 days via a referral link).",
        "maximize": "Fastest path: sign up via a referral link and route $200+ of payroll direct deposit immediately; the $100 posts within 10 business days of the deposits posting. Blocker: requires real recurring payroll deposits.",
        "rationale": "Official Current terms: '$100 referral reward ... paid within 10 business days'.",
    },
    "R0109": {
        "speed": "days",
        "when_cash_arrives": "The $15 follows the qualifying $5+ send within 14 days per official terms (typically posts within days of the send settling).",
        "maximize": "Fastest path: enter a referral code at signup and send $5+ within 14 days; the $15 posts within days. Blocker: the $15 goes to the new user \u2014 the inviter's reward is shown in-app only.",
        "rationale": "Official Cash App terms: the reward follows the qualifying $5+ send within 14 days.",
    },
    "R0111": {
        "speed": "days",
        "timing": "Rewards available to redeem within 14 days after qualifying, per official PayPal Invite Friends terms (verified live 2026-09-23); 1,000 points redeemable for $10 cash back.",
        "when_cash_arrives": "1,000 Rewards points available to redeem within 14 days after qualifying; points redeem for $10 cash back in the PayPal app.",
        "maximize": "Fastest path: the referred friend signs up via your link, links a bank/card, verifies their phone, and makes a $5+ PayPal checkout purchase within 30 days \u2014 points land within 14 days, redeem immediately for $10 cash back. Both sides earn.",
        "rationale": "Official PayPal terms (verified live 2026-09-23): 'Rewards should be available ... to redeem within fourteen (14) days after qualifying'.",
    },
    "R1065": {
        "speed": "days",
        "when_cash_arrives": "1% match (3% with $5/mo Gold) available to invest immediately when each contribution settles \u2014 days after the deposit posts. Must remain 5 years to avoid the early-removal fee.",
        "maximize": "Fastest path: contribute to the Robinhood IRA (transfer settles in days); the match lands as soon as the contribution settles. Blocker: IRA money \u2014 early-withdrawal penalties apply; 5-year clawback on the match.",
        "rationale": "Official Robinhood terms: the match is 'typically available to invest immediately when contributions settle'.",
    },
    "R1066": {
        "speed": "days",
        "when_cash_arrives": "1% match paid in cash into the IRA within 5 business days of the deposit settling. Deposits must stay 5 years or SoFi claws back part of the match.",
        "maximize": "Fastest path: deposit into the SoFi IRA; the match posts within 5 business days of settlement. Blocker: 5-year maintenance clawback; IRA withdrawal rules apply.",
        "rationale": "Official SoFi terms: match 'paid in cash into the IRA within 5 business days of the deposit settling'.",
    },
    "R5802": {
        "speed": "days",
        "when_cash_arrives": "Free share (\u00a310-\u00a3100 value) dropped into the account 7-10 days after qualifying (fund \u2265\u00a350 net within 30 days via an existing customer's referral link).",
        "maximize": "Fastest path: get a referral link from an existing Freetrade customer, open the account, fund \u00a350+ immediately; the free share drops 7-10 days later. Blocker: new customers cannot self-generate a referral link.",
        "rationale": "Official Freetrade terms: free share 'dropped 7-10 days after qualifying'.",
    },
    "R3510": {
        "speed": "days",
        "when_cash_arrives": "Per-signing pay ($5 basic notarization / $25 online real-estate closing) with payouts as quickly as the next business day.",
        "maximize": "Fastest path: complete notary signings in a covered state (FL, NV, PA, TX, VA); earnings can pay out the next business day. Blocker: coverage limited to 5 states; income scales with signing volume \u2014 nothing guaranteed.",
        "rationale": "Official Notarize terms: paid 'as quickly as next business day'.",
    },
    "R0373": {
        "speed": "days",
        "when_cash_arrives": "Student approval usually takes a few days; partner offers (free GitHub Pro, Copilot, Azure credits, JetBrains, etc.) activate immediately when claimed from the Education dashboard.",
        "maximize": "Fastest path: apply with your school email/ID today; once approved (a few days), claim each partner offer from the dashboard \u2014 each activates immediately. Blocker: must be a verifiable student.",
        "rationale": "Official GitHub Education terms: approval 'usually takes a few days'; offers activate on claim.",
    },
    "R1927": {
        "speed": "today",
        "when_cash_arrives": "250 welcome points credit immediately on registration \u2014 enough for one $2 savings redemption (200 pts = $2 in savings) at bp/Amoco/ampm/Thorntons, usable right away.",
        "maximize": "Fastest path: register online; the points land instantly and the $2 reward is usable on your next fuel-up. Blocker: ~$2 value, only at bp-family stations.",
        "rationale": "Official bp earnify terms: 'You will immediately receive 250 bonus points upon registering'.",
    },
    "R0374": {
        "speed": "today",
        "when_cash_arrives": "6-month free trial starts the day you sign up \u2014 full Prime shipping/streaming benefits active immediately (then $7.49/mo or $69/yr unless cancelled).",
        "maximize": "Fastest path: sign up with student verification; trial benefits are live the same day. Set a reminder to cancel before month 6 to pay nothing.",
        "rationale": "Official Amazon terms: 6-month free trial for eligible new members \u2014 benefits active from signup day.",
    },
    "R0375": {
        "speed": "today",
        "when_cash_arrives": "Discounted Premium Student rate applies from signup after SheerID verification \u2014 savings start the same day (up to 12 months per verification, max 4 years).",
        "maximize": "Fastest path: verify student status via SheerID at signup; the discount is live immediately. Re-verify every 12 months to keep it.",
        "rationale": "Official Spotify terms: discounted rate applies from signup after eligibility verification.",
    },
    "R0376": {
        "speed": "today",
        "when_cash_arrives": "Student pricing (~$19.99/mo first year on the annual plan, billed monthly) applies from signup after eligibility verification \u2014 savings start immediately.",
        "maximize": "Fastest path: verify student/teacher status at checkout; the discounted rate is live the same day.",
        "rationale": "Official Adobe terms: discounted rate applies from signup after eligibility verification.",
    },
    "R0377": {
        "speed": "today",
        "when_cash_arrives": "Free Education Plus plan applies as soon as you sign in with your institution email \u2014 active the same day while eligibility holds.",
        "maximize": "Fastest path: sign up with your school-issued email; the free Plus workspace is live immediately.",
        "rationale": "Official Notion terms: free Plus plan for students signed in with an institution email \u2014 active on verification.",
    },
    "R0378": {
        "speed": "today",
        "when_cash_arrives": "Free Professional-tier access granted after education-status verification \u2014 active the same day once approved.",
        "maximize": "Fastest path: apply with student/educator credentials; free access activates on approval, same day in most cases.",
        "rationale": "Official Figma terms: free for students/educators after verification \u2014 access granted on approval.",
    },
}

# ---------------------------------------------------------------- KEPT -----
# speed stays 'weeks'; maximize documents fastest honest path + blocker.
# R0110 also gets a timing refresh from today's live official-terms check.
KEPT = {
    "R0020": "Official: bonus tier determined on day 45, bonus added within 15 days after conditions are met (~day 45-60). Fastest path: fund the full tier amount on day 1 \u2014 smaller tiers share the same 45-day clock ($5k-$25k \u2192 $50). Blocker: the 45-day determination period is structural.",
    "R0021": "Official: Reward Shares deposited 30-45 days after the initial deposit settles. Fastest path: sign up via a referral link and make the initial deposit immediately; the $5 posts 30-45 days later. Blocker: the 30-45 day credit window is structural.",
    "R0023": "Official: free stocks added within 5 trading days after the 60/120/180-day holding period ends (tier-dependent). Fastest path: deposit to the lowest tier you can on day 1 ($500 \u2192 $30 NVDA \u2248 day 65). The $100-in-trading-coupons offer (for a $100 deposit) arrives sooner, but coupons aren't cash. Blocker: the 60-day minimum hold is structural.",
    "R0024": "Official: paid once the friend's application is complete and approved \u2014 no payout timeline published. Fastest path: refer a friend who completes the application immediately; stock credits after approval. Blocker: no published credit timeline \u2014 unverified speed.",
    "R0025": "Official: referral bonus deposited within 45 days of the account being opened and funded. Fastest path: fund $1,000+ within 60 days of opening; bonus posts within 45 days. Blocker: the bonus is withdrawable as cash only after the 6-month holding period.",
    "R0026": "Official: rewards paid within 7 business days after the 60-day funding period expires (~day 67 earliest). Fastest path: fund the full tier amount inside the 60-day window; the reward posts ~1 week after the window closes. Blocker: the 60-day funding period is structural.",
    "R0030": "Official: exact credit timing not stated; the friend must deposit $10k+ within 30 days and maintain the balance. Fastest path: refer someone ready to deposit $10k immediately. Blocker: no published payout timeline \u2014 unverified speed.",
    "R0031": "Official: $100 bonus paid on or around October 29, 2026, if $2,500+ of the qualifying deposit remains until then. Fastest path: enroll and deposit $2,500+ now; the bonus arrives on the fixed bonus date. Blocker: the fixed payout date is structural.",
    "R0032": "Official: $30 deposited within 30 days after meeting the terms \u2014 you must hold $500+ through day 30, so earliest payout is ~day 30-60. Fastest path: fund $500 on day 1 and keep the balance through day 30. Blocker: the day-30 balance check is structural.",
    "R0035": "Official: 150% first-deposit credit (up to $1,500) posts after deposit but can NEVER be withdrawn \u2014 only trading profits are withdrawable, and withdrawals can trigger proportional credit deduction. Fastest path: none for cash \u2014 only profits are real money. Blocker: the bonus itself is non-withdrawable credit, not cash.",
    "R1061": "Official: first 3% cash-match installment credited ~30 days after the 30-day match period closes, then monthly for 36 months. Fastest path: make all deposits inside the 30-day match period; first installment ~day 60. Blocker: the 30-day period plus 36-month drip is structural.",
    "R1062": "Official: one-time cash reward deposited within 2 weeks after the 90-day maintenance period ends (~day 105 earliest). Fastest path: fund the full tier on day 1 ($20k+ within 45 days); the reward posts ~2 weeks after day 90. Blocker: the 90-day maintenance period is structural.",
    "R1063": "Official: bonus credited 5-7 months after account opening, with the $1k/$10k threshold maintained for 90 days. Fastest path: fund $10,000+ on day 1 for the $100 tier. Blocker: the 5-7 month credit window is structural.",
    "R1067": "Official: first monthly match payment credited on/about one month after settlement, then monthly (12 payments for contributions, 60 for transfers). Fastest path: contribute early in the month; first 1% installment ~1 month after settlement. Blocker: the monthly drip schedule is structural.",
    "R1068": "Official: $250 incentive contribution deposited in February 2027 for accounts funded with $250+ by December 31, 2026. Fastest path: open and fund $250+ before Dec 31, 2026. Blocker: the fixed February 2027 payout date is structural.",
    "R5782": "Official: ACAT fee reimbursement (up to $100) credited within 30 days of SogoTrade receiving your transfer form. Fastest path: submit the transfer form the day you initiate the $10k+ ACAT. Blocker: the 30-day reimbursement processing bound is structural.",
    "R5785": "Official: bonus paid ~March 5, 2028 (open by Jan 5, 2027; fund by Feb 5, 2027; hold until Feb 5, 2028). Fastest path: none \u2014 the payout date is fixed. Blocker: 13-month hold plus fixed payout date is structural.",
    "R5786": "Official: $25 cash bonus for funding $1+ within 30 days of opening; exact credit timing not stated, bonus must be retained 180 days. Fastest path: fund $1 on day 1. Blocker: no published credit timeline; 180-day retention.",
    "R5787": "Official: $50 cashback deposited within 90 days after requirements are met (fund $250+ within 60 days of application). Fastest path: fund $250 on day 1. Blocker: the 90-day post-qualification credit window is structural.",
    "R5796": "Official: new-customer stocks (\u20ac5-\u20ac200 value) allocated at signup when a promotion is running; exact credit timing not stated. Fastest path: sign up while the new-customer promotion is active. Blocker: no published credit timeline \u2014 unverified speed.",
    "R5797": "Official: \u20ac10-\u20ac100 fractional share credited to your general account after onboarding + \u20ac100 deposit within 15 days; reward withdrawable 6 months after credit. Fastest path: complete onboarding and deposit \u20ac100 immediately; the share credits after the deposit posts. Blocker: no published credit bound; 6-month withdrawal lock.",
    "R5834": "Official: \u00a320-\u00a3200 investment bonus per side, claimed after the friend's qualifying \u00a3100+ investment. Fastest path: refer a friend ready to invest \u00a3100 immediately. Blocker: payout gated on the friend's timing; no published credit bound.",
    "R5835": "Official: \u20ac25 referral reward paid 6 months after the referred account opens. Fastest path: none \u2014 the 6-month wait is fixed. Blocker: 6-month post-opening payout is structural.",
    "R5836": "Official: $20 referral reward credited 30-45 days after qualification. Fastest path: refer someone who completes signup immediately; the reward posts 30-45 days later. Blocker: the 30-45 day credit window is structural.",
    "R5840": "Official: \u00a3100 Amazon gift cards emailed to both sides after the friend opens and funds/transfers \u00a310,000+ within 120 days. Fastest path: refer a friend ready to fund \u00a310k immediately; gift cards follow once funded. Blocker: the friend's \u00a310k funding (up to 120 days) gates the payout.",
    "R5844": "Official: \u00a3200 paid to the referrer after the friend opens an ii account and meets the funding criteria; no published credit bound. Fastest path: refer a friend who funds immediately. Blocker: payout gated on the friend's funding; no published timeline.",
    "R0098": "Official: $100 paid after all three qualifying steps are complete; no payout timeline published. Fastest path: complete all three steps (including the qualifying direct deposit) immediately. Blocker: no published credit timeline \u2014 unverified speed.",
    "R0100": "Official: $100 deposited within 15 business days of qualifying per the referral page (policy doc says within 30 business days). Fastest path: receive $500+ in qualifying direct deposits within 45 days of opening. Blocker: the 15-30 business-day credit bound is structural.",
    "R0103": "Official: $200 bonus applied within 60 days after meeting the conditions (open Rewards Checking Preferred + 3 debit transactions). Fastest path: open the checking account and make 3 debit transactions immediately. Blocker: the 60-day credit bound is structural.",
    "R0110": "Official (verified live 2026-09-23): reward arrives in fourteen days after the friend fulfills the criteria, but it may take up to a month; credited within 30 days after qualifying per the terms. Fastest path: the friend signs up and spends $50+ on the Venmo Debit Card on day 1; your $10 lands ~14 days later. Blocker: the 14-30 day credit bound is structural.",
    "R0115": "Official: $1,000 statement credit applied by the February 2027 statement (spend $4,000+ in the first 30 days after activation). Fastest path: activate and spend $4k in week 1. Blocker: the fixed February 2027 payout date is structural.",
    "R2682": "Official: $20 bonus credited no later than 30 calendar days after activation + $10 load are both complete. Fastest path: activate the card and load $10 on day 1. Blocker: the 30-day credit bound is structural.",
    "R0366": "BookFinder pays nothing itself \u2014 timing depends on the buyback vendor you pick from the comparison. Fastest path: compare vendors and pick the one with the fastest stated payout (many pay within days of warehouse receipt). Blocker: aggregator \u2014 timing is vendor-dependent.",
    "R0367": "Official (via Valore): payment issued within 14 business days of warehouse processing (check 7-14 business days via USPS; PayPal 2-14 business days). Fastest path: ship books immediately, choose PayPal; money ~2-4 weeks after the warehouse receives them. Blocker: warehouse processing plus the 14-business-day issue bound is structural.",
    "R0368": "Official: payment issued within 14 business days of warehouse processing; PayPal posts 2-14 business days after issue. Fastest path: ship immediately, choose PayPal \u2014 money ~2-4 weeks after warehouse receipt. Blocker: processing plus issue bounds are structural.",
    "R0369": "Official: Amazon gift card deposited after the book is received and verified by the third-party merchant. Fastest path: ship with the prepaid label the same day; the gift card posts after verification. Blocker: mail transit plus third-party verification is structural.",
    "R3501": "Official: featured competition closes ~Oct 2026 ($700k pool); prizes paid after final judging \u2014 months out. Fastest path: enter before the close date with a top-scoring solution. Blocker: fixed competition close plus judging period is structural.",
    "R3502": "Official: competition ends Dec 3, 2026 ($300k pool); prizes paid after final-round scoring. Fastest path: submit early and iterate. Blocker: fixed end date plus scoring is structural.",
    "R3503": "Official: $2,000 prize transferred via bank/PayPal after the challenge closes and winners are confirmed; no close date shown at check time. Fastest path: confirm the challenge is still open, submit before the deadline. Blocker: competition close plus winner confirmation is structural.",
    "R3504": "Official: in-person event Oct 9-11, 2026 in Tempe, AZ ($6,300 pool); prizes awarded at/after the event. Fastest path: attend and place. Blocker: fixed event dates are structural.",
    "R3505": "Official: ongoing bug-bounty program; rewards ($1k-$50k in USDC) paid after report triage, validation, and fix \u2014 typically weeks to months. Fastest path: submit a high-quality PoC for an in-scope critical bug. Blocker: triage/validation timeline is structural.",
    "R3512": "Official: paid hourly ($25-$35/hr typical, $35-$50 after ~a year) for completed work; payroll cycle not stated. Fastest path: apply and start billing hours; pay follows the employer's payroll cycle. Blocker: payroll timing not published \u2014 unverified speed.",
    "R3514": "Official: paid per completed hour (from $17/hr); payment guaranteed for completed work; pay cycle not stated. Fastest path: apply, get matched, log hours. Blocker: pay cycle not published \u2014 unverified speed.",
    "R3515": "Official: payments go out every other week on Tuesday ($3-$7 per task to start). Fastest path: claim tasks daily; pay lands on the next biweekly Tuesday. Blocker: the biweekly pay cycle is structural.",
    "R3517": "Official: paid $0.25-$0.31 per productive minute (30-min minimum); pay cycle not stated. Fastest path: apply for an active program and log productive minutes. Blocker: pay cycle not published \u2014 unverified speed.",
}

# Kept routes that also get a timing refresh from today's live checks.
TIMING_REFRESH = {
    "R0110": "Reward arrives in fourteen days after the friend fulfills the criteria, but it may take up to a month; credited within 30 days after qualifying per the official terms (verified live 2026-09-23).",
}

# Credit-card offers: hard rule - do not touch.
SKIP = {"R1922", "R1923", "R1925", "R1930", "R1931"}


def main():
    moved, kept = [], []
    for rid, spec in MOVED.items():
        assert rid not in SKIP, rid
        p = os.path.join(VDIR, rid + ".json")
        d = json.load(open(p))
        d["speed"] = spec["speed"]
        if "timing" in spec:
            d["timing"] = spec["timing"]
        d["when_cash_arrives"] = spec["when_cash_arrives"]
        d["maximize"] = spec["maximize"]
        hist = d.get("speed_history") or []
        hist.append({"date": DATE, "from": "weeks", "to": spec["speed"],
                     "rationale": spec["rationale"]})
        d["speed_history"] = hist
        json.dump(d, open(p, "w"), indent=2, ensure_ascii=False)
        open(p, "a").write("\n")
        moved.append(rid)
    for rid, text in KEPT.items():
        assert rid not in SKIP, rid
        p = os.path.join(VDIR, rid + ".json")
        d = json.load(open(p))
        d["maximize"] = text
        if rid in TIMING_REFRESH:
            d["timing"] = TIMING_REFRESH[rid]
        json.dump(d, open(p, "w"), indent=2, ensure_ascii=False)
        open(p, "a").write("\n")
        kept.append(rid)

    # DB sync: speed only, per change.
    sys.path.insert(0, "/home/hatch/workspace/upmore/qa")
    from db import req
    patched = []
    for rid, spec in MOVED.items():
        st, out = req("PATCH", f"/rest/v1/routes?route_id=eq.{rid}",
                      {"speed": spec["speed"]})
        patched.append((rid, st))
        if st not in (200, 204):
            print("PATCH FAILED", rid, st, out)
    # Verify no credit-card route was touched.
    for rid in SKIP:
        st, rows = req("GET", f"/rest/v1/routes?route_id=eq.{rid}&select=route_id,speed")
        assert rows and rows[0]["speed"] == "weeks", (rid, rows)

    print("moved:", len(moved), moved)
    print("kept:", len(kept))
    print("patched:", patched)
    print("credit-card routes untouched: OK")


if __name__ == "__main__":
    main()
