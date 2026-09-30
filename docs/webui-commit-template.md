# Web UI commit & PR templates

The repo-level `.github/pull_request_template.md` (upstream) asks what changed, what was
measured and runs the guardrail checklist. For the Web UI wrapper, use the templates below;
every commit and PR description is built from them, nothing improvised in the terminal.

## Commit template (`docs/webui-commit-template.md`)

```
<area>: <statement of what the UI can now do, not a file list>

<body>
- The path a user takes in the UI (route + action), in one sentence.
- The seekter command(s) the server runs for it, and the exit-code contract kept.
- What was exercised by hand at the time of the commit (route opened, action clicked,
  file written), with the visible result.

refs: /seekter-<command>
```

Rules:

- Subject: `<area>: <what it now does>`, lowercase after the colon, no WIP, no file lists.
  Areas used by the Web UI: `webui-server`, `webui-dashboard`, `webui-tracker`,
  `webui-sweep`, `webui-report`, `webui-docs`, `webui-tests`.
- One concern per commit. A fix to a line shipped in the same session goes in its own commit.
- Never write personal data (companies, titles, cities, salaries, URLs you applied through)
  into the message: use the placeholder spellings, `<COMPANY>`, `<ROLE>`, `<CITY>`.

## PR template (extends `.github/pull_request_template.md`)

```markdown
## What changed
<wraps around the whole Web UI slice>

## What you measured
- `python3 -m unittest discover tests` — date, number of tests, pass/fail.
- Server smoke: routes opened by hand (list them), actions clicked (list them),
  and the command each one ran, with the observed output.
- Browser smoke: which pages in `ui/` were opened, screenshot list, and the date.

## Checks
- [x] Guardrails untouched: no CAPTCHA solving, no account creation, no passwords,
      no accepting terms, no sending messages as the user, no invented answers.
      The Web UI only drives the CLI and reads tracked files; it never fills a form.
- [ ] No personal data in the diff (`profile/`, `applications/`, `runs/` stay untracked;
      `.gitignore` unchanged; screenshots contain a dry-run profile only).
- [ ] `python3 -m unittest discover tests` passes.
- [ ] Server binds to 127.0.0.1 by default; the README says how to change it and to keep it local.
- [ ] The diff does not restate README sentences elsewhere; linked instead.
```

## Branch layout used for the Web UI work

| Branch | Contains | Lands in |
|---|---|---|
| `webui-server` | `scripts/webui.py` (API + job runner), `docs/webui-commit-template.md` | PR #1 |
| `webui-ui` | `ui/` (dashboard, tracker, sweep, report screens) | PR #2 on top of #1 |
| `webui-docs` | README sections + screenshots, template files | PR #3 |

Each PR body embeds the checklist above, verbatim, and is merged only when its own
test run line is in place. `main` keeps upstream history: fast-forward merges only,
no force pushes.

## Upstream contributions to `selfishprimate/seekter` (learned on PR #13)

Upstream closed the wrapper PR with praise and a reason that was policy, not code:
"too early for a web surface". What the review cared about, in order: the CONTRIBUTING
format followed line by line, measurements with dates, the guardrail checklist checked
honestly. Two things to remember for the next one:

- Upstream branch naming does not follow the Web UI style: use
  `seekter/<YYYY-MM-DD>-<the-lesson>` (CONTRIBUTING documents it), and squash the Web UI's
  prefixed commits into one sentence-case, prefix-free commit ("The daily loop runs from
  a browser now"), no trailing full stop.
- Checks on a branch from a fork need the maintainer's approval in their repo settings,
  so they may show "no checks" even when the suite passed locally. Carry the test counts
  (suite name, size, date) in the PR description so the branch does not look untested.

The real upstream contribution path is `reference/`: Jobvite, Zoho Recruit, Comeet and
Cornerstone (and the account walls named in `reference/ats/_core.md`) have never been
measured. A measurement means a real run through that system, so plan them for when
actual applications go through those vendors; do not write notes that were not lived.