from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import parse_qs, urlparse

from _utils.enrich import should_refetch
from _utils.enrichment_engine import FetchResult, Patch
from _utils.github import parse_owner_repo
from _utils.http import RetryConfig, fetch_json
from _utils.time import utc_now_iso

GITHUB_API_BASE = "https://api.github.com"


@dataclass(frozen=True)
class GitHubResult:
    owner: str
    repo: str
    stars: int | None
    forks: int | None
    contributors_count: int | None
    open_issues: int | None
    pushed_at: str | None


def _github_repo_api_url(owner: str, repo: str) -> str:
    return f"{GITHUB_API_BASE}/repos/{owner}/{repo}"


def _github_contributors_api_url(owner: str, repo: str) -> str:
    return f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contributors?per_page=1"


_LINK_LAST_RE = re.compile(r'<([^>]+)>;\s*rel="last"')


def _parse_last_page_from_link_header(link: str | None) -> int | None:
    if not isinstance(link, str) or not link.strip():
        return None
    m = _LINK_LAST_RE.search(link)
    if not m:
        return None
    try:
        last_url = m.group(1)
        parsed = urlparse(last_url)
        qs = parse_qs(parsed.query)
        page_vals = qs.get("page")
        if not page_vals:
            return None
        page = int(page_vals[0])
        return page if page >= 0 else None
    except Exception:
        return None


def _get_token(token_env: str) -> str | None:
    token = os.environ.get(token_env)
    if token:
        return token.strip() or None
    for k in ("GH_TOKEN", "GH_API_TOKEN", "GITHUB_TOKEN"):
        token = os.environ.get(k)
        if token:
            return token.strip() or None
    return None


class GitHubEnricher:
    name = "github"
    bucket = "github"

    def __init__(self, *, token_env: str = "GH_TOKEN") -> None:
        self._token_env = token_env
        self._token = _get_token(token_env)
        self._retry_cfg = RetryConfig(retry_statuses=(403, 429, 500, 502, 503, 504))

    def key_for_component(self, comp: dict[str, Any]) -> tuple[str, str] | None:
        gh_url = comp.get("gitHubUrl")
        if not isinstance(gh_url, str) or not gh_url.strip():
            return None
        try:
            owner, repo = parse_owner_repo(gh_url)
        except Exception:
            return None
        return (owner.lower(), repo.lower())

    def needs_fetch(
        self, comp: dict[str, Any], refresh_older_than_hours: float | None
    ) -> bool:
        metrics = comp.get("metrics")
        gh_metrics = metrics.get("github") if isinstance(metrics, dict) else None
        existing_fetched_at = (
            gh_metrics.get("fetchedAt") if isinstance(gh_metrics, dict) else None
        )
        stale = gh_metrics.get("isStale") if isinstance(gh_metrics, dict) else None
        return should_refetch(
            fetched_at=(
                existing_fetched_at if isinstance(existing_fetched_at, str) else None
            ),
            is_stale=stale if isinstance(stale, bool) else None,
            refresh_older_than_hours=refresh_older_than_hours,
        )

    def _headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "component-gallery-enrich-github",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers

    def _fetch_contributors_count(
        self, *, ctx, owner: str, repo: str
    ) -> tuple[int | None, int, int | None, str | None]:
        url = _github_contributors_api_url(owner, repo)
        r = ctx.request_json(
            url=url,
            headers=self._headers(),
            fetcher=fetch_json,
            retry_cfg=self._retry_cfg,
        )
        if not r.ok or not isinstance(r.data, list):
            return None, r.attempts, r.status, r.error
        link = None
        if isinstance(r.headers, dict):
            link = r.headers.get("Link") or r.headers.get("link")
        last_page = _parse_last_page_from_link_header(link)
        if isinstance(last_page, int):
            return last_page, r.attempts, r.status, None
        return (1 if len(r.data) >= 1 else 0), r.attempts, r.status, None

    def fetch(self, key: tuple[str, str], ctx) -> FetchResult:
        owner, repo = key
        url = _github_repo_api_url(owner, repo)
        r = ctx.request_json(
            url=url,
            headers=self._headers(),
            fetcher=fetch_json,
            retry_cfg=self._retry_cfg,
        )
        attempts = int(r.attempts)
        if not r.ok or not isinstance(r.data, dict):
            return FetchResult(
                ok=False,
                data=None,
                error=r.error or "Request failed.",
                attempts=attempts,
                status=r.status,
            )

        data = r.data
        stars = data.get("stargazers_count")
        forks = data.get("forks_count")
        open_issues = data.get("open_issues_count")
        pushed_at = data.get("pushed_at")

        contributors_count, contrib_attempts, status, err = (
            self._fetch_contributors_count(ctx=ctx, owner=owner, repo=repo)
        )
        attempts += int(contrib_attempts)
        if err:
            return FetchResult(
                ok=False,
                data=None,
                error=err,
                attempts=attempts,
                status=status,
            )

        result = GitHubResult(
            owner=owner,
            repo=repo,
            stars=int(stars) if isinstance(stars, int) else None,
            forks=int(forks) if isinstance(forks, int) else None,
            contributors_count=(
                int(contributors_count)
                if isinstance(contributors_count, int) and contributors_count >= 0
                else None
            ),
            open_issues=int(open_issues) if isinstance(open_issues, int) else None,
            pushed_at=str(pushed_at) if isinstance(pushed_at, str) else None,
        )
        return FetchResult(
            ok=True, data=result, error=None, attempts=attempts, status=r.status
        )

    def patch_success(
        self, comp: dict[str, Any], result: GitHubResult, fetched_at: str
    ) -> Patch:
        metrics = comp.get("metrics")
        gh_metrics = metrics.get("github") if isinstance(metrics, dict) else None
        prev_stars = gh_metrics.get("stars") if isinstance(gh_metrics, dict) else None

        updates: dict[str, Any] = {}
        if isinstance(result.stars, int):
            updates["stars"] = result.stars
        if isinstance(result.forks, int):
            updates["forks"] = result.forks
        if isinstance(result.contributors_count, int):
            updates["contributorsCount"] = result.contributors_count
        if isinstance(result.open_issues, int):
            updates["openIssues"] = result.open_issues
        if isinstance(result.pushed_at, str):
            updates["lastPushAt"] = result.pushed_at
        updates["fetchedAt"] = fetched_at or utc_now_iso()
        updates["isStale"] = False

        changed = isinstance(result.stars, int) and prev_stars != result.stars
        return Patch(bucket=self.bucket, updates=updates, changed=changed)

    def patch_failure(self, comp: dict[str, Any], error: str | None) -> Patch:
        return Patch(bucket=self.bucket, updates={"isStale": True}, changed=False)
