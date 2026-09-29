# Direct employer sources

- **Greenhouse public board API** (any tenant, no auth): `https://boards-api.greenhouse.io/v1/boards/<tenant>/jobs`. Filter the JSON as below; the job URL is `job-boards.greenhouse.io/<tenant>/jobs/<id>`.
```js
JSON.parse(document.body.innerText).jobs.filter(x=>/design/i.test(x.title))
 .map(x=>x.id+' | '+x.title+' | '+x.location.name)
```
- **Ashby company boards** (`jobs.ashbyhq.com/<co>`) list the open countries for every role; read them before applying.
- **When you find a strong company, check its whole careers page.** LinkedIn doesn't show every posting.
- `jobs.siemens.com` ("Careers Marketplace") is a single-employer portal covering Siemens AG + Healthineers. Monthly check. The session drops silently mid-flow, so verify the session after each step.
- Workday: after applying, check Candidate Home "Suggested Jobs"; `/apply/useMyLastApplication` makes repeat applications cheap.
