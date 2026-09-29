# Workable

- **URLs:** job `apply.workable.com/j/<id>`; form `apply.workable.com/<company>/j/<id>/apply/`; board `apply.workable.com/<company>`.
- **Set values:** Setter is fine for free text/textareas. Identity fields (name, email) and server-validated fields: `e.focus(); e.select();` (JS) → real `Delete` → real `computer type`. Don't: `form_input` (sets `""`), `triple_click`/`ctrl+a` (inserts inside and truncates at maxlength). Page shifts 10–12 px per keystroke → fresh screenshot before any coordinate click.
- **The form does not exist until you click "Apply for this job".** Measured 24 Sept (Our Future Health): on `/j/<id>` and even after following the "Application" tab link, `input,textarea,select` count is **0** — which reads exactly like a dead or account-walled form. A ref-click on the Apply button did nothing; a **coordinate click** on it navigated to `/apply/` and the 17 fields appeared. So: screenshot, click the button by coordinate, then read the fields. Never conclude "no form" from a zero input count here.
- **The resume `input[type=file]` is hidden behind a `<label>`.** `find` returns the label, and `file_upload` rejects it ("Element is not a file input"). Expose and tag it first, then `find` it by the new id:
  ```js
  [...document.querySelectorAll('input[type=file]')].forEach((f,i)=>{f.style.display='block';f.style.opacity='1';f.style.width='200px';f.style.height='30px';f.id='cvup'+i;});
  ```
- **Phone has its own country selector.** The field strips a typed `+90` and keeps only the national number, with the dial code held next to it. That is correct; don't "fix" it by retyping the E.164 form.
- **Radios need coordinate clicks, and the page shifts between them.** Scroll the group into view first (a radio below the fold gives "Coordinate is outside the coordinate frame"), re-measure after **each** click, and verify `.checked` — the second click of a pair routinely misses by a pixel or two on the first attempt.
- **Traps:** Cookie overlay blocks the form → click "Decline all" by coordinate (ref click doesn't close it). Salary fields number-format ("7,000 USD…" → "7.000") → digits only, explanation elsewhere. Server-side char limits (e.g. 127) with no counter. Form questions may reveal compensation missing from the posting.
