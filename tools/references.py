"""Bounded public-source refresh and offline provenance verification.

Downloaded writing guides are data. This tool never imports or executes them.
"""

import argparse
from datetime import datetime, timezone
import hashlib
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

ROOT = Path(__file__).resolve().parents[1]
STE_REPO = "nuelcyoung/asd-ste100"
STE_LICENSE_SHA256 = "f896090fe5def849c96a9354a201cf5b0cae8c8fa7d5a26838551af7bedcebc2"
STE_FILES = ("README.md", "SKILL.md", "LICENSE", "references/meaning-fidelity.md", "references/writing-rules.md",
             "references/pos-analysis.md", "references/dictionary.md", "references/dictionary-access.md",
             "references/checklist.md", "references/background.md")
SE_TERMS = ("verification", "validation", "requirement", "failure", "fault", "error", "defect", "test case")
RFCS = (2119, 8174)
HOSTS = {"api.github.com", "raw.githubusercontent.com", "www.rfc-editor.org", "rfc-editor.org", "sevocab.computer.org"}
MAX_BYTES = 2_000_000
MANIFEST_FIELDS = {"format_version", "retrieved_at", "files"}
FILE_FIELDS = {"path", "source_url", "revision", "license", "copy_mode", "bytes", "sha256"}
RFC_LICENSE = "Original document notices and IETF reproduction terms"
STE_LICENSE = "MIT; see adjacent LICENSE"
SE_LICENSE = "SEVOCAB per-definition copying notice; source and notices retained"
SE_REVISION = "Online SEVOCAB; edition and clause are in source_attributions"
SE_FIELDS = {"term", "status", "definition_number", "definition_en", "source_attributions",
             "source_url", "copyright_notices", "extraction"}


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")


def checksum(data):
    return hashlib.sha256(data).hexdigest()


def expected_paths():
    return {f"references/rfc/rfc{n}.txt" for n in RFCS} | {
        f"references/asd-ste100/{path}" for path in STE_FILES
    } | {f"references/sevocab/{term.replace(' ', '-')}.json" for term in SE_TERMS}


def allowed_url(url):
    parsed = urlsplit(url)
    if (parsed.scheme != "https" or parsed.hostname not in HOSTS
            or parsed.username or parsed.password or parsed.port not in (None, 443)
            or parsed.fragment):
        raise ValueError(f"Source URL outside the fixed allowlist: {url}")
    return url


class SafeRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        allowed_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch(url):
    allowed_url(url)
    opener = build_opener(SafeRedirects())
    for attempt in range(2):
        try:
            request = Request(url, headers={"User-Agent": "engineering-language-reference/1.0"})
            with opener.open(request, timeout=20) as response:
                allowed_url(response.url)
                data = response.read(MAX_BYTES + 1)
                if len(data) > MAX_BYTES:
                    raise ValueError(f"Source exceeds {MAX_BYTES} bytes: {url}")
                return data
        except HTTPError as exc:
            if attempt or exc.code not in (429, 500, 502, 503, 504):
                raise
            retry = exc.headers.get("Retry-After", "1")
            time.sleep(min(int(retry), 3) if retry.isdigit() else 1)
        except (URLError, TimeoutError):
            if attempt:
                raise
            time.sleep(1)
    raise RuntimeError("unreachable")


class TermParser(HTMLParser):
    """Extract visible term/definition/source spans, including nested highlights."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tables = []
        self.table_depth = self.span_depth = 0
        self.capture_depth = None
        self.current = self.field = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "table":
            self.table_depth += 1
            if attrs.get("class") == "display_table":
                if self.current is not None:
                    raise ValueError("Unexpected nested definition table")
                self.current = {"term": "", "definitions": []}
                self.capture_depth = self.table_depth
        if tag == "span":
            self.span_depth += 1
            kind = attrs.get("class")
            if self.current is not None and self.field is None and kind in ("term", "definition", "source"):
                self.field = (kind, self.span_depth, [])

    def handle_data(self, data):
        if self.field is not None:
            self.field[2].append(data)

    def handle_endtag(self, tag):
        if tag == "span":
            if self.field is not None and self.field[1] == self.span_depth:
                kind, _, chunks = self.field
                text = " ".join("".join(chunks).split())
                if kind == "term":
                    self.current["term"] = text.rstrip(".")
                elif kind == "definition":
                    self.current["definitions"].append({"text": text, "sources": []})
                elif self.current["definitions"]:
                    self.current["definitions"][-1]["sources"].append(text)
                self.field = None
            self.span_depth -= 1
        if tag == "table":
            if self.current is not None and self.table_depth == self.capture_depth:
                self.tables.append(self.current)
                self.current = None
            self.table_depth -= 1


def extract_sevocab(term, raw):
    text = raw.decode("utf-8")
    plain = " ".join(unescape(re.sub(r"<[^>]+>", " ", text)).split())
    year = re.search(r"Copyright\s*©,\s*(20\d{2}),\s*IEEE\. Used by permission\.", plain)
    if (not year or "Permission is granted to copy the definition providing that its source is cited." not in plain):
        raise ValueError(f"{term}: source copying notice changed or is absent")
    parser = TermParser()
    parser.feed(text)
    matches = [entry for entry in parser.tables if entry["term"].casefold() == term.casefold()]
    if len(matches) != 1:
        raise ValueError(f"{term}: expected one exact term entry, found {len(matches)}")
    selected = None
    for index, definition in enumerate(matches[0]["definitions"], 1):
        sources = definition["sources"]
        if (sources and all("PMBOK" not in s and "Project Management Institute" not in s for s in sources)
                and any("ISO" in s or "IEEE" in s for s in sources)):
            selected = {"definition_number": index, "definition_en": definition["text"],
                        "source_attributions": sources}
            break
    if selected is None or not selected["definition_en"]:
        raise ValueError(f"{term}: no attributable ISO/IEEE definition available")
    return {"term": term, "status": "SELECTED_QUOTATION", **selected,
            "source_url": sevocab_url(term),
            "copyright_notices": [f"Copyright©, {year[1]}, IEEE. Used by permission.",
                                  f"Copyright © {year[1]} ISO/IEC. Source cited in source_attributions."],
            "extraction": "Visible definition and source text; whitespace normalized; not a full entry or HTML mirror."}


def sevocab_url(term):
    return "https://sevocab.computer.org/sev_display/search.action?term=" + quote(term, safe="") + "&source="


def validate_rfc(number, raw):
    text = raw.decode("utf-8")
    if (not re.search(rf"Request for Comments:\s*{number}\b", text)
            or "Security Considerations" not in text or "<html" in text.lower()
            or (number == 8174 and "Copyright" not in text)):
        raise ValueError(f"RFC {number}: unexpected document structure/notices")


def collect(get=fetch):
    candidates = {}

    def add(path, data, url, revision, license_name, mode):
        candidates[path] = (data, {"path": path, "source_url": url, "revision": revision,
                                  "license": license_name, "copy_mode": mode,
                                  "bytes": len(data), "sha256": checksum(data)})

    for number in RFCS:
        url = f"https://www.rfc-editor.org/rfc/rfc{number}.txt"
        data = get(url)
        validate_rfc(number, data)
        add(f"references/rfc/rfc{number}.txt", data, url, f"RFC {number}",
            RFC_LICENSE, "BYTE_COPY")
    revision = json.loads(get(f"https://api.github.com/repos/{STE_REPO}/commits/main"))["sha"]
    if not isinstance(revision, str) or not re.fullmatch(r"[a-f0-9]{40}", revision):
        raise ValueError("STE source returned an invalid commit")
    license_url = f"https://raw.githubusercontent.com/{STE_REPO}/{revision}/LICENSE"
    license_data = get(license_url)
    if checksum(license_data) != STE_LICENSE_SHA256:
        raise ValueError("STE license changed: review its permissions before a refresh")
    for path in STE_FILES:
        url = f"https://raw.githubusercontent.com/{STE_REPO}/{revision}/{path}"
        data = license_data if path == "LICENSE" else get(url)
        data.decode("utf-8")
        add("references/asd-ste100/" + path, data, url, revision, STE_LICENSE, "BYTE_COPY")
    for term in SE_TERMS:
        url = sevocab_url(term)
        data = json_bytes(extract_sevocab(term, get(url)))
        add(f"references/sevocab/{term.replace(' ', '-')}.json", data, url,
            SE_REVISION, SE_LICENSE, "EXTRACTED_QUOTATION")
    if set(candidates) != expected_paths():
        raise ValueError("Collection did not produce the complete fixed file set")
    return candidates


def verify(root=ROOT):
    manifest = json.loads((root / "SOURCE.json").read_bytes())
    if (set(manifest) != MANIFEST_FIELDS or type(manifest["format_version"]) is not int
            or manifest["format_version"] != 1 or not isinstance(manifest["retrieved_at"], str)):
        raise ValueError("SOURCE.json: unexpected manifest structure/version")
    timestamp = datetime.fromisoformat(manifest["retrieved_at"].replace("Z", "+00:00"))
    if timestamp.utcoffset() is None or timestamp.utcoffset().total_seconds() != 0:
        raise ValueError("SOURCE.json: retrieval time must be UTC")
    rows = manifest["files"]
    if not isinstance(rows, list) or len(rows) != len(expected_paths()):
        raise ValueError("SOURCE.json: incomplete file list")
    if any(not isinstance(row, dict) or set(row) != FILE_FIELDS for row in rows):
        raise ValueError("SOURCE.json: unexpected file fields")
    if any(not isinstance(row[field], str) or not row[field]
           for row in rows for field in FILE_FIELDS - {"bytes"}):
        raise ValueError("SOURCE.json: source metadata fields must be nonempty strings")
    paths = [row["path"] for row in rows]
    if len(set(paths)) != len(paths) or set(paths) != expected_paths():
        raise ValueError("SOURCE.json: duplicate, missing or unexpected source path")
    tree = list((root / "references").rglob("*"))
    if any(path.is_symlink() for path in tree):
        raise ValueError("references/: symlinks are not permitted")
    actual = {path.relative_to(root).as_posix() for path in tree if path.is_file()}
    if actual != expected_paths():
        raise ValueError("references/: actual files differ from the fixed allowlist")
    ste_revisions = set()
    for row in rows:
        path = row["path"]
        allowed_url(row["source_url"])
        data = (root / path).read_bytes()
        if type(row["bytes"]) is not int or row["bytes"] != len(data) or row["sha256"] != checksum(data):
            raise ValueError(f"{path}: length or SHA-256 mismatch")
        if path.startswith("references/rfc/"):
            number = int(Path(path).stem[3:])
            validate_rfc(number, data)
            if (row["source_url"] != f"https://www.rfc-editor.org/rfc/rfc{number}.txt"
                    or row["revision"] != f"RFC {number}" or row["copy_mode"] != "BYTE_COPY"
                    or row["license"] != RFC_LICENSE):
                raise ValueError(f"{path}: source provenance mismatch")
        elif path.startswith("references/asd-ste100/"):
            relative = path.removeprefix("references/asd-ste100/")
            if (not re.fullmatch(r"[a-f0-9]{40}", row["revision"])
                    or row["source_url"] != f"https://raw.githubusercontent.com/{STE_REPO}/{row['revision']}/{relative}"
                    or row["copy_mode"] != "BYTE_COPY" or row["license"] != STE_LICENSE):
                raise ValueError(f"{path}: pinned source provenance mismatch")
            ste_revisions.add(row["revision"])
            if relative == "LICENSE" and checksum(data) != STE_LICENSE_SHA256:
                raise ValueError(f"{path}: unreviewed license")
        else:
            term = Path(path).stem.replace("-", " ")
            entry = json.loads(data)
            if (set(entry) != SE_FIELDS or row["source_url"] != sevocab_url(term)
                    or row["copy_mode"] != "EXTRACTED_QUOTATION" or row["license"] != SE_LICENSE
                    or row["revision"] != SE_REVISION
                    or entry["term"] != term or entry["source_url"] != row["source_url"]
                    or entry["status"] != "SELECTED_QUOTATION" or not isinstance(entry["definition_en"], str)
                    or not entry["definition_en"].strip() or type(entry["definition_number"]) is not int
                    or entry["definition_number"] < 1 or not isinstance(entry["source_attributions"], list)
                    or not entry["source_attributions"] or not isinstance(entry["copyright_notices"], list)
                    or not any(re.fullmatch(r"Copyright©, 20\d{2}, IEEE\. Used by permission\.", notice)
                               for notice in entry["copyright_notices"] if isinstance(notice, str))
                    or any(not isinstance(s, str) or not s or "PMBOK" in s or "Project Management Institute" in s
                           for s in entry["source_attributions"])):
                raise ValueError(f"{path}: extracted quotation provenance mismatch")
    if len(ste_revisions) != 1:
        raise ValueError("STE snapshots must come from one commit")
    return len(rows)


def update(root=ROOT, get=fetch):
    old = None
    if (root / "SOURCE.json").exists():
        verify(root)
        old = json.loads((root / "SOURCE.json").read_bytes())
    candidates = collect(get)  # Finish every download/permission check before writing.
    rows = [candidates[path][1] for path in sorted(candidates)]
    if old:
        prior = {row["path"]: row for row in old["files"]}
        for path in candidates:
            if path.startswith("references/rfc/") and prior[path]["sha256"] != candidates[path][1]["sha256"]:
                raise ValueError(f"{path}: published RFC bytes changed; investigate without overwriting")
        if rows == old["files"]:
            return False
    for path, (data, _) in candidates.items():
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    manifest = {"format_version": 1, "retrieved_at": datetime.now(timezone.utc).isoformat(), "files": rows}
    (root / "SOURCE.json").write_bytes(json_bytes(manifest))
    verify(root)
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("verify", "update"))
    args = parser.parse_args()
    if args.operation == "update":
        print("Sources changed." if update() else "Sources checked; no content/revision change.")
    else:
        print(f"Verified {verify()} fixed source files; hashes, paths and provenance match.")


if __name__ == "__main__":
    main()
