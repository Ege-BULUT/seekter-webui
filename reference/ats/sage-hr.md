# Sage HR

- Short form: first name, last name, email, phone, one CV upload, then consents. No residence or
  work-authorization questions of its own, so the posting's own text is the only location gate.
- **The terms checkbox lies about being optional.** `applicant_agree_to_terms` reports
  `required=false`, and the submit button is enabled, but client-side validation refuses with a red
  **"Please agree to Terms & Conditions"** under the form and the page does not move. Nothing
  appears in a `fetch` error capture because no request is ever made. Measured 23 Sept on Paybis.
  Since Seekter never accepts terms of use, this ATS is **always a hand-off**: fill everything, upload
  the CV, leave the box, and hand over with the exact remaining action.
- Two privacy radios, "this position only" versus "all suitable positions". Pick the narrower one.
- The upload area confirms with the text **"1 file selected"**, not a filename, so grepping the page
  for the CV's name returns nothing. Verify from that string or from a screenshot.
