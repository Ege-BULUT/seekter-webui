# Rippling

- **URLs:** `ats.rippling.com/...`, also white-labelled on employer sites.
- **File upload:** inputs hidden; expose then `find` → `file_upload`:
  ```js
  [...document.querySelectorAll('input[type=file]')].forEach((e,i)=>{e.id='ff'+i;e.style.cssText='display:block;opacity:1;position:static;width:280px;height:28px;';});
  ```
  Or `find` "hidden file input element for resume upload" (a generic query returns the "Drop or select" button, not the input).
- **Set values:** CV parse fills email, phone code, location, links, company correctly — fix the first/last-name split. Date = three inputs `field-XX-month`, `-day`, `-year`.
- **Dropdowns:** `[class*=select]` divs; open with `mousedown/mouseup/click` dispatch, select via `[role=option]`.
- **Traps:** SMS consent → "No - I do not consent to receiving text messages".
- **Count the text inputs, don't guess their order.** `Pronouns` sits between `Email` and `Current company` and is a plain text input, so "the first empty text field" is Pronouns, not the question you are looking for. Measured 25 Sept: a required free-text question was typed into Pronouns and the submit still failed. Locate a field by walking up from it to the nearest ancestor with text: `e.closest('div')` upwards until `innerText.length > 25`, then match the question wording.
- **`input[type=text]` as a selector has missed on this ATS**; `querySelectorAll('input')` and filtering on `e.type === 'text'` works. Same for the submit: the form validates silently and only paints "This field is required" next to the offender, so read visible error text after every failed submit instead of re-clicking.
- **Rippling's own posting can disagree with the boards.** Measured 25 Sept: intodesignsystems listed a role as "Remote · North America and Europe" and designsystems.jobs listed the same role as "United States, United Kingdom, Canada", while the posting itself named no country and the form asked no residence question. Read the ATS page, not the board card.
