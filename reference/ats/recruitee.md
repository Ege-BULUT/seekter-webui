# Recruitee

- **URLs:** `<company>.recruitee.com/o/<slug>` or `/c/new`.
- **Set values:** `form_input` works on text; `type="date"` via `form_input` in ISO (`2026-10-06` format).
- **Radios/checkboxes:** label-ref click reports success but checks nothing → coordinate click.
- **Phone:** country selector default may be wrong. Open it; typing a country name can jump to a neighbour (e.g. "Turkey" → "Turks & Caicos"; the right row was "Türkiye") — check the highlighted row. Then type the number.
- **Submit:** Before submitting, list `input[type=checkbox]` and tick the one whose name/id contains `agreements` (Legal Agreements / Applicant Privacy Notice) — missing it RESETS the whole form on submit. Missing required field → page jumps to top with a red warning.
