# Breezy

- **URLs:** `<company>.breezy.hr/p/<id>/apply`.
- **Set values:** no ids, only names: `cName`, `cEmail`, `cPhoneNumber`, `cAddress`, `cSummary`, `cCoverLetter`, `cResume` → `querySelector('[name="cName"]')`. Only `cName`, `cEmail` mandatory.
- **Traps:** hidden honeypot field (random suffix, e.g. `hp_7f2b`) — never fill. CV parse spawns 70+ fields and gives the current job an end date → clear the end date so it reads "Present".
- **Submit:** button may be localised ("Başvuruyu Gönder").
- **The slug is `<position_id>-<title-slug>`, and an employer can rename a posting in place.** The id stays, the slug changes, and a tracker that keys on the whole path reads the rename as a brand new job. Measured 25 Sept: Cal.com's `ff94f3182ac2` was applied to on 18 Sept as `senior-product-designer` and reappeared as `senior-product-design-engineer` with a rewritten description. It passed dedup as NEW and only Breezy's server caught it, after the form was filled and the CV uploaded. `job_key` now keys Breezy on the id alone.
- **A silent refusal is readable.** The form is AngularJS: `ng-submit="apply()"` with `formSubmitted` / `isSubmitting` on the scope. When a submit does nothing and no request leaves the page, read the reason instead of re-clicking:
  ```js
  var s = angular.element(document.querySelector('form')).scope();
  s.errorMessage; // e.g. "It looks like maybe you've already applied to this job?"
  s.candidate;    // the exact payload: name, email_address, summary, resume, work_history
  ```
  `s.candidate` is the ground truth for what would be sent, so check it rather than the DOM.
- **The visible `error-container` elements lie.** After a failed submit the form renders every "X gerekli" template at `display:none`, and a naive "collect elements whose text says required" scan reports six blockers that do not exist. Check `getComputedStyle(el).display` and the control's own `$error` (`angular.element(el).controller('ngModel').$error`) before believing any of them.
- **The CV parse lands after the fields are set and overwrites `cSummary`.** Fill the summary *after* the upload finishes, not before, or the parser's generic profile blurb replaces it. The parse also invents a junk work-history block from a project heading ("Title Unknown"); delete the whole `li.experience` with its `a.del-pos` link rather than blanking the fields.
