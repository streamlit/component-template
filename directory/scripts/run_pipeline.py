"""
Run the full Component Gallery pipeline with a single entrypoint.

Default pipeline:

  1) Validate `components/*.json` submissions
  2) Build `compiled/components.json`
  3) Validate `compiled/components.json`
  4) Enrich GitHub metrics
  5) Enrich PyPI metrics
  6) Compute ranking signals
  7) Validate `compiled/components.json` again

Run from the repo root (recommended):

    python directory/scripts/run_pipeline.py

Typical CI usage:

    # Build + validate only (no network)
    python directory/scripts/run_pipeline.py --no-enrich
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def _run(cmd: list[str]) -> int:
    proc = subprocess.run(cmd)
    return int(proc.returncode)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Run validate -> build -> enrich pipeline for the component gallery."
    )
    parser.add_argument(
        "--no-validate",
        action="store_true",
        help="Skip validation steps (not recommended).",
    )
    parser.add_argument(
        "--no-build",
        action="store_true",
        help="Skip build step (assumes compiled/components.json already exists).",
    )
    parser.add_argument(
        "--no-github",
        action="store_true",
        help="Skip GitHub enrichment.",
    )
    parser.add_argument(
        "--no-pypi",
        action="store_true",
        help="Skip PyPI enrichment.",
    )
    parser.add_argument(
        "--no-pypistats",
        action="store_true",
        help="Skip PyPI download enrichment (pypistats).",
    )
    parser.add_argument(
        "--no-enrich",
        action="store_true",
        help="Skip all enrichment (equivalent to --no-github --no-pypi).",
    )
    parser.add_argument(
        "--no-ranking",
        action="store_true",
        help="Skip ranking computation (not recommended).",
    )
    parser.add_argument(
        "--no-images",
        action="store_true",
        help="Skip image URL checking (requires outbound network).",
    )
    parser.add_argument(
        "--allow-enrich-failures",
        action="store_true",
        help="Do not fail the pipeline if some enrichment fetches fail.",
    )
    parser.add_argument(
        "--refresh-older-than-hours",
        type=float,
        default=24.0,
        help=(
            "Only refetch enrichment metrics if existing fetchedAt values are older "
            "than this many hours (default: 24). Use 0 to force refetching everything."
        ),
    )
    parser.add_argument(
        "--enrich-progress-every",
        type=int,
        default=None,
        help=(
            "Forwarded to enrichers as --progress-every N. "
            "Default: use each enricher's default."
        ),
    )
    parser.add_argument(
        "--enrich-verbose",
        action="store_true",
        help="Forwarded to enrichers as --verbose (prints per-request failures as they happen).",
    )
    parser.add_argument(
        "--enrich-sleep-github",
        type=float,
        default=None,
        help=(
            "Sleep between unique GitHub API requests in seconds. "
            "Default: 0.2 with GH_TOKEN set, else 1.0 (safer for large catalogs)."
        ),
    )
    parser.add_argument(
        "--enrich-sleep-pypi",
        type=float,
        default=None,
        help=(
            "Sleep between unique PyPI API requests in seconds. "
            "Default: 0.3 (safer for large catalogs)."
        ),
    )
    parser.add_argument(
        "--enrich-sleep-pypistats",
        type=float,
        default=None,
        help=(
            "Sleep between unique pypistats API requests in seconds. "
            "Default: reuse PyPI sleep (0.3 by default)."
        ),
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Only process the first N components for each enrichment step (debug).",
    )
    args = parser.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[1]
    py = sys.executable

    if args.no_enrich:
        args.no_github = True
        args.no_pypi = True
        args.no_pypistats = True

    # Choose conservative enrichment pacing defaults, especially for large catalogs.
    has_gh_token = bool(
        os.environ.get("GH_TOKEN")
        or os.environ.get("GH_API_TOKEN")
        or os.environ.get("GITHUB_TOKEN")
    )
    github_sleep = (
        float(args.enrich_sleep_github)
        if args.enrich_sleep_github is not None
        else (0.2 if has_gh_token else 1.0)
    )
    pypi_sleep = (
        float(args.enrich_sleep_pypi) if args.enrich_sleep_pypi is not None else 0.3
    )
    pypistats_sleep = (
        float(args.enrich_sleep_pypistats)
        if args.enrich_sleep_pypistats is not None
        else pypi_sleep
    )

    def run_step(name: str, cmd: list[str]) -> int:
        # Flush so headers appear before subprocess output in buffered environments.
        print(f"\n==> {name}\n$ {' '.join(cmd)}", flush=True)
        return _run(cmd)

    # 1) Validate submissions
    if not args.no_validate:
        rc = run_step(
            "Validate submissions", [py, str(repo_root / "scripts" / "validate.py")]
        )
        if rc != 0:
            return rc

    # 1b) Check image URLs (network). Keep this separate from schema validation so
    # CI can enforce it while local/offline runs can skip it.
    if not args.no_images:
        rc = run_step(
            "Check images",
            [py, str(repo_root / "scripts" / "enrich_images.py"), "--check-only"],
        )
        if rc != 0:
            return rc

    # 2) Build compiled artifact
    if not args.no_build:
        rc = run_step(
            "Build compiled catalog",
            [py, str(repo_root / "scripts" / "build_catalog.py")],
        )
        if rc != 0:
            return rc

    # 3) Validate compiled artifact
    if not args.no_validate:
        rc = run_step(
            "Validate compiled catalog",
            [py, str(repo_root / "scripts" / "validate.py"), "--compiled"],
        )
        if rc != 0:
            return rc

    # 4) Enrich (GitHub/PyPI/pypistats)
    services: list[str] = []
    if not args.no_github:
        services.append("github")
    if not args.no_pypi:
        services.append("pypi")
    if not args.no_pypistats:
        services.append("pypistats")

    if services:
        cmd = [
            py,
            str(repo_root / "scripts" / "enrich.py"),
            "--services",
            *services,
            "--sleep-github",
            str(github_sleep),
            "--sleep-pypi",
            str(pypi_sleep),
            "--sleep-pypistats",
            str(pypistats_sleep),
            "--refresh-older-than-hours",
            str(args.refresh_older_than_hours),
        ]
        if args.enrich_progress_every is not None:
            cmd += ["--progress-every", str(args.enrich_progress_every)]
        if args.enrich_verbose:
            cmd += ["--verbose"]
        if args.limit is not None:
            cmd += ["--limit", str(args.limit)]
        if args.allow_enrich_failures:
            cmd += ["--allow-failures"]
        rc = run_step("Enrich catalog", cmd)
        if rc != 0:
            return rc

    # 6) Compute ranking
    if not args.no_ranking:
        cmd = [py, str(repo_root / "scripts" / "compute_ranking.py")]
        if args.limit is not None:
            cmd += ["--limit", str(args.limit)]
        rc = run_step("Compute ranking", cmd)
        if rc != 0:
            return rc

    # 7) Final validate compiled artifact
    if not args.no_validate:
        rc = run_step(
            "Final validate compiled catalog",
            [py, str(repo_root / "scripts" / "validate.py"), "--compiled"],
        )
        if rc != 0:
            return rc

    print("\nOK: pipeline completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
