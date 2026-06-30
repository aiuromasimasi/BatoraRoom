#!/usr/bin/env python3
"""sanrio_candidates.json から表紙レビューページ sanrio_covers_review.html を生成。

各順位について「現在 採用中の cN.png」と「候補A/B/C」を並べて目視確認するためのページ。
おかしい画像があれば、表示されたコマンド例のように fetch_sanrio_covers.py へ 順位:ラベル を渡して差し替える。

使い方: python3 build_sanrio_review.py  →  sanrio_covers_review.html をブラウザで開く
"""
import json, html

cand = json.load(open("sanrio_candidates.json", encoding="utf-8"))

cards = []
for r in sorted(cand, key=lambda x: int(x)):
    e = cand[r]
    name = html.escape(e["name"])
    thumbs = [
        f'<figure class="cur"><img src="sanrio_covers/c{r}.png" '
        f'onerror="this.parentNode.classList.add(\'miss\')" loading="lazy">'
        f'<figcaption>現在 <b>c{r}.png</b></figcaption></figure>'
    ]
    for it in e["candidates"]:
        lab = html.escape(it.get("label", "?"))
        url = html.escape(it.get("url", ""))
        note = html.escape(it.get("note", ""))
        src = html.escape(it.get("source", ""))
        thumbs.append(
            f'<figure><img src="{url}" onerror="this.parentNode.classList.add(\'miss\')" loading="lazy">'
            f'<figcaption><span class="lab">{lab}</span> {note}<br><span class="src">{src}</span></figcaption></figure>'
        )
    page = html.escape(e.get("pageUrl", ""))
    cards.append(
        f'<section><h2><span class="rk">{r}</span> {name} '
        f'{"<a href=\'"+page+"\' target=\'_blank\'>公式ページ</a>" if page else ""}</h2>'
        f'<div class="row">{"".join(thumbs)}</div>'
        f'<code>差し替え例: python3 fetch_sanrio_covers.py {r}:B --upscale 2</code></section>'
    )

HTML = """<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>サンリオ表紙レビュー（確認→差し替え）</title>
<link href="https://fonts.googleapis.com/css2?family=Mochiy+Pop+One&family=M+PLUS+Rounded+1c:wght@700;800&display=swap" rel="stylesheet">
<style>
  *{margin:0;padding:0;box-sizing:border-box}
  body{font-family:"M PLUS Rounded 1c",sans-serif;background:#fff2f8;color:#5a2a4a;padding:18px;line-height:1.5}
  h1{font-family:"Mochiy Pop One";color:#ff5fa6;font-size:24px;margin-bottom:6px}
  .sub{font-weight:700;color:#9a6a86;margin-bottom:18px;font-size:14px}
  section{background:#fff;border-radius:16px;padding:14px 16px;margin-bottom:14px;box-shadow:0 6px 18px rgba(255,138,209,.18)}
  h2{font-size:18px;display:flex;align-items:center;gap:10px;margin-bottom:10px}
  h2 .rk{font-family:"Mochiy Pop One";background:#ff7ac1;color:#fff;border-radius:10px;padding:2px 12px}
  h2 a{font-size:12px;color:#9b7bff;font-weight:800}
  .row{display:flex;gap:12px;flex-wrap:wrap}
  figure{width:150px;background:#faf3fb;border:2px solid #f0d8ea;border-radius:12px;padding:8px;text-align:center}
  figure.cur{border-color:#ff7ac1;background:#fff0f7}
  figure img{width:100%;height:150px;object-fit:contain;border-radius:8px;background:
    linear-gradient(45deg,#eee 25%,transparent 25%,transparent 75%,#eee 75%) 0 0/16px 16px,
    linear-gradient(45deg,#eee 25%,#fafafa 25%,#fafafa 75%,#eee 75%) 8px 8px/16px 16px}
  figure.miss img{display:none}
  figure.miss::before{content:"× 表示不可";display:block;height:150px;display:flex;align-items:center;justify-content:center;color:#c66;font-weight:800;background:#fbe9e9;border-radius:8px}
  figcaption{font-size:11px;font-weight:700;margin-top:6px;color:#7a4a66}
  .lab{display:inline-block;background:#9b7bff;color:#fff;border-radius:6px;padding:0 7px;font-weight:800}
  .src{color:#b08aa0;font-size:10px}
  code{display:block;margin-top:10px;background:#2a1a3a;color:#ffd6ee;font-size:12px;padding:7px 10px;border-radius:8px;font-family:ui-monospace,monospace;user-select:all}
</style></head><body>
  <h1>サンリオ 表紙レビュー 🎀</h1>
  <div class="sub">各順位の「現在採用 cN.png」と「候補A/B/C」を見比べて、違う画像・崩れがあれば下のコマンドで差し替え（順位:ラベル）。差し替え後は <b>python3 build_sanrio_movie.py</b> で再ビルド。チェック柄は透過部分です。</div>
  __CARDS__
</body></html>"""

open("sanrio_covers_review.html", "w", encoding="utf-8").write(HTML.replace("__CARDS__", "\n".join(cards)))
print("sanrio_covers_review.html 生成完了（20順位・現在＋候補A/B/C）")
