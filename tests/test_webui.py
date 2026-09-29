#!/usr/bin/env python3
"""Tests for scripts/webui.py. Standard library only: python3 -m unittest discover tests

The server is the wrapper around the tracker, so the fixtures reuse the same
subprocess + throwaway-checkout pattern as test_seekter.py: a real server boots
against a temporary root seeded through the CLI, and every endpoint is hit over
HTTP exactly the way the browser hits it. The contract here: the API never
bypasses the dedup guard, and the JSON errors surface the CLI contract.
"""
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "webui.py"


def _free_port():
    import socket
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port

SEED_ONE = [
    "--company", "Placeholder Labs", "--role", "Senior Backend Engineer", "--status", "applied",
    "--url", "https://jobs.ashbyhq.com/placeholder-labs/1e548ada-9c1b-4a20-9b7a-0d5ef4b9c111",
    "--source", "freehire", "--ats", "ashby", "--location-fit", "A",
    "--why", "remote eu backend", "--notes", "CAPTCHA at step 3, second CV needed first",
]
SEED_TWO = [
    "--company", "Placeholder Co", "--role", "Staff Data Scientist", "--status", "pending",
    "--url", "https://www.linkedin.com/jobs/view/4468710729",
]


class ServerCase(unittest.TestCase):
    """Boots a real server against a throwaway copy with seeded applications."""

    @classmethod
    def setUpClass(cls):
        cls.root = Path(tempfile.mkdtemp(prefix="seekter-webui-"))
        for name in ("scripts", "tests", "templates", "ui", "reference", ".github"):
            src = REPO / name
            if src.is_dir():
                shutil.copytree(src, cls.root / name)
        cls.port = _free_port()
        cls.proc = subprocess.Popen(
            [sys.executable, str(cls.root / "scripts" / "webui.py"),
             "--port", str(cls.port), "--root", str(cls.root), "--bind", "127.0.0.1"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        cls.base = f"http://127.0.0.1:{cls.port}/"
        cls._wait_up()
        for seed in (SEED_ONE, SEED_TWO):
            cls.run_cli("add", *seed)
        cls.pending = next(r for r in cls.get("/api/apps")["rows"] if r["company"] == "Placeholder Co")

    @classmethod
    def tearDownClass(cls):
        cls.proc.terminate()
        cls.proc.wait()
        shutil.rmtree(cls.root, ignore_errors=True)

    @classmethod
    def _free_port(cls):
        import socket
        s = socket.socket()
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
        s.close()
        return port

    @classmethod
    def _wait_up(cls):
        import time
        for _ in range(40):
            try:
                urllib.request.urlopen(cls.base + "api/overview", timeout=2)
                return
            except Exception:
                time.sleep(0.25)
        raise RuntimeError("webui server did not come up")

    @classmethod
    def run_cli(cls, *argv):
        return subprocess.run([sys.executable, str(cls.root / "scripts" / "seekter.py"), *argv],
                              capture_output=True, text=True, cwd=str(cls.root))

    @classmethod
    def get(cls, path):
        with urllib.request.urlopen(cls.base + path, timeout=10) as r:
            return json.loads(r.read().decode("utf8"))

    @classmethod
    def post(cls, path, payload):
        req = urllib.request.Request(
            cls.base + path, data=json.dumps(payload).encode("utf8"),
            headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode("utf8"))

    # --------------------------------------------------- reads

    def test_overview_counts_match_the_cli(self):
        data = self.get("/api/overview")
        self.assertTrue(data["ok"])
        cli = json.loads(self.run_cli("stats").stdout)
        self.assertEqual(data["stats"]["total"], cli["total"])
        self.assertEqual(data["stats"]["pending"], cli["pending"])
        self.assertEqual(data["stats"]["response_rate"], cli["response_rate"])

    def test_overview_reports_pending_records_in_needs_you(self):
        data = self.get("/api/overview")
        self.assertEqual(len(data["needs_you"]), data["stats"]["pending"])

    def test_apps_list_filters_by_status(self):
        rows = self.get("/api/apps?status=applied")["rows"]
        self.assertTrue(rows)
        for row in rows:
            self.assertEqual(row["status"], "applied")

    def test_app_detail_serves_the_sections(self):
        row = self.pending
        data = self.get("/api/app?path=" + urllib.parse.quote(row["path"]))
        self.assertIn("Answers", data["sections"])
        self.assertIn("Why it fits", data["sections"])

    def test_unknown_app_path_returns_404_json(self):
        with self.assertRaises(urllib.error.HTTPError) as caught:
            self.get("/api/app?path=../README.md")
        self.assertEqual(caught.exception.code, 404)

    # --------------------------------------------------- dedup contract

    def test_check_blocks_a_duplicate_and_reports_the_match(self):
        url = "https://jobs.ashbyhq.com/placeholder-labs/1e548ada-9c1b-4a20-9b7a-0d5ef4b9c111"
        data = self.get("/api/check?url=" + urllib.parse.quote(url) +
                        "&company=" + urllib.parse.quote("Placeholder Labs"))
        self.assertEqual(data["state"], "DUP")
        self.assertEqual(data["matches"][0]["company"], "Placeholder Labs")

    def test_check_many_reports_new_dup_and_same_company(self):
        data = self.post("/api/check-many", {"lines": [
            "https://jobs.ashbyhq.com/placeholder-labs/1e548ada-9c1b-4a20-9b7a-0d5ef4b9c111",
            "https://jobs.ashbyhq.com/placeholder-labs/9f8e7d6c-1111-2222-3333-444455556666 | Placeholder Labs",
            "https://www.linkedin.com/jobs/view/4468710729",
            "https://jobs.example.com/other/never-tracked-1",
            "https://jobs.ashbyhq.com/placeholder-labs/0000aaaa-1111-2222-3333-444455556666 | Placeholder Co"]})
        states = {r["state"] for r in data["results"]}
        self.assertIn("DUP", states)
        self.assertIn("SAMECO", states)
        self.assertIn("NEW", states)

    def test_add_refuses_a_duplicate_and_succeeds_with_force(self):
        body = {"company": "Placeholder Labs", "role": "Other Role",
                "url": "https://jobs.ashbyhq.com/placeholder-labs/1e548ada-9c1b-4a20-9b7a-0d5ef4b9c111",
                "status": "pending"}
        with self.assertRaises(urllib.error.HTTPError):
            self.post("/api/add", body)
        body["force"] = True
        added = self.post("/api/add", body)
        self.assertIn("applications", added["path"])

    # --------------------------------------------------- mutations

    def test_move_writes_a_log_line_and_updates_the_status(self):
        row = self.pending
        moved = self.post("/api/move", {"target": row["path"], "status": "interviewing",
                                        "note": "recruiter calls on Thursday"})
        self.assertIn("applications", moved["path"])
        with open(self.root / moved["path"], encoding="utf8") as f:
            text = f.read()
        self.assertIn("status: interviewing", text)
        self.assertIn("recruiter calls on Thursday", text)

    def test_rebuild_index_endpoint_rewrites_the_overview(self):
        result = self.post("/api/index", {})
        after = (self.root / "applications" / "README.md").read_text(encoding="utf8")
        self.assertTrue(result["ok"])
        self.assertIn("Generated by `scripts/seekter.py`", after)

    def test_normalize_dry_run_reports_without_writing(self):
        result = self.post("/api/normalize", {"dry_run": True})
        self.assertTrue(result["ok"])
        self.assertIn("would change", result["report"])

    # --------------------------------------------------- runs + profile

    def test_run_day_returns_404_when_there_is_no_sweep(self):
        with self.assertRaises(urllib.error.HTTPError) as caught:
            self.get("/api/run/day?date=2030-01-01")
        self.assertEqual(caught.exception.code, 404)

    def test_profile_endpoint_reports_missing_config(self):
        data = self.get("/api/profile")
        self.assertFalse(data["has_profile"])
        self.assertIn("title_keep", data["missing_values"])

    def test_static_ui_serves_the_shell(self):
        with urllib.request.urlopen(self.base, timeout=10) as r:
            html = r.read().decode("utf8")
        self.assertIn("Seekter Web UI", html)
        self.assertIn('id="app"', html)