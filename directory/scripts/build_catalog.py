"""
Build the compiled Component Gallery catalog artifact.

This script compiles per-component submissions in `components/*.json` into a
single legacy-compatible artifact at `compiled/components.json` that the
Streamlit gallery app reads from local disk.

It also supports carrying forward "last-known-good" computed fields (e.g. stars)
from a previous compiled artifact to avoid regressing metrics when enrichment is
not yet implemented.

Run from the repo root (recommended):

    python directory/scripts/build_catalog.py

Common variants:

    # Write somewhere else
    python directory/scripts/build_catalog.py --out dist/components.json

    # Skip invalid component JSON files (prints errors and continues)
    python directory/scripts/build_catalog.py --skip-invalid

    # Explicitly choose the prior artifact used for carry-forward
    python directory/scripts/build_catalog.py --previous compiled/components.json
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from _utils.github import normalize_github_repo_url, repo_key
from _utils.io import dump_json, load_json
from _utils.time import utc_now_iso


@dataclass(frozen=True)
class ComponentBuildError:
    file: Path
    message: str
    json_path: str | None = None


def _load_json(path: Path) -> Any:
    return load_json(path)


def _load_schema(repo_root: Path) -> dict[str, Any]:
    schema_path = repo_root / "schemas" / "component.schema.json"
    obj = load_json(schema_path)
    if not isinstance(obj, dict):
        raise TypeError(f"Schema must be a JSON object: {schema_path}")
    return obj


def _taxonomy_categories(repo_root: Path) -> list[str]:
    """Return the fixed taxonomy categories, prefixed with 'All'."""
    schema = _load_schema(repo_root)
    try:
        enum = schema["properties"]["categories"]["items"]["enum"]
    except Exception as e:  # pragma: no cover
        raise KeyError(
            "Could not find taxonomy enum at "
            "schemas/component.schema.json::properties.categories.items.enum"
        ) from e
    if not isinstance(enum, list) or not all(isinstance(x, str) for x in enum):
        raise TypeError("Category enum must be a list of strings.")
    return ["All", *enum]


def _format_json_path(parts: Iterable[Any]) -> str:
    out: list[str] = []
    for p in parts:
        if isinstance(p, int):
            out.append(f"[{p}]")
        else:
            if out:
                out.append(".")
            out.append(str(p))
    return "".join(out) or "$"


def _validate_instance(
    instance: Any, schema: dict[str, Any]
) -> list[ComponentBuildError]:
    try:
        from jsonschema import Draft202012Validator  # type: ignore
    except Exception as e:  # pragma: no cover
        raise RuntimeError(
            "Missing dependency `jsonschema`.\n\n"
            "Install it with:\n"
            "  pip install jsonschema\n"
            "or add it to `component-gallery/requirements.txt`."
        ) from e

    validator = Draft202012Validator(schema)
    errors: list[ComponentBuildError] = []
    for err in sorted(validator.iter_errors(instance), key=lambda x: list(x.path)):
        errors.append(
            ComponentBuildError(
                file=Path("<in-memory>"),
                message=err.message,
                json_path=_format_json_path(err.path),
            )
        )
    return errors


def _normalize_github_repo_url(url: str) -> str:
    return normalize_github_repo_url(url)


def _component_key_from_github_url(url: str) -> str:
    return repo_key(url)


def _load_previous_index(previous_path: Path | None) -> dict[str, dict[str, Any]]:
    """Index previous compiled components by canonical github owner/repo."""
    if previous_path is None or not previous_path.is_file():
        return {}
    obj = load_json(previous_path)
    if not isinstance(obj, dict):
        return {}
    comps = obj.get("components", [])
    if not isinstance(comps, list):
        return {}

    out: dict[str, dict[str, Any]] = {}
    for c in comps:
        if not isinstance(c, dict):
            continue
        gh = c.get("gitHubUrl")
        if not isinstance(gh, str) or not gh:
            continue
        try:
            key = repo_key(gh)
        except Exception:
            continue
        out[key] = c
    return out


def _prev_int(prev: dict[str, Any], *path: str) -> int | None:
    cur: Any = prev
    for p in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(p)
    return int(cur) if isinstance(cur, int) else None


def _prev_str(prev: dict[str, Any], *path: str) -> str | None:
    cur: Any = prev
    for p in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(p)
    return str(cur) if isinstance(cur, str) else None


def _prev_bool(prev: dict[str, Any], *path: str) -> bool | None:
    cur: Any = prev
    for p in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(p)
    return bool(cur) if isinstance(cur, bool) else None


def _pip_cmd_from_submission(
    links: dict[str, Any], install: dict[str, Any] | None
) -> str | None:
    if isinstance(install, dict):
        pip_cmd = install.get("pip")
        if isinstance(pip_cmd, str) and pip_cmd.strip():
            return pip_cmd.strip()

    pkg = links.get("pypi")
    if isinstance(pkg, str) and pkg.strip():
        return f"pip install {pkg.strip()}"
    return None


def build_catalog(
    *,
    repo_root: Path,
    out_path: Path,
    components_dir: Path,
    previous_path: Path | None,
    skip_invalid: bool,
) -> tuple[dict[str, Any], list[ComponentBuildError]]:
    schema = _load_schema(repo_root)
    categories = _taxonomy_categories(repo_root)
    prev_index = _load_previous_index(previous_path)

    errors: list[ComponentBuildError] = []
    compiled_components: list[dict[str, Any]] = []

    if not components_dir.is_dir():
        raise FileNotFoundError(f"Missing components directory: {components_dir}")

    seen_keys: set[str] = set()
    for json_file in sorted(components_dir.glob("*.json")):
        try:
            submission = _load_json(json_file)
        except json.JSONDecodeError as e:
            errors.append(
                ComponentBuildError(file=json_file, message=str(e), json_path=None)
            )
            continue

        if not isinstance(submission, dict):
            errors.append(
                ComponentBuildError(
                    file=json_file,
                    message="Submission JSON must be an object.",
                    json_path="$",
                )
            )
            continue

        # Schema validation (so we can safely map fields)
        for ve in _validate_instance(submission, schema):
            errors.append(
                ComponentBuildError(
                    file=json_file,
                    message=ve.message,
                    json_path=ve.json_path,
                )
            )
        if any(e.file == json_file for e in errors) and not skip_invalid:
            continue
        if any(e.file == json_file for e in errors) and skip_invalid:
            # Skip this component but keep going.
            continue

        try:
            author_obj = submission["author"]
            links = submission["links"]
            governance = submission["governance"]
            title = submission["title"]

            author_github = author_obj["github"]
            github_url = normalize_github_repo_url(links["github"])
            key = repo_key(github_url)

            if key in seen_keys:
                errors.append(
                    ComponentBuildError(
                        file=json_file,
                        message=f"Duplicate component identity (same GitHub repo): {key}",
                        json_path="links.github",
                    )
                )
                continue
            seen_keys.add(key)

            pip_cmd = _pip_cmd_from_submission(links, submission.get("install"))
            pypi_project = links.get("pypi")
            if not isinstance(pypi_project, str) or not pypi_project.strip():
                pypi_project = None
            demo_url = links.get("demo")
            app_url = demo_url if isinstance(demo_url, str) else None

            media = (
                submission.get("media")
                if isinstance(submission.get("media"), dict)
                else None
            )
            image_url = media.get("image") if isinstance(media, dict) else None
            if not isinstance(image_url, str):
                image_url = None

            enabled = bool(governance.get("enabled", True))

            # Compiled per-component categories should NOT include "All".
            # "All" is an implied UI filter mode, not a real category assignment.
            submitted_categories = submission.get("categories", [])
            cat_list: list[str] = []
            if isinstance(submitted_categories, list):
                for c in submitted_categories:
                    if isinstance(c, str) and c != "All" and c not in cat_list:
                        cat_list.append(c)
            if not cat_list:
                raise ValueError(
                    "Per-component categories must be non-empty (and must not be 'All')."
                )

            prev = prev_index.get(key, {})
            if not isinstance(prev, dict):
                prev = {}

            # Prefer previous metrics.github stars if present, else (legacy) top-level stars.
            stars_val: int | None = _prev_int(prev, "metrics", "github", "stars")
            if stars_val is None:
                stars_val = _prev_int(prev, "stars")
            # Default to 0 to match the current gallery UI expectations.
            if stars_val is None:
                stars_val = 0

            prev_forks = _prev_int(prev, "metrics", "github", "forks")
            prev_open_issues = _prev_int(prev, "metrics", "github", "openIssues")
            prev_contributors = _prev_int(
                prev, "metrics", "github", "contributorsCount"
            )
            prev_last_push_at = _prev_str(prev, "metrics", "github", "lastPushAt")
            prev_fetched_at = _prev_str(prev, "metrics", "github", "fetchedAt")
            prev_is_stale = _prev_bool(prev, "metrics", "github", "isStale")
            prev_pypi = (
                prev.get("metrics", {}).get("pypi")
                if isinstance(prev.get("metrics"), dict)
                else None
            )
            prev_pypistats = (
                prev.get("metrics", {}).get("pypistats")
                if isinstance(prev.get("metrics"), dict)
                else None
            )

            social_url = f"https://github.com/{author_github}"

            compiled_components.append(
                {
                    "title": title,
                    "author": author_github,
                    "pipLink": pip_cmd,
                    "pypi": pypi_project,
                    "categories": cat_list,
                    "image": image_url,
                    "gitHubUrl": github_url,
                    "enabled": enabled,
                    "appUrl": app_url,
                    "socialUrl": social_url,
                    "metrics": {
                        "github": {
                            "stars": stars_val,
                            "forks": prev_forks,
                            "openIssues": prev_open_issues,
                            "contributorsCount": prev_contributors,
                            "lastPushAt": prev_last_push_at,
                            "fetchedAt": prev_fetched_at,
                            "isStale": prev_is_stale,
                        },
                        "pypi": prev_pypi,
                        "pypistats": prev_pypistats,
                    },
                }
            )
        except Exception as e:
            errors.append(
                ComponentBuildError(file=json_file, message=str(e), json_path=None)
            )
            if not skip_invalid:
                continue

    # Deterministic ordering for stable diffs.
    compiled_components.sort(
        key=lambda c: (c.get("gitHubUrl") or "", c.get("title") or "")
    )

    compiled = {
        "generatedAt": utc_now_iso(),
        "schemaVersion": 1,
        "categories": categories,
        "components": compiled_components,
    }
    return compiled, errors


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Build the compiled components catalog."
    )
    parser.add_argument(
        "--out",
        default=None,
        help="Output path for the compiled JSON (default: compiled/components.json).",
    )
    parser.add_argument(
        "--components-dir",
        default=None,
        help="Directory containing per-component JSON submissions (default: components/).",
    )
    parser.add_argument(
        "--previous",
        default=None,
        help=(
            "Path to a previous compiled artifact to carry forward metrics like stars. "
            "Defaults to compiled/components.json if present."
        ),
    )
    parser.add_argument(
        "--skip-invalid",
        action="store_true",
        help="Skip invalid component JSON files instead of failing the build.",
    )
    args = parser.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[1]

    out_path = (
        Path(args.out) if args.out else (repo_root / "compiled" / "components.json")
    )
    components_dir = (
        Path(args.components_dir) if args.components_dir else (repo_root / "components")
    )

    previous_path: Path | None
    if args.previous:
        previous_path = Path(args.previous)
    else:
        candidate = repo_root / "compiled" / "components.json"
        previous_path = candidate if candidate.is_file() else None

    compiled, errors = build_catalog(
        repo_root=repo_root,
        out_path=out_path,
        components_dir=components_dir,
        previous_path=previous_path,
        skip_invalid=args.skip_invalid,
    )

    if errors and not args.skip_invalid:
        print(
            "ERROR: build failed due to invalid component submissions:", file=sys.stderr
        )
        for e in errors:
            rel = e.file.relative_to(repo_root) if e.file.is_absolute() else e.file
            jp = f"{e.json_path}: " if e.json_path else ""
            print(f"- {rel}: {jp}{e.message}", file=sys.stderr)
        return 1

    dump_json(out_path, compiled)

    # Print a compact summary for CI logs
    ts = utc_now_iso()
    print(
        f"Wrote {len(compiled.get('components', []))} component(s) to {out_path} at {ts}."
    )
    if errors and args.skip_invalid:
        print(f"NOTE: Skipped {len(errors)} validation error(s).", file=sys.stderr)
        for e in errors:
            rel = e.file.relative_to(repo_root) if e.file.is_absolute() else e.file
            jp = f"{e.json_path}: " if e.json_path else ""
            print(f"- {rel}: {jp}{e.message}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
