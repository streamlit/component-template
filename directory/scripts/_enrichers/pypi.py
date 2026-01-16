from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from _utils.enrich import should_refetch
from _utils.enrichment_engine import FetchResult, Patch
from _utils.http import RetryConfig, fetch_json
from _utils.pypi_helpers import infer_pypi_project_from_piplink
from _utils.time import utc_now_iso

PYPI_BASE = "https://pypi.org/pypi"


@dataclass(frozen=True)
class PyPiResult:
    project: str
    latest_version: str | None
    latest_release_at: str | None


def _get_project_for_component(comp: dict[str, Any]) -> str | None:
    p = comp.get("pypi")
    if isinstance(p, str) and p.strip():
        return p.strip()
    return infer_pypi_project_from_piplink(comp.get("pipLink"))


def _pypi_api_url(project: str) -> str:
    return f"{PYPI_BASE}/{project}/json"


def _max_upload_time_iso(release_files: Any) -> str | None:
    if not isinstance(release_files, list):
        return None
    times: list[str] = []
    for f in release_files:
        if not isinstance(f, dict):
            continue
        t = f.get("upload_time_iso_8601") or f.get("upload_time")
        if isinstance(t, str) and t:
            times.append(t)
    return max(times) if times else None


class PyPiEnricher:
    name = "pypi"
    bucket = "pypi"

    def __init__(self) -> None:
        self._retry_cfg = RetryConfig(retry_statuses=(429, 500, 502, 503, 504))

    def key_for_component(self, comp: dict[str, Any]) -> str | None:
        return _get_project_for_component(comp)

    def needs_fetch(
        self, comp: dict[str, Any], refresh_older_than_hours: float | None
    ) -> bool:
        metrics = comp.get("metrics")
        pypi_metrics = metrics.get("pypi") if isinstance(metrics, dict) else None
        existing_fetched_at = (
            pypi_metrics.get("fetchedAt") if isinstance(pypi_metrics, dict) else None
        )
        stale = pypi_metrics.get("isStale") if isinstance(pypi_metrics, dict) else None
        return should_refetch(
            fetched_at=(
                existing_fetched_at if isinstance(existing_fetched_at, str) else None
            ),
            is_stale=stale if isinstance(stale, bool) else None,
            refresh_older_than_hours=refresh_older_than_hours,
        )

    def fetch(self, key: str, ctx) -> FetchResult:
        url = _pypi_api_url(key)
        headers = {
            "Accept": "application/json",
            "User-Agent": "component-gallery-enrich-pypi",
        }
        r = ctx.request_json(
            url=url,
            headers=headers,
            fetcher=fetch_json,
            retry_cfg=self._retry_cfg,
        )
        if not r.ok or not isinstance(r.data, dict):
            return FetchResult(
                ok=False,
                data=None,
                error=r.error or "Request failed.",
                attempts=int(r.attempts),
                status=r.status,
            )
        data = r.data
        info = data.get("info")
        releases = data.get("releases")
        if not isinstance(info, dict) or not isinstance(releases, dict):
            return FetchResult(
                ok=False,
                data=None,
                error="Missing info/releases.",
                attempts=int(r.attempts),
                status=r.status,
            )
        latest_version = info.get("version")
        latest_version = (
            str(latest_version)
            if isinstance(latest_version, str) and latest_version
            else None
        )

        latest_release_at: str | None = None
        if latest_version and latest_version in releases:
            latest_release_at = _max_upload_time_iso(releases.get(latest_version))
        if latest_release_at is None:
            best: str | None = None
            for _, files in releases.items():
                t = _max_upload_time_iso(files)
                if t and (best is None or t > best):
                    best = t
            latest_release_at = best

        result = PyPiResult(
            project=key,
            latest_version=latest_version,
            latest_release_at=latest_release_at,
        )
        return FetchResult(
            ok=True, data=result, error=None, attempts=int(r.attempts), status=r.status
        )

    def patch_success(
        self, comp: dict[str, Any], result: PyPiResult, fetched_at: str
    ) -> Patch:
        updates = {
            "latestVersion": result.latest_version,
            "latestReleaseAt": result.latest_release_at,
            "fetchedAt": fetched_at or utc_now_iso(),
            "isStale": False,
        }
        return Patch(bucket=self.bucket, updates=updates, changed=True)

    def patch_failure(self, comp: dict[str, Any], error: str | None) -> Patch:
        return Patch(bucket=self.bucket, updates={"isStale": True}, changed=False)
