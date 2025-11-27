#!/usr/bin/env python3
"""
Scan existing documentation files and continue scraping.
1. Indexes all existing .md files (extract URL and title)
2. Generates TOC from existing files
3. Continues scraping for missing pages
"""

import os
import re
import json
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import html2text
from collections import defaultdict

# Configuration
START_URL = "https://docs.getxray.app/space/XRAYCLOUD"
OUTPUT_DIR = "/Users/ashish/Jira/xray_documentation"
INDEX_FILE = os.path.join(OUTPUT_DIR, "INDEX.json")
TOC_FILE = os.path.join(OUTPUT_DIR, "TABLE_OF_CONTENTS.md")
MAX_DEPTH = 3  # Reduced for faster crawling
DELAY = 1

# Track everything
visited_urls = set()
page_metadata = {}
docs_downloaded = 0
docs_skipped = 0

def scan_existing_files():
    """Scan all existing .md files and extract metadata"""
    print("🔍 Scanning existing documentation files...")

    scanned = 0
    for filename in os.listdir(OUTPUT_DIR):
        if not filename.endswith('.md') or filename in ['TABLE_OF_CONTENTS.md', 'INDEX.md']:
            continue

        filepath = os.path.join(OUTPUT_DIR, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract title (first line starting with #)
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            title = title_match.group(1).strip() if title_match else filename

            # Extract URL (Source: line)
            url_match = re.search(r'^Source:\s+(.+)$', content, re.MULTILINE)
            if url_match:
                url = url_match.group(1).strip()

                # Store metadata
                page_metadata[url] = {
                    'title': title,
                    'filename': filename,
                    'depth': 0,  # Unknown depth for existing files
                    'parent': None
                }
                visited_urls.add(url)
                scanned += 1

        except Exception as e:
            print(f"⚠️  Error scanning {filename}: {e}")

    print(f"✅ Scanned {scanned} existing files")
    return scanned

def is_valid_doc_url(url):
    """Check if URL is part of Xray documentation"""
    return 'docs.getxray.app' in url and '/space/XRAYCLOUD/' in url

def extract_page_id(url):
    """Extract page ID from URL"""
    parts = url.split('/')
    for part in parts:
        if part.isdigit() and len(part) >= 6:
            return part
    return None

def get_filename_from_url(url):
    """Get filename for a URL"""
    page_id = extract_page_id(url)
    return f"{page_id}.md" if page_id else None

def file_exists_for_url(url):
    """Check if file already exists"""
    filename = get_filename_from_url(url)
    if not filename:
        return False
    return os.path.exists(os.path.join(OUTPUT_DIR, filename))

def download_page(url, depth=0, parent_url=None):
    """Download and save a page"""
    global docs_downloaded, docs_skipped

    if file_exists_for_url(url):
        print(f"⏭️  Exists: {url}")
        docs_skipped += 1
        return None, []

    try:
        print(f"📥 Downloading: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        content = soup.find('div', class_='wiki-content') or soup.find('main') or soup.find('body')

        if not content:
            return None, []

        # Extract title
        title = soup.find('h1')
        title_text = title.get_text().strip() if title else 'Untitled'

        # Convert to markdown
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.body_width = 0
        markdown = h.handle(str(content))
        markdown = f"# {title_text}\n\nSource: {url}\n\n---\n\n{markdown}"

        # Get filename
        filename = get_filename_from_url(url)
        if not filename:
            print(f"⚠️  Could not generate filename for {url}")
            return None, []

        # Store metadata
        page_metadata[url] = {
            'title': title_text,
            'filename': filename,
            'depth': depth,
            'parent': parent_url
        }

        # Find links
        links = []
        for link in content.find_all('a', href=True):
            href = urljoin(url, link['href'])
            if is_valid_doc_url(href) and href not in visited_urls:
                links.append(href)

        docs_downloaded += 1
        return (markdown, filename), links

    except Exception as e:
        print(f"❌ Error: {e}")
        return None, []

def save_markdown(filename, content):
    """Save markdown file"""
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Saved: {filename}")

def crawl_from_existing():
    """Continue crawling from existing pages"""
    print(f"\n🚀 Continuing crawl from {len(visited_urls)} existing pages...\n")

    # Queue ALL existing URLs to extract their links
    queue = [(url, 1, None) for url in list(visited_urls)]  # Use ALL pages

    while queue:
        url, depth, parent_url = queue.pop(0)

        if depth > MAX_DEPTH:
            continue

        print(f"[Depth {depth}] Checking: {url}")

        # If file exists, just extract links from the page
        if file_exists_for_url(url):
            try:
                response = requests.get(url, timeout=30)
                soup = BeautifulSoup(response.content, 'html.parser')
                content = soup.find('div', class_='wiki-content') or soup.find('main')

                if content:
                    for link in content.find_all('a', href=True):
                        href = urljoin(url, link['href'])
                        if is_valid_doc_url(href) and href not in visited_urls:
                            visited_urls.add(href)
                            queue.append((href, depth + 1, url))
            except:
                pass
        else:
            # Download new page
            result, links = download_page(url, depth, parent_url)
            if result:
                markdown, filename = result
                save_markdown(filename, markdown)

                for link in links:
                    if link not in visited_urls:
                        visited_urls.add(link)
                        queue.append((link, depth + 1, url))

        # Save progress periodically
        if (docs_downloaded + docs_skipped) % 20 == 0:
            save_progress()
            generate_toc()

        time.sleep(DELAY)

def save_progress():
    """Save progress"""
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

def generate_toc():
    """Generate Table of Contents"""
    try:
        with open(TOC_FILE, 'w', encoding='utf-8') as f:
            f.write("# Xray Documentation - Table of Contents\n\n")
            f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Total Pages: {len(page_metadata)}**\n\n")
            f.write("---\n\n")
            f.write("## 📋 All Pages (Alphabetical)\n\n")

            # Sort by title
            sorted_pages = sorted(page_metadata.items(), key=lambda x: x[1]['title'].lower())

            for url, meta in sorted_pages:
                title = meta['title'].replace(' - Xray Cloud Documentation - XRAY view', '')
                f.write(f"- [{title}]({meta['filename']})\n")
                f.write(f"  - 🔗 {url}\n")

        print(f"✅ TOC updated: {TOC_FILE}")
    except Exception as e:
        print(f"❌ Error generating TOC: {e}")

def main():
    print("="*70)
    print("Xray Documentation Scanner & Scraper")
    print("="*70)
    print(f"📁 Directory: {OUTPUT_DIR}\n")

    # Step 1: Scan existing files
    existing_count = scan_existing_files()

    # Step 2: Generate initial TOC
    print("\n📚 Generating initial TOC...")
    generate_toc()

    # Step 3: Continue scraping
    start_time = time.time()

    try:
        crawl_from_existing()

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")

    finally:
        elapsed = time.time() - start_time

        # Final save
        save_progress()
        generate_toc()

        print("\n" + "="*70)
        print("✅ COMPLETE!")
        print("="*70)
        print(f"📄 Existing files indexed: {existing_count}")
        print(f"📥 New pages downloaded: {docs_downloaded}")
        print(f"📊 Total pages: {len(page_metadata)}")
        print(f"⏱️  Time: {elapsed:.1f}s")
        print(f"📚 TOC: {TOC_FILE}")
        print("="*70)

if __name__ == "__main__":
    main()
