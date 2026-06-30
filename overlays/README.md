# overlays — 背景/オーバーレイ動画の置き場

`sanrio_movie.html` は画面下「✨ 素材」ボタンで、ここの動画を **加算合成(screen)** で全面に重ねます。
黒地の素材なら黒は透過し、**光・キラキラ・玉ボケだけ**が画面に乗ります。

## 既定素材
- `sparkle.mp4` … 同梱の**自前生成**（玉ボケ＋キラキラ・8秒ループ）。ライセンスクリーン。
  - 作り直し: `node make_overlay.mjs`

## 差し替え
`sparkle.webm`（優先）または `sparkle.mp4` を好きな素材に置き換えるだけ。
- **黒背景**の光素材（light leak / bokeh / 紙吹雪 / パーティクル）が screen 合成に最適。
- おすすめフリー素材（ロイヤリティフリー・商用OK。利用前に各規約を確認）：
  **Pixabay Video / Mixkit / Pexels / Coverr**

※ 縦9:16(1080×1920)に合う素材が理想。`object-fit:cover` で自動フィットします。
