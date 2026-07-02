#!/usr/bin/env python3
"""game_clips/ の実機映像クリップを目視確認する clips_review.html を生成。
各タイルに動画プレイヤー＋ランク＋タイトル＋出典(YouTube動画名/リンク)。
違うゲームの映像なら `rm game_clips/c<cid>.mp4` で消せばビルド時に表紙へフォールバック。
使い方: python3 build_clips_review.py"""
import glob, json, os, re

lines = open("game_ranking_draft.md", encoding="utf-8").read().split("\n")
title2cid = {}; c = 0
for l in lines:
    if l.startswith("---"): break
    if l.startswith("- "):
        c += 1; title2cid[l[2:].strip()] = c
cid2title = {v: k for k, v in title2cid.items()}
rank_of = {}
for l in lines:
    m = re.match(r'^(\d+)\.\s+(.*)$', l)
    if m: rank_of[title2cid[m.group(2).strip()]] = int(m.group(1))

sources = {}
if os.path.exists("game_clips/sources.json"):
    sources = json.load(open("game_clips/sources.json", encoding="utf-8"))

def esc(s): return (s or "").replace("&","&amp;").replace("<","&lt;").replace('"',"&quot;")

clips = sorted((int(re.search(r'c(\d+)\.mp4$', p).group(1)), p) for p in glob.glob("game_clips/c*.mp4"))
cells = []
for cid, path in clips:
    t = cid2title.get(cid, "?"); r = rank_of.get(cid)
    src = sources.get(str(cid))
    if src:
        origin = f'<a class="yt" href="{esc(src.get("url",""))}" target="_blank">▶ {esc(src.get("yt_title","?")[:44])}</a>'
    else:
        origin = '<span class="steam">Steam公式トレーラー</span>'
    sz = os.path.getsize(path) // 1024
    cells.append(f'''<div class="cell"><div class="media"><video src="{path}" preload="metadata" muted loop playsinline
      onclick="this.paused?this.play():this.pause()"></video><span class="tap">▶ タップで再生</span></div>
    <div class="cap"><b>{"?" if r is None else str(r)+"位"}</b> <b class="cid">c{cid}</b> {esc(t)}
      <span class="origin">{origin}</span><code>rm game_clips/c{cid}.mp4</code></div></div>''')

HTML = f'''<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>実機クリップ確認（{len(cells)}本）</title>
<style>
 *{{box-sizing:border-box}}
 body{{font-family:"Hiragino Kaku Gothic ProN",sans-serif;margin:0;padding:18px;color:#eef;background:#14102a;min-height:100vh}}
 h1{{font-size:19px;text-align:center;margin:4px 0}}
 .sub{{text-align:center;color:#b8a8e0;font-size:13px;margin-bottom:16px;line-height:1.6}}
 .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:14px;max-width:1400px;margin:0 auto}}
 .cell{{background:#1e1738;border-radius:12px;overflow:hidden;border:2px solid #322858}}
 .media{{position:relative;aspect-ratio:16/9;background:#000;cursor:pointer}}
 .media video{{width:100%;height:100%;object-fit:cover;display:block}}
 .media .tap{{position:absolute;right:6px;bottom:6px;background:rgba(0,0,0,.6);color:#fff;font-size:10px;padding:2px 8px;border-radius:999px;pointer-events:none}}
 .cap{{padding:8px 10px;font-size:12.5px;font-weight:700;line-height:1.5}}
 .cap .cid{{color:#a78bfa;font-family:monospace;margin:0 4px}}
 .origin{{display:block;font-size:11px;font-weight:600;margin-top:3px}}
 .origin .yt{{color:#ff8a8a;text-decoration:none}}
 .origin .steam{{color:#7fd7ff}}
 code{{display:block;font-size:10px;color:#8a7ab8;margin-top:3px;user-select:all}}
</style></head><body>
<h1>🎬 実機クリップ確認（{len(cells)}本）</h1>
<p class="sub">サムネをタップで再生/停止。<b>別のゲームの映像</b>だったら下の rm コマンドで削除→ python3 build_movie.py で表紙にフォールバックします。<br>
赤リンク＝YouTube出典（クリックで元動画）／青＝Steam公式トレーラー</p>
<div class="grid">
{chr(10).join(cells)}
</div>
</body></html>'''
open("clips_review.html", "w", encoding="utf-8").write(HTML)
print(f"clips_review.html 生成（{len(cells)}本）")
