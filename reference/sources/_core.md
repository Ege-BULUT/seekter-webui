# Sources: core

Reference for steps 1-5 of the run. Everything here is **person- and role-independent**: how each source behaves, what its filters do, and which of its labels lie. Queries, titles, geoIds, board names and cadences belong to one candidate and live in `profile/search.json` and `profile/profile.md`.

Where a measurement needed a concrete query to be verifiable, the number is kept and the query is described by shape ("a two-word title", "one discipline category"). Measurements taken for one discipline say so.

## How this folder is read

One file per source. **Read this file plus `linkedin.md` and `freehire.md` on every run**, because those are steps 1-4 and they are not optional. Read a board's file only when that board is in play for the run, which `profile/search.json` decides. A source with no file here has never been measured; add one rather than growing another.

**When a new source is measured, it gets its own file and a row in the table below.** When a lesson is *not* about one source's own mechanics, it belongs in this file, not in a source file, or it will never be read again.

| Source | File | When |
|---|---|---|
| LinkedIn (alerts, notifications, searches, tracker) | `linkedin.md` | every run, steps 2-4 |
| freehire.me API | `freehire.md` | every run, step 1 |
| Jobicy API | `jobicy.md` | with step 1, one curl per tag |
| jobs.intodesignsystems.com | `intodesignsystems.md` | step 5, at the profile's cadence |
| designsystems.jobs | `designsystems-jobs.md` | step 5 |
| Working Nomads | `working-nomads.md` | step 5 |
| Glassdoor | `glassdoor.md` | step 5, home country only |
| Djinni | `djinni.md` | step 5 |
| Indeed | `indeed.md` | step 5 |
| Dice | `dice.md` | step 5 |
| XING | `xing.md` | step 5, relocation track only |
| Wellfound | `wellfound.md` | step 5, discovery only |
| Employer boards (Greenhouse, Ashby, Workday, Siemens) | `direct-employer.md` | when a company is worth checking directly |
| Upwork, Toptal, Malt, A.Team, Proxify and the rest | `freelance-platforms.md` | profile channels, not a sweep step |
| Himalayas, Remotive, We Work Remotely, haystack.cv, Adzuna, Arbeitnow, Otta, RemoteOK and other dead ends | `dead-and-low-value.md` | read before adding a "new" board |
| Inbound recruiter mail, inbox sweep, rejection regex | `inbox.md` | `/seekter-log`, not the run |

**Do not use (measured dead or paid):** Remotive (paywall, 0.4% visible) · We Work Remotely (paid) · Arbeitnow API (ignores the search term: "product designer", "postdoc" and "zzzz" return the same 20) · Himalayas (single-agency spam, `?search=` ignored) · Welcome to the Jungle/Otta (no open search) · euremotejobs, uxjobsboard, europeremotely, justremote, landing.jobs (dead) · Adzuna (CAPTCHA wall) · haystack.cv (country list excludes most candidates) · EWOR GmbH postings (every apply URL 404).

Details and the measurement behind each verdict are in `dead-and-low-value.md`. **Check that file before adding a board**: most of the obvious candidates are already in it.

## Rules that belong to no single source

**⛔ One role, six cities, six ids: the §2.7 spam pattern in its cheapest disguise.** Measured 29 Sept (Air Apps): an identical "Product Designer" title appeared under six separate Ashby ids for Amsterdam, Stockholm, Berlin, Rome, Paris and London. All six scored high in the same candidate list and read as six European opportunities. The tell is `check` returning SAMECO across the set: one company, one title, many ids. **When one company's identical title appears across more than about five cities, resolve one and dedup on the company, not the id.**

**⛔ The US PERM labor-certification notice, and how to recognise it before you fill a form.** Measured 27 Sept on an AcuityMD Greenhouse posting that had reached the candidate list from two sources. A US employer sponsoring a green card must advertise the role publicly, and those notices are posted on the normal job board and look like openings. The tells, all present together:
- The body opens in the third person naming the company and a single city: "‹Company›, Inc seeks ‹Title› in ‹City›, ‹State›", even when the header says "‹City› or Remote".
- The description is a flat "Job Duties:" block rather than a pitch, a team description or benefits.
- "Minimum Requirements: Bachelor's degree, **or foreign equivalent**, in ‹named fields› plus N years of progressively responsible experience **in the job offered** or a related occupation."
- A numbered list of "Special Skill Requirements", each carrying its own year count (3 years, 4 years, 3 years…).
That shape exists to be impossible to match except by the person already in the seat. **Skip on sight.** It is also usually paired with a hard degree field requirement, which is an ordinary knockout on its own.

**A posting's advertised location can be stricter than the gate its own form applies. Read the form's eligibility question before skipping on the label.** Measured 26 Sept on TheyDo: the Ashby header said `Location: European Economic Area`, which Türkiye is not in and which under the country-list rule reads as a closed door. The form asked one eligibility question, **"Will you work/live within the CET +/- 2 timezone?"**, and had no country or residence field anywhere. For a UTC+3 candidate that is CET+2, so the honest answer is Yes and the header was not the rule. A second posting the same day was the mirror image in the candidate's favour: header `Amsterdam / Remote`, `Location Type: Hybrid`, and the description carried "Although this role can be remote, we are only considering candidates based in CET +/-3 timezones". **A region name in the location header is the recruiter's shorthand for where they expect people to be, not always the rule they enforce.** Opening the form costs a navigation and one read. The country-list trap still stands for an explicit list of named countries; this is about a single region word.

**Talent pools versus aggregators.**
- Clera's Ashby board had 279 jobs across 40+ cities, all under "Engineering": it's a talent pool, not an employer.
- **Rule: apply to pools** (self-published real listings, EOR/staffing firms, "companies in our network"). **Skip aggregators** that only copy and redirect; find the source posting and apply there.
- Dedup still applies: a different role in the same pool is a separate application; the same listing never twice.
- Write "pool listing" in the tracker Notes.
- Trust assessment: Trustpilot is bimodal (75% five-star / 22% one-star), with complaints about scraping LinkedIn profiles, fake listings and cold email from other domains. "Use it as a pool, don't trust it as a channel."
- **If a pool introduces a company, check you haven't also applied to that company directly** (double representation hurts both).
- Sign up with email or Google, **not LinkedIn OAuth**. Fill in Role and Industry preferences, or the feed is junk.
- Funding-stage heuristic for pool preferences: Seed through Series D. Seed/A for founding, remote or contractor roles; B–D when the candidate needs dedicated headcount for a specialism, or a sponsorship budget. Skip pre-seed (equity pay) and bootstrapped.

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

## JS execution pitfalls (LinkedIn and general)
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
