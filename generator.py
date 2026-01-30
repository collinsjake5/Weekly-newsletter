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

        # Generate HTML
        html_content = self._generate_html(items)
        html_path = self.output_dir / f"{self.newsletter_type}_{timestamp}.html"
        html_path.write_text(html_content, encoding='utf-8')
        outputs['html'] = str(html_path)

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

        # Track shown items to prevent duplicates
        shown_urls = set()

        # Top 5 Headlines
        lines.extend([
            "## 🔥 Top Stories",
            "",
        ])

        top_items = items[:5]
        for i, item in enumerate(top_items, 1):
            shown_urls.add(item.url)
            lines.append(self._format_top_story(item, i))
            lines.append("")

        # Research Papers (exclude items already shown)
        if 'Research Papers' in grouped and grouped['Research Papers']:
            papers_to_show = [p for p in grouped['Research Papers'] if p.url not in shown_urls][:5]
            if papers_to_show:
                lines.extend([
                    "---",
                    "",
                    "## 📚 Research Highlights",
                    "",
                ])
                for item in papers_to_show:
                    shown_urls.add(item.url)
                    lines.append(self._format_paper(item))
                    lines.append("")

        # Community Discussions (exclude items already shown)
        if 'Community Discussions' in grouped and grouped['Community Discussions']:
            discussions_to_show = [d for d in grouped['Community Discussions'] if d.url not in shown_urls][:5]
            if discussions_to_show:
                lines.extend([
                    "---",
                    "",
                    "## 💬 Community Buzz",
                    "",
                ])
                for item in discussions_to_show:
                    shown_urls.add(item.url)
                    lines.append(self._format_discussion(item))
                    lines.append("")

        # News & Announcements (exclude items already shown)
        if 'News & Announcements' in grouped and grouped['News & Announcements']:
            news_to_show = [n for n in grouped['News & Announcements'] if n.url not in shown_urls][:5]
            if news_to_show:
                lines.extend([
                    "---",
                    "",
                    "## 📰 News & Announcements",
                    "",
                ])
                for item in news_to_show:
                    shown_urls.add(item.url)
                    lines.append(self._format_news(item))
                    lines.append("")

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

    def _generate_html(self, items: List[ContentItem]) -> str:
        """
        Generate HTML newsletter suitable for email distribution.

        Args:
            items: Content items

        Returns:
            HTML string
        """
        date_str = datetime.now().strftime("%B %d, %Y")
        week_num = datetime.now().isocalendar()[1]

        # Group items by category
        grouped = self.summarizer.group_by_category(items)

        # Build HTML
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.newsletter_name} - Week {week_num}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 700px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: #ffffff;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            border-bottom: 3px solid #2563eb;
            padding-bottom: 20px;
            margin-bottom: 25px;
        }}
        .header h1 {{
            color: #1e40af;
            margin: 0 0 5px 0;
            font-size: 28px;
        }}
        .header .date {{
            color: #6b7280;
            font-size: 14px;
        }}
        .stats {{
            background-color: #eff6ff;
            border-radius: 6px;
            padding: 15px;
            margin-bottom: 25px;
            text-align: center;
        }}
        .stats span {{
            margin: 0 15px;
            color: #1e40af;
            font-weight: 500;
        }}
        .section {{
            margin-bottom: 30px;
        }}
        .section-title {{
            color: #1e40af;
            font-size: 20px;
            border-bottom: 2px solid #e5e7eb;
            padding-bottom: 8px;
            margin-bottom: 15px;
        }}
        .story {{
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid #f3f4f6;
        }}
        .story:last-child {{
            border-bottom: none;
        }}
        .story-rank {{
            display: inline-block;
            background-color: #2563eb;
            color: white;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            text-align: center;
            line-height: 24px;
            font-size: 12px;
            font-weight: bold;
            margin-right: 8px;
        }}
        .story-title {{
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 5px;
        }}
        .story-title a {{
            color: #1e40af;
            text-decoration: none;
        }}
        .story-title a:hover {{
            text-decoration: underline;
        }}
        .story-meta {{
            font-size: 12px;
            color: #6b7280;
            margin-bottom: 8px;
        }}
        .story-summary {{
            font-size: 14px;
            color: #4b5563;
            background-color: #f9fafb;
            padding: 10px;
            border-left: 3px solid #d1d5db;
            margin: 0;
        }}
        .paper {{
            margin-bottom: 18px;
            padding: 12px;
            background-color: #fefce8;
            border-radius: 6px;
        }}
        .paper-title a {{
            color: #854d0e;
            text-decoration: none;
            font-weight: 600;
        }}
        .paper-title a:hover {{
            text-decoration: underline;
        }}
        .paper-author {{
            font-size: 12px;
            color: #a16207;
            font-style: italic;
        }}
        .paper-summary {{
            font-size: 13px;
            color: #713f12;
            margin-top: 8px;
        }}
        .discussion {{
            margin-bottom: 15px;
            padding: 12px;
            background-color: #f0fdf4;
            border-radius: 6px;
        }}
        .discussion-title a {{
            color: #166534;
            text-decoration: none;
            font-weight: 600;
        }}
        .discussion-meta {{
            font-size: 12px;
            color: #15803d;
        }}
        .news {{
            margin-bottom: 15px;
        }}
        .news-title a {{
            color: #1e40af;
            text-decoration: none;
            font-weight: 500;
        }}
        .news-meta {{
            font-size: 12px;
            color: #6b7280;
        }}
        .news-summary {{
            font-size: 14px;
            color: #4b5563;
        }}
        .quick-links {{
            background-color: #f9fafb;
            padding: 15px;
            border-radius: 6px;
        }}
        .quick-links ul {{
            margin: 0;
            padding-left: 20px;
        }}
        .quick-links li {{
            margin-bottom: 8px;
        }}
        .quick-links a {{
            color: #2563eb;
            text-decoration: none;
        }}
        .quick-links a:hover {{
            text-decoration: underline;
        }}
        .quick-links .source {{
            color: #9ca3af;
            font-size: 12px;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e5e7eb;
            color: #9ca3af;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{self.newsletter_name}</h1>
            <div class="date">Week {week_num} | {date_str}</div>
        </div>

        <div class="stats">
            <span>📊 <strong>{len(items)}</strong> items</span>
            <span>📰 <strong>{self._count_sources(items)}</strong> sources</span>
            <span>🏆 Top: <strong>{self._get_top_source(items)}</strong></span>
        </div>
'''

        # Track which items have been shown to prevent duplicates
        shown_urls = set()

        # Top Stories (top 5 items by score)
        html += '''
        <div class="section">
            <h2 class="section-title">🔥 Top Stories</h2>
'''
        for i, item in enumerate(items[:5], 1):
            shown_urls.add(item.url)
            summary_html = ""
            if item.summary:
                summary = item.summary[:250] + "..." if len(item.summary) > 250 else item.summary
                summary_html = f'<p class="story-summary">{self._escape_html(summary)}</p>'

            html += f'''
            <div class="story">
                <div class="story-title">
                    <span class="story-rank">{i}</span>
                    <a href="{item.url}" target="_blank">{self._escape_html(item.title)}</a>
                </div>
                <div class="story-meta">
                    {self._escape_html(item.source_name)} | {item.published_at.strftime('%b %d')}
                    {f' | ⬆️ {item.score} | 💬 {item.num_comments}' if item.score > 0 else ''}
                </div>
                {summary_html}
            </div>
'''
        html += '        </div>\n'

        # Research Papers (exclude items already shown)
        if 'Research Papers' in grouped and grouped['Research Papers']:
            papers_to_show = [p for p in grouped['Research Papers'] if p.url not in shown_urls][:5]
            if papers_to_show:
                html += '''
        <div class="section">
            <h2 class="section-title">📚 Research Highlights</h2>
'''
                for item in papers_to_show:
                    shown_urls.add(item.url)
                    summary_html = ""
                    if item.summary:
                        summary = item.summary[:200] + "..." if len(item.summary) > 200 else item.summary
                        summary_html = f'<div class="paper-summary">{self._escape_html(summary)}</div>'

                    author_html = f'<div class="paper-author">{self._escape_html(item.author)}</div>' if item.author else ''

                    html += f'''
            <div class="paper">
                <div class="paper-title"><a href="{item.url}" target="_blank">{self._escape_html(item.title)}</a></div>
                {author_html}
                {summary_html}
            </div>
'''
                html += '        </div>\n'

        # Community Discussions (exclude items already shown)
        if 'Community Discussions' in grouped and grouped['Community Discussions']:
            discussions_to_show = [d for d in grouped['Community Discussions'] if d.url not in shown_urls][:5]
            if discussions_to_show:
                html += '''
        <div class="section">
            <h2 class="section-title">💬 Community Buzz</h2>
'''
                for item in discussions_to_show:
                    shown_urls.add(item.url)
                    html += f'''
            <div class="discussion">
                <div class="discussion-title"><a href="{item.url}" target="_blank">{self._escape_html(item.title)}</a></div>
                <div class="discussion-meta">{self._escape_html(item.source_name)} | ⬆️ {item.score} | 💬 {item.num_comments}</div>
            </div>
'''
                html += '        </div>\n'

        # News & Announcements (exclude items already shown)
        if 'News & Announcements' in grouped and grouped['News & Announcements']:
            news_to_show = [n for n in grouped['News & Announcements'] if n.url not in shown_urls][:5]
            if news_to_show:
                html += '''
        <div class="section">
            <h2 class="section-title">📰 News & Announcements</h2>
'''
                for item in news_to_show:
                    shown_urls.add(item.url)
                    summary_html = ""
                    if item.summary:
                        summary = item.summary[:150] + "..." if len(item.summary) > 150 else item.summary
                        summary_html = f'<div class="news-summary">{self._escape_html(summary)}</div>'

                    html += f'''
            <div class="news">
                <div class="news-title"><a href="{item.url}" target="_blank">{self._escape_html(item.title)}</a></div>
                <div class="news-meta">{self._escape_html(item.source_name)} | {item.published_at.strftime('%b %d')}</div>
                {summary_html}
            </div>
'''
                html += '        </div>\n'

        # Footer
        html += f'''
        <div class="footer">
            Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')} UTC<br>
            This newsletter was compiled using the Weekly Newsletter Builder.
        </div>
    </div>
</body>
</html>'''

        return html

    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters."""
        if not text:
            return ""
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#39;'))
