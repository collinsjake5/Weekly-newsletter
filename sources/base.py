"""
Base classes for content collectors.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum


class SourceType(Enum):
    """Enumeration of content source types."""
    REDDIT = "reddit"
    HACKERNEWS = "hackernews"
    ARXIV = "arxiv"
    RSS = "rss"
    WEBSEARCH = "websearch"


@dataclass
class ContentItem:
    """
    Unified content item from any source.

    This is the canonical format that all collectors normalize to.
    """
    # Required fields
    title: str
    url: str
    source_type: SourceType
    source_name: str  # e.g., "r/MachineLearning", "Hacker News", "ArXiv"
    published_at: datetime

    # Optional content
    summary: Optional[str] = None
    content: Optional[str] = None  # Full text if available
    author: Optional[str] = None

    # Engagement metrics (where available)
    score: int = 0  # Upvotes, points, etc.
    num_comments: int = 0

    # Metadata
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Computed fields (set during processing)
    relevance_score: float = 0.0
    final_score: float = 0.0

    def __hash__(self):
        return hash(self.url)

    def __eq__(self, other):
        if isinstance(other, ContentItem):
            return self.url == other.url
        return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'title': self.title,
            'url': self.url,
            'source_type': self.source_type.value,
            'source_name': self.source_name,
            'published_at': self.published_at.isoformat(),
            'summary': self.summary,
            'content': self.content,
            'author': self.author,
            'score': self.score,
            'num_comments': self.num_comments,
            'tags': self.tags,
            'metadata': self.metadata,
            'relevance_score': self.relevance_score,
            'final_score': self.final_score,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContentItem':
        """Create from dictionary."""
        data = data.copy()
        data['source_type'] = SourceType(data['source_type'])
        data['published_at'] = datetime.fromisoformat(data['published_at'])
        return cls(**data)


class BaseCollector(ABC):
    """
    Abstract base class for all content collectors.

    Each collector is responsible for:
    1. Fetching content from its source
    2. Normalizing content to ContentItem format
    3. Basic filtering by date range
    """

    def __init__(self, lookback_days: int = 7):
        """
        Initialize collector.

        Args:
            lookback_days: Number of days to look back for content
        """
        self.lookback_days = lookback_days
        self.cutoff_date = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )

    @property
    @abstractmethod
    def source_type(self) -> SourceType:
        """Return the source type for this collector."""
        pass

    @abstractmethod
    async def collect(self, topics: List[str], **kwargs) -> List[ContentItem]:
        """
        Collect content items related to given topics.

        Args:
            topics: List of topic keywords to search for
            **kwargs: Source-specific configuration

        Returns:
            List of ContentItem objects
        """
        pass

    def is_within_date_range(self, dt: datetime) -> bool:
        """Check if a datetime is within the lookback period."""
        from datetime import timedelta
        min_date = self.cutoff_date - timedelta(days=self.lookback_days)
        return dt >= min_date

    def filter_by_date(self, items: List[ContentItem]) -> List[ContentItem]:
        """Filter items to only those within the date range."""
        return [
            item for item in items
            if self.is_within_date_range(item.published_at)
        ]
