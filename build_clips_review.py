#!/usr/bin/env python3
"""game_clips/ の実機映像クリップを検品・調整する clips_review.html を生成。
各カード: 動画プレイヤー＋出典＋【開始秒/位置(左中右)/URL差替】の編集UI。
Steam産は fetch_steam_trailers.py で落としたトレーラーを【フル視聴】でき、
複数トレーラーの選択（ドロップダウン）と「⏱この秒を開始秒にセット」ができる。
- 位置はその場でプレビュー反映（「縦9:16プレビュー」で縦画面の見え方も確認可能）
- 「📋 設定をエクスポート」→ JSON を clip_meta.json に保存
  → python3 fetch_clip_meta.py（start/url/tidx分を再取得）→ python3 build_movie.py
使い方: python3 build_clips_review.py"""
import glob, json, os, re

os.chdir(os.path.dirname(os.path.abspath(__file__)))
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

sources = json.load(open("game_clips/sources.json", encoding="utf-8")) if os.path.exists("game_clips/sources.json") else {}
meta = json.load(open("clip_meta.json", encoding="utf-8")) if os.path.exists("clip_meta.json") else {}
trailers = json.load(open("game_trailers/index.json", encoding="utf-8")) if os.path.exists("game_trailers/index.json") else {}

def esc(s): return (s or "").replace("&","&amp;").replace("<","&lt;").replace('"',"&quot;")

clips = sorted((int(re.search(r'c(\d+)\.mp4$', p).group(1)), p) for p in glob.glob("game_clips/c*.mp4"))
cells = []
for cid, path in clips:
    t = cid2title.get(cid, "?"); r = rank_of.get(cid)
    src = sources.get(str(cid)); mt = meta.get(str(cid), {}); tr = trailers.get(str(cid))
    pos = mt.get("pos", "")
    tidx = int(mt.get("tidx", 0) or 0)
    if src:
        origin = f'<a class="yt" href="{esc(src.get("url",""))}" target="_blank">▶ {esc(src.get("yt_title","?")[:40])}</a>'
        cur_start = src.get("start", 90)
    else:
        gname = tr["game"] if tr else "Steam"
        origin = f'<span class="steam">Steam公式トレーラー（{esc(gname[:28])}）</span>'
        cur_start = mt.get("start", 4)
    # Steam産: トレーラー選択＋フル視聴UI
    tr_ui = ""
    if tr:
        opts = "".join(f'<option value="{mv["i"]}"{" selected" if mv["i"]==tidx else ""}>T{mv["i"]+1}: {esc(mv["name"][:26])}（{mv["dur"]}秒）</option>' for mv in tr["movies"])
        tr_ui = f'''<div class="tredit"><label>トレーラー<select class="in-tidx">{opts}</select></label>
      <button type="button" class="tr-open">🎞 フル視聴</button></div>
    <div class="tr-view" hidden><video class="tr-video" controls preload="metadata" playsinline></video>
      <div class="tr-time">現在 <b class="tr-cur">0</b> 秒
        <button type="button" class="tr-set">⏱ この秒を開始秒にセット</button></div></div>'''
    cells.append(f'''<div class="cell" data-cid="{cid}"{' data-steam="1"' if tr else ''}><div class="media"><video src="{path}?v={os.path.getmtime(path):.0f}" preload="metadata" muted loop playsinline
      style="{f'object-position:{pos} center' if pos else ''}"
      onclick="this.paused?this.play():this.pause()"></video><span class="tap">▶ タップで再生</span></div>
    <div class="cap"><b>{"?" if r is None else str(r)+"位"}</b> <b class="cid">c{cid}</b> {esc(t)}
      <span class="origin">{origin}</span></div>
    <div class="edit">
      <label>開始秒<input type="number" class="in-start" min="0" step="1" placeholder="{cur_start}" value="{esc(str(mt.get('start','')))}"></label>
      <label>位置<select class="in-pos">
        <option value=""{'' if pos else ' selected'}>中央</option>
        <option value="left"{' selected' if pos=='left' else ''}>左寄せ</option>
        <option value="right"{' selected' if pos=='right' else ''}>右寄せ</option></select></label>
      <label class="lurl">URL差替<input type="text" class="in-url" placeholder="{'(YouTubeに変える場合のみ)' if tr else '(出典のまま)'}" value="{esc(mt.get('url',''))}"></label>
    </div>{tr_ui}</div>''')

TR_JSON = json.dumps(trailers, ensure_ascii=False)

HTML = f'''<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>実機クリップ検品・調整（{len(cells)}本）</title>
<style>
 *{{box-sizing:border-box}}
 body{{font-family:"Hiragino Kaku Gothic ProN",sans-serif;margin:0;padding:18px;color:#eef;background:#14102a;min-height:100vh}}
 h1{{font-size:19px;text-align:center;margin:4px 0}}
 .sub{{text-align:center;color:#b8a8e0;font-size:12.5px;margin-bottom:10px;line-height:1.7}}
 .bar{{position:sticky;top:0;z-index:9;display:flex;gap:10px;justify-content:center;align-items:center;background:rgba(20,16,42,.96);padding:10px;border-bottom:1px solid #322858;margin:0 -18px 14px}}
 .bar button{{font:inherit;font-weight:800;border:0;border-radius:999px;padding:8px 18px;cursor:pointer;background:#7a5cff;color:#fff}}
 .bar label{{font-size:13px;font-weight:700;display:flex;gap:6px;align-items:center}}
 .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:14px;max-width:1500px;margin:0 auto}}
 .cell{{background:#1e1738;border-radius:12px;overflow:hidden;border:2px solid #322858}}
 .cell.changed{{border-color:#ffd23f}}
 .media{{position:relative;aspect-ratio:16/9;background:#000;cursor:pointer;transition:aspect-ratio .2s}}
 body.vert .media{{aspect-ratio:9/16}}
 .media video{{width:100%;height:100%;object-fit:cover;display:block}}
 .media .tap{{position:absolute;right:6px;bottom:6px;background:rgba(0,0,0,.6);color:#fff;font-size:10px;padding:2px 8px;border-radius:999px;pointer-events:none}}
 .cap{{padding:8px 10px 2px;font-size:12.5px;font-weight:700;line-height:1.5}}
 .cap .cid{{color:#a78bfa;font-family:monospace;margin:0 4px}}
 .origin{{display:block;font-size:11px;font-weight:600;margin-top:2px}}
 .origin .yt{{color:#ff8a8a;text-decoration:none}}
 .origin .steam{{color:#7fd7ff}}
 .edit,.tredit{{display:flex;flex-wrap:wrap;gap:6px 10px;padding:6px 10px;font-size:11px;color:#b8a8e0;align-items:center}}
 .tredit{{padding-top:0}}
 .edit label,.tredit label{{display:flex;align-items:center;gap:4px;font-weight:700}}
 .edit input,.edit select,.tredit select{{font:inherit;font-size:11px;background:#14102a;color:#eef;border:1px solid #443a6e;border-radius:6px;padding:3px 6px}}
 .edit .in-start{{width:64px}}
 .edit .lurl{{flex:1;min-width:100%}}
 .edit .in-url{{flex:1;width:100%}}
 .tredit .in-tidx{{max-width:200px}}
 .tr-open,.tr-set{{font:inherit;font-size:11px;font-weight:800;border:0;border-radius:999px;padding:4px 12px;cursor:pointer;background:#36c5ff;color:#06324f}}
 .tr-view{{padding:0 10px 10px}}
 .tr-view video{{width:100%;border-radius:8px;background:#000}}
 .tr-time{{font-size:12px;font-weight:700;color:#ffd23f;margin-top:4px;display:flex;gap:10px;align-items:center}}
 .tr-time b{{font-size:16px;min-width:2em;text-align:right}}
 #out{{display:none;max-width:900px;margin:12px auto;width:100%}}
 #out textarea{{width:100%;height:150px;font-family:monospace;font-size:12px;background:#0d0a1e;color:#8f8;border:1px solid #443a6e;border-radius:8px;padding:8px}}
 #out .how{{font-size:12px;color:#b8a8e0;line-height:1.8;margin-top:6px}}
 code{{background:#0d0a1e;padding:1px 6px;border-radius:4px;color:#9f9}}
</style></head><body>
<h1>🎬 実機クリップ検品・調整（{len(cells)}本）</h1>
<p class="sub">サムネをタップで再生/停止。<b>開始秒</b>＝切り出し開始位置／<b>位置</b>＝縦画面で見せる場所（即プレビュー）／<b>URL差替</b>＝別動画に変更。<br>
<b>Steam産</b>は「🎞 フル視聴」でトレーラー全編をシーク再生→<b>「⏱この秒を開始秒にセット」</b>。複数トレーラーはドロップダウンで選択（映像のみ・静止画なし）。<br>
※フル視聴のシークは <b>file:// で開いたとき</b>に有効（python http.server 経由はRange非対応でシーク不可）。<br>
変更したカードは<b style="color:#ffd23f">金枠</b>。終わったら上の「📋 設定をエクスポート」。</p>
<div class="bar">
  <button id="exp">📋 設定をエクスポート</button>
  <label><input type="checkbox" id="vert">縦9:16プレビュー</label>
  <label><input type="checkbox" id="autoplay">全部再生</label>
</div>
<div id="out"><textarea id="json" readonly></textarea>
  <div class="how">↑ この内容を <code>clip_meta.json</code> に保存（コピー済み）→
  <code>python3 fetch_clip_meta.py</code>（開始秒/URL/トレーラー変更分を再取得）→ <code>python3 build_movie.py</code>。<br>
  位置(左右)だけの変更なら <code>build_movie.py</code> の再実行だけでOK。チャットにそのまま貼ってもらえれば私がやります。</div></div>
<div class="grid">
{chr(10).join(cells)}
</div>
<script>
const TR = {TR_JSON};
const LS='clip_review_edit_v1';
function collect(){{
  const o={{}};
  document.querySelectorAll('.cell').forEach(c=>{{
    const cid=c.dataset.cid, e={{}};
    const s=c.querySelector('.in-start').value.trim();
    const p=c.querySelector('.in-pos').value;
    const u=c.querySelector('.in-url').value.trim();
    const ti=c.querySelector('.in-tidx');
    if(s!=='')e.start=+s; if(p)e.pos=p; if(u)e.url=u;
    if(ti&&+ti.value!==0)e.tidx=+ti.value;
    if(Object.keys(e).length)o[cid]=e;
    c.classList.toggle('changed',Object.keys(e).length>0);
  }});
  return o;
}}
function applyPosPreview(c){{
  const p=c.querySelector('.in-pos').value;
  c.querySelector('.media video').style.objectPosition=p?p+' center':'';
}}
function trSrc(c){{
  const cid=c.dataset.cid, ti=c.querySelector('.in-tidx');
  const mv=(TR[cid]?.movies||[]).find(m=>m.i===+(ti?.value||0));
  return mv?mv.file:null;
}}
document.querySelectorAll('.cell').forEach(c=>{{
  c.querySelectorAll('.edit input,.edit select,.in-tidx').forEach(i=>i.addEventListener('input',()=>{{
    applyPosPreview(c); localStorage.setItem(LS,JSON.stringify(collect()));
    if(i.classList.contains('in-tidx')){{ const v=c.querySelector('.tr-view');
      if(v&&!v.hidden){{ const s=trSrc(c); if(s){{v.querySelector('video').src=s;}} }} }}
  }}));
  const open=c.querySelector('.tr-open');
  if(open) open.onclick=()=>{{ const v=c.querySelector('.tr-view'); v.hidden=!v.hidden;
    const vid=v.querySelector('video');
    if(!v.hidden){{ const s=trSrc(c); if(s&&!vid.src.endsWith(s))vid.src=s; vid.play().catch(()=>{{}}); open.textContent='🎞 閉じる'; }}
    else {{ vid.pause(); open.textContent='🎞 フル視聴'; }} }};
  const tv=c.querySelector('.tr-video');
  if(tv){{ const showT=()=>{{ c.querySelector('.tr-cur').textContent=Math.floor(tv.currentTime); }};
    tv.addEventListener('timeupdate',showT); tv.addEventListener('seeked',showT); tv.addEventListener('pause',showT);
    c.querySelector('.tr-set').onclick=()=>{{ const st=c.querySelector('.in-start');
      st.value=Math.floor(tv.currentTime); st.dispatchEvent(new Event('input')); }}; }}
}});
try{{ const sv=JSON.parse(localStorage.getItem(LS)||'{{}}');
  for(const cid in sv){{ const c=document.querySelector(`.cell[data-cid="${{cid}}"]`); if(!c)continue;
    if(sv[cid].start!=null)c.querySelector('.in-start').value=sv[cid].start;
    if(sv[cid].pos)c.querySelector('.in-pos').value=sv[cid].pos;
    if(sv[cid].url)c.querySelector('.in-url').value=sv[cid].url;
    if(sv[cid].tidx!=null&&c.querySelector('.in-tidx'))c.querySelector('.in-tidx').value=sv[cid].tidx;
    applyPosPreview(c); }}
  collect();
}}catch(e){{}}
document.getElementById('exp').onclick=()=>{{
  const j=JSON.stringify(collect(),null,1);
  const o=document.getElementById('out'); o.style.display='block';
  document.getElementById('json').value=j;
  navigator.clipboard&&navigator.clipboard.writeText(j).catch(()=>{{}});
  o.scrollIntoView({{behavior:'smooth'}});
}};
document.getElementById('vert').onchange=e=>document.body.classList.toggle('vert',e.target.checked);
document.getElementById('autoplay').onchange=e=>document.querySelectorAll('.media video').forEach(v=>e.target.checked?v.play():v.pause());
</script>
</body></html>'''
open("clips_review.html", "w", encoding="utf-8").write(HTML)
n_steam = sum(1 for cid,_ in clips if str(cid) in trailers)
print(f"clips_review.html 生成（{len(cells)}本・うちSteam産フル視聴対応 {n_steam}本）")
