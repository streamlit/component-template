from __future__ import annotations

from datetime import datetime, timezone

from .time import parse_iso8601


def should_refetch(
    *,
    fetched_at: str | None,
    is_stale: bool | None,
    refresh_older_than_hours: float | None,
) -> bool:
    """Return True if we should refetch a metric bucket.

    Rules:
    - If refresh_older_than_hours is None or <= 0: always refetch
    - If we have no parseable fetched_at: refetch
    - If is_stale is True: refetch
    - Otherwise, refetch only when fetched_at is older than refresh_older_than_hours
    """
    if refresh_older_than_hours is None or refresh_older_than_hours <= 0:
        return True
    if is_stale is True:
        return True

    dt = parse_iso8601(fetched_at)
    if not dt:
        return True

    age_h = (datetime.now(timezone.utc) - dt).total_seconds() / 3600.0
    return age_h >= refresh_older_than_hours


