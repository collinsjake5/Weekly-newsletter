# Sources package
# Collectors for various data sources

from .reddit import RedditCollector
from .hackernews import HackerNewsCollector
from .arxiv import ArxivCollector
from .rss import RSSCollector
from .inbox import InboxCollector
from .base import BaseCollector, ContentItem

__all__ = [
    'BaseCollector',
    'ContentItem',
    'RedditCollector',
    'HackerNewsCollector',
    'ArxivCollector',
    'RSSCollector',
    'InboxCollector',
]
