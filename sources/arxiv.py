"""
ArXiv content collector.

Uses the ArXiv API to fetch recent papers in AI/ML/Robotics categories.
https://arxiv.org/help/api/
"""

import asyncio
import aiohttp
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import List, Optional
from urllib.parse import urlencode
from .base import BaseCollector, ContentItem, SourceType


class ArxivCollector(BaseCollector):
    """
    Collector for ArXiv papers.

    Uses the ArXiv API which is free and doesn't require authentication.
    """

    BASE_URL = "http://export.arxiv.org/api/query"

    # ArXiv namespaces for XML parsing
    NAMESPACES = {
        'atom': 'http://www.w3.org/2005/Atom',
        'arxiv': 'http://arxiv.org/schemas/atom'
    }

    # ArXiv rate limits: 1 request per 3 seconds
    REQUEST_DELAY = 3.0

    # Category mappings for AI/ML/Robotics
    CATEGORY_MAP = {
        'cs.AI': 'Artificial Intelligence',
        'cs.LG': 'Machine Learning',
        'cs.CL': 'Computation and Language (NLP)',
        'cs.CV': 'Computer Vision',
        'cs.RO': 'Robotics',
        'cs.NE': 'Neural and Evolutionary Computing',
        'stat.ML': 'Machine Learning (Statistics)',
    }

    @property
    def source_type(self) -> SourceType:
        return SourceType.ARXIV

    async def collect(
        self,
        topics: List[str],
        categories: Optional[List[str]] = None,
        max_results: int = 50,
        **kwargs
    ) -> List[ContentItem]:
        """
        Collect papers from ArXiv.

        Args:
            topics: Keywords to search for
            categories: ArXiv category codes (e.g., 'cs.AI', 'cs.RO')
            max_results: Maximum papers to fetch

        Returns:
            List of ContentItem objects
        """
        if not categories:
            categories = ['cs.AI', 'cs.LG', 'cs.RO']

        all_items = []

        async with aiohttp.ClientSession() as session:
            for category in categories:
                try:
                    items = await self._fetch_category(
                        session, category, max_results // len(categories)
                    )
                    all_items.extend(items)
                    await asyncio.sleep(self.REQUEST_DELAY)
                except Exception as e:
                    print(f"Error fetching ArXiv category {category}: {e}")

        # Filter by date
        return self.filter_by_date(all_items)

    async def _fetch_category(
        self,
        session: aiohttp.ClientSession,
        category: str,
        max_results: int
    ) -> List[ContentItem]:
        """
        Fetch papers from a specific ArXiv category.

        Args:
            session: aiohttp session
            category: ArXiv category code
            max_results: Maximum results to fetch

        Returns:
            List of ContentItem objects
        """
        # Build query for recent papers in category
        query = f"cat:{category}"

        params = {
            'search_query': query,
            'start': 0,
            'max_results': max_results,
            'sortBy': 'submittedDate',
            'sortOrder': 'descending'
        }

        url = f"{self.BASE_URL}?{urlencode(params)}"

        async with session.get(url) as response:
            if response.status != 200:
                print(f"ArXiv API error: {response.status}")
                return []

            xml_content = await response.text()

        return self._parse_feed(xml_content, category)

    def _parse_feed(self, xml_content: str, category: str) -> List[ContentItem]:
        """
        Parse ArXiv Atom feed XML.

        Args:
            xml_content: Raw XML response
            category: Category being parsed

        Returns:
            List of ContentItem objects
        """
        items = []

        try:
            root = ET.fromstring(xml_content)

            for entry in root.findall('atom:entry', self.NAMESPACES):
                item = self._parse_entry(entry, category)
                if item:
                    items.append(item)

        except ET.ParseError as e:
            print(f"XML parsing error: {e}")

        return items

    def _parse_entry(self, entry: ET.Element, category: str) -> Optional[ContentItem]:
        """
        Parse a single ArXiv entry.

        Args:
            entry: XML entry element
            category: Category code

        Returns:
            ContentItem or None
        """
        try:
            # Get basic fields
            title = entry.find('atom:title', self.NAMESPACES)
            title_text = title.text.strip().replace('\n', ' ') if title is not None else ""

            # Get ArXiv ID and build URL
            id_elem = entry.find('atom:id', self.NAMESPACES)
            arxiv_id = id_elem.text if id_elem is not None else ""
            # ID format: http://arxiv.org/abs/XXXX.XXXXX
            paper_id = arxiv_id.split('/')[-1] if arxiv_id else ""
            url = f"https://arxiv.org/abs/{paper_id}"
            pdf_url = f"https://arxiv.org/pdf/{paper_id}.pdf"

            # Get abstract
            summary = entry.find('atom:summary', self.NAMESPACES)
            abstract = summary.text.strip().replace('\n', ' ') if summary is not None else ""

            # Get authors
            authors = []
            for author in entry.findall('atom:author', self.NAMESPACES):
                name = author.find('atom:name', self.NAMESPACES)
                if name is not None:
                    authors.append(name.text)

            # Get published date
            published = entry.find('atom:published', self.NAMESPACES)
            if published is not None:
                # Format: 2024-01-15T00:00:00Z
                pub_date = datetime.fromisoformat(
                    published.text.replace('Z', '+00:00')
                ).replace(tzinfo=None)
            else:
                pub_date = datetime.now()

            # Get categories
            categories = []
            for cat in entry.findall('arxiv:primary_category', self.NAMESPACES):
                term = cat.get('term')
                if term:
                    categories.append(term)
            for cat in entry.findall('atom:category', self.NAMESPACES):
                term = cat.get('term')
                if term and term not in categories:
                    categories.append(term)

            # Create tags from categories
            tags = ['arxiv', category]
            for cat in categories:
                if cat in self.CATEGORY_MAP:
                    tags.append(cat)

            return ContentItem(
                title=title_text,
                url=url,
                source_type=self.source_type,
                source_name=f"ArXiv [{category}]",
                published_at=pub_date,
                summary=abstract[:1000] + "..." if len(abstract) > 1000 else abstract,
                content=abstract,
                author=", ".join(authors[:5]) + ("..." if len(authors) > 5 else ""),
                score=0,  # ArXiv doesn't have engagement scores
                num_comments=0,
                tags=tags,
                metadata={
                    'arxiv_id': paper_id,
                    'pdf_url': pdf_url,
                    'categories': categories,
                    'all_authors': authors,
                    'primary_category': category,
                }
            )

        except Exception as e:
            print(f"Error parsing ArXiv entry: {e}")
            return None

    async def search(
        self,
        session: aiohttp.ClientSession,
        query: str,
        max_results: int = 20
    ) -> List[ContentItem]:
        """
        Search ArXiv with a custom query.

        Args:
            session: aiohttp session
            query: Search query (supports ArXiv query syntax)
            max_results: Maximum results

        Returns:
            List of ContentItem objects
        """
        params = {
            'search_query': f'all:{query}',
            'start': 0,
            'max_results': max_results,
            'sortBy': 'relevance',
            'sortOrder': 'descending'
        }

        url = f"{self.BASE_URL}?{urlencode(params)}"

        async with session.get(url) as response:
            if response.status != 200:
                return []

            xml_content = await response.text()

        return self._parse_feed(xml_content, "search")
