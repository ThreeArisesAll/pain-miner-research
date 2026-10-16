"""Hacker News via the public Algolia search API."""
import urllib.parse
from .common import RateLimiter, get_json, record

_lim = RateLimiter(1.0)


def search(product, query, max_hits=100):
    url = ("https://hn.algolia.com/api/v1/search?tags=comment&hitsPerPage=%d&query=%s"
           % (max_hits, urllib.parse.quote(query)))
    out = []
    for h in get_json(url, limiter=_lim).get("hits", []):
        text = h.get("comment_text")
        if not text:
            continue
        out.append(record(product, "HN",
                          f"https://news.ycombinator.com/item?id={h['objectID']}",
                          h.get("created_at"), text))
    return out
