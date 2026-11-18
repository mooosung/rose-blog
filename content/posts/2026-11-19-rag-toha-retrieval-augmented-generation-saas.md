---
title: "RAGとは？検索拡張生成の仕組みとファインチューニングとの違い、SaaS企業がRAGで売っているもの"
date: 2026-11-19
draft: false
tags: ["AI SaaS・ソフトウェア", "用語集", "入門・基礎知識", "米国株"]
categories: ["AI SaaS・ソフトウェア銘柄"]
description: "RAG（検索拡張生成）とは、AIが答える前に社内文書やデータベースを検索し、見つけた資料をもとに回答を作る仕組みですわ。4つのステップでの動き方、ファインチューニングとの違い、そしてAWS・MongoDB・Elastic・SnowflakeなどのSaaS企業がRAGで何を売っているのかを、投資家目線で整理いたしますわ。"
featureimage: "https://rozenmaier.com/img/thumbnails/2026-11-19-rag-toha-retrieval-augmented-generation-saas.jpg"
featureimagecaption: "Photo by rozenmaier.com"
---

「RAG（ラグ）」という言葉、AI関連の決算資料やプレスリリースでほぼ必ず目にするようになりましたわね。

でも「結局なにをしているの？」「ファインチューニングとどう違うの？」と聞かれると、説明に困る言葉でもありますの。そして投資家にとっては、**どのSaaS企業がAIブームでお金を取れるのか**を見分けるうえで、とても大事な言葉ですわ。

この記事では、RAGとは何かを**仕組み（4ステップ）とファインチューニングとの違い**から整理し、そのうえで**SaaS企業がRAGで何を売っているのか**を、各社の公式情報をもとに説明いたしますわね🌹

---

## RAGとは｜AIに「調べてから答えさせる」仕組み

**RAG（Retrieval-Augmented Generation／検索拡張生成）**とは、AIが質問に答える前に、**社内文書やデータベースを検索し、見つけた資料を読み込んだうえで回答を作る**仕組みのことですわ。

ふつうの生成AIは、**学習した時点の知識だけ**で答えますの。だから次のような弱点がありますわ。

- 学習した後に起きた出来事を知らない
- 自社の規程・マニュアル・顧客データなど、**外に公開されていない情報**は知らない
- 知らないことでも、もっともらしい文章を作ってしまう（**ハルシネーション**）

RAGはこれを、**「試験に教科書を持ち込ませる」**ようなやり方で解決しますの。AIの頭の中身はそのままに、答える直前に必要なページを開いて見せてあげる、というイメージですわ。

### 名前の由来は2020年の論文

RAGという名前は、Facebook AI Research（現Meta）などの研究者が2020年に発表した論文「[Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401)」（NeurIPS 2020採択）から来ていますわ。この論文では、言語モデルの「頭の中の記憶」に、Wikipediaを検索できる「外付けの記憶」を組み合わせると、**より具体的で事実に沿った文章が作れる**ことが示されましたの。

それから数年で、RAGは**企業が生成AIを業務に使うときの定番の作り方**になりましたわ。

![教科書を開いて調べてから答えるAIのイメージ](/img/body/2026-11-19-rag-toha-retrieval-augmented-generation-saas-1.jpg)

---

## RAGの仕組み｜4つのステップで動く

RAGの流れは、IBMの解説（[RAGとファイン・チューニングの比較](https://www.ibm.com/jp-ja/think/topics/rag-vs-fine-tuning)）にならうと、次の4ステップですわ。

| ステップ | やること | 例：「出張の日当はいくら？」と聞いた場合 |
|---|---|---|
| ① 質問 | 利用者が質問を入力する | 社員がチャット画面に入力 |
| ② 検索 | 社内の資料置き場から、質問に関係する部分を探す | 「出張旅費規程」の日当の条文を見つける |
| ③ 統合 | 見つけた資料を質問にくっつけてAIに渡す | 「次の規程をもとに答えて：〜」という形にする |
| ④ 回答 | AIが資料をもとに答えを作る | 「国内出張の日当は〇〇円です（出張旅費規程 第5条）」 |

### 検索のカギは「ベクトル検索」

②の検索で使われるのが**ベクトル検索**ですわ。文章を数百〜数千個の数字の並び（**ベクトル**、または**埋め込み**）に変換しておき、**意味が近い文章を数字の近さで探す**方法ですの。

キーワード検索だと「日当」と書かれていない資料は見つかりませんが、ベクトル検索なら「出張手当」「宿泊以外の支給額」のような**言い回しの違う文章**も拾えますわ。このベクトルをためておく入れ物を**ベクトルデータベース**と呼びますの。

### 回答に「出典」が付けられる

RAGのもう一つの強みは、**どの資料を見て答えたかを示せる**ことですわ。AWSの[Amazon Bedrock ナレッジベース](https://aws.amazon.com/jp/bedrock/knowledge-bases/)の紹介ページでも、取得した情報には**ハルシネーションを抑えるための引用（出典）が含まれる**と説明されていますの。

社内で使うAIにとって、「どの規程の何条にそう書いてあるのか」が確かめられるのは決定的に大事ですわ。だから企業向けAIの多くがRAGを土台にしていますのよ。

![社内文書を探して出典つきで答えるRAGの流れのイメージ](/img/body/2026-11-19-rag-toha-retrieval-augmented-generation-saas-2.jpg)

---

## RAGとファインチューニングの違い

RAGとよく比べられるのが**ファインチューニング**ですわ。どちらも「AIを自社向けに賢くする」方法ですが、やり方がまったく違いますの。

| | RAG | ファインチューニング |
|---|---|---|
| 何をするか | 答える直前に資料を検索して見せる | 追加のデータでAIそのものを再学習させる |
| たとえ | 教科書の持ち込み | 授業を受けて頭に覚え込ませる |
| 情報の更新 | 資料を差し替えれば翌日から反映 | 新しい情報を入れるには学習し直し |
| 出典の提示 | できる（どの資料を見たか分かる） | 基本的にできない |
| 得意なこと | 最新情報・社内情報・数字の正確さ | 口調、専門用語の使い方、決まった出力形式 |
| 主なお金の行き先 | 検索・データベース・データ整備 | 学習用の計算資源（GPU） |

ざっくり言えば、**「何を知っているか」はRAG、「どう振る舞うか」はファインチューニング**が得意ですわ。

実際の現場では、**まずRAGから始める**ことが多いですの。規程や商品情報は毎月のように変わりますから、学習し直しが必要なファインチューニングより、資料を差し替えるだけで済むRAGのほうが扱いやすいのですわ。もちろん両方を組み合わせる使い方もありますわよ。

### AIエージェント・MCPとの関係

最近よく聞く言葉との関係も整理しておきますわね。

- **[AIエージェント](/posts/2026-11-12-ai-agent-toha-saas-business-model/)**：目標を渡すと、自分で手順を考えて作業を最後までやるAI。その途中で「調べる」場面に、RAGの仕組みが使われますの
- **[MCP（Model Context Protocol）](/posts/2026-11-05-mcp-model-context-protocol-saas-stocks/)**：AIと外部ツールをつなぐ共通規格。社内の検索システムをMCP経由でAIにつなげば、それもRAGの「検索」部分になりますわ

つまり、**MCPは差し込み口、RAGは「調べてから答える」という作法、AIエージェントはそれらを使って働く担い手**、という関係ですの。

![RAGとファインチューニングの違いを比べるイメージ](/img/body/2026-11-19-rag-toha-retrieval-augmented-generation-saas-3.jpg)

---

## SaaS企業はRAGで何を売っているのか

ここからが投資家にとっての本題ですわ。

RAGを動かすには、**①資料を取り込む → ②ベクトルに変換する → ③ためて検索する → ④AIに渡して答えさせる**という一連の部品が必要ですの。そして**この部品一つひとつが、SaaS企業やクラウド企業の商品になっている**のですわ。

| 企業（ティッカー） | RAG向けの商品 | 公式情報で確認できること |
|---|---|---|
| アマゾン（AMZN） | Amazon Bedrock ナレッジベース | 取り込み・検索・プロンプト拡張まで、RAGの流れ全体をフルマネージドで提供。保存先にMongoDBやPineconeなど外部のベクトルストアも選べる（[AWS公式](https://aws.amazon.com/jp/bedrock/knowledge-bases/)） |
| MongoDB（MDB） | MongoDB Vector Search | ふだん使っている業務データと同じ場所でベクトル検索ができ、別のデータベースや同期が不要と説明（[MongoDB公式](https://www.mongodb.com/ja-jp/products/platform/atlas-vector-search)）。2025年2月に埋め込みモデルのVoyage AIを買収（[Voyage AI公式ブログ](https://blog.voyageai.com/2025/02/24/joining-mongodb/)） |
| Elastic（ESTC） | Elasticsearch のベクトルデータベース機能 | 「世界で最もダウンロードされているベクトルデータベース」と自社で打ち出す（[Elastic公式](https://www.elastic.co/jp/elasticsearch/vector-database)）。2025年10月に埋め込み・リランカーのJina AIを買収（[Elastic IR](https://ir.elastic.co/News--Events/news/news-details/2025/Elastic-Completes-Acquisition-of-Jina-AI-a-Leader-in-Frontier-Models-for-Multimodal-and-Multilingual-Search/default.aspx)） |
| スノーフレイク（SNOW） | Snowflake Cortex Search | 自社の文書にRAGで質問するアプリの作り方を公式ガイドで案内（[Snowflake公式](https://www.snowflake.com/en/developers/guides/ask-questions-to-your-own-documents-with-snowflake-cortex-search/)） |

各社の事業の全体像は、[MongoDB（MDB）の株価分析](/posts/2026-07-23-mongodb-mdb-ai-database-stock-analysis-2026/)、[スノーフレイク（SNOW）の株価分析](/posts/2026-06-18-snowflake-snow-ai-data-cloud-stock-analysis/)、未上場の対抗馬は[Databricks（データブリックス）の解説](/posts/2026-06-17-databricks-ai-lakehouse-ipo-investment-analysis/)にまとめてありますわ。

### ポイント1：RAGは「データを持っている会社」の味方

RAGで答えの質を決めるのは、AIの頭の良さより**どんな資料を、どれだけ正確に探せるか**ですわ。つまり、企業の大事なデータをすでに預かっている**データベース・データ基盤のSaaS**にとっては、AIが「データの新しい使い道」を連れてきてくれる構図ですの。

MongoDBが「業務データと同じ場所でベクトル検索」を売り文句にしているのは、まさにここを狙っているからですわ。データを別の場所に移さなくていいなら、顧客はわざわざ乗り換える理由がありませんもの。

### ポイント2：「検索の質」をめぐる買収が続いている

MongoDBのVoyage AI買収、ElasticのJina AI買収はどちらも、**埋め込みモデル（文章をベクトルに変える部品）やリランカー（検索結果を並べ替える部品）**を手に入れるためのものですわ。

RAGの精度は検索の質で決まる——各社がそう考えているからこそ、データベースの会社が**AIモデルの会社を買っている**のですわね。

### ポイント3：クラウド大手との競争もある

一方で、AWSのBedrock ナレッジベースのように、**クラウド大手がRAGの流れ全体を丸ごと提供**する動きもありますの。

ただしAWSは、保存先としてMongoDBやPineconeなどの外部ベクトルストアも選べるようにしていますわ。クラウド大手とデータベースSaaSは、**ぶつかる面とつながる面の両方**がある関係ですの。ここは一方的な「SaaSの負け」とは言えませんわ。

![SaaS企業がRAGの部品を売っているイメージ](/img/body/2026-11-19-rag-toha-retrieval-augmented-generation-saas-4.jpg)

---

## 投資家がRAGの話を聞いたときに見るべき3点

「RAGに対応しました」という発表はもう珍しくありませんわ。だからこそ決算では、次の3点を確かめてくださいまし。

1. **AI関連の利用が、売上の伸びとして数字に出ているか**
   ベクトル検索やAI機能の利用がどれだけ増え、それが従量課金の売上にどう効いているか。「対応しました」だけで数字がない会社は、まだお金になっていない可能性が高いですわ
2. **顧客のデータがその会社に「たまっていく」構造か**
   RAGで有利なのは、資料やデータの置き場所そのものを握っている会社ですの。AI機能だけを後付けで売っている会社は、クラウド大手に置き換えられやすいですわ
3. **買収した技術が製品に組み込まれているか**
   Voyage AIやJina AIのような買収は、製品に組み込まれて初めて意味がありますの。買収後に「どの製品で使えるようになったか」を追ってくださいまし

AIの使われ方の話は、データ分析の現場にAIを持ち込んで成長してきた[パランティア（PLTR）の解説](/posts/2026-07-02-palantir-pltr-ai-enterprise-analytics-stock-analysis/)もあわせて読むと、イメージがつかみやすいですわよ。

---

## よくある質問

**Q. RAGとは簡単に言うと何ですか？**

AIが答える前に、社内文書やデータベースを検索して、見つけた資料をもとに回答を作る仕組みですわ。「教科書を持ち込んで答えるAI」と覚えてくださいまし。

**Q. RAGとファインチューニングはどちらが良いのですか？**

目的しだいですわ。最新の情報や社内の規程を正確に答えさせたいならRAG、口調や出力の形式をそろえたいならファインチューニングが向いていますの。情報の差し替えが簡単で出典も示せるので、企業ではRAGから始めることが多いですわ。

**Q. RAGを使えばハルシネーションはなくなりますか？**

なくなりはしませんわ。減らす効果はありますが、検索で間違った資料や古い資料を拾えば、AIはそれをもとに間違った答えを作りますの。RAGの質は**資料の整備と検索の精度**しだいですわ。

**Q. RAGの関連銘柄はどこですか？**

RAGの部品を提供している会社として、公式情報で確認できるのはアマゾン（Bedrock ナレッジベース）、MongoDB、Elastic、スノーフレイクなどですわ。ただし各社ともRAG専業ではなく、売上のどれだけがRAG由来かは開示されていませんの。銘柄を選ぶときは、上の「見るべき3点」で決算を確かめてくださいまし。

---

## まとめ｜RAGは「データを持つSaaS」にAIの仕事を運んでくる

| 論点 | 要点 |
|------|------|
| RAGとは | AIが答える前に資料を検索し、それをもとに回答を作る仕組み（検索拡張生成） |
| 仕組み | 質問 → 検索（ベクトル検索）→ 資料と質問を統合 → 回答。出典を示せる |
| ファインチューニングとの違い | RAGは「資料を見せる」、ファインチューニングは「頭に覚え込ませる」。更新の手軽さと出典はRAGが有利 |
| SaaS企業が売っているもの | 取り込み・ベクトル変換・ベクトル検索・回答生成の部品（AWS、MongoDB、Elastic、スノーフレイクなど） |
| 業界の動き | MongoDBがVoyage AI、ElasticがJina AIを買収。検索の質をめぐる競争 |
| 決算のチェック点 | AI利用の数字／データがたまる構造か／買収技術の製品化 |

RAGは派手な言葉ではありませんけれど、**企業がAIを「仕事で使える道具」にするための土台**ですわ。そしてその土台の材料は、企業が長年ためてきたデータですの。

AIブームで誰が稼ぐのかを考えるとき、「一番賢いAIを作る会社」だけでなく、**AIが調べに行くデータを預かっている会社**にも目を向けてみてくださいまし。

……べ、別に、MCP・AIエージェントに続けてRAGまで解説したのは、御主人様が用語の洪水で溺れないようにするためじゃありませんわよ。ふん、シリーズは完走するものですわ🌹

**参考データ出典：** [Lewis et al.「Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks」](https://arxiv.org/abs/2005.11401)（arXiv、2020年5月22日初版／NeurIPS 2020）、[IBM「RAGとファイン・チューニングの比較」](https://www.ibm.com/jp-ja/think/topics/rag-vs-fine-tuning)、[AWS「Amazon Bedrock ナレッジベース」](https://aws.amazon.com/jp/bedrock/knowledge-bases/)、[MongoDB「MongoDB Vector Search」](https://www.mongodb.com/ja-jp/products/platform/atlas-vector-search)、[Voyage AI「Stronger Together: Why We Chose to Join MongoDB」](https://blog.voyageai.com/2025/02/24/joining-mongodb/)（2025年2月24日）、[Elastic「世界で最もダウンロードされているベクトルデータベース」](https://www.elastic.co/jp/elasticsearch/vector-database)、[Elastic IR「Elastic Completes Acquisition of Jina AI」](https://ir.elastic.co/News--Events/news/news-details/2025/Elastic-Completes-Acquisition-of-Jina-AI-a-Leader-in-Frontier-Models-for-Multimodal-and-Multilingual-Search/default.aspx)（2025年10月）、[Snowflake「Ask Questions to Your Own Documents with Snowflake Cortex Search」](https://www.snowflake.com/en/developers/guides/ask-questions-to-your-own-documents-with-snowflake-cortex-search/)（いずれも2026年11月19日閲覧）。

※本記事は情報提供を目的としたものであり、特定の銘柄の売買を推奨するものではありませんわ。株価は変動し、投資元本を割り込む可能性がございます。投資判断はご自身の責任でお願いいたしますわね。
