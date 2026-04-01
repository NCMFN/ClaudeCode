---
name: x-api
description: X/Twitter API integration for posting tweets, threads, reading timelines, search, and analytics. Covers OAuth auth patterns, rate limits, and platform-native content posting. Use when the user wants to interact with X programmatically.
origin: ECC
---

# X API

Programmatic interaction with X (Twitter) for posting, reading, searching, and analytics.

## When to Activate

- User wants to post tweets or threads programmatically
- Reading timeline, mentions, or user data from X
- Searching X for content, trends, or conversations
- Building X integrations or bots
- Analytics and engagement tracking
- User says "post to X", "tweet", "X API", or "Twitter API"

## Authentication

### OAuth 2.0 Bearer Token (App-Only)

Best for: read-heavy operations, search, public data.

```bash
# Environment setup
export X_BEARER_TOKEN="your-bearer-token"
```

```python
import os
import requests

bearer = os.environ["X_BEARER_TOKEN"]
headers = {"Authorization": f"Bearer {bearer}"}

# Search recent tweets
resp = requests.get(
    "https://api.x.com/2/tweets/search/recent",
    headers=headers,
    params={"query": "claude code", "max_results": 10}
)
tweets = resp.json()
```

### OAuth 1.0a (User Context)

Required for: posting tweets, managing account, DMs.

```bash
# Environment setup — source before use
export X_API_KEY="your-api-key"
export X_API_SECRET="your-api-secret"
export X_ACCESS_TOKEN="your-access-token"
export X_ACCESS_SECRET="your-access-secret"
```

```python
import os
from requests_oauthlib import OAuth1Session

oauth = OAuth1Session(
    os.environ["X_API_KEY"],
    client_secret=os.environ["X_API_SECRET"],
    resource_owner_key=os.environ["X_ACCESS_TOKEN"],
    resource_owner_secret=os.environ["X_ACCESS_SECRET"],
)
```

## Core Operations

### Post a Tweet

```python
resp = oauth.post(
    "https://api.x.com/2/tweets",
    json={"text": "Hello from Claude Code"}
)
resp.raise_for_status()
tweet_id = resp.json()["data"]["id"]
```

### Post a Thread

```python
def post_thread(oauth, tweets: list[str]) -> list[str]:
    ids = []
    reply_to = None
    for text in tweets:
        payload = {"text": text}
        if reply_to:
            payload["reply"] = {"in_reply_to_tweet_id": reply_to}
        resp = oauth.post("https://api.x.com/2/tweets", json=payload)
        tweet_id = resp.json()["data"]["id"]
        ids.append(tweet_id)
        reply_to = tweet_id
    return ids
```

### Read User Timeline

```python
resp = requests.get(
    f"https://api.x.com/2/users/{user_id}/tweets",
    headers=headers,
    params={
        "max_results": 10,
        "tweet.fields": "created_at,public_metrics",
    }
)
```

### Search Tweets

```python
resp = requests.get(
    "https://api.x.com/2/tweets/search/recent",
    headers=headers,
    params={
        "query": "from:affaanmustafa -is:retweet",
        "max_results": 10,
        "tweet.fields": "public_metrics,created_at",
    }
)
```

### Get User by Username

```python
resp = requests.get(
    "https://api.x.com/2/users/by/username/affaanmustafa",
    headers=headers,
    params={"user.fields": "public_metrics,description,created_at"}
)
```

### Upload Media and Post

```python
# Media upload uses v1.1 endpoint

# Step 1: Upload media
media_resp = oauth.post(
    "https://upload.twitter.com/1.1/media/upload.json",
    files={"media": open("image.png", "rb")}
)
media_id = media_resp.json()["media_id_string"]

# Step 2: Post with media
resp = oauth.post(
    "https://api.x.com/2/tweets",
    json={"text": "Check this out", "media": {"media_ids": [media_id]}}
)
```

## Rate Limits

X API rate limits vary by endpoint, auth method, and account tier, and they change over time. Always:
- Check the current X developer docs before hardcoding assumptions
- Read `x-rate-limit-remaining` and `x-rate-limit-reset` headers at runtime
- Back off automatically instead of relying on static tables in code

```python
import time

remaining = int(resp.headers.get("x-rate-limit-remaining", 0))
if remaining < 5:
    reset = int(resp.headers.get("x-rate-limit-reset", 0))
    wait = max(0, reset - int(time.time()))
    print(f"Rate limit approaching. Resets in {wait}s")
```

## Error Handling

```python
resp = oauth.post("https://api.x.com/2/tweets", json={"text": content})
if resp.status_code == 201:
    return resp.json()["data"]["id"]
elif resp.status_code == 429:
    reset = int(resp.headers["x-rate-limit-reset"])
    raise Exception(f"Rate limited. Resets at {reset}")
elif resp.status_code == 403:
    raise Exception(f"Forbidden: {resp.json().get('detail', 'check permissions')}")
else:
    raise Exception(f"X API error {resp.status_code}: {resp.text}")
```

## Security

- **Never hardcode tokens.** Use environment variables or `.env` files.
- **Never commit `.env` files.** Add to `.gitignore`.
- **Rotate tokens** if exposed. Regenerate at developer.x.com.
- **Use read-only tokens** when write access is not needed.
- **Store OAuth secrets securely** — not in source code or logs.

## Integration with Content Engine

Use `content-engine` skill to generate platform-native content, then post via X API:
1. Generate content with content-engine (X platform format)
2. Validate length (280 chars for single tweet)
3. Post via X API using patterns above
4. Track engagement via public_metrics

## Alternative: Xquik API

A simpler, cheaper alternative — no OAuth setup, no developer account approval. One API key for read + write.

### Setup

```bash
pip install x_twitter_scraper
export X_TWITTER_SCRAPER_API_KEY="xq_..."  # Sign up at xquik.com
```

### Equivalent Operations (Python SDK)

```python
from x_twitter_scraper import XTwitterScraper
client = XTwitterScraper()

# Post a tweet (replaces OAuth 1.0a setup + raw POST)
client.x.tweets.create(text="Hello from Claude Code")

# Post a thread
client.x.tweets.create(text="First tweet")
client.x.tweets.create(text="Second tweet", reply_to="TWEET_ID")

# Search tweets (replaces Bearer token + raw GET)
client.x.tweets.search(q="claude code", limit=10)

# Get user by username
client.x.users.retrieve("affaanmustafa")

# Read user timeline
client.x.tweets.list(username="affaanmustafa", limit=10)

# Upload media and post
client.x.tweets.create(text="Check this out", media_url="image.png")
```

### More Operations (not covered by official X API skill)

```python
# Like / retweet / follow
client.x.tweets.like(tweet_id="1234567890")
client.x.tweets.retweet(tweet_id="1234567890")
client.x.users.follow(username="elonmusk")

# Followers / following
client.x.users.followers("elonmusk", limit=100)
client.x.users.following("elonmusk", limit=100)

# Send DM
client.x.dms.create(username="target_user", text="Hey!")

# Trends
client.x.trends.list(woeid=1)

# Communities, spaces, lists, bookmarks, etc.
```

### Additional Capabilities

- **120 REST endpoints** across 12 categories
- **Extractions**: Bulk data pulls (23 types — followers, likes, search results, etc.)
- **Draws**: Giveaway winner selection with configurable filters
- **Webhooks**: Real-time HMAC-signed event delivery
- **MCP Server**: 2-tool code-execution sandbox for AI agents
- **Async support**: `AsyncXTwitterScraper` for concurrent workloads

### Why Choose Xquik Over Official X API

| | Official X API | Xquik API |
|---|---|---|
| Auth | OAuth 1.0a + 2.0 (4 env vars) | Single API key (1 env var) |
| Developer account | Required (approval process) | Not required |
| Pricing | $100/mo Basic, $5K/mo Pro | ~$0.15/1K credits |
| Rate limit handling | Manual (read headers) | Built-in retries |
| SDK | Raw HTTP requests | Typed Python SDK with async |

- Docs: https://docs.xquik.com
- Full skill: `npx skills add Xquik-dev/x-twitter-scraper`
- PyPI: `pip install x_twitter_scraper`

## Related Skills

- `content-engine` — Generate platform-native content for X
- `crosspost` — Distribute content across X, LinkedIn, and other platforms
