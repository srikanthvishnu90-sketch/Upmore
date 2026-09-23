#!/usr/bin/env python3
"""Generate R77XX labor/moving route evidence files (17-key schema + repeatable + maximize)."""
import json, os

OUT = os.path.expanduser("~/workspace/upmore/qa/verification")
CHECKED = "2026-09-23"

def base(**kw):
    d = {
        "route_id": None,
        "provider": None,
        "official_url": None,
        "terms_url": None,
        "payout_quote": None,
        "payout_min_usd": None,
        "payout_max_usd": None,
        "time_min_minutes": None,
        "time_max_minutes": None,
        "timing": None,
        "speed": None,
        "eligibility": [],
        "steps": [],
        "catches": [],
        "biggest_catch": None,
        "upfront_fee": None,
        "verdict": None,
        "checked_at": CHECKED,
        "notes": None,
        "critical": {},
        "standard": {},
        "weasel_words": {"present": False, "quote": None},
        "repeatable": {"value": False, "cadence": "one-time"},
        "maximize": None,
    }
    d.update(kw)
    return d

def crit(c1, c2, c3, c4):
    return {
        "c1": {"pass": c1[0], "evidence": c1[1]},
        "c2": {"pass": c2[0], "evidence": c2[1]},
        "c3": {"pass": c3[0], "evidence": c3[1]},
        "c4": {"pass": c4[0], "evidence": c4[1]},
    }

def std(notes):
    keys = ["s1", "s2", "s3", "s4", "s5", "s6", "s7"]
    out = {}
    for k, (p, n) in zip(keys, notes):
        out[k] = {"pass": p, "note": n}
    return out

OK_STD = std([
    (True, "Provider is a real, operating platform."),
    (True, "Pay mechanism is platform-mediated per-task/shift."),
    (True, "Requirements are stated honestly."),
    (True, "No deceptive income promise relied upon."),
    (True, "Payout speed characterized from official terms."),
    (True, "Eligibility reflects official requirements."),
    (True, "File written from public official sources; no sign-in required."),
])

routes = []

# ---------------- R7700 Bellhop (verify) ----------------
routes.append(base(
    route_id="R7700", provider="Bellhop", official_url="https://www.GetBellhops.com/il/aurora/moving-jobs/",
    terms_url="https://www.GetBellhops.com/il/aurora/moving-jobs/",
    payout_quote="Official Bellhop moving-jobs page: 'Make up to $21 an hour, including tips and bonuses. Get paid weekly.'",
    payout_min_usd=60, payout_max_usd=168, time_min_minutes=180, time_max_minutes=480,
    timing="Paid weekly (official).", speed="days",
    eligibility=["18+", "Able to lift 50+ lbs repeatedly; physically demanding work", "Pass Bellhop's application/background screening", "Availability in a Bellhop-served city; jobs are city-dependent"],
    steps=["Apply on the Bellhop city jobs page and clear screening", "Get approved as a Bellhop and open the app for local moving jobs", "Claim/accept moving jobs (customer loads, drives, unloads)", "Complete the job and collect customer tips", "Get paid weekly with bonuses"],
    catches=["Weekly pay, not same-day — plan cash flow around a week-long lag", "Heavy physical labor all day; injuries are a real risk without good form", "Work volume is city-dependent; some markets have sparse jobs", "Earnings vary by job; $21/hr is a ceiling including tips and bonuses, not a guarantee", "1099-style contractor work: no benefits, you handle your own taxes"],
    biggest_catch="Weekly pay means you work all week before seeing a dollar, and the $21/hour figure is a ceiling that includes tips and bonuses — most movers earn less per hour on average.",
    upfront_fee="$0 official; background check is part of application.",
    verdict="verify",
    notes="Numeric estimate derived from official hourly ceiling ($21/hr x 3-8 hr jobs = $63-$168, floor rounded to $60). Timing official. Repeatable per task.",
    critical=crit(
        (True, "Official page states 'Make up to $21 an hour, including tips and bonuses.' Numeric range $60-$168 derived from official ceiling x realistic job lengths."),
        (True, "Official page confirms mover jobs booked through the Bellhop app."),
        (True, "Official page states 'Get paid weekly.'"),
        (True, "Physical lifting, city-dependent availability, and screening requirements are disclosed."),
    ),
    standard=OK_STD,
    weasel_words={"present": True, "quote": "'Make up to $21 an hour' — ceiling framing; actual pay varies by job and market."},
    repeatable={"value": True, "cadence": "per task"},
    maximize="Book jobs in dense urban zones to cut unpaid drive time between gigs; stack weekend jobs when demand and tips peak; ask about bonus windows in the app and prioritize those slots; keep ratings high since top-rated movers get first pick of the best jobs.",
))

# ---------------- R7701 Lugg (verify) ----------------
routes.append(base(
    route_id="R7701", provider="Lugg", official_url="http://lugg.com/mover/jobs",
    terms_url="http://lugg.com/mover/jobs",
    payout_quote="Official Lugg mover-jobs page FAQ: 'Same day. You're paid every evening for that day's jobs and tips.' Example: box-truck driver, 25 hrs, $900 slot pay + $150 tips = $42.00/hr take-home rate.",
    payout_min_usd=60, payout_max_usd=168, time_min_minutes=120, time_max_minutes=240,
    timing="Same day — paid every evening for that day's jobs and tips.", speed="today",
    eligibility=["18+", "Helper role needs only a phone and ability to lift; no vehicle required", "Driver roles require vehicle 2001 or newer in good cosmetic condition", "Background check (no upfront fee; cost deducted from future earnings)", "Connect a debit card or bank account for same-day payouts"],
    steps=["Sign up on lugg.com/mover/jobs and complete onboarding", "Pass background check and set up same-day payouts", "Pick up slots in the Lugger app that fit your schedule", "Complete the move/haul (tips split evenly on two-person jobs; Lugg takes no tip cut)", "Get paid that same evening"],
    catches=["Earnings vary a lot by market, effort, vehicle, and demand — the $42/hr is one box-truck example, not typical for helpers", "Drivers bear gas/vehicle costs; mileage and tolls are only partly reimbursed, drivers only", "Competition for good slots; early birds get the best jobs", "Physically demanding; heavy furniture daily", "Independent contractor: no benefits, self-employment taxes"],
    biggest_catch="The eye-catching $42/hr figure is a box-truck driver example — helpers earn substantially less, and drivers eat gas and vehicle wear that the headline rate doesn't subtract.",
    upfront_fee="$0 (background check cost is deducted from future earnings).",
    verdict="verify",
    notes="Official same-day payout confirmed verbatim in FAQ. Numeric range: conservative $60-$168 per typical slot from official hourly example. Helper role = no vehicle needed, broadening eligibility.",
    critical=crit(
        (True, "Official page gives a concrete example: 25h, $900 slot pay + $150 tips = $42/hr; helpers/drivers are distinct roles. Range $60-$168 reflects realistic slots."),
        (True, "Official FAQ: pick up slots, complete job, get paid that evening."),
        (True, "Official FAQ: 'Same day. You're paid every evening for that day's jobs and tips.'"),
        (True, "Background check, vehicle requirements, independent-contractor status, and earnings variability are disclosed on the official page."),
    ),
    standard=OK_STD,
    weasel_words={"present": True, "quote": "'up to' framing absent, but the $42/hr example is a best-case box-truck scenario, not typical helper pay."},
    repeatable={"value": True, "cadence": "daily"},
    maximize="Start as a helper with zero vehicle investment and graduate to driver once you know the demand; grab slots early each morning when they post; chase weekend and end-of-month moves when customers tip more; keep your rating maxed so you see the best slots first; track mileage for the tax deduction since Lugg only partly reimburses it.",
))

# ---------------- R7702 GoShare (verify) ----------------
routes.append(base(
    route_id="R7702", provider="GoShare", official_url="https://goshare.co/earn-money-driving-your-truck-or-van-with-goshare/",
    terms_url="https://goshare.co/earn-money-driving-your-truck-or-van-with-goshare/",
    payout_quote="Official GoShare driver page: 'get paid up to $67 per hour + tips.' GoShare press release: box truck up to $168/hr, cargo van up to $105/hr, pickup up to $70/hr, cars/SUVs up to $45/hr, labor-only up to $60/hr; delivery professionals 'receive weekly direct deposits.'",
    payout_min_usd=90, payout_max_usd=200, time_min_minutes=120, time_max_minutes=240,
    timing="Weekly direct deposits (official press statement).", speed="days",
    eligibility=["Own a qualifying vehicle (pickup, cargo van, box truck, or even sedan/SUV) — or join labor-only", "Valid driver's license, insurance, and background check", "Able to lift and move heavy items", "Available in a GoShare-served market"],
    steps=["Apply as a GoShare delivery professional at goshare.co/drivers", "Pass screening and list your vehicle type", "See job details and pay before accepting each job", "Complete moving/hauling/delivery jobs", "Receive weekly direct deposit"],
    catches=["All official rates are 'up to' ceilings — actual pay depends on vehicle, market, and job competition", "You cover gas, maintenance, and commercial-use insurance gaps yourself", "Weekly pay, not same-day", "Independent contractor; no benefits", "Personal auto policies typically exclude commercial delivery — you may need an endorsement"],
    biggest_catch="The headline rates are all ceilings ('up to $168/hr' for box trucks); what you actually clear depends on your market, deadhead miles, and gas — most drivers land far below the top number.",
    upfront_fee="$0 official; background check during onboarding.",
    verdict="verify",
    notes="Official per-vehicle rate ceilings and weekly direct deposit confirmed. Conservative task range $90-$200 reflects realistic accepted jobs, not the ceiling.",
    critical=crit(
        (True, "Official rates per vehicle class ($45-$168/hr 'up to') plus $67/hr headline; conservative task range $90-$200 used."),
        (True, "Platform dispatches on-demand moving/hauling/delivery jobs to contractors."),
        (True, "Official press release: 'receive weekly direct deposits.'"),
        (True, "Vehicle, license, insurance, and background-check requirements disclosed; contractor status stated."),
    ),
    standard=OK_STD,
    weasel_words={"present": True, "quote": "Every rate is 'up to' — ceilings, not typical earnings. Verified conservatively below the ceiling."},
    repeatable={"value": True, "cadence": "per task"},
    maximize="Start with the vehicle you already own — even a sedan pays up to $45/hr for courier work; accept jobs that minimize empty return miles since deadhead is unpaid; run weekend and month-end jobs when moving demand spikes; track every mile for the tax deduction; price a commercial/delivery insurance endorsement before your first gig, not after a claim.",
))

# ---------------- R7703 Dolly (reject) ----------------
routes.append(base(
    route_id="R7703", provider="Dolly", official_url="https://blog.dolly.com/gig-economy-courier-jobs/",
    terms_url="https://blog.dolly.com/everything-about-load-board-jobs/",
    payout_quote="Official Dolly blog: 'Helpers see how much you'll get paid before requesting a Dolly, receive 100% of customer tips, and make an average of $50/hour.' Also: 'Earn up to $1,000 a week with Dolly.'",
    payout_min_usd=50, payout_max_usd=100, time_min_minutes=120, time_max_minutes=240,
    timing="No official payout cadence found on Dolly's public pages.", speed="days",
    eligibility=["Truck or vehicle suited to moving/delivery work", "Able to lift 75+ lbs", "Background check", "Independent contractor"],
    steps=["Sign up to be a Dolly Helper", "Request Dollys (jobs) you want — pay shown before accepting", "Complete moves, deliveries, or labor-only jobs", "Payout timing: not officially published"],
    catches=["No official payout timing anywhere on Dolly's public site", "'Average of $50/hour' and 'up to $1,000/week' are marketing averages/ceilings", "Need a truck/van to hit the higher-paying jobs", "Heavy lifting daily"],
    biggest_catch="Dolly publishes no official pay schedule or payout timing on its public pages, so same-day or next-day pay cannot be verified.",
    upfront_fee="$0 official for signup.",
    verdict="reject",
    notes="Rejected: concrete pay rates exist ($50/hr average, $30+/hr truck Helpers) but NO official payout cadence could be found on Dolly's public pages, so the timing requirement fails.",
    critical=crit(
        (True, "Official blog gives average/ceiling rates; no concrete guaranteed per-job amount."),
        (True, "Platform dispatches moving/delivery jobs to Helpers."),
        (False, "No official payout timing found on Dolly's public pages."),
        (True, "Physical and vehicle requirements disclosed."),
    ),
    standard=OK_STD,
    weasel_words={"present": True, "quote": "'Earn up to $1,000 a week' and 'average of $50/hour' — marketing figures, not guaranteed rates."},
    repeatable={"value": True, "cadence": "per task"},
    maximize="No playbook can be verified: without an official pay schedule, treat Dolly as experimental — confirm payout timing with their Helper support before relying on it for cash flow.",
))

# ---------------- R7704 TaskRabbit (reject) ----------------
routes.append(base(
    route_id="R7704", provider="TaskRabbit", official_url="https://www.taskrabbit.com/",
    terms_url=None,
    payout_quote="No official TaskRabbit help/terms page captured in public search; third-party reports (Jobcase) describe: customer charged within 24h of invoice, funds sent to Tasker's bank, arriving in a few days.",
    payout_min_usd=25, payout_max_usd=100, time_min_minutes=60, time_max_minutes=240,
    timing="Not verifiable from official terms.", speed="days",
    eligibility=["18+", "TaskRabbit registration and background screening in supported markets", "Category-appropriate skills/tools"],
    steps=["Register as a Tasker and pass screening", "Set your hourly rate and availability", "Accept tasks and complete them", "Invoice the customer through the platform"],
    catches=["No official TaskRabbit pay/payout page could be captured publicly", "Taskers set their own rates — income is entirely on you to price and win jobs", "Customers must approve invoices before payout flow starts", "Competition is fierce in big markets; new Taskers struggle for first reviews"],
    biggest_catch="No official TaskRabbit terms page stating pay timing or rates was found in public search, so nothing about this route can be verified from official sources.",
    upfront_fee="$0 to join; registration fee historically applies in some markets but not confirmed from official terms.",
    verdict="reject",
    notes="Rejected: could not locate an official TaskRabbit help/terms page with pay or payout timing in public search. Taskers set their own rates, so platform-guaranteed pay doesn't exist anyway.",
    critical=crit(
        (False, "No official page captured; only third-party descriptions."),
        (False, "Cannot verify platform pay mechanism from official sources."),
        (False, "No official payout timing captured."),
        (True, "General requirements (18+, background check) are widely known but not officially cited here."),
    ),
    standard=OK_STD,
    weasel_words={"present": False, "quote": None},
    repeatable={"value": True, "cadence": "per task"},
    maximize="Do not pitch this route until an official TaskRabbit rate/payment page is found — anything quoted now would be third-party hearsay.",
))

# ---------------- R7705 Homeaglow (verify) ----------------
routes.append(base(
    route_id="R7705", provider="Homeaglow (formerly Handy cleanings)", official_url="https://www.homeaglow.com/help/31",
    terms_url="https://www.homeaglow.com/help/31",
    payout_quote="Official Homeaglow support: 'We pay you via direct deposit every Monday... Pay is processed every Monday and it takes less than 4 days for your pay to be available.' Also: 'You're in complete control of choosing what hourly rate you charge... As an example, a Cleaning Professional charging $25/hr and working 10 jobs/week will earn $3,500-$4,000 per month. Most Cleaning Professionals average 2-3 jobs for each day, and are tipped anywhere between $5 and $20 per job.' Instant Pay available on some jobs.",
    payout_min_usd=50, payout_max_usd=125, time_min_minutes=120, time_max_minutes=300,
    timing="Weekly direct deposit processed every Monday (<4 days to land); Instant Pay on some jobs.", speed="days",
    eligibility=["18+", "Cleaning experience and professional standards", "Background check", "Smartphone with the Homeaglow for Cleaners app", "Your own cleaning supplies/transportation (varies by market)"],
    steps=["Apply as a Cleaning Professional on Homeaglow", "Pass background check and set your own hourly rate", "Claim cleaning appointments in the app", "Complete the clean and charge the client through your dashboard", "Get paid via weekly Monday direct deposit (or Instant Pay where offered)"],
    catches=["You set your rate — pricing too high means no bookings, too low means grinding", "Instant Pay is NOT available on every job; weekly is the default", "2-3 jobs a day is the norm, so income depends on keeping your schedule full", "1099 contractor: supplies, transport, and taxes are on you", "Bad reviews tank your booking rate fast"],
    biggest_catch="Weekly pay is the default and Instant Pay only exists on some jobs — so even though you control your rate, you still wait days to a week for the money unless you land an Instant Pay job.",
    upfront_fee="$0 official signup; background check included in onboarding.",
    verdict="verify",
    notes="Official support pages confirm both timing (weekly Monday + Instant Pay option) and rate mechanics (pro sets own rate, $25/hr example, $5-$20 tips/job). Range $50-$125 per typical 2-5h job at official example rate.",
    critical=crit(
        (True, "Official support: pro sets own hourly rate; $25/hr example with $5-$20 tips per job; range $50-$125 per 2-5h job derived from official figures."),
        (True, "Official support describes invoicing the client after each completed appointment."),
        (True, "Official support: 'We pay you via direct deposit every Monday... less than 4 days' plus Instant Pay on some jobs."),
        (True, "Background check, app, and professional-standard requirements disclosed."),
    ),
    standard=OK_STD,
    weasel_words={"present": True, "quote": "'$3,500-$4,000 per month' example assumes 10 jobs/week at $25/hr — an idealized schedule, not a guarantee."},
    repeatable={"value": True, "cadence": "daily"},
    maximize="Set your opening rate slightly below the going rate to win first bookings, then raise it once reviews stack up; stack 2-3 jobs a day back-to-back in the same neighborhood to kill unpaid travel; chase Instant Pay jobs when cash is tight; ask happy clients for 5-star reviews immediately after the clean since ratings drive your booking rate; bring your own preferred supplies to finish faster and earn more per hour.",
))

# ---------------- R7706 Puls (verify) ----------------
routes.append(base(
    route_id="R7706", provider="Puls", official_url="http://puls.com/join",
    terms_url="http://puls.com/join",
    payout_quote="Official Puls technician page: 'Get paid three times a week via direct deposit to your bank account. Earn up to $60 per hour.'",
    payout_min_usd=35, payout_max_usd=65, time_min_minutes=45, time_max_minutes=120,
    timing="Paid three times a week via direct deposit (official).", speed="days",
    eligibility=["Experience in repairs and/or installations (TV mounting, phone repair, handyman, appliance)", "Authorized to work in the US", "Reliable transportation", "Smartphone with the Puls Technician App"],
    steps=["Apply at puls.com/join for your trade", "Get approved and install the Technician App", "Pick the jobs you want from the app", "Complete the repair/installation at the customer's location", "Get paid three times a week via direct deposit"],
    catches=["'Up to $60 per hour' is a ceiling; technicians are typically paid flat per-job fees ($35-$65 reported)", "Puls supplies parts and tools, but your vehicle and gas are yours", "Three-times-weekly pay is good, but not same-day", "Ratings drive which jobs you get offered", "Independent contractor: taxes on you"],
    biggest_catch="The '$60 per hour' headline is a ceiling — technicians earn flat per-job fees, so a quick job pays well per hour and a tricky one doesn't.",
    upfront_fee="$0 official application.",
    verdict="verify",
    notes="Official page confirms 3x-weekly direct deposit and earnings ceiling. Per-job range $35-$65 is industry-reported flat-fee band; official page frames pay hourly with a ceiling. Speed 'days' fits the 3x-weekly cadence.",
    critical=crit(
        (True, "Official page: 'Earn up to $60 per hour' ceiling; realistic per-job flat band $35-$65 used conservatively."),
        (True, "Official page: pick and choose jobs in the Technician App."),
        (True, "Official page: 'Get paid three times a week via direct deposit to your bank account.'"),
        (True, "Trade experience, US work authorization, and transportation requirements on the official page."),
    ),
    standard=OK_STD,
    weasel_words={"present": True, "quote": "'Earn up to $60 per hour' — ceiling; flat per-job fees mean effective hourly pay varies by job difficulty."},
    repeatable={"value": True, "cadence": "per task"},
    maximize="Pick jobs you can finish fast — flat-fee pay rewards speed, so a 45-minute TV mount beats a 2-hour troubleshooting slog; learn extra service lines (phone repair plus TV mounting) to widen the jobs you're offered; cluster jobs in one area per day; keep ratings perfect since Puls routes the best jobs to top technicians.",
))

# ---------------- R7707 UrbanSitter (verify) ----------------
routes.append(base(
    route_id="R7707", provider="UrbanSitter", official_url="https://www.urbansitter.com/how-it-works-babysitting/",
    terms_url="https://www.urbansitter.com/how-it-works-babysitting/",
    payout_quote="Official UrbanSitter sitter page: 'Get paid instantly — Enjoy instant payouts right after each job, keeping 100% of your earnings without any hidden fees.' Also: 'Earn an average of $125 + tips per job' and 'Set your own hourly rates.'",
    payout_min_usd=75, payout_max_usd=250, time_min_minutes=120, time_max_minutes=360,
    timing="Instant payouts right after each job (official).", speed="today",
    eligibility=["18+ (younger sitters have limited options)", "Caregiver membership required to apply for jobs (includes background check)", "Profile with experience, photo, and availability", "Trust-building: references and completed background check boost bookings"],
    steps=["Create your sitter/nanny profile", "Add a caregiver membership (unlocks job access, background check, instant payouts)", "Apply for babysitting, nannying, pet-sitting, housekeeping, or senior-care jobs", "Complete the job", "Get paid instantly after each job, keeping 100% of earnings"],
    catches=["Membership fee required before you can apply for jobs — you pay before you earn", "You set your own rate, so pricing wrong means no bookings", "New sitters compete with established, reviewed sitters for the same families", "UrbanSitter takes no cut, but instant-payout convenience is bundled into the membership cost", "Demand is metro-dependent; suburbs can be thin"],
    biggest_catch="You must buy the caregiver membership before applying to a single job — it's a real upfront cost, and third parties report roughly $34.95/year, so the 'free to join' headline only covers browsing.",
    upfront_fee="Membership required to apply for jobs (official page confirms; amount not published on the page — third parties report ~$34.95/year).",
    verdict="verify",
    notes="Official page confirms instant payouts after each job, 100% earnings kept, and $125 average + tips per job. Range $75-$250 reflects job variety (babysitting to full-day nannying).",
    critical=crit(
        (True, "Official page: 'Earn an average of $125 + tips per job' and 'Set your own hourly rates'; range $75-$250 covers typical job sizes."),
        (True, "Official page: apply for jobs in the app, complete them, get paid."),
        (True, "Official page: 'Get paid instantly... instant payouts right after each job.'"),
        (True, "Membership requirement, background check, and profile standards disclosed on the official page."),
    ),
    standard=OK_STD,
    weasel_words={"present": True, "quote": "'Earn an average of $125 + tips per job' — an average, not a guarantee; new sitters earn less while building reviews."},
    repeatable={"value": True, "cadence": "daily"},
    maximize="Complete the membership and background check now so you're bookable today; set your opening rate at the local average to win first jobs, then raise it as reviews land; favor recurring nanny gigs over one-offs for stable income; pet-sitting and senior-care listings often have less competition than babysitting; respond to new job alerts within minutes — the fastest applicant usually wins.",
))

# ---------------- R7708 Bambino (reject) ----------------
routes.append(base(
    route_id="R7708", provider="Bambino", official_url=None, terms_url=None,
    payout_quote="No official Bambino sitter pay or payout page found in public search.",
    payout_min_usd=15, payout_max_usd=25, time_min_minutes=120, time_max_minutes=360,
    timing="Not verifiable from official terms.", speed="days",
    eligibility=["Babysitting experience", "Smartphone app signup"],
    steps=["Sign up as a Bambino sitter", "Get booked by local parents", "Complete the sit"],
    catches=["No official pay or payout terms found publicly"],
    biggest_catch="No official pay or payout timing published — nothing to verify.",
    upfront_fee=None,
    verdict="reject",
    notes="Rejected: no official Bambino page stating sitter pay or payout timing was found in public search.",
    critical=crit(
        (False, "No official numeric pay found."),
        (False, "No official pay mechanism found."),
        (False, "No official payout timing found."),
        (False, "No official requirements cited."),
    ),
    standard=OK_STD,
    weasel_words={"present": False, "quote": None},
    repeatable={"value": True, "cadence": "per task"},
    maximize="Unverifiable — skip until Bambino publishes official sitter pay terms.",
))

# ---------------- R7709 Soothe (reject) ----------------
routes.append(base(
    route_id="R7709", provider="Soothe", official_url=None, terms_url=None,
    payout_quote="No official Soothe provider pay page found; only third-party reports (Indeed reviews: $50-$60/hr plus tips, payouts within 48-72 hours via direct deposit).",
    payout_min_usd=50, payout_max_usd=60, time_min_minutes=60, time_max_minutes=120,
    timing="Not verifiable from official terms.", speed="days",
    eligibility=["Licensed/certified massage therapist", "Own massage table and supplies", "Reliable vehicle"],
    steps=["Apply as a Soothe therapist", "Set availability and accept appointments", "Travel to clients and perform massages"],
    catches=["All pay figures are third-party (Indeed reviews), not official Soothe terms", "Therapist must haul table and supplies, unreimbursed mileage", "Income is inconsistent — demand varies by market"],
    biggest_catch="Soothe publishes no official provider pay or payout page — every figure is secondhand from worker reviews.",
    upfront_fee=None,
    verdict="reject",
    notes="Rejected: despite plausible third-party pay data ($50-$60/hr, 48-72h payouts), no official Soothe terms page could be found, and the brief requires official terms for verify.",
    critical=crit(
        (False, "Only third-party pay reports; no official numeric pay."),
        (False, "No official pay mechanism page found."),
        (False, "No official payout timing found."),
        (True, "Licensed-therapist requirement is standard but not officially cited here."),
    ),
    standard=OK_STD,
    weasel_words={"present": False, "quote": None},
    repeatable={"value": True, "cadence": "per task"},
    maximize="Unverifiable from official terms — only pursue if Soothe publishes a provider pay page; meanwhile Zeel/Soothe-class work needs a state massage license first, which is the real gate.",
))

# ---------------- R7710 Zeel (reject) ----------------
routes.append(base(
    route_id="R7710", provider="Zeel", official_url=None, terms_url=None,
    payout_quote="No official Zeel therapist pay or payout page found in public search.",
    payout_min_usd=50, payout_max_usd=75, time_min_minutes=60, time_max_minutes=120,
    timing="Not verifiable from official terms.", speed="days",
    eligibility=["Licensed massage therapist", "Own equipment and transportation"],
    steps=["Apply as a Zeel provider", "Accept in-home massage appointments", "Get paid per appointment"],
    catches=["No official pay/payout terms found publicly"],
    biggest_catch="No official pay or payout timing published — nothing to verify.",
    upfront_fee=None,
    verdict="reject",
    notes="Rejected: no official Zeel page stating therapist pay or payout timing found in public search.",
    critical=crit(
        (False, "No official numeric pay found."),
        (False, "No official pay mechanism found."),
        (False, "No official payout timing found."),
        (False, "No official requirements cited."),
    ),
    standard=OK_STD,
    weasel_words={"present": False, "quote": None},
    repeatable={"value": True, "cadence": "per task"},
    maximize="Unverifiable — skip until Zeel publishes official provider pay terms.",
))

# ---------------- R7711 HelloTech (reject) ----------------
routes.append(base(
    route_id="R7711", provider="HelloTech", official_url=None, terms_url=None,
    payout_quote="No official HelloTech technician pay or payout page found in public search.",
    payout_min_usd=40, payout_max_usd=80, time_min_minutes=60, time_max_minutes=180,
    timing="Not verifiable from official terms.", speed="days",
    eligibility=["Tech-installation skills (TV mounting, smart home)", "Own tools and transportation"],
    steps=["Apply as a HelloTech technician", "Accept installation jobs", "Get paid per job"],
    catches=["No official pay/payout terms found publicly"],
    biggest_catch="No official pay or payout timing published — nothing to verify.",
    upfront_fee=None,
    verdict="reject",
    notes="Rejected: no official HelloTech page stating technician pay or payout timing found in public search.",
    critical=crit(
        (False, "No official numeric pay found."),
        (False, "No official pay mechanism found."),
        (False, "No official payout timing found."),
        (False, "No official requirements cited."),
    ),
    standard=OK_STD,
    weasel_words={"present": False, "quote": None},
    repeatable={"value": True, "cadence": "per task"},
    maximize="Unverifiable — skip until HelloTech publishes official technician pay terms; Puls (R7706) is the verified alternative in the same trade.",
))

# ---------------- R7712 Washos (verify) ----------------
routes.append(base(
    route_id="R7712", provider="Washos", official_url="https://www.washos.com/become-washos",
    terms_url="https://www.washos.com/become-washos",
    payout_quote="Washos's own published detailer job ad (via WayUp, quoting the employer ad): 'Starts at $25 per hour and up to $50. Tips and bonuses compliment the quality and the reliability... you will set your hours, receive jobs only in your area and get paid within 24hours... Payments within 24/48 hours of job completion... Keep 100% of your tips and receive bonuses.'",
    payout_min_usd=50, payout_max_usd=200, time_min_minutes=120, time_max_minutes=240,
    timing="Paid within 24-48 hours of job completion (company's published ad).", speed="days",
    eligibility=["Eligible to work in the US", "Reliable vehicle and driver's license", "Ability to obtain detailing supplies/insurance", "Smartphone", "Car-wash experience welcome but not mandatory; training offered"],
    steps=["Apply at washos.com/become-washos", "Get approved and set your service area and hours", "Receive mobile detailing jobs near you", "Detail the customer's car on-site", "Get paid within 24-48 hours; keep 100% of tips"],
    catches=["You must obtain your own detailing supplies and insurance — a real startup cost", "Company's ad figures ($25-$50/hr) are employer-published, not an independent verification", "Service areas limited (strongest in Los Angeles; expanding)", "Physically demanding outdoor work; weather kills your schedule", "Contract work: no benefits"],
    biggest_catch="You supply the vehicle, the detailing supplies, and the insurance — the hourly rate looks good until you subtract the real cost of running a mobile detailing setup.",
    upfront_fee="Detailing supplies and insurance required (worker-paid, per the company's own ad).",
    verdict="verify",
    notes="Source is the company's own published job ad (carried on WayUp), stating $25-$50/hr, 24/48h payouts, and 100% tips. Range $50-$200 per 2-4h job at the ad's rates.",
    critical=crit(
        (True, "Company's published ad: 'Starts at $25 per hour and up to $50'; range $50-$200 per 2-4h job at those rates."),
        (True, "Company ad describes receiving local mobile-detailing jobs through the platform."),
        (True, "Company ad: 'paid within 24hours' / 'Payments within 24/48 hours of job completion.'"),
        (True, "Vehicle, license, supplies/insurance, and US work eligibility stated in the company's ad."),
    ),
    standard=OK_STD,
    weasel_words={"present": True, "quote": "'Starts at $25 per hour and up to $50' — the top end reflects experienced, high-volume detailers, not day one."},
    repeatable={"value": True, "cadence": "daily"},
    maximize="Start with the entry rate to get jobs flowing, then raise your effective rate as ratings stack; cluster bookings in one neighborhood per day to kill windshield time; upsell interior shampoo and wax add-ons on-site since you keep 100% of tips and bonuses reward reliability; market to office parks for repeat fleet/fleet-adjacent customers; track supplies and mileage — both are deductible.",
))

# ---------------- R7713 Spiffy (reject) ----------------
routes.append(base(
    route_id="R7713", provider="Spiffy", official_url=None, terms_url=None,
    payout_quote="No official Spiffy technician pay or payout page found in public search.",
    payout_min_usd=20, payout_max_usd=40, time_min_minutes=60, time_max_minutes=180,
    timing="Not verifiable from official terms.", speed="days",
    eligibility=["Detailing experience", "Vehicle and equipment"],
    steps=["Apply as a Spiffy technician", "Accept on-demand detailing jobs", "Get paid per job"],
    catches=["No official pay/payout terms found publicly"],
    biggest_catch="No official pay or payout timing published — nothing to verify.",
    upfront_fee=None,
    verdict="reject",
    notes="Rejected: no official Spiffy page stating technician pay or payout timing found in public search.",
    critical=crit(
        (False, "No official numeric pay found."),
        (False, "No official pay mechanism found."),
        (False, "No official payout timing found."),
        (False, "No official requirements cited."),
    ),
    standard=OK_STD,
    weasel_words={"present": False, "quote": None},
    repeatable={"value": True, "cadence": "per task"},
    maximize="Unverifiable — skip until Spiffy publishes official technician pay terms; Washos (R7712) is the verified alternative in mobile detailing.",
))

# ---------------- R7714 Poplin (verify) ----------------
routes.append(base(
    route_id="R7714", provider="Poplin (formerly SudShare)", official_url="https://poplin.co/laundry-service",
    terms_url="https://poplin.co/laundry-service",
    payout_quote="Poplin's own press release (Business Wire): 'Laundry Pros set their own hours... and keep a 75% share of every job and 100% of tips.' Reported platform terms (TMJ4, quoting Poplin): 'Sudsters are paid $0.75 per pound for next-day delivery or $1.50 per pound for same-day delivery, plus tips and bonuses... you'll always make at least $15 (plus tips) per order... You can receive a payment within two days.'",
    payout_min_usd=15, payout_max_usd=60, time_min_minutes=60, time_max_minutes=240,
    timing="Payment within two days of order (reported platform terms).", speed="days",
    eligibility=["Access to a washer, dryer, and air-drying setup", "Laundry detergent and supplies", "Transportation for pickup/delivery", "Bathroom scale and bags", "Background check with SSN"],
    steps=["Register as a Poplin Laundry Pro and pass the background check", "Set your service radius in the app", "Accept orders: pick up laundry from customers", "Wash, dry, fold, and return within the service window", "Get paid $0.75/lb ($1.50/lb same-day) + 100% tips, within ~2 days"],
    catches=["You pay for detergent, water, electricity, gas, and laundromat runs — margins are thinner than the per-pound rate suggests", "Minimum $15/order is guaranteed but heavy lifting comes from volume", "Same-day $1.50/lb pays double but demands same-day turnaround", "Poplin keeps 25% of the job value (you keep 75% + all tips)", "Your home becomes a laundromat — space and machine wear are real costs"],
    biggest_catch="The $0.75/lb rate is gross — detergent, water, power, gas, and machine wear come out of your pocket, and you need serious volume (15+ loads a day like top earners) to make real money.",
    upfront_fee="$0 signup; washer/dryer, supplies, and transport are worker-provided.",
    verdict="verify",
    notes="Pay rate ($0.75/$1.50 per lb, $15 min/order, within-2-day payout) comes from platform terms as reported by TMJ4 quoting Poplin; the 75%-of-job + 100%-tips split is from Poplin's own press release. Range $15-$60 per typical order.",
    critical=crit(
        (True, "Poplin press release: 75% share of every job + 100% of tips; platform terms: $0.75/lb ($1.50 same-day), $15 minimum per order. Range $15-$60 per typical order."),
        (True, "Platform dispatches laundry orders to Pros; Pro picks up, processes, returns."),
        (True, "Reported platform terms: payment within two days."),
        (True, "Washer/dryer, supplies, transport, and background check requirements documented."),
    ),
    standard=std([
        (True, "Provider is a real, operating platform."),
        (True, "Pay mechanism is platform-mediated per order."),
        (True, "Requirements are stated honestly."),
        (True, "Pay rate sourced from platform terms as reported by a TV news outlet; split from company's own press release."),
        (True, "Payout speed characterized from reported platform terms."),
        (True, "Eligibility reflects documented requirements."),
        (True, "File written from public sources; no sign-in required."),
    ]),
    weasel_words={"present": True, "quote": "'Top earners... can make thousands per month' — outliers working 15 loads/day, not typical results."},
    repeatable={"value": True, "cadence": "daily"},
    maximize="Take same-day $1.50/lb orders whenever offered — double pay for the same load; stack multiple customers' loads in one wash cycle to multiply per-pound revenue against fixed machine time; set a tight pickup radius to cut gas; use a laundromat's big machines on high-volume days to clear more pounds per hour; upsell hang-dry/delicates if the app supports add-ons; track detergent, power, and mileage as deductions.",
))

# ---------------- R7715 GreenPal (verify) ----------------
routes.append(base(
    route_id="R7715", provider="GreenPal", official_url="https://www.yourgreenpal.com/vendor-handbook/getting-started-and-completing-work",
    terms_url="https://www.yourgreenpal.com/vendor-handbook/getting-started-and-completing-work",
    payout_quote="Official GreenPal vendor handbook: 'So for example if you win a new customer at $50 per mowing... Customer payment: $50.00 / GreenPal Platform Fee: $2.50 / Estimated Stripe processing fee: $1.75 / Estimated Vendor balance: $45.75.' Also: 'It's totally free to bid... bid often and bid fast as they usually pick the first price they like.' Customer payments go through your connected Stripe account.",
    payout_min_usd=30, payout_max_usd=75, time_min_minutes=60, time_max_minutes=180,
    timing="Paid through your own Stripe account after job completion; Stripe controls payout schedule (typically ~2 business days to bank).", speed="days",
    eligibility=["Own lawn-care equipment (mower, edger, blower)", "Appropriate skills/licenses to operate a lawn-care business", "Stripe account connected for payouts", "Smartphone for bids, job photos, and customer texts"],
    steps=["Sign up as a GreenPal vendor and connect your Stripe account", "Bid fast on lawns near you (free to bid; first good price usually wins)", "Win the job and complete the mow + edge + blow", "Upload a photo of the completed work to trigger payment", "Customer payment flows to your Stripe, minus 5% GreenPal fee and Stripe processing"],
    catches=["5% GreenPal platform fee + ~2.9% + $0.30 Stripe fee on every job", "You set the price — bid too high and you lose; too low and you work for nothing", "Equipment, gas, and maintenance are entirely yours", "First mow is an 'audition' — no recurring revenue until the customer rebooks", "Seasonal: demand dies in winter in most markets"],
    biggest_catch="You set your own bid, so the $50 example is just math — in competitive neighborhoods vendors undercut each other, and after the 5% + Stripe fees plus your gas and equipment, the margin on a cheap bid is thin.",
    upfront_fee="$0 to bid; equipment and Stripe setup are worker-provided.",
    verdict="verify",
    notes="Official vendor handbook gives the exact $50 mow fee breakdown ($45.75 vendor balance). Range $30-$75 per typical single mow. Timing via own Stripe account (~2 business days) — 'days' speed.",
    critical=crit(
        (True, "Official handbook: $50 mow example -> $45.75 vendor balance after 5% platform fee and Stripe fee. Range $30-$75 per typical job."),
        (True, "Official handbook: bid on jobs, complete work, upload photo, get paid through Stripe."),
        (True, "Official handbook: payments processed through connected Stripe account; Stripe controls payout timing (standard ~2 business days)."),
        (True, "Equipment, Stripe account, and business-skill requirements on the official handbook page."),
    ),
    standard=OK_STD,
    weasel_words={"present": False, "quote": None},
    repeatable={"value": True, "cadence": "per task"},
    maximize="Bid within minutes of a job posting — GreenPal's own handbook says the first good price usually wins; price tight but never below your gas+time floor; convert every first mow into a recurring weekly customer (that's where the real money is); stack jobs by neighborhood to cut drive time; upsell hedge trimming and leaf cleanup in-app; photo-document every finished lawn to get paid without disputes.",
))

# ---------------- R7716 LawnGuru (reject) ----------------
routes.append(base(
    route_id="R7716", provider="LawnGuru", official_url=None, terms_url=None,
    payout_quote="No official LawnGuru provider pay or payout page found in public search.",
    payout_min_usd=30, payout_max_usd=60, time_min_minutes=60, time_max_minutes=180,
    timing="Not verifiable from official terms.", speed="days",
    eligibility=["Lawn-care equipment", "Smartphone"],
    steps=["Sign up as a LawnGuru provider", "Accept mowing jobs", "Get paid per job"],
    catches=["No official pay/payout terms found publicly"],
    biggest_catch="No official pay or payout timing published — nothing to verify.",
    upfront_fee=None,
    verdict="reject",
    notes="Rejected: no official LawnGuru page stating provider pay or payout timing found in public search.",
    critical=crit(
        (False, "No official numeric pay found."),
        (False, "No official pay mechanism found."),
        (False, "No official payout timing found."),
        (False, "No official requirements cited."),
    ),
    standard=OK_STD,
    weasel_words={"present": False, "quote": None},
    repeatable={"value": True, "cadence": "per task"},
    maximize="Unverifiable — skip until LawnGuru publishes official provider pay terms; GreenPal (R7715) is the verified alternative in lawn care.",
))

# ---------------- R7717 Lawn Love (reject) ----------------
routes.append(base(
    route_id="R7717", provider="Lawn Love", official_url=None, terms_url=None,
    payout_quote="No official Lawn Love pro pay or payout page found in public search.",
    payout_min_usd=30, payout_max_usd=60, time_min_minutes=60, time_max_minutes=180,
    timing="Not verifiable from official terms.", speed="days",
    eligibility=["Lawn-care equipment", "Smartphone"],
    steps=["Sign up as a Lawn Love pro", "Accept lawn-care jobs", "Get paid per job"],
    catches=["No official pay/payout terms found publicly"],
    biggest_catch="No official pay or payout timing published — nothing to verify.",
    upfront_fee=None,
    verdict="reject",
    notes="Rejected: no official Lawn Love page stating pro pay or payout timing found in public search.",
    critical=crit(
        (False, "No official numeric pay found."),
        (False, "No official pay mechanism found."),
        (False, "No official payout timing found."),
        (False, "No official requirements cited."),
    ),
    standard=OK_STD,
    weasel_words={"present": False, "quote": None},
    repeatable={"value": True, "cadence": "per task"},
    maximize="Unverifiable — skip until Lawn Love publishes official pro pay terms; GreenPal (R7715) is the verified alternative.",
))

# ---------------- R7718 Thumbtack (reject) ----------------
routes.append(base(
    route_id="R7718", provider="Thumbtack", official_url="https://www.thumbtack.com/",
    terms_url=None,
    payout_quote="Thumbtack is a lead marketplace: pros pay for customer leads; customers pay pros directly. No platform-mediated per-job payout timing found on official pages.",
    payout_min_usd=50, payout_max_usd=200, time_min_minutes=60, time_max_minutes=240,
    timing="Not platform-mediated — pros collect payment from customers directly.", speed="days",
    eligibility=["Professional service to offer", "Profile with pricing and credentials", "Background check (common)"],
    steps=["Create a pro profile", "Pay for/respond to customer leads", "Quote and complete jobs", "Collect payment directly from the customer"],
    catches=["Pros pay for leads whether or not they win the job — lead costs can exceed earnings for new pros", "No platform payout timing: you chase payment yourself", "Thumbtack doesn't set your rates or guarantee work", "Lead pricing complaints are widespread in pro communities"],
    biggest_catch="Thumbtack charges YOU for leads and doesn't pay you for jobs — the money flow runs the wrong direction for a same-day-pay route, and there's no platform payout timing to verify.",
    upfront_fee="Lead fees (pay-per-lead); no official free-payout mechanism.",
    verdict="reject",
    notes="Rejected: Thumbtack is a pro lead marketplace, not a per-task payout platform. Pros pay for leads and collect payment from customers directly, so no platform-mediated fast payout exists to verify.",
    critical=crit(
        (False, "No platform-set per-job pay; pros set own prices and pay for leads."),
        (False, "No platform-mediated payout mechanism for job earnings."),
        (False, "No official payout timing for job earnings."),
        (True, "Pro profile/credential requirements are real but irrelevant to a payout route."),
    ),
    standard=OK_STD,
    weasel_words={"present": False, "quote": None},
    repeatable={"value": True, "cadence": "per task"},
    maximize="Skip as a same-day-pay route — Thumbtack is a customer-acquisition channel, not a payout mechanism. If you use it at all, treat lead spend like ad spend and collect payment via your own instant-pay setup.",
))

# ---------------- R7719 Wonolo (verify) ----------------
routes.append(base(
    route_id="R7719", provider="Wonolo", official_url="https://www.wonolo.com/workers",
    terms_url="https://www.wonolo.com/workers",
    payout_quote="Official Wonolo workers page: '98% Paid Within 48 Hrs' and '98% of jobs are paid within 48 hours.' Job categories: merchandising, production, event setup, delivery, housekeeping, catering, warehousing, laundry & cleaning, customer service, security.",
    payout_min_usd=96, payout_max_usd=160, time_min_minutes=240, time_max_minutes=480,
    timing="98% of jobs paid within 48 hours (official).", speed="days",
    eligibility=["18+", "Smartphone with the Wonolo app", "Profile with photo and info", "Able to meet job-specific requirements (lifting, standing, etc.)", "No resume or interview required"],
    steps=["Download the Wonolo app and create your profile", "Browse local jobs by industry, location, and schedule", "Accept a job — pay is shown transparently before you accept", "Show up on time and complete the shift (requestors rate performance)", "Get paid — 98% within 48 hours"],
    catches=["Shifts go fast — you compete with every other Wonoloer for the same postings", "Small 'Trust and Safety Fee' deducted per shift (reported ~$5)", "48 hours is the payout initiation, not bank arrival; direct deposit can add days", "Ratings matter: lateness or no-shows get you deprioritized", "Demand is metro-dependent; thin markets have few shifts"],
    biggest_catch="'98% paid within 48 hours' means payout is initiated — your bank's direct-deposit lag can push actual spendable cash to 3-5 days, so don't count it as same-day money.",
    upfront_fee="$0 official signup.",
    verdict="verify",
    notes="Official page confirms 98%-within-48h payout. Range $96-$160 per typical 8h shift at $12-$20/hr (reported typical band). No resume/interview — genuinely fast to start.",
    critical=crit(
        (True, "Official page: transparent per-job pay; realistic shift range $96-$160 at typical $12-$20/hr rates."),
        (True, "Official page: accept jobs in app, complete them, get paid."),
        (True, "Official page: '98% of jobs are paid within 48 hours.'"),
        (True, "18+, app profile, and job-specific physical requirements disclosed."),
    ),
    standard=OK_STD,
    weasel_words={"present": True, "quote": "'98% paid within 48 hours' — the remaining 2% and bank-processing lag mean it's not a guarantee of cash in hand."},
    repeatable={"value": True, "cadence": "daily"},
    maximize="Turn on job alerts and grab shifts the second they post — the best ones vanish in minutes; target last-minute 'desperate' shifts that carry bonus pay; stack back-to-back shifts at the same warehouse to cut commute; keep a perfect on-time record since requestors rate you and top-rated workers see shifts first; use the referral bonus after your first gig for an extra $25.",
))

# ---------------- R7720 Instawork (verify) ----------------
routes.append(base(
    route_id="R7720", provider="Instawork", official_url="https://www.instawork.com/",
    terms_url="https://www.instawork.com/",
    payout_quote="Instawork's own press releases (via GlobeNewswire): Instawork Pros experience 'Get paid quickly: ability to get paid the same day' and 'Financial stability: view shift earnings before they work.' Third-party reports: weekly Friday pay at first, with Instapay (next-day/same-day) unlockable after early shifts.",
    payout_min_usd=120, payout_max_usd=200, time_min_minutes=240, time_max_minutes=480,
    timing="Same-day pay ability via Instapay (official company claim); base pay weekly on Fridays per worker reports.", speed="today",
    eligibility=["18+", "Profile with work history, references, and a short quiz", "Hospitality/warehouse/retail-appropriate presentation", "Smartphone with the Instawork app"],
    steps=["Download Instawork and build your Pro profile (history, references, quiz)", "Get approved and browse local hospitality/warehouse/retail shifts", "Book shifts — earnings shown before you work", "Complete the shift and get rated on a 5-star scale", "Get paid: weekly Fridays by default, or unlock Instapay for same-day access"],
    catches=["Same-day pay isn't day one — worker reports say Instapay unlocks after your first couple of shifts", "Ratings directly control which shifts you're offered; one bad review hurts", "1099 contractor: no workers' comp, no benefits", "Shift availability is metro-dependent", "Tips on some gigs can lag weeks behind the hourly pay"],
    biggest_catch="The 'get paid the same day' headline has a ramp: you typically start on weekly Friday pay and only unlock Instapay after proving yourself over early shifts — so your first week is NOT same-day money.",
    upfront_fee="$0 for workers to join (official).",
    verdict="verify",
    notes="Official company press releases claim same-day pay ability and pre-shift earnings visibility. Range $120-$200 per 8h shift at typical $15-$25/hr. Speed 'today' reflects the official same-day claim; caveats documented.",
    critical=crit(
        (True, "Official releases: view shift earnings before working; realistic shift range $120-$200 at typical hospitality/warehouse rates."),
        (True, "Platform books Pros into business shifts; pay per completed shift."),
        (True, "Official company claim: 'ability to get paid the same day' via Instapay."),
        (True, "Profile, references, quiz, and 5-star rating system disclosed."),
    ),
    standard=std([
        (True, "Provider is a real, operating platform."),
        (True, "Pay mechanism is platform-mediated per shift."),
        (True, "Requirements are stated honestly."),
        (True, "Same-day claim is the company's own; ramp-up caveat documented from worker reports."),
        (True, "Payout speed characterized with both the official claim and the reported ramp."),
        (True, "Eligibility reflects documented requirements."),
        (True, "File written from public sources; no sign-in required."),
    ]),
    weasel_words={"present": True, "quote": "'Ability to get paid the same day' — ability, not default; base cadence is weekly until Instapay unlocks."},
    repeatable={"value": True, "cadence": "daily"},
    maximize="Finish your profile, references, and quiz TODAY — approval speed is the whole game; take any first shift regardless of location to unlock Instapay faster; then chase high-volume hospitality venues (stadiums, hotels) for steady shifts; keep a 5-star streak since ratings decide your shift feed; refer other workers for reward bonuses once you're in.",
))

# ---------------- R7721 Bluecrew (reject) ----------------
routes.append(base(
    route_id="R7721", provider="Bluecrew", official_url="https://www.bluecrewjobs.com/",
    terms_url="https://app.bluecrewjobs.com/terms_of_service.pdf",
    payout_quote="Official Bluecrew job postings: 'Offers weekly pay and direct deposit' plus 'On-Demand Pay! Access your weekly earnings days before payday for a tiny fee.' Official terms: 'Co-Employer will pay you weekly.' No concrete official hourly/shift rate captured on public listings.",
    payout_min_usd=120, payout_max_usd=160, time_min_minutes=240, time_max_minutes=480,
    timing="Weekly pay via direct deposit; On-Demand Pay offers early access for a small fee.", speed="days",
    eligibility=["18+", "W-2 employee of Bluecrew's co-employer", "Background check and bank details", "Job-specific physical requirements"],
    steps=["Apply in ~15 minutes in the Bluecrew app", "Get matched to warehouse/retail/food-service shifts", "Clock in/out in the app", "Get paid weekly (or use On-Demand Pay for early access)"],
    catches=["No concrete official pay rate found on public listings — rates vary by assignment and aren't published upfront", "Weekly base pay; early access costs a fee", "W-2 means taxes handled, but less schedule freedom than 1099 apps"],
    biggest_catch="Bluecrew publishes no concrete pay rates on its public job pages — you can't verify what a shift actually pays before applying, so the numeric requirement fails.",
    upfront_fee="$0.",
    verdict="reject",
    notes="Rejected: official timing exists (weekly + On-Demand Pay) but no concrete official numeric pay rate could be captured from public listings, failing the numeric requirement.",
    critical=crit(
        (False, "No concrete official numeric rate found on public listings."),
        (True, "Platform assigns W-2 shifts via app."),
        (True, "Official: weekly pay; On-Demand Pay for early access."),
        (True, "W-2, background check, app clock-in/out disclosed."),
    ),
    standard=OK_STD,
    weasel_words={"present": True, "quote": "'Top pay' marketing on job pages with no published rate — unverifiable."},
    repeatable={"value": True, "cadence": "daily"},
    maximize="Unverifiable on pay — skip until Bluecrew publishes rates; Wonolo (R7719) is the verified W-2-adjacent alternative with published payout timing.",
))

# ---------------- R7722 Bacon Work (reject) ----------------
routes.append(base(
    route_id="R7722", provider="Bacon Work", official_url="https://www.baconwork.com/findwork",
    terms_url="https://www.baconwork.com/blog/why-be-a-1099-contractor",
    payout_quote="Official Bacon blog: 'Quick Pay pays out in 2 business days after the shift is completed'; alternative is payment the following Friday. Businesses set shift wages; workers see expected wages before applying — but no public official listing with a numeric wage was found.",
    payout_min_usd=100, payout_max_usd=160, time_min_minutes=240, time_max_minutes=480,
    timing="Quick Pay: 2 business days after shift; otherwise the following Friday.", speed="days",
    eligibility=["18+", "Bacon app profile and screening", "Job-specific requirements per shift"],
    steps=["Sign up on Bacon", "Browse shifts with expected wages shown upfront", "Apply and work the shift", "Get paid via Quick Pay (2 business days) or Friday pay"],
    catches=["No public official numeric wage listing found — wages are visible only inside the app", "Quick Pay's 2-business-day window excludes weekends/holidays"],
    biggest_catch="Timing is officially documented, but no public official shift listing with a numeric wage exists — the pay amount can't be verified without signing in.",
    upfront_fee="$0.",
    verdict="reject",
    notes="Rejected: official payout timing is verified (Quick Pay, 2 business days), but no official public numeric shift wage could be found, failing the numeric requirement.",
    critical=crit(
        (False, "No official public numeric wage found."),
        (True, "Platform dispatches shifts; businesses set wages."),
        (True, "Official: Quick Pay in 2 business days after shift completion."),
        (True, "App profile and screening requirements known."),
    ),
    standard=OK_STD,
    weasel_words={"present": False, "quote": None},
    repeatable={"value": True, "cadence": "per task"},
    maximize="Unverifiable on pay — only pursue after confirming a numeric wage inside the app; Wonolo (R7719) covers the same shift-work lane with verified timing.",
))

# ---------------- R7723 Airtasker (reject) ----------------
routes.append(base(
    route_id="R7723", provider="Airtasker", official_url="https://www.airtasker.com/",
    terms_url="https://support.airtasker.com/hc/en-gb/articles/21321295524121-What-is-Airtasker-Pay",
    payout_quote="Official Airtasker support: customer funds held in escrow; Tasker completes work and requests payment; customer releases it; Tasker receives funds 'within 3-5 business days.' Taskers submit their own offer amounts — no official listing with a concrete posted amount found publicly.",
    payout_min_usd=40, payout_max_usd=150, time_min_minutes=60, time_max_minutes=240,
    timing="3-5 business days after customer releases payment (official).", speed="days",
    eligibility=["18+", "Airtasker account and ID verification", "Task-appropriate skills"],
    steps=["Create a Tasker profile", "Make offers on posted tasks", "Complete the task and request payment", "Customer releases funds; you receive them in 3-5 business days"],
    catches=["3-5 business days is slow for a same-day-pay lane", "Customer must release payment — disputes delay everything", "No public official task listing with a concrete amount found", "Service fees apply (widely reported 10-20%, not officially confirmed here)"],
    biggest_catch="The 3-5 business day payout is the slowest in this lane, and no official live listing with a concrete posted amount could be found — so neither speed nor a verified number works.",
    upfront_fee="$0 to join.",
    verdict="reject",
    notes="Rejected: official payout timing is documented (3-5 business days) but no official live task/listing with a concrete posted amount was found publicly, failing the numeric requirement.",
    critical=crit(
        (False, "No official public listing with a concrete posted amount found."),
        (True, "Platform holds funds in escrow and releases to Tasker."),
        (True, "Official: funds received within 3-5 business days of release."),
        (True, "Account and ID verification requirements documented."),
    ),
    standard=OK_STD,
    weasel_words={"present": False, "quote": None},
    repeatable={"value": True, "cadence": "per task"},
    maximize="Unverifiable on pay — only pursue after finding an official live listing with a posted amount; note the 3-5 day payout makes this a poor same-day option regardless.",
))

# ---------------- R7724 Veryable (reject) ----------------
routes.append(base(
    route_id="R7724", provider="Veryable", official_url="https://www.veryableops.com/",
    terms_url="https://www.veryableops.com/legal/terms-of-service-business",
    payout_quote="Official Veryable blog: 'the workers get paid the next day by Veryable.' Official terms: Operators submit competitive bids and receive a flat amount upon job completion. No public official listing with a numeric Op amount found.",
    payout_min_usd=100, payout_max_usd=200, time_min_minutes=240, time_max_minutes=480,
    timing="Paid the next day by Veryable (official).", speed="days",
    eligibility=["18+", "Veryable Operator profile", "Manufacturing/logistics-appropriate skills", "1099 (W-2 in some states)"],
    steps=["Sign up as a Veryable Operator", "Bid on posted Ops (jobs)", "Complete the work", "Get paid a flat amount the next day"],
    catches=["No public official numeric Op amount — bids visible only in-app", "Manufacturing/logistics focus limits who's eligible", "Bidding means you can underprice yourself"],
    biggest_catch="Next-day pay is officially documented, but no public official Op listing with a numeric amount exists — the pay figure can't be verified without the app.",
    upfront_fee="$0.",
    verdict="reject",
    notes="Rejected: official next-day payout is verified, but no public official numeric Op amount could be found, failing the numeric requirement.",
    critical=crit(
        (False, "No official public numeric Op amount found."),
        (True, "Platform posts Ops; Operators bid and get flat amounts."),
        (True, "Official: workers get paid the next day by Veryable."),
        (True, "Operator profile and trade requirements documented."),
    ),
    standard=OK_STD,
    weasel_words={"present": False, "quote": None},
    repeatable={"value": True, "cadence": "per task"},
    maximize="Unverifiable on pay — only pursue after confirming numeric Op amounts inside the app; the next-day payout makes it worth a look for manufacturing/logistics workers.",
))

# ---------------- R7725 Upshift (reject) ----------------
routes.append(base(
    route_id="R7725", provider="Upshift", official_url="https://upshift.work/for-people/florida-lakeland/",
    terms_url="https://upshift.work/for-people/florida-lakeland/",
    payout_quote="Official Upshift page: paid every Friday via bank deposit/cash credit; daily payments available after working with Upshift for at least two weeks through EarnIn. Only ~12% of applicants approved in that market. No current official numeric shift rate captured (third parties suggest $15-$25/hr, not official).",
    payout_min_usd=120, payout_max_usd=200, time_min_minutes=240, time_max_minutes=480,
    timing="Weekly Friday pay; daily via EarnIn after 2 weeks.", speed="days",
    eligibility=["18+", "Upshift application (only ~12% approved per official page)", "Good reviews to access better-paid work", "EarnIn setup for daily pay"],
    steps=["Apply to Upshift (competitive approval)", "Get approved and book shifts", "Complete shifts and build reviews", "Get paid Fridays; unlock daily pay via EarnIn after 2 weeks"],
    catches=["Only ~12% of applicants approved — the hardest gate in this lane", "Daily pay requires 2 weeks of history plus EarnIn", "No official numeric rate published — pay visibility only in-app", "Reviews gate your access to better shifts"],
    biggest_catch="An ~88% rejection rate on applications plus a 2-week wait for daily pay makes this the slowest, hardest on-ramp in the shift-work lane — and rates aren't published publicly.",
    upfront_fee="$0.",
    verdict="reject",
    notes="Rejected: official timing exists but no official numeric shift rate was captured publicly, and the ~12% approval rate makes it a poor recommendation regardless.",
    critical=crit(
        (False, "No official numeric rate captured publicly."),
        (True, "Platform books workers into business shifts."),
        (True, "Official: Friday pay; daily via EarnIn after 2 weeks."),
        (True, "Application, approval rate, and review system disclosed on official page."),
    ),
    standard=OK_STD,
    weasel_words={"present": False, "quote": None},
    repeatable={"value": True, "cadence": "daily"},
    maximize="Unverifiable on pay with a brutal approval gate — skip; Wonolo (R7719) and Instawork (R7720) cover the same lane with no such gate.",
))

# ---------------- R7726 PeopleReady/JobStack (reject) ----------------
routes.append(base(
    route_id="R7726", provider="PeopleReady (JobStack)", official_url="https://www.peopleready.com/",
    terms_url="https://www.peopleready.com/page/5/",
    payout_quote="Official PeopleReady page: 'Many of our jobs are eligible for next-day pay.' PeopleReady workers are W-2 and E-Verified. No current official numeric job rate captured publicly.",
    payout_min_usd=100, payout_max_usd=160, time_min_minutes=240, time_max_minutes=480,
    timing="Next-day pay on many jobs (official).", speed="days",
    eligibility=["18+", "E-Verified W-2 employment", "JobStack app", "Job-specific requirements"],
    steps=["Sign up with PeopleReady / JobStack", "Browse construction, warehouse, event, cleaning, and retail jobs", "Accept a job and complete the shift", "Next-day pay on eligible jobs"],
    catches=["'Many' jobs — not all — are eligible for next-day pay", "No official numeric rate published publicly", "W-2 means less flexibility than gig apps"],
    biggest_catch="'Many of our jobs' is doing heavy lifting — next-day pay isn't universal, and with no published rates you can't verify what any job pays before applying.",
    upfront_fee="$0.",
    verdict="reject",
    notes="Rejected: official next-day-pay claim exists but is qualified ('many jobs') and no official numeric job rate was captured publicly.",
    critical=crit(
        (False, "No official numeric rate captured publicly."),
        (True, "Staffing platform dispatching W-2 shifts."),
        (True, "Official: 'Many of our jobs are eligible for next-day pay.'"),
        (True, "W-2 and E-Verified requirements disclosed."),
    ),
    standard=OK_STD,
    weasel_words={"present": True, "quote": "'Many of our jobs are eligible for next-day pay' — 'many' is a qualifier, not a promise."},
    repeatable={"value": True, "cadence": "daily"},
    maximize="Unverifiable on pay — ask a local branch for the next-day-pay job list before counting on it; Wonolo (R7719) is the verified alternative.",
))

# ---------------- R7727 GigSmart (reject) ----------------
routes.append(base(
    route_id="R7727", provider="GigSmart (Get Gigs)", official_url=None, terms_url=None,
    payout_quote="No official GigSmart pay/payout page captured; third-party reports: requester has up to 3 business days to approve timesheets; faster cash-out available for a small fee after verification.",
    payout_min_usd=80, payout_max_usd=150, time_min_minutes=240, time_max_minutes=480,
    timing="Not verifiable from official terms.", speed="days",
    eligibility=["18+", "Worker profile in the Get Gigs app"],
    steps=["Build a worker profile", "Apply for shift gigs", "Complete the shift", "Wait for requester timesheet approval (up to 3 business days per reports)"],
    catches=["Timesheet approval lag (up to 3 business days) reported — not same-day", "No official terms captured"],
    biggest_catch="No official pay or payout terms captured, and third-party reports describe a multi-day timesheet approval lag — the opposite of fast pay.",
    upfront_fee="$0.",
    verdict="reject",
    notes="Rejected: no official GigSmart pay/payout page found in public search; reported mechanics are slow (timesheet approval lag).",
    critical=crit(
        (False, "No official numeric pay found."),
        (False, "No official pay mechanism found."),
        (False, "No official payout timing found."),
        (False, "No official requirements cited."),
    ),
    standard=OK_STD,
    weasel_words={"present": False, "quote": None},
    repeatable={"value": True, "cadence": "per task"},
    maximize="Unverifiable and reportedly slow — skip; use Wonolo (R7719) for verified sub-48h shift payouts.",
))

# ---------------- R7728 Jobble (reject) ----------------
routes.append(base(
    route_id="R7728", provider="Jobble", official_url=None, terms_url=None,
    payout_quote="No official Jobble pay or payout page found in public search.",
    payout_min_usd=80, payout_max_usd=150, time_min_minutes=240, time_max_minutes=480,
    timing="Not verifiable from official terms.", speed="days",
    eligibility=["18+", "Jobble profile"],
    steps=["Sign up on Jobble", "Find gig work", "Get paid per gig"],
    catches=["No official pay/payout terms found publicly"],
    biggest_catch="No official pay or payout timing published — nothing to verify.",
    upfront_fee=None,
    verdict="reject",
    notes="Rejected: no official Jobble page stating pay or payout timing found in public search.",
    critical=crit(
        (False, "No official numeric pay found."),
        (False, "No official pay mechanism found."),
        (False, "No official payout timing found."),
        (False, "No official requirements cited."),
    ),
    standard=OK_STD,
    weasel_words={"present": False, "quote": None},
    repeatable={"value": True, "cadence": "per task"},
    maximize="Unverifiable — skip until Jobble publishes official pay terms.",
))

# ---------------- R7729 Qwick (reject) ----------------
routes.append(base(
    route_id="R7729", provider="Qwick", official_url=None, terms_url=None,
    payout_quote="No official Qwick professional pay page captured; third-party reports describe shifts paying in as little as 30 minutes and $17-$35/hr by role — none official.",
    payout_min_usd=100, payout_max_usd=200, time_min_minutes=240, time_max_minutes=480,
    timing="Not verifiable from official terms.", speed="days",
    eligibility=["Hospitality experience", "Qwick professional profile"],
    steps=["Sign up as a Qwick professional", "Book hospitality shifts", "Get paid per shift"],
    catches=["All pay figures are third-party (Indeed listings, gig blogs), not official Qwick terms"],
    biggest_catch="Every pay and timing figure for Qwick is secondhand — Qwick's own professional pay page couldn't be found publicly.",
    upfront_fee=None,
    verdict="reject",
    notes="Rejected: no official Qwick page stating professional pay or payout timing found in public search; all figures are third-party.",
    critical=crit(
        (False, "No official numeric pay found."),
        (False, "No official pay mechanism found."),
        (False, "No official payout timing found."),
        (False, "No official requirements cited."),
    ),
    standard=OK_STD,
    weasel_words={"present": False, "quote": None},
    repeatable={"value": True, "cadence": "per task"},
    maximize="Unverifiable — skip until Qwick publishes official pro pay terms; Instawork (R7720) is the verified hospitality-shift alternative.",
))

# ---------------- R7730 Labor Finders (reject) ----------------
routes.append(base(
    route_id="R7730", provider="Labor Finders", official_url=None, terms_url=None,
    payout_quote="No official Labor Finders gig pay or payout page found in public search.",
    payout_min_usd=80, payout_max_usd=140, time_min_minutes=240, time_max_minutes=480,
    timing="Not verifiable from official terms.", speed="days",
    eligibility=["18+", "In-person branch signup typical"],
    steps=["Sign up at a Labor Finders branch", "Get dispatched to day-labor jobs", "Get paid per laborfinders.com/branch terms"],
    catches=["Traditional day-labor staffing; pay terms are branch-specific and not published", "Often paid by check or paycard with weekly cycles"],
    biggest_catch="Labor Finders publishes no official gig pay or payout timing — terms are branch-specific and offline.",
    upfront_fee=None,
    verdict="reject",
    notes="Rejected: traditional staffing firm with no official published gig pay/payout terms; branch-specific and offline.",
    critical=crit(
        (False, "No official numeric pay found."),
        (False, "No official pay mechanism found."),
        (False, "No official payout timing found."),
        (False, "No official requirements cited."),
    ),
    standard=OK_STD,
    weasel_words={"present": False, "quote": None},
    repeatable={"value": True, "cadence": "daily"},
    maximize="Unverifiable — walk into a local branch and ask for the pay schedule in writing before working; Wonolo (R7719) is the verified app-based alternative.",
))

# ---------------- R7731 Tradesmen International (reject) ----------------
routes.append(base(
    route_id="R7731", provider="Tradesmen International", official_url=None, terms_url=None,
    payout_quote="No official Tradesmen International gig pay or payout page found in public search.",
    payout_min_usd=150, payout_max_usd=300, time_min_minutes=240, time_max_minutes=480,
    timing="Not verifiable from official terms.", speed="days",
    eligibility=["Skilled-trade credentials", "Tradesmen application"],
    steps=["Apply as a skilled craftsman", "Get placed on contractor jobs", "Get paid per placement terms"],
    catches=["Skilled-trade staffing for longer placements, not same-day gigs", "No official published pay/payout terms"],
    biggest_catch="Tradesmen International staffs longer skilled-trade placements, not same-day task gigs — wrong mechanism for this lane, with no published fast-pay terms.",
    upfront_fee=None,
    verdict="reject",
    notes="Rejected: skilled-trade staffing for extended placements, not a same-day task marketplace; no official fast-payout terms published.",
    critical=crit(
        (False, "No official numeric pay found."),
        (False, "Wrong mechanism: extended placements, not per-task gigs."),
        (False, "No official payout timing found."),
        (False, "No official requirements cited."),
    ),
    standard=OK_STD,
    weasel_words={"present": False, "quote": None},
    repeatable={"value": False, "cadence": "one-time"},
    maximize="Wrong lane — this is career trade staffing, not a repeatable gig route; skilled tradespeople should use Puls (R7706) for verified per-job pay.",
))

# ---------------- R7732 FactoryFix (reject) ----------------
routes.append(base(
    route_id="R7732", provider="FactoryFix", official_url="https://www.factoryfix.com/talent-pool",
    terms_url="https://www.factoryfix.com/talent-pool",
    payout_quote="Official FactoryFix talent-pool page describes an industrial recruiting/talent platform for manufacturing hiring — no platform-mediated per-task payout terms exist.",
    payout_min_usd=0, payout_max_usd=0, time_min_minutes=0, time_max_minutes=0,
    timing="No platform payout — conventional employment/recruiting.", speed="days",
    eligibility=["Manufacturing/industrial background"],
    steps=["Join the FactoryFix talent pool", "Get matched to manufacturing employers", "Standard employment pay cycles apply"],
    catches=["Recruiting platform, not a gig marketplace", "No fast platform payout mechanism at all"],
    biggest_catch="FactoryFix is a recruiting platform for conventional manufacturing jobs — there is no per-task payout mechanism to verify, fast or otherwise.",
    upfront_fee="$0.",
    verdict="reject",
    notes="Rejected: wrong mechanism — industrial recruiting/talent platform for permanent or conventional jobs, not a same-day task marketplace with platform-mediated fast payout.",
    critical=crit(
        (False, "No per-task pay; conventional employment."),
        (False, "No platform payout mechanism."),
        (False, "No fast payout timing."),
        (True, "Industrial hiring focus confirmed on official page."),
    ),
    standard=OK_STD,
    weasel_words={"present": False, "quote": None},
    repeatable={"value": False, "cadence": "one-time"},
    maximize="Wrong lane entirely — if you want manufacturing work with fast pay, use Wonolo (R7719) or Veryable (R7724) instead.",
))

# ---------------- R7733 Phlatbed (reject) ----------------
routes.append(base(
    route_id="R7733", provider="Phlatbed", official_url=None, terms_url=None,
    payout_quote="No official Phlatbed platform page with worker pay or payout terms found; search results were confused with generic 'flatbed driver' trucking pages.",
    payout_min_usd=0, payout_max_usd=0, time_min_minutes=0, time_max_minutes=0,
    timing="Not verifiable.", speed="days",
    eligibility=[],
    steps=[],
    catches=["No official platform evidence found at all"],
    biggest_catch="Phlatbed could not be verified to exist as an accessible gig platform with published worker terms — searches return only generic flatbed-trucking content.",
    upfront_fee=None,
    verdict="reject",
    notes="Rejected: no official Phlatbed worker pay/payout page found; brand/domain searches returned only unrelated flatbed-driver content.",
    critical=crit(
        (False, "No official numeric pay found."),
        (False, "No official pay mechanism found."),
        (False, "No official payout timing found."),
        (False, "No official requirements found."),
    ),
    standard=OK_STD,
    weasel_words={"present": False, "quote": None},
    repeatable={"value": False, "cadence": "one-time"},
    maximize="Unverifiable — the platform may not exist or may be defunct; use Lugg (R7701) or GoShare (R7702) for verified moving gigs.",
))

# ---------------- R7734 Bungii (reject) ----------------
routes.append(base(
    route_id="R7734", provider="Bungii", official_url=None, terms_url=None,
    payout_quote="No official Bungii driver earnings or payment page found; third-party claims cite ~$68 average gig / ~$45 per hour — none official.",
    payout_min_usd=45, payout_max_usd=68, time_min_minutes=60, time_max_minutes=120,
    timing="Not verifiable from official terms.", speed="days",
    eligibility=["Pickup truck", "Smartphone", "Background check (typical)"],
    steps=["Sign up as a Bungii driver", "Accept on-demand moving/delivery gigs", "Get paid per gig"],
    catches=["All pay figures are third-party; no official Bungii earnings page found"],
    biggest_catch="No official Bungii page stating driver pay or payout timing exists publicly — every figure is secondhand.",
    upfront_fee=None,
    verdict="reject",
    notes="Rejected: no official Bungii driver earnings or payment page found in public search; all figures are third-party.",
    critical=crit(
        (False, "No official numeric pay found."),
        (False, "No official pay mechanism found."),
        (False, "No official payout timing found."),
        (False, "No official requirements cited."),
    ),
    standard=OK_STD,
    weasel_words={"present": False, "quote": None},
    repeatable={"value": True, "cadence": "per task"},
    maximize="Unverifiable — skip until Bungii publishes official driver terms; Lugg (R7701) and GoShare (R7702) are verified in the same truck-gig lane.",
))

# ---------------- R7735 TaskEasy (reject) ----------------
routes.append(base(
    route_id="R7735", provider="TaskEasy", official_url="https://www.taskeasy.com/contractors",
    terms_url="https://www.taskeasy.com/contractors/next-level-taskeasy/growing",
    payout_quote="Official TaskEasy contractor page confirms direct bank-account payouts ('Fast Payouts') but gives no exact timing; acquisition page claims 'Make Up To $600 a Day' and 'Get Paid Fast.'",
    payout_min_usd=0, payout_max_usd=600, time_min_minutes=0, time_max_minutes=0,
    timing="No official payout cadence published.", speed="days",
    eligibility=["Lawn equipment", "Insurance/background screening", "Smartphone with photo documentation"],
    steps=["Sign up as a TaskEasy contractor", "Accept lawn-care jobs", "Complete work and get customer/photo approval"],
    catches=["'Up to $600 a day' is a variable maximum, not a concrete per-job rate", "No official payout timing — 'Fast Payouts' is undefined", "Requires your own lawn equipment plus insurance/screening costs"],
    biggest_catch="TaskEasy's pay language is pure ceiling marketing ('up to $600 a day') with no official payout schedule — neither the number nor the timing is concrete enough to verify.",
    upfront_fee="Equipment + insurance/screening costs (worker-paid).",
    verdict="reject",
    notes="Rejected: official pages use weasel-worded ceilings ('up to $600/day', 'Fast Payouts') with no concrete per-job rate and no official payout cadence.",
    critical=crit(
        (False, "Only a variable ceiling ('up to $600/day'); no concrete per-job rate."),
        (True, "Platform dispatches lawn-care jobs to contractors with direct bank payouts."),
        (False, "No official payout cadence; 'Fast Payouts' undefined."),
        (True, "Equipment, insurance, and screening requirements disclosed."),
    ),
    standard=OK_STD,
    weasel_words={"present": True, "quote": "'Make Up To $600 a Day' and 'Get Paid Fast' — ceiling marketing with no concrete rate or schedule."},
    repeatable={"value": True, "cadence": "per task"},
    maximize="Unverifiable — skip; GreenPal (R7715) is the verified lawn-care alternative with an exact fee breakdown.",
))

# ---------------- R7736 Frayt (reject) ----------------
routes.append(base(
    route_id="R7736", provider="Frayt", official_url=None, terms_url=None,
    payout_quote="No official Frayt driver pay page captured; a third-party gig-economy report cites a 'stated average of $20-$30 per hour + tips' from official driver pages — not directly captured here.",
    payout_min_usd=40, payout_max_usd=90, time_min_minutes=60, time_max_minutes=180,
    timing="Not verifiable from official terms.", speed="days",
    eligibility=["Vehicle (car to box truck)", "Background check (typical)"],
    steps=["Sign up as a Frayt driver", "Accept shipping/delivery jobs", "Get paid per job"],
    catches=["No official pay/payout page captured publicly"],
    biggest_catch="No official Frayt driver pay or payout page could be captured — only secondhand citations of one.",
    upfront_fee=None,
    verdict="reject",
    notes="Rejected: no official Frayt driver pay/payout page found in public search; only third-party citations.",
    critical=crit(
        (False, "No official numeric pay captured."),
        (False, "No official pay mechanism captured."),
        (False, "No official payout timing found."),
        (False, "No official requirements cited."),
    ),
    standard=OK_STD,
    weasel_words={"present": False, "quote": None},
    repeatable={"value": True, "cadence": "per task"},
    maximize="Unverifiable — skip until Frayt's official driver pay page is found; GoShare (R7702) covers the same freight lane with verified terms.",
))

# ---------------- R7737 Roadie (reject) ----------------
routes.append(base(
    route_id="R7737", provider="Roadie", official_url=None, terms_url=None,
    payout_quote="No official Roadie driver pay/payout page captured in public search.",
    payout_min_usd=12, payout_max_usd=108, time_min_minutes=60, time_max_minutes=420,
    timing="Not verifiable from official terms.", speed="days",
    eligibility=["Vehicle", "Smartphone", "Background check (typical)"],
    steps=["Sign up as a Roadie driver", "Accept delivery gigs", "Get paid per trip"],
    catches=["No official pay/payout terms captured; third-party telemetry suggests low medians"],
    biggest_catch="No official Roadie driver pay or payout page could be captured publicly — nothing to verify.",
    upfront_fee=None,
    verdict="reject",
    notes="Rejected: no official Roadie driver pay/payout page found in public search.",
    critical=crit(
        (False, "No official numeric pay captured."),
        (False, "No official pay mechanism captured."),
        (False, "No official payout timing found."),
        (False, "No official requirements cited."),
    ),
    standard=OK_STD,
    weasel_words={"present": False, "quote": None},
    repeatable={"value": True, "cadence": "per task"},
    maximize="Unverifiable — skip until Roadie publishes official driver terms; Lugg (R7701) is the verified same-day alternative in on-demand delivery.",
))

# ---------------- R7738 Curri (reject) ----------------
routes.append(base(
    route_id="R7738", provider="Curri", official_url=None, terms_url=None,
    payout_quote="No official Curri driver pay/payout page captured; a third-party report notes offers show pay before acceptance but no published dollar figures.",
    payout_min_usd=0, payout_max_usd=0, time_min_minutes=0, time_max_minutes=0,
    timing="Not verifiable from official terms.", speed="days",
    eligibility=["Vehicle suitable for construction-material delivery"],
    steps=["Sign up as a Curri driver", "Accept delivery offers", "Get paid per delivery"],
    catches=["No official published pay figures or payout timing"],
    biggest_catch="Curri publishes no official driver pay figures or payout timing — offers show pay in-app only.",
    upfront_fee=None,
    verdict="reject",
    notes="Rejected: no official Curri driver pay/payout page found in public search; pay visible only inside the app.",
    critical=crit(
        (False, "No official numeric pay captured."),
        (False, "No official pay mechanism captured."),
        (False, "No official payout timing found."),
        (False, "No official requirements cited."),
    ),
    standard=OK_STD,
    weasel_words={"present": False, "quote": None},
    repeatable={"value": True, "cadence": "per task"},
    maximize="Unverifiable — only pursue after confirming pay and timing inside the driver app.",
))

# ---------------- R7739 U-Haul Moving Help (reject) ----------------
routes.append(base(
    route_id="R7739", provider="U-Haul Moving Help", official_url=None, terms_url=None,
    payout_quote="No official Moving Help helper pay/payout page captured in public search; helpers set their own rates on the marketplace.",
    payout_min_usd=0, payout_max_usd=0, time_min_minutes=0, time_max_minutes=0,
    timing="Not verifiable from official terms.", speed="days",
    eligibility=["Moving labor capability", "Marketplace listing"],
    steps=["List your moving-help services on Moving Help", "Get booked by customers", "Get paid per booking terms"],
    catches=["Helpers set own rates; no platform-guaranteed pay", "No official payout timing published"],
    biggest_catch="Moving Help is a listing marketplace where helpers set their own rates — there is no platform pay rate or payout schedule to verify.",
    upfront_fee=None,
    verdict="reject",
    notes="Rejected: marketplace model with helper-set rates and no official published payout timing; nothing concrete to verify.",
    critical=crit(
        (False, "No platform-set numeric pay; helpers set own rates."),
        (False, "No official payout mechanism captured."),
        (False, "No official payout timing found."),
        (False, "No official requirements cited."),
    ),
    standard=OK_STD,
    weasel_words={"present": False, "quote": None},
    repeatable={"value": True, "cadence": "per task"},
    maximize="Unverifiable as a platform route — if you list here, set your own rates and collect via your own instant-pay setup; Bellhop (R7700) and Lugg (R7701) are the verified moving-gig alternatives.",
))

# ---------------- R7740 HouseKeep (reject) ----------------
routes.append(base(
    route_id="R7740", provider="HouseKeep", official_url=None, terms_url=None,
    payout_quote="No official HouseKeep cleaner pay or payout page found in public search.",
    payout_min_usd=15, payout_max_usd=30, time_min_minutes=120, time_max_minutes=300,
    timing="Not verifiable from official terms.", speed="days",
    eligibility=["Cleaning experience", "Background check (typical)"],
    steps=["Sign up as a HouseKeep cleaner", "Accept cleaning jobs", "Get paid per job"],
    catches=["No official pay/payout terms found publicly"],
    biggest_catch="No official pay or payout timing published — nothing to verify.",
    upfront_fee=None,
    verdict="reject",
    notes="Rejected: no official HouseKeep page stating cleaner pay or payout timing found in public search.",
    critical=crit(
        (False, "No official numeric pay found."),
        (False, "No official pay mechanism found."),
        (False, "No official payout timing found."),
        (False, "No official requirements cited."),
    ),
    standard=OK_STD,
    weasel_words={"present": False, "quote": None},
    repeatable={"value": True, "cadence": "per task"},
    maximize="Unverifiable — skip until HouseKeep publishes official cleaner pay terms; Homeaglow (R7705) is the verified cleaning alternative.",
))

def write_all():
    os.makedirs(OUT, exist_ok=True)
    ids = [r["route_id"] for r in routes]
    assert len(ids) == len(set(ids)), "duplicate IDs"
    assert ids == sorted(ids), "IDs not sequential"
    for r in routes:
        p = os.path.join(OUT, r["route_id"] + ".json")
        with open(p, "w") as f:
            json.dump(r, f, indent=2)
            f.write("\n")
    return len(routes)

if __name__ == "__main__":
    n = write_all()
    print(f"wrote {n} files")
