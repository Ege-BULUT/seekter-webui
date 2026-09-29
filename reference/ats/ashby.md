# Ashby

- **URLs:** `jobs.ashbyhq.com/<company>/<uuid>`; form = append `/application` (loads 8–10 s; "Fetching application form" → wait, re-read). Board `jobs.ashbyhq.com/<co>` lists allowed countries per role — check first.
- **Core problem:** DOM value and React state diverge unpredictably → "Missing entry for required field: X" on fields that look filled.
- **Set values (text/textarea) — default:**
  1. Setter only as a pre-fill; never trust it.
  2. Commit each field: `focus()+select()` → real `Delete` → real `computer type`:
     ```js
     var e=document.querySelector('input[type=email]'); e.focus(); e.select();
     // then real typing with computer type — it overwrites the selected text
     ```
  3. Or after the setter, caret to end + one real space (fires onChange with full value):
     ```js
     var e=document.getElementById(ID); e.focus(); e.setSelectionRange(e.value.length,e.value.length);
     // then computer.type(" ")
     ```
     Throws `InvalidStateError` on `input[type=email]` → try/catch; for email use step 2 or real click + space + `BackSpace`.
  4. ASCII-swallowing field (`_systemfield_name` keeps only Turkish letters): `find` → `form_input`+ref. Verify `value`.
  - Don't: `ctrl+a`+`Delete` (appends), `triple_click`+type, `End`+`Backspace`×60 (layout shift), ref-click+type (types nothing). **Never click into a long textarea and type** — caret lands mid-text (`ctrl+End` doesn't help); use `setSelectionRange`.
  - Number inputs with residue like `4e-`: `End` + `BackSpace` per char + digits.
- **Yes/No buttons:** these are `button[data-option=yes|no]` carrying `aria-pressed`, not radios. **Use a `computer left_click` with a `ref` from `find`.** Measured 24 Sept (Motorway): a coordinate click at the measured centre did nothing and the JS `MouseEvent` dispatch below also left `aria-pressed="false"`; one ref-click set it to `true` immediately. Verify with:
  ```js
  [...document.querySelectorAll('button[data-option]')].map(b=>b.getAttribute('data-option')+'='+b.getAttribute('aria-pressed')).join(' | ')
  ```
  **Do not give the button an `id` to make it easier to find.** Writing an `id` onto it re-renders the component and drops the handler, after which nothing works, including the ref-click that worked a moment earlier (measured 24 Sept, Healf). Use `find` on the question text instead ("No option button under the question Do you have the right to work in the UK"), and re-run `find` after every failed attempt because refs go stale on each re-render.
  The older JS dispatch still works on some tenants; try the ref-click first:
  ```js
  var b=[...document.querySelectorAll('button')].filter(e=>e.offsetParent&&/^Yes$/.test(e.innerText.trim()))[0];
  ['mousedown','mouseup','click'].forEach(t=>b.dispatchEvent(new MouseEvent(t,{bubbles:true,cancelable:true,view:window})));
  ```
  Verify `aria-pressed` (older tenants: `aria-checked`) → `"true"` (visually: filled dark = selected, outline = focus only).
- **Date fields are a calendar, not a text input.** A question like "When can you start a new role?" renders as `input` with placeholder `Pick date...`; typing into it does nothing. Ref-click it, wait 3 s, then click the day cell. Today's cell carries the class `…datepicker__day--today`, so locate it rather than counting grid positions:
  ```js
  [...document.querySelectorAll('div')].filter(e=>/datepicker__day--today/.test((e.className||'').toString()))[0]
  ```
  The field then reads `MM/DD/YYYY`.
- **Radios:** `label[for=...]` click, verify. Reset at submit on long forms → real coordinate click on the circle itself.
- **Dropdowns / comboboxes:** click → type → 3 s → `Return` (Return works in Ashby).
  - **Location** = `input[role=combobox]` (not `input[type=text]`); won't open via ref → coordinate click. Usually searches COUNTRY: "Turkey" → "Türkiye" ("Istanbul" → "No results"); some tenants list "Istanbul, Türkiye" — try the city if the country fails.
- **`Email` is the field that most often fails to commit.** Across five Ashby tenants on 24 Sept it was named in the "Missing entry" list four times, more than any other field. `select()` throws `InvalidStateError` on `input[type=email]`, so commit it with a real click, `End`, a typed space and `BackSpace`. `_systemfield_name` is the second most common and is the ASCII-swallowing field, so commit that one with `find` + `form_input` on the ref.
- **Use the first submit as the diagnostic, not as a failure.** The native setter commits on some fields and not others *within the same form*, with no visible difference between them. Measured 24 Sept (Harvey): one setter pass filled nine fields; the submit accepted Legal Name, Employer, University and Pronouns and returned "Missing entry for required field" for exactly Preferred First Name, Preferred Last Name, Email and Phone Number. So: setter-fill everything, submit once, read the error list, commit **only the named fields** with real typing, submit again. That is one cheap round trip instead of hand-committing every field. Ashby keeps everything else — radios, Yes/No buttons, the combobox and the uploaded CV all survived the failed submit and the re-render.
- **`aria-pressed="true"` plus a dark background is still not proof the answer reached React state.** Measured 26 Sept (Tradeify): four Yes/No groups were set with coordinate clicks in one batch, all four read `aria-pressed="true"` with the filled background colour, and the submit accepted three of them and returned "Missing entry for required field" for the fourth. Re-reading the attribute after the failed submit still said `true`. Clicking the same button again would only have toggled it off. **The fix is to click the OPPOSITE option, verify it flips, then click the intended one.** That forces a real state transition through the component instead of asking it to confirm a state it never had. Do this only for a button the submit has actually named; a button that submit accepted is fine as it is.
- **Give a `button[data-option]` two seconds before you believe the verification.** The `aria-pressed` read straight after the click can still say `false` while the click actually landed; re-reading a moment later shows `true`, and the element also carries an `_active_` class and a dark `backgroundColor`. Measured 24 Sept (Harvey): a ref-click and then a JS dispatch both reported `no=false`, and the button had in fact been set the whole time — a third attempt would have toggled it back off. Check `aria-pressed`, the `_active_` class and the computed background together before retrying.
  **Which click works is per-tenant, so try both and verify between them.** On Harvey the ref-click set it; on Reevo the same hour, two ref-clicks left it unset and a **coordinate click on the button in a fresh screenshot** set it immediately. Refs also go stale on any re-render — uploading the CV re-rendered the Reevo form and invalidated the ref found before it — so re-run `find` after every upload or failed submit, and if a second ref-click still does nothing, screenshot and click the coordinate instead of repeating.
- **The `required` attribute lies.** Ashby renders required radio groups with `required=false` on the inputs, so a pre-submit "are all required fields filled" check passes and the submit then fails on them. Measured 22 Sept on a BeReal form: two expertise groups reported optional, both were required. Trust the asterisk in the label text, not the DOM flag. A `role=combobox` location field has the same problem: it carries no `required` and no value the check can see.
- **A radio set by `label.click()` shows `checked=true` but does not reach React state.** It fails submit with "Missing entry for required field" and keeps failing however many times you re-click it in JS. A real `computer` coordinate click on the circle fixes it in one go. Re-measure the coordinate after each failed submit: the error banner shifts the page.
- Required follow-ups to a "No" answer must still be filled ("None, I have not worked in …").
- **Ashby has the two-dropzone trap too, not just SmartRecruiters.** Every tenant measured on 26 Sept rendered an "Autofill from resume" dropzone above the form and the required `Resume` field inside it, both `input[type=file]`, and the top one only runs the parse. `find` tells them apart reliably ("Resume file upload input" returns the labelled one first and describes the other as the autofill dropzone), so read the description rather than taking the first ref.
- **Check the EEO self-ID radios before every submit; they can end up answered without being clicked.** Measured 26 Sept (Chromatic): a pre-submit count found five checked radios where only two had been set, and the extra three were Gender `Male`, Race `White (Not Hispanic or Latino)` and `I am not a protected veteran`. Whether Ashby prefilled them from the CV parse or a coordinate click aimed at a location suggestion landed in an open race list is unresolved, and it does not matter: they were truthful values that the standing rule says to leave alone. Count `input[type=radio]:checked` against the number you actually set, and if a demographic group is answered, switch it to the group's own `Decline to self-identify` option. A radio cannot be un-answered, so decline is the way back to blank:
  ```js
  [...document.querySelectorAll('input[type=radio]')].filter(r=>{var l=document.querySelector('label[for="'+r.id+'"]');return l&&/decline|prefer not/i.test(l.innerText)}).map(r=>r.id)
  ```
- **File upload:** `find` → `file_upload` (presigned S3). Page-side CV fetch is CSP-blocked.
- **Traps:**
  - Limit: max 3 applications per company per 60 days; same role not within 180 days ("You have reached your application limit for this job").
  - Hidden honeypot instructions (see Universal). Duplicated question blocks whose error never clears → hand over.
- **Submit:**
  1. Click Submit; the first click may only commit blur — click again.
  2. Search page text for `Missing entry for required field`. **It fires on fields that already hold the right value**, `_systemfield_email` most often: submit reported "Missing entry for required field: Email" while `.value` read the address back correctly (24 Sept, Healf), because `form_input` had set the DOM without reaching React. Fix with `focus()` → real `Delete` → real `computer type` of the same string, then resubmit. Not cumulative — fix named fields with step 2 above, resubmit; three rounds is normal.
  3. Still dropping: click the field, `End`, type one character, `BackSpace`, `Tab`.
