"""
Content summarization.

Provides utilities for summarizing and synthesizing content.
When used with Claude Code, leverages Claude for intelligent summarization.
"""

from typing import List, Dict, Any, Optional
from sources.base import ContentItem, SourceType


class ContentSummarizer:
    """
    Summarizes and synthesizes content for newsletter generation.

    This class provides templates and utilities for summarization.
    In Claude Code context, the actual summarization is done by Claude.
    """

    def __init__(self, newsletter_name: str, newsletter_type: str):
        """
        Initialize summarizer.

        Args:
            newsletter_name: Name of the newsletter
            newsletter_type: Type (ai, robotics, etc.)
        """
        self.newsletter_name = newsletter_name
        self.newsletter_type = newsletter_type

    def create_summary_prompt(
        self,
        items: List[ContentItem],
        max_items: int = 25
    ) -> str:
        """
        Create a prompt for Claude to summarize the collected content.

        Args:
            items: List of content items to summarize
            max_items: Maximum items to include in prompt

        Returns:
            Prompt string for summarization
        """
        items = items[:max_items]

        # Build content section
        content_sections = []

        for i, item in enumerate(items, 1):
            section = f"""
### {i}. {item.title}
- **Source**: {item.source_name}
- **URL**: {item.url}
- **Score**: {item.score} | Comments: {item.num_comments}
- **Published**: {item.published_at.strftime('%Y-%m-%d')}
"""
            if item.summary:
                section += f"- **Summary**: {item.summary[:300]}...\n"

            content_sections.append(section)

        content_text = "\n".join(content_sections)

        prompt = f"""
You are creating a weekly newsletter called "{self.newsletter_name}".

Below are the top {len(items)} items collected from various sources this week.
Please synthesize these into an engaging newsletter with:

1. **Executive Summary** (2-3 sentences): The biggest story/theme of the week
2. **Top Stories** (3-5 items): The most important developments with brief commentary
3. **Research Highlights** (2-3 items): Notable papers or technical advances
4. **Community Buzz** (2-3 items): What people are discussing on Reddit/HN
5. **Quick Links**: Remaining interesting items as a bullet list

Guidelines:
- Be concise but informative
- Add brief editorial commentary on why each item matters
- Group related items together when possible
- Highlight any controversies or debates
- Include the source URLs for each item

---

## Collected Content:

{content_text}

---

Please generate the newsletter in Markdown format.
"""
        return prompt

    def create_headline_summary(self, items: List[ContentItem], n: int = 5) -> str:
        """
        Create a quick headline summary of top items.

        Args:
            items: List of content items
            n: Number of headlines

        Returns:
            Formatted headline summary
        """
        headlines = []

        for i, item in enumerate(items[:n], 1):
            source = item.source_name.replace('r/', '').replace('ArXiv ', '')
            headlines.append(f"{i}. [{item.title}]({item.url}) ({source})")

        return "\n".join(headlines)

    def group_by_category(
        self,
        items: List[ContentItem]
    ) -> Dict[str, List[ContentItem]]:
        """
        Group items by source type/category.

        Args:
            items: List of content items

        Returns:
            Dict mapping category names to items
        """
        categories = {
            'Research Papers': [],
            'Community Discussions': [],
            'News & Announcements': [],
            'Other': [],
        }

        for item in items:
            if item.source_type == SourceType.ARXIV:
                categories['Research Papers'].append(item)
            elif item.source_type in (SourceType.REDDIT, SourceType.HACKERNEWS):
                categories['Community Discussions'].append(item)
            elif item.source_type == SourceType.RSS:
                categories['News & Announcements'].append(item)
            else:
                categories['Other'].append(item)

        # Remove empty categories
        return {k: v for k, v in categories.items() if v}

    def extract_key_themes(self, items: List[ContentItem]) -> List[str]:
        """
        Extract key themes from titles and summaries.

        Args:
            items: List of content items

        Returns:
            List of identified themes
        """
        # This is a simple keyword extraction
        # In practice, Claude would do more sophisticated analysis

        theme_keywords = {
            'ai': [
                'gpt', 'llm', 'language model', 'chatgpt', 'claude',
                'openai', 'anthropic', 'google', 'gemini', 'training',
                'fine-tuning', 'rlhf', 'safety', 'alignment'
            ],
            'robotics': [
                # Humanoids
                'humanoid', 'figure ai', 'figure 01', 'figure 02', 'optimus',
                'boston dynamics', 'atlas', 'digit', 'agility', 'apptronik',
                'sanctuary ai', '1x technologies',
                # Mobile Robots
                'amr', 'agv', 'autonomous mobile', 'warehouse robot',
                'logistics robot', 'locus', 'fetch robotics', 'amazon robotics',
                # Industrial Arms
                'robotic arm', 'cobot', 'collaborative robot', 'fanuc', 'kuka',
                'abb robot', 'universal robots', 'yaskawa', 'pick and place',
                'palletizing', 'welding robot', 'bin picking',
                # Drones
                'industrial drone', 'warehouse drone', 'inspection drone',
                # Manufacturing
                'factory automation', 'smart factory', 'industry 4.0',
                'manufacturing automation', 'material handling', 'machine tending',
                'automation', 'machine vision', 'visual inspection'
            ]
        }

        relevant_keywords = theme_keywords.get(self.newsletter_type, [])
        theme_counts: Dict[str, int] = {}

        for item in items:
            text = f"{item.title} {item.summary or ''}".lower()
            for keyword in relevant_keywords:
                if keyword in text:
                    theme_counts[keyword] = theme_counts.get(keyword, 0) + 1

        # Return top themes
        sorted_themes = sorted(
            theme_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [theme for theme, count in sorted_themes[:5] if count >= 2]

    def format_item_for_newsletter(
        self,
        item: ContentItem,
        include_summary: bool = True,
        include_engagement: bool = True
    ) -> str:
        """
        Format a single item for newsletter inclusion.

        Args:
            item: Content item to format
            include_summary: Whether to include summary
            include_engagement: Whether to include engagement metrics

        Returns:
            Formatted markdown string
        """
        lines = [f"### [{item.title}]({item.url})"]

        # Source and date
        date_str = item.published_at.strftime('%b %d')
        lines.append(f"*{item.source_name} | {date_str}*")

        # Engagement metrics (if applicable)
        if include_engagement and item.score > 0:
            lines.append(f"📊 {item.score} points | 💬 {item.num_comments} comments")

        # Summary
        if include_summary and item.summary:
            summary = item.summary[:200]
            if len(item.summary) > 200:
                summary += "..."
            lines.append(f"\n{summary}")

        return "\n".join(lines)
