# moral-keeper-ai

moral-keeper-ai は、SNSなどにおいてユーザーが投稿するテキストが不適切かどうかをAIで判定し、表現を和らげるためのPython製オープンソースプログラムです。
このAI駆動ツールは、投稿内容を解析し、基準に適合しているかを確認します。
個人、企業、コミュニティマネージャーの皆様に、ポジティブで尊敬のあるオンラインプレゼンスを維持するお手伝いをします。

## 使用技術

- Azure OpenAI Service
- OpenAI
- GPT-4o
- GPT-3turbo

## Main features

- ある文章が投稿内容として適切かどうか判定する
- ある文章が投稿内容として適切さをスコアリングする
- 投稿内容として適切な文章を提案する
- Pythonからのメソッド呼び出しが可能。
- APIサーバーとしてhttps経由で使用可能

## Quick Start

1. インストール

```sh
pip install moral-keeper-ai
```

2. 

.envまたは環境変数で各種設定を追加

3. 

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

## 開発環境

## LICENSE

[MIT license](https://github.com/c-3lab/moral-keeper-ai#MIT-1-ov-file)

## CopyRight

Copyright (c) 2024 C3Lab
