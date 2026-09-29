# Personio

- **URLs:** `*.jobs.personio.com|de`. Easiest ATS, ~4 calls.
- **Set values:** native setter on stable ids: `field-first_name`, `field-last_name`, `field-email`, `field-phone`, `field-available_from`, `field-salary_expectations`, `field-custom_attribute_*`. Phone digits only, no `+` (`90<PHONE_LOCAL>`).
- **Dropdowns:** Country list lacks the home country — leave blank if optional and put `<CITY>, <COUNTRY>` in "City"; if mandatory → hand over. "Preferred Work Location" is a custom multi-select checkbox list (invisible to `querySelectorAll('select')`) → real clicks; tick the cities the posting lists.
- **File upload:** `doc-input-cv`, max 750 kb.
- **Traps:** Usercentrics layer (`aside#usercentrics-cmp-ui` shadow root) blocks the page and shows only "Accept All". Run `await window.UC_UI.denyAllConsents()`, then one real coordinate click on the "cookie settings" link inside it; the layer closes. Coordinate clicks silently lost here when K was wrong — recompute.
- **Submit:** `Bewerbung senden` / `Submit Application`.

## Reached through an aggregator redirect

- Reached from aggregators through a `t.gohiring.com/h/<hash>` redirect. Don't guess the tenant from
  the company name: a hand-built `<company>.jobs.personio.de` guess landed on Personio's own
  marketing site (measured 23 Sept on UP42). Follow the redirect instead.
- Plain ids (`field-first_name`, `field-email`, `field-available_from`, `field-salary_expectations`,
  `field-custom_attribute_<n>`); the native setter works on all of them.
- **`field-available_from` accepts a plain ISO date** (`2026-10-07`) even though it is `type=text`
  with a datepicker attached. No need to fight the calendar widget.
- **Three file inputs, always**: `doc-input-cv`, `doc-input-cover-letter`, `doc-input-other`, all
  with identical `Add file` context, so `find` cannot tell them apart. Disable and hide the other
  two, expose `doc-input-cv`, then `find` and upload; restore afterwards. After upload
  `input.files` is **empty** because Personio swaps the element, so confirm from the filename
  rendered under the `CV*` heading.
- The optional `field-gender` select stays empty; it is demographic data with no employer requirement.
