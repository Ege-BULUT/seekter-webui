# Glassdoor

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

**One-line verdict for the report card in `_core.md`:** home country only, one broad discipline keyword + the home `IN<id>`.
