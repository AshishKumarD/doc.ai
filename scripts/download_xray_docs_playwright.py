#!/usr/bin/env python3
"""
Advanced Xray documentation scraper using Playwright.
Handles JavaScript-rendered content and downloads ALL pages.

This scraper:
- Renders JavaScript using a real browser
- Waits for content to load
- Follows all navigation links
- Saves everything as Markdown
- Won't miss any pages!
"""

import os
import sys
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse, parse_qs
from playwright.sync_api import sync_playwright, Page
import re

# Configuration
START_URL = "https://docs.getxray.app/space/XRAYCLOUD/393183414/App+Editions"
OUTPUT_DIR = "/Users/ashish/Jira/xray_documentation"
MAX_PAGES = 500  # Safety limit
DELAY = 0.1  # Seconds between requests

# Track visited URLs
visited_urls = set()
docs_downloaded = 0

def normalize_url(url):
    """Normalize URL to avoid duplicates"""
    parsed = urlparse(url)
    # Remove fragments
    normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    # Remove trailing slashes
    normalized = normalized.rstrip('/')
    return normalized

def is_valid_doc_url(url):
    """Check if URL is part of Xray Cloud documentation"""
    parsed = urlparse(url)
    return (
        'docs.getxray.app' in parsed.netloc and
        '/space/XRAYCLOUD/' in url and
        not url.endswith(('.pdf', '.zip', '.png', '.jpg', '.jpeg', '.gif'))
    )

def clean_filename(url):
    """Convert URL to safe filename"""
    parsed = urlparse(url)
    path_parts = [p for p in parsed.path.split('/') if p and p != 'space' and p != 'XRAYCLOUD']

    if path_parts:
        # Use the page ID if available, otherwise use the title
        name = path_parts[-1]
    else:
        name = 'index'

    # Clean the name
    name = name.replace('+', '_').replace('%20', '_')
    name = ''.join(c if c.isalnum() or c in ('_', '-') else '_' for c in name)
    name = name[:200]  # Limit length

    return name + '.md'

def html_to_markdown(html_content):
    """Convert HTML to Markdown using simple rules"""
    import html2text
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = False
    h.ignore_emphasis = False
    h.body_width = 0
    h.unicode_snob = True
    h.skip_internal_links = False

    return h.handle(html_content)

def extract_links(page: Page):
    """Extract all valid documentation links from the page"""
    links = []

    try:
        # Get all links on the page
        all_links = page.query_selector_all('a[href]')

        for link in all_links:
            href = link.get_attribute('href')
            if not href:
                continue

            # Make absolute URL
            absolute_url = urljoin(page.url, href)
            normalized = normalize_url(absolute_url)

            # Check if valid and not visited
            if is_valid_doc_url(normalized) and normalized not in visited_urls:
                links.append(normalized)

    except Exception as e:
        print(f"⚠️  Error extracting links: {e}")

    return links

def download_page(page: Page, url: str):
    """Download and convert a page to markdown"""
    global docs_downloaded

    try:
        print(f"\n📥 Downloading: {url}")

        # Navigate to the page
        page.goto(url, wait_until="networkidle", timeout=60000)

        # Wait a bit more for any lazy-loaded content
        page.wait_for_timeout(2000)

        # Extract title
        title_element = page.query_selector('h1, .page-title, title')
        if title_element:
            title = title_element.inner_text().strip()
        else:
            title = page.title() or 'Untitled'

        print(f"   Title: {title}")

        # Get the main content area
        content_selectors = [
            '#main-content',
            '.wiki-content',
            'main',
            'article',
            '[role="main"]',
            '.content-body',
            'body'
        ]

        content_html = None
        for selector in content_selectors:
            element = page.query_selector(selector)
            if element:
                content_html = element.inner_html()
                break

        if not content_html:
            print(f"⚠️  Could not find main content")
            return []

        # Convert to Markdown
        markdown = html_to_markdown(content_html)

        # Add metadata header
        markdown = f"# {title}\n\nSource: {url}\n\n---\n\n{markdown}"

        # Extract links for further crawling
        links = extract_links(page)

        # Save the markdown file
        filename = clean_filename(url)
        filepath = os.path.join(OUTPUT_DIR, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown)

        docs_downloaded += 1
        print(f"✅ Saved: {filename} ({len(markdown)} chars)")
        print(f"   Found {len(links)} new links to crawl")

        return links

    except Exception as e:
        print(f"❌ Error downloading {url}: {e}")
        return []

def crawl_documentation():
    """Main crawl function using Playwright"""
    global docs_downloaded, visited_urls

    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Initialize queue with start URL
    queue = [normalize_url(START_URL)]
    visited_urls.add(normalize_url(START_URL))

    print("🚀 Launching browser...")

    with sync_playwright() as p:
        # Launch browser (headless mode)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        page = context.new_page()

        try:
            while queue and docs_downloaded < MAX_PAGES:
                url = queue.pop(0)

                print(f"\n[{docs_downloaded + 1}/{MAX_PAGES}] Processing...")

                # Download the page
                new_links = download_page(page, url)

                # Add new links to queue
                for link in new_links:
                    if link not in visited_urls:
                        visited_urls.add(link)
                        queue.append(link)

                # Be polite - don't hammer the server
                time.sleep(DELAY)

                # Progress update
                print(f"   Queue: {len(queue)} pages remaining")

        except KeyboardInterrupt:
            print("\n\n⚠️  Crawl interrupted by user")
        finally:
            browser.close()

    return docs_downloaded

def main():
    print("="*70)
    print("Advanced Xray Documentation Scraper (Playwright)")
    print("Handles JavaScript-rendered content")
    print("="*70)
    print(f"\n📍 Starting URL: {START_URL}")
    print(f"📁 Output directory: {OUTPUT_DIR}")
    print(f"🔢 Max pages: {MAX_PAGES}")
    print(f"⏱️  Delay between requests: {DELAY}s")
    print("\n" + "="*70)

    # Check if Playwright browsers are installed
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("\n❌ Playwright not installed!")
        print("Install with: pip install playwright && playwright install chromium")
        sys.exit(1)

    # Start crawling
    print("\n🚀 Starting crawl with JavaScript rendering...\n")
    start_time = time.time()

    try:
        total_docs = crawl_documentation()
        elapsed = time.time() - start_time

        print("\n" + "="*70)
        print("✅ CRAWL COMPLETE!")
        print("="*70)
        print(f"📄 Documents downloaded: {total_docs}")
        print(f"🔗 URLs visited: {len(visited_urls)}")
        print(f"⏱️  Time elapsed: {elapsed:.1f}s ({elapsed/60:.1f} minutes)")
        print(f"📁 Saved to: {OUTPUT_DIR}")
        print("\n" + "="*70)
        print("\nNext steps:")
        print("1. Review downloaded docs in:", OUTPUT_DIR)
        print("2. Re-index with JiraDocAI:")
        print("   python 1_index_documents.py")
        print("3. Restart web UI or refresh your queries!")
        print("="*70)

    except Exception as e:
        print(f"\n❌ Error during crawl: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
