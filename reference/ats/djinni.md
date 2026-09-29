# Djinni

- **Blocker:** nothing can be applied to until the profile is published (Apply does nothing; banner "Create your profile to start apply for jobs…"). Publishing = `djinni.co/my/wizard/preview/` → "Start search", which accepts terms → human must press it.
- **Profile wizard** (`djinni.co/my/wizard/profile/`): "Experience summary" is contenteditable (setter on `textarea#moreinfo` doesn't render) → click and type. Category auto-sets — check. `+ Add skill` doesn't move focus. `skills_experience[N][experience_years]` takes the setter. Salary: single `salary_min`.
- **Traps:** the real industry is in the right-column "Domain" field, not the text (check for Gambling). List is truncated until the profile is complete.
