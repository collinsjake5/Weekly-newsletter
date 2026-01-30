"""
Hacker News content collector.

Uses the official Hacker News API (free, no authentication required).
https://github.com/HackerNews/API
"""

import asyncio
import aiohttp
from datetime import datetime
from typing import List, Optional
from .base import BaseCollector, ContentItem, SourceType


class HackerNewsCollector(BaseCollector):
    """
    Collector for Hacker News content.

    Uses the official HN Firebase API which is free and doesn't require auth.
    """

    BASE_URL = "https://hacker-news.firebaseio.com/v0"

    # HN API is quite permissive but let's be respectful
    REQUEST_DELAY = 0.1  # seconds between requests
    MAX_CONCURRENT = 20  # max concurrent requests

    @property
    def source_type(self) -> SourceType:
        return SourceType.HACKERNEWS

    async def collect(
        self,
        topics: List[str],
        min_score: int = 50,
        max_items: int = 100,
        **kwargs
    ) -> List[ContentItem]:
        """
        Collect top stories from Hacker News.

        Args:
            topics: Keywords to filter relevance (used for scoring)
            min_score: Minimum HN points to include
            max_items: Maximum items to fetch

        Returns:
            List of ContentItem objects
        """
        async with aiohttp.ClientSession() as session:
            # Get top story IDs
            story_ids = await self._fetch_top_stories(session)

            # Limit the number we fetch
            story_ids = story_ids[:max_items]

            # Fetch story details concurrently
            items = await self._fetch_stories(session, story_ids)

        # Filter by score and date
        items = [item for item in items if item.score >= min_score]
        return self.filter_by_date(items)

    async def _fetch_top_stories(self, session: aiohttp.ClientSession) -> List[int]:
        """Fetch list of top story IDs."""
        url = f"{self.BASE_URL}/topstories.json"

        async with session.get(url) as response:
            if response.status != 200:
                return []
            return await response.json()

    async def _fetch_best_stories(self, session: aiohttp.ClientSession) -> List[int]:
        """Fetch list of best story IDs."""
        url = f"{self.BASE_URL}/beststories.json"

        async with session.get(url) as response:
            if response.status != 200:
                return []
            return await response.json()

    async def _fetch_stories(
        self,
        session: aiohttp.ClientSession,
        story_ids: List[int]
    ) -> List[ContentItem]:
        """
        Fetch multiple stories concurrently.

        Args:
            session: aiohttp session
            story_ids: List of story IDs to fetch

        Returns:
            List of ContentItem objects
        """
        semaphore = asyncio.Semaphore(self.MAX_CONCURRENT)

        async def fetch_one(story_id: int) -> Optional[ContentItem]:
            async with semaphore:
                item = await self._fetch_item(session, story_id)
                await asyncio.sleep(self.REQUEST_DELAY)
                return item

        tasks = [fetch_one(sid) for sid in story_ids]
        results = await asyncio.gather(*tasks)

        return [item for item in results if item is not None]

    async def _fetch_item(
        self,
        session: aiohttp.ClientSession,
        item_id: int
    ) -> Optional[ContentItem]:
        """
        Fetch a single HN item.

        Args:
            session: aiohttp session
            item_id: HN item ID

        Returns:
            ContentItem or None
        """
        url = f"{self.BASE_URL}/item/{item_id}.json"

        try:
            async with session.get(url) as response:
                if response.status != 200:
                    return None

                data = await response.json()

                if not data or data.get("type") != "story":
                    return None

                return self._parse_story(data)
        except Exception as e:
            print(f"Error fetching HN item {item_id}: {e}")
            return None

    def _parse_story(self, data: dict) -> Optional[ContentItem]:
        """
        Parse HN story data into ContentItem.

        Args:
            data: Raw story data from HN API

        Returns:
            ContentItem or None
        """
        try:
            # Extract timestamp
            timestamp = data.get("time", 0)
            published_at = datetime.fromtimestamp(timestamp)

            # Get URL (some stories are "Ask HN" etc with no URL)
            item_id = data.get("id", 0)
            url = data.get("url", f"https://news.ycombinator.com/item?id={item_id}")

            # HN discussion URL
            hn_url = f"https://news.ycombinator.com/item?id={item_id}"

            return ContentItem(
                title=data.get("title", ""),
                url=url,
                source_type=self.source_type,
                source_name="Hacker News",
                published_at=published_at,
                summary=data.get("text"),  # Only for text posts (Ask HN, etc.)
                author=data.get("by", "unknown"),
                score=data.get("score", 0),
                num_comments=data.get("descendants", 0),
                tags=self._extract_tags(data),
                metadata={
                    "hn_id": item_id,
                    "hn_url": hn_url,
                    "type": data.get("type"),
                    "is_text_post": "url" not in data,
                }
            )
        except Exception as e:
            print(f"Error parsing HN story: {e}")
            return None

    def _extract_tags(self, data: dict) -> List[str]:
        """Extract tags from HN story data."""
        tags = ["hackernews"]

        title = data.get("title", "").lower()

        # Common HN post types
        if title.startswith("ask hn"):
            tags.append("ask-hn")
        elif title.startswith("show hn"):
            tags.append("show-hn")
        elif title.startswith("tell hn"):
            tags.append("tell-hn")
        elif "hiring" in title:
            tags.append("hiring")

        return tags

    async def fetch_comments(
        self,
        session: aiohttp.ClientSession,
        story_id: int,
        limit: int = 10
    ) -> List[dict]:
        """
        Fetch top comments for a story.

        Args:
            session: aiohttp session
            story_id: Story ID
            limit: Max comments to fetch

        Returns:
            List of comment data
        """
        # First get the story to find comment IDs
        url = f"{self.BASE_URL}/item/{story_id}.json"

        async with session.get(url) as response:
            if response.status != 200:
                return []

            data = await response.json()

        comment_ids = data.get("kids", [])[:limit]

        comments = []
        for cid in comment_ids:
            comment_url = f"{self.BASE_URL}/item/{cid}.json"
            async with session.get(comment_url) as response:
                if response.status == 200:
                    comment_data = await response.json()
                    if comment_data and comment_data.get("text"):
                        comments.append({
                            "text": comment_data.get("text", ""),
                            "author": comment_data.get("by", "unknown"),
                        })
            await asyncio.sleep(self.REQUEST_DELAY)

        return comments
