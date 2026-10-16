import html, json, re, time, urllib.request

USER_AGENT = "python:pain-miner-research:v0.1.0 (read-only product feedback research)"
EXCERPT_LEN = 280


class RateLimiter:
    def __init__(self, min_interval):
        self.min_interval, self._last = min_interval, 0.0

    def wait(self):
        d = time.monotonic() - self._last
        if d < self.min_interval:
            time.sleep(self.min_interval - d)
        self._last = time.monotonic()


def clean(text):
    text = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def excerpt(text, n=EXCERPT_LEN):
    t = clean(text)
    return t if len(t) <= n else t[: n - 1] + "\u2026"


def get_json(url, headers=None, limiter=None, data=None):
    if limiter:
        limiter.wait()
    h = {"User-Agent": USER_AGENT}
    h.update(headers or {})
    req = urllib.request.Request(url, headers=h, data=data)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def record(product, source, url, date, text):
    """The only shape stored: no author/username fields, ever."""
    return {"product": product, "source": source, "url": url,
            "date": (date or "")[:10], "excerpt": excerpt(text)}
