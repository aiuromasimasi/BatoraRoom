#!/usr/bin/env python3
"""新規追加カバー(cid101〜)が正しいか目視確認するための一覧ページ cover_review.html を生成。
各タイルに表紙＋cid＋タイトル。表紙が無いものは赤い「未取得」プレースホルダー。
使い方: python3 build_cover_review.py
"""
import re, os

lines = open("game_ranking_draft.md", encoding="utf-8").read().split("\n")
title2cid = {}; cid = 0
for l in lines:
    if l.startswith("---"): break
    if l.startswith("- "):
        cid += 1; title2cid[l[2:].strip()] = cid
cid2title = {v: k for k, v in title2cid.items()}

NEW_FROM = 101
NOTES = {101: "※横長・左右切れ", 103: "※横長・左右切れ", 116: "※横長・左右切れ", 117: "※ほぼ正方形", 119: "※タイトル画面・低解像", 123: "※超横長・中央のみ", 130: "※白余白あり", 159: "※横長・左右切れ",
         146: "△初代？RR-Z要確認", 162: "△SFC版(指定はGG?)", 168: "△A-Train汎用(4?)", 169: "△Assault Horizon", 170: "△現代版Sokoban"}

def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;").replace('"', "&quot;")

cells = []
miss = []
for c in range(NEW_FROM, cid + 1):
    t = cid2title.get(c, "?")
    img = f"game_covers/c{c}.jpg"
    note = NOTES.get(c, "")
    if os.path.exists(img):
        media = f'<img loading="lazy" src="{img}" alt="">'
        cls = "cell"
    else:
        media = '<div class="ph">未取得<br><small>URL求む</small></div>'
        cls = "cell miss"; miss.append(c)
    cells.append(
        f'<div class="{cls}"><div class="media">{media}</div>'
        f'<div class="cap"><b>c{c}</b> {esc(t)}'
        f'{f"<span class=note>{esc(note)}</span>" if note else ""}</div></div>'
    )

HTML = f'''<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>表紙チェック（新規 c{NEW_FROM}〜c{cid}）</title>
<style>
 *{{box-sizing:border-box}}
 body{{font-family:"Hiragino Kaku Gothic ProN",sans-serif;margin:0;padding:18px;color:#23173f;
   background:linear-gradient(135deg,#ffe3f1,#e3ecff,#e1fff6);min-height:100vh}}
 h1{{font-size:19px;text-align:center;margin:4px 0}}
 .sub{{text-align:center;color:#6a4d8a;font-size:13px;margin-bottom:16px;line-height:1.6}}
 .sub b{{color:#d6346a}}
 .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:16px;max-width:1300px;margin:0 auto}}
 .cell{{background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 4px 14px rgba(58,36,86,.16);border:2px solid #fff}}
 .cell.miss{{border-color:#ff6b8e;background:#fff0f4}}
 .media{{aspect-ratio:3/4;background:#241836;display:flex;align-items:center;justify-content:center;overflow:hidden}}
 .media img{{width:100%;height:100%;object-fit:cover;display:block}}
 .ph{{color:#ff5e86;font-weight:800;text-align:center;font-size:15px;line-height:1.5}}
 .ph small{{color:#b06; font-weight:700}}
 .cap{{padding:8px 10px;font-size:12.5px;font-weight:700;line-height:1.4}}
 .cap b{{color:#7a3cff;font-family:Arial;margin-right:4px}}
 .note{{display:block;color:#d6346a;font-size:11px;font-weight:800;margin-top:2px}}
</style></head><body>
<h1>🖼 表紙チェック（新規 c{NEW_FROM}〜c{cid}）</h1>
<p class="sub">アップスケール前の確認用。<b>違う作品の表紙があれば「cデジ」と正しいURL</b>を教えてください。<br>
赤枠＝<b>未取得（{len(miss)}件）</b>：{", ".join("c"+str(m) for m in miss) if miss else "なし"}</p>
<div class="grid">
{chr(10).join(cells)}
</div>
</body></html>'''
open("cover_review.html", "w", encoding="utf-8").write(HTML)
print(f"cover_review.html 生成（c{NEW_FROM}〜c{cid}・{cid-NEW_FROM+1}枚・未取得{len(miss)}件: {miss}）")
