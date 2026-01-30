"""
Content scoring system.

Ranks content items by relevance, recency, and engagement.
"""

import re
from datetime import datetime, timedelta
from typing import List, Dict
from sources.base import ContentItem, SourceType


class ContentScorer:
    """
    Scores and ranks content items based on multiple factors.

    Factors considered:
    - Relevance: How well the content matches the newsletter topics
    - Recency: How recently the content was published
    - Engagement: Upvotes, comments, and other engagement metrics
    """

    def __init__(
        self,
        topics: List[str],
        recency_weight: float = 0.3,
        engagement_weight: float = 0.4,
        relevance_weight: float = 0.3,
        lookback_days: int = 7
    ):
        """
        Initialize scorer.

        Args:
            topics: List of topic keywords for relevance scoring
            recency_weight: Weight for recency score (0-1)
            engagement_weight: Weight for engagement score (0-1)
            relevance_weight: Weight for relevance score (0-1)
            lookback_days: Number of days for recency calculation
        """
        self.topics = [t.lower() for t in topics]
        self.recency_weight = recency_weight
        self.engagement_weight = engagement_weight
        self.relevance_weight = relevance_weight
        self.lookback_days = lookback_days

        # Normalize weights
        total = recency_weight + engagement_weight + relevance_weight
        if total > 0:
            self.recency_weight /= total
            self.engagement_weight /= total
            self.relevance_weight /= total

    def score_items(self, items: List[ContentItem]) -> List[ContentItem]:
        """
        Score and sort all items.

        Args:
            items: List of content items to score

        Returns:
            List of items sorted by final score (highest first)
        """
        if not items:
            return []

        # Calculate max engagement for normalization
        max_score = max(item.score for item in items) if items else 1
        max_comments = max(item.num_comments for item in items) if items else 1

        for item in items:
            # Calculate individual scores
            relevance = self._calculate_relevance(item)
            recency = self._calculate_recency(item)
            engagement = self._calculate_engagement(item, max_score, max_comments)

            # Store relevance score for later use
            item.relevance_score = relevance

            # Calculate weighted final score
            item.final_score = (
                self.relevance_weight * relevance +
                self.recency_weight * recency +
                self.engagement_weight * engagement
            )

        # Sort by final score descending
        return sorted(items, key=lambda x: x.final_score, reverse=True)

    def _calculate_relevance(self, item: ContentItem) -> float:
        """
        Calculate relevance score based on topic matching.

        Returns:
            Score between 0 and 1
        """
        text = f"{item.title} {item.summary or ''} {' '.join(item.tags)}".lower()

        # Count topic matches
        matches = 0
        total_weight = 0

        for topic in self.topics:
            # Exact phrase match gets higher weight
            if topic in text:
                # Weight by position (title matches worth more)
                if topic in item.title.lower():
                    matches += 2
                else:
                    matches += 1
                total_weight += 1

            # Also check for word-level matches for multi-word topics
            topic_words = topic.split()
            if len(topic_words) > 1:
                word_matches = sum(1 for word in topic_words if word in text)
                if word_matches > 0:
                    matches += word_matches / len(topic_words)
                    total_weight += 1

        if total_weight == 0:
            return 0.0

        # Normalize to 0-1 range
        raw_score = matches / (len(self.topics) * 2)  # Max possible is 2 per topic
        return min(1.0, raw_score)

    def _calculate_recency(self, item: ContentItem) -> float:
        """
        Calculate recency score based on publication date.

        Returns:
            Score between 0 and 1 (1 = today, 0 = oldest allowed)
        """
        now = datetime.now()
        age = now - item.published_at

        # Convert to days
        age_days = age.total_seconds() / (24 * 3600)

        if age_days <= 0:
            return 1.0

        if age_days >= self.lookback_days:
            return 0.0

        # Linear decay
        return 1.0 - (age_days / self.lookback_days)

    def _calculate_engagement(
        self,
        item: ContentItem,
        max_score: int,
        max_comments: int
    ) -> float:
        """
        Calculate engagement score based on votes and comments.

        Returns:
            Score between 0 and 1
        """
        # Different sources have different engagement patterns
        if item.source_type == SourceType.ARXIV:
            # ArXiv doesn't have engagement, use neutral score
            return 0.5

        if item.source_type == SourceType.RSS:
            # RSS feeds don't have engagement, use neutral score
            return 0.5

        # Normalize scores
        score_component = item.score / max_score if max_score > 0 else 0
        comment_component = item.num_comments / max_comments if max_comments > 0 else 0

        # Weight score higher than comments
        return 0.7 * score_component + 0.3 * comment_component

    def filter_by_score(
        self,
        items: List[ContentItem],
        min_final_score: float = 0.1,
        min_relevance_score: float = 0.05
    ) -> List[ContentItem]:
        """
        Filter items below score thresholds.

        Args:
            items: List of scored items
            min_final_score: Minimum final score to include
            min_relevance_score: Minimum relevance score to include

        Returns:
            Filtered list of items
        """
        return [
            item for item in items
            if item.final_score >= min_final_score
            and item.relevance_score >= min_relevance_score
        ]

    def get_top_items(
        self,
        items: List[ContentItem],
        n: int = 25,
        ensure_diversity: bool = True
    ) -> List[ContentItem]:
        """
        Get top N items, optionally ensuring source diversity.

        Args:
            items: List of scored items
            n: Number of items to return
            ensure_diversity: If True, limit items per source

        Returns:
            Top N items
        """
        if not ensure_diversity:
            return items[:n]

        # Ensure no single source dominates
        max_per_source = max(3, n // 4)  # At least 3, or 25% of total
        source_counts: Dict[str, int] = {}
        result = []

        for item in items:
            source = item.source_name
            current_count = source_counts.get(source, 0)

            if current_count < max_per_source:
                result.append(item)
                source_counts[source] = current_count + 1

            if len(result) >= n:
                break

        return result
