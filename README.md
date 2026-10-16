# pain-miner-research

A small, read-only collector of **public product feedback** about AI developer
tools. It groups recurring complaints (bugs, setup friction, missing features)
so we can decide which problems are worth solving.

## What it does
- Searches Hacker News (Algolia API), public GitHub issues, and, once access is
  approved, a configurable list of subreddits via the **official Reddit OAuth API**.
- Stores only: product, source, permalink, date, and a short excerpt (max 280 chars).
- Writes JSON Lines locally for internal analysis.

## What it never does
- Never posts, comments, votes, or sends messages (Reddit scope: `read` only).
- Never stores usernames, author fields, or any personal data; builds no user profiles.
- Skips deleted or removed content.
- Never resells or shares data, and never uses it to train AI models.

## Volume
One run per day, typically **under 200 requests**, with a client-side rate limit
(>= 1.1 s between Reddit calls) and a descriptive User-Agent:
`python:pain-miner-research:v0.1.0 (read-only product feedback research) by /u/<username>`.

## Setup
Requires Python 3.9+ and no third-party packages.

```bash
cp config.example.json config.json   # edit products, queries, subreddits
cp .env.example .env                 # fill Reddit script-app credentials (optional)
set -a; . ./.env; set +a
python -m pain_miner.cli config.json out.jsonl
```

Reddit collection is skipped automatically unless all of `REDDIT_CLIENT_ID`,
`REDDIT_CLIENT_SECRET`, `REDDIT_USERNAME`, `REDDIT_PASSWORD` are set.
Credentials are read from environment variables only and are never committed.

## Data policy
Collected data stays local, is not committed (see `.gitignore`), and is used only
for internal analysis. Records whose source content is deleted are not kept.

## License
MIT
