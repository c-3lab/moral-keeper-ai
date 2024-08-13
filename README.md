# moral-keeper-ai

moral-keeper-ai は、入力されたテキストを以下の視点でAIが判定し、テキストの修正案を出力するPython製オープンソースプログラムです。
- ユーザーが投稿するテキストが読み手にとって不快になる
- 投稿者の炎上のきっかけにならない
- 曖昧な意見投稿による運営者のカスタマー業務の工数の肥大を抑止する

これによりポジティブで尊敬のあるオンラインプレゼンスを維持するお手伝いをします。

## 使用技術

- OpenAI API

## 対応APIサーバー

- Azure OpanAI Service

## 推奨モデル

- GPT-4o mini
- GPT-4o
- GPT-3turbo

## Main features

- ある文章が投稿内容として適切かどうか判定する
- 問題のある投稿内容に対してより適切な表現の文章を提案する
- Pythonからのメソッド呼び出しが可能
- APIサーバーとしてhttp経由で使用可能

## Quick Start

1. インストール

```sh
pip install moral-keeper-ai
```

2. 設定

.envまたは環境変数で各種設定を追加( [環境変数および設定方法](#環境変数および設定方法)参照)

3. 使用例

```python
import moral_keeper_ai
judgment, details = moral_keeper_ai.check('チェックしたい文章')
suggested_message = moral_keeper_ai.suggest('投稿内容として適切にしたい文章')
```

### moral_keeper_ai.check()

戻り値：タプル

- judgment: bool ：True(問題無い)、False(問題あり)
- details: list：問題があった場合にどの項目で問題ありと判定されたかのリスト

概要
受け取った文章を企業の広報担当者が検閲するプロンプト。
内部設定された項目で検閲し、全ての項目をクリアしない場合は望ましくない文章であると判断する。

### moral_keeper_ai.suggest()

戻り値：文字列
概要
受け取った文章の表現緩和を行うプロンプト。
表現緩和後の文字列を返す。

## 環境変数および設定方法

### APIキー

```bash
export AZURE_OPENAI_KEY='APIキー'
```

### エンドポイント

```bash
export AZURE_ENDPOINT='エンドポイントURL'
```

### 使用モデル

```bash
export LLM_MODEL='モデル名/デプロイ名'
```

## ディレクトリ構成
<pre>
.  
├── moral_keeper_ai：モジュール本体
├── tests：pytest資材
├── docs：ドキュメント
└── benchmark：ベンチマーク検証用プログラム
  └──evaluate：check関数用
    └──data：テストコメントファイル
  └──mitigation：suggest関数用
    └──data：テストコメントファイル
</pre>

## LICENSE

[MIT license](https://github.com/c-3lab/moral-keeper-ai#MIT-1-ov-file)

## CopyRight

Copyright (c) 2024 C3Lab
