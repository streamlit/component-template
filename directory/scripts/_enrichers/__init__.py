from __future__ import annotations

from .github import GitHubEnricher  # type: ignore[import-not-found]
from .pypi import PyPiEnricher  # type: ignore[import-not-found]
from .pypistats import PyPiStatsEnricher  # type: ignore[import-not-found]


def get_default_enrichers(*, github_token_env: str = "GH_TOKEN") -> list:
    return [
        GitHubEnricher(token_env=github_token_env),
        PyPiEnricher(),
        PyPiStatsEnricher(),
    ]
