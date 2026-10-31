# Initial implementation record

Codex recorded this scope on 2026-10-31. The Human asked for sources in their
GitHub, accessible to everyone, and GitHub Actions to keep them up to date.
The repository is public and independent of GEM or any particular AI product.

Acceptance: publish original RFC copies, the MIT-licensed STE writing aid and
attributed selected SEVOCAB quotations; provide human-readable bilingual guides,
structured provenance and a bounded source refresh that publishes review branches.
Keep official standards separate from working terminology. Verify tampering,
missing/extra files, unavailable sources, extraction failures and update stability.

No complete paid ISO standard or official ASD dictionary is copied. No imported
source code is executed. No auto-merge, automatic semantic changes, deployment,
training, user data collection or private project material is included.

Files: references/, SOURCE.json, glossary.json, guides, tools/, tests/ and two
workflows. Runtime tools use Python's standard library. Sources and permitted
paths are fixed in code; a license change or unexpected source structure fails
the refresh before it writes snapshots. RFCs are immutable by number.

The automation is weekly, Monday 09:00 UTC (06:00 Brasília), plus manual dispatch.
It proposes source updates on a separate branch with a manual PR link. The
repository-wide setting for workflow PR creation/approval remains disabled;
the automation has no PR approval or merge operation. Applying the glossary to a
specific system requires a separate choice and behavior tests.

The implementation branch is reviewable in a draft PR. The scheduled workflow
becomes active when the Human merges it into the default branch. This record
does not authorize an agent to merge its own PR.
