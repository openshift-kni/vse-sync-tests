#!/bin/bash
#
# Import remote repositories into the monorepo while preserving full git history.
#
# Uses git-filter-repo to rewrite paths so each repo's history appears
# under its target subdirectory, then merges with --allow-unrelated-histories.
#
# Prerequisites: git-filter-repo must be installed.

set -ex

TOPDIR="$(git rev-parse --show-toplevel)"
TEMPDIR="$(mktemp -d)"
trap 'rm -rf "$TEMPDIR"' EXIT

# --- Import reporting into reporting/ ---
git clone git@github.com:redhat-partner-solutions/vse-sync-test-report.git "$TEMPDIR/reporting"
cd "$TEMPDIR/reporting"
git filter-repo --to-subdirectory-filter reporting
cd "$TOPDIR"
git remote add reporting-import "$TEMPDIR/reporting"
git fetch reporting-import main
git merge --allow-unrelated-histories reporting-import/main -m "Import vse-sync-test-report into reporting/"
git remote rm reporting-import

# --- Import collector into collection_tools/ ---
git clone git@github.com:redhat-partner-solutions/vse-sync-collection-tools.git "$TEMPDIR/collector"
cd "$TEMPDIR/collector"
git filter-repo --to-subdirectory-filter collection_tools
cd "$TOPDIR"
git remote add collector-import "$TEMPDIR/collector"
git fetch collector-import main
git merge --allow-unrelated-histories collector-import/main -m "Import vse-sync-collection-tools into collection_tools/"
git remote rm collector-import

# --- Import old_tests_repo at top level ---
git clone git@github.com:redhat-partner-solutions/vse-sync-test.git "$TEMPDIR/old_tests"
cd "$TOPDIR"
git remote add old-tests-import "$TEMPDIR/old_tests"
git fetch old-tests-import main
git merge --allow-unrelated-histories old-tests-import/main -m "Import vse-sync-test at top level"
git remote rm old-tests-import

# --- Cleanup old remotes ---
git remote rm collector 2>/dev/null || true
git remote rm reporting 2>/dev/null || true
git remote rm old_tests_repo 2>/dev/null || true

echo "Import complete. Review with 'git log --oneline' and 'ls -la'."
