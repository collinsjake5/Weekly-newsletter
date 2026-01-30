"""
Content deduplication.

Identifies and removes near-duplicate content across sources.
"""

import re
from typing import List, Set, Tuple
from urllib.parse import urlparse
from sources.base import ContentItem


class Deduplicator:
    """
    Removes duplicate and near-duplicate content items.

    Uses multiple strategies:
    1. Exact URL matching
    2. Normalized URL matching (removing tracking params)
    3. Title similarity matching
    """

    # Common tracking parameters to strip
    TRACKING_PARAMS = {
        'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
        'ref', 'source', 'fbclid', 'gclid', 'mc_cid', 'mc_eid',
    }

    def __init__(self, similarity_threshold: float = 0.8):
        """
        Initialize deduplicator.

        Args:
            similarity_threshold: Minimum similarity (0-1) to consider duplicate
        """
        self.similarity_threshold = similarity_threshold

    def deduplicate(self, items: List[ContentItem]) -> List[ContentItem]:
        """
        Remove duplicate items, keeping the highest-scored version.

        Args:
            items: List of content items (should be pre-sorted by score)

        Returns:
            Deduplicated list of items
        """
        if not items:
            return []

        seen_urls: Set[str] = set()
        seen_titles: Set[str] = set()
        result: List[ContentItem] = []

        for item in items:
            # Check URL duplicates
            normalized_url = self._normalize_url(item.url)
            if normalized_url in seen_urls:
                continue

            # Check title duplicates
            normalized_title = self._normalize_title(item.title)
            if self._is_similar_to_seen(normalized_title, seen_titles):
                continue

            # Not a duplicate - add it
            seen_urls.add(normalized_url)
            seen_titles.add(normalized_title)
            result.append(item)

        return result

    def _normalize_url(self, url: str) -> str:
        """
        Normalize URL by removing tracking parameters and fragments.

        Args:
            url: Original URL

        Returns:
            Normalized URL
        """
        try:
            parsed = urlparse(url)

            # Remove fragment
            normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

            # Parse and filter query params
            if parsed.query:
                params = []
                for param in parsed.query.split('&'):
                    if '=' in param:
                        key = param.split('=')[0]
                        if key.lower() not in self.TRACKING_PARAMS:
                            params.append(param)
                    else:
                        params.append(param)

                if params:
                    normalized += '?' + '&'.join(sorted(params))

            return normalized.lower().rstrip('/')

        except Exception:
            return url.lower().rstrip('/')

    def _normalize_title(self, title: str) -> str:
        """
        Normalize title for comparison.

        Args:
            title: Original title

        Returns:
            Normalized title
        """
        # Convert to lowercase
        normalized = title.lower()

        # Remove common prefixes/suffixes
        prefixes = ['breaking:', 'update:', 'new:', '[news]', '[paper]']
        for prefix in prefixes:
            if normalized.startswith(prefix):
                normalized = normalized[len(prefix):]

        # Remove special characters and extra whitespace
        normalized = re.sub(r'[^\w\s]', ' ', normalized)
        normalized = re.sub(r'\s+', ' ', normalized)

        return normalized.strip()

    def _is_similar_to_seen(self, title: str, seen_titles: Set[str]) -> bool:
        """
        Check if title is similar to any seen title.

        Args:
            title: Normalized title to check
            seen_titles: Set of seen normalized titles

        Returns:
            True if similar to a seen title
        """
        if title in seen_titles:
            return True

        # Check word-based similarity
        title_words = set(title.split())

        for seen in seen_titles:
            seen_words = set(seen.split())

            if not title_words or not seen_words:
                continue

            # Calculate Jaccard similarity
            intersection = len(title_words & seen_words)
            union = len(title_words | seen_words)

            if union > 0:
                similarity = intersection / union
                if similarity >= self.similarity_threshold:
                    return True

        return False

    def find_duplicates(
        self,
        items: List[ContentItem]
    ) -> List[Tuple[ContentItem, ContentItem]]:
        """
        Find pairs of duplicate items (for debugging/analysis).

        Args:
            items: List of content items

        Returns:
            List of (item1, item2) duplicate pairs
        """
        duplicates = []

        for i, item1 in enumerate(items):
            for item2 in items[i + 1:]:
                if self._are_duplicates(item1, item2):
                    duplicates.append((item1, item2))

        return duplicates

    def _are_duplicates(self, item1: ContentItem, item2: ContentItem) -> bool:
        """Check if two items are duplicates."""
        # Check URL
        if self._normalize_url(item1.url) == self._normalize_url(item2.url):
            return True

        # Check title similarity
        title1 = self._normalize_title(item1.title)
        title2 = self._normalize_title(item2.title)

        if title1 == title2:
            return True

        # Check word similarity
        words1 = set(title1.split())
        words2 = set(title2.split())

        if words1 and words2:
            intersection = len(words1 & words2)
            union = len(words1 | words2)
            if union > 0 and (intersection / union) >= self.similarity_threshold:
                return True

        return False
