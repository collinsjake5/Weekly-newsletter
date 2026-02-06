# YouTube Transcripts

Drop `.md` files here with video transcripts you want included in the newsletter.

## File Format

Each file should have a frontmatter header with metadata:

```markdown
---
title: The Video Title
url: https://youtube.com/watch?v=xxxxx
channel: Channel Name
type: ai
highlights: Key point 1. Key point 2. Main takeaway.
---

[Paste transcript content here]
```

## Fields

| Field | Required | Description |
|-------|----------|-------------|
| `title` | Yes | Video title |
| `url` | Yes | YouTube URL |
| `channel` | No | Channel name (default: "YouTube") |
| `type` | No | Force into specific newsletter: `ai` or `robotics` |
| `highlights` | **Recommended** | Your notes on what's important - this becomes the summary |

## Example

```markdown
---
title: Figure 01 learns to make coffee - Full Demo
url: https://youtube.com/watch?v=abc123
channel: Figure AI
type: robotics
highlights: First demo of Figure 01 humanoid performing multi-step coffee making task. Uses vision-language model for understanding. Completed task in 2 minutes with zero failures.
---

[00:00] Welcome to Figure AI's latest demo...
[00:15] Today we're showing Figure 01 making coffee...
...
```

## Tips

1. **Highlights are key** - Write 2-3 sentences about why this video matters
2. **Use `type`** to ensure video goes in the right newsletter
3. **Transcripts are archived** after each newsletter run (moved to `archive/` subfolder)

## Getting Transcripts

- **YouTube**: Click "..." → "Show transcript" → Copy
- **Browser extension**: [YouTube Transcript](https://chrome.google.com/webstore/detail/youtube-transcript/...)
- **Online tool**: https://www.youtube-transcript.com/
