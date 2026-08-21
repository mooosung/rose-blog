#!/usr/bin/env python3
"""
generate_thumbnails_v2.py
新方式: LoremFlickr写真 + タイトルオーバーレイ（下パネルなし）
Output: static/img/thumbnails/{slug}.jpg (1200x630)
"""

import os
import re
import sys
import time
import glob
import hashlib
import urllib.request
from io import BytesIO
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
except ImportError:
    print("ERROR: Pillow not installed. Run: pip install Pillow")
    sys.exit(1)

POSTS_DIR = Path(__file__).parent.parent / "content" / "posts"
OUTPUT_DIR = Path(__file__).parent.parent / "static" / "img" / "thumbnails"
FONT_BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_REGULAR = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"

# タグ → LoremFlickrキーワードマッピング
KEYWORD_MAP = [
    (["AI", "GPT", "LLM", "生成AI", "ChatGPT", "Claude", "人工知能", "機械学習"],
     "artificial-intelligence,technology,computer"),
    (["半導体", "chip", "NVIDIA", "AMD", "Intel", "シリコン", "パワー半導体", "HBM"],
     "semiconductor,chip,electronics"),
    (["データセンター", "datacenter", "server", "クラウド", "AWS", "Azure", "冷却"],
     "server,datacenter,technology"),
    (["ETF", "VOO", "QQQ", "VYM", "SCHD", "S&P500", "インデックス", "オルカン"],
     "stock-market,investment,finance"),
    (["NISA", "iDeCo", "積立", "節税"],
     "savings,investment,money"),
    (["米国株", "日本株", "株式", "配当", "dividend", "高配当"],
     "stock-exchange,wall-street,trading"),
    (["不動産", "REIT", "リート"],
     "real-estate,building,city"),
    (["金", "Gold", "ゴールド", "貴金属"],
     "gold,precious-metal"),
    (["債券", "bond", "国債", "TLT"],
     "finance,treasury,investment"),
    (["暗号資産", "ビットコイン", "Bitcoin", "仮想通貨"],
     "bitcoin,cryptocurrency,blockchain"),
    (["ESG", "サステナ", "sustainable", "クリーンエネルギー"],
     "green-energy,solar,sustainable"),
    (["ロボット", "自動化", "robotics"],
     "robot,automation,manufacturing"),
    (["ヘルスケア", "healthcare", "医療"],
     "healthcare,medical,hospital"),
    (["サイバーセキュリティ", "security", "cybersecurity"],
     "cybersecurity,network,technology"),
    (["量子", "quantum"],
     "quantum,technology,future"),
    (["バフェット", "Buffett", "バークシャー"],
     "investment,finance,business"),
    (["新興国", "emerging", "途上国"],
     "global,world,development"),
]

FALLBACK_KEYWORD = "finance,business,investment"


def get_loremflickr_keyword(slug: str, tags: list) -> str:
    combined = (slug + " " + " ".join(tags)).lower()
    for tag_list, keyword in KEYWORD_MAP:
        for t in tag_list:
            if t.lower() in combined:
                return keyword
    return FALLBACK_KEYWORD


def fetch_photo(keyword: str, slug: str) -> Image.Image | None:
    """Picsumから背景写真を取得（安全・高品質な風景・建物・自然写真）。"""
    # スラッグのハッシュでシード固定（同じ記事は毎回同じ画像）
    slug_hash = int(hashlib.md5(slug.encode()).hexdigest()[:8], 16) % 9999 + 1
    urls = [
        f"https://picsum.photos/seed/{slug_hash}/1200/630",
        f"https://picsum.photos/seed/{slug}/1200/630",
        f"https://picsum.photos/1200/630",
    ]
    for url in urls:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read()
            img = Image.open(BytesIO(data)).convert("RGB")
            img = img.resize((1200, 630), Image.LANCZOS)
            return img
        except Exception as e:
            print(f"    fetch failed ({url[:50]}...): {e}")
            time.sleep(1)
    return None


def wrap_text(text: str, font, max_width: int, draw: ImageDraw.ImageDraw) -> list[str]:
    """文字列を max_width に収まるよう折り返す。
    - ASCII連続文字（英数字）を途中で分割しない
    - 行頭禁則文字（・、。：；）を次行先頭に置かない
    """
    # 行頭禁則文字
    LINE_HEAD_FORBIDDEN = set('・、。：；…）】」』')

    lines = []
    current_line = ""

    i = 0
    chars = list(text)
    while i < len(chars):
        ch = chars[i]
        # ASCII連続部分はまとめて1トークンとして扱う
        if ch.isascii() and (ch.isalnum() or ch in '&+#/-_'):
            token = ch
            j = i + 1
            while j < len(chars) and chars[j].isascii() and (chars[j].isalnum() or chars[j] in '&+#/-_.'):
                token += chars[j]
                j += 1
            # トークンが収まるか確認
            test = current_line + token
            bbox = draw.textbbox((0, 0), test, font=font)
            if bbox[2] - bbox[0] <= max_width:
                current_line = test
            else:
                if current_line:
                    lines.append(current_line)
                current_line = token
            i = j
        else:
            test = current_line + ch
            bbox = draw.textbbox((0, 0), test, font=font)
            if bbox[2] - bbox[0] <= max_width:
                current_line = test
                i += 1
            else:
                # 行頭禁則チェック: 次の文字が禁則文字なら現在行に含める
                if ch in LINE_HEAD_FORBIDDEN and current_line:
                    # 禁則文字を現在行に強制追加して改行
                    current_line += ch
                    lines.append(current_line)
                    current_line = ""
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = ch
                i += 1

    if current_line:
        lines.append(current_line)
    return lines


def clean_title(title: str) -> str:
    # 絵文字除去・クォート除去
    # 記号は意味を持つものを必ず残すこと。半角の . % , + × / ~ $ # を落とすと
    # 「0.1%」→「01」、「61,500円」→「61500円」のように意味が変わる（2026-08-21 修正）
    title = re.sub(r'[\U00010000-\U0010ffff]', '', title)
    title = re.sub(r'[^\w\s\u3000-\u9fff\u4e00-\u9fff\uff00-\uffef\u3040-\u309f\u30a0-\u30ff\-：:！!？?（）()【】「」・、。…|｜&.%,+×/~$#]', '', title)
    return re.sub(r'\s+', ' ', title).strip().strip('"\'')


def generate_thumbnail(slug: str, title: str, tags: list, output_path: Path, force: bool = False):
    if output_path.exists() and not force:
        return False  # skip

    W, H = 1200, 630
    keyword = get_loremflickr_keyword(slug, tags)

    # 背景写真を取得
    img = fetch_photo(keyword, slug)
    if img is None:
        # フォールバック: 暗いグラデーション
        img = Image.new("RGB", (W, H), (20, 30, 60))

    img = img.convert("RGBA")

    # ── 全面オーバーレイ（写真を暗くして文字を読みやすく）──
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 110))
    img.paste(overlay, (0, 0), overlay)

    img = img.convert("RGB")
    draw = ImageDraw.Draw(img)

    # ── サイトロゴ（左上）──
    try:
        font_site = ImageFont.truetype(FONT_REGULAR, 24)
    except Exception:
        font_site = ImageFont.load_default()
    draw.text((60, 44), "rozenmaier.com", font=font_site, fill=(255, 255, 255))

    # ── タイトル（画像中央オーバーレイ）──
    clean = clean_title(title)
    MARGIN = 130  # 左右マージン（各130px）
    max_text_width = W - MARGIN * 2  # 940px

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
        total_h = len(lines) * line_height

        # 画像中央エリア（上下各120px余白内）に収まるか
        if total_h <= H - 240 and len(lines) <= 4:
            best_lines = lines
            best_font = font_main
            best_font_size = font_size
            break

    if best_lines is None:
        try:
            best_font = ImageFont.truetype(FONT_BOLD, 30)
        except Exception:
            best_font = ImageFont.load_default()
        best_lines = wrap_text(clean, best_font, max_text_width, draw)[:4]
        best_font_size = 30

    line_height = best_font_size + 16
    total_h = len(best_lines) * line_height
    # 画像全体で垂直中央揃え（ロゴ分を少し下にオフセット）
    start_y = (H - total_h) // 2 + 20

    for line in best_lines:
        bbox = draw.textbbox((0, 0), line, font=best_font)
        text_w = bbox[2] - bbox[0]
        x = (W - text_w) // 2

        # 影（3px オフセット）
        draw.text((x + 3, start_y + 3), line, font=best_font, fill=(0, 0, 0))
        # 本文
        draw.text((x, start_y), line, font=best_font, fill=(255, 255, 255))
        start_y += line_height

    # 保存
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(output_path), "JPEG", quality=88, optimize=True)
    return True


def parse_frontmatter(content: str) -> dict:
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
            m_arr = re.match(r'^tags:\s*\[(.+)\]', line)
            if m_arr:
                result['tags'] = [t.strip().strip('"\'') for t in m_arr.group(1).split(',')]
                continue
            m = re.match(r'^(\w+):\s*(.+)$', line)
            if m:
                result[m.group(1)] = m.group(2).strip().strip('"\'')
    return result


SKIP_SLUGS = {
    "2026-02-22-hello-world",  # ローゼのご挨拶（キャラ画像を維持）
}


def main():
    force = "--force" in sys.argv or "-f" in sys.argv
    posts = sorted(POSTS_DIR.glob("2026-*.md"))
    print(f"対象: {len(posts)} 記事 (force={force})")

    generated = 0
    skipped = 0
    errors = 0

    for post_path in posts:
        slug = post_path.stem
        content = post_path.read_text(encoding='utf-8')
        fm = parse_frontmatter(content)

        title = fm.get('title', slug)
        tags = fm.get('tags', [])
        if isinstance(tags, str):
            tags = [tags]

        output_path = OUTPUT_DIR / f"{slug}.jpg"

        if slug in SKIP_SLUGS:
            skipped += 1
            continue

        if output_path.exists() and not force:
            skipped += 1
            continue

        print(f"  生成中: {slug[:60]}")
        try:
            ok = generate_thumbnail(slug, title, tags, output_path, force=force)
            if ok:
                generated += 1
            else:
                skipped += 1
            time.sleep(0.3)  # LoremFlickrへの負荷軽減
        except Exception as e:
            print(f"  ERROR {slug}: {e}")
            errors += 1

    print(f"\n完了! 生成: {generated} / スキップ: {skipped} / エラー: {errors}")
    print(f"出力先: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
