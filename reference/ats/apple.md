# Apple (jobs.apple.com)

- **Flow:** Add Resume → Profile Information → Self-Disclosure → Review & Submit. Use "Use my resume to fill out my profile", then check name split, duplicated experience records (cause unnamed "required field empty" → Remove), empty descriptions.
  ```js
  [...document.querySelectorAll('input')].filter(e=>/employer/i.test(e.id)).map(e=>e.id+'='+e.value)
  ```
  ```js
  [...document.querySelectorAll('select')].filter(e=>e.offsetParent&&!e.value).map(e=>e.id)
  ```
- **Dropdowns:** real `<select>`s that don't open on click → native setter:
  ```js
  var set=Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set;
  set.call(s,'supportingLinkCategory-PORTF');
  s.dispatchEvent(new Event('input',{bubbles:true}));
  s.dispatchEvent(new Event('change',{bubbles:true}));
  ```
- **Traps:** Self-Disclosure is asked every time. "Add links" adds one row at a time — fill it before clicking again.
- **Submit:** verify at `jobs.apple.com/app/en-us/profile/roles` ("Submitted - <date>").
