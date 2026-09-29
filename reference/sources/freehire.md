# freehire.me

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
