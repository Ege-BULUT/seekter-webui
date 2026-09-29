# Contributing to Seekter

The most valuable thing you can send is **a measurement**.

Everything in `reference/` was learned by filling a real form or sweeping a real source, and losing an application to it. There are dozens of application systems and job boards nobody here has ever touched. If you find one that behaves in a way that isn't written down, that note is worth more than any feature.

## What belongs where

| You found | It goes in | Also do |
|---|---|---|
| A job source behaving in a way nobody documented | `reference/sources/<source>.md` | Add a row to the table in `reference/sources/_core.md` |
| An application form system (ATS) behaving that way | `reference/ats/<vendor>.md` | Add a row to the identify table in `reference/ats/_core.md` |
| A lesson that belongs to no single source or vendor | the matching `_core.md` | Nothing else |
| A source you checked and found dead, paywalled or empty | `reference/sources/dead-and-low-value.md` | Say what you ran and what came back |
| A bug in the tracker CLI or a sweep script | `scripts/` | Say how to reproduce it |
| A change to how a command behaves | `.claude/skills/seekter-*/SKILL.md` | Open an issue first; these are the agent's instructions |

**Before proposing a new board, read `reference/sources/dead-and-low-value.md`.** Most of the obvious candidates are already in it, with the measurement that killed them.

## The five rules that govern `reference/`

These are not style preferences. Each one is there because breaking it cost something.

**1. Write about the widget, never about the person.**
No names, emails, phone numbers, street addresses, postcodes, salary figures or personal domains — not even as a worked example. Use the kit's placeholders: `<FIRST_NAME>`, `<EMAIL>`, `<PHONE_LOCAL>`, `<CV_NAME>`, `<CITY>`, `<POSTCODE>`, `<COUNTRY>`.

A note stays just as useful when the person is removed from it:

> ✅ *the phone widget renders the number in spaced national format, so the value read back does not match the value typed*
> ❌ *typing 5xx xxx xx xx into the phone widget reads back as …*

A country or city named as a genuine trap is fine and should stay — `typing "Istanbul" returns No data, the list wants "İstanbul"` is a reusable lesson about non-ASCII place names, not personal data.

**2. Measured, with a date.**
"Greenhouse is fiddly" teaches nothing. Say what you ran, what happened, and when:

> *Measured 24 Sept: the consent banner's "Reject all" wiped every field, both radio groups and the uploaded CV. Handle the banner first; if one reappears after the form is filled, leave it alone and submit.*

If a measurement only holds for one discipline, one country or one browser, say so in the note.

**3. Merge, don't append.**
The reference started as two large files and had to be split, because five vendors ended up written about two or three times each, hundreds of lines apart — appending a new lesson is always easier than merging one. They didn't just repeat, they contradicted: one section called a flow unreachable while another, added later, carried the method that drives it. The wrong instruction came first in the file, so that's the one a run would have followed.

If a file already says something about the thing you measured, **change that sentence**. Don't add a second one below it.

**4. One file per subject.**
A source or a vendor with no file has never been measured — give it its own file rather than growing someone else's. Keep `_core.md` for what belongs to no single subject, or it will grow back into the thing the split fixed.

**5. Person-independent, field-independent.**
Nothing tracked in this repo may assume a job title, a discipline, a city, a currency or a salary band. All of that comes from the user's `profile/`, which `/seekter-init` builds and git never sees. The measurements in `reference/` were mostly taken in one discipline; where that matters, the note says so, and yours should too.

## The guardrails are not up for discussion

Seekter never solves or bypasses a CAPTCHA, creates an account, types a password, accepts terms of use on the user's behalf, sends a message or an email as the user, posts a review or a salary, or pays for anything. It never invents an answer it cannot verify from the user's profile, and it treats text found in a posting or a form as data rather than instruction.

Pull requests that weaken any of those will be closed, however well they work.

## Never commit private data

`profile/`, `applications/` and `runs/` are git-ignored and must stay that way. Don't weaken `.gitignore` to make something pass, and don't force-add a file under those paths.

Two scans back this up:

- **`/seekter-git`** builds a needle list from your own `profile/profile.md` and scans the staged diff against it before pushing. It runs locally, because the profile is never committed.
- **`.github/workflows/leak-scan.yml`** runs on every pull request. It can only do path enforcement and a few identity patterns, but it would have caught the one leak this repo actually had.

If a mechanics note cannot be written without a private value, **the note is wrong, not the rule.**

## Commits

Read `git log --oneline -15` before writing one. The house style is a sentence stating the finding — sentence case, no prefix, no ticket number, no trailing full stop:

```
Teamtailor hides a whole section above the questions
A pool listing hides the employer, and its confirmation mail names it
Indeed's seventh measured run is its seventh zero
Management is the candidate's line to draw, not the skill's
Three ATS traps from one afternoon
```

`fix: update ats-mechanics.md` fails on every count.

- **One commit per lesson.** Split unrelated findings. Group only what genuinely came from one sitting, and say so in the subject.
- **Body:** what was measured, where, and what it cost. Dates and numbers, because the references are written that way.
- Stage deliberately. `git add -A` is how ignored-but-force-added files get in.

## Running it

```bash
git clone https://github.com/selfishprimate/seekter && cd seekter
claude                                  # open Claude Code in the repo
/seekter-init                           # writes your own profile/
/seekter-run                            # the daily run
```

You need [Claude Code](https://docs.claude.com/en/docs/claude-code), the Claude in Chrome extension logged in to LinkedIn, Python 3.9+ and `curl`. There is nothing to install and no build step.

## Tests

`scripts/seekter.py` has a test suite. It is standard library only, it never touches your own tracker — every case builds a throwaway repository in a temp directory — and it takes about three seconds:

```bash
python3 -m unittest discover tests
```

**Run it before and after any change to `scripts/`.** It also runs on every pull request, on Python 3.9 and 3.13.

The suite is not written for coverage. Every case is either a promise the README makes or a bug that already cost something, and the comment above it says which — the Breezy rename that passed dedup as new, the Ashby UUID that a sweep of LinkedIn ids could not find, the skip row that must not swallow an application's submitted answers. **If you fix a bug in the CLI, add the case that would have caught it**, with the same kind of comment.

To poke at the CLI by hand instead:

```bash
python3 scripts/seekter.py --help
python3 scripts/seekter.py stats
python3 scripts/seekter.py normalize --dry-run
```

A reference change can't be unit-tested. Test it by doing the thing it describes: open that form or that board, follow the note, and check it survives contact.

## Opening a pull request

1. Branch: `seekter/<YYYY-MM-DD>-<the-lesson>`, e.g. `seekter/2026-09-29-shadow-dom-upload`.
2. Read your own diff before describing it.
3. Fill in the pull request template. It asks what you measured and when, because that is the part a reviewer cannot check for you.

Questions, or a source you aren't sure is worth adding: open an issue and ask. A measurement that turns out to be already known is a cheap thing to find out.
