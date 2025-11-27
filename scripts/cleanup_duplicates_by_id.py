#!/usr/bin/env python3
"""
Smart duplicate cleanup based on page ID.
Groups files by Xray page ID (e.g., 44566476) and keeps the one with the fuller URL.

Logic:
- Same page ID = duplicate
- Keep: URL with title in path (e.g., /44566476/About+Xray)
- Remove: URL without title (e.g., /44566476)
"""

import os
import re
from collections import defaultdict

OUTPUT_DIR = "/Users/ashish/Jira/xray_documentation"

def extract_page_id_from_url(url):
    """Extract page ID from URL"""
    match = re.search(r'/space/XRAYCLOUD/(\d+)', url)
    return match.group(1) if match else None

def extract_url_from_file(filepath):
    """Extract Source URL from file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        url_match = re.search(r'^Source:\s+(.+)$', content, re.MULTILINE)
        return url_match.group(1).strip() if url_match else None
    except:
        return None

def extract_title_from_file(filepath):
    """Extract title from file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        return title_match.group(1).strip() if title_match else None
    except:
        return None

def url_has_title(url):
    """Check if URL includes the page title in path"""
    # URLs with title: /44566476/About+Xray
    # URLs without: /44566476
    parts = url.split('/')
    for i, part in enumerate(parts):
        if part.isdigit() and len(part) >= 6:
            # Check if there's a part after the ID
            return i + 1 < len(parts) and parts[i + 1]
    return False

def find_duplicates_by_id():
    """Group files by page ID and find duplicates"""
    id_to_files = defaultdict(list)

    print("🔍 Scanning files by page ID...")

    for filename in os.listdir(OUTPUT_DIR):
        if not filename.endswith('.md') or filename in ['TABLE_OF_CONTENTS.md', 'INDEX.md']:
            continue

        filepath = os.path.join(OUTPUT_DIR, filename)
        url = extract_url_from_file(filepath)

        if url:
            page_id = extract_page_id_from_url(url)
            if page_id:
                title = extract_title_from_file(filepath)
                id_to_files[page_id].append({
                    'filename': filename,
                    'url': url,
                    'title': title,
                    'has_title_in_url': url_has_title(url)
                })

    # Find page IDs with multiple files
    duplicates = {pid: files for pid, files in id_to_files.items() if len(files) > 1}

    return duplicates

def cleanup_duplicates(duplicates, dry_run=True):
    """Clean up duplicates, keeping the file with fuller URL"""
    removed_count = 0
    kept_count = 0

    for page_id, files in duplicates.items():
        # Sort: Files with title in URL first, then by URL length (longer = more complete)
        files.sort(key=lambda f: (not f['has_title_in_url'], -len(f['url'])))

        # Keep the first (most complete URL)
        keep_file = files[0]
        remove_files = files[1:]

        print(f"\n📄 Page ID: {page_id}")
        print(f"  ✅ KEEP: {keep_file['filename']}")
        print(f"     URL: {keep_file['url']}")

        for remove_file in remove_files:
            print(f"  ❌ REMOVE: {remove_file['filename']}")
            print(f"     URL: {remove_file['url']}")

            if not dry_run:
                filepath = os.path.join(OUTPUT_DIR, remove_file['filename'])
                try:
                    os.remove(filepath)
                    removed_count += 1
                except Exception as e:
                    print(f"     ⚠️  Error removing: {e}")

        kept_count += 1

    return kept_count, removed_count

def regenerate_toc():
    """Regenerate TOC with clean files"""
    print("\n📚 Regenerating Table of Contents...")

    page_metadata = {}

    for filename in os.listdir(OUTPUT_DIR):
        if not filename.endswith('.md') or filename in ['TABLE_OF_CONTENTS.md', 'INDEX.md']:
            continue

        filepath = os.path.join(OUTPUT_DIR, filename)
        url = extract_url_from_file(filepath)
        title = extract_title_from_file(filepath)

        if url and title:
            page_metadata[url] = {
                'title': title,
                'filename': filename
            }

    # Write TOC
    import time
    toc_path = os.path.join(OUTPUT_DIR, 'TABLE_OF_CONTENTS.md')

    with open(toc_path, 'w', encoding='utf-8') as f:
        f.write("# Xray Documentation - Table of Contents\n\n")
        f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Total Pages: {len(page_metadata)}**\n\n")
        f.write("---\n\n")
        f.write("## 📋 All Pages (Alphabetical)\n\n")

        sorted_pages = sorted(page_metadata.items(), key=lambda x: x[1]['title'].lower())

        for url, meta in sorted_pages:
            title = meta['title'].replace(' - Xray Cloud Documentation - XRAY view', '').strip()
            f.write(f"- [{title}]({meta['filename']})\n")
            f.write(f"  - 🔗 {url}\n")

    print(f"✅ TOC updated: {len(page_metadata)} unique pages")

def main():
    print("="*70)
    print("Smart Duplicate Cleanup (By Page ID)")
    print("Keeps files with fuller URLs")
    print("="*70)

    duplicates = find_duplicates_by_id()

    if not duplicates:
        print("\n✅ No duplicates found!")
        return

    print(f"\n📊 Found {len(duplicates)} page IDs with multiple files\n")
    print("="*70)
    print("DRY RUN - Preview:")
    print("="*70)

    kept, to_remove = cleanup_duplicates(duplicates, dry_run=True)

    print("\n" + "="*70)
    print(f"Will keep {kept} pages, remove {to_remove} duplicates")
    print("="*70)

    response = input("\n⚠️  Proceed? (yes/no): ")

    if response.lower() != 'yes':
        print("❌ Cancelled")
        return

    print("\n🗑️  Removing duplicates...")
    kept, removed = cleanup_duplicates(duplicates, dry_run=False)

    print(f"\n✅ Removed {removed} duplicates")
    print(f"✅ Kept {kept} unique pages")

    regenerate_toc()

    print("\n" + "="*70)
    print("✅ CLEANUP COMPLETE!")
    print("="*70)

if __name__ == "__main__":
    main()
