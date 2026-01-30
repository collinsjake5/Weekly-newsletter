"""
RSS/Atom feed collector.

Fetches and parses RSS/Atom feeds from various tech news sources.
"""

import asyncio
import aiohttp
from datetime import datetime
from typing import List, Dict, Any, Optional
from email.utils import parsedate_to_datetime
import re
from .base import BaseCollector, ContentItem, SourceType


class RSSCollector(BaseCollector):
    """
    Collector for RSS/Atom feeds.

    Supports both RSS 2.0 and Atom feed formats.
    """

    USER_AGENT = "WeeklyNewsletterBot/1.0 (Educational/Research Purpose)"
    REQUEST_DELAY = 0.5  # seconds between requests
    REQUEST_TIMEOUT = 30  # seconds

    @property
    def source_type(self) -> SourceType:
        return SourceType.RSS

    async def collect(
        self,
        topics: List[str],
        feeds: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> List[ContentItem]:
        """
        Collect items from RSS feeds.

        Args:
            topics: Keywords for relevance scoring
            feeds: List of feed configs [{"name": "...", "url": "..."}]

        Returns:
            List of ContentItem objects
        """
        if not feeds:
            return []

        all_items = []

        async with aiohttp.ClientSession(
            headers={"User-Agent": self.USER_AGENT},
            timeout=aiohttp.ClientTimeout(total=self.REQUEST_TIMEOUT)
        ) as session:
            for feed_config in feeds:
                try:
                    items = await self._fetch_feed(
                        session,
                        feed_config.get("url", ""),
                        feed_config.get("name", "Unknown")
                    )
                    all_items.extend(items)
                    await asyncio.sleep(self.REQUEST_DELAY)
                except Exception as e:
                    print(f"Error fetching feed {feed_config.get('name')}: {e}")

        # Filter by date
        return self.filter_by_date(all_items)

    async def _fetch_feed(
        self,
        session: aiohttp.ClientSession,
        url: str,
        source_name: str
    ) -> List[ContentItem]:
        """
        Fetch and parse a single RSS/Atom feed.

        Args:
            session: aiohttp session
            url: Feed URL
            source_name: Human-readable source name

        Returns:
            List of ContentItem objects
        """
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    print(f"Feed error {response.status}: {url}")
                    return []

                content = await response.text()

            # Try to parse with feedparser-like logic
            return self._parse_feed(content, source_name, url)

        except asyncio.TimeoutError:
            print(f"Timeout fetching feed: {url}")
            return []
        except Exception as e:
            print(f"Error fetching feed {url}: {e}")
            return []

    def _parse_feed(
        self,
        content: str,
        source_name: str,
        feed_url: str
    ) -> List[ContentItem]:
        """
        Parse RSS/Atom feed content.

        Uses basic XML parsing to handle both formats.
        """
        import xml.etree.ElementTree as ET

        items = []

        try:
            # Clean up content - remove encoding declarations that might cause issues
            content = re.sub(r'<\?xml[^>]*\?>', '', content)
            root = ET.fromstring(content)

            # Detect feed type and parse accordingly
            if 'feed' in root.tag.lower() or root.tag.endswith('}feed'):
                # Atom feed
                items = self._parse_atom(root, source_name)
            else:
                # RSS feed
                items = self._parse_rss(root, source_name)

        except ET.ParseError as e:
            print(f"XML parse error for {source_name}: {e}")
        except Exception as e:
            print(f"Error parsing feed {source_name}: {e}")

        return items

    def _parse_rss(self, root, source_name: str) -> List[ContentItem]:
        """Parse RSS 2.0 format."""
        items = []

        # Find channel/item elements
        channel = root.find('channel')
        if channel is None:
            channel = root

        for item in channel.findall('.//item'):
            try:
                content_item = self._parse_rss_item(item, source_name)
                if content_item:
                    items.append(content_item)
            except Exception as e:
                print(f"Error parsing RSS item: {e}")

        return items

    def _parse_rss_item(self, item, source_name: str) -> Optional[ContentItem]:
        """Parse a single RSS item."""
        title_elem = item.find('title')
        title = title_elem.text if title_elem is not None else ""

        link_elem = item.find('link')
        url = link_elem.text if link_elem is not None else ""

        if not title or not url:
            return None

        # Get description/content
        desc_elem = item.find('description')
        content_elem = item.find('{http://purl.org/rss/1.0/modules/content/}encoded')

        description = ""
        if content_elem is not None and content_elem.text:
            description = self._strip_html(content_elem.text)
        elif desc_elem is not None and desc_elem.text:
            description = self._strip_html(desc_elem.text)

        # Get publish date
        pub_date_elem = item.find('pubDate')
        published_at = datetime.now()
        if pub_date_elem is not None and pub_date_elem.text:
            try:
                published_at = parsedate_to_datetime(pub_date_elem.text).replace(tzinfo=None)
            except Exception:
                pass

        # Get author
        author_elem = item.find('author')
        dc_creator = item.find('{http://purl.org/dc/elements/1.1/}creator')
        author = None
        if author_elem is not None:
            author = author_elem.text
        elif dc_creator is not None:
            author = dc_creator.text

        # Get categories
        tags = [source_name.lower().replace(' ', '-')]
        for cat in item.findall('category'):
            if cat.text:
                tags.append(cat.text.lower())

        return ContentItem(
            title=title.strip(),
            url=url.strip(),
            source_type=self.source_type,
            source_name=source_name,
            published_at=published_at,
            summary=description[:500] + "..." if len(description) > 500 else description,
            content=description,
            author=author,
            score=0,
            num_comments=0,
            tags=tags[:10],  # Limit tags
            metadata={
                'feed_type': 'rss',
            }
        )

    def _parse_atom(self, root, source_name: str) -> List[ContentItem]:
        """Parse Atom format."""
        items = []

        # Handle namespace
        ns = {'atom': 'http://www.w3.org/2005/Atom'}

        # Try with namespace first, then without
        entries = root.findall('atom:entry', ns)
        if not entries:
            entries = root.findall('entry')
        if not entries:
            # Try finding entries with any namespace
            entries = root.findall('.//{http://www.w3.org/2005/Atom}entry')

        for entry in entries:
            try:
                content_item = self._parse_atom_entry(entry, source_name, ns)
                if content_item:
                    items.append(content_item)
            except Exception as e:
                print(f"Error parsing Atom entry: {e}")

        return items

    def _parse_atom_entry(self, entry, source_name: str, ns: dict) -> Optional[ContentItem]:
        """Parse a single Atom entry."""
        # Try with and without namespace
        def find_text(tag: str) -> str:
            elem = entry.find(f'atom:{tag}', ns)
            if elem is None:
                elem = entry.find(tag)
            if elem is None:
                elem = entry.find(f'{{http://www.w3.org/2005/Atom}}{tag}')
            return elem.text if elem is not None and elem.text else ""

        title = find_text('title').strip()

        # Get link - Atom can have multiple links
        url = ""
        for link in entry.findall('atom:link', ns) + entry.findall('link') + entry.findall('{http://www.w3.org/2005/Atom}link'):
            rel = link.get('rel', 'alternate')
            if rel == 'alternate' or not url:
                href = link.get('href', '')
                if href:
                    url = href

        if not title or not url:
            return None

        # Get content/summary
        content = find_text('content')
        summary = find_text('summary')
        description = self._strip_html(content or summary)

        # Get published date
        published_str = find_text('published') or find_text('updated')
        published_at = datetime.now()
        if published_str:
            try:
                # Handle ISO format
                published_at = datetime.fromisoformat(
                    published_str.replace('Z', '+00:00')
                ).replace(tzinfo=None)
            except Exception:
                pass

        # Get author
        author = None
        author_elem = entry.find('atom:author/atom:name', ns)
        if author_elem is None:
            author_elem = entry.find('author/name')
        if author_elem is None:
            author_elem = entry.find('{http://www.w3.org/2005/Atom}author/{http://www.w3.org/2005/Atom}name')
        if author_elem is not None:
            author = author_elem.text

        # Get categories
        tags = [source_name.lower().replace(' ', '-')]
        for cat in entry.findall('atom:category', ns) + entry.findall('category'):
            term = cat.get('term')
            if term:
                tags.append(term.lower())

        return ContentItem(
            title=title,
            url=url,
            source_type=self.source_type,
            source_name=source_name,
            published_at=published_at,
            summary=description[:500] + "..." if len(description) > 500 else description,
            content=description,
            author=author,
            score=0,
            num_comments=0,
            tags=tags[:10],
            metadata={
                'feed_type': 'atom',
            }
        )

    def _strip_html(self, text: str) -> str:
        """Remove HTML tags from text."""
        if not text:
            return ""

        # Remove HTML tags
        clean = re.sub(r'<[^>]+>', ' ', text)
        # Normalize whitespace
        clean = re.sub(r'\s+', ' ', clean)
        # Decode common HTML entities
        clean = clean.replace('&nbsp;', ' ')
        clean = clean.replace('&amp;', '&')
        clean = clean.replace('&lt;', '<')
        clean = clean.replace('&gt;', '>')
        clean = clean.replace('&quot;', '"')
        clean = clean.replace('&#39;', "'")

        return clean.strip()
