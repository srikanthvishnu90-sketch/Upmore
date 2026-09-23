#!/usr/bin/env python3
"""Rule-based done_when generator for Upmore route steps.

Honest completion sentences derived ONLY from the step's own text.
Fallback: "You've finished this step." (always honest).
"""
import re

def _obj(m, i=1, words=3):
    o = (m.group(i) or "").strip(" .,:;")
    toks = o.split()
    if not toks:
        return None
    # cut at common tail words
    out = []
    for t in toks[:words]:
        if t.lower() in ("within", "before", "after", "during", "using", "via", "for", "on", "to", "and", "by"):
            break
        out.append(t)
    return " ".join(out) or None

def gen_done_when(text):
    t = (text or "").strip()
    if not t:
        return None
    tl = t.lower()

    # 0. strip leading conditional/temporal clause: "Once X, do Y" -> process Y
    m = re.match(r'^(?:once|after|when|as|if)\b[^,]{0,80}?,\s*(.+)$', tl)
    if m and len(m.group(1)) > 8:
        r = gen_done_when(t[m.start(1):])
        if r and r != "You've finished this step.":
            return r
    m = re.match(r'^between [^,]{0,50}?,\s*(.+)$', tl)
    if m and len(m.group(1)) > 8:
        r = gen_done_when(t[m.start(1):])
        if r and r != "You've finished this step.":
            return r

    # track (before spend/outcome: "Track the $30 credit — it should post ...")
    if re.search(r'\btrack\b', tl):
        return "You're tracking it."
    # donate (before outcome: "...donation to receive compensation")
    if re.search(r'\bdonat', tl):
        return "The donation is complete."
    # go to a referral page
    if re.search(r'\bgo to\b.{0,60}?\b(refer|referral)\b', tl):
        return "The referral page is open."
    # keep open / good standing (before open-account: "Keep the account open, ... bonus posts")
    if re.search(r'\bkeep\b.{0,40}?(open|active|standing)', tl) or \
       re.search(r'\bremain\b.{0,20}?(good standing|active|open)', tl):
        return "The account stays open and in good standing."
    if re.search(r'\bkeep\b.{0,30}?(balance|minimum)', tl):
        return "The requirement is maintained."
    if re.search(r'\bmaintain\b', tl):
        return "The requirement is maintained."
    # request / claim (before referral-link: "request your custom referral link" != having it)
    m2 = re.search(r'\b(request|claim) (?:your |a |an |the )?(\w+(?: \w+){0,3})', tl)
    if m2 and _obj(m2, 2):
        return f"Your {_obj(m2, 2)} is requested."
    # share link/code (before referral-link: "Share your ... referral code" is sharing, not getting)
    if re.search(r'\bshare\b(?!\s+respondent\b|\s+the warmth\b).{0,40}?(link|code)', tl) or re.search(r'\bsend\b.{0,30}?link to a friend', tl):
        return "Your link is shared."
    # referral link / code retrieval (before outcome: "get your referral code")
    if re.search(r'\breferral (link|code)\b', tl):
        return "You have your referral link."

    # referral: friend signs up through your link
    if re.search(r'\bfriend\b.{0,60}?(signs?\s?up|enroll|register|open|joins?)', tl) or \
       re.search(r'\byour referral signs\b', tl) or \
       re.search(r'\breferred person\b.{0,20}?(opens?|signs?\s?up|enroll)', tl) or \
       re.search(r'\bfriend becomes\b', tl):
        return "Your friend signs up through your link."
    if re.search(r'\bfriend\b.{0,50}?active', tl):
        return "Your friend stays an active customer."
    if re.search(r'\bfriend\b.{0,30}?(meets|satisfies)', tl):
        return "Your friend meets the requirements."
    if re.search(r'\bmember\b.{0,30}?\bopens?\b', tl):
        return "Your friend signs up through your link."
    if re.search(r'\bboth\b.{0,60}?(receive|receives|deposited|credited|gets?|paid)', tl):
        return "The reward has arrived for both of you."
    # get paid (before direct deposit: "Get paid in 24-48 hours via PayPal, Zelle, or direct deposit")
    if re.search(r'\bget paid\b', tl):
        return "You've been paid."
    # direct deposit (skip outcomes and redeems: "Redeem ... for cash back (..., direct deposit, or check)")
    if re.search(r'\bdirect deposit', tl) and \
       not re.search(r'\byou receive\b|\b(is|are) direct(ly)? deposited\b|\bredeem\b', tl):
        if re.search(r'\bset ?up\b', tl):
            return "Direct deposit is set up and confirmed."
        return "The qualifying direct deposits have posted."
    # outcome: mailed / deposited / received
    if re.search(r'\bin the mail\b|\bmails? (it|the|your)\b', tl):
        return "It's in the mail to you."
    if re.search(r'\b(you |your .{0,25}?)?(receive|receives|is deposited|are deposited|is credited|is paid|are paid|is delivered|added to|loaded into|lands? in|arrives?|arrive|posts?|you (?:both )?get|get £|get \$)\b', tl):
        if re.search(r'\b(deposit|credit)', tl):
            return "It's in your account."
        return "You've received it."
    # watch for it to post
    if re.search(r'\bwatch\b', tl):
        m2 = re.search(r'the ([a-z0-9 ,.\'\-]{3,35}?) (?:to )?post', tl)
        if m2 and _obj(m2):
            return "It's posted to your account."
        return "It's arrived in your account."
    # share / send link
    if re.search(r'\bsend\b.{0,30}?link to a friend', tl):
        return "Your link is shared."
    if re.search(r'\bshare\b(?!\s+the warmth\b|\s+respondent\b)', tl):
        return "You've shared it."
    # refer a friend (skip "the Refer a Friend program", "Refer-A-Friend program", "Refer a Friend form/page")
    if re.search(r'(?<!\bthe )\brefer(?!-a-friend)\b.{0,30}?\bfriends?\b(?! form| page)', tl):
        return "You've sent the referral."
    # already a member
    if re.search(r'\bbe (?:a |an )existing\b', tl):
        return "You're already a member."
    # open account (not "open the terms page")
    if re.search(r'\bopen\b.{0,60}?\b(account|banking|checking)\b', tl) and 'terms page' not in tl:
        return "The account is open in your name."
    # create account
    if re.search(r'\bcreate\b.{0,60}?\baccount\b', tl):
        return "The account is created."
    # sign up
    if re.search(r'\bsign ?up\b.{0,40}?\baccount\b', tl):
        return "The account is open in your name."
    if re.search(r'\bsign ?up\b', tl):
        return "You're signed up."
    if re.search(r'\bjoin\b', tl):
        return "You've joined."
    if re.search(r'\bregister\b', tl):
        return "You're registered."
    if re.search(r'\benroll\b', tl):
        return "You're enrolled."
    # direct deposit
    if re.search(r'\bdirect deposit', tl):
        if re.search(r'\bset ?up\b', tl):
            return "Direct deposit is set up and confirmed."
        return "The qualifying direct deposits have posted."
    # purchases / spend / transactions / buy
    if re.search(r'\btransactions?\b', tl):
        return "The qualifying transactions have posted."
    if re.search(r'\b(spend|purchases?|(?<!best )buy)\b', tl):
        return "The qualifying purchases have posted."
    if re.search(r'\buse the (?:new )?card\b', tl):
        return "You're using the card."
    # cash out
    if re.search(r'\bcash ?out\b', tl):
        return "You've cashed out."
    # collect reward
    if re.search(r'\bcollect\b.{0,25}?(reward|bonus|\$)', tl):
        return "It's in your account."
    # pay
    if re.search(r'\bpay\b.{0,30}?(balance|statement)', tl):
        return "The balance is paid in full."
    if re.search(r'\bpay\b (the|your|a|an|it|off|down)', tl):
        return "The payment is complete."
    # fund / deposit money
    if re.search(r'\b(fund|deposit)\b.{0,30}?(account|money|\$)', tl) or re.search(r'\bfund\b', tl):
        return "The deposit has posted."
    # schedule (before apply: "Call to schedule your screening appointment or apply online")
    if re.search(r'\bschedule\b', tl):
        return "The appointment is scheduled."
    # start the application (before apply: "start the application" != submitted)
    if re.search(r'\bstart\b.{0,15}?(application|registration)', tl):
        return "The application is started."
    # apply: apply online/for -> application submitted; apply it/the -> applied
    if re.search(r'\bapply\b.{0,20}?(online|for|through|now|here)', tl) or re.search(r'\bapplication\b', tl):
        return "Your application is submitted."
    if re.search(r'\bapply\b.{0,10}?(it|the|this)\b', tl):
        return "It's applied."
    # log in
    if re.search(r'\blog ?in\b|\bsign ?in\b', tl):
        return "You're signed in."
    # codes
    if re.search(r'\bcode\b', tl) and re.search(r'\b(enter|promo|referral|bonus|apply|upload)\b', tl):
        return "The code is accepted."
    # attend first (before eligibility: "Attend your first visit: verify eligibility...")
    if re.match(r'^attend\b', tl):
        return "You've attended."
    # confirm eligibility (before survey/attend mid-list rules)
    if re.search(r'(confirm|check|verify|make sure).{0,30}eligib', tl):
        return "You're confirmed eligible."
    # verify phone / email
    if re.search(r'\bverify\b.{0,25}?phone', tl):
        return "Your phone number is verified."
    if re.search(r'\bverify\b.{0,25}?email', tl):
        return "Your email is verified."
    # identity
    if re.search(r'\bidentity verification\b|\bverify.{0,25}?(identity|id)\b|\bid verification\b', tl):
        return "Your identity is verified."
    # make sure (generic confirmation)
    if re.search(r'\bmake sure\b', tl):
        return "You've confirmed."
    # wait / allow-a-period (before survey/study rules: "Wait to be emailed when eligible studies...")
    if re.search(r'\bwait\b', tl) or re.search(r'\ballow\b.{0,20}?(weeks?|months?|days?)', tl):
        if re.search(r'\b(land|deposit|post)\b', tl):
            return "It's in your account."
        if re.search(r'\binvitation\b', tl):
            return "The invitation has arrived."
        return "The waiting period is over."
    # complete the study
    if re.search(r'\bcomplete\b.{0,20}?\bstud(y|ies)\b', tl):
        return "The study is completed."
    # screening
    if re.search(r'\bscreening\b', tl):
        return "The screening is completed."
    # surveys / tests / studies / tasks
    if re.search(r'\bsurvey', tl):
        return "The survey is submitted."
    if re.search(r'\btests?\b', tl):
        return "The test is submitted."
    if re.search(r'\b(study|studies|experiment|slot|appointment)\b', tl):
        return "The slot is booked."
    if re.search(r'\btasks?\b', tl):
        return "The tasks are submitted."
    # receipt
    if re.search(r'\breceipt\b', tl):
        return "The receipt shows as submitted."
    # link / connect / add card (not "gift card link delivered")
    if (re.search(r'\blink\b|\bconnect\b', tl)) and not re.search(r'\bdeliver', tl):
        return "The account is linked."
    if re.search(r'\badd\b.{0,25}?\bcard', tl):
        return "The card is added to your profile."
    # obtain (before form: "Obtain the referral form" is not submitting it)
    m2 = re.search(r'\bobtain\b.{0,10}?(?:the |a |your )?(\w+(?: \w+){0,3})', tl)
    if m2 and _obj(m2):
        o = _obj(m2)
        o = o.title()
        return f"You've got the {o}."
    # pass / give a form or coupon to someone
    m2 = re.search(r'\b(?:pass|give|hand)\b.{0,10}?(?:the |your |a |an )?([a-z]+(?: [a-z]+)?)', tl)
    if m2 and _obj(m2):
        o = _obj(m2)
        if o in ("it", "them", "this", "that", "him", "her", "me", "us"):
            return "You've passed it on."
        return f"The {o} is passed on."
    # forms (only when filling/submitting/completing one)
    if re.search(r'\b(fill|submit|complete)\b.{0,30}?\bform\b', tl) or re.search(r'\bform\b.{0,20}?(submitted|filled|completed)\b', tl):
        return "The form is submitted."
    # generic submit with object
    m2 = re.search(r'\bsubmit (?:the |your |a |an |that )?(\w+(?: \w+){0,3})', tl)
    if m2 and _obj(m2):
        o = _obj(m2)
        return f"The {o} is submitted."
    # attend
    if re.search(r'\battend\b', tl):
        return "You've attended."
    # redeem
    if re.search(r'\bredeem\b', tl):
        return "The redemption is submitted."
    # send money
    if re.search(r'\bsend \$|\bsend money\b', tl):
        return "The money is sent."
    # ship / send in / mail object
    m2 = re.search(r'(?:\bship\b|\bsend in\b|\bmail\b) (?:the |your |a |an )?([a-z]+(?: [a-z]+)?)', tl)
    if m2 and _obj(m2):
        o = _obj(m2)
        return f"The {o} is sent." if o != "book" else "The book is shipped."
    # download / install
    if re.search(r'\b(download|install)\b', tl):
        if re.search(r'\bextension\b', tl):
            return "The extension is installed."
        if re.search(r'\b(app|software)\b', tl):
            return "The app is installed on your phone."
        return "The download is complete."
    # upload
    if re.search(r'\bupload\b', tl):
        m2 = re.search(r'upload (?:the |your |a |an )?([a-z]+(?: [a-z]+)?)', tl)
        if m2 and _obj(m2):
            o = _obj(m2)
            return f"The {o} are uploaded." if o.endswith("s") else f"The {o} is uploaded."
        return "The upload is complete."
    # email
    if re.search(r'\bemail\b', tl) and (re.search(r'\b(send|write|reply)\b', tl) or '@' in tl):
        return "The email is sent."
    # withdraw
    if re.search(r'\bwithdraw\b', tl):
        return "You've withdrawn."
    # confirm
    if re.search(r'\bconfirm\b', tl):
        return "You've confirmed the details."
    # audit
    if re.search(r'\baudit\b', tl):
        return "The audit is complete."
    # stay / visit
    if re.search(r'\b(live in|stay at)\b', tl):
        return "You've completed the stay."
    # read terms
    if re.search(r'\bread\b.{0,30}?(terms|offer|headline)', tl):
        return "You've read the current terms."
    # check requirements
    if re.search(r'\bcheck\b', tl):
        return "The requirements are confirmed."
    # earn
    if re.search(r'\bearn\b', tl):
        if re.search(r'\bwatts\b', tl):
            return "The Watts are credited."
        if re.search(r'\bcommission\b', tl):
            return "The commission is credited."
        return "It's credited to your account."
    # compare
    if re.search(r'\bcompare\b', tl):
        return "You've compared the options."
    # search
    m2 = re.search(r'\bsearch by (\w+)', tl)
    if m2:
        w = m2.group(1)
        w = "ISBN" if w == "isbn" else w
        return f"You've searched by {w}."
    if re.search(r'\bsearch\b', tl):
        return "You've completed the search."
    # select / pick / choose
    if re.search(r'\b(select|pick|choose)\b', tl):
        return "You've made your choice."
    # click through
    if re.search(r'\bclick\b', tl):
        return "You've clicked through."
    # installed (improvements, equipment — not app install)
    if re.search(r'\binstalled\b', tl):
        return "The installation is complete."
    # work a shift
    if re.search(r'\bwork\b', tl):
        return "The shift is complete."
    # contact
    if re.search(r'\bcontact\b', tl):
        return "You've contacted them."
    # accept
    if re.search(r'\baccept\b', tl):
        return "You've accepted."
    # held / frozen in account
    if re.search(r'\b(held|frozen)\b', tl):
        return "It's in your account."
    # loan closes
    if re.search(r'\bcloses?\b.{0,20}?(loan|mortgage)', tl):
        return "The loan is closed."
    return "You've finished this step."

if __name__ == "__main__":
    import json, sys
    rows = json.load(open("hidden_files/donewhen-fetch.json"))
    changed, empty, filled_total, fallback_n, byrule = 0, 0, 0, 0, {}
    updates = {}
    for r in rows:
        steps = r.get("steps")
        if not isinstance(steps, list):
            continue
        new_steps = []
        touched = False
        for s in steps:
            if not isinstance(s, dict):
                new_steps.append(s)
                continue
            dw = (s.get("done_when") or "").strip()
            if dw:
                filled_total += 1
                new_steps.append(s)
                continue
            g = gen_done_when(s.get("text") or "")
            if g:
                filled_total += 1
                if g == "You've finished this step.":
                    fallback_n += 1
                ns = dict(s)
                ns["done_when"] = g
                new_steps.append(ns)
                touched = True
            else:
                empty += 1
                new_steps.append(s)
        if touched:
            changed += 1
            updates[r["route_id"]] = new_steps
    json.dump(updates, open("hidden_files/donewhen-updates.json", "w"))
    print(f"routes_changed={changed} filled_total={filled_total} fallback={fallback_n} still_empty={empty}")
    json.dump({"changed": changed, "fallback": fallback_n, "empty": empty}, open("hidden_files/donewhen-stats.json", "w"))
