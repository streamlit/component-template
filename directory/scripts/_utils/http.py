from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Any

import requests


def _maybe_int(s: str | None) -> int | None:
    if not isinstance(s, str) or not s.strip():
        return None
    try:
        return int(s.strip())
    except Exception:
        return None


def _retry_after_seconds(headers: dict[str, str] | None) -> int | None:
    if not headers:
        return None
    return _maybe_int(headers.get("Retry-After"))


@dataclass(frozen=True)
class RetryConfig:
    max_attempts: int = 6
    backoff_base_s: float = 0.5
    backoff_cap_s: float = 60.0
    retry_statuses: tuple[int, ...] = (403, 429, 500, 502, 503, 504)


@dataclass(frozen=True)
class FetchJsonResult:
    ok: bool
    status: int | None
    data: Any | None
    headers: dict[str, str] | None
    error: str | None
    attempts: int
    last_retry_after_s: int | None = None


def fetch_json(
    *,
    session: requests.Session,
    url: str,
    headers: dict[str, str] | None,
    timeout_s: float,
    retry: RetryConfig,
) -> FetchJsonResult:
    """GET a URL and parse JSON with retry/backoff.

    Retries on retry_statuses and on request-level exceptions.
    Honors integer Retry-After when present.
    """
    last_retry_after: int | None = None

    for attempt in range(1, max(1, retry.max_attempts) + 1):
        try:
            resp = session.get(url, headers=headers, timeout=timeout_s)
        except requests.RequestException as e:
            # Retryable network error.
            if attempt >= retry.max_attempts:
                return FetchJsonResult(
                    ok=False,
                    status=None,
                    data=None,
                    headers=None,
                    error=f"{type(e).__name__}: {e}",
                    attempts=attempt,
                    last_retry_after_s=last_retry_after,
                )
            wait_s = min(retry.backoff_cap_s, (2**attempt) * retry.backoff_base_s)
            wait_s = wait_s + random.random() * 0.25
            time.sleep(wait_s)
            continue

        status = int(resp.status_code)
        # Success path.
        if 200 <= status < 300:
            try:
                return FetchJsonResult(
                    ok=True,
                    status=status,
                    data=resp.json(),
                    headers=dict(resp.headers) if resp.headers else None,
                    error=None,
                    attempts=attempt,
                    last_retry_after_s=last_retry_after,
                )
            except Exception as e:
                return FetchJsonResult(
                    ok=False,
                    status=status,
                    data=None,
                    headers=dict(resp.headers) if resp.headers else None,
                    error=f"Invalid JSON payload: {e}",
                    attempts=attempt,
                    last_retry_after_s=last_retry_after,
                )

        # Non-success: decide whether to retry.
        body = None
        try:
            body = resp.text
        except Exception:
            body = None

        if status in retry.retry_statuses and attempt < retry.max_attempts:
            ra = _retry_after_seconds(dict(resp.headers) if resp.headers else None)
            if isinstance(ra, int):
                last_retry_after = ra
            wait_s = min(retry.backoff_cap_s, (2**attempt) * retry.backoff_base_s)
            if isinstance(ra, int):
                wait_s = max(wait_s, float(ra))
            wait_s = wait_s + random.random() * 0.25
            time.sleep(wait_s)
            continue

        # Final failure.
        msg = f"HTTP {status}"
        if body:
            msg = f"{msg}: {body[:5000]}"
        ra = _retry_after_seconds(dict(resp.headers) if resp.headers else None)
        return FetchJsonResult(
            ok=False,
            status=status,
            data=None,
            headers=dict(resp.headers) if resp.headers else None,
            error=msg + (f" (Retry-After={ra}s)" if isinstance(ra, int) else ""),
            attempts=attempt,
            last_retry_after_s=ra if isinstance(ra, int) else last_retry_after,
        )

    # Unreachable.
    return FetchJsonResult(
        ok=False,
        status=None,
        data=None,
        headers=None,
        error="Unknown error.",
        attempts=retry.max_attempts,
        last_retry_after_s=last_retry_after,
    )
