#!/usr/bin/env python3
"""Seekter tracker CLI. Standard library only.

Layout: applications/<YYYY-MM>/ holds one markdown file per posting (status in the front
matter; files never move) plus skipped.md, one table row per posting that was passed over.
applications/README.md and applications/<YYYY-MM>/README.md are generated views.

  python3 scripts/seekter.py check <url> [--company NAME]
  printf 'url | company\n4468710729\n' | python3 scripts/seekter.py check-many   (bare numbers = LinkedIn IDs)
  python3 scripts/seekter.py add --company X --role Y --status applied --url U [...]
  python3 scripts/seekter.py move <file|url> <status> [--note TEXT]
  python3 scripts/seekter.py list [--status S] [--since YYYY-MM-DD]
  python3 scripts/seekter.py index
  python3 scripts/seekter.py normalize [--dry-run]
  python3 scripts/seekter.py stats [--since YYYY-MM-DD]
  python3 scripts/seekter.py migrate [--keep-old]         (v1 status folders -> month folders)
"""
import argparse, datetime as dt, json, os, re, sys, unicodedata
from pathlib import Path
from urllib.parse import urlparse, parse_qs

ROOT = Path(__file__).resolve().parent.parent
APPS = ROOT / "applications"
STATUSES = ["pending", "applied", "interviewing", "offer", "rejected", "closed", "skipped"]
FIELDS = ["company", "role", "status", "url", "source", "ats", "apply_type", "location_fit",
          "remote_scope", "fit", "posted", "applied", "updated", "job_key"]
TODAY = dt.date.today().isoformat()

UUID = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"


# ---------- job identity ----------
def job_key(url: str) -> str:
    """Stable identity for a posting, so the same job reached through different URLs matches."""
    if not url:
        return ""
    u = url.strip()
    p = urlparse(u if "://" in u else "https://" + u)
    host = p.netloc.lower().removeprefix("www.")
    q = parse_qs(p.query)
    path = p.path
    m = re.search(r"/jobs/view/(\d+)", path)
    if "linkedin.com" in host and m:
        return f"linkedin:{m.group(1)}"
    if "linkedin.com" in host and "currentJobId" in q:
        return f"linkedin:{q['currentJobId'][0]}"
    for k in ("gh_jid", "token"):
        if k in q and q[k][0].isdigit():
            return f"greenhouse:{q[k][0]}"
    if "ats_id" in q:
        return f"ats:{q['ats_id'][0].lower()}"
    # Same trap as Indeed below, but on company careers sites: the posting id lives in a
    # generic query param (?jobId=, ?gh_src=..., ?requisitionId=) and the path is identical
    # for every opening, so without this every Celonis/Workday-style posting collapses to
    # "<host>/job-detail" and the first one tracked makes all the others look like duplicates.
    # Measured 24 Sept: careers.celonis.com had two design roles that keyed identically.
    for k in ("jobid", "job_id", "requisitionid", "reqid", "posting_id", "postingid", "vacancyid"):
        for qk, qv in q.items():
            if qk.lower() == k and qv and re.fullmatch(r"\d{4,}", qv[0]):
                return f"{host}:{qv[0]}"
    # Indeed keeps the posting id in the query string (?jk=, ?vjk= on a search page).
    # Without this, every posting on a domain collapses to "<host>/viewjob" and the
    # first one tracked makes all the others look like duplicates.
    if "indeed." in host:
        for k in ("jk", "vjk"):
            if q.get(k):
                return f"indeed:{q[k][0].lower()}"
    # Breezy slugs are "<position_id>-<title-slug>", and the employer can rename a posting
    # without opening a new one. Keying on the whole path makes a rename look like a brand
    # new job. Measured 25 Sept: Cal.com's ff94f3182ac2 was applied to on 18 Sept as
    # "senior-product-designer", was re-read today as "senior-product-design-engineer",
    # passed dedup as NEW, and only Breezy's own server caught it ("It looks like maybe
    # you've already applied to this job?") after the form was filled. Key on the id alone.
    if "breezy.hr" in host:
        m = re.search(r"/p/([0-9a-f]{8,})", path, re.I)
        if m:
            return f"breezy:{m.group(1).lower()}"
    m = re.search(UUID, path, re.I)
    if m:
        return f"uuid:{m.group(0).lower()}"
    if "greenhouse" in host:
        m = re.search(r"/jobs/(\d+)", path)
        if m:
            return f"greenhouse:{m.group(1)}"
    m = re.search(r"/(\d{7,})(?:[-/]|$)", path)
    if m:
        return f"{host}:{m.group(1)}"
    path = re.sub(r"/(application|apply|apply/)?$", "", path.rstrip("/"))
    # A URL with no path would key on the host alone, which makes every posting on
    # that site one record. Fall back to the fragment, then to the query.
    if not path:
        tail = p.fragment or p.query
        if tail:
            return f"{host}#{tail}".lower()
    return f"{host}{path}".lower()


ATS_HOSTS = [
    ("ashbyhq.com", "ashby"), ("greenhouse.io", "greenhouse"), ("lever.co", "lever"),
    ("myworkdayjobs.com", "workday"), ("workable.com", "workable"), ("recruitee.com", "recruitee"),
    ("personio.", "personio"), ("teamtailor.com", "teamtailor"), ("smartrecruiters.com", "smartrecruiters"),
    ("bamboohr.com", "bamboohr"), ("pinpointhq.com", "pinpoint"), ("breezy.hr", "breezy"),
    ("rippling.com", "rippling"), ("icims.com", "icims"), ("taleo.net", "taleo"), ("join.com", "join"),
    ("homerun.co", "homerun"), ("hire.trakstar.com", "trakstar"), ("jobylon.com", "jobylon"),
    ("hr-on.com", "hr-on"), ("dayforcehcm.com", "dayforce"), ("successfactors", "successfactors"),
    ("docs.google.com/forms", "google-forms"), ("forms.gle", "google-forms"),
    ("linkedin.com", "linkedin"), ("djinni.co", "djinni"),
]
# Values that are an application system, not a place the posting was found.
ATS_NAMES = {v for _, v in ATS_HOSTS} - {"linkedin", "djinni"}


def ats_from_url(url: str) -> str:
    u = (url or "").lower()
    for host, name in ATS_HOSTS:
        if host in u:
            return name
    return ""


def norm(v: str) -> str:
    """'Company site' -> 'company-site', 'Other board' -> 'other-board'."""
    return re.sub(r"[^a-z0-9]+", "-", (v or "").strip().lower()).strip("-")


# NFKD folds a letter to ASCII only when it decomposes into a base letter plus a
# combining mark. A letter that is its own base character has no decomposition, so
# `encode("ascii", "ignore")` deletes it outright: Turkish ı, Polish ł, Nordic ø/æ,
# Croatian đ, German ß and Icelandic þ/ð all vanish, so a Turkish employer name
# reached a filename as "tasarm" instead of "tasarim". `slug` is also what the
# same-company check compares, so two different employers could fold onto one
# string: "Işık" and "Isk" both became "isk".
FOLD = str.maketrans({"ı": "i", "İ": "I", "ł": "l", "Ł": "L", "ø": "o", "Ø": "O",
                      "đ": "d", "Đ": "D", "ð": "d", "Ð": "D", "ß": "ss",
                      "æ": "ae", "Æ": "AE", "œ": "oe", "Œ": "OE", "þ": "th", "Þ": "TH"})


def slug(s: str, n: int = 40) -> str:
    s = unicodedata.normalize("NFKD", (s or "").translate(FOLD)).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return s[:n].rstrip("-") or "x"


# ---------- storage ----------
# applications/<YYYY-MM>/<date>--<company>--<role>.md   one file per posting that isn't a skip;
#                                                      status lives in the front matter, files never move
# applications/<YYYY-MM>/skipped.md                    one table row per skipped posting
MONTH_RE = re.compile(r"^\d{4}-\d{2}$")
SKIP_COLS = ["Date", "Company", "Role", "Reason", "Source", "Link", "Key"]


def month_of(date: str) -> str:
    return (date or TODAY)[:7]


def month_dirs():
    if not APPS.is_dir():
        return []
    return sorted(d for d in APPS.iterdir() if d.is_dir() and MONTH_RE.match(d.name))


def read(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    meta, body = {}, text
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end != -1:
            for line in text[4:end].splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip()
            body = text[end + 4:].lstrip("\n")
    meta["_path"] = path
    meta["_body"] = body
    meta["_kind"] = "file"
    return meta


def write(path: Path, meta: dict, body: str) -> None:
    lines = ["---"]
    for k in FIELDS:
        if meta.get(k) not in (None, ""):
            lines.append(f"{k}: {str(meta[k]).replace(chr(10), ' ')}")
    for k, v in meta.items():
        if k not in FIELDS and not k.startswith("_") and v not in (None, ""):
            lines.append(f"{k}: {str(v).replace(chr(10), ' ')}")
    lines.append("---")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n\n" + body.rstrip() + "\n", encoding="utf-8")


def _cell(v: str) -> str:
    """One table cell. Idempotent: an already-escaped pipe is not escaped again,
    otherwise a value round-tripping through the table grows a backslash each pass."""
    s = re.sub(r"\s+", " ", str(v or "")).strip()
    return s.replace("\\|", "|").replace("|", "\\|")


def _split_row(line: str):
    parts = re.split(r"(?<!\\)\|", line.strip().strip("|"))
    return [p.strip().replace("\\|", "|") for p in parts]


def read_skips(path: Path):
    out = []
    if not path.exists():
        return out
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
        if not line.startswith("| ") or line.startswith("| Date |"):
            continue
        cells = _split_row(line)
        if len(cells) < len(SKIP_COLS):
            continue
        d = dict(zip(SKIP_COLS, cells))
        url = d["Link"].strip("<>")
        # `ats` has no column of its own: it is a pure function of the URL, so it is
        # derived on read. Without it every row would look unnormalised on every pass.
        out.append(dict(updated=d["Date"], company=d["Company"], role=d["Role"], notes=d["Reason"],
                        source=d["Source"], url=url, job_key=d["Key"] or job_key(url), status="skipped",
                        ats=ats_from_url(url), _path=path, _kind="row", _line=n, _body=""))
    return out


def write_skips(path: Path, recs) -> None:
    recs = sorted(recs, key=lambda r: (r.get("updated", ""), r.get("company", "").lower()))
    lines = [f"# Skipped · {path.parent.name}", "",
             "Postings looked at and not applied to, with the reason. Written by `scripts/seekter.py`; "
             "dedup reads the Key column, so a posting here is never evaluated twice.", "",
             "| " + " | ".join(SKIP_COLS) + " |", "|" + "---|" * len(SKIP_COLS)]
    for r in recs:
        link = f"<{r['url']}>" if r.get("url") else ""
        lines.append("| " + " | ".join(_cell(x) for x in (
            r.get("updated", ""), r.get("company", ""), r.get("role", ""), r.get("notes", ""),
            r.get("source", ""), link, r.get("job_key", ""))) + " |")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def all_apps():
    for d in month_dirs():
        for f in sorted(d.glob("*.md")):
            if f.name in ("skipped.md", "README.md"):
                continue
            yield read(f)
        yield from read_skips(d / "skipped.md")


def label(r) -> str:
    p = r["_path"].relative_to(ROOT).as_posix()
    return p + (f" (row: {r.get('company')})" if r["_kind"] == "row" else "")


def find(target: str):
    p = Path(target).expanduser()
    if not p.is_absolute():
        p = (Path.cwd() / p) if (Path.cwd() / p).is_file() else (ROOT / p)
    if p.is_file() and p.name != "skipped.md":
        return read(p.resolve())
    key = job_key(target)
    for a in all_apps():
        if a.get("job_key") == key or job_key(a.get("url", "")) == key:
            return a
    return None


def new_file_path(date: str, company: str, role: str) -> Path:
    name = f"{date}--{slug(company, 30)}--{slug(role, 40)}.md"
    path = APPS / month_of(date) / name
    i = 2
    while path.exists():
        path = path.with_name(name.replace(".md", f"-{i}.md"))
        i += 1
    return path


def body_for(role, company, why="", notes="", answers="", log=""):
    return (f"# {role} · {company}\n\n## Why it fits\n\n{why}\n\n## Notes\n\n{notes}\n\n"
            f"## Answers submitted\n\n{answers}\n\n## Log\n\n{log}\n")


def save(meta: dict, body: str = "", log: str = ""):
    """Store a new record in the right place for its status. Returns the path written."""
    fix_meta(meta)
    date = meta.get("applied") or meta.get("updated") or TODAY
    if meta["status"] == "skipped":
        path = APPS / month_of(date) / "skipped.md"
        recs = read_skips(path)
        recs.append(dict(meta, updated=meta.get("updated") or date))
        write_skips(path, recs)
        return path
    path = new_file_path(date, meta["company"], meta["role"])
    write(path, meta, body or body_for(meta["role"], meta["company"], log=log))
    return path


def remove(r) -> None:
    if r["_kind"] == "row":
        keep = [x for x in read_skips(r["_path"]) if x["_line"] != r["_line"]]
        write_skips(r["_path"], keep)
    else:
        r["_path"].unlink()


def section(body: str, name: str) -> str:
    m = re.search(rf"## {re.escape(name)}\n(.*?)(?=\n## |\Z)", body, re.S)
    return m.group(1).strip() if m else ""


SENT = ("applied", "interviewing", "offer", "rejected", "closed")


def keep_as_file(r) -> str:
    """Why this record must not be collapsed into a skip row, or '' if it may be.

    A skip row holds a date, a company, a role and one line of reason. That is
    the whole record for a posting that was only ever looked at. For a posting
    that was applied to, it would throw away the submitted answers, the log and
    the application date -- so those stay files, with `status: skipped`.
    """
    if r["_kind"] != "file":
        return ""
    if section(r.get("_body", ""), "Answers submitted"):
        return "it records submitted answers"
    if r.get("applied"):
        return f"it was applied to on {r['applied']}"
    if r.get("status") in SENT:
        return f"its status is '{r['status']}'"
    return ""


# ---------- normalisation ----------
def fix_meta(r: dict) -> dict:
    """Normalise one record: lowercase-hyphen enums, ATS derived from the URL,
    and an ATS name misfiled as `source` moved to `ats`."""
    before = {k: r.get(k, "") for k in ("source", "ats", "apply_type", "job_key")}
    src, ats = norm(r.get("source")), norm(r.get("ats"))
    if src == "other-board":
        src = "board"
    if src in ATS_NAMES:
        ats = ats or src
        src = "board"  # the tracker only knew the form system, not where the posting was found
    r["source"] = src
    r["ats"] = ats or ats_from_url(r.get("url", ""))
    r["apply_type"] = norm(r.get("apply_type"))
    if r.get("url") and not r.get("job_key"):
        r["job_key"] = job_key(r["url"])
    return {k: (before[k], r.get(k, "")) for k in before if before[k] != r.get(k, "")}


# ---------- commands ----------
def cmd_check(a):
    key = job_key(a.url)
    same, company = [], []
    for r in all_apps():
        if key and (r.get("job_key") == key or job_key(r.get("url", "")) == key):
            same.append(r)
        elif a.company and slug(a.company) in slug(r.get("company", ""), 80):
            company.append(r)
    if same:
        print("DUPLICATE: this posting is already tracked")
        for r in same:
            print(f"  {r.get('status')} | {r.get('company')} | {r.get('role')} | {label(r)}")
        sys.exit(1)
    print(f"NEW  key={key}")
    for r in company:
        print(f"  same company, other role: {r.get('status')} | {r.get('role')} | {r.get('applied') or r.get('updated')}")


def cmd_check_many(a):
    """stdin: one posting per line, 'url' or 'url | company'. Prints NEW / DUP / SAMECO per line."""
    apps = list(all_apps())
    keys = {r.get("job_key") or job_key(r.get("url", "")): r for r in apps}
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        url, _, co = (x.strip() for x in line.partition("|"))
        if url.isdigit():
            url = f"https://www.linkedin.com/jobs/view/{url}/"
        r = keys.get(job_key(url))
        if r:
            print(f"DUP    {line} -> {r.get('status')} {label(r)}")
            continue
        same = [x for x in apps if co and slug(co) in slug(x.get("company", ""), 80)]
        print(("SAMECO " if same else "NEW    ") + line + (f" -> {len(same)} earlier: " + ", ".join(f"{x.get('status')}:{x.get('role')}" for x in same[:3]) if same else ""))


def cmd_add(a):
    if a.status not in STATUSES:
        sys.exit(f"status must be one of {STATUSES}")
    key = job_key(a.url or "")
    if key and not a.force:
        for r in all_apps():
            if r.get("job_key") == key:
                sys.exit(f"DUPLICATE: {label(r)} (use --force to add anyway)")
    today = a.date or TODAY
    meta = dict(company=a.company, role=a.role, status=a.status, url=a.url, source=a.source, ats=a.ats,
                apply_type=a.apply_type, location_fit=a.location_fit, remote_scope=a.remote_scope, fit=a.fit,
                posted=a.posted, applied=a.applied or (today if a.status == "applied" else ""),
                updated=today, job_key=key)
    if a.status == "skipped":
        meta["notes"] = a.notes or a.why
        path = save(meta)
    else:
        log = f"- {today}: {a.status}" + (f". {a.log}" if a.log else "")
        path = save(meta, body_for(a.role, a.company, a.why, a.notes, a.answers, log))
    print(path.relative_to(ROOT))
    if not a.no_index:
        cmd_index(None, quiet=True)


def cmd_move(a):
    if a.status not in STATUSES:
        sys.exit(f"status must be one of {STATUSES}")
    r = find(a.target)
    if not r:
        sys.exit("not found")
    note = f"- {TODAY}: {a.status}" + (f". {a.note}" if a.note else "")
    if r["_kind"] == "row" and a.status == "skipped":
        if not a.note:
            print("already skipped: " + label(r)); return
        # Re-annotating a skip is the only way to correct a reason that turned out to be
        # wrong, because the tracker is CLI-only and hand-editing the table is forbidden.
        # Keep the original reason and append the correction after it, dated, so the
        # record shows both what was decided and why it changed.
        remove(r)
        meta = {k: v for k, v in r.items() if not k.startswith("_")}
        meta.update(status="skipped", updated=TODAY,
                    notes=" ".join(x for x in (r.get("notes", ""), f"[{TODAY}] {a.note}") if x))
        path = save(meta)
        print(path.relative_to(ROOT))
        cmd_index(None, quiet=True)
        return
    if r["_kind"] == "row":
        # a skip turned into something else: it gets its own file
        remove(r)
        meta = {k: v for k, v in r.items() if not k.startswith("_")}
        reason = meta.pop("notes", "")
        meta.update(status=a.status, updated=TODAY)
        if a.status == "applied":
            meta["applied"] = TODAY
        path = save(meta, body_for(meta["role"], meta["company"], notes=f"Skipped earlier: {reason}",
                                   log=f"- {r.get('updated')}: skipped\n{note}"))
    elif a.status == "skipped":
        meta = {k: v for k, v in r.items() if not k.startswith("_")}
        keep = keep_as_file(r)
        if keep:
            # Collapsing this to a table row would drop the answers, the reasoning
            # and the dates, and `--answers` is what makes "no sentence twice"
            # checkable. A skip that was once a real application stays a file.
            body = r["_body"]
            meta.update(status="skipped", updated=TODAY)
            if "## Log" not in body:
                body += "\n## Log\n"
            write(r["_path"], meta, body.rstrip() + "\n" + note + "\n")
            path = r["_path"]
            print(f"kept as a file rather than a skip row: {keep}", file=sys.stderr)
        else:
            remove(r)
            meta.update(status="skipped", updated=TODAY,
                        notes=" ".join(x for x in (a.note, section(r["_body"], "Notes")) if x))
            path = save(meta)
    else:
        path, body = r["_path"], r["_body"]
        meta = {k: v for k, v in r.items() if not k.startswith("_")}
        meta.update(status=a.status, updated=TODAY)
        if a.status == "applied" and not meta.get("applied"):
            meta["applied"] = TODAY
        if "## Log" not in body:
            body += "\n## Log\n"
        write(path, meta, body.rstrip() + "\n" + note + "\n")
    print(path.relative_to(ROOT))
    cmd_index(None, quiet=True)


def rows(since=None, status=None):
    out = []
    for r in all_apps():
        d = r.get("applied") or r.get("updated") or ""
        if since and d < since:
            continue
        if status and r.get("status") != status:
            continue
        out.append(r)
    out.sort(key=lambda r: (r.get("applied") or r.get("updated") or ""), reverse=True)
    return out


def cmd_list(a):
    for r in rows(a.since, a.status):
        print(f"{r.get('applied') or r.get('updated')} | {r.get('status'):<12} | {r.get('company')} | {r.get('role')} | {r.get('url','')}")


def counts(rs):
    c = {s: 0 for s in STATUSES}
    for r in rs:
        c[r.get("status") or "pending"] = c.get(r.get("status") or "pending", 0) + 1
    return c, sum(c[s] for s in SENT)


def cmd_stats(a):
    c, sent = counts(rows(a.since))
    print(json.dumps({"total": sum(c.values()), "sent": sent, **c,
                      "response_rate": round((c["interviewing"] + c["offer"] + c["rejected"]) / sent, 3) if sent else None},
                     indent=1))


def cmd_normalize(a):
    files = rows_changed = 0
    for d in month_dirs():
        recs = read_skips(d / "skipped.md")
        # every record, not `any(...)`: that short-circuits on the first change
        # and leaves the rest of the table unnormalised.
        hits = sum(1 for r in recs if fix_meta(r))
        if hits:
            rows_changed += hits
            if not a.dry_run:
                write_skips(d / "skipped.md", recs)
        for f in sorted(d.glob("*.md")):
            if f.name in ("skipped.md", "README.md"):
                continue
            r = read(f)
            path, body = r.pop("_path"), r.pop("_body")
            r.pop("_kind")
            if fix_meta(r):
                files += 1
                if not a.dry_run:
                    write(path, r, body)
    verb = "would change" if a.dry_run else "normalised"
    print(f"{files} files and {rows_changed} skip rows {verb}")


def _link(r, base: Path):
    if r["_kind"] == "row":
        return r.get("role", "")
    return f"[{r.get('role','')}]({r['_path'].relative_to(base).as_posix()})"


def _table(rs, base, cols=("Date", "Company", "Role", "Status", "Fit", "Posting")):
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for r in rs:
        vals = {"Date": r.get("applied") or r.get("updated", ""), "Company": _cell(r.get("company")),
                "Role": _link(r, base), "Status": r.get("status", ""), "Fit": r.get("location_fit", ""),
                "Posting": f"[link]({r['url']})" if r.get("url") else "",
                "Next step": _cell(section(r.get("_body", ""), "Notes"))[:160]}
        out.append("| " + " | ".join(vals[c] for c in cols) + " |")
    return out


def cmd_index(a, quiet=False):
    rs = rows()
    since30 = (dt.date.today() - dt.timedelta(days=30)).isoformat()
    lines = ["# Applications", "", f"Generated by `scripts/seekter.py` on {TODAY}. Don't edit by hand.", ""]
    pend = [r for r in rs if r.get("status") == "pending"]
    live = [r for r in rs if r.get("status") in ("interviewing", "offer")]
    recent = [r for r in rs if r.get("status") in ("applied", "rejected", "closed") and (r.get("applied") or r.get("updated", "")) >= since30]
    lines += [f"## Needs you ({len(pend)})", "", "Forms waiting for a CAPTCHA, an account, a decision or an answer only you have.", ""]
    lines += _table(pend, APPS, ("Date", "Company", "Role", "Next step")) if pend else ["Nothing."]
    lines += ["", f"## In progress ({len(live)})", ""]
    lines += _table(live, APPS) if live else ["Nothing yet."]
    lines += ["", f"## Sent in the last 30 days ({len(recent)})", ""]
    lines += _table(recent, APPS) if recent else ["Nothing."]
    lines += ["", "## By month", "", "| Month | Sent | Replies | Interviewing / offer | Pending | Skipped |", "|---|---|---|---|---|---|"]
    for d in reversed(month_dirs()):
        mr = [r for r in rs if r["_path"].parent == d]
        c, sent = counts(mr)
        lines.append(f"| [{d.name}]({d.name}/README.md) | {sent} | {c['rejected'] + c['interviewing'] + c['offer']} | "
                     f"{c['interviewing'] + c['offer']} | {c['pending']} | [{c['skipped']}]({d.name}/skipped.md) |")
        # per-month page
        ml = [f"# {d.name}", "", f"Generated by `scripts/seekter.py` on {TODAY}.", "",
              " · ".join(f"**{s}** {c[s]}" for s in STATUSES if c[s]), ""]
        files = [r for r in mr if r["_kind"] == "file"]
        ml += _table(files, d) if files else ["No applications this month."]
        ml += ["", f"Skipped postings ({c['skipped']}): [skipped.md](skipped.md)", ""]
        (d / "README.md").write_text("\n".join(ml), encoding="utf-8")
    c, sent = counts(rs)
    lines += ["", f"All time: **{sent} sent** · " + " · ".join(f"{s} {c[s]}" for s in STATUSES if c[s]), ""]
    APPS.mkdir(exist_ok=True)
    (APPS / "README.md").write_text("\n".join(lines), encoding="utf-8")
    if not quiet:
        print(f"applications/README.md ({len(rs)} records, {len(month_dirs())} months)")


def cmd_migrate(a):
    """Move a v1 tracker (applications/<status>/*.md) to the month layout."""
    old = [APPS / s for s in STATUSES if (APPS / s).is_dir()]
    if not old:
        sys.exit("nothing to migrate: no applications/<status>/ folders")
    n_files = n_rows = 0
    for d in old:
        for f in sorted(d.glob("*.md")):
            r = read(f)
            body = r.pop("_body"); r.pop("_path"); r.pop("_kind")
            r["status"] = r.get("status") or d.name
            if r["status"] == "skipped":
                r["notes"] = section(body, "Notes") or section(body, "Why it fits")
                save(r)
                n_rows += 1
            else:
                date = r.get("applied") or r.get("updated") or f.name[:10]
                path = APPS / month_of(date) / f.name
                fix_meta(r)
                write(path, r, body)
                n_files += 1
            if not a.keep_old:
                f.unlink()
        if not a.keep_old:
            try:
                d.rmdir()
            except OSError:
                pass
    cmd_index(None)
    print(f"migrated {n_files} files and {n_rows} skip rows" + (" (old folders kept)" if a.keep_old else ""))


def main():
    ap = argparse.ArgumentParser(description="Seekter tracker")
    sp = ap.add_subparsers(dest="cmd", required=True)
    c = sp.add_parser("check"); c.add_argument("url"); c.add_argument("--company")
    c.set_defaults(fn=cmd_check)
    cm = sp.add_parser("check-many"); cm.set_defaults(fn=cmd_check_many)
    ad = sp.add_parser("add")
    for f in ("company", "role", "url"):
        ad.add_argument("--" + f, required=f != "url", default="")
    ad.add_argument("--status", default="applied")
    for f in ("source", "ats", "apply-type", "location-fit", "remote-scope", "fit", "posted", "applied",
              "date", "why", "notes", "answers", "log"):
        ad.add_argument("--" + f, default="")
    ad.add_argument("--force", action="store_true")
    ad.add_argument("--no-index", action="store_true", help="skip regenerating the README index (bulk adds)")
    ad.set_defaults(fn=cmd_add)
    mv = sp.add_parser("move"); mv.add_argument("target"); mv.add_argument("status"); mv.add_argument("--note", default="")
    mv.set_defaults(fn=cmd_move)
    ls = sp.add_parser("list"); ls.add_argument("--status"); ls.add_argument("--since"); ls.set_defaults(fn=cmd_list)
    ix = sp.add_parser("index"); ix.set_defaults(fn=cmd_index)
    nm = sp.add_parser("normalize", help="lowercase enums, derive ats from url, fix ats-in-source")
    nm.add_argument("--dry-run", action="store_true"); nm.set_defaults(fn=cmd_normalize)
    st = sp.add_parser("stats"); st.add_argument("--since"); st.set_defaults(fn=cmd_stats)
    mg = sp.add_parser("migrate", help="convert applications/<status>/ folders to applications/<YYYY-MM>/")
    mg.add_argument("--keep-old", action="store_true"); mg.set_defaults(fn=cmd_migrate)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
