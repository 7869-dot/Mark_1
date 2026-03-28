"""
integrations/twitter.py

Twitter / X integration — three tools:
  - twitter_post_tweet:    post a new tweet
  - twitter_read_timeline: read home timeline
  - twitter_search:        search recent tweets
"""

from __future__ import annotations

from config.logging import get_logger
from config.settings import settings
from integrations.base import BaseTool, ToolError

logger = get_logger(__name__)


def _get_client():
    try:
        import tweepy
        return tweepy.Client(
            bearer_token=settings.twitter_bearer_token,
            consumer_key=settings.twitter_api_key,
            consumer_secret=settings.twitter_api_secret,
            access_token=settings.twitter_access_token,
            access_token_secret=settings.twitter_access_token_secret,
        )
    except ImportError:
        raise ToolError("tweepy not installed. Run: pip install tweepy")


class TwitterPostTweet(BaseTool):
    name = "twitter_post_tweet"
    description = "Post a new tweet on Twitter/X. Keep it under 280 characters."
    parameters = {
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "Tweet content (max 280 characters)"},
            "reply_to_id": {"type": "string", "description": "Tweet ID to reply to (optional)"},
        },
        "required": ["text"],
    }

    def is_available(self) -> bool:
        return settings.has_twitter

    async def run(self, text: str, reply_to_id: str = "", **kwargs) -> str:
        if len(text) > 280:
            raise ToolError(f"Tweet too long: {len(text)} characters (max 280)")

        try:
            client = _get_client()
            params = {"text": text}
            if reply_to_id:
                params["in_reply_to_tweet_id"] = reply_to_id

            response = client.create_tweet(**params)
            tweet_id = response.data["id"]
            logger.info("twitter_posted", tweet_id=tweet_id)
            return f"Tweet posted successfully. Tweet ID: {tweet_id}"

        except ToolError:
            raise
        except Exception as e:
            raise ToolError(f"Failed to post tweet: {e}")


class TwitterReadTimeline(BaseTool):
    name = "twitter_read_timeline"
    description = "Read recent tweets from the authenticated user's home timeline."
    parameters = {
        "type": "object",
        "properties": {
            "max_results": {"type": "integer", "description": "Number of tweets to fetch (5-20)", "default": 10},
        },
        "required": [],
    }

    def is_available(self) -> bool:
        return settings.has_twitter

    async def run(self, max_results: int = 10, **kwargs) -> str:
        try:
            client = _get_client()
            response = client.get_home_timeline(
                max_results=min(max_results, 20),
                tweet_fields=["created_at", "author_id", "text"],
            )

            if not response.data:
                return "No tweets found in timeline."

            lines = []
            for tweet in response.data:
                lines.append(f"[{tweet.id}] {tweet.text[:200]}")

            return f"Recent timeline tweets:\n" + "\n---\n".join(lines)

        except ToolError:
            raise
        except Exception as e:
            raise ToolError(f"Failed to read timeline: {e}")


class TwitterSearch(BaseTool):
    name = "twitter_search"
    description = "Search recent tweets by keyword or hashtag."
    parameters = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query e.g. '#AI startup' or 'from:elonmusk'"},
            "max_results": {"type": "integer", "description": "Number of results (10-50)", "default": 10},
        },
        "required": ["query"],
    }

    def is_available(self) -> bool:
        return settings.has_twitter

    async def run(self, query: str, max_results: int = 10, **kwargs) -> str:
        try:
            client = _get_client()
            response = client.search_recent_tweets(
                query=query,
                max_results=max(10, min(max_results, 50)),  # API min is 10
                tweet_fields=["created_at", "text", "public_metrics"],
            )

            if not response.data:
                return f"No tweets found for: {query}"

            lines = []
            for tweet in response.data:
                metrics = tweet.public_metrics or {}
                likes = metrics.get("like_count", 0)
                rts = metrics.get("retweet_count", 0)
                lines.append(f"{tweet.text[:200]}\n  [likes: {likes}, retweets: {rts}]")

            return f"Search results for '{query}':\n" + "\n---\n".join(lines)

        except ToolError:
            raise
        except Exception as e:
            raise ToolError(f"Twitter search failed: {e}")
