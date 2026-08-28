#!/usr/bin/env python3
"""IndexNowでBingに更新URLを通知する。

なぜ必要か（2026-08-28）:
    rozenmaier.com の実流入を分解したところ、日本からのオーガニック検索は
    直近7日でbing 74セッションに対し google 1セッションだった。
    稼いでいるのはBingであり、Bingへの反映を早める価値が高い。
    IndexNowはBing公式のプッシュ通知APIで、アカウント登録なしで使える。

前提:
    static/<KEY>.txt にキーを平文で置き、公開されていること。

Usage:
    python3 scripts/indexnow_submit.py                 # sitemapの全URLを通知
    python3 scripts/indexnow_submit.py <url> [<url>..] # 個別URLだけ通知
"""
import glob
import json
import os
import re
import sys
import urllib.request

HOST = 'rozenmaier.com'
STATIC = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static')
ENDPOINT = 'https://api.indexnow.org/indexnow'
BATCH = 10000  # IndexNowの1回あたり上限


def find_key():
    for p in glob.glob(os.path.join(STATIC, '*.txt')):
        name = os.path.basename(p)[:-4]
        if re.fullmatch(r'[0-9a-f]{32,128}', name):
            return name
    sys.exit('static/ にIndexNowのキーファイルが見つかりませんわ')


def sitemap_urls():
    with urllib.request.urlopen(f'https://{HOST}/sitemap.xml', timeout=30) as r:
        xml = r.read().decode('utf-8', 'replace')
    return re.findall(r'<loc>([^<]+)</loc>', xml)


def submit(urls, key):
    payload = {
        'host': HOST,
        'key': key,
        'keyLocation': f'https://{HOST}/{key}.txt',
        'urlList': urls,
    }
    req = urllib.request.Request(
        ENDPOINT, data=json.dumps(payload).encode(),
        headers={'Content-Type': 'application/json; charset=utf-8'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.status, r.read().decode('utf-8', 'replace')[:300]


def main():
    key = find_key()
    urls = sys.argv[1:] or sitemap_urls()
    if not urls:
        sys.exit('通知するURLがありませんわ')
    print(f'キー: {key}')
    print(f'通知URL数: {len(urls)}')
    for i in range(0, len(urls), BATCH):
        chunk = urls[i:i + BATCH]
        try:
            status, body = submit(chunk, key)
            print(f'  {len(chunk)}件 → HTTP {status} {body}')
        except urllib.error.HTTPError as e:
            print(f'  {len(chunk)}件 → HTTP {e.code} {e.read().decode("utf-8","replace")[:300]}')
            sys.exit(1)
    print('完了ですわ。200/202なら受理されています。')


if __name__ == '__main__':
    main()
