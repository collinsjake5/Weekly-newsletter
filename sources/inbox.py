"""
URL Inbox collector.

Reads URLs from a simple text file (inbox.txt) and fetches their content.
Allows users to manually add interesting articles throughout the week.
"""

import asyncio
import aiohttp
import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple
from .base import BaseCollector, ContentItem, SourceType


class InboxCollector(BaseCollector):
    """
    Collector for manually added URLs from inbox.txt.

    Users can add URLs throughout the week, and they'll be included
    in the next newsletter run. The inbox is cleared after processing.
    """

    USER_AGENT = "WeeklyNewsletterBot/1.0 (Educational/Research Purpose)"
    REQUEST_TIMEOUT = 30

    def __init__(
        self,
        lookback_days: int = 7,
        inbox_path: str = "inbox.txt"
    ):
        """
        Initialize collector.

        Args:
            lookback_days: Number of days to look back (not really used here)
            inbox_path: Path to the inbox file
        """
        super().__init__(lookback_days)
        self.inbox_path = Path(inbox_path)

    @property
    def source_type(self) -> SourceType:
        return SourceType.RSS  # Treat as RSS/web content

    async def collect(
        self,
        topics: List[str],
        newsletter_type: Optional[str] = None,
        **kwargs
    ) -> List[ContentItem]:
        """
        Collect items from the inbox file.

        Args:
            topics: Keywords for relevance (used for auto-categorization)
            newsletter_type: If specified, only return items for this newsletter

        Returns:
            List of ContentItem objects
        """
        if not self.inbox_path.exists():
            return []

        # Parse the inbox file
        entries = self._parse_inbox()

        if not entries:
            return []

        # Filter by newsletter type if specified
        if newsletter_type:
            entries = [
                e for e in entries
                if e['type'] is None or e['type'] == newsletter_type
            ]

        # Fetch content for each URL
        items = await self._fetch_urls(entries)

        return items

    def _parse_inbox(self) -> List[dict]:
        """
        Parse the inbox file.

        Returns:
            List of dicts with 'url', 'note', and 'type' keys
        """
        entries = []

        try:
            with open(self.inbox_path, 'r') as f:
                for line in f:
                    line = line.strip()

                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue

                    entry = self._parse_line(line)
                    if entry:
                        entries.append(entry)

        except Exception as e:
            print(f"Error reading inbox: {e}")

        return entries

    def _parse_line(self, line: str) -> Optional[dict]:
        """
        Parse a single line from the inbox.

        Formats:
            https://example.com
            https://example.com | Note about article
            ai: https://example.com | Note
            robotics: https://example.com

        Returns:
            Dict with url, note, type or None
        """
        newsletter_type = None
        note = None

        # Check for newsletter type prefix
        type_match = re.match(r'^(ai|robotics):\s*(.+)$', line, re.IGNORECASE)
        if type_match:
            newsletter_type = type_match.group(1).lower()
            line = type_match.group(2)

        # Check for note suffix
        if '|' in line:
            parts = line.split('|', 1)
            line = parts[0].strip()
            note = parts[1].strip()

        # Validate URL
        url = line.strip()
        if not url.startswith(('http://', 'https://')):
            return None

        return {
            'url': url,
            'note': note,
            'type': newsletter_type
        }

    async def _fetch_urls(self, entries: List[dict]) -> List[ContentItem]:
        """
        Fetch content from all URLs.

        Args:
            entries: List of parsed inbox entries

        Returns:
            List of ContentItem objects
        """
        items = []

        async with aiohttp.ClientSession(
            headers={"User-Agent": self.USER_AGENT},
            timeout=aiohttp.ClientTimeout(total=self.REQUEST_TIMEOUT)
        ) as session:
            for entry in entries:
                try:
                    item = await self._fetch_url(session, entry)
                    if item:
                        items.append(item)
                except Exception as e:
                    print(f"Error fetching {entry['url']}: {e}")
                    # Still create an item with just the URL and note
                    items.append(self._create_fallback_item(entry))

                # Small delay between requests
                await asyncio.sleep(0.5)

        return items

    async def _fetch_url(
        self,
        session: aiohttp.ClientSession,
        entry: dict
    ) -> Optional[ContentItem]:
        """
        Fetch and parse a single URL.

        Args:
            session: aiohttp session
            entry: Inbox entry dict

        Returns:
            ContentItem or None
        """
        url = entry['url']

        try:
            async with session.get(url) as response:
                if response.status != 200:
                    return self._create_fallback_item(entry)

                html = await response.text()

                # Extract title and description from HTML
                title = self._extract_title(html) or url
                description = self._extract_description(html)

                # Use note as summary if provided, otherwise use description
                summary = entry['note'] or description

                return ContentItem(
                    title=title,
                    url=url,
                    source_type=self.source_type,
                    source_name="Manual Inbox",
                    published_at=datetime.now(),  # Use current time
                    summary=summary,
                    content=description,
                    author=None,
                    score=100,  # Give inbox items a boost
                    num_comments=0,
                    tags=["inbox", "curated"],
                    metadata={
                        "from_inbox": True,
                        "user_note": entry['note'],
                        "forced_type": entry['type'],
                    }
                )

        except asyncio.TimeoutError:
            return self._create_fallback_item(entry)
        except Exception as e:
            print(f"Error parsing {url}: {e}")
            return self._create_fallback_item(entry)

    def _create_fallback_item(self, entry: dict) -> ContentItem:
        """Create a basic item when URL fetch fails."""
        url = entry['url']

        # Try to extract domain for title
        domain = re.search(r'https?://(?:www\.)?([^/]+)', url)
        domain_name = domain.group(1) if domain else "Unknown"

        title = entry['note'] or f"Article from {domain_name}"

        return ContentItem(
            title=title,
            url=url,
            source_type=self.source_type,
            source_name="Manual Inbox",
            published_at=datetime.now(),
            summary=entry['note'],
            author=None,
            score=100,
            num_comments=0,
            tags=["inbox", "curated"],
            metadata={
                "from_inbox": True,
                "user_note": entry['note'],
                "forced_type": entry['type'],
                "fetch_failed": True,
            }
        )

    def _extract_title(self, html: str) -> Optional[str]:
        """Extract title from HTML."""
        # Try og:title first
        og_match = re.search(
            r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)["\']',
            html, re.IGNORECASE
        )
        if og_match:
            return self._clean_text(og_match.group(1))

        # Try twitter:title
        tw_match = re.search(
            r'<meta[^>]+name=["\']twitter:title["\'][^>]+content=["\']([^"\']+)["\']',
            html, re.IGNORECASE
        )
        if tw_match:
            return self._clean_text(tw_match.group(1))

        # Fall back to <title> tag
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
        if title_match:
            return self._clean_text(title_match.group(1))

        return None

    def _extract_description(self, html: str) -> Optional[str]:
        """Extract description from HTML."""
        # Try og:description first
        og_match = re.search(
            r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']+)["\']',
            html, re.IGNORECASE
        )
        if og_match:
            return self._clean_text(og_match.group(1))

        # Try meta description
        desc_match = re.search(
            r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']',
            html, re.IGNORECASE
        )
        if desc_match:
            return self._clean_text(desc_match.group(1))

        return None

    def _clean_text(self, text: str) -> str:
        """Clean extracted text."""
        if not text:
            return ""

        # Decode HTML entities
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        text = text.replace('&#39;', "'")
        text = text.replace('&nbsp;', ' ')

        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)

        return text.strip()

    def clear_inbox(self) -> int:
        """
        Clear the inbox file after processing.

        Returns:
            Number of entries that were cleared
        """
        if not self.inbox_path.exists():
            return 0

        # Count entries before clearing
        entries = self._parse_inbox()
        count = len(entries)

        # Rewrite with just the header
        header = """# URL Inbox
# ==========
# Add URLs here (one per line) throughout the week.
# They will be included in your next newsletter run.
#
# Format options:
#   https://example.com/article
#   https://example.com/article | Optional note about the article
#   ai: https://example.com/article | Force into AI newsletter
#   robotics: https://example.com/article | Force into Robotics newsletter
#
# Lines starting with # are ignored.
# This file is automatically cleared after each newsletter run.
#

"""
        with open(self.inbox_path, 'w') as f:
            f.write(header)

        if count > 0:
            print(f"📥 Cleared {count} items from inbox")

        return count

    def get_inbox_count(self) -> int:
        """Get number of URLs in inbox."""
        return len(self._parse_inbox())
