# Pinpoint

- **URLs:** `<company>.pinpointhq.com/en/postings/<uuid>`; form `.../postings/<id>/applications/new`.
- **Set values:** plain ids (`application_form_application_first_name` …), native setter works. Phone flag defaults to the posting's country → type `<PHONE_E164>` and it corrects. Address line is mandatory (`<ADDRESS_LINE>`, `<CITY>`, `<POSTCODE>`).
- **File upload:** hidden `input[type=file][name="application_form[application][cv]"]` → make visible → `find` → `file_upload`. Input disappears after upload — normal.
- **Submit:** mandatory "(Required) Allow us to process your personal information". It is a "pretty checkbox": the real `input` is 0x0 and its `.checked` stays **false** even once the box is visibly ticked, so the DOM flag is useless. Click the visible `.pretty` container by coordinate and **verify with a zoom**, not with JS. A failed submit re-renders the form and clears it, so re-tick before every retry.
- **Salary answers are number-only** even though the field is `type=text` with no pattern. "GBP 50,000 to 62,000 per year" failed with "Text based answers to questions does not match required format"; a bare `62000` passed. The other text answers survive the failed submit, so only the number needs fixing.

## The silent submit, measured 24 Sept (Group O)

- **URLs:** `/en/postings/<uuid>`; the form is at `/applications/new`, reached by an "Apply Now" link. The posting page renders first and the form mounts late: right after the click the page reports only two checkboxes, and the real fields (about 43 of them) appear several seconds later. Wait and re-read before deciding the form is broken.
- **The submit can fail completely silently: no navigation, no error text, and no network request at all.** A wrapped `fetch`/XHR capture stays empty, because HTML5 validation blocks the submit before anything is sent. Do not retry the click. Ask the form instead:
  ```js
  const f=document.querySelector('form');
  [...document.querySelectorAll('input,select,textarea')]
    .filter(e=>e.willValidate&&!e.checkValidity())
    .map(e=>(e.id||e.name)+' | '+e.validationMessage);
  ```
  Measured 24 Sept (Group O): this named the blocker instantly as a required "Allow us to process your personal information" consent that no error message ever mentioned. A scan for empty `required` fields found nothing, because the blocker was an unticked checkbox.
- **Phone is `intl-tel-input` and defaults to the US flag.** Unlike the Dice settings field it is not locked: typing the full `+90…` switches the flag to "Turkey (Türkiye): +90" and keeps every digit. Type E.164 and verify the flag's `title`.
- Country is a plain `<select>` whose option text is **"Türkiye"**. Address is split into Address Line 1 / Town / Postcode, all free text, so a non-US address goes in unchanged. The "Find Address" geocoder above them can be left alone.
- Equality-monitoring selects (gender, ethnicity, age bracket, disability) are optional and carry a "Prefer Not To Say" option; leave them blank.
