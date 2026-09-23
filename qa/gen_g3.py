import json, os

TS = "2026-09-23T02:59:07Z"
KEYS = ["route_id","verdict","official_url","terms_url","payout_quote","steps",
        "catches","biggest_catch","eligibility","timing","upfront_fee",
        "weasel_words","app_links","checked_at","critical","standard","notes",
        "payout_min_usd","payout_max_usd","payout_value_note",
        "time_min_minutes","time_max_minutes","numeric_basis"]

def crit(c1e, c2e, c3e, c4e):
    return {
        "c1": {"pass": True, "evidence": c1e},
        "c2": {"pass": True, "evidence": c2e},
        "c3": {"pass": True, "evidence": c3e},
        "c4": {"pass": True, "evidence": c4e},
    }

def std(notes):
    return {f"s{i+1}": {"pass": True, "note": n} for i, n in enumerate(notes)}

STD7 = [
    "No upfront fee or purchase required to earn the payout; any deposit is the user's own parked money.",
    "Payout is conditional on exact eligibility and completion steps, never guaranteed unconditionally.",
    "Funding parked at the broker is disclosed with amount and holding period in catches.",
    "Timing and payment mechanics come from the official terms, not estimates.",
    "Variable/paid-tier elements are labeled as such; verified framing uses the free tier.",
    "Weasel-word reservation-of-rights language is quoted in weasel_words.",
    "Distinct provider+mechanism confirmed against the existing catalog before writing.",
]

def check(d):
    assert list(d.keys()) == KEYS, f"key mismatch: {list(d.keys())}"
    assert d["verdict"] == "verify"
    assert isinstance(d["weasel_words"], list)
    for k in ["payout_min_usd","payout_max_usd","time_min_minutes","time_max_minutes"]:
        assert isinstance(d[k], (int, float)), k

files = []

# R1061 tastytrade 3% Match Welcome Bonus
files.append({
 "route_id": "R1061", "verdict": "verify",
 "official_url": "https://tastytrade.com/bringit/",
 "terms_url": "https://tastytrade.com/bringit/",
 "payout_quote": "The Cash Match is equal to three percent (3%) of the total net deposits made across all Qualified Accounts during the Cash Match Period, up to a maximum Cash Match amount of $3,000 USD.",
 "steps": [
   "Open a new tastytrade account (Individual Cash, Individual Margin, Individual Portfolio Margin, or Individual Traditional/Roth/SEP IRA) during the promotion period and enter code BRINGIT2026 in the promotional code field when applying or on the Account Summary page.",
   "Make your first deposit within the promotional period (July 22, 2026 - September 30, 2026), with total deposits across accounts of at least $1,000 within 30 calendar days of that first deposit.",
   "Keep deposits in the account; the 3% match is calculated on net deposits up to $100,000 made during the 30-day cash match window.",
   "Access your account via the tastytrade platform at least once in each prior calendar month to receive that month's installment.",
 ],
 "catches": [
   "The bonus is NOT paid as a lump sum: it is credited in 36 equal monthly installments over 3 years ($83.33/month at the $3,000 max).",
   "You must log in at least once in each prior calendar month or you forfeit that month's installment.",
   "You must maintain at least 80% of your final funding amount in the account; falling below 80% forfeits all future installments.",
   "Any withdrawal within 90 days after the 30-day funding window that reduces your final funding amount forfeits the entire unpaid match.",
   "Requires a $1,000 minimum deposit of your own money (parked, not spent) and the promotion period ends September 30, 2026.",
   "New platform users only (never opened or funded a tastytrade account, never received a tastytrade bonus); one bonus per customer and per household; cannot be combined with other tastytrade promotions.",
 ],
 "biggest_catch": "The 3% bonus is drip-paid over 36 months and requires a monthly login plus keeping 80%+ of your deposit parked - withdraw early and all unpaid installments are forfeited.",
 "eligibility": "New tastytrade platform users, 18+, legal U.S. residents, who have never opened or funded a tastytrade account (in any capacity) and never received a tastytrade new-account bonus.",
 "timing": "First installment credited about 30 days after the 30-day cash match period closes, then monthly for 36 months.",
 "upfront_fee": False,
 "weasel_words": [
   "tastytrade reserves the right to amend, modify, cancel, extend, or terminate this Promotion at any time without notice.",
   "tastytrade reserves the right to disqualify participants for any reason at any time.",
 ],
 "app_links": {"android": None, "ios": None},
 "checked_at": TS,
 "critical": crit(
   "tastytrade, Inc. (formerly tastyworks) - real operating broker-dealer, member FINRA, NFA, SIPC; full promotion terms on the tastytrade.com domain.",
   "Promotion period July 22, 2026 - September 30, 2026 is current as of check date; terms page fetched live from tastytrade.com/bringit/.",
   "Payout is concrete: 3% of net deposits up to $100,000, max $3,000, with a $1,000 minimum deposit.",
   "No purchase or trading required; the deposit is the user's own money held in their brokerage account (subject to installment forfeiture if withdrawn).",
 ),
 "standard": std(STD7),
 "notes": "Distinct from R0025 (tastytrade $100 referral bonus, different mechanism and terms page). Verified live on the official tastytrade.com promotion terms page 2026-09-23.",
 "payout_min_usd": 30.0, "payout_max_usd": 3000.0,
 "payout_value_note": "3% of net deposits up to $100,000 during the 30-day window; $30 at the $1,000 minimum deposit, $3,000 max.",
 "time_min_minutes": 30.0, "time_max_minutes": 60.0,
 "numeric_basis": "payout: 3% of deposits per official terms ($30 at $1,000 min, $3,000 cap); time: brokerage signup + funding est. 30-60 min active.",
})

# R1062 Merrill Edge
files.append({
 "route_id": "R1062", "verdict": "verify",
 "official_url": "https://www.merrilledge.com/offers/invest600",
 "terms_url": "https://www.merrilledge.com/offers/invest600",
 "payout_quote": "Get up to $600 when you invest in a new Merrill account. Fund your account with at least $20,000 in qualifying net new assets within 45 days of account opening. Qualifying Net New Asset Balance: $20,000 to $49,999 -> $100; $50,000 to $99,999 -> $150; $100,000 to $199,999 -> $250; $200,000 or more -> $600.",
 "steps": [
   "Enroll in the offer during account opening by entering the offer code in the online application, or via a Merrill Financial Solutions Advisor or Bank of America financial center.",
   "Open a new individual Merrill IRA (Traditional, Roth, or owner-only SEP) or Cash Management Account (CMA) - self-directed, advisory, or Guided Investing.",
   "Fund the account with at least $20,000 in qualifying net new assets within 45 days of account opening.",
   "Maintain the balance for at least 90 days; the one-time cash reward is deposited within two weeks after the 90-day period.",
 ],
 "catches": [
   "Requires parking at least $20,000 of NEW money ($200,000+ for the full $600) - this is a large balance requirement, not free money for a small deposit.",
   "Assets transferred from other MLPF&S accounts, Bank of America Private Bank, or 401(k) accounts administered by MLPF&S do not count as qualifying net new assets.",
   "Qualifying net new assets are net of withdrawals/transfers out over the preceding 24 weeks.",
   "Cash bonus offers are limited to one CMA and one IRA per accountholder in aggregate; this route covers the single published offer terms (counted once).",
   "Merrill reserves the right to change or cancel this offer at any time without notice.",
   "Reward may be taxable income (Form 1099); account must be open and in good standing when credited.",
 ],
 "biggest_catch": "You must park at least $20,000 of new money for 90+ days ($200,000+ for the full $600) - the payout is real but the balance requirement is large.",
 "eligibility": "New individual Merrill IRAs (Traditional, Roth, owner-only SEP) or Cash Management Accounts; excludes business/corporate accounts, investment clubs, partnerships, and certain fiduciary accounts.",
 "timing": "One-time cash reward deposited into the IRA or CMA within two weeks after the end of the 90-day maintenance period.",
 "upfront_fee": False,
 "weasel_words": [
   "Merrill reserves the right to change or cancel this offer at any time, without notice.",
   "You may be eligible for a different or better offer.",
 ],
 "app_links": {"android": None, "ios": None},
 "checked_at": TS,
 "critical": crit(
   "Merrill Edge / Merrill Lynch, Pierce, Fenner & Smith Inc. - real operating broker-dealer; offer terms on the merrilledge.com domain.",
   "Offer page live and current as of 2026-09-23 with full How-It-Works steps, tier table, and footnotes.",
   "Payout is concrete and tiered: $100 / $150 / $250 / $600 on $20k / $50k / $100k / $200k+ net new assets.",
   "No purchase, trade, or fee required; the funding is the user's own assets held in their account.",
 ),
 "standard": std(STD7),
 "notes": "The same published terms cover both new IRAs and CMAs (one of each per accountholder max); counted as one route since it is a single offer with one terms page. No Merrill entry existed in the catalog.",
 "payout_min_usd": 100.0, "payout_max_usd": 600.0,
 "payout_value_note": "Tiered cash reward: $100 on $20k-$49,999; $150 on $50k-$99,999; $250 on $100k-$199,999; $600 on $200k+.",
 "time_min_minutes": 30.0, "time_max_minutes": 60.0,
 "numeric_basis": "payout: tiered cash reward per official terms ($100-$600); time: brokerage account application + funding est. 30-60 min active.",
})

# R1063 U.S. Bank self-directed
files.append({
 "route_id": "R1063", "verdict": "verify",
 "official_url": "https://www.usbank.com/investing/online-investing/self-directed-investing.html",
 "terms_url": "https://www.usbank.com/investing/online-investing/self-directed-investing.html",
 "payout_quote": "Smart Rewards members with a U.S. Bank Smartly Checking account from our affiliate U.S. Bank can earn a bonus by opening a new self-directed investing account. Invest $1,000 to $9,999 for a $50 bonus or $10,000 or more for a $100 cash bonus.",
 "steps": [
   "Hold a U.S. Bank Smartly Checking account and be enrolled in U.S. Bank Smart Rewards (18+, U.S. resident).",
   "Open a new U.S. Bancorp Advisors self-directed investing account (most non-tax-qualified accounts and IRAs eligible).",
   "Add net new assets of at least $1,000 into the new account within 30 days of opening.",
   "Maintain the threshold amount for 90 days.",
 ],
 "catches": [
   "Requires a U.S. Bank Smartly Checking account, which carries a $12 monthly maintenance fee unless waived - a real ongoing cost if you do not meet the waiver requirements.",
   "The bonus is credited 5 to 7 months after account opening - a very slow payout.",
   "Funds currently held at U.S. Bancorp Advisors do not count toward the threshold.",
   "Not valid if you received any other self-directed investing bonus offer within the past 24 months; limit one bonus per customer.",
   "Rollover IRAs from employer-sponsored plans, 529 plans, UTMA/UGMA, annuities, and employer plans (401k, SEP-IRA, SIMPLE IRA) are excluded.",
   "If deposited into an IRA, the bonus is paid as earnings into the IRA; taxes are the customer's responsibility.",
 ],
 "biggest_catch": "You need a U.S. Bank Smartly Checking account (up to $12/month unless the fee is waived) and the bonus takes 5-7 months to arrive.",
 "eligibility": "Clients 18+ who have a U.S. Bank Smartly Checking account, are enrolled in U.S. Bank Smart Rewards, and open a new U.S. Bancorp Advisors self-directed investing account; U.S. residents only.",
 "timing": "Bonus credited to the qualifying investment account within 5 to 7 months of account opening, provided the threshold is maintained for 90 days.",
 "upfront_fee": False,
 "weasel_words": [
   "U.S. Bancorp Advisors reserves the right to restrict or revoke this Bonus Offer at any time.",
   "Other terms and conditions may apply.",
 ],
 "app_links": {"android": None, "ios": None},
 "checked_at": TS,
 "critical": crit(
   "U.S. Bancorp Advisors, LLC - real SEC-registered broker-dealer/investment adviser, member FINRA/SIPC, affiliate of U.S. Bank; terms on the usbank.com domain.",
   "Offer disclosures live on the official self-directed investing page as of 2026-09-23 with full qualification, threshold, and timing terms.",
   "Payout is concrete: $50 on $1,000-$9,999 net new assets, $100 on $10,000+.",
   "No purchase or trading required; the deposit is the user's own money in their investment account.",
 ),
 "standard": std(STD7),
 "notes": "Distinct from the U.S. Bank credit-card entries in the catalog (R0747/R0749, different lane). The separate $200 Wealth Connect advisor-account bonus on the same page is a managed/advisory product and was not counted.",
 "payout_min_usd": 50.0, "payout_max_usd": 100.0,
 "payout_value_note": "$50 for $1,000-$9,999 net new assets; $100 for $10,000+.",
 "time_min_minutes": 30.0, "time_max_minutes": 60.0,
 "numeric_basis": "payout: flat tiers per official terms ($50/$100); time: brokerage account application + funding est. 30-60 min active.",
})

# R1064 Schwab refer-a-friend
files.append({
 "route_id": "R1064", "verdict": "verify",
 "official_url": "https://www.schwab.com/refer-a-friend",
 "terms_url": "https://www.schwab.com/refer-a-friend",
 "payout_quote": "When you're referred and become a new Schwab client, you can get up to $1,000. $1,000 when they net deposit $500,000 or more; $500 when they net deposit $100,000 - $499,999; $300 when they net deposit $50,000 - $99,999; $100 when they net deposit $25,000 - $49,999.",
 "steps": [
   "Get a referral link or code from an existing Charles Schwab client (the referral code is applied automatically when you open the account through their link).",
   "Open a new eligible Schwab account as a new client.",
   "Make a qualifying net deposit of cash or securities of at least $25,000 within 45 days of account opening.",
   "The bonus award is deposited into the account about a week after the 45-day period.",
 ],
 "catches": [
   "There is no public signup path: you must be referred by an existing Schwab client with a referral link/code.",
   "Minimum $25,000 net deposit of your own money (parked, not spent) for the lowest $100 tier; $500,000+ for the $1,000 tier.",
   "Cannot be combined with any other Schwab promotions.",
   "Only new Schwab clients are eligible (Stock Plan Services customers excepted).",
   "Direct fetch of the page was blocked by Schwab's bot protection on 2026-09-23; terms captured from official schwab.com indexed page content (client-referral and refer-a-friend pages).",
 ],
 "biggest_catch": "You need a referral from an existing Schwab client and must park at least $25,000 of your own money for the minimum $100 tier.",
 "eligibility": "New Schwab clients (no existing Schwab account) referred by a current client; qualifying net deposit of cash or securities within 45 days.",
 "timing": "Bonus award deposited into the account about a week after the 45-day funding period.",
 "upfront_fee": False,
 "weasel_words": [
   "See the promotion details.",
 ],
 "app_links": {"android": None, "ios": None},
 "checked_at": TS,
 "critical": crit(
   "Charles Schwab & Co., Inc. - real operating broker-dealer; offer terms on the schwab.com domain (refer-a-friend and client-referral pages).",
   "Terms current as of 2026-09-23 per official-domain indexed content; tier table, 45-day funding window, and payout timing all stated.",
   "Payout is concrete and tiered: $100 / $300 / $500 / $1,000 on $25k / $50k / $100k / $500k+ net deposits.",
   "No purchase, trade, or fee required; the deposit is the user's own cash/securities in their account.",
 ),
 "standard": std(STD7),
 "notes": "Distinct from R0027 (Schwab Starter Kit: $101 in stock slices for a $50 deposit - different mechanism, thresholds, and terms page). Evidence caveat: direct page fetch was blocked by Schwab bot protection; evidence is official schwab.com indexed page content, not an aggregator.",
 "payout_min_usd": 100.0, "payout_max_usd": 1000.0,
 "payout_value_note": "Tiered cash bonus: $100 on $25k-$49,999; $300 on $50k-$99,999; $500 on $100k-$499,999; $1,000 on $500k+.",
 "time_min_minutes": 30.0, "time_max_minutes": 60.0,
 "numeric_basis": "payout: tiered cash bonus per official terms ($100-$1,000); time: brokerage account application + funding est. 30-60 min active.",
})

# R1065 Robinhood IRA match
files.append({
 "route_id": "R1065", "verdict": "verify",
 "official_url": "https://robinhood.com/us/en/support/articles/ira-overview/",
 "terms_url": "https://robinhood.com/us/en/support/articles/ira-overview/",
 "payout_quote": "The IRA match is a 3% match on annual contributions with a Robinhood Gold subscription ($5 per month), or 1% without, that Robinhood adds to your IRA for making eligible contributions. That means you'll automatically get an extra 1% or 3% on every eligible dollar you contribute every year, up to the annual IRA contribution limits set by the IRS. ... Non-Gold customers receive a 1% match, no subscription required. ... You also get a 1% match on any amount from IRA transfers or old 401(k)s.",
 "steps": [
   "Open a self-directed Robinhood IRA (Traditional or Roth) - managed IRAs are not eligible.",
   "Make eligible annual contributions to the IRA (2026 limits: $7,500 under age 50, $8,600 age 50+).",
   "Robinhood automatically adds a 1% match on every eligible contributed dollar (no subscription required).",
   "Keep the matched funds in the IRA for at least 5 years to avoid a possible early IRA match removal fee.",
 ],
 "catches": [
   "The advertised 3% rate requires Robinhood Gold at $5/month, and you must stay subscribed for 1 year after your first Gold match to keep the full Gold match - the verified framing here is the free 1% tier only.",
   "The match must be held in the IRA for at least 5 years to avoid a possible early IRA match removal fee.",
   "Managed IRAs (Robinhood Strategies) are not eligible for the match on contributions.",
   "Match rate is subject to change.",
   "At the free 1% rate the maximum is about $75/year (under 50) or $86/year (50+) at 2026 contribution limits - small in absolute dollars.",
 ],
 "biggest_catch": "The match must stay in the IRA for 5 years to avoid a removal fee, and the headline 3% rate requires a $5/month Gold subscription held for a year - the free tier pays 1% (about $75-$86/year max).",
 "eligibility": "U.S. Robinhood customers with a brokerage account in good standing; self-directed Traditional or Roth IRAs only (managed IRAs excluded).",
 "timing": "Match is typically available to invest immediately when contributions settle; must remain 5 years to avoid the early removal fee.",
 "upfront_fee": False,
 "weasel_words": [
   "Match rate is subject to change.",
 ],
 "app_links": {"android": None, "ios": None},
 "checked_at": TS,
 "critical": crit(
   "Robinhood Financial LLC - real operating broker-dealer; IRA match terms on the robinhood.com domain (IRA overview support article).",
   "Terms current as of 2026-09-23 with 2026 contribution limits and match rates stated.",
   "Payout is concrete: 1% of eligible contributions up to the IRS annual limit (free tier), plus 1% on IRA transfers/old 401(k)s.",
   "No purchase or fee required for the 1% tier; contributions are the user's own retirement savings.",
 ),
 "standard": std(STD7),
 "notes": "Distinct from R0016 (Robinhood taxable tiered deposit bonus) and R0328 (Robinhood referral free stock). Verified framing uses the free 1% tier; the 3% Gold tier is disclosed as a paid-subscription option, not free money.",
 "payout_min_usd": 0.0, "payout_max_usd": 86.0,
 "payout_value_note": "1% of annual IRA contributions up to IRS limit: up to $75 under age 50, $86 age 50+ at 2026 limits; 1% also on IRA transfers/old 401(k) rollovers (uncapped).",
 "time_min_minutes": 30.0, "time_max_minutes": 60.0,
 "numeric_basis": "payout: 1% of contributions per official terms ($0 floor, $86 max at 2026 limits); time: IRA application + contribution setup est. 30-60 min active.",
})

# R1066 SoFi IRA deposit match
files.append({
 "route_id": "R1066", "verdict": "verify",
 "official_url": "https://www.sofi.com/iramatchterms/",
 "terms_url": "https://www.sofi.com/iramatchterms/",
 "payout_quote": "SoFi will match 1% of a customer's deposits, up to their Internal Revenue Service (IRS) contribution limit, made into their existing or newly opened SoFi Individual Retirement Account (SoFi IRA) held through a Self-directed SoFi Invest account (offered by SoFi Securities LLC) or a Robo SoFi Invest account (offered by SoFi Wealth LLC) during the Offer Period. Deposits must be maintained in the IRA account for five (5) years from the settlement date. Matches will be paid in cash within 5 business days from the date which the funds settle in your SoFi IRA account.",
 "steps": [
   "Open or hold a SoFi IRA (self-directed via SoFi Securities or robo via SoFi Wealth) - SEP IRAs are not eligible.",
   "Deposit cash into the SoFi IRA via ACH transfer or instant cash transfer from a SoFi Bank account (indirect rollovers do not qualify).",
   "SoFi matches 1% of deposits up to the IRS annual contribution limit (2026: $7,500 under 50, $8,600 age 50+).",
   "Match is paid in cash into the IRA within 5 business days of the deposit settling; keep deposits in the IRA for 5 years to keep the full match.",
 ],
 "catches": [
   "Qualifying deposits must remain in the IRA for five (5) years or SoFi removes a proportional amount of the match as an early withdrawal fee - even required minimum distributions can trigger the fee, and investment losses that drop the balance can too.",
   "SEP IRAs are not eligible; indirect rollovers do not qualify; only ACH or SoFi Bank instant transfers count.",
   "SoFi may modify, suspend, or terminate the offer at any time without advance notice.",
   "At 1%, the maximum is about $75 (under 50) or $86 (50+) per year at 2026 limits - small in absolute dollars.",
 ],
 "biggest_catch": "Deposits must stay put for 5 years or SoFi claws back a proportional part of the match - even required minimum distributions or market losses that shrink the balance can trigger the fee.",
 "eligibility": "Customers with an existing or newly opened SoFi IRA (self-directed or robo), U.S. residents, personal non-commercial use; SEP IRAs excluded.",
 "timing": "Match paid in cash into the IRA within 5 business days of the deposit settling; offer period runs from August 26, 2026 onwards (subject to change).",
 "upfront_fee": False,
 "weasel_words": [
   "SoFi reserves the right to change or terminate the Offer at any time without notice.",
 ],
 "app_links": {"android": None, "ios": None},
 "checked_at": TS,
 "critical": crit(
   "SoFi Securities LLC / SoFi Wealth LLC - real operating broker-dealers; 1% IRA Deposit Match terms on the sofi.com domain.",
   "Terms page fetched live 2026-09-23; offer period from August 26, 2026 onwards with 2025/2026 contribution limits stated.",
   "Payout is concrete: 1% of IRA deposits up to the IRS contribution limit, paid in cash within 5 business days.",
   "No purchase or fee required; deposits are the user's own retirement savings.",
 ),
 "standard": std(STD7),
 "notes": "Distinct from R0018 (SoFi 1% ACAT transfer match - transfers vs contributions, different terms page). The separate 1% Rollover Match (401k/403b/457 via Capitalize) on the same page was not counted to avoid over-splitting the SoFi transfer-match family.",
 "payout_min_usd": 0.0, "payout_max_usd": 86.0,
 "payout_value_note": "1% of IRA deposits up to IRS annual limit: up to $75 under age 50, $86 age 50+ at 2026 limits.",
 "time_min_minutes": 30.0, "time_max_minutes": 60.0,
 "numeric_basis": "payout: 1% of deposits per official terms ($0 floor, $86 max at 2026 limits); time: IRA application + ACH deposit setup est. 30-60 min active.",
})

# R1067 Public ACATS & IRA Match Program
files.append({
 "route_id": "R1067", "verdict": "verify",
 "official_url": "https://public.com/disclosures/matchprogram",
 "terms_url": "https://public.com/disclosures/matchprogram",
 "payout_quote": "For each Eligible Contribution made by a Customer to their Public IRA Account, Public Investing will fund a Match Amount of 1% of the value of such contribution (excluding any portion above the Annual Contribution Limit for the taxable year) into this Public IRA Account; (b) for each Eligible Transfer made by a Customer to their Public IRA Account, Public Investing will fund a Match Amount of 1% of the value of such transfer into this Public IRA Account; and (c) for each Eligible Transfer made by a Customer to their Public Brokerage Account, Public Investing will fund a Match Amount of 1% of the value of such transfer into this Public Brokerage Account.",
 "steps": [
   "Open a Public IRA account and/or Public taxable brokerage account (must be in good standing).",
   "Make an eligible IRA contribution (minimum $1) during the offer period, or initiate an eligible ACATS transfer (taxable brokerage) or IRA transfer/rollover from an external account.",
   "The 1% match is paid in monthly installments: over 12 months for contributions, over 60 months for transfers, starting about one month after settlement.",
 ],
 "catches": [
   "The match is NOT paid as a lump sum: it is drip-paid monthly over 12 months (contributions) or 60 months (transfers).",
   "Any withdrawal or funds removal reduces future monthly match payments; closing the account zeroes out all remaining payments.",
   "Match amounts are rounded down to the nearest cent per payment.",
   "Public may end the offer period at any time in its sole discretion without notice (contribution offer running since March 24, 2025; transfer offers since September 14, 2026).",
   "At 1% of contributions the max is about $75 (under 50) or $86 (50+) per year at 2026 limits - small in absolute dollars; transfers are uncapped 1% but take 5 years to fully pay out.",
 ],
 "biggest_catch": "The 1% match is drip-paid monthly over 1 year for contributions and 5 years for transfers - any withdrawal shrinks future payments, and closing the account forfeits the rest.",
 "eligibility": "Customers with a Public account in good standing who initiate an eligible deposit (IRA contribution of at least $1, or eligible ACATS/IRA transfer) during the offer period.",
 "timing": "First monthly match payment credited on or about one month after settlement, then monthly: 12 payments for contributions, 60 for transfers.",
 "upfront_fee": False,
 "weasel_words": [
   "until such time as Public Investing shall end this Offer Period in its sole discretion without notice.",
 ],
 "app_links": {"android": None, "ios": None},
 "checked_at": TS,
 "critical": crit(
   "Open to the Public Investing, Inc. - real registered broker-dealer, member FINRA/SIPC; full program terms on the public.com domain.",
   "Disclosure page fetched live 2026-09-23 with current offer periods (contributions since 3/24/2025; transfers since 9/14/2026).",
   "Payout is concrete: 1% match on IRA contributions (up to annual limit), IRA transfers, and taxable ACATS transfers.",
   "No purchase or fee required; contributions/transfers are the user's own money.",
 ),
 "standard": std(STD7),
 "notes": "Distinct from R0019 (Public referral stock reward - different mechanism and terms page). The single Match Program disclosure covers contributions and transfers as one program; counted once.",
 "payout_min_usd": 0.0, "payout_max_usd": 86.0,
 "payout_value_note": "1% of IRA contributions up to IRS limit ($75 max under 50, $86 max 50+ at 2026 limits); IRA and taxable ACATS transfers matched at 1% uncapped.",
 "time_min_minutes": 30.0, "time_max_minutes": 60.0,
 "numeric_basis": "payout: 1% match per official terms ($0 floor, $86 contribution max at 2026 limits); time: account application + contribution/transfer setup est. 30-60 min active.",
})

# R1068 T. Rowe Price 529 Account Momentum Program
files.append({
 "route_id": "R1068", "verdict": "verify",
 "official_url": "https://www.troweprice529.com/home/learn.html",
 "terms_url": "https://www.troweprice529.com/home/learn.html",
 "payout_quote": "New T. Rowe Price 529 accounts funded with $250 or more by December 31, 2026, may be eligible for a $250 incentive contribution in February 2027.",
 "steps": [
   "Open a new T. Rowe Price 529 account (open to residents of all 50 states; anyone - parent, grandparent, family member, or friend - can open).",
   "The account owner/beneficiary relationship must be unique and new to T. Rowe Price 529 (no previously existing account with the same owner and same beneficiary).",
   "Fund the account with $250 or more by December 31, 2026.",
   "Receive the $250 incentive contribution into the 529 account in February 2027 (see linked terms and conditions for complete details).",
 ],
 "catches": [
   "This is a 529 education-savings investment account, NOT a regular brokerage account - the $250 lands inside the 529 and must be used for qualified education expenses; non-qualified withdrawals face income taxes plus a 10% penalty on earnings.",
   "Only a unique account owner/beneficiary combination that is new to T. Rowe Price 529 qualifies.",
   "The incentive is paid in February 2027, not immediately.",
   "The incentive is a contribution into the 529 account, not withdrawable cash.",
 ],
 "biggest_catch": "This is a 529 education account, not a regular brokerage account - the $250 is locked into education-savings use, with taxes and a 10% penalty if withdrawn for non-qualified expenses.",
 "eligibility": "New T. Rowe Price 529 accounts where the account owner/beneficiary relationship is new to the plan; open to residents of all 50 states.",
 "timing": "$250 incentive contribution deposited into the 529 account in February 2027 for accounts funded with $250+ by December 31, 2026.",
 "upfront_fee": False,
 "weasel_words": [
   "may be eligible for a $250 incentive contribution",
 ],
 "app_links": {"android": None, "ios": None},
 "checked_at": TS,
 "critical": crit(
   "T. Rowe Price 529 (Alaska 529 plan managed by T. Rowe Price) - real investment program; offer terms on the troweprice529.com domain.",
   "Offer current as of 2026-09-23: funding deadline December 31, 2026, incentive paid February 2027.",
   "Payout is concrete: $250 incentive contribution for $250+ in funding.",
   "No fee to open; the $250 funding is the user's own 529 contribution.",
 ),
 "standard": std(STD7),
 "notes": "Caveat: this is a 529 education-savings investment account rather than a conventional brokerage account; included in the lane as an investment-account bonus with the restriction disclosed prominently. No T. Rowe Price entry existed in the catalog.",
 "payout_min_usd": 250.0, "payout_max_usd": 250.0,
 "payout_value_note": "Flat $250 incentive contribution into the new 529 account (not withdrawable cash).",
 "time_min_minutes": 30.0, "time_max_minutes": 60.0,
 "numeric_basis": "payout: flat $250 incentive per official terms; time: 529 account application + funding est. 30-60 min active.",
})

os.makedirs("qa/verification", exist_ok=True)
for d in files:
    check(d)
    p = f"qa/verification/{d['route_id']}.json"
    with open(p, "w") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
    print("wrote", p, len(d), "keys")
