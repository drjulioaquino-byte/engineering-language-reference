# Initial verification — 2026-10-31

Author: Codex (implementador). These are implementation checks, not independent
review or certification by any standards organization.

## Observed locally

Environment: Windows 11, Python 3.14.3; runtime tooling uses the standard library
and Git. No model provider, database or private project dependency is needed.

- `python -m unittest discover -s tests -v`: **30 passed**.
- `python tools/references.py verify`: **20 fixed files verified** against their
  manifest paths, source URLs, sizes, revisions, license labels and SHA-256 hashes.
- `python tools/glossary.py verify`: **17 editorial terms** and their bilingual
  Markdown view agree.
- `python -m compileall -q tools tests`: passed.
- `git diff --cached --check`: passed.
- Live source collection succeeded for both original RFCs, the complete ten-file
  MIT guide at `3fe2ccb51b1a98fb8d40aa88ec448575b8439ddb`, and eight attributed
  SEVOCAB quotations. A subsequent live check returned no content/revision change.

The source verifier has project-specific structural and provenance rules.
These references provide no common official machine schema or executable
semantic checker. The library does not invent an official schema certification.
Editorial text, source quotations and byte copies are marked separately.

## Failure and boundary coverage

Tests reject altered bytes; omitted files even when omitted from the manifest;
extra or duplicate entries; wrong sources; license relabeling; non-UTC timestamps;
an absent copying notice; the wrong term; PMI-only attribution; and invalid URLs.
They verify unchanged refreshes do not churn timestamps, source outages and
changed licenses leave snapshots unchanged, RFC changes stop rather than overwrite,
and updated guide files share a single pinned revision.

Glossary tests check duplicate terms, missing languages, uppercase requirement
tokens, editorial status, source paths and a stale human-readable view.
Automation tests exercise the proposal branch path and reuse of identical proposals
with mocked Git operations. They do not claim a live scheduled branch publication.

## Automation permissions and activation

Repository readback: default workflow token permissions are `read`, and workflow
PR creation/approval is disabled. Enabling the combined GitHub setting was rejected
by automatic approval review because it also grants approval capability. That
setting was not changed and no alternative credential was added.

The implemented alternative only requests `contents:write` in its scheduled job.
It publishes an `automation/reference-refresh-<run-id>` branch and a comparison
link, with no PR creation, approval, merge, force push or default-branch write.
Working glossary and workflow files are outside its staging allowlist.

CI runs the offline verifier, glossary check and tests on the implementation PR.
The weekly/manual refresh workflow needs to be merged into the default branch
before it can operate. Its end-to-end scheduled execution remains pending that
Human merge. No run is claimed before it occurs. The PR carries the final head
and observed CI checkpoint; this document does not cite its own commit SHA.

## Material limits

- Eight SEVOCAB terms, not the full vocabulary or full ISO publication.
- The mirrored guide is unofficial; its dictionary examples are not the official
  complete ASD dictionary. Full STE compliance has not been verified.
- Hashes prove consistency with this manifest, not authenticity against a
  compromised upstream or suitability of a definition in every context.
- RFC errata and standard amendments need separate review; immutable RFC text
  is not silently rewritten. Network availability is verified only during a run.
- Public sources and editorial content only; no private project context or data.
