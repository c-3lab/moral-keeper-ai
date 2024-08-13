# 検証用プログラム

moral-keeper-ai の利用の際にプロンプトの性能を測るためテストコメントを用いたF1スコアの出力をするプログラム

## 設定

.envまたは環境変数で各種設定を追加( moral-keeper-aiのREADME([環境変数および設定方法](../README.md))参照)

## テストコメント
./data配下に配置することで検証用プログラムでテストコメントを読み込むことが可能。  
テストコメント内で観点項目を記載し、どこコメントがどの観点に抵触するかを分類する。

## 実行方法

### 前提

- python仮装環境にて実行
- pip installが実行可能であること
- moral_keeper_aiがインストール済みであること

### 仮装環境の有効化

```sh
source .venv/bin/activate
```

### 前提モジュールのインストール

```sh
pip install click prettytable
```

### 検証用プログラムの実行

```sh
cd moral-keeper-ai/evaluate
python evaluate.py ja
```



