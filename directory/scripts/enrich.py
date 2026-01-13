from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from _enrichers import get_default_enrichers  # type: ignore[import-not-found]
from _utils.enrichment_engine import (
    run_enrichment_engine,  # type: ignore[import-not-found]
)
from _utils.io import dump_json, load_json  # type: ignore[import-not-found]
from _utils.time import utc_now_iso  # type: ignore[import-not-found]


def _parse_services(raw: list[str] | None) -> list[str]:
    if not raw:
        return ["github", "pypi", "pypistats"]
    return [s.strip().lower() for s in raw if s.strip()]


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Enrich compiled/components.json using GitHub, PyPI, and pypistats."
    )
    parser.add_argument(
        "--in",
        dest="compiled_in",
        default=None,
        help="Input compiled catalog path (default: compiled/components.json).",
    )
    parser.add_argument(
        "--out",
        dest="compiled_out",
        default=None,
        help="Output compiled catalog path (default: overwrite --in).",
    )
    parser.add_argument(
        "--services",
        nargs="*",
        default=None,
        help="Which enrichers to run (default: github pypi pypistats).",
    )
    parser.add_argument(
        "--token-env",
        default="GH_TOKEN",
        help="Environment variable name holding a GitHub token (default: GH_TOKEN).",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=20.0,
        help="HTTP timeout in seconds (default: 20).",
    )
    parser.add_argument(
        "--sleep-github",
        type=float,
        default=None,
        help="Sleep between unique GitHub API requests in seconds.",
    )
    parser.add_argument(
        "--sleep-pypi",
        type=float,
        default=None,
        help="Sleep between unique PyPI API requests in seconds.",
    )
    parser.add_argument(
        "--sleep-pypistats",
        type=float,
        default=None,
        help="Sleep between unique pypistats API requests in seconds.",
    )
    parser.add_argument(
        "--refresh-older-than-hours",
        type=float,
        default=24.0,
        help=(
            "Only refetch metrics if existing fetchedAt values are older than this many "
            "hours (default: 24). Use 0 to refetch everything."
        ),
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Only process the first N components (debug).",
    )
    parser.add_argument(
        "--allow-failures",
        action="store_true",
        help="Do not fail the process if some enrichment fetches fail.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=max(4, (os.cpu_count() or 4) * 4),
        help="Max worker threads (default: 4 * CPU count).",
    )
    parser.add_argument(
        "--progress-every",
        dest="progress_every",
        type=int,
        default=25,
        help="Print progress every N processed components (default: 25). Use 0 to disable.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print per-service failure details.",
    )
    args = parser.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[1]
    compiled_in = (
        Path(args.compiled_in)
        if args.compiled_in
        else (repo_root / "compiled" / "components.json")
    )
    compiled_out = Path(args.compiled_out) if args.compiled_out else compiled_in

    if not compiled_in.is_file():
        print(f"ERROR: Missing compiled catalog: {compiled_in}", file=sys.stderr)
        return 2

    obj = load_json(compiled_in)
    if not isinstance(obj, dict):
        print(
            f"ERROR: compiled catalog must be a JSON object: {compiled_in}",
            file=sys.stderr,
        )
        return 2
    comps = obj.get("components")
    if not isinstance(comps, list):
        print(
            f"ERROR: compiled catalog missing `components` array: {compiled_in}",
            file=sys.stderr,
        )
        return 2

    services = _parse_services(args.services)
    enrichers = [
        e
        for e in get_default_enrichers(github_token_env=args.token_env)
        if e.name in services
    ]
    if not enrichers:
        print(f"ERROR: No valid services selected: {services}", file=sys.stderr)
        return 2

    has_gh_token = bool(
        os.environ.get(args.token_env)
        or os.environ.get("GH_TOKEN")
        or os.environ.get("GH_API_TOKEN")
        or os.environ.get("GITHUB_TOKEN")
    )
    github_sleep = (
        float(args.sleep_github)
        if args.sleep_github is not None
        else (0.2 if has_gh_token else 1.0)
    )
    pypi_sleep = float(args.sleep_pypi) if args.sleep_pypi is not None else 0.3
    pypistats_sleep = (
        float(args.sleep_pypistats) if args.sleep_pypistats is not None else pypi_sleep
    )

    sleep_by_service = {
        "github": github_sleep,
        "pypi": pypi_sleep,
        "pypistats": pypistats_sleep,
    }

    run_fetched_at = utc_now_iso()
    comps_for_run = comps if args.limit is None else comps[: int(args.limit)]
    expected_counts: dict[str, int] = {e.name: 0 for e in enrichers}
    for comp in comps_for_run:
        if not isinstance(comp, dict):
            continue
        for enricher in enrichers:
            if not enricher.needs_fetch(comp, args.refresh_older_than_hours):
                continue
            if enricher.key_for_component(comp) is None:
                continue
            expected_counts[enricher.name] += 1
    for enricher in enrichers:
        print(
            f"[{enricher.name}] will attempt {expected_counts[enricher.name]} component(s).",
            flush=True,
        )
    result = run_enrichment_engine(
        components=comps_for_run,
        enrichers=enrichers,
        refresh_older_than_hours=args.refresh_older_than_hours,
        timeout_s=float(args.timeout),
        sleep_by_service=sleep_by_service,
        workers=int(args.workers),
        run_fetched_at=run_fetched_at,
        progress_every=(
            int(args.progress_every) if args.progress_every is not None else None
        ),
    )

    dump_json(compiled_out, obj)

    ts = utc_now_iso()
    print(f"Wrote {compiled_out} at {ts}.")
    for enricher in enrichers:
        s = result.stats[enricher.name]
        print(
            f"[{enricher.name}] summary: processed={s.processed} "
            f"requests={s.requests} ok={s.ok} fail={s.failed} "
            f"updated={s.updated} skipped_fresh={s.skipped_fresh} "
            f"cache_hits={s.cache_hits} skipped_no_key={s.skipped_no_key}",
            flush=True,
        )

    any_failures = False
    for enricher in enrichers:
        fails = result.failures[enricher.name]
        if fails:
            any_failures = True
            print(
                f"WARNING: {len(fails)} {enricher.name} fetch failure(s):",
                file=sys.stderr,
            )
            for f in fails[:50]:
                code = f" (status {f.status})" if f.status is not None else ""
                print(f"- {f.key}{code}: {f.error}", file=sys.stderr)
            if len(fails) > 50:
                print(f"... and {len(fails) - 50} more", file=sys.stderr)
            if args.verbose:
                for f in fails:
                    code = f" (status {f.status})" if f.status is not None else ""
                    print(
                        f"[{enricher.name}] FAIL {f.key}{code}: {f.error}",
                        file=sys.stderr,
                    )

    if any_failures and not args.allow_failures:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
