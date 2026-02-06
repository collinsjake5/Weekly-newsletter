"""
YouTube transcript collector.

Fetches transcripts from YouTube videos and extracts key content.
Supports both automatic transcript fetching and manual transcript files.
"""

import asyncio
import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple
from .base import BaseCollector, ContentItem, SourceType

# Try to import youtube_transcript_api (optional dependency)
try:
    from youtube_transcript_api import YouTubeTranscriptApi
    YOUTUBE_API_AVAILABLE = True
except ImportError:
    YOUTUBE_API_AVAILABLE = False


class YouTubeCollector(BaseCollector):
    """
    Collector for YouTube video transcripts.

    Supports:
    1. Automatic transcript fetching via youtube-transcript-api
    2. Manual transcript files in transcripts/ folder
    """

    def __init__(
        self,
        lookback_days: int = 7,
        transcripts_path: str = "transcripts"
    ):
        """
        Initialize collector.

        Args:
            lookback_days: Number of days to look back
            transcripts_path: Path to manual transcripts folder
        """
        super().__init__(lookback_days)
        self.transcripts_path = Path(transcripts_path)

    @property
    def source_type(self) -> SourceType:
        return SourceType.RSS  # Treat as general content

    async def collect(
        self,
        topics: List[str],
        newsletter_type: Optional[str] = None,
        **kwargs
    ) -> List[ContentItem]:
        """
        Collect items from manual transcript files.

        Args:
            topics: Keywords for relevance
            newsletter_type: Filter by newsletter type if specified

        Returns:
            List of ContentItem objects
        """
        items = []

        # Collect from manual transcript files
        if self.transcripts_path.exists():
            items.extend(self._collect_from_files(newsletter_type))

        return items

    def _collect_from_files(
        self,
        newsletter_type: Optional[str] = None
    ) -> List[ContentItem]:
        """
        Collect from manual transcript .md files.

        File format:
        ```
        ---
        title: Video Title
        url: https://youtube.com/watch?v=xxx
        type: ai (or robotics, optional)
        highlights: Key points to include in newsletter
        ---

        [Transcript content here]
        ```
        """
        items = []

        for file_path in self.transcripts_path.glob("*.md"):
            try:
                item = self._parse_transcript_file(file_path)
                if item:
                    # Filter by type if specified
                    forced_type = item.metadata.get('forced_type')
                    if newsletter_type and forced_type and forced_type != newsletter_type:
                        continue
                    items.append(item)
            except Exception as e:
                print(f"Error parsing transcript {file_path}: {e}")

        return items

    def _parse_transcript_file(self, file_path: Path) -> Optional[ContentItem]:
        """
        Parse a transcript markdown file.

        Expected format:
        ---
        title: Video Title
        url: https://youtube.com/watch?v=xxx
        type: ai
        highlights: Key point 1. Key point 2.
        ---

        Transcript content...
        """
        content = file_path.read_text(encoding='utf-8')

        # Parse frontmatter
        frontmatter = {}
        body = content

        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter_text = parts[1].strip()
                body = parts[2].strip()

                # Parse YAML-like frontmatter
                for line in frontmatter_text.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        frontmatter[key.strip().lower()] = value.strip()

        # Extract metadata
        title = frontmatter.get('title', file_path.stem)
        url = frontmatter.get('url', '')
        video_type = frontmatter.get('type')
        highlights = frontmatter.get('highlights', '')
        channel = frontmatter.get('channel', 'YouTube')

        # Use highlights as summary, or extract first paragraph
        if highlights:
            summary = highlights
        else:
            # Get first 500 chars of body
            summary = body[:500].replace('\n', ' ').strip()
            if len(body) > 500:
                summary += "..."

        return ContentItem(
            title=title,
            url=url or f"file://{file_path}",
            source_type=self.source_type,
            source_name=f"YouTube - {channel}",
            published_at=datetime.fromtimestamp(file_path.stat().st_mtime),
            summary=summary,
            content=body,
            author=channel,
            score=150,  # Boost manual transcripts
            num_comments=0,
            tags=["youtube", "video", "transcript"],
            metadata={
                "from_transcript": True,
                "file_path": str(file_path),
                "forced_type": video_type,
                "highlights": highlights,
            }
        )

    def fetch_transcript_from_url(self, url: str) -> Optional[Tuple[str, str]]:
        """
        Fetch transcript from YouTube URL.

        Args:
            url: YouTube video URL

        Returns:
            Tuple of (title, transcript_text) or None
        """
        if not YOUTUBE_API_AVAILABLE:
            print("youtube-transcript-api not installed. Run: pip install youtube-transcript-api")
            return None

        video_id = self._extract_video_id(url)
        if not video_id:
            print(f"Could not extract video ID from: {url}")
            return None

        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            transcript_text = ' '.join([entry['text'] for entry in transcript_list])
            return (video_id, transcript_text)
        except Exception as e:
            print(f"Error fetching transcript for {video_id}: {e}")
            return None

    def _extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL."""
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com/shorts/([a-zA-Z0-9_-]{11})',
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None

    def clear_processed_transcripts(self) -> int:
        """
        Move processed transcripts to archive folder.

        Returns:
            Number of files archived
        """
        if not self.transcripts_path.exists():
            return 0

        archive_path = self.transcripts_path / "archive"
        archive_path.mkdir(exist_ok=True)

        count = 0
        for file_path in self.transcripts_path.glob("*.md"):
            # Move to archive with timestamp
            timestamp = datetime.now().strftime("%Y%m%d")
            new_name = f"{timestamp}_{file_path.name}"
            file_path.rename(archive_path / new_name)
            count += 1

        if count > 0:
            print(f"📺 Archived {count} transcript files")

        return count
