#!/usr/bin/env python3
"""
Find and remove duplicate documentation files.
Keeps ID-based filenames (e.g., 44566476.md) and removes title-based ones (e.g., About_Xray.md)
"""

import os
import re
import json
from collections import defaultdict

OUTPUT_DIR = "/Users/ashish/Jira/xray_documentation"
INDEX_FILE = os.path.join(OUTPUT_DIR, "INDEX.json")
TOC_FILE = os.path.join(OUTPUT_DIR, "TABLE_OF_CONTENTS.md")

def extract_url_from_file(filepath):
    """Extract the Source URL from a markdown file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        url_match = re.search(r'^Source:\s+(.+)$', content, re.MULTILINE)
        if url_match:
            return url_match.group(1).strip()
    except:
        pass
    return None

def is_id_based_filename(filename):
    """Check if filename is ID-based (e.g., 44566476.md)"""
    name = filename.replace('.md', '')
    return name.isdigit() and len(name) >= 6

def find_duplicates():
    """Find all duplicate files (same URL, different filename)"""
    url_to_files = defaultdict(list)

    print("🔍 Scanning for duplicates...")

    for filename in os.listdir(OUTPUT_DIR):
        if not filename.endswith('.md') or filename in ['TABLE_OF_CONTENTS.md', 'INDEX.md']:
            continue

        filepath = os.path.join(OUTPUT_DIR, filename)
        url = extract_url_from_file(filepath)

        if url:
            url_to_files[url].append(filename)

    # Find URLs with multiple files
    duplicates = {url: files for url, files in url_to_files.items() if len(files) > 1}

    return duplicates

def cleanup_duplicates(duplicates, dry_run=True):
    """Remove duplicate files, keeping ID-based ones"""
    removed_count = 0
    kept_count = 0

    for url, files in duplicates.items():
        # Sort: ID-based files first
        files.sort(key=lambda f: (not is_id_based_filename(f), f))

        # Keep the first (ID-based) file
        keep_file = files[0]
        remove_files = files[1:]

        print(f"\n📄 {url}")
        print(f"  ✅ KEEP: {keep_file}")

        for remove_file in remove_files:
            print(f"  ❌ REMOVE: {remove_file}")

            if not dry_run:
                filepath = os.path.join(OUTPUT_DIR, remove_file)
                os.remove(filepath)
                removed_count += 1

        kept_count += 1

    return kept_count, removed_count

def regenerate_index():
    """Regenerate index and TOC after cleanup"""
    print("\n📚 Regenerating index...")

    page_metadata = {}
    visited_urls = set()

    for filename in os.listdir(OUTPUT_DIR):
        if not filename.endswith('.md') or filename in ['TABLE_OF_CONTENTS.md', 'INDEX.md']:
            continue

        filepath = os.path.join(OUTPUT_DIR, filename)

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract title
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            title = title_match.group(1).strip() if title_match else filename

            # Extract URL
            url_match = re.search(r'^Source:\s+(.+)$', content, re.MULTILINE)
            if url_match:
                url = url_match.group(1).strip()

                page_metadata[url] = {
                    'title': title,
                    'filename': filename,
                    'depth': 0,
                    'parent': None
                }
                visited_urls.add(url)
        except:
            pass

    # Save index
    import time
    data = {
        'visited_urls': list(visited_urls),
        'page_metadata': page_metadata,
        'last_updated': time.strftime('%Y-%m-%d %H:%M:%S')
    }

    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    # Generate TOC
    with open(TOC_FILE, 'w', encoding='utf-8') as f:
        f.write("# Xray Documentation - Table of Contents\n\n")
        f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Total Pages: {len(page_metadata)}**\n\n")
        f.write("---\n\n")
        f.write("## 📋 All Pages (Alphabetical)\n\n")

        sorted_pages = sorted(page_metadata.items(), key=lambda x: x[1]['title'].lower())

        for url, meta in sorted_pages:
            title = meta['title'].replace(' - Xray Cloud Documentation - XRAY view', '')
            f.write(f"- [{title}]({meta['filename']})\n")
            f.write(f"  - 🔗 {url}\n")

    print(f"✅ Index updated: {len(page_metadata)} pages")
    print(f"✅ TOC regenerated: {TOC_FILE}")

def main():
    print("="*70)
    print("Duplicate Files Cleanup")
    print("="*70)

    # Find duplicates
    duplicates = find_duplicates()

    if not duplicates:
        print("\n✅ No duplicates found!")
        return

    print(f"\n📊 Found {len(duplicates)} URLs with duplicate files\n")

    # Show what will be removed (dry run)
    print("="*70)
    print("DRY RUN - Showing what will be removed:")
    print("="*70)
    kept, removed = cleanup_duplicates(duplicates, dry_run=True)

    print("\n" + "="*70)
    print(f"Summary: {kept} pages to keep, {removed} duplicates to remove")
    print("="*70)

    # Ask for confirmation
    response = input("\n⚠️  Proceed with deletion? (yes/no): ")

    if response.lower() != 'yes':
        print("❌ Cancelled")
        return

    # Actually remove files
    print("\n🗑️  Removing duplicates...")
    kept, removed = cleanup_duplicates(duplicates, dry_run=False)

    print(f"\n✅ Removed {removed} duplicate files")
    print(f"✅ Kept {kept} unique pages")

    # Regenerate index
    regenerate_index()

    print("\n" + "="*70)
    print("✅ CLEANUP COMPLETE!")
    print("="*70)
    print(f"📁 Directory: {OUTPUT_DIR}")
    print(f"📚 TOC: {TOC_FILE}")
    print("="*70)

if __name__ == "__main__":
    main()
