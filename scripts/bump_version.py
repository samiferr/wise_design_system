#!/usr/bin/env python3
"""Compute and apply the next package version based on what changed.

Bump rules (checked in this order, first match wins):
  - migration          -> MAJOR bump  (X+1.0.0)
  - patch-only change  -> MINOR bump  (X.Y+1.0)   [styling / templates / debug]
  - anything else       -> PATCH bump (X.Y.Z+1)   [new feature / default]

Classification looks at both the commit message and the changed file paths
of the merged commit(s), so it works whether the signal is a conventional
commit prefix or the shape of the diff itself.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PYPROJECT = REPO_ROOT / "pyproject.toml"

MIGRATION_PATH_RE = re.compile(r"(^|/)migrations/.*\.py$")
PATCH_ONLY_PATH_RE = re.compile(
    r"\.(css|scss)$"
    r"|(^|/)templates/.*\.html$"
    r"|(^|/)static/"
    r"|(^|/)static_src/"
)
MIGRATION_KEYWORDS = ("migration", "migrate")
PATCH_KEYWORDS = ("style", "styling", "template", "debug", "patch")


def run(*args: str) -> str:
    return subprocess.run(args, cwd=REPO_ROOT, check=True, capture_output=True, text=True).stdout.strip()


def get_commit_range(before: str, after: str) -> tuple[str, str]:
    zero_sha = "0" * 40
    if not before or before == zero_sha:
        try:
            run("git", "cat-file", "-e", "HEAD~1")
            before = run("git", "rev-parse", "HEAD~1")
        except subprocess.CalledProcessError:
            before = run("git", "rev-list", "--max-parents=0", after)
    return before, after


def get_changed_files(before: str, after: str) -> list[str]:
    diff = run("git", "diff", "--name-only", f"{before}..{after}")
    return [line for line in diff.splitlines() if line]


def get_commit_messages(before: str, after: str) -> str:
    return run("git", "log", "--format=%B", f"{before}..{after}")


def classify(commit_messages: str, changed_files: list[str]) -> str:
    lowered_messages = commit_messages.lower()

    if any(keyword in lowered_messages for keyword in MIGRATION_KEYWORDS):
        return "major"
    if any(MIGRATION_PATH_RE.search(path) for path in changed_files):
        return "major"

    if any(keyword in lowered_messages for keyword in PATCH_KEYWORDS):
        return "minor"
    if changed_files and all(PATCH_ONLY_PATH_RE.search(path) for path in changed_files):
        return "minor"

    return "patch"


def read_version() -> str:
    text = PYPROJECT.read_text()
    match = re.search(r'^version\s*=\s*"(\d+)\.(\d+)\.(\d+)"', text, re.MULTILINE)
    if not match:
        raise RuntimeError("Could not find a version = \"X.Y.Z\" line in pyproject.toml")
    return match.group(0), match.group(1), match.group(2), match.group(3)


def bump(major: int, minor: int, patch: int, level: str) -> tuple[int, int, int]:
    if level == "major":
        return major + 1, 0, 0
    if level == "minor":
        return major, minor + 1, 0
    return major, minor, patch + 1


def write_version(old_line: str, new_version: str) -> None:
    text = PYPROJECT.read_text()
    new_line = re.sub(r'"\d+\.\d+\.\d+"', f'"{new_version}"', old_line)
    text = text.replace(old_line, new_line, 1)
    PYPROJECT.write_text(text)


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: bump_version.py <before-sha> <after-sha>", file=sys.stderr)
        return 2

    before, after = get_commit_range(sys.argv[1], sys.argv[2])
    changed_files = get_changed_files(before, after)
    commit_messages = get_commit_messages(before, after)

    level = classify(commit_messages, changed_files)

    old_line, major, minor, patch = read_version()
    new_major, new_minor, new_patch = bump(int(major), int(minor), int(patch), level)
    new_version = f"{new_major}.{new_minor}.{new_patch}"

    write_version(old_line, new_version)

    print(f"level={level}")
    print(f"old_version={major}.{minor}.{patch}")
    print(f"new_version={new_version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
