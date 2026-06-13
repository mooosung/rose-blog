#!/usr/bin/env python3
"""
generate_thumbnails_v3.py
新方式 (2026-06-13): OpenAI API (gpt-image-2) でテーマに合ったベース画像を生成し、
v2と同じタイトルオーバーレイを重ねる。
API失敗時は v2 の写真取得（picsum）へ自動フォールバックするので画像なし事故は起きない。

Usage:
    python3 scripts/generate_thumbnails_v3.py --slug 2026-06-14-foo
    python3 scripts/generate_thumbnails_v3.py --slug ... --rose            # ローゼを控えめに登場させる
    python3 scripts/generate_thumbnails_v3.py --slug ... --scene "..."    # 情景ヒント（英語1文）
    python3 scripts/generate_thumbnails_v3.py --slug ... --out /tmp/x.jpg # テスト用出力先
Output: static/img/thumbnails/{slug}.jpg (1200x630)
"""

import argparse
import base64
import sys
import time
from io import BytesIO
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
from generate_thumbnails_v2 import (  # noqa: E402
    FONT_BOLD, FONT_REGULAR, OUTPUT_DIR, POSTS_DIR,
    clean_title, fetch_photo, get_loremflickr_keyword, parse_frontmatter,
    wrap_text,
)

KEY_FILE = Path.home() / ".openclaw/secrets/openai_api_key"
REFERENCE = Path.home() / ".openclaw/workspace/images/rose_reference.png"
MODEL = "gpt-image-2"
W, H = 1200, 630


def build_prompt(title: str, tags: list, scene: str | None, rose: bool) -> str:
    p = (
        "Wide landscape blog header background illustration. "
        f"Theme: {title}"
        + (f" (tags: {', '.join(tags)})" if tags else "") + ". "
    )
    if scene:
        p += f"Scene direction: {scene}. "
    if rose:
        # noteのアイキャッチよりさらに控えめ: 主題はあくまでテーマ、ローゼは脇役の点景
        p += (
            "The attached image is the character reference for Rose. "
            "Rose may appear only as a very small, subtle background accent "
            "in a corner — far less prominent than the theme itself; "
            "she must not draw attention away from the subject. "
            "Keep her appearance consistent with the reference. "
        )
    p += (
        "Atmospheric and slightly dark-toned, suitable as a background that "
        "will have white title text overlaid on it. "
        "ABSOLUTELY NO text, letters, numbers, words, signs or typography "
        "anywhere in the image. Do not depict any real company logos or "
        "trademarks. Pure illustration only."
    )
    return p


def generate_base_via_api(title: str, tags: list, scene: str | None,
                          rose: bool) -> Image.Image | None:
    """gpt-image-2でベース画像を生成。失敗したらNone（呼び出し側でフォールバック）。"""
    try:
        api_key = KEY_FILE.read_text().strip()
        prompt = build_prompt(title, tags, scene, rose)
        headers = {"Authorization": f"Bearer {api_key}"}
        if rose and REFERENCE.exists():
            with open(REFERENCE, "rb") as f:
                resp = requests.post(
                    "https://api.openai.com/v1/images/edits",
                    headers=headers,
                    data={"model": MODEL, "prompt": prompt,
                          "size": "1536x1024", "quality": "medium"},
                    files={"image": (REFERENCE.name, f, "image/png")},
                    timeout=300,
                )
        else:
            resp = requests.post(
                "https://api.openai.com/v1/images/generations",
                headers=headers,
                json={"model": MODEL, "prompt": prompt,
                      "size": "1536x1024", "quality": "medium"},
                timeout=300,
            )
        if resp.status_code != 200:
            print(f"    API error HTTP {resp.status_code}: {resp.text[:200]}")
            return None
        raw = base64.b64decode(resp.json()["data"][0]["b64_json"])
        img = Image.open(BytesIO(raw)).convert("RGB")
        # 1536x1024 → 中央クロップで1200x630（アスペクト比 1.5 → 1.905）
        target_ratio = W / H
        w, h = img.size
        crop_h = int(w / target_ratio)
        top = (h - crop_h) // 2
        img = img.crop((0, top, w, top + crop_h)).resize((W, H), Image.LANCZOS)
        tokens = resp.json().get("usage", {}).get("total_tokens", "?")
        print(f"    API生成OK (tokens={tokens}, rose={rose})")
        return img
    except Exception as e:
        print(f"    API生成失敗: {e}")
        return None


def overlay_title(img: Image.Image, title: str) -> Image.Image:
    """v2と同一のタイトルオーバーレイ（暗幕＋ロゴ＋中央タイトル）。"""
    img = img.convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 110))
    img.paste(overlay, (0, 0), overlay)
    img = img.convert("RGB")
    draw = ImageDraw.Draw(img)

    try:
        font_site = ImageFont.truetype(FONT_REGULAR, 24)
    except Exception:
        font_site = ImageFont.load_default()
    draw.text((60, 44), "rozenmaier.com", font=font_site, fill=(255, 255, 255))

    clean = clean_title(title)
    max_text_width = W - 130 * 2

    best_lines = None
    best_font = None
    best_font_size = 28
    for font_size in [60, 54, 48, 44, 38, 34, 30]:
        try:
            font_main = ImageFont.truetype(FONT_BOLD, font_size)
        except Exception:
            font_main = ImageFont.load_default()
        lines = wrap_text(clean, font_main, max_text_width, draw)
        line_height = font_size + 16
        if len(lines) * line_height <= H - 240 and len(lines) <= 4:
            best_lines, best_font, best_font_size = lines, font_main, font_size
            break
    if best_lines is None:
        try:
            best_font = ImageFont.truetype(FONT_BOLD, 30)
        except Exception:
            best_font = ImageFont.load_default()
        best_lines = wrap_text(clean, best_font, max_text_width, draw)[:4]
        best_font_size = 30

    line_height = best_font_size + 16
    start_y = (H - len(best_lines) * line_height) // 2 + 20
    for line in best_lines:
        bbox = draw.textbbox((0, 0), line, font=best_font)
        x = (W - (bbox[2] - bbox[0])) // 2
        draw.text((x + 3, start_y + 3), line, font=best_font, fill=(0, 0, 0))
        draw.text((x, start_y), line, font=best_font, fill=(255, 255, 255))
        start_y += line_height
    return img


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True, help="記事slug（content/posts/{slug}.md）")
    ap.add_argument("--rose", action="store_true",
                    help="ローゼを控えめに登場させる（記事の雰囲気で判断）")
    ap.add_argument("--scene", default=None, help="情景ヒント（英語1文、任意）")
    ap.add_argument("--out", default=None, help="出力先の上書き（テスト用）")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    post_path = POSTS_DIR / f"{args.slug}.md"
    if not post_path.exists():
        raise SystemExit(f"ERROR: 記事がありません: {post_path}")
    fm = parse_frontmatter(post_path.read_text(encoding="utf-8"))
    title = fm.get("title", args.slug)
    tags = fm.get("tags", [])
    if isinstance(tags, str):
        tags = [tags]

    output_path = Path(args.out) if args.out else OUTPUT_DIR / f"{args.slug}.jpg"
    if output_path.exists() and not args.force and not args.out:
        print(f"skip（既存）: {output_path}")
        return

    t0 = time.time()
    img = generate_base_via_api(title, tags, args.scene, args.rose)
    if img is None:
        # フォールバック: v2の写真取得（画像なし事故を防ぐ）
        print("    → v2方式（写真）にフォールバック")
        img = fetch_photo(get_loremflickr_keyword(args.slug, tags), args.slug)
        if img is None:
            img = Image.new("RGB", (W, H), (20, 30, 60))

    img = overlay_title(img, title)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(output_path), "JPEG", quality=88, optimize=True)
    print(f"OK: {output_path} ({output_path.stat().st_size:,} bytes, "
          f"{time.time()-t0:.0f}s)")


if __name__ == "__main__":
    main()
