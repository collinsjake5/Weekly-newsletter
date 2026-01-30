"""
Reddit content collector.

Uses Reddit's public JSON API (no authentication required for public subreddits).
"""

import asyncio
import aiohttp
from datetime import datetime
from typing import List, Dict, Any, Optional
from .base import BaseCollector, ContentItem, SourceType


class RedditCollector(BaseCollector):
    """
    Collector for Reddit content.

    Uses Reddit's public JSON endpoints which don't require authentication.
    Rate limited to be respectful of Reddit's servers.
    """

    BASE_URL = "https://www.reddit.com"
    USER_AGENT = "WeeklyNewsletterBot/1.0 (Educational/Research Purpose)"

    # Rate limiting: Reddit allows ~60 requests per minute for unauthenticated
    REQUEST_DELAY = 1.0  # seconds between requests

    @property
    def source_type(self) -> SourceType:
        return SourceType.REDDIT

    async def collect(
        self,
        topics: List[str],
        subreddits: Optional[List[str]] = None,
        **kwargs
    ) -> List[ContentItem]:
        """
        Collect posts from specified subreddits.

        Args:
            topics: Keywords to filter relevance (used for scoring, not filtering)
            subreddits: List of subreddit names to fetch from

        Returns:
            List of ContentItem objects
        """
        if not subreddits:
            return []

        all_items = []

        async with aiohttp.ClientSession(
            headers={"User-Agent": self.USER_AGENT}
        ) as session:
            for subreddit in subreddits:
                try:
                    items = await self._fetch_subreddit(session, subreddit)
                    all_items.extend(items)
                    await asyncio.sleep(self.REQUEST_DELAY)
                except Exception as e:
                    print(f"Error fetching r/{subreddit}: {e}")

        # Filter by date
        return self.filter_by_date(all_items)

    async def _fetch_subreddit(
        self,
        session: aiohttp.ClientSession,
        subreddit: str,
        sort: str = "top",
        time_filter: str = "week",
        limit: int = 50
    ) -> List[ContentItem]:
        """
        Fetch posts from a single subreddit.

        Args:
            session: aiohttp session
            subreddit: Subreddit name (without r/)
            sort: Sort method (hot, new, top, rising)
            time_filter: Time filter for top (hour, day, week, month, year, all)
            limit: Maximum posts to fetch (max 100)

        Returns:
            List of ContentItem objects
        """
        url = f"{self.BASE_URL}/r/{subreddit}/{sort}.json"
        params = {
            "limit": min(limit, 100),
            "t": time_filter
        }

        async with session.get(url, params=params) as response:
            if response.status == 429:
                # Rate limited, wait and signal to retry
                print(f"Rate limited on r/{subreddit}, waiting...")
                await asyncio.sleep(60)
                return []

            if response.status != 200:
                print(f"Error {response.status} fetching r/{subreddit}")
                return []

            data = await response.json()

        items = []
        posts = data.get("data", {}).get("children", [])

        for post in posts:
            item = self._parse_post(post.get("data", {}), subreddit)
            if item:
                items.append(item)

        return items

    def _parse_post(self, post_data: Dict[str, Any], subreddit: str) -> Optional[ContentItem]:
        """
        Parse a Reddit post into a ContentItem.

        Args:
            post_data: Raw post data from Reddit API
            subreddit: Subreddit name

        Returns:
            ContentItem or None if parsing fails
        """
        try:
            # Extract timestamp
            created_utc = post_data.get("created_utc", 0)
            published_at = datetime.fromtimestamp(created_utc)

            # Build URL
            permalink = post_data.get("permalink", "")
            url = f"https://www.reddit.com{permalink}" if permalink else post_data.get("url", "")

            # Extract content
            title = post_data.get("title", "")
            selftext = post_data.get("selftext", "")

            # Truncate selftext if too long
            summary = selftext[:500] + "..." if len(selftext) > 500 else selftext
            if not summary:
                summary = None

            return ContentItem(
                title=title,
                url=url,
                source_type=self.source_type,
                source_name=f"r/{subreddit}",
                published_at=published_at,
                summary=summary,
                content=selftext if selftext else None,
                author=post_data.get("author", "[deleted]"),
                score=post_data.get("score", 0),
                num_comments=post_data.get("num_comments", 0),
                tags=[subreddit] + post_data.get("link_flair_text", "").split() if post_data.get("link_flair_text") else [subreddit],
                metadata={
                    "subreddit": subreddit,
                    "is_self": post_data.get("is_self", False),
                    "upvote_ratio": post_data.get("upvote_ratio", 0),
                    "distinguished": post_data.get("distinguished"),
                    "stickied": post_data.get("stickied", False),
                    "over_18": post_data.get("over_18", False),
                    "spoiler": post_data.get("spoiler", False),
                    "link_flair_text": post_data.get("link_flair_text"),
                }
            )
        except Exception as e:
            print(f"Error parsing Reddit post: {e}")
            return None

    async def fetch_post_comments(
        self,
        session: aiohttp.ClientSession,
        permalink: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Fetch top comments for a post.

        Args:
            session: aiohttp session
            permalink: Post permalink
            limit: Max comments to fetch

        Returns:
            List of comment data
        """
        url = f"{self.BASE_URL}{permalink}.json"
        params = {"limit": limit, "sort": "top"}

        async with session.get(url, params=params) as response:
            if response.status != 200:
                return []

            data = await response.json()

        # Comments are in the second element of the response
        if len(data) < 2:
            return []

        comments = []
        for comment in data[1].get("data", {}).get("children", []):
            comment_data = comment.get("data", {})
            if comment_data.get("body"):
                comments.append({
                    "body": comment_data.get("body", ""),
                    "author": comment_data.get("author", "[deleted]"),
                    "score": comment_data.get("score", 0),
                })

        return comments[:limit]
