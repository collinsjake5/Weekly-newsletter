"""
Newsletter generator.

Combines collected content into formatted newsletters.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from sources.base import ContentItem, SourceType
from processors.summarizer import ContentSummarizer


class NewsletterGenerator:
    """
    Generates formatted newsletters from processed content.

    Supports multiple output formats:
    - Markdown
    - JSON (for further processing)
    - HTML (future)
    """

    def __init__(
        self,
        output_dir: str = "output",
        newsletter_name: str = "Weekly Digest",
        newsletter_type: str = "general"
    ):
        """
        Initialize generator.

        Args:
            output_dir: Directory for output files
            newsletter_name: Name of the newsletter
            newsletter_type: Type (ai, robotics, etc.)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.newsletter_name = newsletter_name
        self.newsletter_type = newsletter_type
        self.summarizer = ContentSummarizer(newsletter_name, newsletter_type)

    def generate(
        self,
        items: List[ContentItem],
        include_raw: bool = True
    ) -> Dict[str, str]:
        """
        Generate newsletter in all configured formats.

        Args:
            items: Processed and scored content items
            include_raw: Whether to also save raw JSON data

        Returns:
            Dict mapping format names to file paths
        """
        timestamp = datetime.now().strftime("%Y-%m-%d")
        outputs = {}

        # Generate markdown
        md_content = self._generate_markdown(items)
        md_path = self.output_dir / f"{self.newsletter_type}_{timestamp}.md"
        md_path.write_text(md_content)
        outputs['markdown'] = str(md_path)

        # Generate JSON
        if include_raw:
            json_content = self._generate_json(items)
            json_path = self.output_dir / f"{self.newsletter_type}_{timestamp}.json"
            json_path.write_text(json_content)
            outputs['json'] = str(json_path)

        # Generate prompt for Claude summarization
        prompt_content = self.summarizer.create_summary_prompt(items)
        prompt_path = self.output_dir / f"{self.newsletter_type}_{timestamp}_prompt.md"
        prompt_path.write_text(prompt_content)
        outputs['prompt'] = str(prompt_path)

        return outputs

    def _generate_markdown(self, items: List[ContentItem]) -> str:
        """
        Generate markdown newsletter.

        Args:
            items: Content items

        Returns:
            Markdown string
        """
        date_str = datetime.now().strftime("%B %d, %Y")
        week_num = datetime.now().isocalendar()[1]

        lines = [
            f"# {self.newsletter_name}",
            f"**Week {week_num} | {date_str}**",
            "",
            "---",
            "",
        ]

        # Group items by category
        grouped = self.summarizer.group_by_category(items)

        # Add summary stats
        lines.extend([
            "## This Week at a Glance",
            "",
            f"- **{len(items)}** items collected from {self._count_sources(items)} sources",
            f"- **Top source**: {self._get_top_source(items)}",
            "",
        ])

        # Top 5 Headlines
        lines.extend([
            "## 🔥 Top Stories",
            "",
        ])

        top_items = items[:5]
        for i, item in enumerate(top_items, 1):
            lines.append(self._format_top_story(item, i))
            lines.append("")

        # Research Papers (if any)
        if 'Research Papers' in grouped and grouped['Research Papers']:
            lines.extend([
                "---",
                "",
                "## 📚 Research Highlights",
                "",
            ])
            for item in grouped['Research Papers'][:5]:
                lines.append(self._format_paper(item))
                lines.append("")

        # Community Discussions
        if 'Community Discussions' in grouped and grouped['Community Discussions']:
            lines.extend([
                "---",
                "",
                "## 💬 Community Buzz",
                "",
            ])
            for item in grouped['Community Discussions'][:5]:
                lines.append(self._format_discussion(item))
                lines.append("")

        # News & Announcements
        if 'News & Announcements' in grouped and grouped['News & Announcements']:
            lines.extend([
                "---",
                "",
                "## 📰 News & Announcements",
                "",
            ])
            for item in grouped['News & Announcements'][:5]:
                lines.append(self._format_news(item))
                lines.append("")

        # Quick Links (remaining items)
        remaining = items[5:]
        if remaining:
            lines.extend([
                "---",
                "",
                "## 🔗 Quick Links",
                "",
            ])
            for item in remaining[:15]:
                source = item.source_name.replace('r/', '').replace('ArXiv ', '')[:15]
                lines.append(f"- [{item.title}]({item.url}) *({source})*")

        # Footer
        lines.extend([
            "",
            "---",
            "",
            f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')} UTC*",
            "",
            "*This newsletter was compiled using the Weekly Newsletter Builder.*",
        ])

        return "\n".join(lines)

    def _format_top_story(self, item: ContentItem, rank: int) -> str:
        """Format a top story item."""
        lines = [
            f"### {rank}. [{item.title}]({item.url})",
            "",
            f"**{item.source_name}** | {item.published_at.strftime('%b %d')}",
        ]

        if item.score > 0:
            lines.append(f"⬆️ {item.score} | 💬 {item.num_comments}")

        if item.summary:
            summary = item.summary[:250]
            if len(item.summary) > 250:
                summary += "..."
            lines.extend(["", f"> {summary}"])

        return "\n".join(lines)

    def _format_paper(self, item: ContentItem) -> str:
        """Format a research paper item."""
        lines = [
            f"### [{item.title}]({item.url})",
            "",
            f"*{item.author}*" if item.author else "",
            "",
        ]

        if item.summary:
            summary = item.summary[:300]
            if len(item.summary) > 300:
                summary += "..."
            lines.append(f"> {summary}")

        # Add PDF link if available
        pdf_url = item.metadata.get('pdf_url')
        if pdf_url:
            lines.append(f"\n📄 [PDF]({pdf_url})")

        return "\n".join(filter(None, lines))

    def _format_discussion(self, item: ContentItem) -> str:
        """Format a community discussion item."""
        lines = [
            f"**[{item.title}]({item.url})**",
            "",
            f"{item.source_name} | ⬆️ {item.score} | 💬 {item.num_comments}",
        ]

        if item.summary:
            summary = item.summary[:150]
            if len(item.summary) > 150:
                summary += "..."
            lines.extend(["", f"_{summary}_"])

        return "\n".join(lines)

    def _format_news(self, item: ContentItem) -> str:
        """Format a news item."""
        lines = [
            f"**[{item.title}]({item.url})**",
            "",
            f"*{item.source_name} | {item.published_at.strftime('%b %d')}*",
        ]

        if item.summary:
            summary = item.summary[:200]
            if len(item.summary) > 200:
                summary += "..."
            lines.extend(["", summary])

        return "\n".join(lines)

    def _generate_json(self, items: List[ContentItem]) -> str:
        """
        Generate JSON output.

        Args:
            items: Content items

        Returns:
            JSON string
        """
        data = {
            'newsletter': {
                'name': self.newsletter_name,
                'type': self.newsletter_type,
                'generated_at': datetime.now().isoformat(),
                'item_count': len(items),
            },
            'items': [item.to_dict() for item in items],
            'summary': {
                'sources': self._count_sources(items),
                'top_source': self._get_top_source(items),
                'date_range': self._get_date_range(items),
            }
        }

        return json.dumps(data, indent=2, default=str)

    def _count_sources(self, items: List[ContentItem]) -> int:
        """Count unique sources."""
        return len(set(item.source_name for item in items))

    def _get_top_source(self, items: List[ContentItem]) -> str:
        """Get the most common source."""
        if not items:
            return "N/A"

        source_counts: Dict[str, int] = {}
        for item in items:
            source_counts[item.source_name] = source_counts.get(item.source_name, 0) + 1

        return max(source_counts.items(), key=lambda x: x[1])[0]

    def _get_date_range(self, items: List[ContentItem]) -> Dict[str, str]:
        """Get the date range of items."""
        if not items:
            return {'start': 'N/A', 'end': 'N/A'}

        dates = [item.published_at for item in items]
        return {
            'start': min(dates).isoformat(),
            'end': max(dates).isoformat(),
        }
