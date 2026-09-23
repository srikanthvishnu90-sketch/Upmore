import json

verdicts = []

def reject(id, category, provider, name, reason, urls=None):
    verdicts.append({
        "category": category,
        "decision": "reject",
        "evidence_urls": urls or [],
        "id": id,
        "name": name,
        "provider": provider,
        "reason": reason,
    })

# ---------------------------------------------------------------- rejects

reject("M001", "Usability Testing", "TryMyUI",
    "Test websites and provide usability feedback",
    "Dead worker program. The official domain did not load on 2026-09-23 and TryMyUI is a known-shuttered testing platform with no verifiable current tester program or pay terms. Closed programs must be rejected.",
    ["https://trymyui.com"])

reject("M005", "Usability Testing", "TestTime",
    "Complete remote usability testing studies",
    "Dead domain. testtime.com/testers/ now resolves to a GoDaddy 'domain for sale' parking page, so the claimed worker program no longer exists. (Likely confused with TestingTime, a different provider.) Closed programs must be rejected.",
    ["https://testtime.com/testers/"])

reject("M009", "Usability Testing", "PingPong",
    "Test websites and participate in UX research sessions",
    "Worker program closed. hellopingpong.com now redirects to Contentsquare's customer survey product with no tester program remaining. Closed programs must be rejected.",
    ["https://hellopingpong.com"])

reject("M014", "Transcription", "Allegis Transcription",
    "Transcribe audio for legal and corporate clients",
    "Official worker terms incomplete + demand uncertainty. The official site confirms experienced-transcriptionist hiring with rigorous vetting, but worker pay timing and full terms could not be verified from official sources, and worker reports describe frequent work holds. The nine questions cannot be answered from official terms. Reject.",
    ["https://allegistranscription.com"])

reject("M018", "Transcription", "GMR Transcription",
    "Transcribe legal, medical, and general audio",
    "Sheet payout unsupported. The '$75-$270 per audio hour' figure appears to be customer pricing, not verified worker pay; official worker pay rates, acceptance, and payout terms could not be verified. The $10-per-unit bar cannot be confirmed from official terms. Reject.",
    ["https://gmrtranscription.com"])

reject("M022", "Captioning", "CaptionMax",
    "Create captions for broadcast and media content",
    "Stale/absorbed program. CaptionMax was acquired by 3Play Media, so the named worker program no longer exists as stated; no official current worker terms could be verified for it. Merged/closed programs must be rejected.",
    ["https://captionmax.com"])

reject("M034", "Content Writing", "ServiceScape",
    "Write, edit, and proofread for clients worldwide",
    "Stale provider. servicescape.com now redirects to editing.services (ServiceScape was renamed EditingServices), so the named provider/program as submitted is dead. The named entity and its terms no longer match a live official worker program. Redirected/merged programs must be rejected.",
    ["https://servicescape.com"])

reject("M038", "Proofreading", "Wordvice",
    "Proofread and edit academic papers",
    "Professional gate + unverified worker economics. The current official freelance-editor role requires native English fluency, graduate-level education, an editing test, and academic-format expertise; no official current payout rate or timing could be verified, so the nine questions cannot be answered. Reject.",
    ["https://wordvice.com"])

reject("M042", "Proofreading", "Enago",
    "Proofread and edit academic manuscripts for researchers",
    "Professional gate + unverified worker economics. Freelance academic-editor hiring requires 2+ years editing experience in selected STEM fields, but current official pay, acceptance, and payout timing could not be verified. The nine questions cannot be answered from official terms. Reject.",
    ["https://enago.com"])

reject("M046", "Virtual Assistant", "Time Etc",
    "Work as a part-time virtual assistant",
    "Duplicate of existing catalog route R3514 (Time Etc). Reject to avoid a duplicate import.",
    ["https://timetc.com"])

reject("M050", "Virtual Assistant", "OkayRelax",
    "Provide virtual assistant services to clients",
    "No verifiable current official worker terms. The customer site remains active, but no current official worker hiring, pay rates, acceptance rules, or payout terms could be verified from official sources. The nine questions cannot be answered. Reject.",
    ["https://okayrelax.com"])

reject("M054", "Customer Service", "Working Solutions",
    "Work from home as a customer service agent",
    "Duplicate of existing catalog route R3517 (Working Solutions). Reject to avoid a duplicate import.",
    ["https://workingsolutions.com"])

reject("M058", "Customer Service", "TTEC",
    "Work from home as a customer service representative",
    "Generic corporate route. TTEC is a real employer but no specific current remote role with stated pay/terms was supplied or verified; the nine questions cannot be answered for the generic claim from official terms. Reject.",
    ["https://ttec.com"])

reject("M062", "Customer Service", "Conduent",
    "Work from home as a customer service representative",
    "Generic corporate route. Conduent is a real employer but no specific current remote role with stated pay/terms was supplied or verified; the nine questions cannot be answered for the generic claim from official terms. Reject.",
    ["https://conduent.com"])

reject("M066", "Customer Service", "Amazon Virtual Customer Service",
    "Work from home as an Amazon customer service associate",
    "Generic corporate route. Amazon VCS is real but no specific current fully-remote opening with official stated pay/terms was supplied or verified on 2026-09-23; the nine questions cannot be answered for the generic claim. Reject.",
    ["https://amazon.jobs"])

reject("M070", "Moderation", "The Social Element",
    "Moderate and manage social media for brands",
    "No verified official pay for the generic claim + restrictive fit. Active project roles are language/location/shift-specific and often require experience, background checks, and specific hardware; no official current worker pay terms could be verified. The nine questions cannot be answered from official terms. Reject.",
    ["https://thesocialelement.com"])

reject("M074", "Chat Support", "The Chat Shop",
    "Provide live chat support for businesses",
    "Official worker economics unverifiable. The site is live but current demand and pay could not be established from official sources, and third-party reports conflict (low availability). The nine questions cannot be answered from official terms. Reject.",
    ["https://thechatshop.com"])

reject("M078", "Data Annotation", "V7 Labs",
    "Annotate images and videos for AI model training",
    "No worker program. The official site is B2B annotation software, not an open paid annotator platform; there is no public annotator signup, pay, or payout terms. The nine questions cannot be answered. Reject.",
    ["https://v7labs.com"])

reject("M082", "Data Annotation", "CloudFactory",
    "Complete data annotation tasks for AI training",
    "No universal self-serve worker route + opaque terms. Hiring is regional and project-based with waiting pools and low-pay reports; there is no public worker program with official transparent rates or terms. The nine questions cannot be answered from official terms. Reject.",
    ["https://cloudfactory.com"])

reject("M092", "Bookkeeping", "AccountingDepartment.com",
    "Provide remote bookkeeping services",
    "Professional-staffing job, not a beginner method. Roles require 3-5+ years full-charge bookkeeping experience, QuickBooks/NetSuite, U.S. location, and 30-40 scheduled hours/week (full-time W-2, with calls/webcam). Not an ordinary-person extra-income method. Reject.",
    ["https://accountingdepartment.com"])

reject("M096", "Medical Coding", "Aviacode",
    "Provide remote medical coding services",
    "Professional gate + unverified current terms. Roles require CPC/AHIMA certification, 2+ years specialty experience, 95% accuracy, and project tests; current official worker terms are old and unverified. Professional-certification gate, not a beginner method. Reject.",
    ["https://aviacode.com"])

reject("M100", "Freelance Coding", "Gun.io",
    "Work as a freelance software developer",
    "Elite professional gate, not a beginner method. Roughly 100 of 1,000 monthly applicants pass vetting; most engaged developers have 8-10+ years of experience and rates run $80-$200/hr. Senior-professional network, not a realistic ordinary-person path (same bar as Toptal's lane-2 reject). Reject.",
    ["https://gun.io"])

reject("M108", "Expert Advice", "PrestoExperts",
    "Answer questions as an expert consultant online",
    "No verifiable official current worker terms. prestoexperts.com failed to load and the sheet's description (tutoring/homework help) does not match the platform's actual expert-consultation model; no official current commission, pay, or payout terms could be verified. The nine questions cannot be answered. Reject.",
    ["https://prestoexperts.com"])

reject("M112", "Virtual Assistant", "Outsourcing Angel",
    "Provide virtual assistant services to clients",
    "Official worker economics unverifiable. The agency is real and hiring, but no official current worker pay rates, demand, or payout terms could be verified from official sources, so the $10-per-unit bar cannot be confirmed. The nine questions cannot be answered. Reject.",
    ["https://outsourcingangel.com"])

reject("M116", "Freelance Platform", "Hubstaff Talent",
    "Work as a freelance professional on a 0% commission platform",
    "Discontinued program. hubstaff.com/talent returns a 404; the freelance talent marketplace has been shut down. Closed programs must be rejected.",
    ["https://hubstaff.com/talent"])

reject("M124", "Design Services", "Kimp",
    "Work as a graphic designer for Kimp",
    "Employer/service company, not an open worker marketplace. Kimp is a design-services company (now kimp.io); no specific current remote designer role with official pay/terms was supplied or verified. The nine questions cannot be answered for the generic claim. Reject.",
    ["https://kimp.com"])

reject("M128", "Creative Staffing", "24 Seven",
    "Work as a freelance creative professional through 24 Seven",
    "Staffing agency with no committed online-only order. Placements may be hybrid/on-site and no specific current remote-only placement with stated pay/terms was verified; the nine questions cannot be answered for the generic claim. Reject.",
    ["https://24seventalent.com"])

reject("M132", "Illustration", "Artists&Clients",
    "Accept commissioned art requests on Artists&Clients",
    "Dead/unverifiable worker program. The official domain failed to load on 2026-09-23 and no current official worker terms could be verified. Unverifiable programs must be rejected.",
    ["https://artistsnclients.com"])

reject("M136", "Grant Writing", "Instrumentl",
    "Provide freelance grant writing and research services",
    "Wrong entity. Instrumentl is grant-search software for nonprofits, not a freelancer marketplace; there is no official freelance grant-writing worker program. The nine questions cannot be answered. Reject.",
    ["https://instrumentl.com"])

reject("M140", "Resume Writing", "ZipJob",
    "Write and optimize resumes for Canadian and US clients",
    "Stale provider. zipjob.com now redirects to TopResume; the named worker program no longer exists as stated. Redirected/closed programs must be rejected.",
    ["https://zipjob.com"])

reject("M144", "Design Freelance", "Dribbble Hiring",
    "Work as a freelance designer through Dribbble's job platform",
    "Payment certainty fails. Dribbble Hiring is a job-discovery/direct-client channel with no platform escrow, contracted payment, or official worker payment terms; there is no committed high-certainty payout mechanism. Reject.",
    ["https://dribbble.com/hiring"])

# ---------------------------------------------------------------- imports
# Route IDs assigned in input order: M026->R9100, M030->R9101, M087->R9102,
# M104->R9103, M120->R9104

verdicts.append({
    "id": "M026",
    "category": "Content Writing",
    "provider": "WriterAccess",
    "name": "Write articles and content for businesses",
    "decision": "import",
    "route_id": "R9100",
    "title": "WriterAccess — Write Articles for Businesses",
    "url": "https://writeraccess.com",
    "speed": "weeks",
    "who_pays": "WriterAccess pays writers — biweekly payouts via PayPal for approved work (15th/last-day approval cycles).",
    "qualifies": "18+; apply with writing samples and expertise categories; pass a short writing test; WriterAccess assigns a 2-6 star rating that sets your pay tier. Platform description states writers are US-based.",
    "availability": "Live marketplace verified active 2026-09-23. Order volume varies by tier; higher star ratings unlock more and better-paying work.",
    "accepted": "Client-approved work. Customers post specs with suggested pay; writer accepts or declines. Approved work becomes payable; unapproved clients' work auto-approves after the window (default 5-7 days), so work is paid. Extra words beyond the order are unpaid.",
    "costs_unpaid_time": "No fees to apply or work. Unpaid time: application, writing samples, short test, and waiting for approval cycles (pay lags submission).",
    "cash_timing": "Biweekly via PayPal. Work approved by the 15th or last day of the month is paid out on the following pay run; first cash realistically arrives 2-4 weeks after starting.",
    "repeatable": {"value": True, "cadence": "Ongoing — browse and claim content orders repeatedly; repeat clients and teams boost steady volume."},
    "demand_side": "Businesses ordering web content (blog posts, sales copy, email newsletters) through WriterAccess's client marketplace.",
    "evidence_urls": [
        "https://writeraccess.com",
        "https://www.freedomwithwriting.com/freedom/uncategorized/writing-jobs-from-writeraccess/",
    ],
    "realistic_weekly_earn": "$20-$150/week for an ordinary beginner part-time (a few short articles at 2-4 star rates).",
    "payout_min": 10,
    "payout_max": 50,
    "payout_unit": "article",
    "difficulty": 6,
    "ease": "medium",
    "anyone_can_do": True,
    "ease_note": "Requires decent writing skills, samples, and passing the platform's writing test; new writers start at lower star tiers with lower pay.",
    "biggest_catch": "Official talent FAQ pay tiers: 2-star $0.02/word, 3-star $0.04, 4-star $0.06, 5-star $0.08, 6-star $0.10-$2+/word. New writers start low and must earn their way up; extra words beyond the order are unpaid, and payout cycles mean cash lags the work by weeks.",
    "lane": "content-writing",
    "reason": "Live vetted writing marketplace with official pay tiers and biweekly PayPal payouts; approved/auto-approved work gets paid. Gate is an honest skill test, not a professional credential. Meets the bar.",
})

verdicts.append({
    "id": "M030",
    "category": "Content Writing",
    "provider": "Crowd Content",
    "name": "Write content for businesses and agencies",
    "decision": "import",
    "route_id": "R9101",
    "title": "Crowd Content — Write Content for Businesses",
    "url": "https://crowdcontent.com",
    "speed": "days",
    "who_pays": "Crowd Content pays writers and editors — twice-weekly PayPal payouts (Tuesdays and Fridays) for approved work; $10 minimum balance.",
    "qualifies": "18+; pass the initial writing assessment to join a writer level; PayPal account required for payout.",
    "availability": "Marketplace live and taking writers as of 2026-09-23. Demand varies; lower-tier marketplace work is competitive and slim for newcomers — managed projects, teams, and direct orders are steadier.",
    "accepted": "Approved marketplace orders. Once a submitted order is approved, it counts toward the $10 payout threshold; claim limits start at 1 order in progress for new writers and rise with clean completions.",
    "costs_unpaid_time": "No fees to apply or work. Unpaid time: application, writing assessment, and waiting for approval windows on submissions.",
    "cash_timing": "Twice a week via PayPal (Tuesday and Friday); anything approved before ~11pm EST the night before payday is paid out the next evening. First cash realistically arrives within 1-3 weeks.",
    "repeatable": {"value": True, "cadence": "Ongoing — claim marketplace orders repeatedly; teams and direct orders give repeat volume."},
    "demand_side": "Businesses and agencies buying articles, product descriptions, and web copy through Crowd Content's marketplace and managed content projects.",
    "evidence_urls": [
        "https://crowdcontent.com",
        "https://www.freedomwithwriting.com/freedom/uncategorized/7-reasons-you-should-be-making-money-writing-at-crowd-content/",
        "https://www.contentrefined.com/crowd-content-vs-textbroker/",
    ],
    "realistic_weekly_earn": "$20-$100/week for an ordinary beginner part-time (short marketplace orders at entry tiers).",
    "payout_min": 10,
    "payout_max": 30,
    "payout_unit": "assignment",
    "difficulty": 5,
    "ease": "medium",
    "anyone_can_do": True,
    "ease_note": "Requires passing a writing assessment; new writers compete for lower-tier work and must build reputation for steadier volume.",
    "biggest_catch": "Twice-weekly PayPal payout with a $10 minimum is real and reliable, but beginner work is thin and competitive — expect small orders until you earn team placements or direct orders.",
    "lane": "content-writing",
    "reason": "Live content marketplace with verified twice-weekly PayPal payouts ($10 minimum) and an assessment-based entry gate. Meets the bar with honest demand notes.",
})

verdicts.append({
    "id": "M087",
    "category": "Test Scoring",
    "provider": "Measurement Incorporated",
    "name": "Score standardized tests and essays remotely",
    "decision": "import",
    "route_id": "R9102",
    "title": "Measurement Incorporated — Score Tests Remotely",
    "url": "https://measurementinc.com",
    "speed": "weeks",
    "who_pays": "Measurement Incorporated pays readers/evaluators — base $15/hour plus paid training, paid every other Friday via direct deposit or pay card.",
    "qualifies": "Bachelor's degree required; U.S. resident in one of the eligible states (AL, AR, DE, FL, GA, IA, ID, IN, KS, KY, LA, MI, MO, MS, MT, NE, NC, NH, OH, OK, PA, SC, SD, TN, TX, UT, VA, WI, WV); computer/laptop, password-protected high-speed internet, and a secure workspace.",
    "availability": "Seasonal. Peak demand mid-February through June; first-time scorers are typically staffed closer to April; limited work the rest of the year. 2026 General Population Reader/Evaluator role verified active via the official-linked application.",
    "accepted": "Contracted scoring work. Pass the qualification/training for each project and complete scored assignments; work is project-by-project and seasonal, not year-round employment.",
    "costs_unpaid_time": "No fees. Unpaid time: application, qualification process, and waiting for seasonal projects. Training itself is paid.",
    "cash_timing": "Every other Friday via direct deposit or pay card. First cash realistically arrives 3-6 weeks after applying (qualification + seasonal start).",
    "repeatable": {"value": True, "cadence": "Project-by-project; seasonal repeat work each testing season while eligible and qualified."},
    "demand_side": "Schools, districts, and states whose student assessments Measurement Incorporated scores; demand peaks during standardized testing season.",
    "evidence_urls": [
        "https://measurementinc.com",
    ],
    "realistic_weekly_earn": "$150-$450/week during active scoring periods (part-time at $15/hr; hours vary by project).",
    "payout_min": 15,
    "payout_max": 17,
    "payout_unit": "hour",
    "difficulty": 6,
    "ease": "medium",
    "anyone_can_do": False,
    "ease_note": "Bachelor's degree is a hard requirement (not bridgeable quickly); also restricted to listed U.S. states and seasonal project windows.",
    "biggest_catch": "Real $15/hr remote scoring work with paid training — but it is strictly seasonal (Feb-Jun peak, April start for first-timers), requires a bachelor's degree, and is limited to 29 eligible states. Not a year-round income source.",
    "lane": "test-scoring",
    "reason": "Verified 2026 active role with official $15/hr pay, paid training, and biweekly direct-deposit payouts. Seasonal and degree-gated but fully stated. Meets the bar.",
})

verdicts.append({
    "id": "M104",
    "category": "Accessibility",
    "provider": "Knowbility",
    "name": "Participate in accessibility advocacy and testing programs",
    "decision": "import",
    "route_id": "R9103",
    "title": "Knowbility AccessWorks — Paid Accessibility Testing",
    "url": "https://knowbility.org/services/accessworks",
    "speed": "days",
    "who_pays": "Knowbility pays testers incentive payments for completed usability studies (Knowbility handles scheduling and incentive payments for its client studies).",
    "qualifies": "Must be a person with a disability who uses assistive technology (blind, low vision, unable to use a mouse/pointing device, or a cognitive/neurological condition); register as an AccessWorks tester via the signup form. Panel is U.S. and Canada.",
    "availability": "Occasional studies only. AccessWorks is a standing user panel; studies arrive when client research needs match your disability/assistive-tech profile — expect a handful of studies per year, not steady work.",
    "accepted": "Invited study participation. Complete the scheduled remote usability test and follow-up; incentive payment is tied to completed study participation, not a lottery or contest.",
    "costs_unpaid_time": "No fees. Unpaid time: registration form and waiting to be matched to studies.",
    "cash_timing": "Incentive payment after each completed study (Knowbility-managed). First cash arrives whenever the first matching study is completed — days to months.",
    "repeatable": {"value": True, "cadence": "Repeatable per study — panel members can be invited to multiple studies over time, but frequency is low."},
    "demand_side": "Businesses, educational institutions, government agencies, and nonprofits that hire Knowbility to recruit disabled testers for website/app usability studies.",
    "evidence_urls": [
        "https://knowbility.org/services/accessworks",
        "https://knowbility.github.io/knowbility-website/programs/accessworks/",
    ],
    "realistic_weekly_earn": "Not a weekly income source — typical usability-study incentives run $50-$150 per completed study, a few studies per year.",
    "payout_min": 50,
    "payout_max": 150,
    "payout_unit": "study",
    "difficulty": 7,
    "ease": "medium",
    "anyone_can_do": False,
    "ease_note": "Only open to people with qualifying disabilities who use assistive technology (blind/low vision, mobility, cognitive/neurological); this gate is not bridgeable — the route is only for people who already qualify.",
    "biggest_catch": "Genuine paid testing with no skill test, but studies are occasional (a few per year) and you must have a qualifying disability. Do not treat this as steady income.",
    "lane": "accessibility",
    "reason": "Real standing paid panel run by a nonprofit; Knowbility handles incentive payments for completed studies. Per-study pay clears the bar; infrequency is stated honestly. Meets the bar for qualifying users.",
})

verdicts.append({
    "id": "M120",
    "category": "Freelance Platform",
    "provider": "PeoplePerHour",
    "name": "Work as a freelance professional on PeoplePerHour",
    "decision": "import",
    "route_id": "R9104",
    "title": "PeoplePerHour — Freelance on an Escrow Platform",
    "url": "https://peopleperhour.com",
    "speed": "weeks",
    "who_pays": "Clients pay through PeoplePerHour's escrow; the freelancer invoices and the buyer releases escrowed funds on approval. Withdrawals to PayPal or bank account, processed in about one business day.",
    "qualifies": "18+; free application to become a seller (optional fee to expedite, otherwise ~7-day processing); complete profile with skills, experience, and rates. One account per seller.",
    "availability": "Live global freelance marketplace verified active 2026-09-23 with client demand across skill categories. 15 free proposals per month; extra visibility costs extra.",
    "accepted": "Accepted proposals and purchased offers. Client escrows project funds before work starts (ask for escrow or milestones upfront); invoice on completion and the buyer releases funds. Disputes are investigated by the platform.",
    "costs_unpaid_time": "Free to join and 15 proposals/month free. Platform commission: 20% on the first ~£250 billed per client, 7.5% up to £5,000, then 3.5%. Unpaid time: writing proposals (only 15 free/month), client revisions (2 free per project).",
    "cash_timing": "On project approval + ~1 business day withdrawal processing. First cash realistically arrives 2-6 weeks after approval (winning proposals takes time).",
    "repeatable": {"value": True, "cadence": "Ongoing — bid on projects and post fixed-price 'hourlies' repeatedly; repeat clients lower commission to 7.5%/3.5%."},
    "demand_side": "Businesses posting freelance projects (design, writing, development, marketing) and buying fixed-price 'hourlie' offers on PeoplePerHour.",
    "evidence_urls": [
        "https://peopleperhour.com",
        "https://www.peopleperhour.com/discover/guides/how-to-use-peopleperhour-safely-a-complete-guide-for-buyers-and-freelancers/",
    ],
    "realistic_weekly_earn": "Highly variable — ordinary beginners with a sellable skill realistically earn $50-$300/week once winning work; nothing is guaranteed until proposals convert.",
    "payout_min": 20,
    "payout_max": 75,
    "payout_unit": "project",
    "difficulty": 6,
    "ease": "medium",
    "anyone_can_do": True,
    "ease_note": "Needs a sellable skill and the patience to win early proposals against global competition; only 15 free proposals per month.",
    "biggest_catch": "Escrow protection is real but only if you insist funds are escrowed before starting. The 20% first-client commission is steep, and a brand-new profile with no reviews converts slowly — budget weeks of proposals before first paid work.",
    "lane": "freelance-platform",
    "reason": "Established marketplace with platform escrow, published tiered fees, and ~1-day withdrawals. Payment certainty holds when escrow is used. Meets the bar with honest commission/demand notes.",
})

with open("/home/hatch/workspace/upmore/qa/hidden_files/xlsx-verdicts-lane1.json", "w") as f:
    json.dump(verdicts, f, indent=1)

print("total:", len(verdicts))
print("imports:", sum(1 for v in verdicts if v["decision"] == "import"))
print("rejects:", sum(1 for v in verdicts if v["decision"] == "reject"))
ids = [v["id"] for v in verdicts]
print("unique ids:", len(set(ids)))
expected = ["M001","M005","M009","M014","M018","M022","M026","M030","M034","M038","M042","M046","M050","M054","M058","M062","M066","M070","M074","M078","M082","M087","M092","M096","M100","M104","M108","M112","M116","M120","M124","M128","M132","M136","M140","M144"]
print("order matches input:", ids == expected)
import_ids = [(v["id"], v.get("route_id")) for v in verdicts if v["decision"] == "import"]
print("import route ids:", import_ids)
req = {"id","category","provider","name","decision","route_id","title","url","speed","who_pays","qualifies","availability","accepted","costs_unpaid_time","cash_timing","repeatable","demand_side","evidence_urls","realistic_weekly_earn","payout_min","payout_max","payout_unit","difficulty","ease","anyone_can_do","ease_note","biggest_catch","lane","reason"}
for v in verdicts:
    if v["decision"] == "import":
        missing = req - set(v.keys())
        assert not missing, (v["id"], missing)
print("import field check: OK")
