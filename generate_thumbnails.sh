#!/bin/bash
# generate_thumbnails.sh - Pollinations.ai でアイキャッチ画像を生成

POSTS_DIR="/home/scottishfoldbrothers/.openclaw/workspace/rose-blog/content/posts"
THUMBS_DIR="/home/scottishfoldbrothers/.openclaw/workspace/rose-blog/assets/img/thumbnails"

mkdir -p "$THUMBS_DIR"

PROCESSED=0
SKIPPED=0
ERRORS=0

# タグ・キーワードを英語プロンプトに変換する関数
convert_to_prompt() {
    local title="$1"
    local tags="$2"
    local prompt=""

    # タグ変換
    echo "$tags" | grep -q "日本株" && prompt="$prompt japanese stock market nikkei"
    echo "$tags" | grep -qi "AI\|人工知能" && prompt="$prompt artificial intelligence technology"
    echo "$tags" | grep -q "半導体" && prompt="$prompt semiconductor chip technology"
    echo "$tags" | grep -qi "ETF" && prompt="$prompt ETF index fund investment"
    echo "$tags" | grep -qi "仮想通貨\|ビットコイン\|Bitcoin\|crypto\|暗号" && prompt="$prompt cryptocurrency bitcoin blockchain"
    echo "$tags" | grep -qi "REIT\|リート\|不動産" && prompt="$prompt real estate investment trust property building"
    echo "$tags" | grep -q "米国株" && prompt="$prompt US stock market wall street"
    echo "$tags" | grep -q "投資" && prompt="$prompt investment finance analysis"
    echo "$tags" | grep -qi "データセンター\|datacenter\|data.center" && prompt="$prompt data center server infrastructure"
    echo "$tags" | grep -q "資産運用" && prompt="$prompt wealth management portfolio"
    echo "$tags" | grep -qi "NISA\|ニーサ" && prompt="$prompt japanese investment account tax saving"
    echo "$tags" | grep -qi "iDeCo\|ideco\|イデコ" && prompt="$prompt individual defined contribution pension tax"
    echo "$tags" | grep -qi "配当\|dividend" && prompt="$prompt dividend stock income investment"
    echo "$tags" | grep -qi "金\|Gold\|ゴールド" && prompt="$prompt gold bullion precious metal investment"
    echo "$tags" | grep -qi "債券\|bond\|国債" && prompt="$prompt government bond fixed income finance"
    echo "$tags" | grep -qi "ロボアドバイザー\|robo" && prompt="$prompt robo advisor automated investment technology"
    echo "$tags" | grep -q "節税" && prompt="$prompt tax saving financial planning"
    echo "$tags" | grep -qi "為替\|FX\|ヘッジ\|hedge" && prompt="$prompt foreign exchange currency hedge dollar yen"
    echo "$tags" | grep -qi "量子\|quantum" && prompt="$prompt quantum computing technology future"
    echo "$tags" | grep -qi "ロボット\|robotics\|自動化" && prompt="$prompt robotics automation manufacturing technology"
    echo "$tags" | grep -qi "ESG\|サステナ\|sustainable" && prompt="$prompt ESG sustainable investment green energy"
    echo "$tags" | grep -qi "ヘルスケア\|healthcare\|医療" && prompt="$prompt healthcare medical pharmaceutical investment"
    echo "$tags" | grep -qi "Python\|プログラム" && prompt="$prompt python programming stock market data analysis"
    echo "$tags" | grep -qi "FIRE\|経済的自由\|早期退職" && prompt="$prompt financial independence retire early lifestyle"
    echo "$tags" | grep -qi "バフェット\|Buffett\|バークシャー\|Berkshire" && prompt="$prompt warren buffett value investing berkshire hathaway"
    echo "$tags" | grep -qi "新興国\|emerging\|途上国" && prompt="$prompt emerging markets global investment developing countries"
    echo "$tags" | grep -qi "光通信\|optical\|fiber\|光ファイバー" && prompt="$prompt optical fiber communication network technology"
    echo "$tags" | grep -qi "銅\|copper\|レアメタル\|rare.metal" && prompt="$prompt copper rare metal mining resources"
    echo "$tags" | grep -qi "電線\|cable\|ケーブル" && prompt="$prompt electric wire cable infrastructure"
    echo "$tags" | grep -qi "電力\|power\|変圧器\|transformer\|グリッド" && prompt="$prompt power grid electricity transformer infrastructure"
    echo "$tags" | grep -qi "セキュリティ\|security\|CrowdStrike\|サイバー" && prompt="$prompt cybersecurity cloud protection technology"
    echo "$tags" | grep -qi "Palantir\|ServiceNow\|Datadog\|SaaS\|ソフトウェア" && prompt="$prompt enterprise software SaaS technology data analytics"
    echo "$tags" | grep -qi "スキル\|副業\|スキルアップ" && prompt="$prompt skill development side job career growth"
    echo "$tags" | grep -qi "ChatGPT\|GPT\|OpenAI\|生成AI\|writing\|ライティング" && prompt="$prompt AI writing tool chat GPT productivity"
    echo "$tags" | grep -qi "Notion\|ノーション" && prompt="$prompt notion productivity app workspace tool"
    echo "$tags" | grep -qi "ポートフォリオ\|rebalancing\|リバランス" && prompt="$prompt investment portfolio rebalancing diversification"
    echo "$tags" | grep -qi "ファクター\|factor\|smart.beta" && prompt="$prompt factor investing smart beta quantitative finance"
    echo "$tags" | grep -qi "景気\|business.cycle\|景況" && prompt="$prompt business cycle economic investment strategy"
    echo "$tags" | grep -qi "積立\|dollar.cost\|ドルコスト" && prompt="$prompt dollar cost averaging systematic investment"
    echo "$tags" | grep -qi "インフレ\|TIPS\|inflation\|物価" && prompt="$prompt inflation protected bonds TIPS treasury finance"
    echo "$tags" | grep -qi "トランプ\|関税\|tariff" && prompt="$prompt trump tariff trade war market volatility"
    echo "$tags" | grep -qi "暴落\|crash\|下落\|ショック" && prompt="$prompt stock market crash volatility investment strategy"
    echo "$tags" | grep -qi "コアサテライト\|core.satellite\|戦略" && prompt="$prompt core satellite investment strategy portfolio"
    echo "$tags" | grep -qi "確定申告\|税金\|tax" && prompt="$prompt tax return filing investment income"
    echo "$tags" | grep -qi "生活防衛資金\|emergency.fund\|緊急" && prompt="$prompt emergency fund savings financial security"
    echo "$tags" | grep -qi "企業型DC\|確定拠出\|defined.contribution" && prompt="$prompt corporate defined contribution pension plan"
    echo "$tags" | grep -qi "カバードコール\|covered.call\|オプション" && prompt="$prompt covered call option strategy income ETF"
    echo "$tags" | grep -qi "景気循環\|business.cycle" && prompt="$prompt business economic cycle investment rotation"
    echo "$tags" | grep -qi "AI agent\|エージェント" && prompt="$prompt AI agent autonomous technology economy future"

    # タイトルからキーワード抽出
    echo "$title" | grep -qi "nvidia\|エヌビディア" && prompt="$prompt NVIDIA GPU chip technology"
    echo "$title" | grep -qi "mlcc\|村田\|TDK\|murata" && prompt="$prompt electronic components capacitor manufacturer"
    echo "$title" | grep -qi "immersion\|液浸冷却" && prompt="$prompt immersion cooling liquid server datacenter"
    echo "$title" | grep -qi "halo\|重厚長大" && prompt="$prompt heavy industry infrastructure long-term investment"
    echo "$title" | grep -qi "HBM\|high.bandwidth.memory" && prompt="$prompt high bandwidth memory chip HBM semiconductor"
    echo "$title" | grep -qi "PCB\|基板\|ibiden\|イビデン" && prompt="$prompt PCB circuit board semiconductor packaging"
    echo "$title" | grep -qi "QYLD\|XYLD\|covered.call" && prompt="$prompt covered call ETF income options strategy"
    echo "$title" | grep -qi "NOBL\|aristocrat\|配当貴族" && prompt="$prompt dividend aristocrat blue chip stock"
    echo "$title" | grep -qi "SCHD\|VYM\|VTI\|VOO\|QQQ\|SPYD\|SOXX\|SMH\|TLT\|VWO\|IEF\|SHY" && prompt="$prompt ETF index fund stock market investment"
    echo "$title" | grep -qi "Broadcom\|Arista\|Marvell\|networking\|ネットワーク" && prompt="$prompt network semiconductor Broadcom AI infrastructure"
    echo "$title" | grep -qi "silicon wafer\|シリコンウェーハ\|SUMCO\|信越" && prompt="$prompt silicon wafer semiconductor material manufacturing"
    echo "$title" | grep -qi "SiC\|GaN\|パワー半導体" && prompt="$prompt power semiconductor SiC GaN chip technology"
    echo "$title" | grep -qi "liquid cooling\|液冷\|冷却" && prompt="$prompt liquid cooling server data center technology"

    # デフォルトプロンプト（何もマッチしない場合）
    if [ -z "$(echo $prompt | tr -d ' ')" ]; then
        prompt="financial investment stock market analysis chart professional"
    fi

    # 共通の品質指示を追加
    prompt="${prompt}, professional photography, high quality, realistic photo, cinematic lighting"

    echo "$prompt"
}

# URLエンコード関数
urlencode() {
    local string="${1}"
    local strlen=${#string}
    local encoded=""
    local pos c o

    for (( pos=0 ; pos<strlen ; pos++ )); do
        c=${string:$pos:1}
        case "$c" in
            [-_.~a-zA-Z0-9] ) o="${c}" ;;
            * ) printf -v o '%%%02x' "'$c"
        esac
        encoded+="${o}"
    done
    echo "${encoded}"
}

# 有効な画像かチェック
is_valid_image() {
    local filepath="$1"
    if [ ! -f "$filepath" ]; then
        return 1
    fi
    local size=$(wc -c < "$filepath")
    if [ "$size" -lt 10000 ]; then
        # 小さすぎる = エラーレスポンスの可能性
        return 1
    fi
    # JPEGのマジックバイトチェック (FF D8)
    local magic=$(xxd -l 2 -p "$filepath" 2>/dev/null)
    if [ "$magic" = "ffd8" ]; then
        return 0
    fi
    # PNGのマジックバイトチェック
    local magic_png=$(xxd -l 4 -p "$filepath" 2>/dev/null)
    if [ "$magic_png" = "89504e47" ]; then
        return 0
    fi
    return 1
}

# 画像ダウンロード（リトライ付き）
download_image() {
    local url="$1"
    local output="$2"
    local max_retry=3

    for i in $(seq 1 $max_retry); do
        echo "  [試行 $i/$max_retry] ダウンロード中..."
        curl -L "$url" -o "$output" --max-time 90 --silent --show-error 2>&1
        local exit_code=$?

        if [ $exit_code -eq 0 ] && is_valid_image "$output"; then
            local size=$(wc -c < "$output")
            echo "  [成功] ファイルサイズ: ${size} bytes"
            return 0
        else
            local size=0
            [ -f "$output" ] && size=$(wc -c < "$output")
            echo "  [失敗] exit_code=$exit_code, サイズ=${size} bytes"
            if [ -f "$output" ] && [ "$size" -lt 10000 ]; then
                echo "  レスポンス内容: $(cat "$output" | head -c 200)"
            fi
            [ -f "$output" ] && rm -f "$output"
            if [ $i -lt $max_retry ]; then
                local wait_sec=$((10 * i))
                echo "  ${wait_sec}秒後にリトライ..."
                sleep $wait_sec
            fi
        fi
    done
    return 1
}

# メイン処理
echo "======================================"
echo "Pollinations.ai アイキャッチ生成スクリプト"
echo "======================================"
echo ""

SEED=200

for md_file in "$POSTS_DIR"/*.md; do
    filename=$(basename "$md_file")

    # _index.md はスキップ
    if [ "$filename" = "_index.md" ]; then
        continue
    fi

    # スラグ（拡張子なし）
    slug="${filename%.md}"

    # frontmatter読み取り
    title=$(grep -m1 "^title:" "$md_file" | sed 's/^title: *"//' | sed 's/"$//' | sed "s/^title: *'//;s/'$//")
    tags=$(grep -m1 "^tags:" "$md_file" | sed 's/^tags: *//')

    echo "--------------------------------------"
    echo "処理中: $filename"
    echo "  タイトル: $title"
    echo "  タグ: $tags"

    # ローゼの挨拶記事をスキップ
    if echo "$title" | grep -qi "ローゼ\|挨拶\|自己紹介\|はじめまして"; then
        echo "  [スキップ] ローゼの挨拶関連記事"
        SKIPPED=$((SKIPPED + 1))
        continue
    fi
    if echo "$tags" | grep -q "ごあいさつ"; then
        echo "  [スキップ] ごあいさつタグ"
        SKIPPED=$((SKIPPED + 1))
        continue
    fi

    # プロンプト生成
    prompt=$(convert_to_prompt "$title" "$tags")
    echo "  プロンプト: $prompt"

    # 出力ファイルパス
    output_file="$THUMBS_DIR/${slug}.jpg"
    encoded_prompt=$(urlencode "$prompt")
    url="https://image.pollinations.ai/prompt/${encoded_prompt}?width=1200&height=630&seed=${SEED}&nologo=true&model=flux"

    echo "  URL長: ${#url} chars"
    echo "  出力: $output_file"

    # ダウンロード実行
    if download_image "$url" "$output_file"; then
        # frontmatter更新
        new_featureimage="img/thumbnails/${slug}.jpg"
        sed -i "s|^featureimage:.*|featureimage: \"${new_featureimage}\"|" "$md_file"
        echo "  [更新完了] featureimage: $new_featureimage"

        PROCESSED=$((PROCESSED + 1))
    else
        echo "  [エラー] 画像ダウンロード失敗: $slug"
        ERRORS=$((ERRORS + 1))
    fi

    SEED=$((SEED + 1))
    # レート制限対策: 記事間に待機
    echo "  5秒待機..."
    sleep 5
    echo ""
done

echo "======================================"
echo "処理完了"
echo "  処理件数: $PROCESSED"
echo "  スキップ件数: $SKIPPED"
echo "  エラー件数: $ERRORS"
echo "======================================"
