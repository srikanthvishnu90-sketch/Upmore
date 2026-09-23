#!/usr/bin/env python3
"""Write G29 verification JSONs R3441-R3446 (exactly 23 top-level keys each)."""
import json, sys

UTC = "2026-09-23T04:08:30Z"

def base(route_id, **kw):
    d = {
        "app_links": {"android": None, "ios": None},
        "biggest_catch": "",
        "catches": [],
        "checked_at": UTC,
        "critical": {"c1": {"evidence": "", "pass": True}, "c2": {"evidence": "", "pass": True},
                     "c3": {"evidence": "", "pass": True}, "c4": {"evidence": "", "pass": True}},
        "eligibility": "",
        "notes": "",
        "official_url": "",
        "payout_quote": "",
        "route_id": route_id,
        "standard": {"s1": {"note": "", "pass": True}, "s2": {"note": "", "pass": True},
                     "s3": {"note": "", "pass": True}, "s4": {"note": "", "pass": True},
                     "s5": {"note": "", "pass": True}, "s6": {"note": "", "pass": True},
                     "s7": {"note": "", "pass": True}},
        "steps": [],
        "terms_url": "",
        "timing": "",
        "upfront_fee": False,
        "verdict": "verify",
        "weasel_words": [],
        "payout_min_usd": 0.0,
        "payout_max_usd": 0.0,
        "payout_value_note": "",
        "time_min_minutes": 0.0,
        "time_max_minutes": 0.0,
        "numeric_basis": "",
    }
    d.update(kw)
    assert len(d) == 23, (route_id, len(d))
    assert set(d["standard"].keys()) == {f"s{i}" for i in range(1, 8)}
    assert set(d["critical"].keys()) == {f"c{i}" for i in range(1, 5)}
    assert isinstance(d["weasel_words"], list)
    return d

routes = []

# R3441 PacketStream bandwidth sharing
routes.append(base("R3441",
    biggest_catch="Tiny earnings for most users: $0.10/GB means you must share 100 GB to reach the $5 cashout, and buyer demand for your connection determines whether traffic flows at all. Third-party customers' traffic exits under your home IP address, and sharing may violate your ISP terms or consume data caps.",
    catches=[
        "Earnings are usage-based: $0.10 per GB of customer traffic routed through your connection (official: 'earn $0.10 for every GB'). No traffic demand, no earnings.",
        "Minimum cashout is $5, processed within one week; a 3% PacketStream processing fee applies and PayPal may charge additional fees.",
        "You grant customers' traffic access to your internet connection - residential IP exposure, privacy risk, ISP terms-of-service risk, and data-cap/electricity costs.",
        "Most users earn only small amounts; reaching even the $5 minimum can take a long time on a typical connection.",
    ],
    critical={
        "c1": {"pass": True, "evidence": "packetstream.io is the provider's official domain; the 'Share your bandwidth' page (https://packetstream.io/share-bandwidth/) states the rate, currency, minimum payout, timing, and fee in the provider's own words."},
        "c2": {"pass": True, "evidence": "Catalog claim: earn money sharing unused bandwidth at $0.10/GB with $5 minimum cashout via PayPal. Official page matches on every point: $0.10/GB, USD through PayPal, $5 minimum, processed within one week, 3% processing fee."},
        "c3": {"pass": True, "evidence": "No signup fee. Costs disclosed on the official page: 3% PacketStream processing fee on payouts, plus possible PayPal fees. Bandwidth/electricity/ISP-data-cap costs are real but disclosed here as catches."},
        "c4": {"pass": True, "evidence": "Official page states: 'earn $0.10 for every GB' and 'all payouts are made in USD through PayPal' with a '$5 minimum cashout' 'processed within one week'. Concrete per-unit rate, threshold, method, and timing."},
    },
    eligibility="Users with a Windows, macOS, or Linux device and an internet connection; customer traffic routes through the user's connection.",
    notes="Verified against official packetstream.io share-bandwidth page on 2026-09-23. Browser page-fetch was unavailable this session; evidence rests on the provider's own domain content via search snippets. No upstream demand means no earnings - most earners get very little. Framed as selling residential bandwidth with IP/ISP/privacy tradeoffs, not passive income.",
    official_url="https://packetstream.io/share-bandwidth/",
    payout_quote="earn $0.10 for every GB; all payouts are made in USD through PayPal; $5 minimum cashout processed within one week; 3% PacketStream processing fee",
    standard={
        "s1": {"pass": True, "note": "Eligibility: Windows/macOS/Linux users with an internet connection; customer traffic routes through the user's connection. Clear from official page."},
        "s2": {"pass": True, "note": "Payout mechanics stated: USD through PayPal, $5 minimum, 3% processing fee (PayPal may charge more)."},
        "s3": {"pass": True, "note": "Payout timing stated: processed within one week of request."},
        "s4": {"pass": True, "note": "Core money claims are exact figures ($0.10/GB, $5 minimum) - no vague promotional multiplier on the payout amount."},
        "s5": {"pass": False, "note": "packetstream.io pages not loadable via page fetch this session; official-domain content reached via search snippets."},
        "s6": {"pass": True, "note": "Steps are concrete and grounded in official instructions: install, run, cash out at $5."},
        "s7": {"pass": True, "note": "Checked 2026-09-23."},
    },
    steps=[
        "Sign up for a PacketStream account and install the app on Windows, macOS, or Linux.",
        "Keep the app running; customer traffic is routed through your internet connection and you earn $0.10 per GB shared.",
        "Accumulate at least $5 in earnings.",
        "Request a PayPal payout in USD; it is processed within one week (minus the 3% PacketStream processing fee and any PayPal fees).",
    ],
    terms_url="https://packetstream.io/share-bandwidth/",
    timing="Payouts requested at the $5 minimum are processed within one week via PayPal.",
    upfront_fee=False,
    weasel_words=["passive"],
    payout_min_usd=0.10, payout_max_usd=0.10,
    payout_value_note="official per-unit rate $0.10 per GB shared; $5 minimum cashout",
    time_min_minutes=10.0, time_max_minutes=20.0,
    numeric_basis="payout: official $0.10/GB rate; time: active setup (install + account) estimate 10-20 min, earnings accrue passively thereafter",
))

# R3442 Honeygain bandwidth sharing
routes.append(base("R3442",
    biggest_catch="Very slow to real money: at the official 10 GB = $1 rate, reaching the $20 payout threshold takes most users months, and payouts are PayPal only. Earnings depend entirely on demand for your location and connection - you are selling your residential IP/bandwidth to third-party businesses.",
    catches=[
        "Official rate: one credit per 10 MB, and the official FAQ restates it as 10 GB = $1 (credits convert 1:1 to cents). One indexed official blog sentence appears to contain a typo saying one credit is 'worth $0.1' - the internally consistent official figure is 10 GB = $1, disclosed here.",
        "$20 minimum payout through PayPal; most users report taking months to reach it.",
        "You share your connection with business customers; IP/privacy exposure, ISP terms risk, data caps, and electricity costs apply.",
        "Earnings vary sharply by country/location and device uptime; most earners get very little.",
    ],
    critical={
        "c1": {"pass": True, "evidence": "honeygain.com is the provider's official domain; the official blog article and FAQ state the credit rate (one credit per 10 MB, 10 GB = $1) and the $20 PayPal minimum payout."},
        "c2": {"pass": True, "evidence": "Catalog claim: earn credits for sharing bandwidth, $20 PayPal minimum. Official sources match: 1 credit per 10 MB, 10 GB = $1, $20 minimum payout through PayPal."},
        "c3": {"pass": True, "evidence": "No signup fee. Costs are the user's own bandwidth/electricity/data caps; disclosed here as catches. No hidden provider fee stated."},
        "c4": {"pass": True, "evidence": "Concrete official figures: one credit per 10 MB shared; official FAQ restates 10 GB = $1; $20 minimum payout via PayPal."},
    },
    eligibility="Users who can install the Honeygain app; availability and rates vary by country and network.",
    notes="Verified against official honeygain.com blog/FAQ content on 2026-09-23. Browser page-fetch unavailable this session; evidence rests on provider-domain content via search snippets. Note the apparent typo in one official blog sentence ('worth $0.1' per credit) - verified against the internally consistent FAQ quote (10 GB = $1) and disclosed as a caveat. Slow, variable passive earning; most users get little.",
    official_url="https://www.honeygain.com/blog/why-honeygain-is-the-ultimate-free-money-deal/",
    payout_quote="one credit for every 10 MB of data shared; FAQ: 10 GB shared = 1 USD; $20 minimum payout through PayPal",
    standard={
        "s1": {"pass": True, "note": "Eligibility: anyone able to install the app; rates vary by country/network per official FAQ."},
        "s2": {"pass": True, "note": "Payout mechanics stated: credits, $20 minimum, PayPal payout."},
        "s3": {"pass": False, "note": "Payout processing timing not stated in the indexed official content."},
        "s4": {"pass": True, "note": "Rate figures are exact (10 MB per credit, 10 GB = $1); the blog typo is disclosed rather than hidden."},
        "s5": {"pass": False, "note": "honeygain.com pages not loadable via page fetch this session; official-domain content reached via search snippets."},
        "s6": {"pass": True, "note": "Steps concrete: install, run, accumulate, cash out at $20."},
        "s7": {"pass": True, "note": "Checked 2026-09-23."},
    },
    steps=[
        "Create a Honeygain account and install the app on your device.",
        "Keep the app running; you earn one credit per 10 MB of shared bandwidth (official FAQ: 10 GB = $1).",
        "Accumulate at least $20 in earnings.",
        "Request payout through PayPal once the $20 minimum is reached.",
    ],
    terms_url="https://www.honeygain.com/blog/why-honeygain-is-the-ultimate-free-money-deal/",
    timing="Payout available once the $20 minimum is reached; processing timing not stated in official content.",
    upfront_fee=False,
    weasel_words=["free money", "passive"],
    payout_min_usd=1.0, payout_max_usd=1.0,
    payout_value_note="official rate equivalent: $1 per 10 GB shared (10 MB per credit); $20 minimum payout",
    time_min_minutes=10.0, time_max_minutes=20.0,
    numeric_basis="payout: official 10 GB = $1 equivalent; time: active setup (install + account) estimate 10-20 min, earnings accrue passively thereafter",
))

# R3443 IZEA creator marketplace
routes.append(base("R3443",
    biggest_catch="Variable marketplace income: the $50 figure is a floor on the price you can ask, not a guaranteed payment. You only get paid if a brand buys your listing, accepts your offer, and approves your delivered content - most creators get few or no orders.",
    catches=[
        "Creators create free listings and set their own price, but listings cannot be under $50 (official: 'set your price (minimum $50)').",
        "Payment is per completed brand deal via PayPal: buyer purchases, creator accepts, delivers content, buyer approves, then the creator is paid.",
        "No earnings without brand demand - selection, niche, audience size, and competition determine outcomes; most earners get little.",
        "IZEA states it never charges creators to participate and never pays in crypto (official anti-scam guidance) - disclosed as consumer protection.",
    ],
    critical={
        "c1": {"pass": True, "evidence": "izea.com is the provider's official domain; the official 'why join influencer marketplace' resource states free listings, creator-set pricing with a $50 minimum, the buy-accept-deliver-approve-pay workflow, and PayPal payment."},
        "c2": {"pass": True, "evidence": "Catalog claim: creators list services for brands and get paid per sponsored content deal. Official page matches: free listings, set your price (min $50), buyer purchases, creator accepts and delivers, buyer approves, creator paid via PayPal."},
        "c3": {"pass": True, "evidence": "Free to join and list; IZEA officially states it never charges creators to participate. No upfront fee."},
        "c4": {"pass": True, "evidence": "Concrete official figures: minimum listing price $50; per-deal payment flow ending in PayPal payout. Earnings are variable by design - honestly framed with 0/0 numeric."},
    },
    eligibility="Content creators who can create a free IZEA marketplace listing.",
    notes="Verified against official izea.com resources on 2026-09-23. Browser page-fetch unavailable this session; evidence rests on provider-domain content via search snippets. This is a distinct route from the rejected R0260 (discontinued TapInfluence). Earnings are fully variable: the $50 is a price floor, not a payout guarantee.",
    official_url="https://izea.com/resources/why-join-influencer-marketplace/",
    payout_quote="create free listings; set your price (minimum $50); buyer purchases, creator accepts, creates and delivers content, buyer approves, creator is paid through PayPal",
    standard={
        "s1": {"pass": True, "note": "Eligibility: creators; free listings; no follower minimum stated in indexed content."},
        "s2": {"pass": True, "note": "Payout mechanics stated: per-deal payment via PayPal after buyer approval of delivered content."},
        "s3": {"pass": False, "note": "Payment processing timing after approval not stated in indexed official content."},
        "s4": {"pass": True, "note": "Core claim is honestly variable; no guaranteed-earnings language on the official page."},
        "s5": {"pass": False, "note": "izea.com pages not loadable via page fetch this session; official-domain content reached via search snippets."},
        "s6": {"pass": True, "note": "Steps concrete: create listing, set price >= $50, accept orders, deliver, get paid on approval."},
        "s7": {"pass": True, "note": "Checked 2026-09-23."},
    },
    steps=[
        "Sign up as a creator on the IZEA Creator Marketplace and create a free listing for your sponsored-content service.",
        "Set your own price, with a minimum of $50 per listing.",
        "When a buyer purchases, accept the offer and create/deliver the agreed content.",
        "Once the buyer approves the delivered content, receive payment through PayPal.",
    ],
    terms_url="https://izea.com/resources/why-join-influencer-marketplace/",
    timing="Payment follows buyer approval of delivered content; exact processing time not stated officially.",
    upfront_fee=False,
    weasel_words=[],
    payout_min_usd=0.0, payout_max_usd=0.0,
    payout_value_note="variable marketplace: no fixed payout; provider states creators set own price with $50 minimum listing price - earnings not guaranteed",
    time_min_minutes=60.0, time_max_minutes=240.0,
    numeric_basis="payout: no parseable guaranteed amount; variable; time: listing setup ~60 min, sponsored deliverable work varies 1-4+ hours per order",
))

# R3444 TraffMonetizer affiliate program
routes.append(base("R3444",
    biggest_catch="You earn only from other people's payouts: 10% of each payout your referrals request, so with no active referrals you earn nothing. Referral bases are tiny - most affiliates earn little. Payouts are in USDT (crypto) TRC20 or wire transfer for $1,000+, not cash/bank.",
    catches=[
        "Official: 'we're paying you 10% from all the payouts we made to the end-customer that you attracted' - two balances: withheld (10% of referral account amounts) and actual withdrawable (10% of payouts referrals requested).",
        "Each referred user gets a $5 signup bonus, which adds $0.50 to the referrer (10% of $5) per official affiliate listing.",
        "Minimum payout $10, paid within 48 hours after request; payout methods are USDT TRC20 or wire transfer ($1,000+).",
        "Official says 'It should take less than a month for a user to reach the minimum $10 payout' - affiliate earnings depend entirely on referrals reaching payout.",
    ],
    critical={
        "c1": {"pass": True, "evidence": "traffmonetizer.com is the provider's official domain; the official 'For affiliates' page (https://traffmonetizer.com/for-affiliates/) states the 10% commission, the two-balance system, the $5 referral signup bonus, the $10 minimum payout, 48h payments, and payout methods."},
        "c2": {"pass": True, "evidence": "Catalog claim: earn 10% lifetime commission on referrals' payouts with $10 minimum. Official page matches: 10% of all payouts made to attracted end-customers, $10 minimum, 48h payments."},
        "c3": {"pass": True, "evidence": "No signup fee for the affiliate program. No provider fee on affiliates stated."},
        "c4": {"pass": True, "evidence": "Concrete official figures: 10% commission on referrals' requested payouts, $0.50 per referred signup bonus, $10 minimum payout, 48h payment processing. Earnings variable by design - honestly framed with 0/0 numeric."},
    },
    eligibility="Anyone who signs up for a free TraffMonetizer account and obtains a unique affiliate link.",
    notes="Verified against official traffmonetizer.com/for-affiliates/ on 2026-09-23. Browser page-fetch unavailable this session; evidence rests on provider-domain content via search snippets. This is the affiliate/referral mechanism only - the bandwidth-sharing route itself is rejected separately (no official unit rate). Payouts in USDT TRC20 crypto.",
    official_url="https://traffmonetizer.com/for-affiliates/",
    payout_quote="paying you 10% from all the payouts we made to the end-customer that you attracted; $5 sign-up bonus per referred user ($0.5 for referrer); minimum payout $10; 48h payments after payout is requested",
    standard={
        "s1": {"pass": True, "note": "Eligibility: free account signup; share unique affiliate link on website/social networks."},
        "s2": {"pass": True, "note": "Payout mechanics stated: actual balance = 10% of payouts referrals requested; USDT TRC20 or wire ($1,000+)."},
        "s3": {"pass": True, "note": "Payout timing stated: 48h payments after payout is requested."},
        "s4": {"pass": True, "note": "Core claim is a fixed 10% commission - exact, not weasel-worded."},
        "s5": {"pass": False, "note": "traffmonetizer.com pages not loadable via page fetch this session; official-domain content reached via search snippets."},
        "s6": {"pass": True, "note": "Steps concrete: sign up, get link, share, earn 10% of referrals' requested payouts."},
        "s7": {"pass": True, "note": "Checked 2026-09-23."},
    },
    steps=[
        "Sign up for a free TraffMonetizer account to obtain your unique affiliate link.",
        "Share the link on your website or social networks; each signup through it gets a $5 bonus (adding $0.50 to your balance).",
        "Earn 10% of every payout your referrals request, credited to your actual (withdrawable) balance.",
        "Request payout once your balance reaches $10; paid within 48 hours via USDT TRC20 (or wire transfer for $1,000+).",
    ],
    terms_url="https://traffmonetizer.com/for-affiliates/",
    timing="48h payments after payout is requested, once the $10 minimum is reached.",
    upfront_fee=False,
    weasel_words=[],
    payout_min_usd=0.0, payout_max_usd=0.0,
    payout_value_note="variable: 10% of each referred user's requested payout + $0.50 per referred signup; no fixed personal payout - depends on referral activity",
    time_min_minutes=30.0, time_max_minutes=120.0,
    numeric_basis="payout: no parseable guaranteed amount; variable; time: signup + promotion effort varies 30 min-2+ hours before any earnings",
))

# R3445 Userfeel usability testing
routes.append(base("R3445",
    biggest_catch="Test availability is the bottleneck: tests are assigned only if you match each client's specific demographics, and testers report getting anywhere from several tests a day to none for a year. You are not paid for the unpaid qualification test or for tests that fail approval.",
    catches=[
        "Official: 'Become a tester of websites and apps and earn $3 - $30 per test'; each test lasts 5 to 60 minutes; 'Most tests are 20 minutes where you earn $10'.",
        "Tests (including referral tests) are only assigned if you match the client's specific demographic criteria.",
        "You must watch the training video and read the FAQ or you will not get paid; payment follows approval, about one week after the test, to the Userfeel wallet, transferable to PayPal.",
        "Paid work depends entirely on client demand matching your profile; most testers get few tests.",
    ],
    critical={
        "c1": {"pass": True, "evidence": "userfeel.com is the provider's official domain; the official Tester FAQ (https://www.userfeel.com/tester-faq) states the $3-$30 per-test range, the 5-60 minute durations, the $10-for-20-minutes typical rate, the demographic assignment rule, and payment via PayPal."},
        "c2": {"pass": True, "evidence": "Catalog claim: earn $3-$30 per usability test via PayPal. Official FAQ matches exactly: earn $3-$30 per test, tests 5-60 minutes, most are 20 minutes earning $10, paid to PayPal."},
        "c3": {"pass": True, "evidence": "No signup or qualification-test fee. Payment requires watching the training video and reading the FAQ; unpaid qualification test disclosed as a catch."},
        "c4": {"pass": True, "evidence": "Concrete official figures: $3-$30 per test; most tests 20 minutes paying $10; payment ~1 week after approval to PayPal via the Userfeel wallet."},
    },
    eligibility="Anyone who completes the free qualification test and matches client demographic criteria; computer, tablet, or smartphone with microphone.",
    notes="Verified against official userfeel.com/tester-faq on 2026-09-23. Browser page-fetch unavailable this session; evidence rests on provider-domain content via search snippets. Distinct provider from UserTesting (R0221), Userlytics (R0222), PlaytestCloud (R0167/R0226), and TryMyUI (rejected - no official terms). Test supply is demand-driven; most earners get little.",
    official_url="https://www.userfeel.com/tester-faq",
    payout_quote="Become a tester of websites and apps and earn $3 - $30 per test; each test lasts 5 to 60 minutes; most tests are 20 minutes where you earn $10",
    standard={
        "s1": {"pass": True, "note": "Eligibility: pass free qualification test; tests assigned only on demographic match; device with mic required."},
        "s2": {"pass": True, "note": "Payout mechanics stated: payment after approval (~1 week) to Userfeel wallet, transferable to PayPal."},
        "s3": {"pass": True, "note": "Payout timing stated: about one week after the test, after approval."},
        "s4": {"pass": True, "note": "Core pay claims are exact ranges ($3-$30, $10 for 20 min); no vague multipliers."},
        "s5": {"pass": False, "note": "userfeel.com pages not loadable via page fetch this session; official-domain content reached via search snippets."},
        "s6": {"pass": True, "note": "Steps concrete: qualify, receive assignments, complete tests, get paid on approval."},
        "s7": {"pass": True, "note": "Checked 2026-09-23."},
    },
    steps=[
        "Sign up on userfeel.com and complete the free qualification test.",
        "Watch the mandatory training video and read the tester FAQ (required to get paid).",
        "Receive test assignments by email when you match a client's demographics; complete each test (5-60 minutes, most 20 minutes) with spoken feedback.",
        "After approval (~1 week), receive $3-$30 per test (typically $10 for 20 minutes) to your Userfeel wallet, transferable to PayPal.",
    ],
    terms_url="https://www.userfeel.com/tester-faq",
    timing="Payment about one week after each test, following approval; transferable to PayPal from the Userfeel wallet.",
    upfront_fee=False,
    weasel_words=[],
    payout_min_usd=3.0, payout_max_usd=30.0,
    payout_value_note="official per-test pay: $3-$30 per test (typical $10 for a 20-minute test); assignment depends on demographic match",
    time_min_minutes=5.0, time_max_minutes=60.0,
    numeric_basis="payout: official $3-$30/test range; time: official per-test duration 5-60 min (typical 20 min)",
))

# R3446 Prosper P2P lending investor notes
routes.append(base("R3446",
    biggest_catch="This is investing, not a paycheck: you must risk your own capital (minimum $25 per Note), returns are NOT guaranteed, and you can lose principal to borrower defaults. The 5.3% figure is a historical weighted average, explicitly not a promise of future results.",
    catches=[
        "Prosper's official invest page and prospectus state: 'Historical performance is no guarantee of future results and the information presented is not intended to be investment advice or a guarantee about the performance of any Note.'",
        "Weighted average historical return of borrower loans was 5.3% as of September 30, 2025 (net of fees and charge-offs) - historical only; 'Individual results may vary'.",
        "Investors bear credit risk: charged-off/defaulted loans produce gross principal losses; actual return depends on the prepayment and delinquency pattern of underlying loans, 'which is highly uncertain'.",
        "Minimum $25 per Note investment; servicing/collection fees reduce returns; auto-invest mixes (AA-B weighted, D-HR weighted, marketplace) shift risk/return.",
    ],
    critical={
        "c1": {"pass": True, "evidence": "prosper.com is the provider's official domain; the official invest page (https://www.prosper.com/invest) and the SEC-filed prospectus (prosper.com Downloads/Legal) state the historical-return methodology, the 5.3% weighted average, and the no-guarantee disclaimer."},
        "c2": {"pass": True, "evidence": "Catalog claim: earn interest by funding personal loans via P2P notes. Official sources confirm investors fund borrower loans and receive payments net of fees; historical return figures are provider-stated but explicitly not guaranteed."},
        "c3": {"pass": True, "evidence": "No provider signup fee. Servicing and collection fees are deducted from investor payments and disclosed in the prospectus; the $25 minimum per Note is the user's own at-risk capital, not a fee."},
        "c4": {"pass": True, "evidence": "Concrete official figures: $25 minimum per Note; 5.3% weighted average historical return (Sept 30, 2025) net of fees and charge-offs; explicit disclaimer that this is not a guarantee. Variable by design - honestly framed with 0/0 numeric."},
    },
    eligibility="Investors meeting Prosper's eligibility requirements (U.S. persons; state availability may vary).",
    notes="Verified against official prosper.com/invest and the SEC-filed Prosper prospectus on 2026-09-23. Browser page-fetch unavailable this session; evidence rests on provider-domain and SEC-filed content via search snippets. This is a risk-capital route: earnings require risking principal, returns are variable and can be negative. Included with full capital-at-risk framing per the variable-framing rule.",
    official_url="https://www.prosper.com/invest",
    payout_quote="The weighted average historical return, as of September 30, 2025, of the Borrower Loans is 5.3%... Historical performance is no guarantee of future results... The actual return on any Note depends on the prepayment and delinquency pattern of the Borrower Loan underlying each Note, which is highly uncertain.",
    standard={
        "s1": {"pass": True, "note": "Eligibility: investor eligibility per Prosper terms; U.S. investors, state restrictions may apply."},
        "s2": {"pass": True, "note": "Payout mechanics stated: investors receive interest/principal payments on Notes net of servicing and collection fees."},
        "s3": {"pass": True, "note": "Loan payments follow borrower repayment schedules (36/60-month terms); historical returns are annualized calculations, not payment timing."},
        "s4": {"pass": True, "note": "Official copy explicitly disclaims guarantees ('no guarantee of future results') - honest, no weasel-worded promise on the core claim."},
        "s5": {"pass": False, "note": "prosper.com pages not loadable via page fetch this session; official-domain and SEC-filed content reached via search snippets."},
        "s6": {"pass": True, "note": "Steps concrete: open investor account, fund, select/auto-invest Notes at $25 minimum, receive payments."},
        "s7": {"pass": True, "note": "Checked 2026-09-23."},
    },
    steps=[
        "Open a Prosper investor account and complete eligibility verification.",
        "Fund the account and select individual Notes (minimum $25 each) or a pre-set Auto Invest mix.",
        "Hold the Notes as borrowers repay over the loan term; receive monthly payments of principal plus interest, net of servicing/collection fees.",
        "Reinvest or withdraw proceeds; expect variable results including possible principal loss on defaults.",
    ],
    terms_url="https://www.prosper.com/invest",
    timing="Returns accrue over the multi-year loan term via borrower monthly payments; historical returns are annualized, not a payment schedule.",
    upfront_fee=False,
    weasel_words=["Diversify & Earn"],
    payout_min_usd=0.0, payout_max_usd=0.0,
    payout_value_note="variable investing: no fixed payout; provider states 5.3% weighted average HISTORICAL return (Sept 2025) net of fees/charge-offs - not guaranteed; capital at risk",
    time_min_minutes=30.0, time_max_minutes=60.0,
    numeric_basis="payout: no parseable guaranteed amount; variable; time: one-time account setup + note selection estimate 30-60 min active",
))

import os
os.makedirs("/home/hatch/workspace/upmore/qa/verification", exist_ok=True)
for r in routes:
    p = f"/home/hatch/workspace/upmore/qa/verification/{r['route_id']}.json"
    with open(p, "w") as f:
        json.dump(r, f, indent=2, ensure_ascii=False)
    print("wrote", p, "keys:", len(r))
