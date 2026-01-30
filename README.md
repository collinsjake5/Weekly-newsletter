# Weekly Newsletter Builder

Automated weekly newsletter generator for AI and Robotics topics. Collects content from Reddit, Hacker News, ArXiv, and RSS feeds, then generates formatted newsletters.

## Features

- **Multi-source collection**: Reddit, Hacker News, ArXiv papers, RSS feeds
- **Smart scoring**: Ranks content by relevance, recency, and engagement
- **Deduplication**: Removes near-duplicate content across sources
- **Configurable**: YAML-based configuration for topics and sources
- **Multiple outputs**: Markdown newsletters and JSON data
- **Claude integration**: Generates prompts for AI-powered summarization

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/your-repo/Weekly-newsletter.git
cd Weekly-newsletter

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```bash
# Generate all newsletters (AI + Robotics)
python newsletter.py

# Generate AI newsletter only
python newsletter.py --type ai

# Generate Robotics newsletter only
python newsletter.py --type robotics

# Look back 14 days instead of 7
python newsletter.py --days 14

# Test without saving (dry run)
python newsletter.py --dry-run
```

### Output

Newsletters are generated in the `output/` directory:

```
output/
├── ai_2024-01-15.md           # AI newsletter (Markdown)
├── ai_2024-01-15.json         # AI newsletter (JSON data)
├── ai_2024-01-15_prompt.md    # Prompt for Claude summarization
├── robotics_2024-01-15.md     # Robotics newsletter
├── robotics_2024-01-15.json
└── robotics_2024-01-15_prompt.md
```

## Configuration

Edit `config.yaml` to customize:

### Topics and Keywords

```yaml
newsletters:
  ai:
    name: "AI Weekly Digest"
    topics:
      - "artificial intelligence"
      - "machine learning"
      - "LLM"
      # Add more keywords...
```

### Data Sources

```yaml
    sources:
      reddit:
        - "MachineLearning"
        - "artificial"
        - "LocalLLaMA"

      hackernews:
        enabled: true
        min_score: 50

      arxiv:
        categories:
          - "cs.AI"
          - "cs.LG"
        max_results: 20

      rss:
        - name: "OpenAI Blog"
          url: "https://openai.com/blog/rss.xml"
```

### Scoring Weights

```yaml
scoring:
  recency_weight: 0.3      # Newer content scores higher
  engagement_weight: 0.4   # More upvotes/comments = higher score
  relevance_weight: 0.3    # Better topic match = higher score
```

## Data Sources

| Source | Access Method | Auth Required | Rate Limits |
|--------|--------------|---------------|-------------|
| Reddit | Public JSON API | No | ~60 req/min |
| Hacker News | Firebase API | No | Generous |
| ArXiv | REST API | No | 1 req/3 sec |
| RSS Feeds | HTTP | No | Varies |

## Project Structure

```
Weekly-newsletter/
├── newsletter.py          # Main orchestrator
├── config.yaml            # Configuration
├── requirements.txt       # Dependencies
├── generator.py           # Newsletter generation
├── sources/
│   ├── base.py           # Base classes
│   ├── reddit.py         # Reddit collector
│   ├── hackernews.py     # HN collector
│   ├── arxiv.py          # ArXiv collector
│   ├── rss.py            # RSS collector
│   └── websearch.py      # Web search (Claude integration)
├── processors/
│   ├── scorer.py         # Content scoring
│   ├── deduplicator.py   # Duplicate removal
│   └── summarizer.py     # Summary generation
├── templates/
│   └── newsletter.md     # Newsletter template
└── output/               # Generated newsletters
```

## Using with Claude Code

This tool is designed to work seamlessly with Claude Code. For enhanced summarization:

1. Run the collector: `python newsletter.py --type ai`
2. Open the generated `*_prompt.md` file
3. Ask Claude to process it for a polished newsletter

Example Claude prompt:
```
Please read the file output/ai_2024-01-15_prompt.md and generate
a polished newsletter based on the collected content.
```

## Automation

### Cron Job (Weekly)

```bash
# Run every Sunday at 8 AM
0 8 * * 0 cd /path/to/Weekly-newsletter && python newsletter.py >> /var/log/newsletter.log 2>&1
```

### GitHub Actions

```yaml
name: Weekly Newsletter
on:
  schedule:
    - cron: '0 8 * * 0'  # Every Sunday at 8 AM UTC

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python newsletter.py
      - uses: actions/upload-artifact@v4
        with:
          name: newsletters
          path: output/
```

## Extending

### Adding New Sources

1. Create a new collector in `sources/`
2. Inherit from `BaseCollector`
3. Implement `collect()` method
4. Add to `sources/__init__.py`

```python
from sources.base import BaseCollector, ContentItem, SourceType

class MyCollector(BaseCollector):
    @property
    def source_type(self) -> SourceType:
        return SourceType.RSS  # or add new type

    async def collect(self, topics, **kwargs):
        # Fetch and parse your source
        return [ContentItem(...), ...]
```

### Adding New Newsletter Types

Add to `config.yaml`:

```yaml
newsletters:
  my_topic:
    name: "My Topic Weekly"
    topics:
      - "keyword1"
      - "keyword2"
    sources:
      reddit:
        - "relevant_subreddit"
      # ... more sources
```

## Troubleshooting

### Rate Limiting

If you see "Rate limited" messages:
- Reddit: Wait 60 seconds between runs
- ArXiv: Built-in 3-second delay between requests

### No Items Collected

1. Check your internet connection
2. Verify subreddit names are correct
3. Try increasing `--days` parameter
4. Check if RSS feed URLs are valid

### Import Errors

Ensure you're running from the project root:
```bash
cd Weekly-newsletter
python newsletter.py
```

## License

MIT License - feel free to use and modify.

## Contributing

Contributions welcome! Please open an issue or PR.
