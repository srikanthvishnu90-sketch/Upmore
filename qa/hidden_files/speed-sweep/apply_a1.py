#!/usr/bin/env python3
"""Speed audit for chunk A1 (179 referral-bonus routes). Writes per-route decisions."""
import json, re

QADIR = '/home/hatch/workspace/upmore/qa'
chunk = json.load(open(f'{QADIR}/hidden_files/speed-sweep/chunk_A1.json'))

TODAY = {
'R3903': {
 'rationale': "Official terms (verified live): referrer bonus 'deposited into the referrer's account at the time of the referral's checking account opening' — same-day.",
 'wca': "The $25 referrer bonus is deposited into your PeoplesBank account AT THE TIME the friend's checking account is opened — same day, per official disclosures ('The $25 will be deposited into the referrer's account at the time of the referral's checking account opening'). The friend must present the referral form at account opening (in-branch). Note: the FRIEND's own $25 is slower — paid within 6 weeks of their first direct deposit.",
 'maximize': ["Have the friend open the account with your completed referral form in hand — the form must be presented at the exact time of opening; no retroactive credit.",
  "Your $25 posts same-day; move or spend it immediately — no holding period on the referrer side.",
  "No referral cap is published — every same-day account opening through your form is another $25."]},
'R3884': {
 'rationale': "Official terms (verified live): bonuses credited 'instantly' and 'upon account opening' — same-day.",
 'wca': "Both $25 bonuses are credited INSTANTLY at account opening ('they get $25 instantly, and you'll receive $25 too... credited to both parties upon account opening'), provided the friend presents the physical referral coupon at opening and both accounts are in good standing. Fairfield County CT eligibility; offer valid through 12/31/2026.",
 'maximize': ["Pick up referral coupons at a Members CU office in advance — the coupon is only valid at the exact time of account opening and cannot be applied retroactively.",
  "Same-day credit means same-day usability; the friend's only prerequisite is the $5 minimum share deposit.",
  "No referral cap is published — each new-member opening with your coupon is $25 the same day."]},
'R3436': {
 'rationale': "Official terms (verified live): referrer bonus 'credited to your account when Referred Customer opens a qualified account' — same-day.",
 'wca': "The REFERRER's $50 is credited to your account when the referred customer opens a qualifying account ('Referring Customer bonus will be credited to your account when Referred Customer opens a qualified account') — same day for openings with the completed Refer-A-Friend card. Note: the FRIEND's $50 is slower (credited after 60 days of opening). Cap 10/year ($500); card required at account opening.",
 'maximize': ["Give the friend the pre-filled Refer-A-Friend card before they visit a branch — it must be presented at account opening; there is no online flow.",
  "Your $50 posts at opening; only the friend's side waits 60 days — your speed is unaffected.",
  "Checking, savings, or money market all qualify for your bonus — steer the friend to the easiest qualifying account."]},
}

DAYS = {
'R2254': {
 'rationale': "Official terms (verified live): bonus credited 'within seven (7) business days' after qualifying activities are validated.",
 'wca': "Bonus credited within seven (7) business days after all qualifying activities are completed and validated — per official Bank Referral Program terms (verified live 2026-09-23). Qualifying activity: friend opens SoFi Checking and Savings via your link and makes $500+ in deposits (ACH, wire, mobile check deposit, or debit-card instant transfer — NOT Venmo/PayPal/Zelle) within 21 days of registering. A wire or instant transfer can satisfy the $500 in 1-2 days, so end-to-end can be ~1 week. Referrer gets $100 (SoFi Plus member / direct-deposit holder / $5k+ deposits) or $75. Current promo window ends Sept 30, 2026.",
 'maximize': ["Have the friend fund via wire or debit-card instant transfer instead of waiting on payroll direct deposit — any non-P2P method counts toward the $500 and can land in 1-2 days.",
  "The 21-day funding clock starts the day after registration — register via the link immediately.",
  "Check your tier before referring: SoFi Plus members / direct-deposit holders / $5k+ depositors get $100, others $75.",
  "Refer inside the promo window (ends Sept 30, 2026)."]},
'R2514': {
 'rationale': "Official terms: rewards deposited 'within 2-3 business days' of the friend opening required accounts.",
 'wca': "Rewards deposited into share accounts within 2-3 business days of the friend opening the required accounts and completing eligibility actions — per official program terms. Required: new Everyday Hero Checking opened via your custom referral link. Cap $250/year (10 referrals).",
 'maximize': ["Use your custom referral link (not in-branch) — link-attributed openings trigger the 2-3 business day clock automatically.",
  "Have the friend complete all required actions in the same session as account opening so the clock starts immediately.",
  "No deposit marathon required — qualification is the account opening itself, making this one of the fastest credit-union referrals."]},
'R3361': {
 'rationale': "Official terms: $50 reward 'within 48 hours' of the friend's qualifying direct deposit.",
 'wca': "Both parties receive $50 within 48 hours of the friend's qualifying direct deposit — per official terms. Qualifying: $200+ ACH direct deposit from employer/payroll/government/unemployment within 45 days of account opening (bank transfers, P2P, tax refunds don't count). The 48-hour clock starts at the deposit, so a friend whose payroll hits in week 1 gets you paid in ~1 week. Cap $1,500/year.",
 'maximize': ["Refer friends with an upcoming payroll date — the only wait is their first $200+ paycheck landing.",
  "Confirm the deposit codes as ACH direct deposit (employer/payroll/government); P2P transfers from Cash App/Venmo do NOT qualify and waste the 45-day window.",
  "Prioritize friends with regular payroll — cap is $1,500/year (30 referrals)."]},
'R2448': {
 'rationale': "Official terms: bonuses paid 'within 3 business days' after qualifications are met.",
 'wca': "Bonus paid to your savings account within 3 business days after qualifications are met — per official terms. Qualifications: friend opens savings + checking with eStatements, keeps $50+ balance until bonus paid, enrolls in Digital Banking/Bill Pay/Direct Deposit. The $100 rate is a limited-time 2x boost of the standard $50 — can end anytime. Cap $500/year.",
 'maximize': ["Move fast on the limited-time 2x rate — it reverts to $50 without notice once bonus funds are exhausted.",
  "Have the friend open both accounts, enroll in digital banking, and park $50+ in one session — the 3-business-day clock starts when the last requirement posts.",
  "Warn the friend not to zero the account before the bonus lands — the $50 balance must stay until paid."]},
'R3931': {
 'rationale': "Official terms: '$25 deposited within 5 business days of account opening'.",
 'wca': "$25 deposited within 5 business days of account opening — per official terms. Friend must: join with $5 share savings deposit, open High-Rate Checking ($5 min), and enroll in new online/mobile banking — all within 60 days of opening.",
 'maximize': ["Have the friend complete all three requirements (share savings, checking, online/mobile banking) at account opening — the 5-business-day clock runs from opening.",
  "All three are same-session actions; nothing requires waiting on payroll or statements."]},
'R3868': {
 'rationale': "Official terms: payout deposited 'within 5 days of new member account opening'.",
 'wca': "Payout deposited into your primary savings within 5 days of the new member's account opening — per official terms. Friend must be a genuinely new member. Cap $500/year (20 referrals).",
 'maximize': ["No deposit or transaction hoops — the trigger is the membership opening itself, so the 5-day clock starts at opening.",
  "Refer in volume: the 20-paid-referrals/year cap is the binding constraint, not speed."]},
'R3875': {
 'rationale': "Official terms: redemption emails 'within 5 business days' of meeting requirements.",
 'wca': "Reward redemption emails sent within 5 business days of meeting offer requirements — per official terms. Requirements: friend (new member) opens Smart Money Checking or Money Market Select and maintains a $5 minimum balance for 30 days. So: ~30 days qualification + up to 5 business days for the email. Reward is a $25 Visa or Amazon e-gift card (not cash).",
 'maximize': ["The 30-day $5-balance hold is the only wait — have the friend open with the $5 on day 1 and don't touch it; the 5-business-day email clock starts the day the hold completes.",
  "Account must stay open/unrestricted until payout — warn the friend not to close early.",
  "E-gift card (not cash) — pick the Amazon option if you shop there to avoid Visa gift-card fees."]},
'R2276': {
 'rationale': "Official terms: loan-referral credit 'within 5 business days after loan closes' (closing itself takes weeks).",
 'wca': "Loan-referral path: credited within 5 business days AFTER the referred loan closes — per official terms. Honest caveat: loan underwriting/closing itself typically takes 2-6 weeks, so end-to-end is weeks; only the post-close crediting is fast. (Account-opening referrals have no stated clock.)",
 'maximize': ["Use the loan path only — it's the only one with a published fast clock (5 business days post-close).",
  "Refer friends already shopping for a loan (pre-approved elsewhere) to compress the closing timeline.",
  "Make sure the friend names you at loan closing — no retroactive credit."]},
'R3365': {
 'rationale': "Official terms: bonus 'arrives the day after' requirements complete (requirements can take ~120 days).",
 'wca': "Bonus arrives THE DAY AFTER the friend completes all requirements — per official terms. Honest caveat: completing the requirements can take up to ~120 days. Escalating tiers: $250 (1st referral) up to $750 (5th+ in a calendar year); tiers reset every January 1st.",
 'maximize': ["Time referrals early in the calendar year — the $250-to-$750 escalator counts only same-year referrals and resets every January 1.",
  "Coach the friend through every requirement immediately after joining; the day-after payout clock rewards fast completion.",
  "This is the highest per-referral payout in the sweep ($250-$750) — worth the qualification effort despite the wait."]},
'R2245': {
 'rationale': "Official terms (verified live): '$25 will be deposited in your account' once the new account is opened — event-triggered, no waiting window.",
 'wca': "Once the friend's new qualifying personal checking account is opened, '$25 will be deposited in your account' — per official terms (verified live 2026-09-23). No published payout clock, but payment is event-triggered on account opening (friend can open online with code REFER25). Cap $100 total (4 referrals).",
 'maximize': ["Have the friend open online with promo code REFER25 — no branch visit needed, so the opening (and your deposit trigger) can happen same-day.",
  "No published clock — expect 1-3 business days typical for an event-triggered bank credit (unverified beyond the official 'once opened' language).",
  "Cap is only $100 total — use all four referral slots."]},
'R2267': {
 'rationale': "Official terms (verified live): 'Once their new account is open, you and your friend each receive $50' — event-triggered.",
 'wca': "'Once their new account is open, you and your friend each receive $50' — per official terms (verified live 2026-09-23). No published payout clock; payment is event-triggered on membership opening. Friend must be new (no OHCU account in last 120 days) and give your name + address at sign-up.",
 'maximize': ["Make sure the friend gives your name AND address at sign-up — miss it and the referral can't be credited.",
  "Friend must be genuinely new (120-day lookback) — pre-screen before they apply.",
  "No published clock — expect prompt event-triggered posting (unverified beyond official 'once open' language)."]},
'R3864': {
 'rationale': "Official referral form (verified): incentive paid 'once your friend or family member opens their account'.",
 'wca': "'You will receive your incentive once your friend or family member opens their account' — per official referral form (verified 2026-09-23). No published payout clock; in-branch opening with the coupon. Referrer must have been a member 90+ days. (The friend's separate $150 bonus has its own 60-day transaction requirements.)",
 'maximize': ["Fill out the MEMBER section and hand the physical coupon to the friend — they must take it to a branch; in-branch only.",
  "You must have been a member for 90+ days to qualify as referrer — newer members earn nothing.",
  "No published clock — expect prompt event-triggered posting (unverified beyond official 'once opens' language)."]},
'R2257': {
 'rationale': "Official page (verified live): $25 'credited to your checking account when your referred friend becomes a member'.",
 'wca': "'Earn $25 credited to your checking account when your referred friend or family member becomes an Align Credit Union member' — per official page (verified live 2026-09-23). No published payout clock; payment is event-triggered on membership (friend can apply online after you submit the online referral form).",
 'maximize': ["Submit the online referral form first, then have the friend apply online immediately — the membership event triggers your credit.",
  "Low barrier: membership alone (not deposits/transactions) triggers payment.",
  "No published clock — expect prompt event-triggered posting (unverified beyond official 'when becomes a member' language)."]},
'R2294': {
 'rationale': "Official referral form: '$25 will be deposited into my savings account' after the friend opens membership + checking.",
 'wca': "'After my friend opens a membership with a checking account, $25 will be deposited into my savings account' — per the official referral form. No published payout clock; payment is event-triggered on the membership+checking opening. Unlimited referrals, no cap.",
 'maximize': ["No cap and a simple trigger (membership + checking) — this is a volume play: every completed opening is $25.",
  "The form states no payout clock — confirm current timing at the branch.",
  "No published clock — expect prompt event-triggered posting (unverified beyond the form's 'after opens' language)."]},
'R2295': {
 'rationale': "Official page: 'When they open their new account, both you and your friend will receive $25' — event-triggered.",
 'wca': "'When they open their new account, both you and your friend will receive $25' — per official program page. No published payout clock; event-triggered on account opening. No limits on referral count. Friend must be brand-new (never a member) and the referral form filed at account opening.",
 'maximize': ["File the referral form AT account opening — late forms don't count.",
  "Friend must be brand-new to Members First — pre-screen.",
  "Unlimited count with an event trigger — stack openings in the same week for compounding $25s."]},
'R2446': {
 'rationale': "Official form: '$25 dividend bonus on referred new member's joining' — earned on the joining event.",
 'wca': "Each side earns a '$25 dividend bonus on referred new member's joining HFDFCU' — per official referral form. No explicit crediting window; the bonus is earned on the joining event itself. Friend must be a brand-new member 18+; referrer must be in good standing.",
 'maximize': ["The trigger is the joining event — no deposit/transaction requirements to wait on.",
  "Referrer must be in good standing; friend must be 18+ and brand-new.",
  "No published clock — expect prompt event-triggered posting (unverified beyond the form's 'on joining' language)."]},
'R2456': {
 'rationale': "Official page: $25 'credited... once the referral successfully opens and funds their new membership' — event-triggered.",
 'wca': "'$25 will be credited to the current member's Savings account as a dividend once the referral successfully opens and funds their new membership' — per official page. Event-triggered on opening + funding (funding can be the $5 minimum share). Offer can end anytime.",
 'maximize': ["The friend only needs to open AND fund (minimum share deposit) — a same-day action — then your credit triggers.",
  "Limited-time framing ('can end anytime') — refer sooner rather than later."]},
'R2250': {
 'rationale': "Official terms: '$100 FOR YOU. $100 FOR THEM' paid 'once both accounts are open and in good standing'.",
 'wca': "'$100 FOR YOU. $100 FOR THEM' — 'paid once both accounts are open and in good standing,' per official terms. No day-count clock; event-triggered on both accounts being open. Seasonally-framed promo — confirm it's still running before referring.",
 'maximize': ["No deposit/transaction hoops stated — the trigger is both accounts open and in good standing.",
  "Confirm the promo is still live (seasonal framing) before spending referral effort.",
  "No published clock — expect prompt event-triggered posting (unverified beyond 'once open' language)."]},
'R3889': {
 'rationale': "Official page: 'After their new accounts are open, you will each receive $50' — event-triggered.",
 'wca': "'After their new accounts are open, you will each receive $50' — per official page. No day-count stated and no fine print published; event-triggered on the accounts opening. 'Earn up to $500 a month' suggests high volume is allowed.",
 'maximize': ["No qualifying-activity hoops are stated — the friend just opens accounts.",
  "The page publishes no fine print — ask SECU for terms before counting on it (unverified beyond the page's 'after open' language)."]},
'R3343': {
 'rationale': "Official page: $100 'deposited... when the referred business opens' its accounts — event-triggered.",
 'wca': "'$100 will be deposited to your Business Membership Savings Account when the referred business opens their Business Membership Savings and Business Checking with a debit card' — per official page. Event-triggered on the business's account opening (business openings take a few days for entity docs). Cap 5 business referrals/year ($500).",
 'maximize': ["Target businesses with formation docs ready — entity paperwork is the only lead time; the deposit triggers on opening.",
  "Each qualifying business is $100 — the highest same-event payout among CU referrals here.",
  "Cap is 5/year — prioritize serious prospects."]},
'R2447': {
 'rationale': "Official terms: paid 'once confirmed' after the 30-day open-checking + activated-debit-card period.",
 'wca': "Paid 'once confirmed' — after the new member completes 30 days with an open checking account and activated debit card, per 2023 newsletter terms (confirm the program is still running). The payout leg is event-triggered on the 30-day confirmation; no additional payout clock. $50 each side, reported as taxable income.",
 'maximize': ["The 30-day clock is the whole wait — have the friend open + activate the debit card on day 1.",
  "Evidence is from 2023 newsletters — verify the program still runs before referring (unverified currentness)."]},
'R2506': {
 'rationale': "Official page: 'Reward is paid once the new loan... is approved and funded' — event-triggered on funding.",
 'wca': "'Reward is paid once the new loan over $10,000 is approved and funded' — per official page. Event-triggered on funding; no payout clock stated. Honest caveat: loan approval/funding typically takes 1-4 weeks, so end-to-end is weeks; only the post-funding payment is prompt. Loan must be new-to-CoastLife, over $10k. $100 each side.",
 'maximize': ["Refer friends already approved/shopping for a loan elsewhere — a fast funding compresses the whole timeline.",
  "The loan must be new to CoastLife and actually fund — applications alone pay nothing.",
  "No published post-funding clock (unverified beyond 'once funded' language)."]},
'R3420': {
 'rationale': "Official flyer: 'referrer paid at loan origination' — event-triggered on origination.",
 'wca': "'Referrer paid at loan origination' — per official April 2024 flyer. Event-triggered on origination; no payout clock. Tiers: $50 ($5k-$9,999), $75 ($10k-$19,999), $100 ($20k+) each side. Honest caveats: origination takes days-weeks after application; official terms are an April 2024 flyer with no end date (confirm currentness).",
 'maximize': ["Steer toward the $20k+ tier — same origination wait, double the payout ($100 vs $50).",
  "Confirm the program is still running — the only official terms found are a 2024 flyer (unverified currentness)."]},
'R3866': {
 'rationale': "Official page: loan bonus 'paid upon closing of loan' — event-triggered (account leg stays 90-day).",
 'wca': "Loan-referral leg: '$100 sign-on bonus will be paid upon closing of loan' — event-triggered on closing, per official page. (The account-referral leg is slower: deposited after 90 days with $2,500 balance + direct deposit requirements.) Use the loan path for speed. Cap 5 referrals/year.",
 'maximize': ["Use the loan path, not the account path — 'paid upon closing' vs 90-day deposit hold.",
  "Refer friends already closing a loan — the closing event is the entire trigger.",
  "Cap is 5/year — allocate to loan referrals for fastest $100s."]},
'R3870': {
 'rationale': "Official page: 'Gift card awarded once the referred loan is active' — event-triggered.",
 'wca': "'Gift card awarded once the referred loan is active' — per official page. Event-triggered on the loan booking (HELOC $100 / auto $50 / Visa $25 gift cards). Limited-time offer, can be withdrawn without notice. Gift-card fulfillment adds mail/delivery time (unverified).",
 'maximize': ["Steer toward HELOC referrals — $100 gift card for the same 'loan active' trigger vs $25 for a Visa.",
  "Limited-time offer — refer while it's live.",
  "Gift card (not cash) — fulfillment timing beyond 'awarded' is unverified."]},
'R3895': {
 'rationale': "Official page: paid 'upon approval' of the referred friend's loan — event-triggered.",
 'wca': "'Earn $25 if they get approved for a personal loan, $50 for approval of an auto loan, and $100 for a home equity loan' — paid upon approval, per official page. Event-triggered on approval (approval itself takes days). Referrer must have been a member 3+ months; friend must mention the referral at application.",
 'maximize': ["Home-equity approvals pay $100 — 4x the personal-loan $25 for the same approval event.",
  "You must have been a member 3+ months — newer members aren't eligible.",
  "Friend must mention you AT application — no retroactive credit."]},
'R3912': {
 'rationale': "Official module: '$50.00 gift card digitally' sent 'after the referred person opens an account'.",
 'wca': "'Gift cards sent after the referred person opens an account' — $50 digital gift card per valid referral, per official module. Digital delivery (email), event-triggered on account opening. Cap 10/year ($500). Friend must not have been a member in past 24 months.",
 'maximize': ["Digital gift card = no mail delay — sent after the opening event.",
  "Pre-screen: friend must not have been a member in the last 24 months.",
  "Cap 10/year — volume-plan accordingly."]},
'R3906': {
 'rationale': "Official page: '$50 emailed after account requirements are met' — digital delivery.",
 'wca': "'Your $50 emailed after account requirements are met' — per official page. Emailed (digital) delivery once requirements are met. Referrals must use the shareable link from the page — in-branch/in-person referrals don't count. Cap $500/year.",
 'maximize': ["Generate and use the page's shareable link — in-person referrals don't count.",
  "Emailed delivery — no mail delay once requirements verify."]},
'R2216': {
 'rationale': "Official terms: '$150 investing bonus deposited on/around the friend's Qualifying Deposit' — event-triggered, no waiting window (bonus lands as invested funds; liquidating to cash adds ~3-5 days).",
 'wca': "'$150 investing bonus deposited on/around the friend's Qualifying Deposit' — per official terms. The bonus posts with the friend's qualifying deposit (no waiting window), but it lands as invested funds inside your Betterment automated investing account, not spendable cash — liquidating + ACH to your bank adds ~3-5 days, still within about a week. Cap 5/year ($750).",
 'maximize': ["The bonus posts on/around the friend's qualifying deposit — have the friend fund immediately after opening to trigger it.",
  "To make it spendable cash, sell and ACH out right after it posts (adds ~3-5 days) — or leave it invested.",
  "Cap is 5 referrals/year — each is $150, the largest fast-posting brokerage referral here."]},
}

def weeks_reason(timing, catches):
    t = (timing or '').lower()
    if '4-5 months' in t: return "structural: credits land the calendar month after the third qualifying direct deposit (~4-5 months)"
    if 'year' in t or '12 months' in t or '12-month' in t: return "structural: the bonus requires a 12-month funding/balance hold before it is even earned"
    if '120 days' in t: return "structural: payout can take up to ~120 days from account opening"
    if '90th day' in t: return "structural: a 90-day seasoning must elapse (paid by the statement cycle after the 90th day)"
    if '90 days' in t or '90-day' in t: return "structural: a 90-day account-open/seasoning requirement must elapse before payout"
    if '4-6 weeks' in t: return "structural: the reward is fulfilled as a mailed physical card (4-6 weeks) — no electronic payout option per terms"
    if '2-3 weeks' in t: return "the payout window is 2-3 weeks after qualification"
    if '30-45 days' in t: return "the payout window runs 30-45 days after the triggering deposit settles"
    if '30th day' in t or '30 days following' in t: return "paid on a fixed schedule after the 30th day from account opening"
    if 'within 30 days' in t or 'up to 30 days' in t or '30 days after' in t or 'in 30 days' in t or 'after 30 days' in t or '(30) days' in t: return "the program's payout window runs up to 30 days after qualification"
    if '60 days' in t: return "the friend's qualification window runs up to 60 days and the payout clock starts only after"
    if '45 days' in t: return "a ~45-day window in the terms elapses before the bonus posts"
    if 'next calendar month' in t or 'month after' in t or 'following month' in t or 'month following' in t or 'second month' in t: return "paid in the calendar month after qualification — up to ~60 days end-to-end"
    if '15 business days' in t or 'within 15 days' in t or 'ten business days' in t or 'within 14 days' in t or '7-10 business days' in t or 'two weeks' in t or '10 business days' in t: return "the payout window is ~2 weeks after qualification"
    if 'timing not stated' in t or 'not stated' in t or 'no exact timing' in t or 'no payout clock' in t or 'no fixed day count' in t or 'no day count' in t or 'no fixed timing' in t: return "no published payout clock in official terms — no fast path can be claimed (unverified)"
    return "the stated payout timeline runs multiple weeks"

def weeks_maximize(timing, catches, payout_quote):
    t = (timing or ''); tips = []
    tips.append("Front-load the friend's qualifying activity: terms give the friend 60-90 days, but the payout clock starts at completion — a friend who finishes in week 1 gets you paid weeks earlier.")
    tl = t.lower()
    if '4-6 weeks' in tl and ('card' in tl or 'mailed' in tl or 'visa' in tl or 'mastercard' in tl):
        tips.append("The reward arrives as a physical card by mail (4-6 weeks); no expedite option exists in the terms — factor mail time into expectations.")
    if '30 days' in tl or 'within 30' in tl:
        tips.append("The 30-day payout window is the binding constraint after qualification — nothing in the terms shortens it; compress the qualification leg instead.")
    if '90' in tl:
        tips.append("The 90-day seasoning/hold is structural — pick a different referral program if you need money sooner.")
    if 'year' in tl or '12 months' in tl:
        tips.append("The 12-month hold is structural — this route cannot pay fast under any reading of the terms.")
    c = (catches or '')
    m = re.search(r'cap[^.]{0,80}', c, re.I)
    if m:
        tips.append("Volume constraint noted in terms: " + m.group(0).strip() + " — plan referral count against the cap, not the calendar.")
    return tips[:3]

decisions = {}
for rid in chunk:
    d = json.load(open(f'{QADIR}/verification/{rid}.json'))
    if rid in TODAY:
        decisions[rid] = ('today', TODAY[rid])
    elif rid in DAYS:
        decisions[rid] = ('days', DAYS[rid])
    else:
        timing = str(d.get('timing') or '')
        catches = str(d.get('catches') or '')
        pq = str(d.get('payout_quote') or '')
        reason = weeks_reason(timing, catches)
        wca = f"Per official terms: {timing} — {reason}."
        decisions[rid] = ('weeks', {'rationale': f"Speed audit 2026-09-23: confirmed weeks — {reason}.",
                                    'wca': wca,
                                    'maximize': weeks_maximize(timing, catches, pq)})

json.dump({k: {'new': v[0], 'rationale': v[1]['rationale']} for k, v in decisions.items()},
          open('/tmp/a1_decisions.json', 'w'), indent=1)
print('today:', sum(1 for v in decisions.values() if v[0]=='today'))
print('days:', sum(1 for v in decisions.values() if v[0]=='days'))
print('weeks:', sum(1 for v in decisions.values() if v[0]=='weeks'))
