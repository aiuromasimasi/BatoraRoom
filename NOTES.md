# 制作ノウハウ — サンリオ大賞 TOP20 カウントダウン動画ジェネレータ

> マージせず参照用に残すブランチ。次回「縦型ランキング発表動画」を作るときの再利用メモ。
> 汎用部分はスキル `/countdown-movie` に抽出済み（このリポジトリ非依存）。

## 何ができるか
データ(CSV)から、**自己完結HTML**の縦9:16カウントダウン発表ムービーを生成し、**Puppeteer+ffmpegでMP4化**する。
派手な演出（投票数ローリング／順位レーン／プロフィールクイズ→シルエット→公開／3テーマ／バースト・紙吹雪・スポットライト／効果音／オーバーレイ動画）入り。

## ファイル構成と役割
| ファイル | 役割 |
|---|---|
| `sanrio_data.csv` | マスターデータ（順位/名前/票数/紹介/昨年順位/好きなもの/デビュー/趣味/誕生日/画像） |
| `build_sanrio_movie.py` | CSV→`sanrio_movie.html` 生成（CSS/JSを文字列で埋め込む単一ビルダ） |
| `sanrio_movie.html` | 生成物（外部依存ゼロ。ダブルクリックでも再生可） |
| `fetch_sanrio_covers.py` | 公式立ち絵をDL→sipsでPNG変換＆2倍アップスケール |
| `sanrio_candidates.json` / `sanrio_out_candidates.json` | 画像候補URL(A/B/C)とランク外キャラ |
| `build_sanrio_review.py` / `sanrio_covers_review.html` | 採用画像vs候補の目視レビュー＆差替コマンド表示 |
| `record_sanrio.mjs` | Puppeteer screencast→ffmpegでMP4録画（標準/速い×30/60fps） |
| `make_overlay.mjs` | 加算合成オーバーレイ素材(玉ボケ)を自前生成（ライセンスクリーン） |
| `sounds/` `overlays/` `sanrio_covers/` | 差し替え素材置き場（各READMEに手順） |

## 基本フロー
```bash
# 1. データ編集後、再ビルド
python3 build_sanrio_movie.py

# 2. プレビュー（静的サーバ）
python3 -m http.server 8141   # → http://localhost:8141/sanrio_movie.html

# 3. 画像の取得/差替（必要時）
python3 fetch_sanrio_covers.py            # 全A取得
python3 fetch_sanrio_covers.py 19:B --upscale 2   # 個別差替＋2倍
python3 build_sanrio_review.py            # レビューページ生成

# 4. オーバーレイ素材を作り直す（任意）
node make_overlay.mjs                      # → overlays/sparkle.mp4

# 5. MP4化（録画）
node record_sanrio.mjs                      # 全4本
node record_sanrio.mjs standard             # 標準30fps のみ
node record_sanrio.mjs standard60 fast60    # 60fps版
```

## 設計の勘所（再利用ポイント）
- **自己完結HTML**: CSS/JSをPython文字列に埋め込み、CSVをJSONとして差し込む。外部依存ゼロ＝配布・録画が楽。
- **演出の駆動**: `steps[]`（op→各バナー/キャラ→ed）に重み`WT()`で尺配分、RAFで投票数イーズアウト。`gen`カウンタで世代管理し、シーク/速度変更時の競合を防ぐ。
- **クイズのタメ**: `QUIZ_FROM`で対象ランク境界を制御（1=全ランク）。ヒントはCSS `animation-delay`で段階表示、正解は最後のヒント+0.5sで公開。
- **シルエット**: 透過PNGに `filter:brightness(0)`、別レイヤー`.sil`で背景色。→キャラ形のシルエットになる（カード全体を暗くするとただの黒四角になるので注意）。
- **テーマ**: `#frame.theme-a/b/c` をCSS変数で切替。既定は②キャンディ(`theme-b`)。
- **音**: Web Audioで手続き合成（`SFX`）。`sounds/<name>.mp3`があれば自動差替。ブラウザ仕様上ユーザー操作で起動。
- **オーバーレイ**: `<video>`を`mix-blend-mode:screen`で重ねる。黒背景素材なら光だけ乗る。`overlays/`で差替。

## ハマりどころ（重要）
- **Python 3.14/3.12 で pyexpat が壊れておりpip/playwright不可** → Node.js + **Puppeteer** で録画した。
- **録画サイズがプレビューと一致しない** → `deviceScaleFactor:2` でlogical 540×960描画→物理1080×1920。これでcqwスケールがプレビュー等倍に。
- **screencastは映像のみ＝MP4は無音**。SE/BGMはライブ再生/画面録画用。MP4に音を入れるなら後段でffmpeg muxが必要。
- **透過PNGの確認**: PNGのIHDR `color_type`（25バイト目）が6ならRGBA(透過あり)。シルエットには透過必須。RGB(2)の候補は避ける。
- **macOSのgrepが日本語で文字化け** → Python `str.count()`/`re` で代替。
- **HTMLテンプレ内の `\u{...}`** は非raw文字列だとSyntaxError → 絵文字は直書き。
- **オーバーレイのerror監視はvideo要素単位**（capture:trueにすると`<source>`単位の失敗まで拾い誤作動）。

## フリー素材運用
- SE: 効果音ラボ / DOVA-SYNDROME / 甘茶の音楽工房 / Pixabay・Mixkit（`sounds/`に同名mp3）
- 動画: Pixabay / Mixkit / Pexels / Coverr（黒背景の光素材を`overlays/`へ。screen合成前提）
- ⚠ サンリオのキャラ画像自体は著作物（ファン利用）。周辺素材をクリーンにしても画像の扱いは別途確認。
