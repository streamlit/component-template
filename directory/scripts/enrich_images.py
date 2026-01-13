"""
Validate Component Gallery preview images (`media.image`) for stability + accessibility.

Rules enforced:
- `media.image` is optional (it may be missing, null, or an empty string). If present and non-empty:
- URL must be https://
- must not be a brittle proxy (e.g. `camo.githubusercontent.com`)
- must not contain signed/expiring query params (X-Amz-*, X-Goog-*, Signature/Expires/etc)
- must be fetchable (HTTP 2xx) and plausibly an image (best-effort via Content-Type)

Typical usage (from repo root):
  python directory/scripts/enrich_images.py --check-only

Notes:
- This script is intentionally check-only (no auto-fix, no caching).
- It requires outbound network access.
"""

from __future__ import annotations

import argparse
import os
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlparse

import requests
from _utils.image_url_policy import DISALLOWED_IMAGE_HOSTS, DISALLOWED_IMAGE_QUERY_KEYS
from _utils.io import load_json
from requests.adapters import HTTPAdapter

DEFAULT_TIMEOUT_S = 15.0
DEFAULT_WORKERS = min(32, max(4, (os.cpu_count() or 4) * 5))


def _is_https_url(url: str) -> bool:
    """Return True if a URL is a well-formed HTTPS URL.

    Parameters
    ----------
    url
        URL to check.

    Returns
    -------
    bool
        True if the URL uses the ``https`` scheme and has a non-empty network
        location (host).
    """
    p = urlparse(url)
    return p.scheme == "https" and bool(p.netloc)


def _is_disallowed_host(url: str) -> bool:
    """Return True if the URL host is disallowed for preview images.

    Parameters
    ----------
    url
        URL to check.

    Returns
    -------
    bool
        True if the URL host is in the disallowed host list.
    """
    host = (urlparse(url).netloc or "").lower()
    return host in DISALLOWED_IMAGE_HOSTS


def _has_disallowed_query_params(url: str) -> bool:
    """Return True if the URL includes signed/expiring query parameters.

    Parameters
    ----------
    url
        URL to check.

    Returns
    -------
    bool
        True if any query parameter key matches a disallowed key (case-insensitive).
    """
    for k, _ in parse_qsl(urlparse(url).query, keep_blank_values=True):
        if k.strip().lower() in DISALLOWED_IMAGE_QUERY_KEYS:
            return True
    return False


def _is_imageish_content_type(ct: str | None) -> bool:
    """Return True if an HTTP Content-Type is plausibly an image.

    Parameters
    ----------
    ct
        Content-Type header value (may be missing).

    Returns
    -------
    bool
        True if the value looks like an image MIME type (``image/*``), or if it
        is missing/blank, or if it is ``application/octet-stream`` (some CDNs
        mislabel images). This is intentionally permissive to avoid false negatives.
    """
    if not isinstance(ct, str) or not ct.strip():
        return True
    base = ct.split(";", 1)[0].strip().lower()
    if base.startswith("image/"):
        return True
    if base in {"application/octet-stream"}:
        return True
    return False


@dataclass(frozen=True)
class ImageCheck:
    """Result of a best-effort remote image URL check.

    Attributes
    ----------
    ok
        True if the URL was fetchable (HTTP 2xx).
    status
        HTTP status code if available.
    final_url
        Final URL after redirects if available.
    content_type
        Response Content-Type header if available.
    error
        Human-readable error string for failures.
    """

    ok: bool
    status: int | None
    final_url: str | None
    content_type: str | None
    error: str | None = None


_tls = threading.local()


def _get_thread_session(*, pool_maxsize: int) -> requests.Session:
    """Return a thread-local `requests.Session` for connection reuse.

    Parameters
    ----------
    pool_maxsize
        Max number of pooled connections to keep per host for the mounted adapters.

    Returns
    -------
    requests.Session
        A per-thread session instance.

    Notes
    -----
    `requests.Session` is not guaranteed to be thread-safe. Using one session per
    worker thread preserves connection pooling without cross-thread sharing.
    """
    s = getattr(_tls, "session", None)
    if s is None:
        s = requests.Session()
        adapter = HTTPAdapter(pool_connections=pool_maxsize, pool_maxsize=pool_maxsize)
        s.mount("https://", adapter)
        s.mount("http://", adapter)
        _tls.session = s
    return s


def _check_fetchable(
    session: requests.Session, url: str, *, timeout_s: float
) -> ImageCheck:
    """Fetch an image URL (HEAD then GET) and return an `ImageCheck`.

    Parameters
    ----------
    session
        `requests` session used to issue HTTP requests.
    url
        Image URL to fetch.
    timeout_s
        Per-request timeout in seconds.

    Returns
    -------
    ImageCheck
        Structured result containing status, final URL after redirects, and
        Content-Type (best-effort).

    Notes
    -----
    This function tries a ``HEAD`` request first (faster, less bandwidth). Some
    servers block or mishandle ``HEAD``; in that case we fall back to a streaming
    ``GET``.
    """
    headers = {"User-Agent": "component-gallery-image-check"}

    # HEAD first; fall back to GET (some servers block HEAD).
    try:
        with session.head(
            url, allow_redirects=True, timeout=timeout_s, headers=headers
        ) as r:
            status = int(r.status_code)
            ct = r.headers.get("Content-Type")
            if 200 <= status < 300:
                return ImageCheck(
                    ok=True,
                    status=status,
                    final_url=str(r.url),
                    content_type=ct,
                    error=None,
                )
    except requests.RequestException:
        # Some servers reject or mishandle HEAD requests; ignore the error and
        # fall back to a full GET request below.
        pass

    try:
        with session.get(
            url, allow_redirects=True, timeout=timeout_s, headers=headers, stream=True
        ) as r:
            status = int(r.status_code)
            ct = r.headers.get("Content-Type")
            if 200 <= status < 300:
                return ImageCheck(
                    ok=True,
                    status=status,
                    final_url=str(r.url),
                    content_type=ct,
                    error=None,
                )
            return ImageCheck(
                ok=False,
                status=status,
                final_url=str(r.url),
                content_type=ct,
                error=f"HTTP {status}",
            )
    except requests.RequestException as e:
        return ImageCheck(
            ok=False,
            status=None,
            final_url=None,
            content_type=None,
            error=f"{type(e).__name__}: {e}",
        )


def _get_media_image(obj: dict[str, Any]) -> str | None:
    """Extract a non-empty `media.image` string from a component JSON object.

    Parameters
    ----------
    obj
        Parsed JSON object for a component.

    Returns
    -------
    str | None
        The stripped image URL if present and non-empty; otherwise ``None``.
    """
    media = obj.get("media")
    if not isinstance(media, dict):
        return None
    img = media.get("image")
    return img.strip() if isinstance(img, str) and img.strip() else None


@dataclass(frozen=True)
class _FetchTask:
    """Unit of work for a single network fetch."""

    json_name: str
    url: str


@dataclass(frozen=True)
class _FetchResult:
    """Network fetch result for a single component JSON file."""

    json_name: str
    url: str
    chk: ImageCheck


def _fetch_one(
    task: _FetchTask, *, timeout_s: float, pool_maxsize: int
) -> _FetchResult:
    """Fetch one URL for a `_FetchTask` and return a `_FetchResult`.

    Parameters
    ----------
    task
        Task describing which component file the URL came from.
    timeout_s
        Per-request timeout in seconds.
    pool_maxsize
        Per-thread connection pool size for the thread-local session.

    Returns
    -------
    _FetchResult
        Result record with the originating JSON file name and `ImageCheck`.
    """
    session = _get_thread_session(pool_maxsize=pool_maxsize)
    chk = _check_fetchable(session, task.url, timeout_s=timeout_s)
    return _FetchResult(json_name=task.json_name, url=task.url, chk=chk)


def check_images(
    *,
    components_dir: Path,
    timeout_s: float,
    verbose: bool,
    workers: int,
) -> int:
    """Validate component preview image URLs under `components_dir`.

    Parameters
    ----------
    components_dir
        Directory containing `components/*.json` submission files.
    timeout_s
        Per-request timeout in seconds for image fetch checks.
    verbose
        If True, print an OK line for each successfully validated image.
    workers
        Maximum number of concurrent network fetches to run.

    Returns
    -------
    int
        Process-style return code: 0 if all checks pass, otherwise 1.

    Notes
    -----
    The validation happens in two phases:

    1. Local policy checks (HTTPS, disallowed hosts, disallowed query params).
    2. Network checks (fetchability + permissive Content-Type validation), run in
       parallel because they are I/O-bound.
    """
    failures = 0
    tasks: list[_FetchTask] = []
    local_failures: dict[str, str] = {}

    for json_file in sorted(components_dir.glob("*.json")):
        try:
            obj = load_json(json_file)
        except Exception as e:
            local_failures[json_file.name] = f"invalid JSON ({e})"
            continue
        if not isinstance(obj, dict):
            continue

        img = _get_media_image(obj)
        if not img:
            # Optional: null/empty is allowed.
            continue

        if not _is_https_url(img):
            local_failures[json_file.name] = f"not https:// ({img})"
            continue

        if _is_disallowed_host(img):
            local_failures[json_file.name] = f"disallowed_host=camo ({img})"
            continue

        if _has_disallowed_query_params(img):
            local_failures[json_file.name] = f"signed/expiring_url ({img})"
            continue

        tasks.append(_FetchTask(json_name=json_file.name, url=img))

    # Report local (non-network) failures deterministically.
    for json_name in sorted(local_failures.keys()):
        print(
            f"[images] FAIL {json_name}: {local_failures[json_name]}", file=sys.stderr
        )
        failures += 1

    # Network-bound checks: run in parallel (bounded).
    results_by_json: dict[str, _FetchResult] = {}
    if tasks:
        # Ensure a sane lower bound; allow workers=1 for debugging.
        w = max(1, int(workers))
        pool_maxsize = max(8, w)
        with ThreadPoolExecutor(max_workers=w) as ex:
            futs = [
                ex.submit(_fetch_one, t, timeout_s=timeout_s, pool_maxsize=pool_maxsize)
                for t in tasks
            ]
            for fut in as_completed(futs):
                r = fut.result()
                results_by_json[r.json_name] = r

        for json_name in sorted(results_by_json.keys()):
            r = results_by_json[json_name]
            chk = r.chk
            img = r.url

            if not chk.ok:
                print(
                    f"[images] FAIL {json_name}: unfetchable ({chk.error}) ({img})",
                    file=sys.stderr,
                )
                failures += 1
                continue

            if not _is_imageish_content_type(chk.content_type):
                print(
                    f"[images] FAIL {json_name}: non-image content-type ({chk.content_type}) ({img})",
                    file=sys.stderr,
                )
                failures += 1
                continue

            if verbose:
                print(f"[images] OK {json_name}: {chk.final_url or img}")

    print(f"[images] done: failures={failures}")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    """CLI entrypoint.

    Parameters
    ----------
    argv
        Command line arguments excluding the program name (i.e., ``sys.argv[1:]``).

    Returns
    -------
    int
        Process exit code:

        - 0: all checks passed
        - 1: one or more checks failed
        - 2: configuration error (e.g., missing components dir, offline mode set)
    """
    parser = argparse.ArgumentParser(
        description="Validate `media.image` URLs for components."
    )
    parser.add_argument(
        "--components-dir",
        default=None,
        help="Directory containing components/*.json (default: components/).",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Compatibility flag; this script is always check-only.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT_S,
        help=f"HTTP timeout in seconds (default: {DEFAULT_TIMEOUT_S}).",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=DEFAULT_WORKERS,
        help=f"Max parallel fetches (default: {DEFAULT_WORKERS}).",
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose output.")
    args = parser.parse_args(argv)

    if os.environ.get("COMPONENT_GALLERY_OFFLINE") == "1":
        print(
            "ERROR: COMPONENT_GALLERY_OFFLINE=1 set; image checks require network.",
            file=sys.stderr,
        )
        return 2

    project_root = Path(__file__).resolve().parents[1]
    components_dir = (
        Path(args.components_dir)
        if args.components_dir
        else (project_root / "components")
    )
    if not components_dir.is_dir():
        print(f"ERROR: components dir not found: {components_dir}", file=sys.stderr)
        return 2

    return check_images(
        components_dir=components_dir,
        timeout_s=float(args.timeout),
        verbose=bool(args.verbose),
        workers=int(args.workers),
    )


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
