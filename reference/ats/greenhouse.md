# Greenhouse

- **The phone must be typed for real; a native setter fills the display and nothing else.** Measured 25 Sept (Parloa, `job-boards.eu.greenhouse.io`): setting `#phone` with the native setter rendered the number correctly formatted, with the right country flag already selected, and the submit still failed with **"Phone is required."** plus **"Select a country"** under `#country`. `#country` stayed empty the whole time. Fix: click the phone field, `cmd+a`, `BackSpace`, then `computer type` the national number. The flag and dial code are picked up from the existing selection, `#country` stays visibly empty, and the next submit passes. Don't chase the country dropdown; it isn't the blocker.
- **Greenhouse error text is stale between submits.** The "Phone is required." / "Select a country" labels stay painted after the field is fixed and only clear on the next submit, so a post-fix error scan will report a blocker that no longer exists. Submit again and read the result rather than trusting the banner.
- **Select-type questions are comboboxes with no `<select>` and no readable `.value`.** `document.getElementById('question_<id>').value` returns `''` whether the question is answered or not. Drive them by coordinate: screenshot, click the row, screenshot the open list, click the option, and verify from the screenshot. `aria-controls` is null, so there's no listbox to query.
- **`#country` can be the blocker after all, and it is a react-select, not the flag picker.** The line below says not to chase it. Measured 26 Sept (OpenTable) that is wrong on some tenants: the phone was typed for real, the number and the flag both rendered, and every submit still returned **"Country\*" / "Select a country"** with nothing else outstanding. `#country` is `input.select__input` inside its own control between Email and Phone, and its options read "United States +1", "Turkey +90". The `Select country` button that `find` returns next to the phone field is a different widget and does not satisfy it. Click the control by coordinate, confirm `document.activeElement.id === 'country'`, then pick the option with the usual `mousedown`/`mouseup`/`click` dispatch; the control afterwards reads just `+90`. So: type the phone for real **and**, if the error survives, fill `#country` itself. **Seen twice:** RTB House on `job-boards.eu.greenhouse.io` did the same on 27 Sept, every field answered and the submit returning only "Country\*" / "Select a country". Treat filling `#country` as part of the standard Greenhouse pass, not as something to try after a failed submit.
- ⛔ **And the reverse, which is worse: a question that reads exactly like an essay prompt can be a react-select with four canned options.** Measured 28 Sept (Workwize). Three questions ran two or three sentences of scenario and ended in "What do you do?", "What do you design first?" — the shape of a long-answer field in every ATS. All three were `input.select__input`. Long answers were written into all three with the native setter, each read back the correct `value.length`, and each had silently landed in the **select's search box**, which submits as nothing. The give-away in the rendered page was a small "Please choose one answer" hint under the row, easy to miss, and the give-away in the DOM is the class. **So the rule is symmetric: never write into a `question_*` field, long or short, without reading `e.className` first.** `input input__single-line` is free text, `select__input` is a react-select. One line:
  ```js
  [...document.querySelectorAll('[id^=question_]')].map(e=>e.id.slice(-6)+':'+(/select__input/.test(e.className)?'SELECT':e.tagName)).join(' ')
  ```
  Clear a mis-filled one with the setter and an empty string before opening the menu, or the typed text filters the options away.
- **A `question_*` field that looks like a dropdown can be a plain text input.** Same form, same day: `question_37924546002` ("Will you now or in the future require sponsorship for employment?") answered nothing to a ref click, a coordinate click, typed filtering, or `Down`, because it was never a combobox. `e.className` read `input input__single-line` while the real comboboxes on the page read `select__input`. **Check `className` before spending calls hunting for a menu that does not exist**, and note that this turns a Yes/No-looking question into free text, which is a better answer anyway.
- **`#country` is the phone dial code, not a country field.** On the current form it sits between Email and Phone and its options read "Turkey +90". There is no separate country-of-residence field, so don't go hunting for one, and don't read a filled `#country` as a residence answer.
- **A hidden question can also name the wrong company, and it is the parent group leaking through.** Measured 26 Sept on OpenTable and again 29 Sept on KAYAK, both Booking Holdings brands. Both ask **"Are you a current or former employee of Deloitte?"** (OpenTable also "Are you a family member ... of a CURRENT employee of Deloitte?"), alongside a checklist of the group's own sister brands: Agoda, booking.com, FareHarbor, Getaroom, KAYAK, OpenTable, Priceline. On OpenTable the whole set stayed hidden until the first submit. It is boilerplate the group applies to every brand, not a sign the posting is fake or that you are on the wrong form. Answer it as asked and move on.
- **Required questions can stay hidden until the first failed submit.** Measured 24 Sept (Carrot): the form showed nine questions, submit returned one validation error, and **five more required questions appeared with it**, including two domain screeners and an acknowledgment. Never read a Greenhouse form's visible length as its real length; budget for a second pass after the first submit.
- **`Location (City)` is a geocoder, not a text field.** Typing "Istanbul" leaves it looking filled and fails with "Please enter your location". Click it, type, wait, and pick the suggestion ("Istanbul, Turkey"). Its `.value` reads empty afterwards even when set, so confirm by screenshot.
- **The Yes/No question widgets are react-select, and `.value` always reads empty**, filled or not. Confirm every one by zoom before submitting. Typing into the wrong one silently clears whatever was selected there, so click the field, verify `document.activeElement.id`, and only then type.
- **A "voluntary" demographic block can still be hard-required.** Measured 23 Sept (Moniepoint): the section says "Your responses are voluntary and will not impact your application in any way", yet the gender question and the demographic-data consent checkbox both validate as required, and submit fails with "This field is required." / "Please accept the terms to proceed." Clearing the survey answer, the usual escape, does not work. Decide from the profile: if it supplies the value and the consent is a precondition of applying rather than an optional extra, answer and tick, and say so in the tracker notes. If the profile withholds the value, it is a hand-off.
- **Tenant hunting:** if a company site only carries `gh_jid`, probe `boards-api.greenhouse.io/v1/boards/<guess>/jobs/<id>` for 200 (Plata = `platacard`).
- **A tenant can make the ordinary board URL redirect, not 404.** Measured 29 Sept (N26): both `n26.com/.../careers/positions/<id>` and `job-boards.greenhouse.io/n26/jobs/<id>` land on the company's own marketing page with no form on it, so it reads like the posting has no Greenhouse behind it. It does. The embed URL is the only way in and it works first time. **Try the embed before concluding a company site is not Greenhouse**, whenever the page carries a `gh_jid`.
- **URLs:** Iframe on a company site → open the embed directly: `https://job-boards.greenhouse.io/embed/job_app?for=<company>&token=<id>` (EU: `https://job-boards.eu.greenhouse.io/embed/job_app?for=<x>&token=<y>`). The iframe `src` is lazy: scroll, wait 5 s, read `for=`/`token=`. Use the embed URL even if `/<company>/jobs/<id>` 404s. `app.greenhouse.io/embed/job_app` is robots-blocked for WebFetch → browser or rewrite to `job-boards`.
- **Board API (no auth):** `https://boards-api.greenhouse.io/v1/boards/<tenant>/jobs`
  ```js
  JSON.parse(document.body.innerText).jobs.filter(x=>/design/i.test(x.title))
   .map(x=>x.id+' | '+x.title+' | '+x.location.name)
  ```
  School lookup API: `boards.greenhouse.io/v1/boards/<tenant>/education/schools?term=...`
- **Set values:** Text fields have stable ids; native setter works. Helper set:
  ```js
  window.RSET=function(id,v){var e=document.getElementById(id);if(!e)return 'no:'+id;
   var p=Object.getPrototypeOf(e);var d=Object.getOwnPropertyDescriptor(p,'value');
   d.set.call(e,v);e.dispatchEvent(new Event('input',{bubbles:true}));
   e.dispatchEvent(new Event('change',{bubbles:true}));return e.value;};
  window.OPEN=function(id){var e=document.getElementById(id);e.scrollIntoView({block:'center'});
   e.focus();['mousedown','mouseup','click'].forEach(function(t){
     e.dispatchEvent(new MouseEvent(t,{bubbles:true,cancelable:true,view:window}));});return 'op';};
  window.OPTS=function(){return [...document.querySelectorAll('[class*=select__option],[role=option]')]
   .filter(function(e){return e.getBoundingClientRect().height>0;})
   .map(function(e){return e.innerText.trim();});};
  window.PICKOPT=function(txt){var o=[...document.querySelectorAll('[class*=select__option],[role=option]')]
   .filter(function(e){return e.getBoundingClientRect().height>0&&
     e.innerText.trim().toLowerCase().indexOf(txt.toLowerCase())===0;});
   if(!o.length)return 'nf';var e=o[0];
   ['mousedown','mouseup','click'].forEach(function(t){
     e.dispatchEvent(new MouseEvent(t,{bubbles:true,cancelable:true,view:window}));});return 'ok';};
  ```
  If real typing swallows ASCII on a tenant, use `RSET` or `form_input`+ref; verify `value`.
- **Dropdowns (react-select, not `<select>`):**
  - `OPEN(id)` → 2 s → `OPTS()` → `PICKOPT('...')` → verify. Unresolved: synthetic open works on some forms only; if `OPTS()` is empty, open with `find`+ref click or coordinate click, then `PICKOPT`.
  - `PICKOPT` is prefix match, breaks on apostrophes: `PICKOPT("Bachelor's Degree")` → `nf`, `PICKOPT('Bachelor')` → `ok`. `innerText` collapses double spaces → substring match with `\s+` normalised, never `===`.
  - Plain `.click()` on options is swallowed; use the `mousedown`/`mouseup`/`click` sequence:
    ```js
    ['mousedown','mouseup','click'].forEach(function(t){
      el.dispatchEvent(new MouseEvent(t,{bubbles:true,cancelable:true,view:window}));});
    ```
  - Yes/No lists, fastest: `document.getElementById('question_XXXX').focus();` → `computer type "No"` (list filters to one) → `Return`. Don't use `ArrowDown`+`Enter` without filtering — option 0 is pre-focused, so it picks the SECOND option.
  - Verify every pick via `[class*=singleValue]` / `[class*="select__single-value"]` `innerText` (`input.value` is empty).
  - Never native-set a react-select input (text lands in search → "No options"); clear with `RSET(id,'')` first.
  - A coordinate click elsewhere while a menu is open selects the hovered option → `Escape` first.
  - Visible options only (hidden phone-country list is in the DOM):
    ```js
    [...document.querySelectorAll('[role=option]')].filter(e=>e.getBoundingClientRect().width>0)
    ```
    ```js
    [...document.querySelectorAll('[role=option]')].filter(e=>e.offsetParent).map(e=>e.innerText)
    ```
    `document.querySelector('[class*="menu"]')` grabs the phone list first; filter `.filter(m => !/iti__/.test(m.className))`.
  - `form_input` can't do comboboxes. Fallback: click → type → 2 s → `Return`, new screenshot.
  - **Multi-select:** one pick per JS call (only the last sticks otherwise). Per item: `computer.left_click` on the arrow, then a separate `javascript_exec` dispatching the event sequence on the option; pair them in `browser_batch`. Verify by deduping `[class*="multi-value"]`.
  - **Education** `school--0`, `degree--0`, `discipline--0`: typing over existing text prepends at a jumping cursor → `window.RSET('school--0','')` first, then real keyboard. School search needs a distinctive word of the official name, not the colloquial/city name — try variants.
- **Field ids:** `question_XXXX` order is misleading — confirm with `label[for="<id>"]` before writing.
- **Phone (intl-tel-input), resists JS.** "Country" is the dial-code selector (e.g. `Turkey +90`), not residence; the real one is "Location (City)". JS on `country`/`phone` fails ("Phone is required"). Only route:
  1. empty `phone`
  2. real coordinate click on the flag/arrow (~x+25 right of the Country box); or click Country, type `Turk`
  3. real click on the **<HOME_COUNTRY> +<code>** row
  4. real keyboard `<PHONE_LOCAL>`, no country code (field auto-formats)
  Stale "Phone is required." may remain; second Submit goes through. Two "<HOME_COUNTRY>" refs: the one with the dial code is the phone widget.
- **Location (City):** click → type city → 3 s → click the "`<CITY>`, <HOME_COUNTRY>" suggestion by coordinate.
- **File upload:** **CV LAST**, then submit immediately — later re-renders drop it ("Resume/CV is required"). `find` → `file_upload`; the input then vanishes and the filename shows (normal).
- **Scrolling:** window scroll often stuck at `scrollY=0`. Hide the job description:
  ```js
  const jp=document.querySelector('.job-post-container');
  [...jp.children].forEach(c=>{if(!c.classList.contains('application--container'))c.style.display='none';});
  ```
  Still long — hide filled fields:
  ```js
  const w=[...document.querySelectorAll('.application--questions > *')];
  w.slice(0,11).forEach(e=>e.style.display='none');
  ```
  Or use `computer scroll`. `scrollIntoView` on a specific element usually works.
- **Traps:**
  - **Optional D&I survey → mandatory consent.** Any demographic answer makes the "I consent to <Company> collecting… demographic data" box required; submit fails with "You answered some demographic questions. Please accept the terms to proceed, or clear your responses." Don't tick — clear each answer via its **×** (coordinate click; `Escape` the menu that opens) until all read "Select...".
  - Company forms built on Greenhouse (e.g. Miro) may have server-side char limits with no counter (900) and strict phone format: the field's own placeholder shows the shape it wants, which is E.164 with no spaces and no punctuation, so send `<PHONE_E164>`.
  - "How did you hear" with only company channels, no "other" → hand over.
  - `find` may return options unnamed — list texts via JS first.
- **Submit:** if only stale phone errors remain, submit again. Confirm the thank-you page.

`okta.com/company/careers/<slug>` is not a Greenhouse board: it is Drupal hosting the Greenhouse questions, so the field ids are `edit-*` and `edit-question-<id>` rather than Greenhouse's own. Plain `<select>` elements with option values `1`/`0` for Yes/No, so the native setter plus a `change` event works; no react-select anywhere.

- **The uploaded filename gets `_N` appended, and it is not a sign that anything is wrong.** Files land in `okta.com/system/files/jobs_document/` and Drupal appends `_0`, `_1`, `_2`… whenever that filename already exists in the folder, which it does as soon as you upload the same CV twice. The stored document is unchanged; opening the served URL renders the real PDF. Say so plainly if the candidate asks, because it looks alarming.
- **The file upload is an AJAX round-trip that re-posts and re-validates the whole form.** Values set with the native setter survive it, verified field by field.
- **"1 error has been found: ‹field’s label›" usually means that field is over its `maxlength`, and the message never says so.** Measured 24 Sept: "If yes, please describe" errored while the textarea was visibly full, and it was rejected only because it held 194 characters against a `maxlength` of **128**. I first recorded this as a stale error to be ignored; that was wrong, and the candidate caught it. **Never dismiss a Drupal/Greenhouse field error as stale.** Run this before every submit:
  ```js
  [...document.querySelectorAll('input[maxlength],textarea[maxlength]')]
    .filter(e=>e.value && e.value.length > +e.getAttribute('maxlength'))
    .map(e=>e.id+' '+e.value.length+'/'+e.getAttribute('maxlength'));
  ```
  The native setter writes past `maxlength` without complaint, so a setter-filled free-text answer can silently exceed a limit that real typing would have capped.
- **The `Remove` button under an attached file does not respond to clicks while that stale error is showing** — not to a ref click, not to a coordinate click on the button in a fresh screenshot. To swap a CV, **reload the posting URL and refill**: the whole form is a setter pass plus one upload, so a rebuild is faster than fighting the AJAX, and it clears the error too.
