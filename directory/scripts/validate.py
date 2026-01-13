"""
Validate Component Gallery JSON files.

This script validates:

- Source-of-truth component submissions: `components/*.json`
  against `schemas/component.schema.json`.
- Optionally, the compiled artifact: `compiled/components.json`
  against `schemas/compiled.schema.json` (use `--compiled`).

Run from the repo root (recommended):

    python directory/scripts/validate.py
    python directory/scripts/validate.py --compiled
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import parse_qsl, urlparse

from _utils.github import normalize_github_repo_url
from _utils.image_url_policy import DISALLOWED_IMAGE_HOSTS, DISALLOWED_IMAGE_QUERY_KEYS
from _utils.io import load_json


@dataclass(frozen=True)
class ValidationIssue:
    """A single schema validation issue tied to a specific JSON file."""

    file: Path
    schema: Path
    message: str
    json_path: str | None = None


def _format_json_path(parts: Iterable[Any]) -> str:
    """Format a jsonschema error path into a compact JSONPath-ish string.

    Parameters
    ----------
    parts
        Iterable of path parts (strings for object keys, ints for array indices),
        typically from `jsonschema.ValidationError.path`.

    Returns
    -------
    str
        A compact, human-readable path (e.g. ``$``, ``author.github``,
        ``components[0].title``).
    """
    out: list[str] = []
    for p in parts:
        if isinstance(p, int):
            out.append(f"[{p}]")
        else:
            if out:
                out.append(".")
            out.append(str(p))
    return "".join(out) or "$"


def _load_json(path: Path) -> Any:
    """Load a JSON file from disk.

    Parameters
    ----------
    path
        Path to a JSON file.

    Returns
    -------
    Any
        Parsed JSON data.
    """
    return load_json(path)


def _load_schema(path: Path) -> dict[str, Any]:
    """Load and sanity-check a JSON Schema from disk.

    Parameters
    ----------
    path
        Path to a JSON Schema file.

    Returns
    -------
    dict[str, Any]
        Parsed schema object.

    Raises
    ------
    TypeError
        If the schema file does not contain a JSON object.
    """
    obj = _load_json(path)
    if not isinstance(obj, dict):
        raise TypeError(f"Schema must be a JSON object: {path}")
    return obj


def _missing_required_fields(err: Any) -> list[str] | None:
    """Compute missing required field names for a jsonschema "required" error.

    jsonschema "required" errors can be noisy; this extracts the specific fields
    missing at the failing location so output stays readable.

    Parameters
    ----------
    err
        A `jsonschema.ValidationError` instance (typed as `Any` to keep this
        script dependency-light).

    Returns
    -------
    list[str] | None
        List of missing field names if applicable; otherwise ``None``.
    """
    if err.validator != "required" or not isinstance(err.validator_value, list):
        return None
    if not isinstance(err.instance, dict):
        return None
    # validator_value is the list of required fields for the schema at this path.
    required: list[str] = [str(x) for x in err.validator_value]
    return [k for k in required if k not in err.instance]


def _validate_one(instance_path: Path, schema_path: Path) -> list[ValidationIssue]:
    """Validate one JSON instance file against a JSON Schema.

    Parameters
    ----------
    instance_path
        Path to the JSON file to validate.
    schema_path
        Path to the JSON Schema file to validate against.

    Returns
    -------
    list[ValidationIssue]
        A (de-duplicated) list of validation issues for this file. Empty means
        the file is valid.

    Raises
    ------
    RuntimeError
        If the `jsonschema` dependency is not installed.
    TypeError
        If the schema file is not a JSON object.
    json.JSONDecodeError
        If either the schema or instance JSON cannot be parsed.
    """
    try:
        from jsonschema import Draft202012Validator  # type: ignore
    except Exception as e:  # pragma: no cover
        raise RuntimeError(
            "Missing dependency `jsonschema`.\n\n"
            "Install it with:\n"
            "  pip install jsonschema\n"
            "or add it to `component-gallery/requirements.txt`."
        ) from e

    schema = _load_schema(schema_path)
    instance = _load_json(instance_path)

    validator = Draft202012Validator(schema)
    issues: list[ValidationIssue] = []

    for err in sorted(validator.iter_errors(instance), key=lambda x: list(x.path)):
        # jsonschema gives a path deque; make it readable
        json_path = _format_json_path(err.path)
        message = err.message

        missing = _missing_required_fields(err)
        if missing:
            message = f"Missing required field(s): {', '.join(missing)}"

        issues.append(
            ValidationIssue(
                file=instance_path,
                schema=schema_path,
                message=message,
                json_path=json_path,
            )
        )

    # De-dupe identical messages (common when multiple schemas report the same root-level issue)
    deduped: list[ValidationIssue] = []
    seen: set[tuple[str, str]] = set()
    for issue in issues:
        key = (issue.json_path or "$", issue.message)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(issue)
    return deduped


def validate_components(repo_root: Path) -> list[ValidationIssue]:
    """Validate all source component submissions under `components/`.

    Parameters
    ----------
    repo_root
        Path to the component-gallery repo root.

    Returns
    -------
    list[ValidationIssue]
        Validation issues across all `components/*.json` files.
    """
    schema_path = repo_root / "schemas" / "component.schema.json"
    components_dir = repo_root / "components"

    issues: list[ValidationIssue] = []
    for json_file in sorted(components_dir.glob("*.json")):
        issues.extend(_validate_one(json_file, schema_path))
    return issues


def _is_https_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme == "https" and bool(parsed.netloc)


def _is_disallowed_url(url: str) -> bool:
    """Reject obvious XSS / unsafe schemes even if schema is relaxed."""
    parsed = urlparse(url)
    return parsed.scheme in {"javascript", "data", "file"}


# --- Image URL hardening -----------------------------------------------------
#
# We want preview images to remain stable over time. In practice, the most common
# sources of broken images are:
# - Signed / expiring URLs (S3/GCS/CloudFront style query params)
# - Proxy URLs like `camo.githubusercontent.com` (can change/expire and is not the
#   canonical image source)
#
# We enforce these constraints only for `media.image` (not general links).


def _has_disallowed_image_query_params(url: str) -> bool:
    parsed = urlparse(url)
    for k, _ in parse_qsl(parsed.query, keep_blank_values=True):
        if k.strip().lower() in DISALLOWED_IMAGE_QUERY_KEYS:
            return True
    return False


def _is_disallowed_image_host(url: str) -> bool:
    parsed = urlparse(url)
    host = (parsed.netloc or "").lower()
    return host in DISALLOWED_IMAGE_HOSTS


def validate_policies(
    repo_root: Path, *, max_component_bytes: int = 50_000
) -> list[ValidationIssue]:
    """Policy/lint checks beyond JSON Schema for `components/*.json`.

    This matches the tech spec's CI expectations:
    - Unique component identity (unique GitHub owner/repo across submissions)
    - HTTPS-only URLs
    - Basic abuse guardrails (file size)
    """
    schema_path = repo_root / "schemas" / "component.schema.json"
    components_dir = repo_root / "components"

    issues: list[ValidationIssue] = []
    first_by_repo: dict[str, Path] = {}

    for json_file in sorted(components_dir.glob("*.json")):
        # File size abuse guardrail
        try:
            size = json_file.stat().st_size
        except OSError as e:  # pragma: no cover
            issues.append(
                ValidationIssue(
                    file=json_file,
                    schema=schema_path,
                    message=f"Could not stat file: {e}",
                    json_path=None,
                )
            )
            continue
        if size > max_component_bytes:
            issues.append(
                ValidationIssue(
                    file=json_file,
                    schema=schema_path,
                    message=(
                        f"File too large ({size} bytes). "
                        f"Max allowed is {max_component_bytes} bytes."
                    ),
                    json_path=None,
                )
            )

        # Best-effort JSON load for lint checks (schema validation handled separately)
        try:
            obj = _load_json(json_file)
        except Exception:
            continue
        if not isinstance(obj, dict):
            continue

        links = obj.get("links")
        if not isinstance(links, dict):
            continue

        gh = links.get("github")
        if isinstance(gh, str) and gh:
            # Extra HTTPS enforcement (schema already restricts, but keep as policy)
            if _is_disallowed_url(gh) or not _is_https_url(gh):
                issues.append(
                    ValidationIssue(
                        file=json_file,
                        schema=schema_path,
                        message="URL must be https:// and must not use a disallowed scheme.",
                        json_path="links.github",
                    )
                )
            else:
                try:
                    canonical = normalize_github_repo_url(gh)
                    key = urlparse(canonical).path.lower().strip("/")
                    if key in first_by_repo:
                        issues.append(
                            ValidationIssue(
                                file=json_file,
                                schema=schema_path,
                                message=(
                                    f"Duplicate component identity: links.github repo `{key}` "
                                    f"already submitted in `{first_by_repo[key].name}`."
                                ),
                                json_path="links.github",
                            )
                        )
                    else:
                        first_by_repo[key] = json_file
                except Exception as e:
                    issues.append(
                        ValidationIssue(
                            file=json_file,
                            schema=schema_path,
                            message=str(e),
                            json_path="links.github",
                        )
                    )

        # Enforce HTTPS for other URL fields we accept
        for path, val in (
            ("links.demo", links.get("demo")),
            ("links.docs", links.get("docs")),
        ):
            if val is None:
                continue
            if isinstance(val, str):
                if _is_disallowed_url(val) or not _is_https_url(val):
                    issues.append(
                        ValidationIssue(
                            file=json_file,
                            schema=schema_path,
                            message="URL must be https:// and must not use a disallowed scheme.",
                            json_path=path,
                        )
                    )

        media = obj.get("media")
        if isinstance(media, dict):
            img = media.get("image")
            if img is None:
                # Image is optional; null is allowed.
                pass
            elif isinstance(img, str):
                if _is_disallowed_url(img) or not _is_https_url(img):
                    issues.append(
                        ValidationIssue(
                            file=json_file,
                            schema=schema_path,
                            message="URL must be https:// and must not use a disallowed scheme.",
                            json_path="media.image",
                        )
                    )
                elif _is_disallowed_image_host(img):
                    issues.append(
                        ValidationIssue(
                            file=json_file,
                            schema=schema_path,
                            message=(
                                "Image host is not allowed for `media.image` "
                                "(brittle proxy). Use a stable upstream URL instead."
                            ),
                            json_path="media.image",
                        )
                    )
                elif _has_disallowed_image_query_params(img):
                    issues.append(
                        ValidationIssue(
                            file=json_file,
                            schema=schema_path,
                            message=(
                                "Signed/expiring image URLs are not allowed for `media.image` "
                                "(disallowed query parameters detected)."
                            ),
                            json_path="media.image",
                        )
                    )
            else:
                issues.append(
                    ValidationIssue(
                        file=json_file,
                        schema=schema_path,
                        message="`media.image` must be a string URL or null.",
                        json_path="media.image",
                    )
                )

    return issues


def validate_compiled(repo_root: Path) -> list[ValidationIssue]:
    """Validate the compiled catalog artifact `compiled/components.json`.

    Parameters
    ----------
    repo_root
        Path to the component-gallery repo root.

    Returns
    -------
    list[ValidationIssue]
        Validation issues for the compiled artifact. If the artifact is missing,
        returns a single issue indicating it was skipped.
    """
    schema_path = repo_root / "schemas" / "compiled.schema.json"
    compiled_path = repo_root / "compiled" / "components.json"
    if not compiled_path.is_file():
        return [
            ValidationIssue(
                file=compiled_path,
                schema=schema_path,
                message="Compiled artifact not found (skipping).",
                json_path=None,
            )
        ]
    return _validate_one(compiled_path, schema_path)


def main(argv: list[str]) -> int:
    """CLI entrypoint.

    Parameters
    ----------
    argv
        CLI arguments excluding the program name (i.e., ``sys.argv[1:]``).

    Returns
    -------
    int
        Process exit code:

        - 0: success
        - 1: validation failed
        - 2: configuration error (missing required files/dirs)
    """
    parser = argparse.ArgumentParser(
        description="Validate Component Gallery JSON files."
    )
    parser.add_argument(
        "--compiled",
        action="store_true",
        help="Also validate compiled/components.json against schemas/compiled.schema.json.",
    )
    parser.add_argument(
        "--no-policy",
        action="store_true",
        help="Disable policy/lint checks beyond schema validation.",
    )
    parser.add_argument(
        "--max-component-bytes",
        type=int,
        default=50_000,
        help="Max allowed size for each components/*.json file (default: 50000).",
    )
    args = parser.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[1]

    all_issues: list[ValidationIssue] = []

    # Guardrails for common mistakes
    if not (repo_root / "schemas" / "component.schema.json").is_file():
        print("ERROR: Missing schema: schemas/component.schema.json", file=sys.stderr)
        return 2
    if not (repo_root / "components").is_dir():
        print("ERROR: Missing directory: components/", file=sys.stderr)
        return 2

    all_issues.extend(validate_components(repo_root))
    if not args.no_policy:
        all_issues.extend(
            validate_policies(repo_root, max_component_bytes=args.max_component_bytes)
        )
    if args.compiled:
        all_issues.extend(validate_compiled(repo_root))

    hard_errors = [i for i in all_issues if "skipping" not in i.message.lower()]

    if hard_errors:
        # Group and compress output by file for readability.
        by_file: dict[Path, list[ValidationIssue]] = defaultdict(list)
        for issue in hard_errors:
            by_file[issue.file].append(issue)

        total_files = len(by_file)
        print(
            f"Found {len(hard_errors)} validation error(s) across {total_files} file(s):",
            file=sys.stderr,
        )

        for file_path in sorted(by_file.keys()):
            issues = by_file[file_path]
            # All issues for a given file share the same schema in our usage.
            schema_path = issues[0].schema
            rel = (
                file_path.relative_to(repo_root)
                if file_path.is_absolute()
                else file_path
            )
            print(f"\n- {rel} ({len(issues)} error(s))", file=sys.stderr)
            print(f"  schema: {schema_path.relative_to(repo_root)}", file=sys.stderr)
            for issue in sorted(issues, key=lambda i: (i.json_path or "$", i.message)):
                jp = issue.json_path or "$"
                print(f"  - {jp}: {issue.message}", file=sys.stderr)
        return 1

    print("OK: all validated files passed.")
    # If the only issues are "compiled missing (skipping)", be explicit.
    skipped = [i for i in all_issues if "skipping" in i.message.lower()]
    for s in skipped:
        print(f"NOTE: {s.file} - {s.message}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
