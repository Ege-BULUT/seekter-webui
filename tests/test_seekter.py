#!/usr/bin/env python3
"""Tests for scripts/seekter.py. Standard library only: python3 -m unittest discover tests

The tracker CLI is the one part of this kit that can lose an application. Every
case below is either a promise the README makes or a bug that already cost a
duplicate submission, and the comment says which.

The pure functions are imported directly. Everything that touches the tracker
runs the real script as a subprocess against a throwaway repository, because
ROOT is derived from the script's own location and the exit code of `check` is
part of the contract.
"""
import datetime as dt
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "seekter.py"
TODAY = dt.date.today().isoformat()


def _import():
    spec = importlib.util.spec_from_file_location("seekter_under_test", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


sk = _import()


# ---------------------------------------------------------------- job identity

class JobKeyTests(unittest.TestCase):
    """job_key is the load-bearing field: it is what makes the same posting
    reached through three different sites one record instead of three."""

    def test_empty_url_has_no_key(self):
        self.assertEqual(sk.job_key(""), "")
        self.assertEqual(sk.job_key(None), "")

    def test_linkedin_path_and_query_forms_agree(self):
        # The same job arrives as /jobs/view/<id> from the API and as
        # ?currentJobId=<id> from the search page. They must key the same.
        a = sk.job_key("https://www.linkedin.com/jobs/view/4468710729/")
        b = sk.job_key("https://www.linkedin.com/jobs/search/?currentJobId=4468710729&keywords=x")
        self.assertEqual(a, "linkedin:4468710729")
        self.assertEqual(a, b)

    def test_greenhouse_forms(self):
        self.assertEqual(sk.job_key("https://boards.greenhouse.io/acme/jobs/4567890"),
                         "greenhouse:4567890")
        self.assertEqual(sk.job_key("https://acme.com/careers?gh_jid=4567890"),
                         "greenhouse:4567890")

    def test_uuid_anywhere_in_the_path_wins_and_is_lowercased(self):
        upper = "https://jobs.ashbyhq.com/acme/1E548ADA-1111-2222-3333-444455556666"
        lower = "https://jobs.ashbyhq.com/acme/1e548ada-1111-2222-3333-444455556666/application"
        self.assertEqual(sk.job_key(upper), "uuid:1e548ada-1111-2222-3333-444455556666")
        self.assertEqual(sk.job_key(upper), sk.job_key(lower))

    def test_breezy_keys_on_the_id_not_the_title_slug(self):
        # Measured 25 Sept: an employer renamed a Breezy posting without opening a
        # new one. Keying on the whole path made the rename look like a new job, it
        # passed dedup as NEW, and only Breezy's own server caught the second form.
        before = "https://acme.breezy.hr/p/ff94f3182ac2-senior-product-designer"
        after = "https://acme.breezy.hr/p/ff94f3182ac2-senior-product-design-engineer"
        self.assertEqual(sk.job_key(before), "breezy:ff94f3182ac2")
        self.assertEqual(sk.job_key(before), sk.job_key(after))

    def test_indeed_keeps_the_id_in_the_query(self):
        # Without this every Indeed posting collapses to "<host>/viewjob" and the
        # first one tracked makes all the others look like duplicates.
        one = sk.job_key("https://uk.indeed.com/viewjob?jk=abc123def456")
        two = sk.job_key("https://uk.indeed.com/viewjob?jk=999888777666")
        self.assertEqual(one, "indeed:abc123def456")
        self.assertNotEqual(one, two)

    def test_generic_id_query_param_on_a_careers_site(self):
        # Measured 24 Sept: careers.celonis.com had two design roles whose paths
        # were identical and whose ids lived in a query param.
        one = sk.job_key("https://careers.example.com/job-detail?jobId=1234567")
        two = sk.job_key("https://careers.example.com/job-detail?jobId=7654321")
        self.assertEqual(one, "careers.example.com:1234567")
        self.assertNotEqual(one, two)

    def test_apply_suffix_and_www_do_not_create_a_second_record(self):
        plain = sk.job_key("https://www.example.com/careers/senior-designer")
        applying = sk.job_key("https://example.com/careers/senior-designer/apply")
        self.assertEqual(plain, applying)
        self.assertEqual(plain, "example.com/careers/senior-designer")

    def test_a_url_with_no_path_falls_back_rather_than_keying_on_the_host(self):
        # Keying on the host alone would make every posting on that site one record.
        a = sk.job_key("https://jobs.example.com/#/postings/aaa")
        b = sk.job_key("https://jobs.example.com/#/postings/bbb")
        self.assertNotEqual(a, b)
        self.assertNotEqual(sk.job_key("https://jobs.example.com/?id=aaa"),
                            sk.job_key("https://jobs.example.com/?id=bbb"))


# ------------------------------------------------------------- normalisation

class NormaliseTests(unittest.TestCase):

    def test_slug_folds_letters_that_nfkd_alone_would_delete(self):
        # NFKD only folds a letter that decomposes into base + combining mark.
        # A letter that is its own base character gets deleted instead, so the
        # dotless ı disappeared: "Tasarım Atölyesi" became "tasarm-atolyesi".
        self.assertEqual(sk.slug("Tasarım Atölyesi"), "tasarim-atolyesi")
        self.assertEqual(sk.slug("İstanbul Ürün"), "istanbul-urun")
        for word, want in [("Łódź", "lodz"), ("Ørsted", "orsted"), ("Straße", "strasse"),
                           ("Æther", "aether"), ("Đuro", "duro")]:
            self.assertEqual(sk.slug(word), want, word)

    def test_slug_does_not_fold_two_different_employers_onto_one_string(self):
        # The same-company check in `check` compares slugs, so a deletion here
        # is not only cosmetic: before the fix both of these were "isk".
        self.assertNotEqual(sk.slug("Işık"), sk.slug("Isk"))

    def test_slug_truncates_without_a_trailing_dash(self):
        self.assertEqual(sk.slug("a" * 60), "a" * 40)
        self.assertFalse(sk.slug("word " + "x" * 60, 6).endswith("-"))
        self.assertEqual(sk.slug(""), "x")  # never an empty filename fragment

    def test_norm_lowercases_and_hyphenates_enums(self):
        self.assertEqual(sk.norm("Company site"), "company-site")
        self.assertEqual(sk.norm("  Other  Board "), "other-board")
        self.assertEqual(sk.norm(None), "")

    def test_ats_is_a_function_of_the_url(self):
        self.assertEqual(sk.ats_from_url("https://jobs.ashbyhq.com/acme/x"), "ashby")
        self.assertEqual(sk.ats_from_url("https://jobs.lever.co/acme/x"), "lever")
        self.assertEqual(sk.ats_from_url("https://acme.com/careers"), "")

    def test_an_ats_name_stored_as_source_moves_to_ats(self):
        # A common mix-up in hand-kept trackers: the column says where you applied
        # through, not where you found it. Source becomes the generic "board".
        r = {"source": "Greenhouse", "url": "https://boards.greenhouse.io/acme/jobs/1"}
        sk.fix_meta(r)
        self.assertEqual(r["ats"], "greenhouse")
        self.assertEqual(r["source"], "board")

    def test_other_board_is_just_board(self):
        r = {"source": "Other board"}
        sk.fix_meta(r)
        self.assertEqual(r["source"], "board")

    def test_fix_meta_fills_the_key_and_reports_only_real_changes(self):
        r = {"url": "https://www.linkedin.com/jobs/view/123456789/"}
        changed = sk.fix_meta(r)
        self.assertEqual(r["job_key"], "linkedin:123456789")
        self.assertIn("job_key", changed)
        # Running it again must be a no-op, or `normalize` reports work forever.
        self.assertEqual(sk.fix_meta(dict(r)), {})


class TableTests(unittest.TestCase):
    """A skip row is a markdown table cell, so a reason containing a pipe has to
    survive being read and written repeatedly."""

    def test_escaping_a_cell_is_idempotent(self):
        once = sk._cell("remote | EU only")
        self.assertEqual(once, r"remote \| EU only")
        self.assertEqual(sk._cell(once), once)  # no second backslash

    def test_a_reason_with_a_pipe_survives_a_round_trip(self):
        original = "country list: DE | IT | PT, not TR"
        row = "| " + " | ".join(sk._cell(x) for x in
                                (TODAY, "Acme", "Designer", original, "board", "", "k")) + " |"
        cells = sk._split_row(row)
        self.assertEqual(cells[3], original)
        again = sk._cell(cells[3])
        self.assertEqual(sk._split_row("| " + again + " |")[0], original)

    def test_newlines_are_flattened_so_a_cell_cannot_break_the_table(self):
        self.assertEqual(sk._cell("two\nlines"), "two lines")


# --------------------------------------------------------------- the tracker

class TrackerTests(unittest.TestCase):
    """The real script, run against a throwaway repository."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="seekter-test-"))
        (self.tmp / "scripts").mkdir()
        shutil.copy2(SCRIPT, self.tmp / "scripts" / "seekter.py")
        (self.tmp / "applications").mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_cli(self, *args, stdin=None):
        p = subprocess.run([sys.executable, str(self.tmp / "scripts" / "seekter.py"), *args],
                           input=stdin, capture_output=True, text=True)
        return p.returncode, p.stdout, p.stderr

    def add(self, **kw):
        args = []
        for k, v in kw.items():
            args += ["--" + k.replace("_", "-"), v]
        rc, out, err = self.run_cli("add", *args)
        self.assertEqual(rc, 0, f"add failed: {err}")
        return self.tmp / out.strip().splitlines()[0]

    def skips_table(self, month=None):
        return (self.tmp / "applications" / (month or TODAY[:7]) / "skipped.md").read_text()

    # -- dedup ------------------------------------------------------------

    def test_check_is_new_then_duplicate_after_add(self):
        url = "https://jobs.ashbyhq.com/acme/1e548ada-1111-2222-3333-444455556666"
        rc, out, _ = self.run_cli("check", url, "--company", "Acme")
        self.assertEqual(rc, 0)
        self.assertIn("NEW", out)

        self.add(company="Acme", role="Senior Designer", url=url, status="applied")

        rc, out, _ = self.run_cli("check", url, "--company", "Acme")
        self.assertEqual(rc, 1, "an already-tracked posting must exit 1")
        self.assertIn("DUPLICATE", out)

    def test_dedup_matches_across_the_url_it_was_first_stored_under(self):
        # Measured 23 Sept: a role was submitted a third time because the sweep
        # deduped LinkedIn ids while the record was keyed on the Ashby UUID.
        # `check` runs on the resolved apply URL, and must match either form.
        stored = "https://jobs.ashbyhq.com/acme/1e548ada-1111-2222-3333-444455556666"
        self.add(company="Acme", role="Designer", url=stored)
        same_job_other_path = ("https://jobs.ashbyhq.com/acme/"
                               "1E548ADA-1111-2222-3333-444455556666/application")
        rc, out, _ = self.run_cli("check", same_job_other_path)
        self.assertEqual(rc, 1)
        self.assertIn("DUPLICATE", out)

    def test_a_skipped_posting_is_never_evaluated_twice(self):
        # The README promises dedup reads the skip table too.
        url = "https://acme.com/careers/designer"
        self.add(company="Acme", role="Designer", url=url, status="skipped",
                 notes="the country list leaves out yours")
        self.assertIn("the country list leaves out yours", self.skips_table())
        rc, out, _ = self.run_cli("check", url)
        self.assertEqual(rc, 1)
        self.assertIn("DUPLICATE", out)

    def test_same_company_different_role_is_not_a_duplicate(self):
        self.add(company="Acme", role="Designer", url="https://acme.com/careers/1234567")
        rc, out, _ = self.run_cli("check", "https://acme.com/careers/7654321", "--company", "Acme")
        self.assertEqual(rc, 0)
        self.assertIn("NEW", out)
        self.assertIn("same company, other role", out)

    def test_add_refuses_a_duplicate_unless_forced(self):
        url = "https://acme.com/careers/1234567"
        self.add(company="Acme", role="Designer", url=url)
        rc, _, err = self.run_cli("add", "--company", "Acme", "--role", "Designer", "--url", url)
        self.assertEqual(rc, 1)
        self.assertIn("DUPLICATE", err)
        rc, _, _ = self.run_cli("add", "--company", "Acme", "--role", "Designer",
                                "--url", url, "--force")
        self.assertEqual(rc, 0)

    def test_check_many_reads_bare_ids_as_linkedin_and_reports_per_line(self):
        self.add(company="Acme", role="Designer",
                 url="https://www.linkedin.com/jobs/view/4468710729/")
        rc, out, _ = self.run_cli("check-many", stdin="4468710729\n9999999999 | Acme\n\n")
        self.assertEqual(rc, 0)
        lines = [l for l in out.splitlines() if l.strip()]
        self.assertTrue(lines[0].startswith("DUP"), lines)
        self.assertTrue(lines[1].startswith("SAMECO"), lines)

    # -- status changes ---------------------------------------------------

    def test_a_file_never_changes_folder_when_its_status_changes(self):
        # The whole point of the layout: a rejection a month later edits one line.
        path = self.add(company="Acme", role="Designer", url="https://acme.com/careers/1234567",
                        status="applied", date="2026-08-14", applied="2026-08-14")
        self.assertEqual(path.parent.name, "2026-08")
        rc, out, _ = self.run_cli("move", "https://acme.com/careers/1234567", "rejected",
                                  "--note", "form mail, 2 days")
        self.assertEqual(rc, 0)
        self.assertTrue(path.exists(), "the file moved, and it must not")
        text = path.read_text()
        self.assertIn("status: rejected", text)
        self.assertIn("applied: 2026-08-14", text)
        self.assertIn("form mail, 2 days", text)
        self.assertIn("- 2026-08-14: applied", text)  # the original log line survives

    def test_moving_a_skip_row_to_applied_turns_it_into_a_file(self):
        url = "https://acme.com/careers/1234567"
        self.add(company="Acme", role="Designer", url=url, status="skipped",
                 notes="looked like a relocation role")
        rc, out, _ = self.run_cli("move", url, "applied", "--note", "the form had no country gate")
        self.assertEqual(rc, 0)
        path = self.tmp / out.strip().splitlines()[-1]
        self.assertTrue(path.is_file())
        text = path.read_text()
        self.assertIn("status: applied", text)
        self.assertIn(f"applied: {TODAY}", text)
        self.assertIn("Skipped earlier: looked like a relocation role", text)
        self.assertNotIn("1234567", self.skips_table())  # the row is gone

    def test_moving_a_plain_pending_record_to_skipped_turns_it_into_a_row(self):
        url = "https://acme.com/careers/1234567"
        path = self.add(company="Acme", role="Designer", url=url, status="pending")
        rc, _, _ = self.run_cli("move", url, "skipped", "--note", "account wall")
        self.assertEqual(rc, 0)
        self.assertFalse(path.exists())
        self.assertIn("account wall", self.skips_table())

    def test_a_skip_that_was_once_a_real_application_stays_a_file(self):
        # Collapsing it would drop the submitted answers, which is what makes
        # "no sentence goes to two companies" checkable.
        url = "https://acme.com/careers/1234567"
        path = self.add(company="Acme", role="Designer", url=url, status="applied",
                        answers="Why us: because the design system work is real.")
        rc, out, err = self.run_cli("move", url, "skipped", "--note", "withdrew")
        self.assertEqual(rc, 0)
        self.assertTrue(path.exists(), "an application with answers must not become a row")
        self.assertIn("kept as a file", err)
        text = path.read_text()
        self.assertIn("status: skipped", text)
        self.assertIn("design system work is real", text)

    def test_reannotating_a_skip_keeps_the_original_reason(self):
        url = "https://acme.com/careers/1234567"
        self.add(company="Acme", role="Designer", url=url, status="skipped",
                 notes="country list leaves out yours")
        rc, _, _ = self.run_cli("move", url, "skipped", "--note", "the form had no country field")
        self.assertEqual(rc, 0)
        table = self.skips_table()
        self.assertIn("country list leaves out yours", table)
        self.assertIn(f"[{TODAY}] the form had no country field", table)

    def test_move_rejects_an_unknown_status_and_an_unknown_target(self):
        rc, _, err = self.run_cli("move", "https://acme.com/x", "ghosted")
        self.assertEqual(rc, 1)
        self.assertIn("status must be one of", err)
        rc, _, err = self.run_cli("move", "https://nowhere.example.com/1234567", "rejected")
        self.assertEqual(rc, 1)
        self.assertIn("not found", err)

    # -- generated views and reports --------------------------------------

    def test_stats_counts_sent_and_the_response_rate(self):
        self.add(company="A", role="D", url="https://a.com/careers/1111111", status="applied")
        self.add(company="B", role="D", url="https://b.com/careers/2222222", status="rejected")
        self.add(company="C", role="D", url="https://c.com/careers/3333333", status="pending")
        self.add(company="D", role="D", url="https://d.com/careers/4444444", status="skipped",
                 notes="sector")
        rc, out, _ = self.run_cli("stats")
        self.assertEqual(rc, 0)
        s = json.loads(out)
        self.assertEqual(s["total"], 4)
        self.assertEqual(s["sent"], 2)           # applied + rejected; pending and skipped are not sent
        self.assertEqual(s["pending"], 1)
        self.assertEqual(s["skipped"], 1)
        self.assertEqual(s["response_rate"], 0.5)

    def test_stats_response_rate_is_none_rather_than_zero_when_nothing_was_sent(self):
        rc, out, _ = self.run_cli("stats")
        self.assertIsNone(json.loads(out)["response_rate"])

    def test_index_writes_the_needs_you_table_and_a_month_page(self):
        self.add(company="Acme", role="Designer", url="https://acme.com/careers/1234567",
                 status="pending", notes="tick the reCAPTCHA yourself")
        rc, _, _ = self.run_cli("index")
        self.assertEqual(rc, 0)
        top = (self.tmp / "applications" / "README.md").read_text()
        self.assertIn("## Needs you (1)", top)
        self.assertIn("tick the reCAPTCHA yourself", top)
        month = (self.tmp / "applications" / TODAY[:7] / "README.md").read_text()
        self.assertIn("Acme", month)

    def test_list_filters_by_status_and_date(self):
        self.add(company="Old", role="D", url="https://old.com/careers/1111111",
                 status="applied", date="2026-01-05", applied="2026-01-05")
        self.add(company="New", role="D", url="https://new.com/careers/2222222", status="applied")
        rc, out, _ = self.run_cli("list", "--since", "2026-06-01")
        self.assertIn("New", out)
        self.assertNotIn("Old", out)
        rc, out, _ = self.run_cli("list", "--status", "pending")
        self.assertEqual(out.strip(), "")

    # -- normalize --------------------------------------------------------

    def test_normalize_dry_run_changes_nothing_on_disk(self):
        path = self.add(company="Acme", role="Designer",
                        url="https://boards.greenhouse.io/acme/jobs/4567890")
        path.write_text(path.read_text().replace("source: ", "source: Greenhouse"))
        before = path.read_text()
        rc, out, _ = self.run_cli("normalize", "--dry-run")
        self.assertEqual(rc, 0)
        self.assertIn("would change", out)
        self.assertEqual(path.read_text(), before)
        rc, out, _ = self.run_cli("normalize")
        self.assertIn("normalised", out)
        self.assertIn("ats: greenhouse", path.read_text())

    def test_normalize_is_stable_on_a_second_pass(self):
        # `normalize` counting work forever would mean it is rewriting files on
        # every run, which is how a hand-editable tracker drifts.
        self.add(company="Acme", role="Designer", url="https://jobs.lever.co/acme/1234567")
        self.add(company="Bcme", role="Designer", url="https://b.com/careers/7654321",
                 status="skipped", notes="pipe | in the reason")
        self.run_cli("normalize")
        rc, out, _ = self.run_cli("normalize")
        self.assertEqual(out.strip(), "0 files and 0 skip rows normalised")

    def test_a_skip_reason_containing_a_pipe_does_not_grow_backslashes(self):
        self.add(company="Acme", role="Designer", url="https://a.com/careers/1111111",
                 status="skipped", notes="country list: DE | IT | PT")
        # A second skip in the same month rewrites the whole table.
        self.add(company="Bcme", role="Designer", url="https://b.com/careers/2222222",
                 status="skipped", notes="sector")
        self.run_cli("normalize")
        table = self.skips_table()
        self.assertIn(r"country list: DE \| IT \| PT", table)
        self.assertNotIn(r"\\|", table)


if __name__ == "__main__":
    unittest.main(verbosity=2)
