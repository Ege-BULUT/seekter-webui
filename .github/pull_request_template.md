## What changed

<!-- One or two sentences. The same sentence that should be the commit subject: a statement of the finding, not a file list. -->

## What you measured

<!-- What you ran, what happened, and on what date. This is the part a reviewer cannot check for you.
     Skip only if this is a typo fix or a script change with no measurement behind it. -->

## Checks

- [ ] No real names, emails, phone numbers, addresses, salary figures or CV contents anywhere in the diff — including in examples. Placeholders used instead (`<FIRST_NAME>`, `<EMAIL>`, `<PHONE_LOCAL>`, `<CV_NAME>`, `<CITY>`, `<COUNTRY>`).
- [ ] Nothing under `profile/`, `applications/` or `runs/` is added, and `.gitignore` is unchanged.
- [ ] Nothing tracked assumes a job title, a discipline, a city, a currency or a salary band. Where a measurement only holds for one of those, the note says so.
- [ ] If a file already said something about this, I changed that sentence rather than adding a second one below it.
- [ ] A new source or vendor file has a row in the matching `_core.md` index table.
- [ ] The guardrails are untouched: no CAPTCHA solving, no account creation, no passwords, no accepting terms, no sending messages as the user, no invented answers.
- [ ] I read my own diff.

## Anything a reviewer should know

<!-- A contradiction you found, something you weren't sure about, a limit on how far the measurement travels. Optional. -->
