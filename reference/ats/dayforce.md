# Dayforce

- **URLs:** `jobs.dayforcehcm.com`. No account needed: Apply → "Apply without an Account".
- **Flow:** CV upload (parse is correct) → Candidate Info → 5-page Questionnaire → Candidate Acknowledgement → Submit → **record the confirmation number**.
- **Set values:** mandatory: Preferred Contact Method, Country, State/Province, Address Line 1 (`<ADDRESS_LINE>`), City, Zip, How did you hear.
- **Dropdowns:** click-selection doesn't stick. Click the chevron → `Down` ×N → `Return` (N Downs lands on option N+1). Wrong → `Escape`, reopen, fix with `Up`. State/Province: clear the field and type nothing — the list then shows `İstanbul` (typing `Istanbul` → "No data").
- **Traps:** US disability (CC-305) → "I do not want to answer"; veteran → "I am not a protected veteran"; EEO optional → blank.

## The no-account path and the import trap, measured 24 Sept

- **The "Sign In" wall is not the only way in.** The Apply button sends you to account creation, but the same posting has a no-account path: `…/jobs/<id>/apply/manualApplication?applicationSource=Manual`. Try that before recording an account-wall hand-off. Measured 24 Sept (Questrade): the posting was logged as account-walled on the Apply button alone and the manual form turned out to be fully open, which the candidate found himself.
- **Uploading the CV silently runs "Import Resume" and overwrites fields you already filled.** It split a two-token first name across First and Middle, cleared Confirm Email and every address line, and kept only what it had parsed. **Upload the CV first, then fill the text fields**, and re-verify the name split afterwards. The phone country code is the one thing it gets right: it detects the dial code from the CV.
- **`State/Province` is a required strict dropdown with no list for many countries.** With Country = Turkey it returns "No Data" for any typed input and there is no free-text fallback, while Next still fails with `'State/Province' is required`. No truthful value exists, so the application cannot be completed; a US or Canadian province would be a false answer. Hand off rather than inventing one. Check this field early on any Dayforce posting for a non-US/CA candidate, because everything else on the form fills cleanly and the block only shows at the end of step 1.
- Comboboxes are `rc-select` (`role=option` in an `.rc-virtual-list-holder`). They do not filter as you type and a `find` ref can resolve to a neighbouring dropdown, so several lists sit in the DOM at once and a naive `[role=option]` sweep returns all of them. Open the one you want by clicking its **chevron** by coordinate, then pick the option with a JS text match and a dispatched `pointerdown/mousedown/pointerup/mouseup/click` sequence.

## ⚠️ The two measurements disagree about State/Province

The first note says to clear the field and type nothing, after which the list offers the home-country
province. The second says the field is a strict dropdown that returns "No Data" for any input once
Country is set to the home country, with no free-text fallback and no truthful value available, while
Next still fails on it. Both were measured, on different tenants. **Try the empty-field trick first,
because it costs one interaction; if the list still says "No Data" the posting is a hand-off on that
field alone.** Do not spend a second pass fighting it, and do not invent a province.
