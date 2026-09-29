# Indeed SmartApply

- **URLs:** `smartapply.indeed.com` (opened in a new tab by Glassdoor Easy Apply; Glassdoor itself needs sign-in — human does it).
- **Flow:** Resume (38%) → employer questions (50%) → consent (88%) → Review → "Submit your application" → back on posting with "Your application was sent!" / `smart-apply-action POST_APPLY` in URL. Upload the current CV; don't reuse an old stored one.
- **File upload:**
  ```js
  document.querySelector('input[type=file]').id='cvupload';
  ```
  then `find` "hidden file input with id cvupload" → `file_upload`.
- **Traps:** Hangs on "Preparing review" → `navigate` to `smartapply.indeed.com/beta/indeedapply/form/review-module`; flow restarts at 38% with answers remembered; Continue ×3 → Submit appears. Don't refill.
