"""Public GitHub issues (unauthenticated REST API)."""
from .common import RateLimiter, get_json, record

_lim = RateLimiter(1.0)


def issues(product, repo, pages=1):
    out = []
    for page in range(1, pages + 1):
        url = f"https://api.github.com/repos/{repo}/issues?state=all&per_page=100&page={page}"
        for i in get_json(url, limiter=_lim):
            if "pull_request" in i:
                continue
            out.append(record(product, "GitHub issues", i["html_url"], i.get("created_at"),
                              i.get("title", "") + " - " + (i.get("body") or "")))
    return out
