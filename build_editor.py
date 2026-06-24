#!/usr/bin/env python3
"""ドラッグ&ドロップで順位を調整する一時エディタ rank_edit.html + rank_edit.js を生成する。
【グリッド版・固定ID方式】表紙画像だけのタイルを横並びグリッドで表示し、ワイド画面で100個同時に
ドラッグ&ドロップ並べ替え。各タイルに順位バッジ。タイトルはホバーで表示。
- カバー/ID は固定ID(cid)。並べ替えてもファイル名・ID不変＝破綻しない
- 並べ替えるたび「新順位CID: ...」を自動出力（コピー→貼り戻しで反映）
- 保存はバージョン署名つき（順位確定で作り直すと古い保存は自動無視）
- サイズ切替(小/中/大)つき
使い方: python3 build_editor.py
"""
import json, re

lines = open("game_ranking_draft.md", encoding="utf-8").read().split("\n")
title2cid = {}; cid = 0
for l in lines:
    if l.startswith("---"): break
    if l.startswith("- "):
        cid += 1; title2cid[l[2:].strip()] = cid
assert cid == 100, f"candidate={cid}"
order = []
for l in lines:
    m = re.match(r'^(\d+)\.\s+(.*)$', l)
    if m: order.append((int(m.group(1)), m.group(2).strip()))
order.sort()
games = [{"id": title2cid[t], "title": t, "img": f"game_covers/c{title2cid[t]}.jpg"} for _, t in order]
SIG = ",".join(str(g["id"]) for g in games)

JS = '''const GAMES = __GAMES__;
const SIG = "__SIG__";
const OKEY='game_edit_grid_v1';
const $=id=>document.getElementById(id);
let dragEl=null;
function curOrder(){return [...document.querySelectorAll('#grid .cell')].map(r=>+r.dataset.id);}
function renumber(){document.querySelectorAll('#grid .cell').forEach((c,i)=>{c.querySelector('.rk').textContent=(i+1);});}
function output(){const ids=curOrder();$('out').value='新順位CID: '+ids.join(',');
  localStorage.setItem(OKEY,JSON.stringify({sig:SIG,order:ids}));}
function cellHTML(g){const t=g.title.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/"/g,'&quot;');
  return '<div class="cell" draggable="true" data-id="'+g.id+'" title="'+t+'">'
    +'<span class="rk"></span>'
    +'<img loading="lazy" src="'+g.img+'" alt="'+t+'" onerror="this.style.opacity=0">'
    +'<span class="cap">'+t+'</span></div>';}
function build(orderIds){
  const byId=Object.fromEntries(GAMES.map(g=>[g.id,g]));
  const ids=(orderIds&&orderIds.length===GAMES.length&&orderIds.every(i=>byId[i]))?orderIds:GAMES.map(g=>g.id);
  $('grid').innerHTML=ids.map(id=>cellHTML(byId[id])).join('');
  renumber(); output();
}
// グリッド用: ポインタの「読み順で次」のセルを返す（無ければ末尾)
function insBefore(x,y){
  const els=[...document.querySelectorAll('#grid .cell:not(.dragging)')];
  let best=null,bd=Infinity;
  for(const el of els){const b=el.getBoundingClientRect();const cx=b.left+b.width/2,cy=b.top+b.height/2;
    const lowerRow = (cy - y) > b.height/2;
    const sameRow = Math.abs(cy - y) <= b.height/2;
    const after = lowerRow || (sameRow && cx >= x);
    if(after){const d=Math.hypot(cx-x,cy-y);if(d<bd){bd=d;best=el;}}}
  return best;
}
function init(){
  let saved=null; try{saved=JSON.parse(localStorage.getItem(OKEY)||'null');}catch(e){}
  build(saved && saved.sig===SIG ? saved.order : null);
  const grid=$('grid');
  grid.addEventListener('dragstart',e=>{const c=e.target.closest('.cell');if(!c)return;dragEl=c;setTimeout(()=>c.classList.add('dragging'),0);e.dataTransfer.effectAllowed='move';});
  grid.addEventListener('dragend',()=>{if(dragEl)dragEl.classList.remove('dragging');dragEl=null;renumber();output();});
  grid.addEventListener('dragover',e=>{e.preventDefault();if(!dragEl)return;const a=insBefore(e.clientX,e.clientY);if(a==null)grid.appendChild(dragEl);else grid.insertBefore(dragEl,a);renumber();});
  $('copy').onclick=()=>{const t=$('out');t.removeAttribute('readonly');t.select();try{navigator.clipboard.writeText(t.value)}catch(e){}try{document.execCommand('copy')}catch(e){}t.setAttribute('readonly','');};
  $('reset').onclick=()=>{if(confirm('並べ替えを破棄して現在の順位に戻す？')){localStorage.removeItem(OKEY);build(null);}};
  document.querySelectorAll('.sz').forEach(b=>b.onclick=()=>{document.getElementById('grid').style.setProperty('--cw',b.dataset.w+'px');});
}
if(document.readyState!=='loading') init(); else document.addEventListener('DOMContentLoaded', init);
'''
JS = JS.replace("__GAMES__", json.dumps(games, ensure_ascii=False)).replace("__SIG__", SIG)
open("rank_edit.js", "w", encoding="utf-8").write(JS)

HTML = '''<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>順位を編集（グリッド・ドラッグ&ドロップ）</title>
<style>
 :root{--pink:#ff5ea8;--purple:#9b5cff;--blue:#36c5ff;--ink:#2a1a4a}
 *{box-sizing:border-box}
 body{font-family:"Hiragino Kaku Gothic ProN",sans-serif;color:var(--ink);margin:0;
   background:linear-gradient(135deg,#ffd6ec,#d6e4ff,#d9fff4);min-height:100vh;padding:14px 14px 96px}
 h1{font-size:18px;text-align:center;margin:2px 0}
 .hint{max-width:1000px;margin:0 auto 10px;color:#6a4d8a;font-size:12px;text-align:center;line-height:1.6}
 .tools{text-align:center;margin-bottom:10px}
 .tools .sz{font:inherit;font-weight:800;border:0;border-radius:999px;padding:5px 12px;margin:0 3px;cursor:pointer;background:#eadcff;color:#6a4d8a}
 #grid{--cw:84px;display:flex;flex-wrap:wrap;gap:8px;justify-content:center;align-content:flex-start}
 .cell{position:relative;width:var(--cw);aspect-ratio:3/4;border-radius:8px;overflow:hidden;cursor:grab;
   background:linear-gradient(150deg,#c9d6ff,#a18bbf);box-shadow:0 3px 8px rgba(58,36,86,.18);border:2px solid #fff}
 .cell:hover{outline:3px solid var(--blue);z-index:2}
 .cell.dragging{opacity:.35;outline:3px solid var(--pink)}
 .cell img{width:100%;height:100%;object-fit:cover;display:block;pointer-events:none}
 .cell .rk{position:absolute;top:-5px;left:-5px;min-width:20px;height:20px;padding:0 5px;border-radius:999px;z-index:3;
   background:linear-gradient(135deg,var(--blue),var(--purple));color:#fff;font-weight:800;font-size:11px;font-family:Arial;
   display:flex;align-items:center;justify-content:center;box-shadow:0 2px 4px rgba(0,0,0,.3)}
 .cell .cap{position:absolute;left:0;right:0;bottom:0;padding:2px 3px;font-size:9px;font-weight:700;color:#fff;line-height:1.15;
   background:linear-gradient(transparent,rgba(0,0,0,.72));max-height:46%;overflow:hidden;pointer-events:none}
 .bar{position:fixed;left:0;right:0;bottom:0;background:rgba(255,255,255,.97);border-top:2px solid #eadcff;
   padding:10px 16px;display:flex;gap:10px;align-items:center;flex-wrap:wrap;box-shadow:0 -6px 18px rgba(58,36,86,.1);z-index:10}
 textarea{flex:1;min-width:240px;height:44px;border:2px solid #eadcff;border-radius:10px;padding:8px;font:inherit;font-size:13px}
 .btn{font:inherit;font-weight:800;border:0;border-radius:999px;padding:10px 18px;cursor:pointer;color:#fff;background:linear-gradient(135deg,var(--purple),var(--pink))}
 .btn.g{background:#eadcff;color:#6a4d8a}
</style></head><body>
<h1>✏️ 順位を編集（グリッド・ドラッグ&ドロップ）</h1>
<p class="hint">表紙タイルを<b>ドラッグして好きな位置へ</b>。番号は自動で振り直し。左上＝1位、右下＝100位（読み順）。<br>
ホバーでタイトル表示。並べ替えるたび下に<b>「新順位CID」</b>が出るので<b>「コピー」</b>して貼り付けてね。</p>
<div class="tools">表示サイズ：
  <button class="sz" data-w="60">小</button>
  <button class="sz" data-w="84">中</button>
  <button class="sz" data-w="120">大</button>
</div>
<div id="grid"></div>
<div class="bar">
  <button class="btn g" id="reset">現在の順位に戻す</button>
  <textarea id="out" readonly></textarea>
  <button class="btn" id="copy">コピー</button>
</div>
<script src="rank_edit.js"></script>
</body></html>'''
open("rank_edit.html", "w", encoding="utf-8").write(HTML)
print(f"rank_edit.html + rank_edit.js を生成（グリッド版・固定ID・{len(games)}作）")
