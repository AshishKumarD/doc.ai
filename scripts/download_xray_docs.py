#!/usr/bin/env python3
"""
Download Xray documentation from the web for indexing in JiraDocAI.
Crawls the documentation site and saves all pages as markdown files.
"""

import os
import sys
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from pathlib import Path
import html2text

# Configuration
START_URL = "https://docs.getxray.app/space/XRAYCLOUD/393183414/App+Editions"
OUTPUT_DIR = "/Users/ashish/Jira/xray_documentation"
MAX_DEPTH = 5  # How deep to crawl (5 levels should get everything)
DELAY = 1  # Seconds between requests (be polite!)

# Track visited URLs to avoid duplicates
visited_urls = set()
docs_downloaded = 0

def is_valid_doc_url(url):
    """Check if URL is part of Xray documentation"""
    parsed = urlparse(url)
    return (
        'docs.getxray.app' in parsed.netloc and
        '/space/XRAYCLOUD/' in url
    )

def clean_filename(url):
    """Convert URL to safe filename"""
    parsed = urlparse(url)
    path = parsed.path.strip('/')

    # Get the last part of the path as filename
    parts = [p for p in path.split('/') if p]
    if parts:
        name = parts[-1].replace('+', '_').replace('%20', '_')
    else:
        name = 'index'

    # Add query params if present
    if parsed.query:
        name += '_' + parsed.query.replace('=', '_').replace('&', '_')

    # Remove special chars and limit length
    name = ''.join(c if c.isalnum() or c in ('_', '-') else '_' for c in name)
    name = name[:200]  # Limit filename length

    return name + '.md'

def download_page(url):
    """Download and convert a page to markdown"""
    global docs_downloaded

    try:
        print(f"📥 Downloading: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        # Try to find main content area (adjust selectors as needed)
        content = soup.find('div', class_='wiki-content') or \
                  soup.find('main') or \
                  soup.find('article') or \
                  soup.find('body')

        if not content:
            print(f"⚠️  Could not find main content in {url}")
            return None, []

        # Extract title
        title = soup.find('h1')
        title_text = title.get_text().strip() if title else 'Untitled'

        # Convert HTML to Markdown
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = False
        h.ignore_emphasis = False
        h.body_width = 0  # Don't wrap lines

        markdown = h.handle(str(content))

        # Add metadata header
        markdown = f"# {title_text}\n\nSource: {url}\n\n---\n\n{markdown}"

        # Find all links in content for further crawling
        links = []
        for link in content.find_all('a', href=True):
            href = urljoin(url, link['href'])
            if is_valid_doc_url(href) and href not in visited_urls:
                links.append(href)

        docs_downloaded += 1
        return markdown, links

    except Exception as e:
        print(f"❌ Error downloading {url}: {e}")
        return None, []

def save_markdown(filename, content):
    """Save markdown content to file"""
    filepath = os.path.join(OUTPUT_DIR, filename)

    # Create subdirectories if needed
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✅ Saved: {filename}")

def crawl(start_url, max_depth=5):
    """Recursively crawl documentation"""
    # Queue: (url, depth)
    queue = [(start_url, 0)]
    visited_urls.add(start_url)

    while queue:
        url, depth = queue.pop(0)

        if depth > max_depth:
            continue

        print(f"\n[Depth {depth}] Processing: {url}")

        # Download page
        markdown, links = download_page(url)

        if markdown:
            # Save to file
            filename = clean_filename(url)
            save_markdown(filename, content=markdown)

            # Add new links to queue
            for link in links:
                if link not in visited_urls:
                    visited_urls.add(link)
                    queue.append((link, depth + 1))

        # Be polite - don't hammer the server
        time.sleep(DELAY)

    return docs_downloaded

def main():
    print("="*70)
    print("Xray Documentation Downloader for JiraDocAI")
    print("="*70)
    print(f"\n📍 Starting URL: {START_URL}")
    print(f"📁 Output directory: {OUTPUT_DIR}")
    print(f"🔢 Max depth: {MAX_DEPTH}")
    print(f"⏱️  Delay between requests: {DELAY}s")
    print("\n" + "="*70)

    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Check dependencies
    try:
        import requests
        import bs4
        import html2text
    except ImportError as e:
        print("\n❌ Missing required library!")
        print("Install with: pip install requests beautifulsoup4 html2text")
        sys.exit(1)

    # Start crawling
    print("\n🚀 Starting crawl...\n")
    start_time = time.time()

    try:
        total_docs = crawl(START_URL, MAX_DEPTH)
        elapsed = time.time() - start_time

        print("\n" + "="*70)
        print("✅ CRAWL COMPLETE!")
        print("="*70)
        print(f"📄 Documents downloaded: {total_docs}")
        print(f"🔗 URLs visited: {len(visited_urls)}")
        print(f"⏱️  Time elapsed: {elapsed:.1f}s")
        print(f"📁 Saved to: {OUTPUT_DIR}")
        print("\n" + "="*70)
        print("\nNext steps:")
        print("1. Review downloaded docs in:", OUTPUT_DIR)
        print("2. Index them with JiraDocAI:")
        print("   python 1_index_documents.py")
        print("3. Start asking questions!")
        print("="*70)

    except KeyboardInterrupt:
        print("\n\n⚠️  Crawl interrupted by user")
        print(f"Downloaded {docs_downloaded} documents before stopping")
    except Exception as e:
        print(f"\n❌ Error during crawl: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
