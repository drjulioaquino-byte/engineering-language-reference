import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from tools import glossary
from tools import publish_update_branch as proposal


class GlossaryTests(unittest.TestCase):
    def setUp(self):
        work = glossary.ROOT / ".work"
        work.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=work)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copytree(glossary.ROOT / "references", self.root / "references")
        shutil.copytree(glossary.ROOT / "docs", self.root / "docs")
        shutil.copy2(glossary.ROOT / "glossary.json", self.root / "glossary.json")
        self.data = json.loads((self.root / "glossary.json").read_bytes())

    def save(self, value):
        (self.root / "glossary.json").write_text(json.dumps(value), encoding="utf-8")

    def test_bilingual_reading_view_matches_structured_glossary(self):
        self.assertEqual(glossary.verify(self.root), 17)

    def test_duplicate_term_fails(self):
        self.data["entries"].append(copy.deepcopy(self.data["entries"][0]))
        self.save(self.data)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            glossary.read_glossary(self.root)

    def test_lowercase_normative_token_is_not_silently_treated_as_bcp14(self):
        self.data["entries"][-1]["term"] = "may"
        self.save(self.data)
        with self.assertRaisesRegex(ValueError, "uppercase"):
            glossary.read_glossary(self.root)

    def test_editorial_text_cannot_claim_it_is_an_official_quotation(self):
        self.data["entries"][0]["source_status"] = "OFFICIAL_DEFINITION"
        self.save(self.data)
        with self.assertRaisesRegex(ValueError, "editorial"):
            glossary.read_glossary(self.root)

    def test_source_cannot_escape_reference_directory(self):
        self.data["entries"][0]["source_files"] = ["../private.json"]
        self.save(self.data)
        with self.assertRaisesRegex(ValueError, "source path"):
            glossary.read_glossary(self.root)

    def test_portuguese_and_english_text_are_both_mandatory(self):
        for field in ("definition_en", "explanation_pt"):
            with self.subTest(field=field):
                data = copy.deepcopy(self.data)
                data["entries"][0][field] = ""
                self.save(data)
                with self.assertRaisesRegex(ValueError, "missing text"):
                    glossary.read_glossary(self.root)

    def test_stale_human_reading_view_fails(self):
        (self.root / "docs/GLOSSARY.md").write_text("stale", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "differs"):
            glossary.verify(self.root)


class AutomationBoundaryTests(unittest.TestCase):
    def test_automation_can_only_stage_reference_snapshots_and_manifest(self):
        self.assertTrue(proposal.approved_changes(["SOURCE.json", "references/rfc/rfc2119.txt"]))
        for paths in ([".github/workflows/refresh.yml"], ["glossary.json"], ["tools/references.py"],
                      ["SOURCE.json", "../README.md"], []):
            with self.subTest(paths=paths):
                self.assertFalse(proposal.approved_changes(paths))

    def test_git_porcelain_leading_status_space_is_preserved(self):
        with patch.object(proposal.subprocess, "check_output", return_value=" M SOURCE.json\n"):
            line = proposal.run("git", "status", "--porcelain")
        self.assertEqual(line[3:], "SOURCE.json")

    def test_existing_identical_branch_prevents_duplicate_publication(self):
        calls = []
        def fake_run(*args):
            calls.append(args)
            if args[:2] == ("git", "status"):
                return " M SOURCE.json"
            if args[:2] == ("git", "ls-remote"):
                return "a" * 40 + "\trefs/heads/automation/reference-refresh-122"
            if args[:2] == ("git", "fetch"):
                return ""
            if args[:2] == ("git", "show"):
                return json.dumps({"files": []})
            if args[:2] == ("git", "diff"):
                return "SOURCE.json"
            raise AssertionError(f"Unexpected mutation: {args}")
        with patch.object(Path, "read_bytes", return_value=b'{"files": []}'), patch.object(
            proposal, "verify"
        ), patch.object(proposal, "run", side_effect=fake_run), patch.dict(
            proposal.os.environ, {"GITHUB_REPOSITORY": "owner/repo", "GITHUB_RUN_ID": "123",
                                   "REFERENCE_DEFAULT_BRANCH": "main"}):
            self.assertEqual(proposal.main(), 0)
        self.assertFalse(any(call[:2] == ("git", "push") for call in calls))

    def test_new_snapshot_is_published_only_to_an_automation_branch(self):
        calls = []
        def fake_run(*args):
            calls.append(args)
            if args[:2] == ("git", "status"):
                return " M SOURCE.json"
            return ""
        with patch.object(proposal, "verify"), patch.object(proposal, "run", side_effect=fake_run), patch.dict(
            proposal.os.environ, {"GITHUB_REPOSITORY": "owner/repo", "GITHUB_RUN_ID": "123",
                                   "REFERENCE_DEFAULT_BRANCH": "main"}):
            self.assertEqual(proposal.main(), 0)
        self.assertIn(("git", "push", "origin", "HEAD:refs/heads/automation/reference-refresh-123"), calls)
        self.assertFalse(any(call[0] == "gh" for call in calls))


if __name__ == "__main__":
    unittest.main()
