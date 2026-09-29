# Recruitly

- Recruitment-agency boards. Two-step wizard: step 1 is name, CV, email, phone with a **Continue**
  button; step 2 holds nationality, languages, expected salary range and the consent. **Step 2's
  fields exist in the DOM before you reach them**, so values written early are silently discarded.
  Fill each step after it renders.
- Fields have no `id`, only `name` (`firstName`, `surname`, `applicantEmail`, `applicantPhone`,
  `expectedPay.minPay`, `expectedPay.maxPay`, `agreedPrivacyPolicy`). Use `[name="…"]`.
- Nationality and Languages are **Tom Select** multi-selects (`tomselect-N-ts-control`). Two traps:
  a JS `.focus()` does not make them active (`document.activeElement` stays elsewhere), so click by
  coordinate and confirm `activeElement`; and while their dropdown is open, **a stray click adds
  whatever option is under the cursor** (added "Aland Island" once). Escape the list before clicking
  anything else, and re-read the chips after every pick.
- Languages are levelled entries, not bare names: type `English > Full` and pick the single result.
  C1 maps to **"English > Full Professional"**.
- Cloudflare Turnstile sits on the submit and self-solves; `cf-turnstile-response` reads empty right
  up to the click and the submit still goes through. Confirmation is **"Application received"**.
