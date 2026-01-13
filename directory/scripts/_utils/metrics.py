from __future__ import annotations

from typing import Any, Literal

Bucket = Literal["github", "pypi", "pypistats"]


def ensure_metrics(comp: dict[str, Any]) -> dict[str, Any]:
    metrics = comp.get("metrics")
    if not isinstance(metrics, dict):
        metrics = {}
        comp["metrics"] = metrics
    return metrics


def ensure_bucket(comp: dict[str, Any], bucket: Bucket) -> dict[str, Any]:
    metrics = ensure_metrics(comp)
    b = metrics.get(bucket)
    if not isinstance(b, dict):
        b = {}
        metrics[bucket] = b
    return b
