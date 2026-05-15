#!/usr/bin/env python3
"""Pollinations.aiで全記事のアイキャッチ画像を生成・ダウンロード"""

import os
import re
import subprocess
import hashlib
import time
import urllib.parse
import sys

POSTS_DIR = "/home/scottishfoldbrothers/.openclaw/workspace/rose-blog/content/posts"
THUMBNAILS_DIR = "/home/scottishfoldbrothers/.openclaw/workspace/rose-blog/assets/img/thumbnails"

# タグ→英語プロンプトのマッピング
TAG_PROMPTS: dict[str, str] = {
    "日本株": "japanese stock market trading chart, financial investment, professional finance photo, blue tones",
    "株": "japanese stock market trading chart, financial investment, professional finance photo, blue tones",
    "株式投資": "japanese stock market trading chart, financial investment, professional finance photo, blue tones",
    "投資": "wealth management investment portfolio, financial planning, money growth",
    "AI": "artificial intelligence semiconductor chip, technology circuit board, futuristic digital",
    "人工知能": "artificial intelligence semiconductor chip, technology circuit board, futuristic digital",
    "半導体": "artificial intelligence semiconductor chip, technology circuit board, futuristic digital",
    "GPU": "artificial intelligence semiconductor chip, technology circuit board, futuristic digital",
    "ETF": "ETF index fund investment, diversified portfolio, financial growth chart",
    "インデックス": "ETF index fund investment, diversified portfolio, financial growth chart",
    "インデックス投資": "ETF index fund investment, diversified portfolio, financial growth chart",
    "REIT": "real estate investment trust, modern office building, property investment",
    "不動産": "real estate investment trust, modern office building, property investment",
    "暗号資産": "cryptocurrency bitcoin trading chart, digital currency blockchain",
    "ビットコイン": "cryptocurrency bitcoin trading chart, digital currency blockchain",
    "仮想通貨": "cryptocurrency bitcoin trading chart, digital currency blockchain",
    "データセンター": "modern data center server room, cloud computing infrastructure",
    "クラウド": "modern data center server room, cloud computing infrastructure",
    "決算": "corporate earnings report financial results, stock market analysis, business chart",
    "NVIDIA": "NVIDIA GPU graphics card, AI computing, green technology circuit board",
    "エヌビディア": "NVIDIA GPU graphics card, AI computing, green technology circuit board",
    "Apple": "Apple technology innovation, sleek modern device, minimalist design",
    "Google": "Google search technology, colorful digital innovation, cloud computing",
    "Microsoft": "Microsoft cloud computing Azure, enterprise technology, blue digital",
    "Tesla": "Tesla electric vehicle, futuristic automotive technology, green energy",
    "テスラ": "Tesla electric vehicle, futuristic automotive technology, green energy",
    "自動運転": "autonomous driving technology, self-driving car sensors, futuristic vehicle",
    "ロボット": "robotics automation technology, industrial robot arm, futuristic",
    "ロボティクス": "robotics automation technology, industrial robot arm, futuristic",
    "金": "gold investment bars and coins, precious metal trading, wealth preservation",
    "ゴールド": "gold investment bars and coins, precious metal trading, wealth preservation",
    "コモディティ": "commodity trading market, raw materials investment, global trade",
    "債券": "government bond certificate, fixed income investment, financial stability",
    "FX": "foreign exchange trading chart, currency pairs, global forex market",
    "為替": "foreign exchange trading chart, currency pairs, global forex market",
    "IPO": "IPO initial public offering, stock market bell, new company listing celebration",
    "宇宙": "space technology satellite, aerospace investment, rocket launch",
    "量子コンピュータ": "quantum computing chip, futuristic processor, blue glowing technology",
    "量子": "quantum computing chip, futuristic processor, blue glowing technology",
    "バイオ": "biotechnology DNA helix, pharmaceutical research, medical innovation",
    "医療": "healthcare medical technology, pharmaceutical innovation, hospital",
    "EV": "electric vehicle charging station, green transportation, sustainable energy",
    "エネルギー": "renewable energy solar panels wind turbines, green investment, sustainability",
    "再エネ": "renewable energy solar panels wind turbines, green investment, sustainability",
    "原子力": "nuclear power plant, clean energy technology, industrial infrastructure",
    "防衛": "defense technology military aircraft, security investment, aerospace",
    "サイバーセキュリティ": "cybersecurity digital lock shield, network protection, blue technology",
    "メタバース": "metaverse virtual reality, digital world, futuristic VR headset",
    "ブロックチェーン": "blockchain technology network, distributed ledger, digital nodes connected",
    "配当": "dividend income investment, passive income growth, money tree concept",
    "高配当": "dividend income investment, passive income growth, money tree concept",
    "新NISA": "Japanese NISA tax-free investment account, savings growth, Japan finance",
    "NISA": "Japanese NISA tax-free investment account, savings growth, Japan finance",
    "iDeCo": "retirement pension fund investment, long-term savings, financial security",
    "資産運用": "wealth management investment portfolio, financial planning, money growth",
    "ポートフォリオ": "diversified investment portfolio pie chart, asset allocation, financial strategy",
    "マクロ経済": "macroeconomics global economy, world trade map, economic indicators chart",
    "経済": "macroeconomics global economy, world trade map, economic indicators chart",
    "金利": "interest rate chart Federal Reserve, monetary policy, banking finance",
    "インフレ": "inflation rising prices chart, consumer price index, economic indicator",
    "景気": "economic cycle business growth, GDP chart, market expansion",
    "米国株": "US stock market Wall Street, American flag NYSE, financial district",
    "S&P500": "S&P 500 index chart, US stock market bull, Wall Street trading",
    "中国株": "Chinese stock market Shanghai, Asian financial market, red dragon economy",
    "新興国": "emerging markets global investment, developing countries growth, world map",
    "ごあいさつ": "elegant rose flower, luxury greeting card, pink and gold aesthetic",
    "日記": "elegant rose flower, luxury greeting card, pink and gold aesthetic",
}

DEFAULT_PROMPT = "wealth management investment portfolio, financial planning, money growth, professional photo"


def log(msg: str) -> None:
    print(msg, flush=True)


def parse_frontmatter(filepath: str) -> dict[str, str | list[str]]:
    """フロントマターを解析"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}

    fm_text = match.group(1)
    result: dict[str, str | list[str]] = {}

    title_match = re.search(r'^title:\s*"?(.*?)"?\s*$', fm_text, re.MULTILINE)
    if title_match:
        result["title"] = title_match.group(1)

    tags_match = re.search(r'^tags:\s*\[(.*?)\]', fm_text, re.MULTILINE)
    if tags_match:
        tags_str = tags_match.group(1)
        result["tags"] = [t.strip().strip('"').strip("'") for t in tags_str.split(",")]

    fi_match = re.search(r'^featureimage:\s*"?(.*?)"?\s*$', fm_text, re.MULTILINE)
    if fi_match:
        result["featureimage"] = fi_match.group(1)

    return result


def generate_prompt(tags: list[str], title: str) -> str:
    """タグとタイトルから英語プロンプトを生成"""
    for tag in tags:
        tag_clean = tag.strip()
        if tag_clean in TAG_PROMPTS:
            return TAG_PROMPTS[tag_clean]

    title_lower = title.lower()
    for keyword, prompt in TAG_PROMPTS.items():
        if keyword.lower() in title_lower:
            return prompt

    return DEFAULT_PROMPT


def slug_from_filename(filename: str) -> str:
    return os.path.splitext(os.path.basename(filename))[0]


def get_seed(slug: str) -> int:
    return int(hashlib.md5(slug.encode()).hexdigest(), 16) % 100000


def is_valid_image(path: str) -> bool:
    """ファイルが有効な画像かチェック（JPEGヘッダ確認）"""
    if not os.path.exists(path):
        return False
    if os.path.getsize(path) < 5000:
        return False
    with open(path, "rb") as f:
        header = f.read(3)
    # JPEG: FF D8 FF, PNG: 89 50 4E
    return header[:2] == b'\xff\xd8' or header[:3] == b'\x89PN'


def download_image(prompt: str, seed: int, output_path: str) -> bool:
    """Pollinations.aiから画像をダウンロード（リトライ付き、レート制限対応）"""
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1200&height=630&seed={seed}&nologo=true"

    for attempt in range(3):
        try:
            result = subprocess.run(
                ["curl", "-L", "-s", "-o", output_path, "--max-time", "120", url],
                capture_output=True,
                text=True,
                timeout=150,
            )
            if is_valid_image(output_path):
                return True
            log(f"  リトライ {attempt + 1}/3: 無効なレスポンス")
        except subprocess.TimeoutExpired:
            log(f"  リトライ {attempt + 1}/3: タイムアウト")

        # レート制限対策: リトライ前に長めに待つ
        wait = 30 * (attempt + 1)
        log(f"  {wait}秒待機...")
        time.sleep(wait)

    return False


def update_featureimage(filepath: str, new_value: str) -> None:
    """フロントマターのfeatureimageを更新"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if re.search(r'^featureimage:', content, re.MULTILINE):
        content = re.sub(
            r'^featureimage:.*$',
            f'featureimage: "{new_value}"',
            content,
            count=1,
            flags=re.MULTILINE,
        )
    else:
        content = re.sub(
            r'^(description:.*$)',
            rf'\1\nfeatureimage: "{new_value}"',
            content,
            count=1,
            flags=re.MULTILINE,
        )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


def main() -> None:
    os.makedirs(THUMBNAILS_DIR, exist_ok=True)

    md_files = sorted(
        [f for f in os.listdir(POSTS_DIR) if f.endswith(".md")]
    )

    log(f"処理対象: {len(md_files)} 記事")

    # 既にダウンロード済みの画像をスキップ
    success = 0
    skipped = 0
    failed = 0

    for i, filename in enumerate(md_files, 1):
        filepath = os.path.join(POSTS_DIR, filename)
        slug = slug_from_filename(filename)
        seed = get_seed(slug)

        fm = parse_frontmatter(filepath)
        title = fm.get("title", "")
        tags = fm.get("tags", [])

        prompt = generate_prompt(tags, title)
        output_path = os.path.join(THUMBNAILS_DIR, f"{slug}.jpg")
        featureimage_value = f"img/thumbnails/{slug}.jpg"

        # 既に有効な画像があればスキップ
        if is_valid_image(output_path):
            log(f"[{i}/{len(md_files)}] {slug} — SKIP (既存)")
            update_featureimage(filepath, featureimage_value)
            skipped += 1
            continue

        log(f"[{i}/{len(md_files)}] {slug}")
        log(f"  プロンプト: {prompt[:60]}...")

        if download_image(prompt, seed, output_path):
            update_featureimage(filepath, featureimage_value)
            size_kb = os.path.getsize(output_path) / 1024
            log(f"  OK ({size_kb:.0f}KB)")
            success += 1
        else:
            log(f"  FAILED")
            failed += 1

        # レート制限対策: 各リクエスト間に20秒待機
        time.sleep(20)

    log(f"\n完了: 成功={success}, スキップ={skipped}, 失敗={failed}")


if __name__ == "__main__":
    main()
