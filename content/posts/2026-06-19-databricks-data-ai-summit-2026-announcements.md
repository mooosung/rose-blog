---
title: "Databricks「Data + AI Summit 2026」全発表まとめ｜Genie One・LTAP・Omnigentの何が変わるのか"
date: 2026-06-19
slug: 2026-06-19-databricks-data-ai-summit-2026-announcements
categories:
  - AIバブルのツルハシ銘柄
tags: ["Databricks", "AI", "データエンジニアリング", "エンタープライズAI", "レイクハウス", "Genie", "MLflow", "Delta Lake", "AI SaaS", "米国株"]
description: "2026年6月サンフランシスコ開催のDatabricks最大年次イベント「Data + AI Summit 2026」の全発表内容を解説。Genie One、LTAP（OLTP+OLAP統合）、Agent Bricks、Unity AI Gatewayなど、エンタープライズAIの未来を変える新機能を徹底まとめ。"
summary: "2026年6月、Databricksが年次最大イベント「Data + AI Summit 2026」をサンフランシスコで開催。3万人超が参加した今年の発表は、Genie OneというAI同僚の登場から、OLTPとOLAPを統合するLTAP、オープンソースのエージェントメタハーネスOmnigentまで、盛りだくさんでしたわ。投資家・エンジニア必読のまとめよ。"
featureimage: "/img/thumbnails/2026-06-19-databricks-data-ai-summit-2026-announcements.jpg"
---

🌹 2026年6月15〜18日、サンフランシスコのモスコーニセンターで **Databricks最大の年次カンファレンス「Data + AI Summit 2026」** が開催されましたわ。登録者数は3万人超、Databricks共同創業者陣（Ali Ghodsi・Matei Zaharia・Arsalan Tavakoli-Shiraji・Reynold Xin）に加え、Satya Nadella（Microsoft CEO、事前録画）とGreg Brockman（OpenAI）がキーノートに登壇した、まさにエンタープライズAI業界最大の祭典でしたの。

今回の発表は量・質ともに過去最大規模。わたくしが主要発表を全部まとめましたわ。ふん、追いきれていない人のためにやってあげているんだから、感謝しなさいよ。

---

## 1. Genie：「AI同僚」スタック

今回最大の発表が **Genie** シリーズですわ。3つの製品が相互に連携する仕組みになっていますの。

### Genie Ontology（基盤レイヤー）
すべてのGenieの文脈を支える **自己改善型ナレッジグラフ** ですわ。テーブル・ダッシュボード・クエリ・パイプライン、さらにJira・Slack・Google Drive・SharePointなど50以上の外部アプリからビジネス知識を自動抽出しますの。

内部ベンチマークでは、実務員の質問に **84.5%を初回で正答**（汎用コーディングエージェントは52.4%）。これは単なる「AIチャット」ではなく、会社のデータの文脈を学習したビジネス特化型AIですわ。

### Genie One（フラッグシップ製品）
Web・iOS・Android・Slack・Microsoft Teamsで使えるエージェント型「AI同僚」ですわ。できることは：
- 業務上の質問への回答
- ドキュメントの自動作成
- スケジュールタスクの実行
- MCPツール経由での外部操作
- 会話からエージェントを起動

**価格体系は「1ユーザーあたり月額固定費なし」のDBU従量課金**（7月6日〜）。月150 DBU無料（約$10.50相当）ですわ。

### Genie Agents & Genie Code
Genie AgentsはGenie Spacesの進化版。非構造化データへの推論・MCPツール呼び出し・外部共有（OpenSharing）に対応しましたわ。

Genie Codeは機械学習統合（MLflow・Model Serving）・並列スレッド管理・スケジュールバックグラウンドタスク・BI移行機能（TableauやPower BIファイルを読み込んでAI/BIダッシュボードを自動生成）が追加されましたの。

---

## 2. AI/BI：ダッシュボード刷新とBI移行

AI/BI製品も大幅更新ですわ。ワークスペーステーマ・20以上のフォント・ガントチャート・コロプレスマップ・クロスフィルタリング・ドリルスルーが追加。ダッシュボードのSlack/Teamsへのサブスクリプション（CSVレポート送付）も可能になりましたわ。

バックエンドは新しい低レイテンシ高並列エンジン **Reyden** に刷新。そしてGenie Codeを通じた **TableauとPower BIからの移行機能** が今回の目玉のひとつ。既存のBIファイルをインポートするだけでUnity Catalog接続済みのAI/BIダッシュボードが生成されますわ。

---

## 3. Databricks Apps：「統制されたVibe Coding」

エンタープライズ向けのアプリ開発基盤が強化されましたわ。

| 機能 | 内容 |
|------|------|
| **App Spaces** | 複数アプリへのリソース・セキュリティ・Unity Catalogポリシーを一括管理 |
| **Genie App Builder** | 自然言語でアプリを生成するDatabricks専用AIツール（TypeScript SDK「AppKit」上） |
| **Serverless Micro Apps** | アイドル時ゼロスケール。小規模内部ツールを低コストで大量展開可能 |

さらに **Databricks Marketplace** 上でアプリを配布可能に（2万社以上の顧客が対象）。コードを公開せずIPを保護したまま配布できますわ。

---

## 4. Agent Bricks + Omnigent

**Agent Bricks** が本格的なエージェント開発プラットフォームに進化しましたわ。

- 累計エージェント構築数：10万件超
- 処理トークン：年間1京（1 quadrillion）超
- 新対応モデル：Kimi・Grok（SpaceXパートナーシップ経由）・OpenAI・Anthropic・Gemini
- 対応ハーネス：LangGraph・CrewAI・**Claude Code SDK**
- エージェント記憶管理：Lakebase統合
- Document Intelligence SQL関数（GA）
- Databricks Sandbox：エージェントの安全な隔離実行環境

**Omnigent** は今回の投資家注目ポイントのひとつ。Apache 2.0ライセンスの **オープンソース版エージェントメタハーネス** ですわ。LangGraph・CrewAI・Claude Code SDKなど複数フレームワークを1行変更で切り替え・組み合わせ可能。コスト上限設定・コンテキストポリシー設定・エージェントセッションのURL共有に対応。マネージド版（Beta）もDatabricks上で提供されますわ。

---

## 5. Unity Catalog：エージェントの文脈管理

**Unity Catalog** にセマンティクス管理機能が3つ追加されましたわ。

- **Business Glossary（近日Preview）**：ビジネス概念の権威的な定義を管理。Genie Codeと人間が共同でキュレーション
- **Domains（Public Preview）**：データ・AIアセットをビジネス部門単位で整理。エージェントが全カタログではなく関連スコープだけを参照できるように
- **Metrics**：KPIをガバナンス対象のオブジェクトとして一元定義。ダッシュボード・エージェント・アプリ全体で再利用可能

これら3つはGenie Ontologyと直接連携しますわ。Unity Catalogでセマンティクスを整備すればするほど、Genieの回答精度が上がる仕組みですの。

---

## 6. Unity AI Gateway：エージェントの行動統制

エージェントが「何にアクセスできるか」だけでなく **「何をしているか」をリアルタイムで統制** する新レイヤーが **Unity AI Gateway** ですわ。

主な機能：
- ハードな支出上限（コスト管理）
- スマートルーティング
- コンテキスト依存サービスポリシー（特定アクションの許可/拒否/承認）
- PII保護・プロンプトインジェクション対策の組み込みガードレール
- 全エージェント操作の統合トレーシング

セキュリティパートナーはCrowdStrike・Palo Alto Networks・Okta・Zscaler・Netskopeなど。エージェントのトレースはLakeWatchに流れてセキュリティ分析にも使えますわ。

---

## 7. LTAP・Lakebase：インフラの次の一手

**LTAP（Lake Transactional/Analytical Processing）** はデータインフラ史上最大級の変更かもしれませんわ。OLTPとOLAPを「データの1コピー」でオープン形式のまま統合する新アーキテクチャ。CDCパイプラインもレプリケーションも不要ですの。Databricksはこれを「データウェアハウスをレイクハウスが置き換えたのと同等のパラダイムシフト」と位置づけていますわ。

**Lakebase** は日次1200万データベース起動を処理中。今回の追加機能：
- クラウド間・リージョン間ディザスタリカバリ
- gitスタイルのブランチ・スナップショット（サブ秒操作）
- 自律型データベース運用
- Lakebase Search（Beta）：ハイブリッドベクター＋全文検索

---

## 投資家として注目すべきポイント

今回の発表を投資角度でまとめるとこうなりますわ。

*Databricksの競合優位の変化：*
• **Snowflakeとの対比**：SnowflakeがSQL・BIに特化する中、DatabricksはLTAPでOLTPまで取り込もうとしていますわ。データ統合プラットフォームとしての守備範囲が根本的に広がりましたの。
• **OpenAI・Anthropicとの共存**：Agent BricksがAnthropicやOpenAIのモデルをサポートしつつ、自社LLM（DBRX）路線も継続。「AIモデルを内包するデータ基盤」として差別化していますわ。
• **Microsoft統合の深化**：SatyaとAliの対話に象徴されるように、Azure Databricksは単なるマルチクラウド対応ではなく戦略的同盟に進化しましたの。

ふん、IPOを睨んだ発表の充実度は明らかですわね。ARR $3B超・成長率50%超の数字に、今回の製品群が乗っかれば評価額$100B超は現実的な話ですわ。べ、別にDatabricksを応援しているわけじゃないけど、投資家としては無視できない動きなんだから。

---

## まとめ

| 発表 | 一言でいうと |
|------|-------------|
| Genie One | 「ビジネスを理解するAI同僚」の誕生 |
| LTAP | OLTPとOLAPの統合・CDC不要 |
| Omnigent | エージェントフレームワーク統合の標準OSS |
| Unity AI Gateway | エージェントの「行動」をリアルタイム統制 |
| Databricks Apps | エンタープライズ向けVibe Coding |

Databricksは今や「データウェアハウスの置き換え」を超え、**エンタープライズAIの作業基盤そのもの** を取りにきていますわ。次のIPOタイミングは見逃せませんわよ 🌹
