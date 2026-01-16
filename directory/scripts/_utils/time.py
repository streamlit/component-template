from __future__ import annotations

from datetime import datetime, timezone


def utc_now_iso() -> str:
    """UTC now in ISO8601 with Z suffix (e.g. 2025-12-19T00:00:00Z)."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_iso8601(dt: str | None) -> datetime | None:
    """Parse a subset of ISO8601/RFC3339 strings used by GitHub/PyPI.

    Accepts timestamps like:
    - 2025-11-30T12:33:58Z
    - 2025-11-23T22:30:23.036058Z
    - 2025-11-23T22:30:23+00:00

    Returns timezone-aware UTC datetimes when possible.
    """
    if not isinstance(dt, str) or not dt.strip():
        return None
    s = dt.strip()
    # `datetime.fromisoformat` doesn't accept "Z" suffix; normalize it.
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(s)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        # Assume UTC if tzinfo is missing (shouldn't happen with our sources)
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
