#!/usr/bin/env python3
"""Seekter Web UI server. Standard library only.

Serves the ui/ single page application and a JSON API that drives the tracker
CLI (scripts/seekter.py) and the freehire sweep (scripts/freehire_sweep.py),
so the daily loop can be watched and carried out from the browser instead of
the terminal.

  python3 scripts/webui.py                  # 127.0.0.1:8770
  python3 scripts/webui.py --port 9000
  python3 scripts/webui.py --open           # open a tab after the server binds
  python3 scripts/webui.py --root <other-seekter-checkout>

Endpoints (JSON unless they serve a file):
  GET  /api/overview        funnel numbers, needs-you, last 30 days, months
  GET  /api/apps?status=&since=&q=
  GET  /api/app?path=       one record: front matter + body sections
  GET  /api/check?url=&company=
  GET  /api/runs            runs/ directories and their candidate counts
  GET  /api/run/day?date=   one day's freehire.json
  GET  /api/profile         profile/search.json + profile.md head + documents
  GET  /api/jobs            background job statuses, output so far
  GET  /api/jobs/<id>
  POST /api/check-many      {lines: ["url", "url | company", "4468710729", ...]}
  POST /api/add             the same fields the `add` subcommand takes
  POST /api/move            {target, status, note}
  POST /api/index           rebuild applications/README.md
  POST /api/normalize       {dry_run}
  POST /api/jobs/sweep      start scripts/freehire_sweep.py in the background

Mutations go through the exact functions the CLI subcommands call, so the dedup
guards, the generated index and everything else behave the same as the terminal.
The server binds to 127.0.0.1 by default; the tracker is an unencrypted local
log of the job search and never leaves the machine.
"""
import argparse
import datetime as dt
import importlib.util
import io
import json
import re
import subprocess
import sys
import threading
import time
import uuid
from contextlib import redirect_stdout
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import urlparse, parse_qs, unquote

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def load_seekter(root: Path):
    spec = importlib.util.spec_from_file_location("seekter_live", root / "scripts" / "seekter.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ----------------------------------------------------------------- module state

sk = load_seekter(ROOT)
UI = ROOT / "ui"
SWEEP_SCRIPT = HERE / "freehire_sweep.py"
JOBS = {}
JOBS_LOCK = threading.Lock()


def set_root(path: Path):
    """Drive a different seekter checkout (--root)."""
    global sk, UI
    sk = load_seekter(path)
    UI = path / "ui"


# ----------------------------------------------------------------- job runner

def start_job(argv):
    job_id = uuid.uuid4().hex[:10]
    with JOBS_LOCK:
        JOBS[job_id] = {"argv": argv, "lines": [], "status": "running", "code": None,
                        "started": time.time()}
    threading.Thread(target=_exec, args=(job_id, argv), daemon=True).start()
    return job_id


def _exec(job_id, argv):
    job = JOBS[job_id]
    try:
        p = subprocess.run([sys.executable, *argv], capture_output=True, text=True,
                           cwd=str(sk.ROOT), encoding="utf-8", errors="replace")
        for line in (p.stdout or "").splitlines():
            job["lines"].append(line)
        err = (p.stderr or "").strip()
        if err:
            job["lines"].append("[stderr] " + err)
        job["status"] = "done" if p.returncode == 0 else "failed"
        job["code"] = p.returncode
    except Exception as exc:  # noqa: BLE001 - job log is the UI's only window
        job["lines"].append(f"[error] {exc}")
        job["status"] = "failed"


# ----------------------------------------------------------------- payloads

def json_ok(payload):
    return {"ok": True, **payload}


def public(r, body=False):
    keys = ["company", "role", "status", "url", "source", "ats", "apply_type",
            "location_fit", "remote_scope", "fit", "posted", "applied", "updated",
            "job_key", "notes"]
    out = {k: r.get(k, "") for k in keys}
    out["kind"] = r.get("_kind", "")
    out["path"] = r["_path"].relative_to(sk.ROOT).as_posix() if r.get("_path") else ""
    if body:
        b = r.get("_body", "")
        out["sections"] = {n: sk.section(b, n) for n in ("Why it fits", "Notes", "Answers", "Log")}
    return out


def overview():
    rs = sk.rows()
    c, sent = sk.counts(rs)
    s30 = (dt.date.today() - dt.timedelta(days=30)).isoformat()
    months = []
    for d in reversed(sk.month_dirs()):
        mr = [x for x in rs if x["_path"].parent == d]
        mc, m_sent = sk.counts(mr)
        months.append({"month": d.name, "sent": m_sent,
                       "replies": mc["rejected"] + mc["interviewing"] + mc["offer"],
                       "live": mc["interviewing"] + mc["offer"],
                       "pending": mc["pending"], "skipped": mc["skipped"]})
    needs = []
    for r in [x for x in rs if x.get("status") == "pending"]:
        needs.append({**public(r),
                      "next_step": sk.section(r.get("_body", ""), "Notes") or r.get("notes", "")})
    cands = today_candidates()
    return {"ok": True,
            "stats": {"total": sum(c.values()), "sent": sent, **c,
                      "response_rate": (round((c["interviewing"] + c["offer"] + c["rejected"]) / sent, 3)
                                        if sent else None)},
            "statuses": sk.STATUSES, "months": months, "needs_you": needs,
            "recent": [public(x) for x in rs if (x.get("applied") or x.get("updated", "")) >= s30],
            "runs": run_days(), "swept_today": cands is not None}


def apps_list(q):
    out = []
    for r in sk.rows(q.get("since") or None, q.get("status") or None):
        out.append(public(r, body=True))
    if q.get("q"):
        probe = q["q"].lower()
        out = [x for x in out if probe in json.dumps(
            {k: x.get(k, "") for k in ("company", "role", "url", "source", "ats", "notes", "path")},
            ensure_ascii=False).lower()]
    return out


def app_detail(path):
    p = (sk.ROOT / path).resolve()
    if sk.ROOT not in p.parents or not p.exists():
        return None
    return public(sk.read(p), body=True)


def do_check(url, company):
    key = sk.job_key(url)
    same, co = [], []
    for r in sk.all_apps():
        if key and (r.get("job_key") == key or sk.job_key(r.get("url", "")) == key):
            same.append(public(r))
        elif company and sk.slug(company) in sk.slug(r.get("company", ""), 80):
            co.append(public(r))
    return {"ok": True, "state": "DUP" if same else ("SAMECO" if co else "NEW"),
            "job_key": key, "matches": same[:6], "same_co": co[:6]}


def check_many(lines):
    apps = list(sk.all_apps())
    keys = {x.get("job_key") or sk.job_key(x.get("url", "")): x for x in apps}
    res = []
    for line in lines:
        line = (line or "").strip()
        if not line:
            continue
        url, _, co = (x.strip() for x in line.partition("|"))
        if url.isdigit():
            url = f"https://www.linkedin.com/jobs/view/{url}/"
        key = sk.job_key(url)
        r = keys.get(key)
        if r:
            res.append({"line": line, "state": "DUP", "match": public(r), "key": key})
            continue
        same = [x for x in apps if co and sk.slug(co) in sk.slug(x.get("company", ""), 80)]
        res.append({"line": line, "state": "SAMECO" if same else "NEW", "key": key,
                    "url": url, "company": co, "matches": [public(x) for x in same[:3]]})
    return {"ok": True, "results": res}


def do_add(args):
    a = SimpleNamespace(**{k: (args.get(k, "") or "") for k in
                           ("company", "role", "url", "status", "source", "ats",
                            "apply_type", "location_fit", "remote_scope", "fit",
                            "posted", "applied", "date", "why", "notes", "answers", "log")})
    a.force = bool(args.get("force"))
    a.no_index = bool(args.get("no_index"))
    if a.status not in sk.STATUSES:
        return {"ok": False, "error": f"status must be one of {sk.STATUSES}"}
    out = io.StringIO()
    try:
        with redirect_stdout(out):
            sk.cmd_add(a)
    except SystemExit as e:
        return {"ok": False, "duplicate": True, "error": str(e)}
    lines = out.getvalue().strip().splitlines()
    return {"ok": True, "path": lines[-1] if lines else "", "output": out.getvalue()}


def do_move(args):
    out = io.StringIO()
    try:
        with redirect_stdout(out):
            sk.cmd_move(SimpleNamespace(target=args.get("target", ""),
                                        status=args.get("status", ""),
                                        note=args.get("note", "") or ""))
    except SystemExit as e:
        return {"ok": False, "error": str(e)}
    lines = out.getvalue().strip().splitlines()
    return {"ok": True, "path": lines[-1] if lines else "", "output": out.getvalue()}


def profile_payload():
    cfg_path = sk.ROOT / "profile" / "search.json"
    prof = sk.ROOT / "profile" / "profile.md"
    cfg = {}
    if cfg_path.exists():
        try:
            cfg = json.loads(cfg_path.read_text(encoding="utf8"))
        except Exception:
            cfg = {"_parse_error": True}
    docs = []
    docdir = sk.ROOT / "profile" / "documents"
    if docdir.is_dir():
        docs = sorted(f.name for f in docdir.iterdir() if f.is_file())
    head = prof.read_text(encoding="utf8")[:6000] if prof.exists() else ""
    missing = []
    if not str(cfg.get("title_keep", "")).strip():
        missing.append("title_keep")
    for k in ("queries", "categories"):
        if not cfg.get("freehire", {}).get(k):
            missing.append("freehire." + k)
    return {"ok": True, "search": cfg, "profile_head": head, "documents": docs,
            "has_profile": prof.exists(), "missing_values": missing}


def run_days():
    days = []
    if (sk.ROOT / "runs").is_dir():
        for d in sorted((sk.ROOT / "runs").iterdir(), reverse=True):
            f = d / "freehire.json"
            if d.is_dir() and f.exists():
                try:
                    cands = json.loads(f.read_text(encoding="utf8"))
                except Exception:
                    cands = []
                days.append({"date": d.name, "candidates": len(cands)})
    return days


def today_candidates():
    p = sk.ROOT / "runs" / sk.TODAY / "freehire.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf8"))
    except Exception:
        return None


def day_payload(date):
    p = sk.ROOT / "runs" / date / "freehire.json"
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf8"))


# ----------------------------------------------------------------- handlers

class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "seekter-webui"
    sk = sk
    ui = UI

    def log_message(self, fmt, *args):  # keep the terminal clean
        pass

    def json_out(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def file_out(self, target: Path):
        try:
            body = target.read_bytes()
        except OSError:
            return self.json_out({"ok": False, "error": "not found"}, 404)
        ctype = {".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8",
                 ".css": "text/css; charset=utf-8", ".png": "image/png",
                 ".svg": "image/svg+xml"}.get(target.suffix, "text/plain; charset=utf-8")
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def get_body(self):
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n).decode("utf8")) if n else {}

    def guard(self, fn):
        try:
            fn()
        except BrokenPipeError:
            pass
        except SystemExit as e:
            self.json_out({"ok": False, "error": str(e)}, 400)
        except Exception as e:  # noqa: BLE001 - errors reach the UI, never swallowed
            self.json_out({"ok": False, "error": f"{type(e).__name__}: {e}"}, 500)

    def do_GET(self):
        self.guard(self._get)

    def do_POST(self):
        try:
            n = int(self.headers.get("Content-Length") or 0)
            body = json.loads(self.rfile.read(n).decode("utf8")) if n else {}
            self._post(urlparse(self.path).path, body)
        except BrokenPipeError:
            pass
        except SystemExit as e:
            self.json_out({"ok": False, "error": str(e)}, 400)
        except Exception as e:  # noqa: BLE001 - errors reach the UI
            self.json_out({"ok": False, "error": f"{type(e).__name__}: {e}"}, 500)

    def _get(self):
        u = urlparse(self.path)
        q = {k: (v[0] if v else "") for k, v in parse_qs(u.query).items()}
        p = u.path
        if p.startswith("/api/"):
            return self._api_get(p, q)
        rel = "index.html" if p in ("", "/") else p.lstrip("/")
        target = (self.ui / rel).resolve()
        if not str(target).startswith(str((self.ui).resolve())) or not target.is_file():
            return self.json_out({"ok": False, "error": "not found"}, 404)
        self.file_out(target)

    def _api_get(self, p, q):
        if p == "/api/overview":
            return self.json_out(overview())
        if p == "/api/apps":
            return self.json_out({"ok": True, "rows": apps_list(q)})
        if p == "/api/app":
            rec = app_detail(unquote(q.get("path", "")))
            return self.json_out(rec if rec else {"ok": False, "error": "not found"},
                                 200 if rec else 404)
        if p == "/api/check":
            return self.json_out(do_check(q.get("url", ""), q.get("company", "")))
        if p == "/api/runs":
            return self.json_out({"ok": True, "days": run_days()})
        if p == "/api/run/day":
            date = q.get("date") or sk.TODAY
            cands = day_payload(date)
            if cands is None:
                return self.json_out({"ok": False, "error": "no sweep output for that date"}, 404)
            return self.json_out({"ok": True, "date": date, "candidates": cands})
        if p == "/api/profile":
            return self.json_out(profile_payload())
        if p == "/api/jobs":
            with JOBS_LOCK:
                jobs = {jid: {"status": x["status"], "code": x["code"], "argv": x["argv"],
                              "lines": x["lines"][-400:]} for jid, x in JOBS.items()}
            return self.json_out({"ok": True, "jobs": jobs})
        m = re.fullmatch(r"/api/jobs/([a-z0-9]+)", p)
        if m:
            with JOBS_LOCK:
                job = JOBS.get(m.group(1))
            if not job:
                return self.json_out({"ok": False, "error": "unknown job"}, 404)
            return self.json_out({"ok": True, "status": job["status"],
                                  "lines": job["lines"][-400:]})
        return self.json_out({"ok": False, "error": "unknown endpoint"}, 404)

    def _post(self, p, body):
        if p == "/api/add":
            result = do_add(body)
            return self.json_out(result, 200 if result.get("ok") else 409)
        if p == "/api/move":
            result = do_move(body)
            return self.json_out(result, 200 if result.get("ok") else 409)
        if p == "/api/check-many":
            return self.json_out(check_many(body.get("lines", [])))
        if p == "/api/index":
            out = io.StringIO()
            with redirect_stdout(out):
                sk.cmd_index(None)
            return self.json_out({"ok": True, "report": out.getvalue().strip()})
        if p == "/api/normalize":
            out = io.StringIO()
            with redirect_stdout(out):
                sk.cmd_normalize(SimpleNamespace(dry_run=bool(body.get("dry_run"))))
            return self.json_out({"ok": True, "report": out.getvalue().strip()})
        if p == "/api/jobs/sweep":
            return self.json_out({"ok": True, "job": start_job([str(SWEEP_SCRIPT)])})
        return self.json_out({"ok": False, "error": "unknown endpoint"}, 404)


# ------------------------------------------------------------- bootstrap

def main():
    ap = argparse.ArgumentParser(description="Seekter Web UI server")
    ap.add_argument("--port", type=int, default=8770)
    ap.add_argument("--bind", default="127.0.0.1")
    ap.add_argument("--root", help="seekter checkout to drive (default: scripts' sibling root)")
    ap.add_argument("--open", action="store_true")
    a = ap.parse_args()
    root = Path(a.root).resolve() if a.root else ROOT
    set_root(root)
    Handler.sk = sk
    Handler.ui = UI
    url = f"http://{a.bind}:{a.port}/"
    print(url, "Ctrl+C stops. profile:", (root / "profile" / "profile.md").exists())
    if a.open:
        import webbrowser
        webbrowser.open(url)
    ThreadingHTTPServer((a.bind, a.port), Handler).serve_forever()


if __name__ == "__main__":
    main()