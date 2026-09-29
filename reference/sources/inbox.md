# Inbox: inbound mail and reply analysis

## Inbound recruiter mail: verify before replying

An unsolicited approach is not a source, it is a claim. Four checks, all cheap, before anything is sent:

1. **Find the vacancy.** Probe `boards-api.greenhouse.io/v1/boards/<co>/jobs`, `api.ashbyhq.com/posting-api/job-board/<co>`, `jobs.lever.co/<co>`, `apply.workable.com/<co>`, `<co>.recruitee.com/api/offers/`, and the company's own `/careers`. A real role usually exists somewhere. Note that `/careers` can return **200 and silently redirect to the homepage**, so check the final URL, not the status code.
2. **Read what the mail does not say.** A recruiter writing to a named person about a named job says the title, the level, the location and usually the band. A mail that offers to send "the role summary" *after* you reply is asking for a reply, not offering a job.
3. **Check whether anything in it is about the candidate.** "Your experience stood out" with no mention of a single thing from the profile is a template.
4. **The reply-to domain is the deciding signal.** A company address is a good sign; an unrelated free or agency domain on a mail written in the company's voice is not. Ask the candidate for it if it is not in view.

None of this makes an approach fraudulent, and small companies do source quietly for roles they never advertise. It decides how much of the candidate's data goes out in the first reply. **Seekter never sends the reply**; it drafts, and the candidate sends.

Measured 27 Sept on one such approach: real company, the description of it in the mail accurate, `/careers` redirected to the homepage, no board on any of the five ATSs, and their Recruitee API returned **0 offers**. Log it as `pending` against the company so dedup catches them later.

## Reply analysis (Outlook web) and rejection regex

**Lessons**
- **Don't trust subject lines; read the body.** Half the rejections have neutral subjects ("Your Application With X", "Thanks for your interest in X"). A subject filter like `update|regarding` misses half.
- Rejection regex (measured, working):
```
/unfortunat|regret to inform|we regret|not moving forward|not be moving forward|won't be moving forward|
not to move forward|decided not to move|made the decision to not|will not be proceeding|not be proceeding|
not proceeding with|isn't an ideal fit|regrettably|we have decided not|we've decided not|
decided to move forward with other|other candidates|other applicants|another candidate|not progress your|
not to proceed|won't be able to invite|not be taking your application|not the right fit|was not successful|
leider|nicht weiter|malheureusement|bohužel|no continuar|continue with other/i
```
- **False-positive trap:** thank-you mails often carry the boilerplate "If you are not selected for this position, keep an eye on…". Read the matched sentence; don't rely on the boolean.

**Which folders to sweep.** Never just the Inbox. Candidates file application mail, and employer mail lands in Junk regularly, so read every folder the profile lists (§11). A sweep of one folder under-counts replies and makes the funnel look worse than it is.

**Fast reading technique in Outlook Web**
1. The list is virtualized (6-8 rows in the DOM). **Harvest `[role=option]` and read its `aria-label`** (re-measured 22 Sept; the older `[data-convid]` attribute is gone). The label carries sender, subject, date and a body preview in one string, which is enough to triage before opening anything:
   ```js
   window.H=[];window.SEEN=new Set();
   window.GRAB=function(){document.querySelectorAll('[role=option]').forEach(o=>{
     const a=(o.getAttribute('aria-label')||o.innerText||'').replace(/\s+/g,' ').trim();
     if(a&&!window.SEEN.has(a)){window.SEEN.add(a);window.H.push(a);}});return window.H.length;};
   ```
   `[role=option]` returns 0 after a folder switch, and **"several seconds" understates it**: measured 23 Sept, the list stayed at 0 through waits totalling 18 s and 25 s on two different folders, while the rows were already visible in a screenshot the whole time. It is not a selector problem and not an empty folder. **Probe `document.querySelectorAll('[role=option]').length` on its own before believing a 0**, and keep re-running the harvest until it is non-zero; a screenshot showing rows while the count is 0 means keep waiting, nothing else. The same trap in a different costume as the Indeed `h2 a span` bug: a zero count over a visibly full list is a bug until proven otherwise.
2. **The `aria-label` carries 200+ characters of the body, which is usually enough to classify without opening the message.** Measured 22 Sept: of 173 harvested labels, 30 matched the rejection regex and all 30 quoted a real decision sentence ("we won't be moving forward", "decided to move forward with other candidates"). Not one was the "if you are not selected" boilerplate false positive. Read the matched sentence out of the label, and only open a message when the label truncates before the verdict.
3. Rejection mails usually name the role, which resolves a company with several open applications ("the Staff Product Designer position", "Senior Design Engineer - MetaMask"). Match on the role before moving a row, or the wrong application gets closed.
4. Scroll with a **real** `computer` scroll and `GRAB()` after each one. Setting `scrollTop` moves the container but does **not** make the virtualized list fetch more rows, so the harvest silently stops growing while the scrollbar appears to move. About 6 new rows per 5 ticks; the server pauses to fetch every ~40 rows.
2. Open messages cheaply by changing the SPA route (no reload):
```js
window.BASE=location.pathname.split('/id/');
window.GO=function(id){history.pushState({},'',window.BASE+'/id/'+encodeURIComponent(id));
  window.dispatchEvent(new PopStateEvent('popstate'));};
window.RP=function(){var m=document.querySelector('div[role="main"]');return m?m.innerText.replace(/\s+/g,' '):'';};
```
   `GO(id)` → wait 2 s → `RP()`. No screenshots needed.
5. At most 12 messages per `browser_batch`; 60+ actions time out.
6. `resize_window` can't exceed the screen ("Bounds must be at least 50% within visible screen space").
7. Outlook body search is weak (`unfortunately` found 2 of 188); subject and sender search work well.

- **A knockout can live only in the reply.** Measured 25 Sept: Emporix rejected the Senior UX/UI Designer application one day after it went in, with *"we are only able to consider candidates who reside in Poland."* That rule was **not in the posting and not in the form**, which asked no residence question at all. So a residence wall is not always catchable in advance: posting, form, reply. Nothing in the filter chain could have seen this one, and that is worth knowing before blaming the triage for it.
- **Same-day and next-day rejections are now the norm.** Of the five rejections in the 25 Sept sweep, three came back within a day and two of those were on applications sent the previous day. A sweep run weekly will therefore see mostly *outcomes*, not pending states.
- **An employer can send the identical rejection twice.** Deutsche Telekom sent the same mail at 10:00 and 11:00 on 25 Sept, same role and same requisition number. Match on the requisition or the role before logging, or the funnel double-counts.

**How to use the results:** match rejections to tracker rows and set Status = Rejected. Rejections are also the moment to catch past applications missing from the tracker, and duplicate tracker rows. Diagnostic signals: most rejections arrive 1–2 days after applying (some the same day), and none cite location, visa or work permit. That points to CV/portfolio screening at the gate, not targeting. Email tracking is the user's job; the Microsoft 365 connector rejects personal accounts.
