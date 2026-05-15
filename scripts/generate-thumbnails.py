#!/usr/bin/env python3
"""
Generate unique thumbnail images for each blog post.
Output: static/img/thumbnails/{slug}.jpg (1200x630)
"""

import os
import re
import glob
import hashlib
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
except ImportError:
    print("ERROR: Pillow not installed. Run: pip install Pillow")
    exit(1)

POSTS_DIR = Path(__file__).parent.parent / "content" / "posts"
OUTPUT_DIR = Path(__file__).parent.parent / "static" / "img" / "thumbnails"
FONT_BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_REGULAR = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"

# Category color themes (gradient: start → end)
THEMES = {
    "ai":         [(15, 32, 78),   (32, 120, 200)],   # deep blue
    "semi":       [(10, 60, 30),   (20, 160, 80)],    # deep green
    "stock":      [(80, 20, 10),   (200, 80, 20)],    # deep orange
    "etf":        [(50, 15, 80),   (150, 50, 200)],   # purple
    "reit":       [(10, 60, 60),   (20, 160, 160)],   # teal
    "crypto":     [(80, 60, 5),    (200, 160, 10)],   # gold
    "nisa":       [(20, 50, 80),   (60, 130, 200)],   # light blue
    "default":    [(25, 25, 60),   (70, 70, 150)],    # navy
}

# Keywords to theme mapping
KEYWORD_MAP = {
    "ai": ["ai", "gpt", "openai", "nvidia", "llm", "chatgpt", "claude", "機械学習", "人工知能"],
    "semi": ["semiconductor", "silicon", "mlcc", "hbm", "chip", "半導体", "シリコン", "パワー半導体"],
    "stock": ["stock", "株", "銘柄", "日経", "nikkei", "crowdstrike", "palantir", "crwd", "pltr"],
    "etf": ["etf", "voo", "qqq", "vym", "schd", "sp500", "s&p", "オルカン", "インデックス"],
    "reit": ["reit", "不動産", "real estate"],
    "crypto": ["bitcoin", "btc", "crypto", "暗号資産", "仮想通貨"],
    "nisa": ["nisa", "ideco", "idc", "積立", "配当", "dividend"],
    "ai": ["datacenter", "data center", "データセンター", "冷却", "電力", "電線", "変圧器"],
}


def get_theme(slug: str, tags: list) -> list:
    """Determine color theme based on slug and tags."""
    combined = (slug + " " + " ".join(tags)).lower()
    for theme_name, keywords in KEYWORD_MAP.items():
        for kw in keywords:
            if kw in combined:
                return THEMES[theme_name]
    return THEMES["default"]


def make_gradient(size, color1, color2):
    """Create a vertical gradient background."""
    w, h = size
    img = Image.new("RGB", (w, h))
    for y in range(h):
        ratio = y / h
        r = int(color1[0] + (color2[0] - color1[0]) * ratio)
        g = int(color1[1] + (color2[1] - color1[1]) * ratio)
        b = int(color1[2] + (color2[2] - color1[2]) * ratio)
        for x in range(w):
            img.putpixel((x, y), (r, g, b))
    return img


def add_noise(img, intensity=8):
    """Add subtle noise for texture."""
    import random
    pixels = img.load()
    w, h = img.size
    for _ in range(w * h // 8):
        x = random.randint(0, w - 1)
        y = random.randint(0, h - 1)
        r, g, b = pixels[x, y]
        d = random.randint(-intensity, intensity)
        pixels[x, y] = (
            max(0, min(255, r + d)),
            max(0, min(255, g + d)),
            max(0, min(255, b + d)),
        )
    return img


def draw_grid_pattern(draw, size, color):
    """Draw subtle grid lines for visual interest."""
    w, h = size
    for x in range(0, w, 60):
        draw.line([(x, 0), (x, h)], fill=color, width=1)
    for y in range(0, h, 60):
        draw.line([(0, y), (w, y)], fill=color, width=1)


def wrap_text(text, font, max_width, draw):
    """Wrap text to fit within max_width."""
    lines = []
    # Split by natural break points (。、space)
    words = list(text)
    current_line = ""

    for char in words:
        test_line = current_line + char
        bbox = draw.textbbox((0, 0), test_line, font=font)
        w = bbox[2] - bbox[0]
        if w <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = char

    if current_line:
        lines.append(current_line)

    return lines


def clean_title(title: str) -> str:
    """Remove emojis and clean title for image display."""
    # Remove emoji characters
    title = re.sub(r'[\U00010000-\U0010ffff]', '', title)
    # Remove 🌹 and similar
    title = re.sub(r'[^\w\s\u3000-\u9fff\u4e00-\u9fff\uff00-\uffef\u3040-\u309f\u30a0-\u30ff\-：:！!？?（）()【】「」・、。…]', '', title)
    # Clean up whitespace
    title = re.sub(r'\s+', ' ', title).strip()
    # Remove leading/trailing quotes
    title = title.strip('"\'')
    return title


def generate_thumbnail(slug: str, title: str, tags: list, output_path: Path):
    """Generate a 1200x630 thumbnail for a blog post."""
    W, H = 1200, 630

    theme = get_theme(slug, tags)
    img = make_gradient((W, H), theme[0], theme[1])
    img = add_noise(img)

    draw = ImageDraw.Draw(img)

    # Grid pattern (subtle)
    grid_color = tuple(min(255, c + 20) for c in theme[1]) + (30,)
    img_rgba = img.convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_overlay = ImageDraw.Draw(overlay)
    for x in range(0, W, 60):
        draw_overlay.line([(x, 0), (x, H)], fill=(255, 255, 255, 15), width=1)
    for y in range(0, H, 60):
        draw_overlay.line([(0, y), (W, y)], fill=(255, 255, 255, 15), width=1)
    img = Image.alpha_composite(img_rgba, overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Site name watermark (top-left)
    try:
        font_site = ImageFont.truetype(FONT_BOLD, 24)
    except:
        font_site = ImageFont.load_default()
    draw.text((60, 50), "rozenmaier.com", font=font_site, fill=(255, 255, 255, 180))

    # Bottom decorative bar
    draw.rectangle([(0, H - 8), (W, H)], fill=(255, 255, 255, 60))

    # Main title
    clean = clean_title(title)

    # Try different font sizes to fit
    for font_size in [52, 44, 38, 32, 28]:
        try:
            font_main = ImageFont.truetype(FONT_BOLD, font_size)
        except:
            font_main = ImageFont.load_default()

        lines = wrap_text(clean, font_main, W - 120, draw)

        # Check if it fits within reasonable height
        line_height = font_size + 16
        total_height = len(lines) * line_height
        if total_height <= 300 and len(lines) <= 5:
            break

    # Center text vertically
    start_y = (H - total_height) // 2 - 20

    # Draw text shadow
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font_main)
        text_w = bbox[2] - bbox[0]
        x = (W - text_w) // 2
        y = start_y
        draw.text((x + 3, y + 3), line, font=font_main, fill=(0, 0, 0, 100))
        start_y += line_height

    # Draw actual text
    start_y = (H - total_height) // 2 - 20
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font_main)
        text_w = bbox[2] - bbox[0]
        x = (W - text_w) // 2
        draw.text((x, start_y), line, font=font_main, fill=(255, 255, 255))
        start_y += line_height

    # Investment/category tag (bottom center)
    try:
        font_tag = ImageFont.truetype(FONT_REGULAR, 22)
    except:
        font_tag = ImageFont.load_default()

    tag_display = " · ".join(tags[:3]) if tags else "投資"
    bbox = draw.textbbox((0, 0), tag_display, font=font_tag)
    tag_w = bbox[2] - bbox[0]
    draw.text(((W - tag_w) // 2, H - 60), tag_display, font=font_tag, fill=(220, 220, 220))

    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(output_path), "JPEG", quality=85, optimize=True)


def parse_frontmatter(content: str) -> dict:
    """Extract frontmatter values."""
    result = {}
    in_fm = False
    for line in content.split('\n'):
        if line.strip() == '---':
            if not in_fm:
                in_fm = True
                continue
            else:
                break
        if in_fm:
            m = re.match(r'^(\w+):\s*(.+)$', line)
            if m:
                key, val = m.group(1), m.group(2).strip().strip('"\'')
                result[key] = val
            # Parse tags array
            m_arr = re.match(r'^tags:\s*\[(.+)\]', line)
            if m_arr:
                tags_raw = m_arr.group(1)
                result['tags'] = [t.strip().strip('"\'') for t in tags_raw.split(',')]
    return result


def main():
    posts = sorted(POSTS_DIR.glob("*.md"))
    print(f"Processing {len(posts)} posts...")

    generated = 0
    skipped = 0

    for post_path in posts:
        slug = post_path.stem
        content = post_path.read_text(encoding='utf-8')
        fm = parse_frontmatter(content)

        title = fm.get('title', slug)
        tags = fm.get('tags', [])
        if isinstance(tags, str):
            tags = [tags]

        output_path = OUTPUT_DIR / f"{slug}.jpg"

        if output_path.exists():
            skipped += 1
            continue

        print(f"  Generating: {slug}")
        try:
            generate_thumbnail(slug, title, tags, output_path)
            generated += 1
        except Exception as e:
            print(f"  ERROR {slug}: {e}")

    print(f"\nDone! Generated: {generated}, Skipped (exists): {skipped}")
    print(f"Output: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
