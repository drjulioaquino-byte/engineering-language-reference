import copy
from html import escape
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import URLError

from tools import references as ref


def page(term, entry, source=None):
    citations = source or entry["source_attributions"]
    return ("<table class='display_table'><span class='term'>" + escape(term) + ".</span>"
            "<span class='definition'>" + escape(entry["definition_en"]) + "</span>"
            + "".join("<span class='source'>" + escape(s) + "</span>" for s in citations)
            + "</table>Copyright©, 2026, IEEE. Used by permission. "
            "Permission is granted to copy the definition providing that its source is cited.").encode()


class ReferenceTests(unittest.TestCase):
    def setUp(self):
        work = ref.ROOT / ".work"
        work.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=work)
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)
        shutil.copytree(ref.ROOT / "references", self.root / "references")
        shutil.copy2(ref.ROOT / "SOURCE.json", self.root / "SOURCE.json")
        self.original = json.loads((self.root / "SOURCE.json").read_bytes())

    def save(self, manifest):
        (self.root / "SOURCE.json").write_bytes(ref.json_bytes(manifest))

    def state(self):
        return {p.relative_to(self.root).as_posix(): p.read_bytes()
                for p in self.root.rglob("*") if p.is_file()}

    def get(self, url):
        if url == f"https://api.github.com/repos/{ref.STE_REPO}/commits/main":
            return json.dumps({"sha": self.original["files"][0]["revision"]}).encode()
        for row in self.original["files"]:
            if row["source_url"] == url:
                data = (self.root / row["path"]).read_bytes()
                if row["copy_mode"] == "EXTRACTED_QUOTATION":
                    entry = json.loads(data)
                    return page(entry["term"], entry)
                return data
        raise AssertionError(f"Unexpected fixture URL: {url}")

    def test_complete_real_snapshot_passes(self):
        self.assertEqual(ref.verify(self.root), 20)

    def test_tampered_bytes_fail(self):
        (self.root / "references/rfc/rfc2119.txt").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            ref.verify(self.root)

    def test_omitting_manifest_and_actual_file_still_fails_fixed_inventory(self):
        manifest = copy.deepcopy(self.original)
        omitted = manifest["files"].pop()
        (self.root / omitted["path"]).unlink()
        self.save(manifest)
        with self.assertRaisesRegex(ValueError, "incomplete file list"):
            ref.verify(self.root)

    def test_extra_file_fails_even_if_not_in_manifest(self):
        (self.root / "references/unregistered.txt").write_text("unexpected")
        with self.assertRaisesRegex(ValueError, "fixed allowlist"):
            ref.verify(self.root)

    def test_duplicate_manifest_entry_fails(self):
        manifest = copy.deepcopy(self.original)
        manifest["files"][-1] = manifest["files"][0]
        self.save(manifest)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            ref.verify(self.root)

    def test_manifest_cannot_change_source_url(self):
        manifest = copy.deepcopy(self.original)
        manifest["files"][0]["source_url"] = "https://example.invalid/source"
        self.save(manifest)
        with self.assertRaisesRegex(ValueError, "allowlist"):
            ref.verify(self.root)

    def test_manifest_cannot_relabel_licensed_source_as_own_mit(self):
        manifest = copy.deepcopy(self.original)
        manifest["files"][-1]["license"] = "MIT"
        self.save(manifest)
        with self.assertRaisesRegex(ValueError, "provenance"):
            ref.verify(self.root)

    def test_timestamp_must_be_utc_and_version_must_be_integer(self):
        for field, value in (("retrieved_at", "2026-10-31T13:00:00-03:00"), ("format_version", True)):
            with self.subTest(field=field):
                manifest = copy.deepcopy(self.original)
                manifest[field] = value
                self.save(manifest)
                with self.assertRaises(ValueError):
                    ref.verify(self.root)

    def test_unchanged_refresh_does_not_change_retrieval_time_or_files(self):
        before = self.state()
        self.assertFalse(ref.update(self.root, self.get))
        self.assertEqual(self.state(), before)

    def test_source_failure_leaves_all_snapshots_unchanged(self):
        before = self.state()
        def fail_last(url):
            if url == ref.sevocab_url(ref.SE_TERMS[-1]):
                raise URLError("simulated source outage")
            return self.get(url)
        with self.assertRaises(URLError):
            ref.update(self.root, fail_last)
        self.assertEqual(self.state(), before)

    def test_changed_license_stops_before_any_snapshot_write(self):
        before = self.state()
        def changed_license(url):
            return b"A different license" if url.endswith("/LICENSE") else self.get(url)
        with self.assertRaisesRegex(ValueError, "license changed"):
            ref.update(self.root, changed_license)
        self.assertEqual(self.state(), before)

    def test_published_rfc_changed_bytes_are_not_silently_overwritten(self):
        before = self.state()
        def changed_rfc(url):
            value = self.get(url)
            return value + b"\n" if url.endswith("rfc2119.txt") else value
        with self.assertRaisesRegex(ValueError, "RFC bytes changed"):
            ref.update(self.root, changed_rfc)
        self.assertEqual(self.state(), before)

    def test_new_ste_commit_is_pinned_consistently(self):
        old = self.original["files"][0]["revision"]
        new = "b" * 40
        def new_revision(url):
            if url == f"https://api.github.com/repos/{ref.STE_REPO}/commits/main":
                return json.dumps({"sha": new}).encode()
            return self.get(url.replace(new, old))
        self.assertTrue(ref.update(self.root, new_revision))
        self.assertEqual(ref.verify(self.root), 20)
        manifest = json.loads((self.root / "SOURCE.json").read_bytes())
        ste = [r for r in manifest["files"] if r["path"].startswith("references/asd-ste100/")]
        self.assertEqual({r["revision"] for r in ste}, {new})


class ParserAndNetworkTests(unittest.TestCase):
    def setUp(self):
        self.entry = json.loads((ref.ROOT / "references/sevocab/verification.json").read_bytes())

    def test_extracts_exact_term_and_retains_attribution(self):
        result = ref.extract_sevocab("verification", page("verification", self.entry))
        self.assertEqual(result, self.entry)

    def test_nested_highlight_preserves_visible_text(self):
        raw = page("verification", self.entry).replace(b"verification.</span>",
                                                       b"<span class='highlight'>verification</span>.</span>")
        self.assertEqual(ref.extract_sevocab("verification", raw), self.entry)

    def test_wrong_term_and_missing_copy_notice_fail(self):
        for raw in (page("unrelated", self.entry), page("verification", self.entry).replace(b"Used by permission.", b"")):
            with self.assertRaises(ValueError):
                ref.extract_sevocab("verification", raw)

    def test_pmi_only_definition_is_not_copied(self):
        with self.assertRaisesRegex(ValueError, "no attributable"):
            ref.extract_sevocab("verification", page("verification", self.entry, ["PMBOK Project Management Institute"]))

    def test_unknown_host_userinfo_http_and_nonstandard_port_fail(self):
        for url in ("https://example.invalid/", "http://www.rfc-editor.org/", "https://user@www.rfc-editor.org/",
                    "file:///etc/passwd", "https://www.rfc-editor.org:8443/"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                ref.allowed_url(url)

    def test_transient_network_error_has_only_two_attempts(self):
        with patch.object(ref, "build_opener") as opener, patch.object(ref.time, "sleep"):
            opener.return_value.open.side_effect = URLError("temporary")
            with self.assertRaises(URLError):
                ref.fetch("https://www.rfc-editor.org/rfc/rfc2119.txt")
            self.assertEqual(opener.return_value.open.call_count, 2)


if __name__ == "__main__":
    unittest.main()
