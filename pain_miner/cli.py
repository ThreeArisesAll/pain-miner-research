"""Usage: python -m pain_miner.cli config.json output.jsonl"""
import json, os, sys
from . import github_issues, hn, reddit

MAX_REQUESTS_HINT = 200  # design budget per daily run


def main(argv=sys.argv[1:]):
    cfg_path, out_path = argv[0], argv[1]
    cfg = json.load(open(cfg_path))
    subs = cfg.get("subreddits", [])
    use_reddit = bool(subs) and all(os.environ.get(k) for k in (
        "REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET", "REDDIT_USERNAME", "REDDIT_PASSWORD"))
    rows, seen = [], set()
    for prod in cfg["products"]:
        name = prod["name"]
        for q in prod.get("queries", []):
            rows += hn.search(name, q)
            if use_reddit:
                rows += reddit.search(name, q, subs)
        if prod.get("github_repo"):
            rows += github_issues.issues(name, prod["github_repo"])
    with open(out_path, "w") as f:
        for r in rows:
            if r["url"] in seen or len(r["excerpt"]) < 15:
                continue
            seen.add(r["url"])
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"wrote {len(seen)} records to {out_path} (reddit={'on' if use_reddit else 'off'})")


if __name__ == "__main__":
    main()
