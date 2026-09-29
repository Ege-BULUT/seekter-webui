# Traffit

- Single-page form, no account. Fields are `dynamic_form_properties_<id>`; the native setter works on all text inputs.
- **Dropdowns are selectize and only open on a click at the caret**, the right-hand ~14 px of the control. A click in the middle of the field, or `focus()` plus typing, leaves the list closed and silently accepts free text that never becomes a value.
- **Some selectize lists never load.** Measured 24 Sept (HTD): "What country are you applying from?" returned no options after "Tur", "Turk" and "Turkey" with waits up to 8 s, while the two required lists on the same form opened normally. If the field is optional, clear it rather than leaving a partial string; do not invent a value.
- **Consent checkboxes can both be hard-required**, including one covering *future* recruitment processes. Read them: a future-recruitment consent that is a precondition of applying is a different thing from an optional talent-pool tick.
- Success = redirect to `/public/form/thankyou/<id>`.
