#!/usr/bin/env python3
"""ドラッグ&ドロップで順位を調整する一時エディタ rank_edit.html + rank_edit.js を生成する。
【グリッド版・固定ID方式・ランク外プール対応】表紙タイルを横並びグリッドで表示し、ワイド画面で
全作品(TOP100＋ランク外)を同時にドラッグ&ドロップ並べ替え。
- カバー/ID は固定ID(cid)。並べ替えてもファイル名・ID不変＝破綻しない
- 上から100枠＝ランキング、その下に「ランク外（101位〜）」の区切り線。境界をまたいで入替できる
- 表紙が無い作品（予備軍など）は「タイトル札」プレースホルダーで表示（昇格後に表紙取得）
- 並べ替えるたび「新順位CID（上位100）」＋「ランク外CID（残り）」を自動出力（コピー→貼り戻しで反映）
- 保存はバージョン署名つき（候補が増減すると古い保存は自動無視）
- サイズ切替(小/中/大)つき
使い方: python3 build_editor.py
"""
import json, re

RANKED = 100  # 上位この数までがランキング。それ以降はランク外プール
lines = open("game_ranking_draft.md", encoding="utf-8").read().split("\n")
title2cid = {}; cid = 0
for l in lines:
    if l.startswith("---"): break
    if l.startswith("- "):
        cid += 1; title2cid[l[2:].strip()] = cid
cid2title = {v: k for k, v in title2cid.items()}
TOTAL = cid
assert TOTAL >= RANKED, f"candidate={TOTAL} (< {RANKED})"

order = []
for l in lines:
    m = re.match(r'^(\d+)\.\s+(.*)$', l)
    if m: order.append((int(m.group(1)), m.group(2).strip()))
order.sort()
ranked_cids = [title2cid[t] for _, t in order]
reserve_cids = [c for c in range(1, TOTAL + 1) if c not in set(ranked_cids)]  # cid昇順
INIT = ranked_cids + reserve_cids
assert len(INIT) == TOTAL, f"INIT={len(INIT)} TOTAL={TOTAL}"

games = [{"id": c, "title": cid2title[c], "img": f"game_covers/c{c}.jpg"} for c in range(1, TOTAL + 1)]
SIG = ",".join(str(x) for x in INIT)

JS = '''const GAMES = __GAMES__;
const INIT = __INIT__;
const SIG = "__SIG__";
const RANKED = __RANKED__;
const OKEY='game_edit_grid_v2';
const $=id=>document.getElementById(id);
let dragEl=null;
function curOrder(){return [...document.querySelectorAll('#grid .cell')].map(r=>+r.dataset.id);}
function placeDivider(){
  const grid=$('grid'); const old=$('divider'); if(old) old.remove();
  const cells=[...grid.querySelectorAll('.cell')];
  if(cells.length>RANKED && cells[RANKED]){
    const d=document.createElement('div'); d.id='divider'; d.className='divider';
    d.innerHTML='▼ ここから下は <b>ランク外（'+(RANKED+1)+'位〜）</b>　／　上へドラッグで TOP'+RANKED+' 入り';
    grid.insertBefore(d, cells[RANKED]);
  }
}
function renumber(){document.querySelectorAll('#grid .cell').forEach((c,i)=>{c.querySelector('.rk').textContent=(i+1);c.classList.toggle('reserve',i>=RANKED);});placeDivider();}
function output(){const ids=curOrder();const top=ids.slice(0,RANKED),res=ids.slice(RANKED);
  $('out').value='新順位CID: '+top.join(',')+(res.length?'\\nランク外CID: '+res.join(','):'');
  localStorage.setItem(OKEY,JSON.stringify({sig:SIG,order:ids}));}
function cellHTML(g){const t=g.title.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/"/g,'&quot;');
  return `<div class="cell" draggable="true" data-id="${g.id}" title="${t}">`
    +`<span class="rk"></span><div class="ph">${t}</div>`
    +`<img loading="lazy" src="${g.img}" alt="${t}" onload="this.closest('.cell').classList.add('hascover')" onerror="this.style.display='none'">`
    +`<span class="cap">${t}</span></div>`;}
function build(orderIds){
  const byId=Object.fromEntries(GAMES.map(g=>[g.id,g]));
  const ids=(orderIds&&orderIds.length===GAMES.length&&orderIds.every(i=>byId[i]))?orderIds:INIT;
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
JS = (JS.replace("__GAMES__", json.dumps(games, ensure_ascii=False))
        .replace("__INIT__", json.dumps(INIT))
        .replace("__RANKED__", str(RANKED))
        .replace("__SIG__", SIG))
open("rank_edit.js", "w", encoding="utf-8").write(JS)

HTML = '''<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>順位を編集（TOP100＋ランク外・ドラッグ&ドロップ）</title>
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
 /* 表紙なし＝タイトル札（プレースホルダー） */
 .cell .ph{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;text-align:center;
   padding:5px;font-size:10px;font-weight:800;color:#fff;line-height:1.22;letter-spacing:.2px;
   background:linear-gradient(150deg,#8a6bd6,#c45ea0);pointer-events:none;overflow:hidden}
 .cell.hascover .ph{display:none}
 .cell .cap{position:absolute;left:0;right:0;bottom:0;padding:2px 3px;font-size:9px;font-weight:700;color:#fff;line-height:1.15;
   background:linear-gradient(transparent,rgba(0,0,0,.72));max-height:46%;overflow:hidden;pointer-events:none;display:none}
 .cell.hascover .cap{display:block}
 .cell .rk{position:absolute;top:-5px;left:-5px;min-width:20px;height:20px;padding:0 5px;border-radius:999px;z-index:3;
   background:linear-gradient(135deg,var(--blue),var(--purple));color:#fff;font-weight:800;font-size:11px;font-family:Arial;
   display:flex;align-items:center;justify-content:center;box-shadow:0 2px 4px rgba(0,0,0,.3)}
 /* ランク外ゾーンのタイル */
 .cell.reserve{filter:grayscale(.5) brightness(.96);opacity:.92}
 .cell.reserve .rk{background:linear-gradient(135deg,#9aa3b2,#c4b0d6);color:#34304a}
 .cell.reserve .ph{background:linear-gradient(150deg,#8f8aa6,#a98aa0)}
 /* TOP100 / ランク外 の区切り線 */
 .divider{flex:0 0 100%;width:100%;text-align:center;color:#6a4d8a;font-weight:800;font-size:13px;
   padding:12px 6px 4px;margin:6px 0 2px;border-top:3px dashed #b79be0}
 .divider b{color:#d6346a}
 .bar{position:fixed;left:0;right:0;bottom:0;background:rgba(255,255,255,.97);border-top:2px solid #eadcff;
   padding:10px 16px;display:flex;gap:10px;align-items:center;flex-wrap:wrap;box-shadow:0 -6px 18px rgba(58,36,86,.1);z-index:10}
 textarea{flex:1;min-width:240px;height:54px;border:2px solid #eadcff;border-radius:10px;padding:8px;font:inherit;font-size:13px}
 .btn{font:inherit;font-weight:800;border:0;border-radius:999px;padding:10px 18px;cursor:pointer;color:#fff;background:linear-gradient(135deg,var(--purple),var(--pink))}
 .btn.g{background:#eadcff;color:#6a4d8a}
</style></head><body>
<h1>✏️ 順位を編集（TOP100＋ランク外・ドラッグ&ドロップ）</h1>
<p class="hint">表紙タイルを<b>ドラッグして好きな位置へ</b>。番号は自動で振り直し。上から1位、点線より下は<b>ランク外（101位〜）</b>。<br>
ランク外から上へ運べば<b>TOP100入り</b>、下へ落とせば圏外。表紙が無い作品は<b>タイトル札</b>で表示（昇格後に表紙取得）。<br>
並べ替えるたび下に<b>「新順位CID／ランク外CID」</b>が出るので<b>「コピー」</b>して貼り付けてね。</p>
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
print(f"rank_edit.html + rank_edit.js を生成（グリッド版・固定ID・TOP{RANKED}＋ランク外={TOTAL-RANKED}・計{len(games)}作）")
