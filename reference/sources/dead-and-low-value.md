# Dead and low-value boards

**Himalayas**
- Useful for **verification**: its "eligibility" line shows country eligibility inline.
- `https://himalayas.app/jobs/countries/<country>/<discipline>` was readable via WebFetch.
- 12 Sept onward: not usable by fetch. `/jobs/design` matches company names containing "design", `?search=` is ignored, and `/jobs/categories/design` is a 404.
- 17 Sept: the list doesn't render. 18 Sept: flooded with one agency's copies; almost everything single-country. Low value.

**Remotive**: the API is blocked by robots.txt. The site is a half-to-full paywall ("You're seeing 0.4% of available roles / Unlock 120,000+ jobs"), with company names hidden. **Don't enter.**

**We Work Remotely**: **paid** ($2.95 first month, then $14.95/mo on a 12-month commitment). Don't subscribe. Its "Anywhere in the World" region label proved false twice ("Poland only"; "Remote (US)"). `remoteineurope.com` 302-redirects to WWR.

**haystack.cv**: "Where are you based?" is mandatory and offered only UK/DE/FR/CA/US. It is structurally unusable for a candidate based elsewhere; picking one would be a false residence claim. Don't chase `haystack.cv/apply/...` jobs; find the company directly or skip ("platform doesn't support the candidate's country").

**Other dead or low-value sources.** Reachability notes transfer; the discipline-specific ones are marked.
- `relocate.me`: the discipline category was empty and the listing stale. Weekly at most.
- `euremotejobs.com`: 404.
- `uxjobsboard.com`: closed.
- `europeremotely.com`: HTTP 445.
- `justremote.co`: client-side render.
- `landing.jobs`: 0 results.
- `dribbble.com/jobs`, `designjobsboard.com`: design-only, US/UK agency brand work — an example of a niche board that looks on-topic but carries the wrong sub-discipline. Check a niche board's actual sub-discipline before committing to it.
- `jobgether.com/remote-jobs`: 18–30+ days old, and an aggregator.
- `arbeitnow.com/api`: ignores the search term. "product designer", "postdoc" and "zzzz" all return the same 20 records.
- `adzuna.co.uk`: CAPTCHA wall, treat as closed.
- `app.greenhouse.io/embed/job_app` is blocked by robots.txt in WebFetch; convert to `job-boards.greenhouse.io/<company>/jobs/<id>`.
