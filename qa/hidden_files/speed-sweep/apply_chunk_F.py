#!/usr/bin/env python3
"""Chunk F speed reclassification: apply evidence JSON updates."""
import json, os

VDIR = "/home/hatch/workspace/upmore/qa/verification"
DATE = "2026-09-23"

# Routes moving weeks -> days (official terms verified)
MOVED = {
    "R0229": {
        "speed": "days",
        "timing": "Paid within a few days of study completion (official User Interviews page).",
        "when_cash_arrives": "Incentive arrives within a few days after you complete a study, delivered through Tremendous.",
        "maximize": "Apply to online studies you qualify for and complete them the same day they appear \u2014 User Interviews officially pays within a few days of each completed study, so back-to-back completions stack payouts. Fastest honest path: complete an online study today, paid within a few days.",
        "rationale": "Official User Interviews page states 'Paid within a few days of study completion' (route's own official URL).",
    },
    "R0226": {
        "speed": "days",
        "timing": "Official PlaytestCloud Tester FAQ (updated 2026-09-01): 'As long as you have completed a playtest study well, you can expect to receive the payment in up to 3 days' \u2014 paid via Tremendous (gift cards, virtual bank cards, donations, PayPal). No payout threshold.",
        "when_cash_arrives": "Within 3 days after completing a playtest well, via Tremendous email.",
        "maximize": "Fill in the 'Reward payment information' section of your profile (improves invite chances) and complete playtests well with full commentary \u2014 rewards land within 3 days of each completed test with no minimum to cash out. Tremendous sends rewards by email, so keep inbox space free.",
        "rationale": "Official PlaytestCloud Tester FAQ (updated 2026-09-01) states payment arrives 'in up to 3 days' after a well-completed playtest.",
    },
    "R0204": {
        "speed": "days",
        "timing": "Official PrizeRebel blog: Silver+ members receive rewards within a few hours; Bronze members within ~24 hours; first PayPal/Bitcoin/bank withdrawal held ~24 hours for manual verification.",
        "when_cash_arrives": "Within a few hours (Silver+ level) to ~24 hours (Bronze) after redeeming; first PayPal/Bitcoin/bank withdrawal takes ~24 hours for manual verification.",
        "maximize": "Reach Silver level for few-hour redemptions; gift cards redeem from 200 points even at Bronze. Fastest honest path: earn 500 points ($5 minimum) and redeem \u2014 payment within hours (Silver) to 24 hours (Bronze).",
        "rationale": "Official PrizeRebel company blog states Silver+ redemptions take a few hours and Bronze ~24 hours.",
    },
    "R3044": {
        "speed": "days",
        "timing": "Tango Card compensation email typically sent within 3-4 business days of participation (official Roman Family Center for Decision Research page).",
        "when_cash_arrives": "Tango Card gift-card email arrives 3-4 business days after each completed study session.",
        "maximize": "Complete the 10-15 min Zoom Prerequisite Study ($3) to join the standing pool, then take paid studies as slots open \u2014 the Tango Card email arrives 3-4 business days after each session. Note: compensation is gift cards (Tango Card), not cash.",
        "rationale": "Official Chicago Booth Roman Center page states the Tango Card compensation email is 'typically sent within 3-4 business days of participation'.",
    },
}

# Routes staying weeks: fastest honest path + blocker
KEPT = {
    "R0220": "Fastest honest path: researcher approval, then PayPal cashout is instant once you reach $6/\u00a36 and have completed 4 cashouts. Blocker: researcher approval timing is not fixed in official terms \u2014 can take days to weeks.",
    "R0221": "Official: paid ~14 days after each test via PayPal, no minimum. Fastest path: complete tests back-to-back; payouts stack on a rolling ~14-day cycle. Blocker: the 14-day window is fixed.",
    "R0223": "Approved tests pend 7 days, then payouts are handled within 5-10 business days of your request. Fastest path: request payout as soon as approved tests clear the 7-day pend. Blocker: fixed pending + processing windows.",
    "R0224": "No official payout schedule published \u2014 accounts credited after the session concludes and responses are reviewed. Fastest path: complete many short tasks; credits accrue continuously. Blocker: review/payment cycle undisclosed.",
    "R0227": "Paid via PayPal after mission review and approval \u2014 no official timeline, no minimum threshold. Fastest path: finish missions quickly and cleanly so review passes first time. Blocker: review length not stated.",
    "R0228": "Paid through Tremendous after project completion (5%/$1-min fee disclosed). Fastest path: pick projects with near-term completion dates and respond promptly after each session. Blocker: project-level payment timing not stated officially.",
    "R0230": "Paid per study after researcher approval; no fixed platform-wide schedule published. Fastest path: complete studies promptly after approval. Blocker: researcher approval timing varies per study.",
    "R0233": "Official: reward email from Tremendous within 21 days after completing the study. Fastest path: none \u2014 the 21-day window is fixed. Blocker: official 21-day window.",
    "R0240": "Rewards redeemed via Tremendous after your test report is accepted; no fixed timing promised. Fastest path: submit clean, complete reports so acceptance is not delayed. Blocker: invite volume is 0-5/month \u2014 earning, not payout speed, is the binding constraint.",
    "R0285": "Official FAQ: incentives generally appear within 2-3 weeks of study completion. Fastest path: none \u2014 fixed processing window. Blocker: official 2-3 week window.",
    "R0286": "Payment timing not stated in official terms reviewed. Blocker: undisclosed schedule \u2014 assume weeks.",
    "R0292": "Paid per completed case; payment terms disclosed per case in advance. Timing not stated in official terms. Blocker: no official fast path.",
    "R0293": "Method: PayPal or check (official FAQ); exact payout timing not stated. Blocker: undisclosed schedule.",
    "R1331": "Fixed session Thursday Sept 24, 2026, 9am-1pm CT; payment method/timing not stated on the listing. Blocker: one-time event + undisclosed pay timing.",
    "R1371": "Official: payments issued 'as soon as a study has concluded,' via check or electronically. Fastest path: choose electronic payment over check. Blocker: no numeric timeline stated; checks take weeks.",
    "R1372": "Incentive paid per study; method/timing not stated on the official page. Blocker: undisclosed schedule.",
    "R1373": "Points credited per project; cash out at 1,000+ points; paid by check or PayPal within 6-8 weeks after validation (validation up to 30 days). Blocker: structural \u2014 validation plus processing takes weeks by design.",
    "R1374": "Official: incentive email within one to two weeks after study completion, via Tremendous. Fastest path: choose digital gift card in the email; in-person sessions sometimes pay on the spot (in-person). Blocker: 1-2 week email window for remote studies.",
    "R3046": "Paid via BruinCard deposit (UCLA affiliates) or Amazon.com gift certificate by email (non-UCLA). Timing not stated officially. Blocker: undisclosed processing.",
    "R3049": "Official FAQ: compensation provided at checkout after the study. Fastest path: in-lab studies pay at checkout same-day \u2014 but in-lab is IN-PERSON. Online/virtual study payment timing is per-study and not stated. Blocker: this route bundles in-person lab studies with online ones; online timing undisclosed.",
    "R4517": "Longitudinal study: baseline $20 at start, daily surveys over 3 weeks, follow-ups at 1 and 3 months; gift-card delivery timing not stated. Blocker: structural \u2014 earnings spread over months by study design.",
    "R6603": "Official FAQ: paid via PayPal or bank transfer within 10 business days of the completed study. Fastest path: none \u2014 fixed 10-business-day window. Blocker: official window.",
    "R7106": "Paid once monthly via direct deposit or PayPal for all completed/approved shops. Fastest path: choose direct deposit (free; PayPal has a $1 fee). Blocker: structural monthly pay cycle.",
    "R0295": "Search is instant; claiming runs through each state's official program, commonly weeks to months. Fastest path: file a complete claim with ID/ownership proof immediately \u2014 some states process small electronic claims faster. Blocker: state processing.",
    "R0296": "Search is instant. Claim processing is per-state \u2014 typically weeks to a few months after you submit proof of identity and ownership. Blocker: state review.",
    "R0298": "Search is instant; benefit verification and payout are per-case through PBGC. Blocker: federal verification timeline.",
    "R0299": "Search is instant; claims filed with the FDIC claim form and verified per case. Blocker: federal verification.",
    "R0300": "Search is instant; claims go through the Member Verification Form (mail or amacmail@ncua.gov), per-case timing. Blocker: agency review.",
    "R0301": "E-filed direct-deposit refunds typically arrive in about 21 days (paper returns ~4 weeks). Fastest path: e-file with direct deposit. Blocker: IRS processing window is fixed.",
    "R0302": "Payouts arrive months after the final court approval hearing. Fastest path: none. Blocker: legal process \u2014 structural.",
    "R0303": "Claims must be filed before each settlement's hard deadline; payouts arrive months after. Fastest path: file immediately on open settlements. Blocker: settlement distribution schedule \u2014 structural.",
    "R0306": "Complaint filing is immediate online; mediation outcomes and multistate-settlement payouts are slow (years). Fastest path: none. Blocker: legal process \u2014 structural.",
    "R0307": "Per-case: notice of distribution plan, ~30-day comments, approval, claims bar date \u2014 distributions often come years after enforcement. Blocker: legal process \u2014 structural.",
    "R0308": "Search is instant; remedies follow each recall notice \u2014 often a return to the store where purchased (same-day refund possible) or direct contact with the manufacturer, usually no receipt needed. Blocker: remedy varies per recall; no guaranteed payout amount.",
    "R0309": "Search is instant; CPSC posts recalls in weekly batches; remedy timing follows each recall notice. Blocker: per-recall remedy.",
    "R1650": "Paid after Election Day service and qualifying training, per county payroll. Fastest path: complete training (paid training stipend where offered). Blocker: county payroll cycles \u2014 paid after the election, structural.",
    "R1651": "Paid per day served during the election period, per county payroll. Blocker: payroll after the election \u2014 structural.",
    "R1652": "Paid after the election for the full assignment, per county payroll. Blocker: payroll after the election \u2014 structural.",
    "R1655": "Paid after the election; $50 training pay for required class. Fastest path: attend the paid training. Blocker: payroll after the election \u2014 structural.",
    "R1656": "Paid for the election ($300/day per NJ statute A-208, 2022), per county payroll. Blocker: payroll after the election \u2014 structural.",
    "R1657": "Paid after the election, per county payroll. Blocker: payroll after the election \u2014 structural.",
    "R1658": "Paid after the election per county payroll. Blocker: payroll after the election \u2014 structural.",
    "R1659": "Paid after the election, per county payroll. Blocker: payroll after the election \u2014 structural.",
    "R0187": "Official page does not state processing time; third-party sources report ~1-2 business days. Fastest path per third-party reports: cash out once threshold met. Blocker: no official timing \u2014 unverified.",
    "R0189": "$5 added to balance per 5 completed surveys; redemption via PayPal/gift cards. Exact processing time not stated officially. Blocker: undisclosed.",
    "R0192": "Official: $3 minimum cashout, low thresholds so you get paid quicker; official site does not state transfer timing. Third-party reports: PayPal usually within minutes, up to 72 hours if verification required. Blocker: official timing unstated.",
    "R0196": "Payment requestable once minimum reached ($15 blog / $30 Terms of Use \u2014 confirm in account); PayPal and gift cards supported. Timing not stated officially. Blocker: undisclosed.",
    "R0198": "Official blog: PayPal transfers take 3-10 business days. Fastest path: redeem as soon as the threshold is met \u2014 often arrives in 3-5 business days. Blocker: up to 10 business days by official terms.",
    "R0201": "Redeemable once points threshold reached; voucher claim instructions emailed after redemption. Timing not stated officially. Blocker: undisclosed.",
    "R0206": "Official: cashouts processed in up to 10 business days (up to 15 for new accounts or first cashout); max 2 cashouts/day. Fastest path: none for new accounts. Blocker: fixed processing window + new-account delay.",
    "R0209": "Not stated on the official site; third-party sources report payout within 72 hours of request. Blocker: official timing unstated \u2014 unverified.",
    "R0215": "Paid monthly or per project once payment-cycle minimums are met. Fastest path: none. Blocker: structural monthly pay cycle.",
    "R0216": "First payout 3-6 weeks (address PIN verification); later withdrawals faster; $9+ fees ($20 + 5% for Payoneer). Fastest path: verify your address PIN immediately on signup. Blocker: structural \u2014 PIN verification for first payout.",
}

def main():
    moved, kept = [], []
    for rid, spec in MOVED.items():
        p = os.path.join(VDIR, rid + ".json")
        d = json.load(open(p))
        d["speed"] = spec["speed"]
        d["timing"] = spec["timing"]
        d["when_cash_arrives"] = spec["when_cash_arrives"]
        d["maximize"] = spec["maximize"]
        hist = d.get("speed_history", [])
        hist.append({"date": DATE, "from": "weeks", "to": spec["speed"], "rationale": spec["rationale"]})
        d["speed_history"] = hist
        json.dump(d, open(p, "w"), indent=2, ensure_ascii=False)
        open(p, "a").write("\n")
        moved.append(rid)
    for rid, text in KEPT.items():
        p = os.path.join(VDIR, rid + ".json")
        d = json.load(open(p))
        d["maximize"] = text
        json.dump(d, open(p, "w"), indent=2, ensure_ascii=False)
        open(p, "a").write("\n")
        kept.append(rid)
    print("moved:", moved)
    print("kept:", len(kept))

if __name__ == "__main__":
    main()
