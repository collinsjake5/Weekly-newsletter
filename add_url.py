#!/usr/bin/env python3
"""
Quick helper to add URLs to the inbox.

Usage:
    python add_url.py URL [NOTE]
    python add_url.py --ai URL [NOTE]
    python add_url.py --robotics URL [NOTE]
    python add_url.py --list
    python add_url.py --clear

Examples:
    python add_url.py https://example.com/article
    python add_url.py https://example.com/article "Great article about robots"
    python add_url.py --robotics https://example.com/article
    python add_url.py --ai https://openai.com/blog "New GPT model"
"""

import argparse
import sys
from pathlib import Path


INBOX_PATH = Path(__file__).parent / "inbox.txt"


def add_url(url: str, note: str = None, newsletter_type: str = None):
    """Add a URL to the inbox."""
    # Build the line
    line = ""
    if newsletter_type:
        line = f"{newsletter_type}: "
    line += url
    if note:
        line += f" | {note}"
    line += "\n"

    # Append to inbox
    with open(INBOX_PATH, 'a') as f:
        f.write(line)

    print(f"✅ Added to inbox: {url}")
    if note:
        print(f"   Note: {note}")
    if newsletter_type:
        print(f"   Newsletter: {newsletter_type}")


def list_inbox():
    """List all URLs in the inbox."""
    if not INBOX_PATH.exists():
        print("Inbox is empty.")
        return

    with open(INBOX_PATH, 'r') as f:
        lines = f.readlines()

    entries = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            entries.append(line)

    if not entries:
        print("Inbox is empty.")
        return

    print(f"📥 Inbox ({len(entries)} items):\n")
    for i, entry in enumerate(entries, 1):
        print(f"  {i}. {entry}")


def clear_inbox():
    """Clear all URLs from the inbox."""
    header = """# URL Inbox
# ==========
# Add URLs here (one per line) throughout the week.
# They will be included in your next newsletter run.
#
# Format options:
#   https://example.com/article
#   https://example.com/article | Optional note about the article
#   ai: https://example.com/article | Force into AI newsletter
#   robotics: https://example.com/article | Force into Robotics newsletter
#
# Lines starting with # are ignored.
# This file is automatically cleared after each newsletter run.
#

"""
    with open(INBOX_PATH, 'w') as f:
        f.write(header)

    print("🗑️  Inbox cleared.")


def main():
    parser = argparse.ArgumentParser(
        description="Add URLs to the newsletter inbox",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python add_url.py https://example.com/article
    python add_url.py https://example.com/article "Great article"
    python add_url.py --ai https://openai.com/blog "New model"
    python add_url.py --robotics https://example.com/robots
    python add_url.py --list
    python add_url.py --clear
        """
    )

    parser.add_argument('url', nargs='?', help='URL to add')
    parser.add_argument('note', nargs='?', help='Optional note about the URL')
    parser.add_argument('--ai', action='store_true', help='Force into AI newsletter')
    parser.add_argument('--robotics', action='store_true', help='Force into Robotics newsletter')
    parser.add_argument('--list', '-l', action='store_true', help='List inbox contents')
    parser.add_argument('--clear', action='store_true', help='Clear the inbox')

    args = parser.parse_args()

    if args.list:
        list_inbox()
        return

    if args.clear:
        clear_inbox()
        return

    if not args.url:
        parser.print_help()
        sys.exit(1)

    # Validate URL
    if not args.url.startswith(('http://', 'https://')):
        print(f"❌ Invalid URL: {args.url}")
        print("   URL must start with http:// or https://")
        sys.exit(1)

    # Determine newsletter type
    newsletter_type = None
    if args.ai:
        newsletter_type = "ai"
    elif args.robotics:
        newsletter_type = "robotics"

    add_url(args.url, args.note, newsletter_type)


if __name__ == "__main__":
    main()
