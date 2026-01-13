from __future__ import annotations

import threading
import time
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any, Callable, Iterable, Protocol, cast

import requests

from .metrics import Bucket, ensure_bucket


class Enricher(Protocol):
    name: str
    bucket: str

    def key_for_component(self, comp: dict[str, Any]) -> Any | None: ...

    def needs_fetch(
        self, comp: dict[str, Any], refresh_older_than_hours: float | None
    ) -> bool: ...

    def fetch(self, key: Any, ctx: "EnricherContext") -> "FetchResult": ...

    def patch_success(
        self, comp: dict[str, Any], result: Any, fetched_at: str
    ) -> "Patch": ...

    def patch_failure(self, comp: dict[str, Any], error: str | None) -> "Patch": ...


@dataclass(frozen=True)
class FetchResult:
    ok: bool
    data: Any | None
    error: str | None
    attempts: int
    status: int | None = None


@dataclass(frozen=True)
class Patch:
    bucket: str
    updates: dict[str, Any]
    changed: bool = True


@dataclass(frozen=True)
class Failure:
    key: str
    status: int | None
    error: str | None


@dataclass
class ServiceStats:
    processed: int = 0
    requests: int = 0
    ok: int = 0
    failed: int = 0
    updated: int = 0
    skipped_fresh: int = 0
    skipped_no_key: int = 0
    cache_hits: int = 0


class ServiceLimiter:
    def __init__(self, min_interval_s: float) -> None:
        self._min_interval_s = max(0.0, float(min_interval_s))
        self._lock = threading.Lock()
        self._next_allowed = 0.0

    def acquire(self) -> None:
        if self._min_interval_s <= 0:
            return
        wait_s = 0.0
        with self._lock:
            now = time.monotonic()
            if now < self._next_allowed:
                wait_s = self._next_allowed - now
            self._next_allowed = max(now, self._next_allowed) + self._min_interval_s
        if wait_s > 0:
            time.sleep(wait_s)


class ThreadLocalSession:
    def __init__(self) -> None:
        self._tls = threading.local()

    def get(self) -> requests.Session:
        sess = getattr(self._tls, "session", None)
        if sess is None:
            sess = requests.Session()
            self._tls.session = sess
        return sess


@dataclass
class EnricherContext:
    name: str
    limiter: ServiceLimiter
    session_getter: Callable[[], requests.Session]
    timeout_s: float

    def request_json(
        self,
        *,
        url: str,
        headers: dict[str, str] | None,
        fetcher: Callable[..., Any],
        retry_cfg: Any,
    ) -> Any:
        self.limiter.acquire()
        session = self.session_getter()
        return fetcher(
            session=session,
            url=url,
            headers=headers,
            timeout_s=self.timeout_s,
            retry=retry_cfg,
        )


@dataclass
class EngineRunResult:
    stats: dict[str, ServiceStats]
    failures: dict[str, list[Failure]]


def run_enrichment_engine(
    *,
    components: list[dict[str, Any]],
    enrichers: Iterable[Enricher],
    refresh_older_than_hours: float | None,
    timeout_s: float,
    sleep_by_service: dict[str, float],
    workers: int,
    run_fetched_at: str,
    progress_every: int | None = None,
) -> EngineRunResult:
    enricher_list = list(enrichers)
    stats: dict[str, ServiceStats] = {e.name: ServiceStats() for e in enricher_list}
    failures: dict[str, list[Failure]] = {e.name: [] for e in enricher_list}

    inflight: dict[tuple[str, Any], tuple[Enricher, Any, Future[FetchResult]]] = {}
    future_meta: dict[Future[FetchResult], tuple[str, Any]] = {}
    comp_tasks: list[list[tuple[Enricher, Future[FetchResult]]]] = [
        [] for _ in range(len(components))
    ]

    limiter_by_service = {
        e.name: ServiceLimiter(sleep_by_service.get(e.name, 0.0)) for e in enricher_list
    }
    session_by_service = {e.name: ThreadLocalSession() for e in enricher_list}

    def submit_fetch(enricher: Enricher, key: Any) -> Future[FetchResult]:
        limiter = limiter_by_service[enricher.name]
        session_factory = session_by_service[enricher.name].get

        def _run() -> FetchResult:
            ctx = EnricherContext(
                name=enricher.name,
                limiter=limiter,
                session_getter=session_factory,
                timeout_s=timeout_s,
            )
            return enricher.fetch(key, ctx)

        return executor.submit(_run)

    with ThreadPoolExecutor(max_workers=max(1, int(workers))) as executor:
        for idx, comp in enumerate(components):
            if not isinstance(comp, dict):
                continue
            for enricher in enricher_list:
                stats[enricher.name].processed += 1
                if not enricher.needs_fetch(comp, refresh_older_than_hours):
                    stats[enricher.name].skipped_fresh += 1
                    continue
                key = enricher.key_for_component(comp)
                if key is None:
                    stats[enricher.name].skipped_no_key += 1
                    continue
                inflight_key = (enricher.name, key)
                if inflight_key in inflight:
                    stats[enricher.name].cache_hits += 1
                    fut = inflight[inflight_key][2]
                else:
                    fut = submit_fetch(enricher, key)
                    inflight[inflight_key] = (enricher, key, fut)
                    future_meta[fut] = (enricher.name, key)
                comp_tasks[idx].append((enricher, fut))

        # Apply patches deterministically by component index, resolving futures lazily
        # so progress can be reported as components complete.
        result_cache: dict[Future[FetchResult], FetchResult] = {}
        counted: set[Future[FetchResult]] = set()
        for idx, comp in enumerate(components):
            if not isinstance(comp, dict):
                continue
            for enricher, fut in comp_tasks[idx]:
                if fut in result_cache:
                    res = result_cache[fut]
                else:
                    res = fut.result()
                    result_cache[fut] = res
                if fut not in counted:
                    counted.add(fut)
                    meta = future_meta.get(fut)
                    if meta is not None:
                        service_name, key = meta
                    else:
                        service_name, key = enricher.name, "?"
                    stats[service_name].requests += int(res.attempts)
                    if res.ok:
                        stats[service_name].ok += 1
                    else:
                        stats[service_name].failed += 1
                        failures[service_name].append(
                            Failure(key=str(key), status=res.status, error=res.error)
                        )
                if res.ok:
                    patch = enricher.patch_success(comp, res.data, run_fetched_at)
                else:
                    patch = enricher.patch_failure(comp, res.error)
                bucket = ensure_bucket(comp, cast(Bucket, patch.bucket))
                for k, v in patch.updates.items():
                    bucket[k] = v
                if patch.changed:
                    stats[enricher.name].updated += 1

            if (
                progress_every
                and progress_every > 0
                and (idx + 1) % progress_every == 0
            ):
                for enricher in enricher_list:
                    s = stats[enricher.name]
                    print(
                        f"[{enricher.name}] requests={s.requests} "
                        f"ok={s.ok} fail={s.failed} "
                        f"updated={s.updated} skipped_fresh={s.skipped_fresh} "
                        f"cache_hits={s.cache_hits} skipped_no_key={s.skipped_no_key}",
                        flush=True,
                    )

    return EngineRunResult(stats=stats, failures=failures)
