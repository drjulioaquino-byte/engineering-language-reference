"""Verify original editorial definitions and render their bilingual reading view."""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELDS = {"term", "definition_en", "explanation_pt", "source_files", "source_status"}
KEYWORDS = {"MUST", "MUST NOT", "SHOULD", "SHOULD NOT", "MAY"}


def read_glossary(root=ROOT):
    data = json.loads((root / "glossary.json").read_bytes())
    if (set(data) != {"format_version", "status", "entries"} or data["format_version"] != 1
            or data["status"] != "EDITORIAL_WORKING_GLOSSARY"
            or not isinstance(data["entries"], list) or not data["entries"]):
        raise ValueError("glossary.json: invalid structure/version/status")
    seen = set()
    for entry in data["entries"]:
        if not isinstance(entry, dict) or set(entry) != FIELDS:
            raise ValueError("glossary.json: invalid entry fields")
        for field in ("term", "definition_en", "explanation_pt"):
            if not isinstance(entry[field], str) or not entry[field].strip():
                raise ValueError(f"glossary.json: missing text in {field}")
            if "|" in entry[field] or "\n" in entry[field]:
                raise ValueError(f"glossary.json: unsupported table characters in {field}")
        term = entry["term"]
        if term.casefold() in seen:
            raise ValueError(f"glossary.json: duplicate term {term}")
        seen.add(term.casefold())
        if term.upper() in KEYWORDS and term not in KEYWORDS:
            raise ValueError("BCP 14 tokens must retain uppercase in this glossary")
        sources = entry["source_files"]
        if not isinstance(sources, list) or any(not isinstance(path, str) for path in sources):
            raise ValueError(f"{term}: source_files must be a list of paths")
        expected_status = "EDITORIAL_WITH_SOURCE_CONTEXT" if sources else "EDITORIAL_NO_STANDARD_DEFINITION_CLAIM"
        if entry["source_status"] != expected_status:
            raise ValueError(f"{term}: source status must distinguish editorial definitions")
        for path in sources:
            target = (root / path).resolve()
            if not target.is_relative_to((root / "references").resolve()) or not target.is_file():
                raise ValueError(f"{term}: source path outside local references or missing: {path}")
    if not KEYWORDS <= {e["term"] for e in data["entries"]}:
        raise ValueError("glossary.json: missing normative keyword distinctions")
    return data


def render(data):
    lines = ["# Working glossary / Glossário de trabalho", "",
             "Original editorial explanations under MIT. These are not official definitions or translations of standards.",
             "Source context is linked where available; entries without it are explicitly editorial.",
             "Read the original quotations in references/sevocab/ and the original RFCs before adopting a meaning.", "",
             "| Term | Working definition (English) | Explicação editorial (português) | Source context |",
             "| --- | --- | --- | --- |"]
    for entry in data["entries"]:
        sources = ", ".join(f"[{Path(path).name}](../{path})" for path in entry["source_files"]) or "Editorial only"
        lines.append(f"| `{entry['term']}` | {entry['definition_en']} | {entry['explanation_pt']} | {sources} |")
    return "\n".join(lines) + "\n"


def verify(root=ROOT):
    data = read_glossary(root)
    if (root / "docs/GLOSSARY.md").read_text(encoding="utf-8") != render(data):
        raise ValueError("docs/GLOSSARY.md differs from glossary.json; render it again")
    return len(data["entries"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("verify", "render"))
    args = parser.parse_args()
    if args.operation == "render":
        (ROOT / "docs/GLOSSARY.md").write_text(render(read_glossary()), encoding="utf-8", newline="\n")
    print(f"Verified {verify()} editorial terms and their reading view.")


if __name__ == "__main__":
    main()
