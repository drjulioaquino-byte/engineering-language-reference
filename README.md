# Engineering Language Reference

**Public references for clear software engineering communication — for people,
teams, educators and tools.** [Leia em português](README.pt-BR.md).

This library separates three jobs: define technical terms, write clear prose,
and express the force of requirements. It is independent of any AI product or
private project. Everyone can read, reuse within the source licenses and contribute.

## Read the sources

| Need | Local material | Original source |
| --- | --- | --- |
| Software and systems vocabulary | [Selected, attributed definitions](references/sevocab/) | [IEEE/ISO SEVOCAB](https://sevocab.computer.org/sev_display/index.action) |
| Clear technical English | [STE writing aid](references/asd-ste100/README.md) | [nuelcyoung/asd-ste100](https://github.com/nuelcyoung/asd-ste100), [Júlio's fork](https://github.com/drjulioaquino-byte/asd-ste100) |
| Requirement levels | [RFC 2119, original text](references/rfc/rfc2119.txt) | [RFC Editor](https://www.rfc-editor.org/rfc/rfc2119.txt) |
| Uppercase requirement keywords | [RFC 8174, original text](references/rfc/rfc8174.txt) | [RFC Editor](https://www.rfc-editor.org/rfc/rfc8174.txt) |

The SEVOCAB selection contains eight terms, not the entire vocabulary or a paid
ISO publication. Each quotation keeps its definition number, source editions,
copyright notices and lookup URL. The [ISO/IEC/IEEE 24765 catalogue entry](https://www.iso.org/standard/71952.html)
describes the associated vocabulary standard. Online SEVOCAB definitions can cite
newer source standards; do not label every selected entry as a quotation from 24765:2017.

The complete ten-file STE aid is unofficial and MIT-licensed. Its presence does not certify STE
compliance. The official ASD dictionary is not included.

## Use the library

1. Read the [usage guide](docs/USAGE.md).
2. Read the [working glossary](docs/GLOSSARY.md) and its [structured form](glossary.json).
3. Choose the meaning and context for your project. Preserve the source reference.
4. Add examples and behavior tests where a term changes an action or permission.

Working definitions and Portuguese explanations are original editorial content,
not official translations of standards. A shared vocabulary supports communication;
it does not prove that people or models interpret every term identically.

## Verify or refresh

Python 3.11 or newer; no third-party Python packages:

```sh
python tools/references.py verify
python -m unittest discover -s tests -v
python tools/references.py update   # network access; fixed public sources only
```

[`SOURCE.json`](SOURCE.json) records exact paths, origins, pinned commits where
available, retrieval time, sizes, hashes and copy modes. RFC and guide copies
keep source bytes. SEVOCAB files contain selected visible text with normalized
whitespace; they are explicitly marked as extracted quotations.

## Weekly GitHub Actions

The [refresh workflow](.github/workflows/refresh.yml) runs Mondays at **09:00 UTC**
(06:00 Brasília), and on manual dispatch. It retrieves permitted sources, checks
the result, and publishes a separate proposal branch when content or a pinned
revision changes. The run prints a comparison link for manual review/PR creation.
It reuses the latest candidate when the snapshots already match. The automation
never creates or approves PRs, merges, force-pushes or writes to the default branch.

The schedule becomes active after this workflow is merged into the default branch.
GitHub may delay scheduled runs or disable them after prolonged public-repository
inactivity. Review the Actions tab for actual execution. The repository keeps
workflow PR creation/approval disabled and default token permissions read-only.
Only the refresh job requests contents:write to publish its separate proposal
branch. It does not request pull-requests:write or a personal token.

The job cannot install the official ASD dictionary, mirror a paid standard, apply
a glossary to another project, or rewrite working definitions automatically.
If a source, permission notice or parser changes unexpectedly, the job fails for
review instead of silently publishing guessed definitions.

## Rights and contribution

Original tools, guides and working definitions use [MIT](LICENSE).
Third-party files retain their own notices; see [THIRD_PARTY.md](THIRD_PARTY.md).
Updates use reviewed PRs. See [CONTRIBUTING.md](CONTRIBUTING.md).
