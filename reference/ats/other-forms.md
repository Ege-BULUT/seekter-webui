# Other and one-off forms

- **HR-ON (same-origin iframe, e.g. EIVA):** if the uploader doesn't register the file ("no files has been uploaded"), choose "I want to type my résumé" and paste text: `pdftotext -layout <CV_PATH> -`. Quill editor: `editor.innerText = cv` + `input` event, then click → `End` → space → `BackSpace`.
- **Alfa Jobs (welovealfa.com):** scroll locks after the country combobox. Drive everything by JS: combobox `.click()`, option from `[role=option]` by text `.click()`, text via setter. Turnstile self-solves.
- **Huzzle:** `form_input`+ref one field at a time; a bulk setter script got blocked ("[Real-World Transactions]"). Draft: "Save this application?" → Save.
- **Siemens (jobs.siemens.com):** session drops silently (`/Error`, `/Login`); verify session after each step; check posting status before retrying.
- **Viterbit:** setter works. City dropdown: click dropdown → click its search box separately (first typing swallowed) → type without Turkish chars (`stanbul`) → click option. Reject cookies: `s-rall-bn`.
- **select2-style widgets (e.g. In4Matic):** `option.selected=true`+`change` leaves the placeholder visible = not selected → real clicks.
- **BambooHR (content):** read "Minimum Experience" (e.g. Manager/Supervisor) at the end of `get_page_text` — the employer's own seniority tag.
