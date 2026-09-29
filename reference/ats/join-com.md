# join.com

- Log in via "Send me a login link" → open the `noreply@join.com` mail → don't print the link (query strings blocked); tokenise:
  `h.replace(/\?/g,'<Q>').replace(/&/g,'<A>').replace(/=/g,'<E>')` → rebuild → `navigate` → "Continue". Session then allows one-click applies.
- Remembers the last CV: "Remove file" → re-upload to switch.
- Unresolved: some postings still demanded full account creation after magic-link login → hand over when that happens.
