#!/usr/bin/env python3
"""
generate_body_images.py
rose-blog記事の本文中に挿入する画像をOpenAI API (gpt-image-2) で生成する。
2026-07-28: 「新規記事から画像入れて」（御主人様2指示）に基づき、
featureimage（アイキャッチ）とは別に、本文中に1〜2枚の挿絵を入れるための画像を生成する。

タイトルオーバーレイなし・純粋なイラストのみ（本文に馴染ませるため）。
サムネイル生成(generate_thumbnails_v3.py)と同じくrose_reference.pngを使い、
ローゼの顔・衣装の一貫性を保つ。

Usage:
    python3 scripts/generate_body_images.py --slug 2026-07-28-foo-slug
    python3 scripts/generate_body_images.py --slug ... --count 1
    python3 scripts/generate_body_images.py --slug ... --scene1 "..." --scene2 "..."

Output: static/img/body/{slug}-1.jpg, static/img/body/{slug}-2.jpg (1200x630)
挿入用のMarkdown画像タグを標準出力に表示する。
"""
import argparse
import base64
import hashlib
import sys
import time
from io import BytesIO
from pathlib import Path

import requests
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from generate_thumbnails_v2 import POSTS_DIR, parse_frontmatter  # noqa: E402

OUTPUT_DIR = Path(__file__).parent.parent / "static" / "img" / "body"
KEY_FILE = Path.home() / ".openclaw/secrets/openai_api_key"
REFERENCE = Path.home() / ".openclaw/workspace/images/rose_reference.png"
MODEL = "gpt-image-2"
W, H = 1200, 630

EXPRESSION_POOL = [
    "beaming with pride — wide bright smile, sparkling eyes, triumphant pose",
    "sharp tsundere smirk — one eyebrow raised, arms crossed, confident half-lidded eyes",
    "wide-eyed shock — mouth slightly open, eyebrows raised high, genuinely surprised",
    "passionate lecture — index finger raised, leaning forward, intense focused eyes",
    "deep thoughtful concern — furrowed brows, hand on chin, contemplative frown",
    "mischievous grin — sharp eyes, cat-like smile, playful troublemaker energy",
    "tsundere blush — cheeks flushed red, eyes averted, pouting lips",
    "cold analytical stare — expressionless face, sharp calculating eyes, ice-queen composure",
    "bright excited cheer — both fists raised, open joyful smile, eyes crinkled",
    "determined resolve — eyes narrowed with conviction, jaw set, purposeful expression",
]


def pick_expression(slug: str, idx: int) -> str:
    key = f"{slug}-{idx}"
    h = int(hashlib.sha256(key.encode()).hexdigest(), 16)
    return EXPRESSION_POOL[h % len(EXPRESSION_POOL)]


def build_prompt(title: str, tags: list, scene: str | None, expression: str) -> str:
    p = (
        "The attached image is the character reference for Rose, an elegant "
        "tsundere young-lady maid character with long curly blonde hair. Keep "
        "her face, hair and outfit fully consistent with the reference. "
        "Create a wide landscape illustration to be embedded inside the body "
        "of a Japanese blog article. "
        f"Article theme: {title}"
        + (f" (tags: {', '.join(tags)})" if tags else "") + ". "
    )
    if scene:
        p += f"Scene direction: {scene}. "
    p += (
        f"Feature Rose naturally integrated into the theme's world and "
        f"setting (not floating or pasted on), with this expression and pose: "
        f"[{expression}]. "
        "Atmospheric, well-lit illustration suitable as an in-article image. "
        "ABSOLUTELY NO text, letters, numbers, words, signs or typography "
        "anywhere in the image. Do not depict any real company logos or "
        "trademarks. Pure illustration only."
    )
    return p


def generate_one(api_key: str, prompt: str, out_path: Path) -> bool:
    t0 = time.time()
    for attempt in range(2):
        try:
            with open(REFERENCE, "rb") as f:
                resp = requests.post(
                    "https://api.openai.com/v1/images/edits",
                    headers={"Authorization": f"Bearer {api_key}"},
                    data={"model": MODEL, "prompt": prompt,
                          "size": "1536x1024", "quality": "medium"},
                    files={"image": (REFERENCE.name, f, "image/png")},
                    timeout=300,
                )
            if resp.status_code >= 500:
                time.sleep(10)
                continue
            if resp.status_code != 200:
                print(f"API error HTTP {resp.status_code}: {resp.text[:200]}")
                return False
            raw = base64.b64decode(resp.json()["data"][0]["b64_json"])
            img = Image.open(BytesIO(raw)).convert("RGB")
            target_ratio = W / H
            w, h = img.size
            crop_h = int(w / target_ratio)
            top = (h - crop_h) // 2
            img = img.crop((0, top, w, top + crop_h)).resize((W, H), Image.LANCZOS)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            img.save(str(out_path), "JPEG", quality=88, optimize=True)
            print(f"OK: {out_path} ({out_path.stat().st_size:,} bytes, "
                  f"{time.time()-t0:.0f}s)")
            return True
        except requests.RequestException as e:
            print(f"failed (attempt {attempt+1}): {e}")
            time.sleep(10)
    return False


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True, help="記事slug（content/posts/{slug}.md）")
    ap.add_argument("--count", type=int, default=2, choices=[1, 2],
                    help="生成する本文画像の枚数（デフォルト2）")
    ap.add_argument("--scene1", default=None, help="1枚目の情景ヒント（英語1文、任意）")
    ap.add_argument("--scene2", default=None, help="2枚目の情景ヒント（英語1文、任意）")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    if not REFERENCE.exists():
        raise SystemExit(f"ERROR: 参照画像がありません: {REFERENCE}")
    api_key = KEY_FILE.read_text().strip()

    post_path = POSTS_DIR / f"{args.slug}.md"
    if not post_path.exists():
        raise SystemExit(f"ERROR: 記事がありません: {post_path}")
    fm = parse_frontmatter(post_path.read_text(encoding="utf-8"))
    title = fm.get("title", args.slug)
    tags = fm.get("tags", [])
    if isinstance(tags, str):
        tags = [tags]

    scenes = [args.scene1, args.scene2]
    snippets = []
    for i in range(1, args.count + 1):
        out_path = OUTPUT_DIR / f"{args.slug}-{i}.jpg"
        if out_path.exists() and not args.force:
            print(f"skip（既存）: {out_path}")
        else:
            expression = pick_expression(args.slug, i)
            print(f"[{i}] Expression: {expression}")
            prompt = build_prompt(title, tags, scenes[i - 1], expression)
            ok = generate_one(api_key, prompt, out_path)
            if not ok:
                raise SystemExit(f"ERROR: 画像{i}枚目の生成に失敗しました")
        snippets.append(f'![{title}](/img/body/{args.slug}-{i}.jpg)')

    print("\n--- 本文に挿入するMarkdown（各H2セクションの下に1つずつ配置） ---")
    for s in snippets:
        print(s)


if __name__ == "__main__":
    main()
