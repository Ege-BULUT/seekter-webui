# Security

Seekter is an agent that drives your own logged-in browser, reads your inbox, and holds your contact details, salary bands and CVs on disk. The interesting security questions here are not about a server, because there isn't one.

## Reporting a vulnerability

**Open a [private security advisory](https://github.com/selfishprimate/seekter/security/advisories/new).** Please don't open a public issue for anything in the list below.

Tell me what you did, what happened, and what it would have cost a real user. A working example — a posting, a form, a diff — is worth more than a description. You'll get an acknowledgement within a few days; this is a one-person project, so please be patient with the fix.

## What counts

**Prompt injection through a job posting or a form.** This is the one that matters most. Seekter reads untrusted text all day: descriptions, form labels, help text, confirmation pages. It is built to treat all of it as data, never as instruction, and to report postings that carry hidden directions to AI readers rather than follow them.

If you find a shape of text that gets past that — something in a posting or a form that changes what the agent does, makes it fill a field it shouldn't, send something, follow a link, or reveal part of the user's profile — that is a security report, not a bug report. Include the text verbatim.

**A path for private data to reach the public repository.** `profile/`, `applications/` and `runs/` are git-ignored, and `/seekter-git` plus the CI leak scan check the staged diff for identity values. If you find a way for a name, an email address, a phone number or a CV to be committed anyway — a reference note that quotes one, a script that writes outside the ignored paths, a scan that can be walked past — report it.

**Anything that crosses a guardrail.** Seekter must never solve or bypass a CAPTCHA, create an account, type a password, accept terms of use for the user, send a message or an email as the user, post a review or a salary, or pay for anything. A way to make it do one of those is a vulnerability, even if it takes an unusual posting to trigger.

**Anything that acts outside the task.** The agent has a real browser session with real logins. A path that gets it to act on an account beyond filling the application in front of it — changing settings, deleting mail, posting, authorising an app — counts.

**A way to make it submit something untrue.** Seekter refuses to invent an answer it cannot verify from the profile. A route that gets a guessed date of birth, salary, or work-authorisation answer into a submitted form is a real problem: the person, not the tool, signs that declaration.

## What doesn't count

- **That it fills in forms at all.** That is the product.
- **That it uses your logged-in browser session.** That is the design; the alternative is handing credentials to a server, which this project will not do.
- **Rate limits, terms of service, or bot detection on a job board.** Seekter does not evade detection and will not accept changes that do. If a source blocks automation, the answer is to stop using that source, and there's a file for that: `reference/sources/dead-and-low-value.md`.
- **Anything requiring an attacker who already has your machine or your unlocked browser.** At that point your inbox is theirs regardless.

## What the design gives you

- **No server, no account, no telemetry.** Everything runs on your machine. Your profile and tracker never leave it unless you commit them, and `.gitignore` is set up so you don't do that by accident.
- **No dependencies.** Python 3.9+ standard library and `curl`. There is nothing to `pip install`, which means there is no dependency chain to compromise. Keep it that way; a pull request adding a package needs a very good reason.
- **Nothing tracked assumes a person.** Every personal value comes from `profile/`, which git never sees. See `CONTRIBUTING.md` for how that is enforced.
- **The agent stops rather than guesses.** A mandatory question with no truthful answer available becomes a hand-off in the **Needs you** table, not a plausible-looking answer.

## If you use Seekter

- Keep `profile/`, `applications/` and `runs/` out of version control. If you want your tracker versioned, use a separate private repository rather than removing the ignore lines here.
- Never put a password, an API key or a security answer in `profile/profile.md`. Seekter doesn't type passwords and has no use for them.
- Read the **Needs you** table in `applications/README.md` before asking for more applications. It is where everything the agent refused to decide ends up.
- Review what went out. Every application file has an `## Answers submitted` section holding the free-text answers exactly as sent.
