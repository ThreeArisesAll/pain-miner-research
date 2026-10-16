"""Reddit via the official OAuth API (script app, read-only scope).

Credentials come only from environment variables:
  REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD
Only permalink, date and a short excerpt are stored. Author fields are never
read into the output, and deleted/removed content is skipped.
"""
import base64, datetime, os, time, urllib.parse
from .common import USER_AGENT, RateLimiter, get_json, record

API = "https://oauth.reddit.com"
_lim = RateLimiter(1.1)  # well under Reddit's published OAuth limits
_token = {"value": None, "exp": 0}
_REMOVED = {"[deleted]", "[removed]", ""}


def _ua():
    user = os.environ.get("REDDIT_USERNAME", "unknown")
    return f"{USER_AGENT} by /u/{user}"


def _auth():
    if _token["value"] and time.time() < _token["exp"] - 60:
        return _token["value"]
    cid, sec = os.environ["REDDIT_CLIENT_ID"], os.environ["REDDIT_CLIENT_SECRET"]
    body = urllib.parse.urlencode({
        "grant_type": "password", "scope": "read",
        "username": os.environ["REDDIT_USERNAME"],
        "password": os.environ["REDDIT_PASSWORD"]}).encode()
    basic = base64.b64encode(f"{cid}:{sec}".encode()).decode()
    d = get_json("https://www.reddit.com/api/v1/access_token", limiter=_lim, data=body,
                 headers={"Authorization": "Basic " + basic, "User-Agent": _ua()})
    _token.update(value=d["access_token"], exp=time.time() + d.get("expires_in", 3600))
    return _token["value"]


def _get(path):
    return get_json(API + path, limiter=_lim,
                    headers={"Authorization": "bearer " + _auth(), "User-Agent": _ua()})


def _date(ts):
    return datetime.datetime.fromtimestamp(ts or 0, datetime.timezone.utc).strftime("%Y-%m-%d")


def search(product, query, subreddits, limit=25):
    out = []
    for sub in subreddits:
        q = urllib.parse.urlencode({"q": query, "restrict_sr": 1, "limit": limit,
                                    "sort": "new", "raw_json": 1})
        for child in _get(f"/r/{sub}/search?{q}").get("data", {}).get("children", []):
            p = child.get("data", {})
            text = (p.get("title", "") + " " + p.get("selftext", "")).strip()
            if p.get("removed_by_category") or p.get("selftext") in ("[deleted]", "[removed]") \
                    or text in _REMOVED:
                continue
            out.append(record(product, "Reddit", "https://www.reddit.com" + p["permalink"],
                              _date(p.get("created_utc")), text))
    return out
