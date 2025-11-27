#!/usr/bin/env python3
"""
Enhanced Xray Documentation Downloader with:
- Resume capability (skip existing pages)
- Tree structure index/TOC generation
- Progress tracking
"""

import os
import sys
import time
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from pathlib import Path
import html2text
from collections import defaultdict

# Configuration
START_URL = "https://docs.getxray.app/space/XRAYCLOUD/393183414/App+Editions"
OUTPUT_DIR = "/Users/ashish/Jira/xray_documentation"
INDEX_FILE = "/Users/ashish/Jira/xray_documentation/INDEX.json"
TOC_FILE = "/Users/ashish/Jira/xray_documentation/TABLE_OF_CONTENTS.md"
MAX_DEPTH = 5
DELAY = 1  # Seconds between requests

# Track visited URLs and page hierarchy
visited_urls = set()
page_metadata = {}  # url -> {title, filename, depth, parent}
docs_downloaded = 0
docs_skipped = 0

def load_progress():
    """Load previously downloaded pages"""
    global visited_urls, page_metadata

    if os.path.exists(INDEX_FILE):
        try:
            with open(INDEX_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                visited_urls = set(data.get('visited_urls', []))
                page_metadata = data.get('page_metadata', {})
            print(f"📋 Loaded progress: {len(visited_urls)} URLs already visited")
        except Exception as e:
            print(f"⚠️  Could not load progress file: {e}")

def save_progress():
    """Save progress for resume capability"""
    try:
        data = {
            'visited_urls': list(visited_urls),
            'page_metadata': page_metadata,
            'last_updated': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        with open(INDEX_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"⚠️  Could not save progress: {e}")

def extract_page_id(url):
    """Extract page ID from URL for filename"""
    # Xray docs URLs like: /space/XRAYCLOUD/393183414/Page+Title
    parts = url.split('/')
    for i, part in enumerate(parts):
        if part.isdigit() and len(part) >= 6:
            return part
    return None

def get_filename_from_url(url):
    """Get filename for a URL"""
    page_id = extract_page_id(url)
    if page_id:
        return f"{page_id}.md"

    # Fallback to old method
    parsed = urlparse(url)
    path = parsed.path.strip('/')
    parts = [p for p in path.split('/') if p]
    if parts:
        name = parts[-1].replace('+', '_').replace('%20', '_')
    else:
        name = 'index'

    name = ''.join(c if c.isalnum() or c in ('_', '-') else '_' for c in name)
    return name[:200] + '.md'

def is_valid_doc_url(url):
    """Check if URL is part of Xray documentation"""
    parsed = urlparse(url)
    return (
        'docs.getxray.app' in parsed.netloc and
        '/space/XRAYCLOUD/' in url
    )

def file_exists_for_url(url):
    """Check if file already exists for this URL"""
    filename = get_filename_from_url(url)
    filepath = os.path.join(OUTPUT_DIR, filename)
    return os.path.exists(filepath)

def download_page(url, depth=0, parent_url=None):
    """Download and convert a page to markdown"""
    global docs_downloaded, docs_skipped

    # Check if already exists
    if file_exists_for_url(url):
        print(f"⏭️  Skipping (exists): {url}")
        docs_skipped += 1

        # Still extract metadata if not already present
        if url not in page_metadata:
            filename = get_filename_from_url(url)
            filepath = os.path.join(OUTPUT_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    first_line = f.readline()
                    if first_line.startswith('# '):
                        title = first_line[2:].strip()
                        page_metadata[url] = {
                            'title': title,
                            'filename': filename,
                            'depth': depth,
                            'parent': parent_url
                        }
            except:
                pass

        return None, []

    try:
        print(f"📥 Downloading: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find main content
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
        h.body_width = 0

        markdown = h.handle(str(content))

        # Add metadata header
        markdown = f"# {title_text}\n\nSource: {url}\n\n---\n\n{markdown}"

        # Save filename
        filename = get_filename_from_url(url)

        # Store metadata
        page_metadata[url] = {
            'title': title_text,
            'filename': filename,
            'depth': depth,
            'parent': parent_url
        }

        # Find all links in content for further crawling
        links = []
        for link in content.find_all('a', href=True):
            href = urljoin(url, link['href'])
            if is_valid_doc_url(href) and href not in visited_urls:
                links.append(href)

        docs_downloaded += 1
        return (markdown, filename), links

    except Exception as e:
        print(f"❌ Error downloading {url}: {e}")
        return None, []

def save_markdown(filename, content):
    """Save markdown content to file"""
    filepath = os.path.join(OUTPUT_DIR, filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✅ Saved: {filename}")

def generate_toc():
    """Generate tree structure Table of Contents"""
    print("\n📚 Generating Table of Contents...")

    # Build tree structure
    tree = defaultdict(list)
    root_pages = []

    for url, meta in page_metadata.items():
        parent = meta.get('parent')
        if parent and parent in page_metadata:
            tree[parent].append(url)
        else:
            root_pages.append(url)

    # Sort by depth and title
    root_pages.sort(key=lambda u: (page_metadata[u]['depth'], page_metadata[u]['title']))

    def write_tree(f, url, level=0):
        """Recursively write tree structure"""
        meta = page_metadata[url]
        indent = "  " * level
        icon = "📄" if level > 0 else "📁"

        # Write current page
        f.write(f"{indent}{icon} [{meta['title']}]({meta['filename']}) `{meta['filename']}`\n")

        # Write children
        children = tree.get(url, [])
        children.sort(key=lambda u: page_metadata[u]['title'])
        for child in children:
            write_tree(f, child, level + 1)

    # Write TOC file
    try:
        with open(TOC_FILE, 'w', encoding='utf-8') as f:
            f.write("# Xray Documentation - Table of Contents\n\n")
            f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"Total Pages: {len(page_metadata)}\n\n")
            f.write("---\n\n")
            f.write("## 📚 Documentation Tree\n\n")

            # Write root pages
            for url in root_pages:
                write_tree(f, url, 0)
                f.write("\n")

            # Write orphaned pages (no parent)
            f.write("\n---\n\n")
            f.write("## 📋 All Pages (Alphabetical)\n\n")
            sorted_pages = sorted(page_metadata.items(), key=lambda x: x[1]['title'])
            for url, meta in sorted_pages:
                f.write(f"- [{meta['title']}]({meta['filename']}) - `{url}`\n")

        print(f"✅ TOC saved to: {TOC_FILE}")
    except Exception as e:
        print(f"❌ Error generating TOC: {e}")

def crawl(start_url, max_depth=5):
    """Recursively crawl documentation"""
    queue = [(start_url, 0, None)]  # (url, depth, parent_url)
    visited_urls.add(start_url)

    while queue:
        url, depth, parent_url = queue.pop(0)

        if depth > max_depth:
            continue

        print(f"\n[Depth {depth}] Processing: {url}")

        # Download page (will skip if exists)
        result, links = download_page(url, depth, parent_url)

        if result:
            markdown, filename = result
            save_markdown(filename, markdown)

            # Add new links to queue
            for link in links:
                if link not in visited_urls:
                    visited_urls.add(link)
                    queue.append((link, depth + 1, url))

        # Save progress periodically
        if (docs_downloaded + docs_skipped) % 10 == 0:
            save_progress()

        # Be polite
        time.sleep(DELAY)

    return docs_downloaded, docs_skipped

def main():
    print("="*70)
    print("Enhanced Xray Documentation Downloader")
    print("With Resume & Tree Structure TOC")
    print("="*70)
    print(f"\n📍 Starting URL: {START_URL}")
    print(f"📁 Output directory: {OUTPUT_DIR}")
    print(f"🔢 Max depth: {MAX_DEPTH}")
    print(f"⏱️  Delay: {DELAY}s")
    print("\n" + "="*70)

    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Check dependencies
    try:
        import requests
        import bs4
        import html2text
    except ImportError:
        print("\n❌ Missing required library!")
        print("Install with: pip install requests beautifulsoup4 html2text")
        sys.exit(1)

    # Load previous progress
    load_progress()

    # Start crawling
    print("\n🚀 Starting crawl (will skip existing pages)...\n")
    start_time = time.time()

    try:
        downloaded, skipped = crawl(START_URL, MAX_DEPTH)
        elapsed = time.time() - start_time

        # Save final progress
        save_progress()

        # Generate TOC
        generate_toc()

        print("\n" + "="*70)
        print("✅ CRAWL COMPLETE!")
        print("="*70)
        print(f"📥 New documents downloaded: {downloaded}")
        print(f"⏭️  Documents skipped (existed): {skipped}")
        print(f"📄 Total pages: {len(page_metadata)}")
        print(f"🔗 URLs visited: {len(visited_urls)}")
        print(f"⏱️  Time elapsed: {elapsed:.1f}s")
        print(f"📁 Saved to: {OUTPUT_DIR}")
        print(f"📚 TOC: {TOC_FILE}")
        print("\n" + "="*70)
        print("\nNext steps:")
        print("1. View TOC:", TOC_FILE)
        print("2. Index docs: python 1_index_documents.py")
        print("3. Start querying!")
        print("="*70)

    except KeyboardInterrupt:
        print("\n\n⚠️  Crawl interrupted by user")
        print(f"Downloaded {docs_downloaded} new documents")
        print(f"Skipped {docs_skipped} existing documents")
        save_progress()
        generate_toc()
    except Exception as e:
        print(f"\n❌ Error during crawl: {e}")
        save_progress()
        sys.exit(1)

if __name__ == "__main__":
    main()
