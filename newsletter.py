#!/usr/bin/env python3
"""
Weekly Newsletter Builder - Main Orchestrator

This script coordinates the collection, processing, and generation
of weekly newsletters on AI and Robotics topics.

Usage:
    python newsletter.py [OPTIONS]

Options:
    --type TYPE     Newsletter type: ai, robotics, or all (default: all)
    --days DAYS     Lookback period in days (default: 7)
    --output DIR    Output directory (default: output)
    --dry-run       Collect and score but don't generate output
"""

import asyncio
import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

import yaml

from sources import (
    RedditCollector,
    HackerNewsCollector,
    ArxivCollector,
    RSSCollector,
    InboxCollector,
    YouTubeCollector,
    ContentItem,
)
from processors import ContentScorer, Deduplicator, ContentSummarizer
from generator import NewsletterGenerator


class NewsletterOrchestrator:
    """
    Orchestrates the newsletter generation pipeline.

    Pipeline stages:
    1. Load configuration
    2. Collect content from all sources
    3. Score and rank content
    4. Deduplicate
    5. Generate newsletter
    """

    def __init__(
        self,
        config_path: str = "config.yaml",
        lookback_days: int = 7,
        output_dir: str = "output"
    ):
        """
        Initialize orchestrator.

        Args:
            config_path: Path to configuration file
            lookback_days: Number of days to look back
            output_dir: Directory for output files
        """
        self.config_path = Path(config_path)
        self.lookback_days = lookback_days
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Load configuration
        self.config = self._load_config()

        # Initialize collectors
        self.reddit_collector = RedditCollector(lookback_days)
        self.hn_collector = HackerNewsCollector(lookback_days)
        self.arxiv_collector = ArxivCollector(lookback_days)
        self.rss_collector = RSSCollector(lookback_days)
        self.inbox_collector = InboxCollector(lookback_days, inbox_path="inbox.txt")
        self.youtube_collector = YouTubeCollector(lookback_days, transcripts_path="transcripts")

        # Initialize processors
        self.deduplicator = Deduplicator(similarity_threshold=0.8)

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            print(f"Warning: Config file {self.config_path} not found, using defaults")
            return self._default_config()

        with open(self.config_path) as f:
            return yaml.safe_load(f)

    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            'newsletters': {
                'ai': {
                    'name': 'AI Weekly Digest',
                    'topics': ['artificial intelligence', 'machine learning', 'LLM'],
                    'sources': {
                        'reddit': ['MachineLearning', 'artificial'],
                        'hackernews': {'enabled': True, 'min_score': 50},
                        'arxiv': {'categories': ['cs.AI', 'cs.LG']},
                        'rss': [],
                    }
                }
            },
            'output': {'max_items': 25}
        }

    async def run(
        self,
        newsletter_type: str = "all",
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Run the newsletter generation pipeline.

        Args:
            newsletter_type: Type of newsletter (ai, robotics, or all)
            dry_run: If True, collect and process but don't save

        Returns:
            Dict with results and statistics
        """
        results = {}
        newsletters = self.config.get('newsletters', {})

        # Determine which newsletters to generate
        if newsletter_type == "all":
            types_to_run = list(newsletters.keys())
        else:
            types_to_run = [newsletter_type]

        for ntype in types_to_run:
            if ntype not in newsletters:
                print(f"Warning: Newsletter type '{ntype}' not found in config")
                continue

            print(f"\n{'='*60}")
            print(f"Generating {newsletters[ntype].get('name', ntype)} Newsletter")
            print(f"{'='*60}\n")

            result = await self._generate_newsletter(ntype, dry_run)
            results[ntype] = result

        # Clear inbox and archive transcripts after successful generation (not in dry run)
        if not dry_run and any(r.get('status') == 'success' for r in results.values()):
            self.inbox_collector.clear_inbox()
            self.youtube_collector.clear_processed_transcripts()

        return results

    async def _generate_newsletter(
        self,
        newsletter_type: str,
        dry_run: bool
    ) -> Dict[str, Any]:
        """
        Generate a single newsletter.

        Args:
            newsletter_type: Type of newsletter
            dry_run: If True, don't save output

        Returns:
            Dict with results
        """
        config = self.config['newsletters'][newsletter_type]
        topics = config.get('topics', [])
        sources_config = config.get('sources', {})

        # Stage 1: Collect content from all sources
        print("📥 Stage 1: Collecting content...")
        all_items = await self._collect_all(topics, sources_config, newsletter_type)
        print(f"   Collected {len(all_items)} items")

        if not all_items:
            return {'status': 'error', 'message': 'No items collected'}

        # Stage 2: Score and rank
        print("\n📊 Stage 2: Scoring and ranking...")
        scorer = ContentScorer(
            topics=topics,
            recency_weight=self.config.get('scoring', {}).get('recency_weight', 0.3),
            engagement_weight=self.config.get('scoring', {}).get('engagement_weight', 0.4),
            relevance_weight=self.config.get('scoring', {}).get('relevance_weight', 0.3),
            lookback_days=self.lookback_days,
            newsletter_type=newsletter_type,
            guidelines_path=str(self.config_path.parent / "guidelines.yaml")
        )
        scored_items = scorer.score_items(all_items)
        print(f"   Scored {len(scored_items)} items")

        # Stage 3: Deduplicate
        print("\n🔄 Stage 3: Deduplicating...")
        unique_items = self.deduplicator.deduplicate(scored_items)
        print(f"   {len(unique_items)} unique items (removed {len(scored_items) - len(unique_items)} duplicates)")

        # Stage 4: Filter by relevance and limit
        print("\n🎯 Stage 4: Filtering top items...")
        min_relevance = self.config.get('scoring', {}).get('min_relevance_score', 0.05)
        filtered_items = scorer.filter_by_score(unique_items, min_relevance_score=min_relevance)
        print(f"   {len(filtered_items)} items passed relevance filter (removed {len(unique_items) - len(filtered_items)} off-topic)")

        max_items = self.config.get('output', {}).get('max_items', 20)
        top_items = scorer.get_top_items(filtered_items, n=max_items, ensure_diversity=True)
        print(f"   Selected top {len(top_items)} items")

        # Stage 5: Generate output
        if dry_run:
            print("\n⏸️  Dry run - skipping output generation")
            return {
                'status': 'dry_run',
                'item_count': len(top_items),
                'items': [item.to_dict() for item in top_items[:5]]
            }

        print("\n📝 Stage 5: Generating newsletter...")
        generator = NewsletterGenerator(
            output_dir=str(self.output_dir),
            newsletter_name=config.get('name', 'Weekly Digest'),
            newsletter_type=newsletter_type
        )
        outputs = generator.generate(top_items)

        print(f"\n✅ Newsletter generated!")
        for fmt, path in outputs.items():
            print(f"   - {fmt}: {path}")

        return {
            'status': 'success',
            'item_count': len(top_items),
            'outputs': outputs,
            'sources_summary': self._summarize_sources(top_items)
        }

    async def _collect_all(
        self,
        topics: List[str],
        sources_config: Dict[str, Any],
        newsletter_type: str
    ) -> List[ContentItem]:
        """
        Collect content from all configured sources.

        Args:
            topics: Topic keywords
            sources_config: Source configuration
            newsletter_type: Type of newsletter (for inbox filtering)

        Returns:
            List of all collected items
        """
        all_items = []

        # Collect from inbox (manual URLs)
        inbox_count = self.inbox_collector.get_inbox_count()
        if inbox_count > 0:
            print(f"   - Inbox: processing {inbox_count} manually added URLs...")
            try:
                items = await self.inbox_collector.collect(
                    topics=topics,
                    newsletter_type=newsletter_type
                )
                all_items.extend(items)
                print(f"     ✓ {len(items)} curated items")
            except Exception as e:
                print(f"     ✗ Error: {e}")

        # Collect from Reddit
        reddit_subs = sources_config.get('reddit', [])
        if reddit_subs:
            print(f"   - Reddit: fetching from {len(reddit_subs)} subreddits...")
            try:
                items = await self.reddit_collector.collect(
                    topics=topics,
                    subreddits=reddit_subs
                )
                all_items.extend(items)
                print(f"     ✓ {len(items)} posts")
            except Exception as e:
                print(f"     ✗ Error: {e}")

        # Collect from Hacker News
        hn_config = sources_config.get('hackernews', {})
        if hn_config.get('enabled', True):
            print("   - Hacker News: fetching top stories...")
            try:
                items = await self.hn_collector.collect(
                    topics=topics,
                    min_score=hn_config.get('min_score', 50)
                )
                all_items.extend(items)
                print(f"     ✓ {len(items)} stories")
            except Exception as e:
                print(f"     ✗ Error: {e}")

        # Collect from ArXiv
        arxiv_config = sources_config.get('arxiv', {})
        arxiv_categories = arxiv_config.get('categories', [])
        if arxiv_categories:
            print(f"   - ArXiv: fetching from {len(arxiv_categories)} categories...")
            try:
                items = await self.arxiv_collector.collect(
                    topics=topics,
                    categories=arxiv_categories,
                    max_results=arxiv_config.get('max_results', 20)
                )
                all_items.extend(items)
                print(f"     ✓ {len(items)} papers")
            except Exception as e:
                print(f"     ✗ Error: {e}")

        # Collect from RSS feeds
        rss_feeds = sources_config.get('rss', [])
        if rss_feeds:
            print(f"   - RSS: fetching from {len(rss_feeds)} feeds...")
            try:
                items = await self.rss_collector.collect(
                    topics=topics,
                    feeds=rss_feeds
                )
                all_items.extend(items)
                print(f"     ✓ {len(items)} articles")
            except Exception as e:
                print(f"     ✗ Error: {e}")

        # Collect from YouTube transcripts
        try:
            items = await self.youtube_collector.collect(
                topics=topics,
                newsletter_type=newsletter_type
            )
            if items:
                print(f"   - YouTube: processing transcript files...")
                all_items.extend(items)
                print(f"     ✓ {len(items)} video transcripts")
        except Exception as e:
            print(f"     ✗ YouTube Error: {e}")

        return all_items

    def _summarize_sources(self, items: List[ContentItem]) -> Dict[str, int]:
        """Summarize items by source."""
        summary = {}
        for item in items:
            source = item.source_type.value
            summary[source] = summary.get(source, 0) + 1
        return summary


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Weekly Newsletter Builder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python newsletter.py                    # Generate all newsletters
    python newsletter.py --type ai          # Generate AI newsletter only
    python newsletter.py --type robotics    # Generate Robotics newsletter only
    python newsletter.py --days 14          # Look back 14 days
    python newsletter.py --dry-run          # Test without saving
        """
    )

    parser.add_argument(
        '--type', '-t',
        choices=['ai', 'robotics', 'all'],
        default='all',
        help='Newsletter type to generate (default: all)'
    )

    parser.add_argument(
        '--days', '-d',
        type=int,
        default=7,
        help='Number of days to look back (default: 7)'
    )

    parser.add_argument(
        '--output', '-o',
        default='output',
        help='Output directory (default: output)'
    )

    parser.add_argument(
        '--config', '-c',
        default='config.yaml',
        help='Configuration file (default: config.yaml)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Collect and process but do not save output'
    )

    args = parser.parse_args()

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║              Weekly Newsletter Builder                        ║
╠══════════════════════════════════════════════════════════════╣
║  Type:     {args.type:<48} ║
║  Days:     {args.days:<48} ║
║  Output:   {args.output:<48} ║
╚══════════════════════════════════════════════════════════════╝
""")

    # Create orchestrator and run
    orchestrator = NewsletterOrchestrator(
        config_path=args.config,
        lookback_days=args.days,
        output_dir=args.output
    )

    try:
        results = asyncio.run(orchestrator.run(
            newsletter_type=args.type,
            dry_run=args.dry_run
        ))

        # Print summary
        print("\n" + "="*60)
        print("📋 Summary")
        print("="*60)

        for ntype, result in results.items():
            status = result.get('status', 'unknown')
            count = result.get('item_count', 0)

            if status == 'success':
                print(f"\n✅ {ntype}: Generated with {count} items")
                for fmt, path in result.get('outputs', {}).items():
                    print(f"   - {fmt}: {path}")
            elif status == 'dry_run':
                print(f"\n⏸️  {ntype}: Dry run completed ({count} items)")
            else:
                print(f"\n❌ {ntype}: {result.get('message', 'Unknown error')}")

        print("\n" + "="*60)
        print("Done!")

    except KeyboardInterrupt:
        print("\n\nAborted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
