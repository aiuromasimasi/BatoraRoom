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
    # YouTube産（またはURL差替）: その場で埋め込み視聴→⏱開始秒セット
    yt_ui = f'''<div class="ytedit"><button type="button" class="yt-open">▶ YouTube視聴</button>
      <span class="ythint">シークして「⏱セット」で開始秒が入る</span></div>
    <div class="yt-view" hidden><div class="yt-holder"></div>
      <div class="tr-time">現在 <b class="yt-cur">0</b> 秒
        <button type="button" class="yt-set">⏱ この秒を開始秒にセット</button></div></div>'''
    cells.append(f'''<div class="cell" data-cid="{cid}"{' data-steam="1"' if tr else ''}{f' data-yt="{esc(src.get("url",""))}"' if src else ''}><div class="media"><video src="{path}?v={os.path.getmtime(path):.0f}" preload="metadata" muted loop playsinline
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
    </div>{tr_ui}{yt_ui}</div>''')

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
 .tr-view,.yt-view{{padding:0 10px 10px}}
 .tr-view video{{width:100%;border-radius:8px;background:#000}}
 .ytedit{{display:flex;gap:8px;align-items:center;padding:0 10px 8px;font-size:10.5px;color:#8f7fc0}}
 .yt-open,.yt-set{{font:inherit;font-size:11px;font-weight:800;border:0;border-radius:999px;padding:4px 12px;cursor:pointer;background:#ff5e5e;color:#fff}}
 .yt-holder{{aspect-ratio:16/9;border-radius:8px;overflow:hidden;background:#000}}
 .yt-holder iframe{{width:100%;height:100%;display:block;border:0}}
 .tr-time{{font-size:12px;font-weight:700;color:#ffd23f;margin-top:4px;display:flex;gap:10px;align-items:center}}
 .tr-time b{{font-size:16px;min-width:2em;text-align:right}}
 #out{{display:none;max-width:900px;margin:12px auto;width:100%}}
 #out textarea{{width:100%;height:150px;font-family:monospace;font-size:12px;background:#0d0a1e;color:#8f8;border:1px solid #443a6e;border-radius:8px;padding:8px}}
 #out .how{{font-size:12px;color:#b8a8e0;line-height:1.8;margin-top:6px}}
 code{{background:#0d0a1e;padding:1px 6px;border-radius:4px;color:#9f9}}
</style></head><body>
<h1>🎬 実機クリップ検品・調整（{len(cells)}本）</h1>
<p class="sub">サムネをタップで再生/停止。<b>開始秒</b>＝切り出し開始位置／<b>位置</b>＝縦画面で見せる場所（即プレビュー）／<b>URL差替</b>＝別動画に変更。<br>
<b>Steam産</b>は「🎞 フル視聴」でトレーラー全編をシーク再生、<b>YouTube産</b>は「▶ YouTube視聴」でその場再生——どちらもシークして<b>「⏱この秒を開始秒にセット」</b>。<br>
※おすすめの開き方: <code>python3 serve_review.py</code> → <b>http://localhost:8899/clips_review.html</b>（SteamシークとYouTube埋め込みの両方が使える）。<br>
　file:// で開くとYouTube埋め込みが動かない場合あり／python http.server はシーク不可（Range非対応）。<br>
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
  // ---- YouTube その場視聴（IFrame API）----
  const yopen=c.querySelector('.yt-open');
  if(yopen) yopen.onclick=async()=>{{
    const v=c.querySelector('.yt-view');
    if(!v.hidden){{ v.hidden=true; yopen.textContent='▶ YouTube視聴';
      if(c._yt&&c._yt.pauseVideo)try{{c._yt.pauseVideo();}}catch(e){{}} return; }}
    const url=c.querySelector('.in-url').value.trim()||c.dataset.yt||'';
    const id=ytId(url);
    if(!id){{ alert('YouTube URLが見つかりません。URL差替欄に入れてから押してください'); return; }}
    v.hidden=false; yopen.textContent='▶ 閉じる';
    const YT=await loadYT();
    const start=Math.max(0,+(c.querySelector('.in-start').value||0));
    if(c._yt&&c._ytid===id){{ try{{c._yt.playVideo();}}catch(e){{}} return; }}
    if(c._yt){{ try{{c._yt.destroy();}}catch(e){{}} c._yt=null; }}
    const holder=v.querySelector('.yt-holder'); holder.innerHTML='<div></div>';
    c._ytid=id;
    c._yt=new YT.Player(holder.firstChild,{{videoId:id,playerVars:{{start:start,rel:0,playsinline:1}},
      events:{{onReady:e=>{{try{{e.target.playVideo();}}catch(_){{}}}}}}}});
    if(!c._ytTimer)c._ytTimer=setInterval(()=>{{ const p=c._yt;
      if(p&&p.getCurrentTime)try{{c.querySelector('.yt-cur').textContent=Math.floor(p.getCurrentTime());}}catch(e){{}} }},250);
  }};
  const yset=c.querySelector('.yt-set');
  if(yset) yset.onclick=()=>{{ const p=c._yt; if(!p||!p.getCurrentTime)return;
    const st=c.querySelector('.in-start');
    try{{ st.value=Math.floor(p.getCurrentTime()); st.dispatchEvent(new Event('input')); }}catch(e){{}} }};
}});
// YouTube IFrame API を遅延ロード（最初の「YouTube視聴」クリック時のみ）
let _ytReady=null;
function loadYT(){{ if(_ytReady)return _ytReady;
  _ytReady=new Promise(res=>{{ if(window.YT&&window.YT.Player)return res(window.YT);
    window.onYouTubeIframeAPIReady=()=>res(window.YT);
    const s=document.createElement('script'); s.src='https://www.youtube.com/iframe_api';
    document.head.appendChild(s); }});
  return _ytReady; }}
function ytId(u){{ const m=(u||'').match(/(?:v=|youtu\\.be\\/|shorts\\/|embed\\/)([A-Za-z0-9_-]{{11}})/);
  return m?m[1]:null; }}
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
