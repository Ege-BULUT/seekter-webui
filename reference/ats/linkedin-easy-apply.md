# LinkedIn Easy Apply

- **Flow:** modal, 4–6 steps: Contact info → Resume (pick a profile PDF; no upload) → optional → Additional Questions → Review → Submit. No CAPTCHA. Works in Claude's own browser panel.
- **Driver (single JS call):**
  ```js
  const CV='<CV_NAME>';   // filename of the resume already on the LinkedIn profile
  function panel(){const t=[...document.querySelectorAll('button')].find(x=>x.offsetParent&&/^(Next|Review|Submit application)$/.test((x.innerText||'').trim()));if(!t)return null;let p=t;for(let i=0;i<10;i++){p=p.parentElement;if(p&&(p.innerText||'').length>120)break;}return p;}
  function pickCV(n){const t=[...document.querySelectorAll('*')].filter(e=>e.textContent.includes(n)&&e.children.length===0)[0];if(!t)return 0;let c=t;for(let i=0;i<8;i++){c=c.parentElement;if(c.getAttribute('role')==='button')break;}c.click();return 1;}
  const b=[...document.querySelectorAll('button')].find(x=>/Easy Apply to this job/.test(x.getAttribute('aria-label')||''));
  if(!b)throw new Error('NOEASYAPPLY');
  b.click();await new Promise(r=>setTimeout(r,3500));
  let prev='',log=[];
  for(let i=0;i<12;i++){const p=panel();if(!p){log.push('NOPANEL');break;}
   const cur=(p.innerText.match(/^\d+\/\d+ pages/)||[''])[0];const txt=p.innerText.replace(/\n{2,}/g,'\n').slice(0,700);
   if(/Select or upload a resume/.test(txt)){pickCV(CV);await new Promise(r=>setTimeout(r,1200));}
   if(cur&&cur===prev){log.push('STUCK:'+txt);break;}prev=cur;
   const nx=[...document.querySelectorAll('button')].find(x=>x.offsetParent&&/^(Next|Review)$/.test((x.innerText||'').trim()));
   if(!nx){const s=[...document.querySelectorAll('button')].find(x=>x.offsetParent&&(x.innerText||'').trim()==='Submit application');
    if(s){s.click();await new Promise(r=>setTimeout(r,4500));}log.push('SUBMITTED:'+/Application submitted|application was sent/i.test(document.body.innerText));break;}
   log.push(cur);nx.click();await new Promise(r=>setTimeout(r,2600));}
  JSON.stringify(log)
  ```
  `STUCK:` → answer that page manually, re-run. Privacy-notice consent extension (insert inside the loop):
  ```js
  if(/privacy notice/i.test(txt)){const cb=[...document.querySelectorAll('input[type=checkbox]')].filter(e=>e.offsetParent||e.id)[0];if(cb&&!cb.checked){const lb=[...document.querySelectorAll('label')].find(l=>l.getAttribute('for')===cb.id);if(lb)lb.click();await new Promise(r=>setTimeout(r,500));}}
  ```
  The driver misses consents rendered as a `<select>` — pick those manually.
- **Set values:** `<select>`: native setter + `change`. Text: `form_input`/setter. Click+type in one `browser_batch` (separate calls → modal shifts).
- **Radios/checkboxes:** radios are 0×0; real `left_click` at the centre of `label[for=<radio id>]`. Fallback: click radio → `space`. **On the work-authorization page, go straight to the fallback.** Measured 24 Sept (SoTalent): clicks landed dead centre on both circles, confirmed by zoom, and `.checked` stayed false for all four options; click-then-`space` set each one first try. JS `.click()` unreliable — verify `.checked`. Checkbox "Element type DIV is not a supported form input" → `scroll_to` + coordinate click.
- **Typeahead:** Location can't be JS-set: ref-click → type city → 3 s → click suggestion by coordinate (`Return` fails here). "Location (city)" may be pre-filled yet look empty — typing appends; `End` + `BackSpace`s, then pick.
- **Traps:**
  - "Years" fields with a 20-char counter are still number-only ("Invalid input").
  - **A screening input can refuse JS focus entirely.** Measured 24 Sept (Ayesa): `e.focus(); e.select()` then real typing left the field empty and "Invalid input" standing, twice. A coordinate click into the input inside the modal, then typing in the same `browser_batch`, filled it first try. Screenshot the modal and click the input rather than trusting `focus()`.
  - **Read the screening questions before assuming the employment type.** One posting described a staff UI/UX role and its single question was "What would be your expected daily rate as a freelancer for this position?", the only place the contract type appeared anywhere.
  - Some fields strip spaces → hyphens or one word. Salary text may cap at 20 chars → terse ("5500 EUR/mes" style).
  - Custom typeaheads that never validate → save draft, hand over.
  - Voyager `applyingInfo.applied` is unreliable (`undefined`) — dedup from own records.
- **Drafts:** "Save this application?" → `Save` (→ `linkedin.com/jobs-tracker/?stage=draft`) or `Discard`. Resume via "Continue" on `linkedin.com/jobs/view/<id>`. "Discard draft application and remove this job?" → Yes deletes; "Did you finish applying?" cards can't be deleted — leave them.
- **Submit:** driver logs `SUBMITTED:true` when "Application submitted"/"application was sent" appears.
