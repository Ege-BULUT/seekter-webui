# jobs.intodesignsystems.com

- **27 Sept: the board is paginated now** and no longer renders a long flat list. The footer reads "Showing 1–20 of 186" with 10 pages, so `a[href^="/jobs/"]` returns 20 anchors however far you scroll. Page 1 is newest-first and on a daily cadence it covers everything posted in the last three days, which is the whole point of the stop; page 2 onward is material earlier runs already swept. Don't read 20 anchors as "the board shrank".
- **A daily stop can legitimately return nothing.** 28 Sept: page 1 was byte-for-byte the same twenty listings as 27 Sept, newest still 2 days old. That is the board being quiet, not the scrape failing. Compare the first slug against yesterday's before spending calls re-resolving apply URLs.
- About 254–259 roles, no account, no paywall. The main domain `/jobs` returns 404; use the `jobs.` subdomain.
- Each job page has an "Apply on <company>" link to the ATS: fetch `/jobs/<slug>` and take the `a` whose text matches `/apply on/i`.
- 8 Sept bulk extraction script. **The `page=` loop no longer works** now that the board paginates its own way (see the 27 Sept note above); keep it only for the anchor-parsing shape:
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
