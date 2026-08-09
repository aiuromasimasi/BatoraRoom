#!/usr/bin/env python3
"""ペア比較(マージソート)で順位を再整理する一時UIを生成する（ティア＝10位ごとのバンド内ソート版）。
- 1-10 / 11-20 / ... / 91-100 の各グループ内だけで「どっちが思い入れある？」を比較ソート
  （グループ間は移動しないので比較回数を約230〜250回に抑える）
- JSは sorter.js に分離（インラインscript禁止のCSP環境でも動くように）
- 回答は localStorage に保存（途中再開OK／1つ戻すOK）
- 完了で「新順位ID: ...」を出力（ID=現在の順位）。貼り戻すと並び替え
使い方: python3 build_sorter.py
"""
import json, re

_lines = open("game_ranking_draft.md", encoding="utf-8").read().split("\n")
title2cid = {}; _c = 0
for l in _lines:
    if l.startswith("---"): break
    if l.startswith("- "):
        _c += 1; title2cid[l[2:].strip()] = _c
rank = {}
for l in _lines:
    m = re.match(r'^(\d+)\.\s+(.*)$', l)
    if m:
        rank[int(m.group(1))] = m.group(2).strip()

# id=固定ID(cid・出力/比較用), pos=現在順位(バンド分け用), img=固定IDカバー
games = [{"id": title2cid[rank[r]], "pos": r, "title": rank[r], "img": f"game_covers/c{title2cid[rank[r]]}.jpg"} for r in sorted(rank)]
BANDS = [[lo, lo + 9] for lo in range(1, 101, 10)]  # 現順位(pos)で 1-10/11-20/.../91-100

JS = '''const GAMES = __GAMES__;
const BANDS = __BANDS__;
const PKEY='game_sort_prefs_v3', OKEY='game_sort_order_v3';
let prefs = JSON.parse(localStorage.getItem(PKEY)||'{}');
let order = JSON.parse(localStorage.getItem(OKEY)||'[]');
const keyOf=(a,b)=>Math.min(a,b)+'-'+Math.max(a,b);
let pending=null;
const EST=240;
const $=id=>document.getElementById(id);
function save(){localStorage.setItem(PKEY,JSON.stringify(prefs));localStorage.setItem(OKEY,JSON.stringify(order));}
function progress(){const n=Object.keys(prefs).length;$('cnt').textContent=n;$('pi').style.width=Math.min(100,Math.round(n/EST*100))+'%';}
function setBand(lo,hi,bi){$('band').textContent=lo+'〜'+hi+'位 グループを整理中（'+(bi+1)+'/'+BANDS.length+'）';}
function render(a,b){
  $('Limg').src=a.img;$('Lnm').textContent=a.title;$('Lrk').textContent='現在 '+a.pos+'位';
  $('Rimg').src=b.img;$('Rnm').textContent=b.title;$('Rrk').textContent='現在 '+b.pos+'位';
  $('undo').disabled = order.length===0;
}
function compare(a,b){
  const k=keyOf(a.id,b.id);
  if(prefs[k]!=null) return Promise.resolve(prefs[k]);
  return new Promise(res=>{pending={a,b,k,res};render(a,b);});
}
function choose(winnerId){
  if(!pending)return; const {k,res}=pending; prefs[k]=winnerId; order.push(k); pending=null; save(); progress(); res(winnerId);
}
async function mergeSort(arr){
  if(arr.length<=1)return arr;
  const mid=arr.length>>1;
  const L=await mergeSort(arr.slice(0,mid));
  const R=await mergeSort(arr.slice(mid));
  const out=[];let i=0,j=0;
  while(i<L.length&&j<R.length){const w=await compare(L[i],R[j]);if(w===L[i].id)out.push(L[i++]);else out.push(R[j++]);}
  while(i<L.length)out.push(L[i++]);while(j<R.length)out.push(R[j++]);return out;
}
function finish(sorted){
  $('game').classList.add('hide');
  $('result').classList.remove('hide');
  $('out').value='新順位CID: '+sorted.map(g=>g.id).join(',');
  $('list').innerHTML=sorted.map((g,i)=>'<li>'+g.title+' <span style="color:#bbb">(現'+g.pos+'位)</span></li>').join('');
}
// 途中でも、今ある回答だけで並べ替えを出力（回答収集と同じマージソート構造で再生。未回答ペアは現状順位で補完）
function msSync(arr){
  if(arr.length<=1)return arr;
  const mid=arr.length>>1;const L=msSync(arr.slice(0,mid)),R=msSync(arr.slice(mid));
  const out=[];let i=0,j=0;
  while(i<L.length&&j<R.length){const a=L[i],b=R[j];const k=keyOf(a.id,b.id);
    const w=(prefs[k]!=null)?prefs[k]:(a.pos<b.pos?a.id:b.id);
    if(w===a.id)out.push(L[i++]);else out.push(R[j++]);}
  while(i<L.length)out.push(L[i++]);while(j<R.length)out.push(R[j++]);return out;
}
function exportNow(){
  const result=[];
  for(const [lo,hi] of BANDS){const items=GAMES.filter(g=>g.pos>=lo&&g.pos<=hi);result.push(...msSync(items));}
  $('expbox').classList.remove('hide');
  $('out2').value='新順位ID: '+result.map(g=>g.id).join(',');
  const n=Object.keys(prefs).length;
  $('expnote').textContent='（'+n+'回ぶんの回答を反映。未回答ペアは現状順位のまま）';
}
async function run(){
  const result=[];
  for(let bi=0;bi<BANDS.length;bi++){
    const [lo,hi]=BANDS[bi]; setBand(lo,hi,bi);
    const items=GAMES.filter(g=>g.pos>=lo&&g.pos<=hi);
    const sorted=await mergeSort(items);
    result.push(...sorted);
  }
  finish(result);
}
function init(){
  $('L').onclick=()=>{if(pending)choose(pending.a.id);};
  $('R').onclick=()=>{if(pending)choose(pending.b.id);};
  document.addEventListener('keydown',e=>{if(e.key==='ArrowLeft'&&pending)choose(pending.a.id);if(e.key==='ArrowRight'&&pending)choose(pending.b.id);});
  $('undo').onclick=()=>{if(order.length===0)return;const k=order.pop();delete prefs[k];save();location.reload();};
  const reset=()=>{if(confirm('回答を全部消して最初から？')){localStorage.removeItem(PKEY);localStorage.removeItem(OKEY);location.reload();}};
  $('reset').onclick=reset; $('reset2').onclick=reset;
  const cp=id=>{const t=$(id);t.removeAttribute('readonly');t.select();try{navigator.clipboard.writeText(t.value)}catch(e){}try{document.execCommand('copy')}catch(e){}t.setAttribute('readonly','');};
  $('copy').onclick=()=>cp('out');
  $('exp').onclick=exportNow; $('copy2').onclick=()=>cp('out2');
  progress();
  run();
}
if(document.readyState!=='loading') init(); else document.addEventListener('DOMContentLoaded', init);
'''
JS = JS.replace("__GAMES__", json.dumps(games, ensure_ascii=False)).replace("__BANDS__", json.dumps(BANDS))
open("sorter.js", "w", encoding="utf-8").write(JS)

HTML = '''<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>順位 再整理（ティア内）— どっちが思い入れある？</title>
<style>
 :root{--pink:#ff5ea8;--purple:#9b5cff;--blue:#36c5ff;--ink:#2a1a4a}
 *{box-sizing:border-box}
 body{font-family:"Hiragino Kaku Gothic ProN",sans-serif;color:var(--ink);margin:0;
   background:linear-gradient(135deg,#ffd6ec,#d6e4ff,#d9fff4);min-height:100vh;padding:18px}
 h1{font-size:20px;text-align:center;margin:4px 0 2px}
 .band{text-align:center;font-weight:800;color:var(--blue);margin:2px 0;font-size:14px}
 .q{text-align:center;font-weight:800;color:var(--purple);margin:6px 0 4px;font-size:16px}
 .prog{max-width:760px;margin:0 auto 14px;text-align:center;color:#6a4d8a;font-size:13px}
 .bar{height:10px;background:#fff;border-radius:999px;overflow:hidden;margin:6px auto;max-width:520px;box-shadow:inset 0 1px 3px rgba(0,0,0,.1)}
 .bar>i{display:block;height:100%;background:linear-gradient(90deg,var(--purple),var(--pink));width:0}
 .arena{display:flex;gap:18px;justify-content:center;align-items:stretch;max-width:760px;margin:0 auto;flex-wrap:wrap}
 .pick{flex:1;min-width:240px;max-width:340px;background:#fff;border:4px solid #fff;border-radius:22px;padding:14px;
   cursor:pointer;text-align:center;box-shadow:0 10px 26px rgba(58,36,86,.18);transition:transform .12s,box-shadow .12s}
 .pick:hover{transform:translateY(-6px) scale(1.02);box-shadow:0 18px 36px rgba(58,36,86,.3);border-color:var(--pink)}
 .pick .cv{width:100%;aspect-ratio:3/4;border-radius:14px;overflow:hidden;background:linear-gradient(150deg,#c9d6ff,#a18bbf);display:flex;align-items:center;justify-content:center}
 .pick .cv img{width:100%;height:100%;object-fit:contain}
 .pick .nm{font-weight:800;margin-top:10px;font-size:16px;line-height:1.35;min-height:2.6em;display:flex;align-items:center;justify-content:center}
 .pick .rk{color:#a18bbf;font-size:12px;font-weight:700}
 .vs{display:flex;align-items:center;font-family:Arial;font-weight:900;color:var(--pink);font-size:24px}
 .ctl{max-width:760px;margin:16px auto;display:flex;gap:10px;justify-content:center;flex-wrap:wrap}
 .btn{font:inherit;font-weight:800;border:0;border-radius:999px;padding:9px 18px;cursor:pointer;color:#fff;background:var(--blue)}
 .btn.g{background:#eadcff;color:#6a4d8a} .btn:disabled{opacity:.4;cursor:default}
 .done{max-width:760px;margin:0 auto;background:#fff;border-radius:18px;padding:16px;box-shadow:0 8px 20px rgba(58,36,86,.12)}
 .done h2{margin:0 0 8px;color:var(--purple)}
 textarea{width:100%;height:80px;border:2px solid #eadcff;border-radius:10px;padding:8px;font:inherit;font-size:13px}
 ol{padding-left:22px;line-height:1.7;max-height:340px;overflow:auto;border:1px solid #eee;border-radius:10px;padding:10px 10px 10px 30px;margin-top:10px}
 .hide{display:none}
 .hint{max-width:760px;margin:0 auto 10px;color:#6a4d8a;font-size:12px;text-align:center;line-height:1.6}
</style></head><body>
<h1>🎮 順位を再整理（ティア内）：どっちが思い入れある？</h1>
<p class="hint">10位ごとのグループ内だけで並べ替えます（グループ間の移動なし）。<b>より思い入れがある方をクリック</b>。キーボード <b>&larr;</b>/<b>&rarr;</b> もOK。回答は自動保存＝途中で閉じてもOK。</p>
<div id="game">
  <div class="band" id="band"></div>
  <div class="q">どっちが思い入れある？</div>
  <div class="prog"><span id="cnt">0</span> 回比較（目安 約240回） <div class="bar"><i id="pi"></i></div></div>
  <div class="arena">
    <div class="pick" id="L"><div class="cv"><img id="Limg" alt=""></div><div class="nm" id="Lnm"></div><div class="rk" id="Lrk"></div></div>
    <div class="vs">VS</div>
    <div class="pick" id="R"><div class="cv"><img id="Rimg" alt=""></div><div class="nm" id="Rnm"></div><div class="rk" id="Rrk"></div></div>
  </div>
  <div class="ctl">
    <button class="btn g" id="undo">&larr; 1つ戻す</button>
    <button class="btn" id="exp">📋 今の回答で順位を出力</button>
    <button class="btn g" id="reset">最初からやり直す</button>
  </div>
  <div id="expbox" class="done hide">
    <p style="margin:0 0 6px">📋 途中結果 — この「新順位ID」をコピーして貼り付けてね <span id="expnote" style="color:#a18bbf;font-size:12px"></span></p>
    <textarea id="out2" readonly></textarea>
    <div class="ctl" style="margin:8px auto 0"><button class="btn" id="copy2">コピー</button></div>
  </div>
</div>
<div id="result" class="done hide">
  <h2>✅ 並び替え完了！</h2>
  <p>下の「新順位ID」をコピーしてチャットに貼り付けてね（こちらで順位＆カバー画像を並び替えます）。</p>
  <textarea id="out" readonly></textarea>
  <div class="ctl"><button class="btn" id="copy">コピー</button><button class="btn g" id="reset2">やり直す</button></div>
  <ol id="list"></ol>
</div>
<script src="sorter.js"></script>
</body></html>'''
open("sorter.html", "w", encoding="utf-8").write(HTML)
print(f"sorter.html + sorter.js を生成（ティア内ソート版・{len(games)}作・{len(BANDS)}グループ）")
