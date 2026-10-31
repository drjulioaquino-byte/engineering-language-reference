"""Publish verified source proposals on a branch, without PR privileges."""

import json
import os
import re
import subprocess

from tools.references import ROOT, expected_paths, verify


def run(*args):
    return subprocess.check_output(args, cwd=ROOT, text=True).rstrip("\r\n")


def approved_changes(paths):
    allowed = expected_paths() | {"SOURCE.json"}
    return bool(paths) and set(paths) <= allowed


def compare_url(repository, base, branch):
    return f"https://github.com/{repository}/compare/{base}...{branch}"


def main():
    verify()
    repository = os.environ["GITHUB_REPOSITORY"]
    run_id = os.environ["GITHUB_RUN_ID"]
    base = os.environ["REFERENCE_DEFAULT_BRANCH"]
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository) or not run_id.isdigit():
        raise ValueError("Unexpected workflow repository or run identity")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_./-]*", base) or ".." in base:
        raise ValueError("Unexpected default branch")
    # Print no token, fetched source text, environment or upstream instructions.
    changed = run("git", "status", "--porcelain", "--untracked-files=all").splitlines()
    paths = [line[3:] for line in changed]
    if not paths:
        print("No source update to propose.")
        return 0
    if not approved_changes(paths):
        raise ValueError("Refresh changed files outside the fixed source inventory")
    refs = run("git", "ls-remote", "--heads", "origin", "refs/heads/automation/reference-refresh-*")
    candidates = []
    for line in refs.splitlines():
        match = re.fullmatch(r"[a-f0-9]{40}\trefs/heads/(automation/reference-refresh-(\d+))", line)
        if match:
            candidates.append((int(match[2]), match[1]))
    if candidates:
        _, prior_branch = max(candidates)
        run("git", "fetch", "--no-tags", "--depth=1", "origin", prior_branch)
        prior = json.loads(run("git", "show", "FETCH_HEAD:SOURCE.json"))
        current = json.loads((ROOT / "SOURCE.json").read_bytes())
        prior_changes = run("git", "diff", "--name-only", "HEAD", "FETCH_HEAD").splitlines()
        if approved_changes(prior_changes) and prior.get("files") == current["files"]:
            print("The latest source proposal already contains these snapshots:")
            print(compare_url(repository, base, prior_branch))
            return 0
    branch = f"automation/reference-refresh-{run_id}"
    run("git", "switch", "-c", branch)
    run("git", "config", "user.name", "github-actions[bot]")
    run("git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com")
    run("git", "add", "--", "SOURCE.json", "references")
    run("git", "commit", "-m", "Propose refreshed public reference snapshots")
    run("git", "push", "origin", f"HEAD:refs/heads/{branch}")
    print("Source proposal published. Review or open a PR manually; no PR approval permission is used:")
    print(compare_url(repository, base, branch))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
