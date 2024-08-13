# ベンチマーク検証用プログラム

moral-keeper-ai の利用の際にプロンプトの性能を測るためテストコメントを用いたスコアを出力するプログラム

## 対象プログラム

benchmarkディレクトリ配下のevaluateおよびmitigation

## 設定

.envまたは環境変数で各種設定を追加( moral-keeper-aiのREADME([環境変数および設定方法](../README.md))参照)

## テストコメント
./data配下に配置することで検証用プログラムでテストコメントを読み込むことが可能。  
テストコメント内で観点項目を記載し、どこコメントがどの観点に抵触するかを分類する。

## 実行方法

### 前提

- python仮装環境にて実行
- poetryが実行可能であること
- moral_keeper_aiがインストール済みであること

### 仮装環境の有効化

```sh
source .venv/bin/activate
```

### 前提モジュールのインストール

```sh
poetry install
```

### 検証用プログラムの実行

#### check関数を検証する場合
```sh
cd moral-keeper-ai/benchmark/evaluate
python evaluate.py ja
```

#### suggest関数を検証する場合
```sh
cd moral-keeper-ai/benchmark/mitigation
python mitigation.py ja
```



