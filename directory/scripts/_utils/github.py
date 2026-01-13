from __future__ import annotations

from urllib.parse import urlparse


def normalize_github_repo_url(url: str) -> str:
    """Canonicalize `https://github.com/<owner>/<repo>` (no trailing slash)."""
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.netloc != "github.com":
        raise ValueError(f"Not a GitHub HTTPS URL: {url}")
    parts = [p for p in parsed.path.split("/") if p]
    if len(parts) < 2:
        raise ValueError(f"Not a GitHub repo URL: {url}")
    owner, repo = parts[0], parts[1]
    return f"https://github.com/{owner}/{repo}"


def parse_owner_repo(github_url: str) -> tuple[str, str]:
    canonical = normalize_github_repo_url(github_url)
    parsed = urlparse(canonical)
    parts = [p for p in parsed.path.split("/") if p]
    return parts[0], parts[1]


def repo_key(github_url: str) -> str:
    """Stable identifier `owner/repo` (lowercased)."""
    owner, repo = parse_owner_repo(github_url)
    return f"{owner.lower()}/{repo.lower()}"
