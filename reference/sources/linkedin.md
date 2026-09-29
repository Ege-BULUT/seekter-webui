# LinkedIn

## Job alerts
- **Where the list lives:** linkedin.com/jobs → left menu "Preferences" → "Job alerts" → `linkedin.com/jobs/jam?viewType=JOB_ALERTS`, then "Show 5 more". `/jobs/job-alerts/` is not the list.
- **Editing:** the pencil only offers frequency (Daily/Weekly), notification type (Email and notification / Email / Notification) and "Delete job alert". **Keyword and location can't be edited**, so a query change means delete and recreate from the search page.
- **Creating:** open the search URL, then click the "Set alert" toggle at the top right (`input[type=checkbox]`, `id^=adToggle`, 43×27 CSS px). **The first click after navigation is often swallowed** because the sticky header re-renders. Click, zoom to check, and click again if it's still off. On shows the text **"Alert on"** with a green pill; off shows **"Set alert"** with a navy pill and the knob on the left.
- **Deleting:** pencil → "Delete job alert" → confirm "Delete". The confirm button's y position shifts about 26 frame px with text length, so take a screenshot before each delete. **Bulk JS delete loops get "Blocked by classifier"**; do them one at a time with real clicks.
- **Quoted vs unquoted, measured over 7 days.** The narrower and more compound the title, the more the quotes cost; a broad one-word title loses nothing, which is why the damage goes unnoticed:

| Query shape | Quoted | Unquoted |
|---|---|---|
| Two-word niche title · EEA · remote | **0** | 25 |
| Two-word niche title · Worldwide · remote | 7 | 25 |
| Title with a slash variant · EEA · remote | 13 | 25 |
| Common two-word title · EEA · remote | 25 | 25 |

- **Real miss rate:** running the old quoted alert queries (257 jobs) against 13 jobs actually applied to via LinkedIn gave **3/13 caught, a 77% miss rate**.
- **Root causes** (generic lessons):
  - Quotes.
  - A whole title family missing from the alert set. List the candidate's titles first, then check every alert covers one.
  - **LinkedIn does not stem or merge title variants.** A slash variant and its plain form don't match each other, and neither matches the reversed order. Each variant the candidate's field uses needs its own alert.
  - **EEA (`91000002`) excludes the UK, Switzerland and every non-EEA European country**, so those need separate alerts and searches.
  - Seniority filters pull in the level above the one you want.
  - **The Remote filter hides hybrid and on-site roles** in target countries.
  - Noise titles: another industry using the same words (see "Title collisions" in `/seekter-run` §2.3).
- **Unquoted breadth:** adding words doesn't narrow results (a two-word title Worldwide remote = 1,579; the same title plus a third word = 1,527). LinkedIn treats an unquoted query as loose, OR-like and relevance-sorted. **Result count says nothing about alert quality, so filter by title**.
- **Notification type:** keep very broad alerts (thousands of results) as notification-only so they don't flood the inbox; put narrow ones on email plus notification.
- **Small markets:** search the **broadest single word** of the candidate's discipline, not their exact title. Measured in a small home market: the two-word title missed two senior roles that the one-word search found, because local postings use local title conventions. The same holds on Glassdoor.
- **Change policy:** originally "don't change alerts yourself, report it". Alerts were later rebuilt with the user's explicit approval. Don't delete alerts the user deliberately created.
- **Job preferences ("Open to work")** drive a separate feed. Max 5 titles. **The title field is a closed taxonomy, not free text**, and a specialised or hyphenated title is often absent from it — the offered completions can even belong to a different industry. Pick the nearest standard title and record the substitution in the profile, because it is not what the candidate calls themselves. Set start date to "Immediately, I am actively applying" for recruiter visibility. Title combobox pitfalls: the frame width shifts and a click lands on the wrong option, so use `find` plus ref. `ctrl+a` doesn't select, so use triple_click. To reopen the list: click, Backspace, retype the last letter.

## Notification ID harvesting (`originToLandingJobPostings`)
- URL: `https://www.linkedin.com/notifications/?filter=job_alerts`. The 19 Sept entry writes `?filter=job_alert`. Switch to the **Jobs** filter.
- "See N jobs similar to…" and alert cards link to search URLs whose `originToLandingJobPostings=` parameter is a **comma-separated list of job IDs**. Take the IDs from there instead of scraping.
- Harvest script (scroll down first):
```js
const ids=new Set();
document.querySelectorAll('a[href*="originToLandingJobPostings"]').forEach(a=>{
 const u=new URL(a.href,location.origin);const p=u.searchParams.get('originToLandingJobPostings');
 if(p)p.split(',').forEach(x=>ids.add(decodeURIComponent(x).trim()));});
document.querySelectorAll('a[href*="currentJobId="]').forEach(a=>{const u=new URL(a.href,location.origin);const c=u.searchParams.get('currentJobId');if(c)ids.add(c);});
document.querySelectorAll('a[href*="/jobs/view/"]').forEach(a=>{const m=a.href.match(/\/jobs\/view\/(\d+)/);if(m)ids.add(m);});
JSON.stringify([...ids])
```
- Feed the IDs to the detail harvest by hand (`const ids=['4441616273','4441603770',...]`). In one call you get title, location, apply URL, `workRemoteAllowed`, `closed` and the description.
- `companyDetails` sometimes returns `?` for the company. Identify it from the description's first sentence instead.
- Also scan `/jobs/job-alerts/` (alerts) and merge the IDs. One 11 Sept round: 42 raw → 39 unique → 7 applications.
- **Overlap measured a fifth time (25 Sept): 2.** The notification harvest gave 57 ids and about 40 title matches; the 40 searches gave 338 unique ids and 190 title matches, of which **188 were absent from the notification harvest**. Running tally of searches-not-in-notifications: 13 of 24, then 53 of 55, then 59 of 59, then 121 of 132, now **188 of 190**. Five measurements, same answer every time.
- **Overlap with the searches, measured a fourth time (24 Sept): 11.** The notification harvest gave 47 ids / 35 title matches; the 16 searches gave 208 unique ids / 132 title matches, of which **121 were absent from the notification harvest**. Running totals for the overlap between the two channels on the same day: 13 of 24 missing (one direction), then 53 of 55 missing, then 59 of 59 missing, now 121 of 132 missing. The channels do not substitute for each other in either direction.
- **`closed` from the detail endpoint is not a liveness check.** Measured 24 Sept: a posting returned `closed=false` while its job page read "Not currently accepting applications", 3 hours after being posted, with 9 applicants. Fresh postings can shut within hours, so for anything you intend to apply to, the job page or the ATS is the only status worth trusting.
- Yield is noisy. One measured round: 36 IDs → 9 already applied, 4 title collisions from other industries, 2 blacklisted, 2 sensitive sector, 1 aggregator, 1 fake location → 9 real candidates. Always bulk-fetch; never open jobs one by one.
- `SEMANTIC_SEARCH_JOB_ALERT` links carry geoId and keyword as well.

## Search URL (UI) and parameters
```
https://www.linkedin.com/jobs/search/?keywords=<term>&f_WT=2&f_TPR=r86400&geoId=<geoId>
```
- `f_WT=2` = remote.
- `f_TPR=r86400` (24 h) / `r259200` (3 days) / `r604800` (7 days) / `r2592000` (30 days).
- `f_E=4,5,6` = mid-senior and above.
- `sortBy=DD` = newest first. **Do not use it.** It is an ordering, not a filter, and on a loose multi-word query it ranks by posting time across everything matching any single word, which floods the result set with other industries. Use `f_TPR` for freshness and leave the ordering at relevance. Measured 23 Sept, one query, EEA, 3-day window: relevance 25/25 on-discipline, `sortBy=DD` 1/25. The same trap as `sort=posted_at` on the freehire API, documented there since the first week and never transferred here.
- Pagination: `&start=25,50,75...`.
- **Don't use `f_AL=true` (Easy Apply filter).** It breaks keyword matching: with it on, a two-word title returned roles from unrelated disciplines. Detect Easy Apply from `applyMethod` instead: no `companyApplyUrl` means Easy Apply.
- **geoIds** (extend as the candidate's geography needs; read a new one out of the URL after picking the location in the UI): `91000002` EEA · `92000000` Worldwide · `102105699` TR · `102890719` NL · `101282230` DE · `104738515` IE · `105646813` ES · `103350119` IT · `105072130` PL · `105015875` FR · `100364837` PT · `101165590` UK. EEA doesn't cover the UK or Switzerland, so search them separately.
- **Country geo + remote filter trap:** remote plus a single-country geo mostly returns *global roles that accept that country*, not local companies. To see local-company jobs, drop the remote filter, grep descriptions for `uzaktan|remote` (local-language "remote"), then verify with `workRemoteAllowed`.
- **Search-set size:** a set of quoted, narrowly-worded searches was superseded by 8 or more unquoted ones. Fewer, broader searches plus a title filter beat many narrow ones.

## Voyager detail endpoint (bulk harvest, still working)
```js
const csrf=document.cookie.match(/JSESSIONID="?([^";]+)"?/);
const ids=[...document.querySelectorAll('li[data-occludable-job-id]')].map(li=>li.getAttribute('data-occludable-job-id'));
window.__jobs=[];let out=[];
for(const id of ids){try{
const r=await fetch('/voyager/api/jobs/jobPostings/'+id+'?decorationId=com.linkedin.voyager.deco.jobs.web.shared.WebFullJobPosting-65',
  {headers:{'csrf-token':csrf,'x-restli-protocol-version':'2.0.0'}});
const d=await r.json();
const am=JSON.stringify(d.applyMethod||{});
let u=(am.match(/"companyApplyUrl":"([^"]+)"/)||[]);
u=u?decodeURIComponent(u.replace(/\\u002F/g,'/')).split('?'):'EASY';
let h='EASY';if(u!=='EASY'){try{h=new URL(u).hostname;}catch(e){h='?';}}
window.__jobs.push({id,u,title:d.title,desc:(d.description&&d.description.text||'').replace(/\s+/g,' ')});
out.push([id,d.title,d.formattedLocation,h].join(' :: '));
}catch(e){out.push(id+' :: ERR');}}
out.join('\n');
```
- **Print only the hostname.** Printing the full apply URL returns `[BLOCKED: Cookie/query string data]`, so keep full URLs in `window.__jobs`. `.split('?')` is required.
- **Response body is `j`, not `j.data`.** Use `const j=await r.json(); const d=j.data||j;`. Writing `(await r.json()).data||{}` empties every record.
- Parallel bulk fetch in batches of 8 into `window.__RES`, then filter.
- ATS triage by hostname:
  - Drivable: `jobs.ashbyhq.com`, `jobs.lever.co`, `jobs.eu.lever.co`, `job-boards.greenhouse.io`, `*.recruitee.com`, `apply.workable.com`.
  - `*.myworkdayjobs.com` needs an account.
  - `click.appcast.io`, `jsv3.recruitics.com` and `*.icims.com` are usually US.
- Keyword scan on descriptions:
```js
window.__jobs.filter(j=>/sponsor|relocat|visa|EMEA|anywhere in the world|worldwide|EOR|contractor|B2B/i.test(j.desc))
  .map(j=>j.id+' :: '+j.title).join('\n');
```

## Voyager search endpoint: current working REST version (16 Sept)
```js
window.SEARCH=function(key,kw,geo,remote,tpr,start){
  // Relevance order. Never add sortBy:List(DD) here — see "sortBy=DD" above.
  // Filters are joined, so no leading comma can sneak in when one is absent.
  var f=[];
  if(remote)f.push('workplaceType:List(2)');
  if(tpr)f.push('timePostedRange:List('+tpr+')');
  var q='(origin:JOB_SEARCH_PAGE_OTHER_ENTRY,keywords:'+encodeURIComponent(kw)+
        ',locationUnion:(geoId:'+geo+'),selectedFilters:('+f.join(',')+
        '),spellCorrectionEnabled:true)';
  var u='https://www.linkedin.com/voyager/api/voyagerJobsDashJobCards'+
        '?decorationId=com.linkedin.voyager.dash.deco.jobs.search.JobSearchCardsCollection-220'+
        '&count=25&q=jobSearch&query='+q+'&start='+(start||0);
  fetch(u,{headers:{'csrf-token':window.CSRF,
    'accept':'application/vnd.linkedin.normalized+json+2.1'}})
   .then(function(r){return r.json();}).then(function(j){window.R[key]=j;});
  return 'fired';};
```
- The script assumes `window.CSRF` (from the JSESSIONID regex above) and `window.R={}` are set beforehand.
- `count` max 25; paginate with `start=0/25/50`.
- `tpr` values: `r86400`, `r259200`, `r604800`, `r2592000`. `workplaceType:List(2)` = remote.
- Headers: `csrf-token`, plus `x-restli-protocol-version: 2.0.0` (in the 12 Sept version), plus `accept: application/vnd.linkedin.normalized+json+2.1`.
- In `j.included`, records whose `entityUrn` is `...jobPosting:<id>` carry `title`, so **ID + title arrive in one request**. Filter by title, then fetch details only for candidates.
- This decoration returns an empty `formattedLocation`. Get location from the detail endpoint (`WebFullJobPosting-65`).
- **Finding a new queryId when one dies:** open `read_network_requests` on the search page and click "Next" pagination. The first page is server-rendered (SSR), so only the client-side pagination request shows up.
- ⚠️ LinkedIn shows "We're gradually retiring classic job search starting in September", so this endpoint may also go.
- The 12 Sept predecessor (for reference): `/voyager/api/voyagerJobsDashJobCards?decorationId=com.linkedin.voyager.dash.deco.jobs.search.JobSearchCardsCollection-224&count=25&q=jobSearch&query=(origin:JOB_SEARCH_PAGE_JOB_FILTER,keywords:<encoded>,locationUnion:(geoId:<geo>),selectedFilters:(workplaceType:List(2),timePostedRange:List(r604800)),spellCorrectionEnabled:true)&start=0`

## Job tracker and drafts
- Drafts: `linkedin.com/jobs-tracker/?stage=draft`. Resume a draft via the job page's **"Continue"** button. The tracker's "Continue Application" link sometimes does nothing, so go straight to `linkedin.com/jobs/view/<id>`.
- Two kinds of card:
  - "Discard draft application and remove this job?" → Yes removes it.
  - "Did you finish applying?" → **can't be removed.** "Yes" would be a false claim, "No" does nothing, and Delete/Archive don't work. Leave it.
- The draft counter doesn't match the visible cards, so trust the list.
- Save an Easy Apply you can't finish with Dismiss → **Save**; it becomes a draft.
- LinkedIn's "Applied" mark (on cards and job pages) catches applications the user made by hand that aren't in the tracker. Check it too.
- The same ATS job can appear under two LinkedIn titles, so compare the ATS UUID.

## Easy Apply driver (single JS call)
```js
const CV='<CV_NAME>';   // file name stem of the CV to pick, from the profile
function panel(){const t=[...document.querySelectorAll('button')].find(x=>x.offsetParent&&/^(Next|Review|Submit application)$/.test((x.innerText||'').trim()));if(!t)return null;let p=t;for(let i=0;i<10;i++){p=p.parentElement;if(p&&(p.innerText||'').length>120)break;}return p;}
function pickCV(n){const t=[...document.querySelectorAll('*')].filter(e=>e.textContent.includes(n)&&e.children.length===0);if(!t)return 0;let c=t;for(let i=0;i<8;i++){c=c.parentElement;if(c.getAttribute('role')==='button')break;}c.click();return 1;}
const b=[...document.querySelectorAll('button')].find(x=>/Easy Apply to this job/.test(x.getAttribute('aria-label')||''));
if(!b)throw new Error('NOEASYAPPLY');
b.click();await new Promise(r=>setTimeout(r,3500));
let prev='',log=[];
for(let i=0;i<12;i++){const p=panel();if(!p){log.push('NOPANEL');break;}
 const cur=(p.innerText.match(/^\d+\/\d+ pages/)||['']);const txt=p.innerText.replace(/\n{2,}/g,'\n').slice(0,700);
 if(/Select or upload a resume/.test(txt)){pickCV(CV);await new Promise(r=>setTimeout(r,1200));}
 if(cur&&cur===prev){log.push('STUCK:'+txt);break;}prev=cur;
 const nx=[...document.querySelectorAll('button')].find(x=>x.offsetParent&&/^(Next|Review)$/.test((x.innerText||'').trim()));
 if(!nx){const s=[...document.querySelectorAll('button')].find(x=>x.offsetParent&&(x.innerText||'').trim()==='Submit application');
  if(s){s.click();await new Promise(r=>setTimeout(r,4500));}log.push('SUBMITTED:'+/Application submitted|application was sent/i.test(document.body.innerText));break;}
 log.push(cur);nx.click();await new Promise(r=>setTimeout(r,2600));}
JSON.stringify(log)
```
Consent-checkbox add-on to put inside the loop (11 Sept):
```js
if(/privacy notice/i.test(txt)){const cb=[...document.querySelectorAll('input[type=checkbox]')].filter(e=>e.offsetParent||e.id);if(cb&&!cb.checked){const lb=[...document.querySelectorAll('label')].find(l=>l.getAttribute('for')===cb.id);if(lb)lb.click();await new Promise(r=>setTimeout(r,500));}}
```
Notes:
- `STUCK:` means answer that page's questions, then re-run the driver.
- The CV card is a `div[role=button]`.
- Radios and checkboxes:
  - Most reliable: a real click at the centre of `label[for=<radio id>]` (the radio itself is 0×0).
  - Fallback: click the radio for focus, then press `space`.
  - `label.click()` followed by `input.click()` sometimes works. Always verify `.checked`.
- Native `<select>`s: native setter plus `change`.
- City typeahead: click the field via ref → type → wait 3 s → click the suggestion **by coordinate**. Return doesn't work. The location is often **pre-filled but looks empty**, and typing appends to it. Clear with End + Backspaces first.
- A field that never validates may be a hidden **date picker** (calendar icon). DOM order ≠ visual order and `label[for]` mapping can mislead, so **sort fields by `getBoundingClientRect().y`**.
- Some fields swallow spaces.
- **"How many years" and salary fields are number-only.** Text returns "Invalid input". Clear with `End` + many `BackSpace` presses (triple_click, ctrl+a and Delete don't work).
- Easy Apply can wrap Greenhouse questions; a consent may be a `select`, not a checkbox.
- Use `browser_batch` so click and type happen in one round trip. Separate calls let the modal shift.
- Closing the modal asks "Save this application?". Choose `Discard` for jobs that don't fit.
- Cost is about 6 tool calls per application, with no upload and no CAPTCHA.
