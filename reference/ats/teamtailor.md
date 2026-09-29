# Teamtailor

- **URLs:** company careers domain; form `/c/new` or `/applications/new`; success `/applied`; `/applications/email_verification_needed` = human must click the email link.
- **Set values:** native setter works on all text fields. Names: `candidate[first_name]`, `candidate[last_name]`, `candidate[email]`, `candidate[phone]`, `candidate[job_applications_attributes][0][cover_letter]`, custom `candidate[answers_attributes][N][text|number]`, locations `candidate[location_ids][]`, file `#candidate_resume_remote_url`. `range` sliders take the setter.
- **Radios/checkboxes:** click `labels[0]`, not the input. Bulk:
  ```js
  var picks=['content-20-3','multiContent-21-0','flag-24-0'];
  picks.forEach(function(s){var e=document.querySelector('[id$="'+s+'"]');
   var lab=e.labels&&e.labels[0];(lab||e).click();});
  ```
- **Consent:** `candidate_consent_given` is mandatory (missing → silent failure, page looks refreshed); `candidate_consent_given_future_jobs` also appears. Inputs are 0×0; two share `candidate[consent_given]` (one hidden) → filter by visibility. Ref via `find` → `scroll_to` → coordinate click on the visible box; JS `checked` right after can be stale — verify by screenshot.
- **Traps:**
  - Bottom-modal form has its own scroller: set `scrollTop` on the nearest `overflow-y: auto|scroll` ancestor.
  - Reject cookies first. Form non-interactive after the banner (`document.activeElement` = `SECTION`) → clean tab, else hand over.
  - "Job details"/"Apply" tabs: a ref-clicked Send can bounce to Job details (values survive). Close banner → click "Apply" tab by coordinate (`/c/new`) → `End` → Send by coordinate.
  - Location lists may lack the home country → truthful region if present (e.g. "Europe") + state location in free text.
  - Knockout radios close the form — read before calling a match.
- **Phone country picker carries the Turkish-spelling trap**, the same one Recruitee has: typing the English name jumps to neighbours ("Turk" → Turks & Caicos, Tuvalu, Uganda) because the row reads **Türkiye** with an umlaut and sorts just above them. The list is virtualized, so a DOM text search for it returns nothing until it is scrolled into view. Scroll the open dropdown up ~2 ticks, confirm by zoom, click by coordinate. Selecting it pre-fills the dial code; put the caret at the end and type `<PHONE_LOCAL>`, which the widget then renders in spaced national format.
- **File upload:** `find` → `file_upload` (S3 presigned via `/uploads/presigned_data`).
- **Submit:** Success = `/applied`, "All done! Your application has been successfully submitted!". Form reappearing empty, "Content missing", or a 503 may still mean success → reload `/applications/new`; "You already applied for this job" confirms. Never submit three times.

## The apply modal, measured 23 Sept (Leadtech)

- The apply modal can **open scrolled past a Personal information block** (first name, last name,
  email, phone) that sits above the screening questions. Nothing hints at it: the questions fill
  fine, and submit then closes the modal and returns to the job description with **no request made
  and no visible error**, which reads exactly like a silent failure. Scroll the modal to the top and
  to the bottom before concluding anything, and re-open it: Teamtailor **keeps every answer**.
- `candidate_phone` wants the **national number** (`<PHONE_LOCAL>`), not E.164. The country code is a
  separate selector, and an E.164 value leaves the field outlined red with "Name or email is required"
  shown instead of a phone error.
- Consent checkboxes can be duplicated: two identical 24-month talent-pool consents, one whose label
  starts with "Required." and one without. Tick the first, leave the second.
- **The consent checkbox does not accept a JS label click.** `label.click()` sets `.checked` to true and
  reports success, and the form still refuses with the consent error. Click it by coordinate and confirm
  with a zoom, the same rule Recruitee already has.
- **A post-submit re-render can look exactly like a validation failure**: the form comes back empty with
  a red required-consent message. Before refilling, reload the posting and look for "You already applied
  for this job", which is Teamtailor's own applied marker.
