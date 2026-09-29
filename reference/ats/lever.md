# Lever

- **URLs:** `jobs.lever.co/<company>/<id>`, `jobs.eu.lever.co/...`; form = append `/apply`.
- **Set values:** Upload CV first, **wait 8–13 s for the parse** (earlier writes nest values). Then fix Full name (parser reorders it); keep parsed email if it equals `<EMAIL>`. Real `<select>`s: `form_input`.
- **Radios:** ref clicks don't register (submit fails silently) → coordinate click, verify by screenshot.
- **Location:** "Current location" is a real autocomplete; typed text alone is not saved (`input[name=location]`), `form_input` fails. `triple_click` → type city → 3 s → pick "`<CITY>`, TUR". If pre-filled, don't type over (merges). It can empty itself — recheck right before submit.
- **File upload:** make the hidden input visible **in place** — do NOT `document.body.appendChild` it (it leaves the form):
  ```js
  f.style.cssText='opacity:1;width:260px;height:34px;display:block;visibility:visible;position:relative;z-index:9999';
  ```
- **URLs:** `jobs.lever.co/<company>/<uuid>`, form = append `/apply`. Fields are named, not id'd: `name`, `email`, `phone`, `location`, `org`, `urls[LinkedIn]`, `urls[Portfolio]`, and custom questions as `cards[<uuid>][field0]`, `[field1]`…
- **Read the questions before filling:** `[...document.querySelectorAll('.application-question')].map(e=>e.innerText)`. The custom cards sit at the end, and that is where the knockouts live.
- ⛔ **The US payroll-state checklist is a knockout class of its own.** Measured 27 Sept (HighLevel): posting said "United States / Remote" with no country list in the text, and the last required question was **"‹Company› is registered to payroll employees in the following states. Do you currently live in any of these states?"** followed by 18 state names and **no "none of these" option**. A candidate outside the US has nothing truthful to select, so the form cannot be submitted. This is not the same as a sponsorship question and no sponsorship answer rescues it; a company can only employ where it has registered payroll. Check the last `.application-question` blocks on any US remote posting before typing anything.
- **Native setter works** on every text field and textarea; use `[name="..."]` selectors.
- **Yes/No custom questions are checkboxes, not radios**, sharing one `name`. A JS `.click()` on the input does nothing useful; click the wrapping `label` instead, then verify `.checked` on both.
- **The file input is `input[type=file][name=resume]` and is hidden.** `find` returns nothing for it even after making it visible; use `read_page` with `filter: interactive` and take the `type="file"` ref.
- Demographic blocks (ethnicity, gender, age range, veteran) are separate `surveysResponses[...]` checkboxes and are optional. Leave them.
- **Traps:** Some tenants (e.g. FARFETCH, Deliverect) return "Page script returned empty result" for `find`/`read_page`/`form_input`/`file_upload` — no fix; fill via JS setter, human attaches CV.
- **Submit:** scroll-back to form = empty required field. No network request on submit / `form.submit()` → "There was an error verifying your application" = bot layer → hand over.
