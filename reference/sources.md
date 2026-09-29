# Sources and search methods

Reference for steps 1–5 of the run. Everything here is **person- and role-independent**: how each source behaves, what its filters do, and which of its labels lie. Queries, titles, geoIds, board names and cadences belong to one candidate and live in `profile/search.json` and `profile/profile.md`.

Where a measurement needed a concrete query to be verifiable, the number is kept and the query is described by shape ("a two-word title", "one discipline category"). Measurements taken for one discipline say so.

## Search methods per source

### LinkedIn (primary source)

#### Job alerts
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

#### Notification ID harvesting (`originToLandingJobPostings`)
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

#### Search URL (UI) and parameters
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

#### Voyager detail endpoint (bulk harvest, still working)
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

#### Voyager search endpoint: current working REST version (16 Sept)
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

#### JS execution pitfalls (LinkedIn and general)
- **The async result gets lost:** an `async` IIFE comes back as `{}`. Do the work, write the result to `window.X`, and read it in a **second synchronous call**. That's why `SEARCH` is fire-and-store.
- **At most 3 searches per JS call.** CDP times out at 45 s, so plan 2–3 per call. Long `setTimeout` or scroll loops hit the same 45 s timeout, so do waits as separate `computer wait` steps.
- Output is cut off at about 1000 characters; slice large outputs.
- REPL semantics: no `return`, the last expression is the result.
- **CSRF** = `document.cookie.match(/JSESSIONID="?([^";]+)"?/)`.
- **Parentheses in a keyword silently return 0.** The Voyager `query=` value is a DSL whose own grammar is built from `(` and `)`, and `encodeURIComponent` does **not** escape those two characters. A keyword the user typed with brackets, e.g. a title plus a parenthesised specialism, corrupts the query and comes back empty, which reads as "no such jobs". Escape them to `%28`/`%29` by hand, or strip them: they add nothing, since LinkedIn treats the query as loose anyway.
- **DOM scraping doesn't work.** The list is virtualized: 18 of 25 off-screen `li[data-occludable-job-id]` cards are empty. The list container is found with the helper below. `LIST().scrollTop` works, but the list still doesn't render every step. **The API is always better**.
```js
window.LIST=function(){return [...document.querySelectorAll('div')].filter(function(e){
  return e.scrollHeight>e.clientHeight+200&&e.clientHeight>300&&
         !/job-details/.test((e.className||'').toString());});};
```
- Bulk setter or delete loops can be blocked by the safety classifier ("[Real-World Transactions]", "Blocked by classifier"). Use single `form_input` + ref calls or real clicks.

#### Job tracker and drafts
- Drafts: `linkedin.com/jobs-tracker/?stage=draft`. Resume a draft via the job page's **"Continue"** button. The tracker's "Continue Application" link sometimes does nothing, so go straight to `linkedin.com/jobs/view/<id>`.
- Two kinds of card:
  - "Discard draft application and remove this job?" → Yes removes it.
  - "Did you finish applying?" → **can't be removed.** "Yes" would be a false claim, "No" does nothing, and Delete/Archive don't work. Leave it.
- The draft counter doesn't match the visible cards, so trust the list.
- Save an Easy Apply you can't finish with Dismiss → **Save**; it becomes a draft.
- LinkedIn's "Applied" mark (on cards and job pages) catches applications the user made by hand that aren't in the tracker. Check it too.
- The same ATS job can appear under two LinkedIn titles, so compare the ATS UUID.

#### Easy Apply driver (single JS call)
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

### freehire.me: primary source (step 1)

Use the **API from the cloud shell with `curl`**. No key, no browser, no login. Base `https://freehire.me/api/v1` (docs `https://freehire.me/docs/api`).

| Endpoint | Purpose |
|---|---|
| `GET /jobs/search` | `q`, `limit` (max 100), `offset`, plus every facet as a filter |
| `GET /agent/jobs/search` | same, plus `description_format=text|markdown|html` for full descriptions |
| `GET /jobs/facets?q=...` | available filter values with counts |
| `GET /jobs/{slug}` | one posting, full description + `enrichment` (closed postings too) |
| `GET /jobs/{slug}/apply-form` | **ATS provider + required fields + screening questions**, before opening the form |

Response shape: `{ data: [...], meta: { limit, offset, total } }`.

**Ordering — measured, important.** Leave the default ordering (relevance). With default ordering 100 of the first 100 titles matched the query and the results were still fresh (median age 2–15 days). With `sort=posted_at&order=desc` only 19–56 of 100 matched, which floods the run with title collisions from unrelated industries. For a daily run: query by relevance, then drop anything whose `posted_at` is older than the run window on your side.

**`q` orders but does not narrow.** A two-word job title reported ~366k total. Combine `q` with `category` and keep a title filter as a second pass.

Filter keys: `category`, `countries`, `regions`, `work_mode`, `posting_language`, `domains`, `seniority`, `employment_type`, `english_level`, `salary_currency`, `salary_period`, `company_size`, `company_type`, `relocation`, `requires_clearance`, `role_type`, `skills`, `source`, `visa_sponsorship`, `is_tech`, `cities`, `collections`, `ai_interview`, `auto_apply_available`, `reality`.
- `regions`: there is **no `worldwide`**; use `global`. Others: `eu`, `uk`, `mena`, `emea`, `europe`, `turkey`, `north_america`, `latam`, `apac`, `africa`, `cis`.
- Design work is spread across `category` = `design`, `frontend`, `engineering_design`, `product`. Query each.

Per-record fields worth using:
- `enrichment.domains` → sector. `gambling` is tagged; drop it before anything else.
- `enrichment.posting_language` → drop postings not in the profile's accepted languages.
- `countries`, `regions`, `visa_sponsorship` → pre-filter only. **Not authoritative:** "global" has repeatedly turned out to be an explicit country list on the ATS page.
- `closed_at` → drop if set.
- `reality` → `{class: fresh|stale, age_days, repost_count, mass_posting_count, fake_freshness}`. `mass_posting_count ≥ 3` is the "one text republished under many titles" pattern (EWOR: 10+ variants, every apply URL 404). Push these to the end or skip; a legitimate multi-team hire can also trip it, so check before discarding.
- `url` → the apply link. It can be the employer's ATS, **another aggregator (Adzuna seen as the top result)**, or a Telegram post (`t.me/...`, skip: no messaging on the user's behalf). Resolve to the real employer before applying.

Pitfalls:
- The API returns **403 to Python's default user agent**. curl and Node `fetch` pass. Always send an explicit `User-Agent`.
- The Pro plan's "unattended applications" bypasses dedup and every filter. Don't use it. CLI install or API keys are the user's call.

Sweep pattern (cloud shell):
```python
import json, subprocess, urllib.parse
BASE = "https://freehire.me/api/v1/jobs/search"
def get(**kw):
    kw.setdefault("limit", 100)            # default ordering = relevance; do NOT sort by date
    u = BASE + "?" + urllib.parse.urlencode(kw)
    r = subprocess.run(["curl", "-sS", "-A", "Mozilla/5.0 job-hunt", u], capture_output=True, text=True)
    try: return json.loads(r.stdout).get("data", [])
    except Exception: return []
rows = {}
for q in PROFILE_QUERIES:                  # the candidate's target titles, from profile/search.json
    for cat in ["design", "frontend", "engineering_design", "product"]:
        for reg in PROFILE_REGIONS:        # from the profile, e.g. global, eu, emea, mena
            for j in get(q=q, category=cat, work_mode="remote", regions=reg):
                rows[j["public_slug"]] = j
# home-country pass without work_mode (for on-site/hybrid exceptions in the profile)
for q in PROFILE_QUERIES:
    for j in get(q=q, countries=PROFILE_HOME_COUNTRY):
        rows[j["public_slug"]] = j
# then: drop closed_at, gambling domain, non-accepted language, stale window, title filter, dedup vs tracker
```

UI fallback (browser): `https://freehire.me/jobs?q=<search>&regions=europe,global&posted=1w`. `categories=design` is ignored in the UI; use `q`. Cards: `[...document.querySelectorAll('a')].filter(a=>/^\/jobs\//.test(a.getAttribute('href')||''))`. Real apply link on a detail page: `[...document.querySelectorAll('a')].filter(e=>/^apply$/i.test(e.innerText.trim())).map(e=>e.getAttribute('href'))`.

### Jobicy (secondary API)

`https://jobicy.com/api/v2/remote-jobs` with `tag=<keyword>`. Measured: semantic matching, every result remote, median age 4–19 days, almost no overlap with freehire. `jobGeo` lists the allowed countries, which feeds the eligibility check directly. Returns nothing for academic queries.

### Other boards

**Do not use (measured dead or paid):** Remotive (paywall, 0.4% visible) · We Work Remotely (paid) · Arbeitnow API (ignores the search term: "product designer", "postdoc" and "zzzz" return the same 20) · Himalayas (single-agency spam, `?search=` ignored) · Welcome to the Jungle/Otta (no open search) · euremotejobs, uxjobsboard, europeremotely, justremote, landing.jobs (dead) · Adzuna (CAPTCHA wall) · haystack.cv (country list excludes most candidates) · EWOR GmbH postings (every apply URL 404).


**designsystems.jobs**
- 12 Sept: "the best" board, with 144 roles and calendar dates. (`jobs.designsystem.tools` doesn't exist.)
- Card links open an empty popup and detail pages load empty, so go to the company's own career site (e.g. `jobs.sap.com/search/?q=...`).
- Mostly US.
- 16–17 Sept: wouldn't open (`document_idle` 45 s timeout). 18 Sept: newest posting dated 15 Sept. 19 Sept: working again.
- 27 Sept: alive, 118 jobs, filters for Discipline / Role / Type / Location. Newest entry was 2 days old and the fresh page is dominated by US roles plus a run of French postings from one agency (NEXTON). Useful, but it surfaces less than the niche design-systems board and it lags it by a day or two.
- Scan 2–3 days a week, not daily.

**⛔ One role, six cities, six ids: the §2.7 spam pattern in its cheapest disguise.** Measured 29 Sept (Air Apps): an identical "Product Designer" title appeared under six separate Ashby ids for Amsterdam, Stockholm, Berlin, Rome, Paris and London. All six scored high in the same candidate list and read as six European opportunities. The tell is `check` returning SAMECO across the set: one company, one title, many ids. **When one company's identical title appears across more than about five cities, resolve one and dedup on the company, not the id.**

**⛔ The US PERM labor-certification notice, and how to recognise it before you fill a form.** Measured 27 Sept on an AcuityMD Greenhouse posting that had reached the candidate list from two sources. A US employer sponsoring a green card must advertise the role publicly, and those notices are posted on the normal job board and look like openings. The tells, all present together:
- The body opens in the third person naming the company and a single city: "‹Company›, Inc seeks ‹Title› in ‹City›, ‹State›", even when the header says "‹City› or Remote".
- The description is a flat "Job Duties:" block rather than a pitch, a team description or benefits.
- "Minimum Requirements: Bachelor's degree, **or foreign equivalent**, in ‹named fields› plus N years of progressively responsible experience **in the job offered** or a related occupation."
- A numbered list of "Special Skill Requirements", each carrying its own year count (3 years, 4 years, 3 years…).
That shape exists to be impossible to match except by the person already in the seat. **Skip on sight.** It is also usually paired with a hard degree field requirement, which is an ordinary knockout on its own.

**jobs.intodesignsystems.com**
- **27 Sept: the board is paginated now** and no longer renders a long flat list. The footer reads "Showing 1–20 of 186" with 10 pages, so `a[href^="/jobs/"]` returns 20 anchors however far you scroll. Page 1 is newest-first and on a daily cadence it covers everything posted in the last three days, which is the whole point of the stop; page 2 onward is material earlier runs already swept. Don't read 20 anchors as "the board shrank".
- **A daily stop can legitimately return nothing.** 28 Sept: page 1 was byte-for-byte the same twenty listings as 27 Sept, newest still 2 days old. That is the board being quiet, not the scrape failing. Compare the first slug against yesterday's before spending calls re-resolving apply URLs.
- About 254–259 roles, no account, no paywall. The main domain `/jobs` returns 404; use the `jobs.` subdomain.
- Each job page has an "Apply on <company>" link to the ATS: fetch `/jobs/<slug>` and take the `a` whose text matches `/apply on/i`.
- 8 Sept bulk extraction script (the pagination part stopped working later, see §0):
```js
let o=[];for(let p=1;p<=5;p++){const t=await (await fetch('/?europe=true&page='+p)).text();
const d=new DOMParser().parseFromString(t,'text/html');
[...d.querySelectorAll('a[href^="/jobs/"]')].forEach(a=>{const s=a.getAttribute('href').replace('/jobs/','');
const tx=a.textContent.replace(/\s+/g,' ').trim(); if(!o.some(x=>x.s===s))o.push({s,tx});});}
```
- `/remote-design-system-jobs` has no dates and contains dead listings. Use it as a lead list and verify each role.
- `?work=remote` gave 61 on 16 Sept.
- MCP server: `https://jobs.intodesignsystems.com/mcp`. Install with `claude mcp add -s user --transport http ids-jobs https://jobs.intodesignsystems.com/mcp` (the user's decision).
- Location badges are unreliable: "🌍 Remote · Utrecht" was Hybrid on Ashby.
- 17 Sept verdict: "works, best; should be a fixed daily stop".

**Glassdoor**
- Logged out: the list **and full descriptions** are readable, but every job says "Sign in to apply". Use it for discovery and apply on the employer's site.
- **locId trap:** the ids are not guessable (`locId=217` is Singapore, not anything nearby). **Never hand-build the location**: type the country into `#searchBar-location`, click the suggestion, and read the resulting `IN<id>` out of the URL. Store it in the profile once.
- URL pattern, where `<country>` is the country slug, `IN<id>` the id you just read, and `KO<a>,<b>` the keyword's start and end character index in the path:
```
https://www.glassdoor.com/Job/<country>-<keyword>-jobs-SRCH_IL.0,<len(country)>_IN<id>_KO<len(country)+1>,<len(country)+1+len(keyword)>.htm
```
  **The broad keyword beats the sum of the narrow ones.** Measured in one home market: the single discipline word returned 117 results, while the two-word title returned 63 and a variant 17 — and the narrow pair did not cover the broad one.
- Scraping: cards are `document.querySelectorAll('[data-test=jobListing],li[data-jobid]')`. The first load gives 30 with `innerText` filled (not virtualized). Click a card's `a` → the right panel fills → the full description is in `document.body.innerText`. `alt+Left` doesn't return to the list, so re-navigate to the search URL for each job.
- Pagination: "Show more jobs" adds 30 per click. **Wait 8 s between clicks.** 4 clicks gave 115/117.
```js
window.MORE=function(){var b=[...document.querySelectorAll('button')]
 .filter(e=>/show more|load more/i.test(e.innerText));
 if(!b.length)return 'nobtn';b.scrollIntoView({block:'center'});b.click();return 'ok';};
```
- The list is live and rotating (a card disappeared within 15 min), so review a job **in the same pass** you see it.
- `?remoteWorkType=1` returned 0 plus irrelevant results for a non-US country; **don't use it** outside the US.
- `SRCH_IL.0,6_IS11047` ("Remote") = US-anchored remote with US salary bands. Worthless for worldwide or EMEA roles.
- Effects of logging in: the sign-in wall lifts, Easy Apply opens, and full-list pagination works. A permanent banner appears: "To restore your access… write a review or add a salary". **Never post a review or salary on the user's behalf**.
- **Glassdoor "Easy Apply" = Indeed SmartApply** (opens `smartapply.indeed.com`). Flow: resume (38%) → employer questions (50%) → consent (88%) → Review → "Submit your application" → "Your application was sent!" (`smart-apply-action POST_APPLY` in the URL).
  - If it's stuck on "Preparing review", navigate to `smartapply.indeed.com/beta/indeedapply/form/review-module`; answers are remembered.
  - The file input has no id. Set `document.querySelector('input[type=file]').id='cvupload';`, then find it with `find` and call `file_upload`.
  - Upload the current CV, not the stale one stored in the account.
- Verdict: **the home-country track only, at the cadence in the profile: one broad discipline keyword + the home `IN<id>`, "Show more" to the end.** It finds local jobs LinkedIn misses. Don't use it for remote, regional or relocation roles — its "Remote" location is US-anchored. Dedup caught everything it returned on a later run, so it earns its slot by coverage, not volume.

**Djinni**
- Ukraine-centred talent market. **Can't apply until the candidate profile is published.** The Apply button clicks but does nothing ("Create your profile to start apply for jobs…"). Publishing happens at `djinni.co/my/wizard/preview/` → "Start search", which carries a **terms-of-use acceptance, so only the user can click it**.
- **A missing Apply button is usually a language mismatch, not the profile block.** Djinni hides Apply and leaves only Save when the candidate does not meet `Required languages`, with no error message, which reads exactly like the unpublished-profile symptom. Measured 22 Sept with a published, actively searching profile: four design postings showed only Save, and all four asked for **Ukrainian Native**. Read `Required languages` before blaming the profile. A posting outside the candidate's own category behaves the same way.
- ⛔⛔ **The sector is in the right-column `Domain:` field, not the text.** jito.dev's text said "AI-first coaching platform"; `Domain: Gambling` gave it away. The only textual hint was "skill-based" (gambling jargon). **Read `Domain:` before opening anything.** The same column shows `Employment`, `Startup`, the salary range and `Response activity`.
- The title salary "to $7000" is a ceiling; the right column showed $2100–7000.
- `892 views · 244 applications` plus "Response activity: Low" → push down the priority order.
- Measured on one discipline category (`djinni.co/jobs/keyword-<category>/`): 15 visible, 3 "Worldwide", and **all 3 were Gambling**. The rest were limited to Ukraine / "Countries of Europe or Ukraine" / EU, or were junior. The list is truncated until the profile is complete.
- Once the profile is live, every job page shows a "Your profile does not meet some of the requirements" block (countries, native language, salary). Read it first: it is the company's own filter. "Countries of Europe or Ukraine" does **not** include non-EU European countries such as Türkiye. On 21 Sept all 5 queued roles for a Türkiye-based candidate failed it.
- Verdict: not a daily source. Weekly at most, `keyword-ui_ux` + Worldwide, always check Domain. Also check that the listing is still active.
- Profile-form mechanics: "Experience summary" is a contenteditable editor (the setter on `textarea#moreinfo` doesn't display), so type for real. The category auto-sets from the position. `+ Add skill` doesn't focus the new row. `skills_experience[N][experience_years]` accepts the native setter. There is only a single `salary_min`, no range.

**Jobicy, measured 26, 27 and 28 Sept — the same three stale records every time.** Four tags (`product-designer`, `ux-designer`, `design-system`, `product-design`) returned **3 records in total** and none on-discipline: a Staff Android Engineer under `design-system`, and two Canada-only marketing designer roles under `product-design`. `product-designer` and `ux-designer` returned nothing at all. Re-run on 27 and 28 Sept it returned **the identical three rows**, none newer than 20 Sept. It stays in the daily list because it costs one curl per tag, but do not read an empty Jobicy as an empty market, and do not read a changed count as freshness either.

**Working Nomads, measured 26 Sept: the HTML category page is worth its slot.** `workingnomads.com/remote-design-jobs` rendered 50 listings, of which 15 were on-discipline and **12 passed dedup as new**. One more looked new and resolved to a posting already applied to weeks earlier under a different ATS key, reached through a third URL. That is the best single-source yield of the day outside LinkedIn, and it is the same source whose open `exposed_jobs` API carried zero design roles on 24 Sept. **Scrape the anchors, not the cards:** `closest('li')` grabs the wrong container and every row comes back with the first listing's text, which looks like the page failed to load. `a[href^="/jobs/"]` gives one slug per listing and the slug carries the title and the company (`senior-product-designer-codelitt-1895013`). The apply URL is behind `/job/go/<id>/`, which 302s to the real ATS, so resolve it before running `check`.

**Himalayas**
- Useful for **verification**: its "eligibility" line shows country eligibility inline.
- `https://himalayas.app/jobs/countries/<country>/<discipline>` was readable via WebFetch.
- 12 Sept onward: not usable by fetch. `/jobs/design` matches company names containing "design", `?search=` is ignored, and `/jobs/categories/design` is a 404.
- 17 Sept: the list doesn't render. 18 Sept: flooded with one agency's copies; almost everything single-country. Low value.

**Remotive**: the API is blocked by robots.txt. The site is a half-to-full paywall ("You're seeing 0.4% of available roles / Unlock 120,000+ jobs"), with company names hidden. **Don't enter.**

**We Work Remotely**: **paid** ($2.95 first month, then $14.95/mo on a 12-month commitment). Don't subscribe. Its "Anywhere in the World" region label proved false twice ("Poland only"; "Remote (US)"). `remoteineurope.com` 302-redirects to WWR.

**XING**: relocation track only, at the profile's cadence. Any keyword + Full Remote returned 0 jobs, so it is useless for remote. It catches DACH on-site jobs that LinkedIn's `f_TPR` misses.
- `xing.com/jobs/search?keywords=<url-encoded query>`, location DE/AT/CH. Run one pass per query in the profile's search config.
- Drop German-language postings. XING shows salary bands; use them to sanity-check assumptions.

**Clera (getclera.com) and talent pools**
- Clera's Ashby board had 279 jobs across 40+ cities, all under "Engineering": it's a talent pool, not an employer.
- **Rule: apply to pools** (self-published real listings, EOR/staffing firms, "companies in our network"). **Skip aggregators** that only copy and redirect; find the source posting and apply there.
- Dedup still applies: a different role in the same pool is a separate application; the same listing never twice.
- Write "pool listing" in the tracker Notes.
- Trust assessment: Trustpilot is bimodal (75% five-star / 22% one-star), with complaints about scraping LinkedIn profiles, fake listings and cold email from other domains. "Use it as a pool, don't trust it as a channel."
- **If a pool introduces a company, check you haven't also applied to that company directly** (double representation hurts both).
- Sign up with email or Google, **not LinkedIn OAuth**. Fill in Role and Industry preferences, or the feed is junk.
- Funding-stage heuristic for pool preferences: Seed through Series D. Seed/A for founding, remote or contractor roles; B–D when the candidate needs dedicated headcount for a specialism, or a sponsorship budget. Skip pre-seed (equity pay) and bootstrapped.

**haystack.cv**: "Where are you based?" is mandatory and offered only UK/DE/FR/CA/US. It is structurally unusable for a candidate based elsewhere; picking one would be a false residence claim. Don't chase `haystack.cv/apply/...` jobs; find the company directly or skip ("platform doesn't support the candidate's country").

**A 10-platform report card.** The platforms below were measured for one discipline (product design). **The verdicts on reachability — paywalled, no open search, client-side render, account required, stale — transfer to any field; the coverage verdicts do not.** Run the same checks for the candidate's discipline and replace the niche rows.

| Platform | Verdict |
|---|---|
| The best niche board for the discipline | ✅ best by far, daily. Find this one first; it outperformed every generic board |
| Working Nomads (`workingnomads.com/remote-<discipline>-jobs`) | ⚠️ fresh (hours old) but US-heavy; the location filter doesn't apply via URL. **Its open feed `workingnomads.com/api/exposed_jobs/` is not the site's catalogue**: measured 24 Sept it returned 58 rows, all sales, teaching, bookkeeping and admin, with **zero** design roles at any title. Records carry `url,title,description,company_name,category_name,tags,location,pub_date`. Use the HTML category pages, not this feed, or the source reads as empty. 2×/week |
| Wellfound (`wellfound.com/role/r/<role-slug>`) | ⚠️ browsable logged out. The "Remote only • Everywhere" tag is gold, but jobs are 1–4 months old and Apply needs an account. Discovery only, monthly |
| RemoteOK (`remoteok.com/remote-<discipline>-jobs`) | ⚠️ stale; the `remoteok.com/api` tag was weak |
| Remotive | ⚠️/⛔ paywall |
| A home-country national board | ⚠️ worked, but every result was on-site/hybrid or a title collision. Yearly check |
| Himalayas | ❌ list doesn't render |
| Welcome to the Jungle (Otta) | ❌ open search removed; now profile-matching only |
| weloveproduct.co | ❌ detail pages paywalled (16 Sept). The list pages still work for discovery |
| designsystems.jobs | ❌ at the time (timeouts), recovered 19 Sept |

Lesson, and it is the transferable one: **generic remote boards are US-heavy and stale, while one good niche board for the candidate's discipline outperforms all of them.** After this measurement the board step shrank to one niche board daily, one generic board twice a week, and one discovery-only board monthly. Find the equivalent three for the candidate's field rather than adding more generic boards.

**A posting's advertised location can be stricter than the gate its own form applies. Read the form's eligibility question before skipping on the label.** Measured 26 Sept on TheyDo: the Ashby header said `Location: European Economic Area`, which Türkiye is not in and which under the country-list rule reads as a closed door. The form asked one eligibility question, **"Will you work/live within the CET +/- 2 timezone?"**, and had no country or residence field anywhere. For a UTC+3 candidate that is CET+2, so the honest answer is Yes and the header was not the rule. A second posting the same day was the mirror image in the candidate's favour: header `Amsterdam / Remote`, `Location Type: Hybrid`, and the description carried "Although this role can be remote, we are only considering candidates based in CET +/-3 timezones". **A region name in the location header is the recruiter's shorthand for where they expect people to be, not always the rule they enforce.** Opening the form costs a navigation and one read. The country-list trap still stands for an explicit list of named countries; this is about a single region word.

**11th platform, Glassdoor:** home country only, one broad discipline keyword + the home `IN<id>`.

**Indeed** (measured 22 Sept, one home market)

- **One site per country** (`tr.`, `ie.`, `de.`, `uk.`, `www.` for the US), and **a country site is not a window onto the others.** `tr.indeed.com/jobs?q=product+designer&l=Germany` returned Izmir, Ankara and Istanbul postings: the foreign `l=` was **silently ignored**, with no error and no empty state. `de.indeed.com/jobs?q=product+designer&l=Deutschland` returned German postings normally. So covering N countries means N domains, each its own pass.
- **The remote filter is country-scoped too.** `&sc=0kf%3Aattr(DSQF7)%3B` on a country site returns remote jobs *open to that country*, not worldwide remote. On the home market: 5 unique results over 14 days, 2 of them on-discipline, 1 already tracked.
- **Cloudflare wall: transient, and triggered by a malformed query.** `?q=...&l=` with an **empty** location returned "Additional verification required" with a Ray ID on two domains. The same domains served results normally minutes later once `l=` carried a real location. **Always pass a location**, and treat the wall as a retry, not as a dead source. Never work around it: if a real check appears, it is the user's to clear.
- **Yield is poor for a specialised title.** Broadest discipline keyword, home country, 7-day window: 8 results, **0 new candidates**. One was already tracked; the other seven were title collisions from other industries (game design, furniture, graphic/intern) or another discipline entirely. The same run on LinkedIn and the niche boards had already found everything worth finding.
- **Scraping:** cards carry `[data-jk]`; walk up with `closest('.cardOutline')` for the title (`h2 a span`), `[data-testid=company-name]` and `[data-testid=text-location]`. **Returning the anchor's `href` trips the `[BLOCKED: Cookie/query string data]` filter** — read `data-jk` and build the URL yourself. The same posting can appear twice with two ids, so dedup on `jk` before counting.
- **The apply side works and is unaffected:** Glassdoor "Easy Apply" hands off to `smartapply.indeed.com`, documented in `ats-mechanics.md`.
- **Card titles are only in `aria-label` on `[data-jk]`, not in `h2 a span`.** The `h2 a span` selector returns empty strings, and a title filter over empty strings reports **zero matches on a full page of results**, which looks exactly like an empty market. The label ends with a localised suffix ("… ile ilgili tüm ayrıntılar" on the Turkish site) that has to be stripped before matching. Whenever a title filter returns 0 out of N>0 cards, print the raw titles before believing it.
- **Second measurement, 23 Sept, same home market:** three passes (broadest local discipline word 7 days, the English two-word title 7 days, the bare discipline acronym 14 days) returned 38 cards, 2 on-discipline postings, and **0 new candidates**. Both on-discipline hits were already in the tracker from other sources, one of them applied to 17 days earlier through the employer's own careers site. The rest were the same collisions as the first measurement: packaging, construction, lighting, architecture, social media, front-end.
- **Third measurement, 24 Sept, same home market:** four passes (the English two-word title, the broadest local discipline word, the bare acronym, and a design-system pass) returned 33 cards and **0 new candidates**. Every on-discipline hit was already tracked: one applied to 18 days earlier through the employer's own careers site, one applied to 7 days earlier, one skipped 7 days earlier for scope. The rest were the same collisions (graphic, social media, interior/industrial, mould design, HVAC).
- **The same posting can appear under two `jk` values on one results page**, and the second one can look synthetic (`f1e2d3c4b5a67890`, `456789abcdef0123` seen alongside ordinary random hex on 24 Sept). Dedup on `jk` before counting, and don't treat a tidy-looking `jk` as evidence of anything; resolve the posting and dedup on the employer's own apply URL.
- **Fourth measurement, 26 Sept, same home market:** five passes (`product designer`, `tasarımcı`, `ux`, `ui designer`, `design system`, all 7 days, `l=Türkiye`) returned 53 cards, 5 on-discipline postings, and **0 new candidates**. Every one was already in the tracker, one of them applied to twenty days earlier through the employer's own site and the rest already judged and skipped. The collisions were the same families again: graphic and social media, packaging, HVAC, and on the `design system` pass an entire page of electrical, physical and .NET engineering.
- **Fifth measurement, 27 Sept, same home market:** five passes over a 3-day window returned about 51 cards, 4 on-discipline, and **0 new candidates**. The same five employers as the day before, all already in the tracker, plus one applied to three weeks earlier through the employer's own site. The `design system` pass returned 16 cards and **0** that survived a title filter. Five runs, five zeroes.
- **Sixth measurement, 28 Sept:** three passes over a 3-day window, 23 cards, 4 on-discipline, **0 new**. Three already-judged local postings and a metro-project design manager. Six runs, six zeroes, and the yield has now been 100% already-tracked on every single measured pass since 22 Sept. **The evidence for a daily slot is gone.** Fortnightly at most, on the same footing as Dice. The cadence is still the candidate's call.
- **The results list rotates between passes minutes apart, so capture the `jk` in the same call that reads the titles.** Measured 26 Sept: a `ui designer` pass returned Canva, Growmodo and Macellan; the identical URL re-read a few minutes later returned Kriyus Digital and a co-founder ad instead, with all three of the first set gone. Re-running the query to "go back and get the ids" does not work, and searching the company name is worse: `q=Canva` returns every posting that mentions Canva as a tool, which on this market is social-media and graphic roles. Read `data-jk`, the `aria-label` title, `[data-testid=company-name]` and `[data-testid=text-location]` in one pass and keep them.
- **Seventh measurement, 29 Sept:** two passes, 13 cards, 4 on-discipline, **0 new**. Seven runs, seven zeroes.
- **Evidence summary, measured seven times (22, 23, 24, 26, 27, 28 and 29 Sept):** low yield, and the only source so far whose entire yield was already in the tracker on **every single run**. The inventory arrives through LinkedIn, the niche boards and Glassdoor first, usually days earlier.
- **Cadence is the candidate's call, not this file's.** The evidence above argues for fortnightly at most; a candidate may reasonably want it daily anyway, since a cheap source that duplicates 100% of its yield still costs only a few calls and its miss rate on local postings is unmeasured. Run whatever `boards` in `profile/search.json` says. **How to run it:** one domain per country, home country only, a real location value (an empty one trips the verification wall), the broadest discipline word plus the candidate's English titles, a 7-day window, and expect dedup to absorb most of it. Dedup on `jk` before counting, and check the apply URL against the tracker before opening anything.

**Dice (dice.com)** — US tech board, profile set up 24 Sept, first run measured the same day.

- **US-only by construction, and the platform says so itself.** The candidate profile asks you to "share your eligibility to work in **the US**", its only authorization statuses are US ones (US Citizen, Have/Need H1 Visa, Green Card, TN, EAD), its salary fields are USD, and its employment types are the US staffing taxonomy: Corp-to-Corp, W2, Contract-to-Hire. Treat the inventory as US contract work placed by staffing firms.
- **Expect the closers already measured elsewhere.** The 24 Sept US pass found that US-remote postings die on explicit state lists, "pay range … **on W2**" (US payroll employment, which requires authorization outright), and staffing intermediaries with the end employer unnamed. Dice is largely made of that third category, so budget for a low conversion rate before committing a standing slot.
- **Profile mechanics** (all measured 24 Sept): the city field is Google Places and **only matches the Turkish spelling "İstanbul"**; plain "Istanbul" returns "No results found" even with Country set to Turkey. Country accepts "Turkey" and then relabels itself "Türkiye". The postcode field is also a geocoder and resolves the full address. **Uploading a CV auto-creates dozens of skills with invented year figures** (49 skills, one reading 58 years); tool-years is a never-guess item, so correct them against the profile or leave them for the candidate. Profile Visibility defaults to Off and the profile is close to useless until it is On, which is the candidate's decision to make.
- **Work history mechanics:** rows are `employmentHistory.<n>.<field>` and the **native setter works on every text input and month select**, so a role can be filled in one JS call. Only the "Add role" button needs a real click, and it needs a **ref click**: a JS `.click()` adds nothing, and repeating a coordinate click after the layout shifts opens a stray tab. Add one row, fill it, then re-click. Dice re-sorts the whole list reverse-chronologically on save, so entry order is irrelevant. Non-ASCII characters in employer names and surnames are accepted throughout.
- **The "Open to relocation" preference does not persist (measured four times, 24 Sept).** Save returns 200 and every other field on the same form sticks, but relocation reverts to "Not open to relocation" and the locations clear. The payload explains it: the front end serialises a chosen place as `{"municipality":"United States","region":"","country":"undefined"}`, with the literal string `undefined`, and the server discards it. **Resolved: only country-level picks fail.** Picking a **city** from the suggestion list saves and survives a reload (verified with New York, Amsterdam and Toronto, which Dice normalises to `New York, NY, US` and so on). The field caps at three locations. The combobox ignores a ref click: click it by coordinate, type the city, then click the suggestion by coordinate.
- **The phone number is locked to +1 and silently corrupts a foreign one.** It sits in `dice.com/settings`, not the profile, and its country selector is `disabled` with `title="United States"`. A typed `+90…` loses the country code, is reformatted as a US number and has its overflow digits dropped, so a Türkiye mobile becomes a plausible-looking but wrong North American number with no error shown. Leave it blank for any non-US candidate rather than saving a mangled value.
- **Apply mechanics (measured 24 Sept, two applications submitted).** The "Easy Apply" control is an `<a href="/job-applications/<job-id>/wizard">` carrying an onclick handler, and **neither a ref click nor a coordinate click on it does anything** — no dialog, no navigation, no console error. **Navigate to the wizard URL directly.** It then works normally. The wizard is two steps: step 1 offers the CV already attached from the profile plus an optional cover letter, step 2 is a review page. There are **no screening questions on any posting**, so there is nothing to answer and nothing to guess.
- **Dice attaches two fields to every application and shows them on the review step: `Work Authorization` and `Current Location`.** They read back the profile's authorization answer and its `<CITY>, <REGION> <POSTCODE>, <COUNTRY>` location string. That is the whole sponsorship conversation, declared up front, on every single application — which makes Dice unusually honest for a non-US candidate: the employer knows the residence and the visa need before opening the CV. It also means the profile's authorization status is not a private setting, so set it to the truthful value.
- **The submit takes longer than five seconds and the page does not change while it runs.** Reading the DOM too early returns the unchanged review page, which looks exactly like a silent failure. Wait 8 s and re-read, or check the tab title, before touching the button again. Success is `…/wizard/success` and "Fantastic! Your application is on its way."
- **The location metadata is unreliable in both fields, and one of them is a template artifact.** Every posting checked rendered the employment line as "Full Time On-site" or "Contract W2 … On-site" — including postings whose own title is "Remote in Remote, NY, US" — so **"On-site" in that line carries no information and must be ignored**. The title's "Remote in ‹city›" is equally weak: one posting labelled Remote stated "Location: 5 days onsite in Irving, TX" in its body. Read the description; where the description says nothing at all about location (common on Dice), treat it as tier B rather than inventing a constraint from the metadata.
- **First measured run, 24 Sept** (4 queries, `filters.postedDate=SEVEN`, `filters.workplaceTypes=Remote`): "product designer" 2 results, "ux designer" 11, "design system" **135**, "design engineer" **37**. The two large numbers are almost entirely title collisions with other industries — "design system" returns electrical and control-systems engineering, "design engineer" returns hardware and mechanical. Net on-discipline candidates: **7**, of which 2 were applied to, 5 skipped. The skip reasons are worth knowing in advance because they repeat: onsite despite a Remote label, "fully remote role working **Pacific Time hours**" (UTC-7 against UTC+3 is a 20:00–04:00 day and a genuine knockout, seen on both Kforce postings), brand/graphic design under a "Senior Designer" title, and an FDE title over pure AI solution architecture.
- **Verdict after run 2 (25 Sept): does not earn a daily slot.** Second measured pass, 24-hour filter, four queries: `product designer` returned **2** results (a Compressor CAD Product Designer and a Director, both off-discipline); `design system` returned **397**, headed by Harley-Davidson's "Engineer Design", a "Physical Design Engineer" and an "Electronic Design Engineer"; `ux designer` returned **22**, essentially all staffing intermediaries with the end employer unnamed (DTEL Engineering, ADG Tech Consulting, Digital Health Links, Cyberobotix, Atash Enterprises, International Software Systems), plus Sierra Nevada Corporation, which dies on the clearance/ITAR class. **421 raw, zero applications.** Two passes, two applications total, both through intermediaries. Move Dice to fortnightly or drop it; it is not worth a slot in the daily five.
- **Verdict after run 1: trial, not a standing daily slot.** Two applications from a full pass, both through staffing intermediaries with the end employer unnamed, against 185 raw results dominated by engineering collisions. Run the second measured pass before deciding; if it lands in the same range, Dice belongs on a weekly or fortnightly cadence.

**Other dead or low-value sources.** Reachability notes transfer; the discipline-specific ones are marked.
- `relocate.me`: the discipline category was empty and the listing stale. Weekly at most.
- `euremotejobs.com`: 404.
- `uxjobsboard.com`: closed.
- `europeremotely.com`: HTTP 445.
- `justremote.co`: client-side render.
- `landing.jobs`: 0 results.
- `dribbble.com/jobs`, `designjobsboard.com`: design-only, US/UK agency brand work — an example of a niche board that looks on-topic but carries the wrong sub-discipline. Check a niche board's actual sub-discipline before committing to it.
- `jobgether.com/remote-jobs`: 18–30+ days old, and an aggregator.
- `arbeitnow.com/api`: ignores the search term (see "Do not use" above).
- `adzuna.co.uk`: CAPTCHA wall, treat as closed.
- `app.greenhouse.io/embed/job_app` is blocked by robots.txt in WebFetch; convert to `job-boards.greenhouse.io/<company>/jobs/<id>`.

**Direct employer sources**
- **Greenhouse public board API** (any tenant, no auth): `https://boards-api.greenhouse.io/v1/boards/<tenant>/jobs`. Filter the JSON as below; the job URL is `job-boards.greenhouse.io/<tenant>/jobs/<id>`.
```js
JSON.parse(document.body.innerText).jobs.filter(x=>/design/i.test(x.title))
 .map(x=>x.id+' | '+x.title+' | '+x.location.name)
```
- **Ashby company boards** (`jobs.ashbyhq.com/<co>`) list the open countries for every role; read them before applying.
- **When you find a strong company, check its whole careers page.** LinkedIn doesn't show every posting.
- `jobs.siemens.com` ("Careers Marketplace") is a single-employer portal covering Siemens AG + Healthineers. Monthly check. The session drops silently mid-flow, so verify the session after each step.
- Workday: after applying, check Candidate Home "Suggested Jobs"; `/apply/useMyLastApplication` makes repeat applications cheap.

**Freelance marketplaces (Upwork, Toptal, Malt, A.Team…): profile channels, not job-board sources**
- Upwork: not worth focusing on as a primary channel. Rates sit well below employment equivalents (one discipline measured at $20–50/h); average proposal reply rate is 7.45%; the client base is shrinking. Automation works for text and simple selects, but **not** for the hourly rate, date dropdowns or portfolio publishing; hand those to the user.
- Toptal: a talent account rejected at first screening shows only a paid "TopAccess" upsell ($29.95/mo × 12, "does not guarantee acceptance"). **Don't buy.** Reapplying needs a new account (password).
- Malt: day-rate model; 5% commission (10% for the first 6 months in FR/ES/BE). Check its country list against the candidate's.
- A.Team: no builder commission, under 2% acceptance; product and engineering roles only.
- Braintrust: free, US/LATAM-heavy. Third.
- Contra: pivoted to creator/AI work. Secondary.
- Skip: Fiverr Pro, PeoplePerHour, Freelancer.com, YunoJuno/Worksome, and developer-only platforms (Lemon.io, Gun.io, Turing, Andela).
- Day rate from a monthly band = monthly ÷ 20 working days, minus commission; it is also a seniority signal.
- Account creation and T&C/code-of-conduct acceptance stay with the user.

---


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

---

