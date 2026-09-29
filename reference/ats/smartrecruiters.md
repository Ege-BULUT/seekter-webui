# SmartRecruiters

Two surfaces, one ATS. The classic form is ordinary DOM; the `oneclick-ui` flow is shadow DOM all the way down and needs the walker below. Read which one you are on before anything else.

## The classic form

- **URLs:** `jobs.smartrecruiters.com/<Company>`. "I'm interested" leads to `/oneclick-ui/company/<Co>/publication/<uuid>`, then a second `/screening` page of employer questions.
- **The phone widget guesses the country from the job, not the candidate.** It set Germany +49 for a Munich role even though the city field said Istanbul. Writing the full E.164 number into the field corrects the flag. Check it: the number is silently wrong otherwise.
- **Set values:** If `document.querySelectorAll('input')` returns ~1 result, fields are in shadow DOM: `read_page` won't see them, coordinate click + `type` works. Textarea can't be cleared by keys (text goes mid-string) — get it right first time or reset with:
  ```js
  const s=Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value').set;
  s.call(el,'yeni metin'); el.dispatchEvent(new Event('input',{bubbles:true}));
  ```
- **File upload (`SPL-DROPZONE` shadow input):** never click "Choose a file".
  1. Inject a helper:
     `i=document.createElement('input'); i.type='file'; i.id='cvhelper'; i.setAttribute('aria-label','Resume helper upload'); i.style.cssText='position:fixed;left:20px;top:20px;z-index:999999;width:300px;height:30px;'; document.body.appendChild(i)`
  2. `find` it → `file_upload`.
  3. Transfer: `const f=document.getElementById('cvhelper').files[0]; const sr=document.querySelector('SPL-DROPZONE').shadowRoot; const inp=sr.querySelector('input[type=file]'); const dt=new DataTransfer(); dt.items.add(f); inp.files=dt.files; inp.dispatchEvent(new Event('change',{bubbles:true,composed:true}));`
  4. Remove the helper. Reading `inp.files[0].name` errors (component empties the input) — normal; verify by screenshot.
  Alternative (also worked): walk shadow roots, move the input into light DOM, then `find` → `file_upload`:
  ```js
  function walk(root,out){root.querySelectorAll('*').forEach(el=>{if(el.shadowRoot)walk(el.shadowRoot,out);
  if(el.tagName==='INPUT'&&el.type==='file'&&(el.accept||'').includes('.pdf'))out.push(el);});return out;}
  const f=walk(document,[])[0];
  f.setAttribute('aria-label','Resume CV upload field');
  f.style.cssText='position:fixed;top:5px;left:5px;width:260px;height:34px;opacity:1;z-index:2147483647';
  document.body.appendChild(f);
  ```
  (Moving to light DOM is SmartRecruiters-only; on Lever it breaks the upload.)
- **Traps:** Message fields reject `:` and `;` ("This field cannot contain following characters: ;") — use dashes.

## `oneclick-ui` (`jobs.smartrecruiters.com/oneclick-ui/...`)

- The "I'm interested" button on a job page lands here; `/apply` on the job URL does not.
- **The whole form is shadow DOM** (39 shadow roots measured 24 Sept, IFS), so `document.querySelectorAll('input,textarea')` returns **one** element and it is the **profile-image** slot, not the resume. Handing the CV to that slot is the documented avatar trap. Fill everything by coordinate click plus typing instead.
- The phone country picker has its own search box and uses the English name, so "Turk" finds "Turkey +90" directly. The City field is a geocoder: type, wait, pick "Istanbul, Türkiye".

**The flow looks unreachable and is not.** The page nests ~1,800 shadow roots and `find`, `read_page` and `document.querySelectorAll` all return nothing, which is what made it look like a wall. A recursive walk reaches everything:

```js
window.__deepAll=function(){const out=[];(function w(r,d){if(d>14)return;
 (r.querySelectorAll?[...r.querySelectorAll('*')]:[]).forEach(e=>{
  if(/^(INPUT|TEXTAREA|SELECT)$/.test(e.tagName))out.push(e);
  if(e.shadowRoot)w(e.shadowRoot,d+1);});})(document,0);return out;};
```
Set values with the native setter and dispatch `input`/`change` with **`composed:true`** so the event crosses the shadow boundary.

- **Uploading a file when the input is in shadow DOM.** `file_upload` needs a ref and refs cannot reach shadow roots, so bridge it: create a light-DOM `<input type="file">` with a distinctive `aria-label`, `find` it, upload to it, then move the file across and remove the proxy:
  ```js
  const f=document.getElementById('__cvproxy').files[0];
  const dt=new DataTransfer(); dt.items.add(f);
  const d=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'files');
  d.set.call(target, dt.files);           // plain `target.files = …` is ignored
  target.dispatchEvent(new Event('change',{bubbles:true,composed:true}));
  ```
  Exclude the proxy when you collect the targets, and note there are usually **two** dropzones (resume and cover letter) with identical `accept` lists: fill only the first and clear the second.
- **There are two resume-accepting file inputs and they do different jobs.** The top "Easy Apply" dropzone only runs the CV parse that fills Experience and Education; the required **Resume** field sits further down the page and is a separate input with the same `accept` list. Bridging the file to the first one leaves Resume empty and the form fails. Measured 25 Sept on IFS and NBCUniversal: send the file to the **last** matching input for the attachment, and if you also want the parse, send it to the first one too. Both come from the same proxy.
- **The upload triggers a CV parse that overwrites fields you already filled.** It split a two-token first name across the First and Middle fields, cleared Confirm Email, and put the location string into the postal-code field. It also populates Experience and Education from the CV, accurately. **Upload first, then fill the text fields**, and re-check the name split.
- **The place-of-residence field is a postal-code geocoder and needs a picked suggestion**, not typed text; until one is chosen it fails with "Please provide your place of residence". Typing the postcode returns **international** matches on the same digits, so read the list before clicking: one five-digit code offered entries in the US, Spain, Mexico, Syria and two in the home country.
- Radio groups on the screening step are not `input[type=radio]` in the walk; click them by coordinate from a full-resolution screenshot.
