from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from _utils.enrich import should_refetch
from _utils.enrichment_engine import FetchResult, Patch
from _utils.http import RetryConfig, fetch_json
from _utils.pypi_helpers import infer_pypi_project_from_piplink
from _utils.time import utc_now_iso

PYPISTATS_BASE = "https://pypistats.org/api/packages"


@dataclass(frozen=True)
class PyPiStatsResult:
    project: str
    last_day: int | None
    last_week: int | None
    last_month: int | None


def _get_project_for_component(comp: dict[str, Any]) -> str | None:
    p = comp.get("pypi")
    if isinstance(p, str) and p.strip():
        return p.strip()
    return infer_pypi_project_from_piplink(comp.get("pipLink"))


def _pypistats_recent_url(project: str) -> str:
    return f"{PYPISTATS_BASE}/{project}/recent"


class PyPiStatsEnricher:
    name = "pypistats"
    bucket = "pypistats"

    def __init__(self) -> None:
        self._retry_cfg = RetryConfig(retry_statuses=(429, 500, 502, 503, 504))

    def key_for_component(self, comp: dict[str, Any]) -> str | None:
        return _get_project_for_component(comp)

    def needs_fetch(
        self, comp: dict[str, Any], refresh_older_than_hours: float | None
    ) -> bool:
        metrics = comp.get("metrics") if isinstance(comp.get("metrics"), dict) else None
        pypistats_metrics = (
            metrics.get("pypistats") if isinstance(metrics, dict) else None
        )
        existing_fetched_at = (
            pypistats_metrics.get("fetchedAt")
            if isinstance(pypistats_metrics, dict)
            else None
        )
        stale = (
            pypistats_metrics.get("isStale")
            if isinstance(pypistats_metrics, dict)
            else None
        )
        return should_refetch(
            fetched_at=(
                existing_fetched_at if isinstance(existing_fetched_at, str) else None
            ),
            is_stale=stale if isinstance(stale, bool) else None,
            refresh_older_than_hours=refresh_older_than_hours,
        )

    def fetch(self, key: str, ctx) -> FetchResult:
        url = _pypistats_recent_url(key)
        headers = {
            "Accept": "application/json",
            "User-Agent": "component-gallery-enrich-pypistats",
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
        data = r.data.get("data") if isinstance(r.data, dict) else None
        if not isinstance(data, dict):
            return FetchResult(
                ok=False,
                data=None,
                error="Missing data payload.",
                attempts=int(r.attempts),
                status=r.status,
            )

        def _as_int(x: Any) -> int | None:
            return int(x) if isinstance(x, int) and x >= 0 else None

        result = PyPiStatsResult(
            project=key,
            last_day=_as_int(data.get("last_day")),
            last_week=_as_int(data.get("last_week")),
            last_month=_as_int(data.get("last_month")),
        )
        return FetchResult(
            ok=True, data=result, error=None, attempts=int(r.attempts), status=r.status
        )

    def patch_success(
        self, comp: dict[str, Any], result: PyPiStatsResult, fetched_at: str
    ) -> Patch:
        updates = {
            "lastDay": result.last_day,
            "lastWeek": result.last_week,
            "lastMonth": result.last_month,
            "fetchedAt": fetched_at or utc_now_iso(),
            "isStale": False,
        }
        return Patch(bucket=self.bucket, updates=updates, changed=True)

    def patch_failure(self, comp: dict[str, Any], error: str | None) -> Patch:
        return Patch(bucket=self.bucket, updates={"isStale": True}, changed=False)
