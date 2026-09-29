# Workday

- **Account:** mandatory (also for "Apply Manually"); human creates/signs in, Claude fills.
- **Start:** **Apply Manually**. Don't use "Autofill with Resume" (broken experience blocks). Cleanup helper, 1 s between calls:
  ```js
  window.DEL=function(){var b=[...document.querySelectorAll('button')].filter(function(e){return /delete/i.test((e.innerText||'')+(e.getAttribute('aria-label')||''))&&e.getBoundingClientRect().width>0;});
  if(b.length<2)return 'stop'; b[b.length-2].click(); return 'ok';};
  ```
- **Same company again:** `/apply/useMyLastApplication` carries everything incl. CV; only "How Did You Hear" + Application Questions need input. Check Candidate Home "Suggested Jobs".
- **Set values:** tenant-dependent — test one field.
  - Inputs: real `computer type` on some tenants; on others it swallows ASCII → native setter.
  - ⛔ **Textareas: the setter lies, and `value.length` does not catch it.** Measured 27 Sept (Warner Bros. Discovery tenant): four role-description textareas were filled with the native setter, every one read back the correct `value.length` immediately **and again after a re-read**, the step saved without error, and the **Review page showed "Role Description ~ No Response" for all four**. The DOM value was real; it never reached Workday's state. Real `computer type` into a focused textarea worked first time. So: type textareas for real, and **treat the Review step as the only proof** — `value.length` proves nothing on this ATS. Worth a `(t.match(/No Response/g)||[]).length` scan of the Review page before submitting.
  - The same setter DOES work on plain text inputs (job title, company, location, names, address) on the same tenant, which is why the failure is easy to miss.
  - Setter does NOT work on date and prompt fields.
  - Clear: `End` + `BackSpace` ×40 (written out), re-focus, type. Quote characters are rejected.
- **Dropdowns / questionnaire — pure JS clicks (no coordinates):**
  ```js
  window.BT=[...document.querySelectorAll('button[id^="primaryQuestionnaire--"],textarea[id^="primaryQuestionnaire--"]')];
  window.PICK=function(i){var b=window.BT[i];b.scrollIntoView({block:'center'});b.click();return 'opened '+i;};
  window.CL=function(txt){
    var o=[...document.querySelectorAll('div,li')].filter(function(e){
      var r=e.getBoundingClientRect();
      return r.width>0&&r.height>0&&e.children.length===0&&
             (e.innerText||'').trim().toLowerCase().indexOf(txt.toLowerCase())===0;});
    if(!o.length)return 'nf'; o[0].click(); return 'clicked';};
  ```
  Batch: `[js PICK(4)] [wait 2] [js CL('No')] [wait 2] [js PICK(5)] [wait 2] [js CL('No')] ...` Re-read `window.BT` after answers that add conditional questions. Checkboxes: `.click()`.
- **Date (month/year): try the segment inputs first, they are much cheaper.** On tenants that render From/To as two `spinbutton` inputs (`aria-label` "Month" and "Year"), focus the month input and type the whole thing in one go, e.g. `computer type "062026"` — it fills the month, auto-advances and fills the year. The `name` attribute is dropped after render, so grab them positionally out of `document.querySelectorAll('input')` and give them ids. Verify by reading the screen-reader text: `current value is 6/2026`. Measured 27 Sept across four work-experience blocks and one education block, no failures.
- **Date (month/year), fallback for the single combined field:** click month segment (x ≈ left+10px) → `BackSpace`×8 → month digit → `Tab` → `BackSpace`×6 → year. Error may linger until Save and Continue.
- **Phone:** "Country Phone Code" is a separate field. Phone Number = `<PHONE_LOCAL>` only; with `+90` → "The number isn't recognized".
- **"How Did You Hear":** two-level menu; LinkedIn sits under "Social Network", "Job Board/Website" or "Job Sites" per tenant; search may not filter. First option may be "Email" — don't misclick.
- **Option lists in Education and Skills: the search box does not filter and the list is virtualized.** Measured 27 Sept: "Field of Study" and "Skills" both returned an alphabetical list starting at Accounting no matter what was typed, and a DOM query for the wanted option found nothing because only the visible rows exist. Both are optional on that tenant, so leave them; the CV carries them. `School or University` was a plain text input, not a picker, so the education block was usable after all.
- **The Degree list needs `find` + a ref click.** A coordinate click on the option row left it on "Select One"; `find` "Bachelors option in the open Degree list" then a ref click set it immediately.
- **"How Did You Hear About Us" — typing in its search box RESETS the menu to the top level.** Measured 27 Sept: opening it, drilling into "Job Board", then typing "LinkedIn" threw the drill-down away and showed the eight top-level categories again. Navigate by clicking only: Job Board → scroll the sub-list → LinkedIn. It sits between JobTeaser and Mediabistro.com.
- **Step labels in the progress bar are not links.** To go back and fix something, click **Back** once per step; it preserves everything already entered.
- **Voluntary Disclosures can be hard-required even while the page says it is voluntary.** On the Warner Bros. Discovery tenant, gender, ethnicity and veteran status all carry an asterisk and block Save and Continue, directly under a paragraph saying "Providing the information or declining to provide it will not affect your application in any way." The profile supplies all three, so answer them and note it; Hispanic/Latino had no asterisk and was left blank.
- **Traps:** School list returning "No items." → delete the optional education block. Only the Data Privacy Notice is required on tenants that have one.
- **Submit / save:** Save and Continue often — a session drop (`Something went wrong ... Error Code: VPS|...`) loses the unsaved page. Buttons may need two clicks; check `completed step N of 5`.
