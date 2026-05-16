#!/usr/bin/env python3
"""
Regenerate invalid thumbnail images for rose-blog.
Invalid files contain JSON (Pollinations.ai rate limit errors) instead of JPEG data.
"""

import os
import subprocess
import time
import urllib.parse
import sys

THUMBNAILS_DIR = "/home/scottishfoldbrothers/.openclaw/workspace/rose-blog/assets/img/thumbnails"
POSTS_DIR = "/home/scottishfoldbrothers/.openclaw/workspace/rose-blog/content/posts"

SKIP_SLUGS = {"2026-02-22-hello-world"}  # Already successful, exclude


def get_invalid_files():
    """Find all .jpg files that are NOT actual JPEG images."""
    result = subprocess.run(
        ["file"] + [f for f in os.listdir(THUMBNAILS_DIR) if f.endswith(".jpg")],
        capture_output=True, text=True, cwd=THUMBNAILS_DIR
    )
    invalid = []
    for line in result.stdout.splitlines():
        if "JPEG" not in line and "PNG" not in line and "GIF" not in line:
            filename = line.split(":")[0].strip()
            if filename.endswith(".jpg"):
                slug = filename[:-4]
                if slug not in SKIP_SLUGS:
                    invalid.append(slug)
    return sorted(invalid)


def is_jpeg(filepath):
    """Check if a file is actually a JPEG/PNG/GIF image."""
    result = subprocess.run(["file", filepath], capture_output=True, text=True)
    output = result.stdout
    return any(fmt in output for fmt in ["JPEG", "PNG", "GIF", "image data"])


def build_prompt(slug):
    """Generate an English image prompt from the slug."""
    # Remove date prefix (YYYY-MM-DD-)
    parts = slug.split("-")
    # First 3 parts are YYYY, MM, DD
    keyword_parts = parts[3:]
    slug_words = " ".join(keyword_parts)
    prompt = (
        f"professional finance investment blog thumbnail, {slug_words}, "
        f"stock market chart data visualization, modern clean design, "
        f"blue purple gradient background, financial technology"
    )
    return prompt


def download_image(slug, max_retries=3):
    """Download image from Pollinations.ai with retry logic."""
    prompt = build_prompt(slug)
    encoded_prompt = urllib.parse.quote(prompt)

    # Deterministic seed from slug
    seed = sum(ord(c) for c in slug) % 99999999

    output_file = os.path.join(THUMBNAILS_DIR, f"{slug}.jpg")
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1200&height=630&seed={seed}&nologo=true"

    print(f"\n[{slug}]")
    print(f"  Prompt: {prompt[:80]}...")
    print(f"  Seed: {seed}")

    for attempt in range(1, max_retries + 1):
        print(f"  Attempt {attempt}/{max_retries}: sleeping 5s...")
        time.sleep(5)

        try:
            result = subprocess.run(
                ["curl", "-sL", url, "-o", output_file, "--max-time", "90"],
                capture_output=True, text=True
            )

            if is_jpeg(output_file):
                size = os.path.getsize(output_file)
                print(f"  SUCCESS (size: {size:,} bytes)")
                return True
            else:
                with open(output_file, "r", errors="ignore") as f:
                    preview = f.read(100)
                print(f"  Got non-image data: {preview!r}")

                if attempt < max_retries:
                    print(f"  Waiting 10s before retry...")
                    time.sleep(10)

        except Exception as e:
            print(f"  Error on attempt {attempt}: {e}")
            if attempt < max_retries:
                time.sleep(10)

    print(f"  FAILED after {max_retries} attempts")
    return False


def main():
    print("=== rose-blog Thumbnail Regenerator ===")
    print(f"Thumbnails dir: {THUMBNAILS_DIR}")
    print(f"Posts dir: {POSTS_DIR}")
    print()

    invalid_slugs = get_invalid_files()
    total = len(invalid_slugs)
    print(f"Found {total} invalid thumbnail files to regenerate:")
    for s in invalid_slugs:
        print(f"  - {s}")
    print()

    if total == 0:
        print("Nothing to do!")
        return

    success_list = []
    failed_list = []

    for i, slug in enumerate(invalid_slugs, 1):
        print(f"\n[{i}/{total}] Processing: {slug}")
        if download_image(slug):
            success_list.append(slug)
        else:
            failed_list.append(slug)

    print("\n" + "="*50)
    print(f"COMPLETE: {len(success_list)} succeeded, {len(failed_list)} failed")

    if failed_list:
        print("\nFailed slugs:")
        for s in failed_list:
            print(f"  - {s}")
        sys.exit(1)


if __name__ == "__main__":
    main()
