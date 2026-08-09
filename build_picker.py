#!/usr/bin/env python3
"""candidates.json から「クリックで選べる」インタラクティブ候補ピッカーを生成する。
- まだ game_covers/<順位>.jpg が無い順位のうち、候補が1つ以上あるものだけ表示
- 候補カードをクリックで選択/解除（localStorageに保持）。「なし」も選べる
- 「プロンプト生成」ボタンで採用結果(例: 8:A, 24:B, 50:なし)を出力＆コピー
ネットワーク不要。使い方: python3 build_picker.py
"""
import json, os, re, html

rank = {}
for l in open("game_ranking_draft.md", encoding="utf-8"):
    m = re.match(r'^(\d+)\.\s+(.*)$', l)
    if m:
        rank[int(m.group(1))] = m.group(2).strip()

cand = json.load(open("candidates.json", encoding="utf-8"))

have = set()
for fn in (os.listdir("game_covers") if os.path.isdir("game_covers") else []):
    m = re.match(r'^(\d+)\.jpg$', fn)
    if m and os.path.getsize(os.path.join("game_covers", fn)) > 2000:
        have.add(int(m.group(1)))

# 表示対象: 未取得 かつ 候補1つ以上
targets = sorted(int(r) for r, v in cand.items() if int(r) not in have and v)
omitted_nocand = sorted(int(r) for r, v in cand.items() if int(r) not in have and not v)

def card(r):
    title = html.escape(rank[r])
    cells = []
    for it in cand[str(r)]:
        fb = html.escape(it.get("fallback", ""))
        onerr = "if(this.dataset.fb){this.src=this.dataset.fb;this.dataset.fb='';}else{this.closest('.cand').style.display='none';}"
        cells.append(
            f'<button type="button" class="cand" data-label="{it["label"]}">'
            f'<span class="lab">{it["label"]}</span>'
            f'<img loading="lazy" src="{html.escape(it["url"])}" data-fb="{fb}" onerror="{onerr}">'
            f'<span class="src">{html.escape(it["source"])}<br><i>{html.escape(it["note"])[:38]}</i></span>'
            f'</button>')
    cells.append('<button type="button" class="cand none" data-label="なし"><span class="lab">×</span><span class="nonetxt">なし<br>(タイルのまま)</span></button>')
    return (f'<section class="g" data-rank="{r}"><h2><b>{r}位</b> {title}</h2>'
            f'<div class="row">{"".join(cells)}</div></section>')

body = "\n".join(card(r) for r in targets)
omit_note = ""
if omitted_nocand:
    lst = "、".join(f"{r}位 {html.escape(rank[r])}" for r in omitted_nocand)
    omit_note = f'<p class="omit">※ 公開APIに候補が無く、ここに出せないタイトル（手元画像のみ対応）：{lst}</p>'

out = f'''<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>カバー候補ピッカー（クリック選択）</title>
<style>
 body{{font-family:"Hiragino Kaku Gothic ProN",sans-serif;background:#f4f1fb;color:#2a1a4a;margin:0;padding:20px 20px 110px}}
 h1{{font-size:20px;margin:0 0 6px}}
 .lead{{color:#6a4d8a;font-size:13px;line-height:1.7;margin-bottom:14px}}
 .omit{{color:#a18bbf;font-size:12px;background:#fff;border-radius:10px;padding:10px 12px;margin-bottom:14px}}
 .g{{background:#fff;border-radius:14px;padding:12px 14px;margin:0 0 14px;box-shadow:0 4px 12px rgba(58,36,86,.08)}}
 .g h2{{font-size:15px;margin:0 0 10px}} .g h2 b{{color:#9b5cff}}
 .row{{display:flex;gap:12px;flex-wrap:wrap}}
 .cand{{position:relative;width:132px;text-align:center;border:2px solid #eee;border-radius:10px;padding:6px;
   background:#fafafa;cursor:pointer;font:inherit;color:inherit;transition:transform .1s,border-color .1s,box-shadow .1s}}
 .cand:hover{{transform:translateY(-3px);box-shadow:0 8px 16px rgba(58,36,86,.14)}}
 .cand .lab{{position:absolute;top:6px;left:6px;font-weight:800;color:#fff;background:#9b5cff;border-radius:6px;padding:1px 8px;z-index:2}}
 .cand img{{width:100%;height:158px;object-fit:contain;background:#fff;border-radius:6px;display:block}}
 .cand .src{{font-size:10px;color:#888;margin-top:4px;line-height:1.3;display:block}} .cand .src i{{color:#bbb;font-style:normal}}
 .cand.none{{display:flex;flex-direction:column;align-items:center;justify-content:center;width:132px;color:#bbb}}
 .cand.none .lab{{background:#bbb}} .cand.none .nonetxt{{font-size:12px;line-height:1.5}}
 .cand.sel{{border-color:#ff5ea8;background:#fff0f7;box-shadow:0 0 0 3px rgba(255,94,168,.25)}}
 .cand.sel .lab{{background:#ff5ea8}}
 .cand.sel::after{{content:"✓ 採用";position:absolute;bottom:6px;right:6px;background:#ff5ea8;color:#fff;
   font-size:10px;font-weight:800;border-radius:6px;padding:1px 6px;z-index:2}}
 .bar{{position:fixed;left:0;right:0;bottom:0;background:rgba(255,255,255,.97);border-top:2px solid #eadcff;
   padding:10px 16px;display:flex;align-items:center;gap:12px;flex-wrap:wrap;box-shadow:0 -6px 18px rgba(58,36,86,.1)}}
 .bar b{{color:#9b5cff}}
 .btn{{font:inherit;font-weight:800;color:#fff;background:linear-gradient(135deg,#9b5cff,#ff5ea8);border:0;
   border-radius:999px;padding:10px 20px;cursor:pointer}}
 .btn.sub{{background:#eadcff;color:#6a4d8a}}
 textarea{{flex:1;min-width:240px;height:46px;border:2px solid #eadcff;border-radius:10px;padding:8px;font:inherit;font-size:13px}}
</style></head><body>
<h1>🎮 カバー候補ピッカー（クリックで選択）</h1>
<p class="lead">各ゲームで正しい候補を<b>クリック</b>して選んでね（もう一度押すと解除／「なし」も選べる）。選択は自動保存。<br>
クリックするたび下のボックスに<b>採用リストが自動で出ます</b>。最後に右下の<b>「コピー」</b>でコピーしてチャットに貼り付けてください。</p>
{omit_note}
{body}
<div class="bar">
  <span>選択中: <b id="cnt">0</b> 件</span>
  <button class="btn" onclick="genPrompt()">プロンプト生成</button>
  <button class="btn sub" onclick="clearAll()">全解除</button>
  <textarea id="out" readonly placeholder="ここに採用リストが出ます（例: 8:A, 24:B, 50:なし）"></textarea>
  <button class="btn sub" onclick="copyOut()">コピー</button>
</div>
<script>
 const KEY='gamecover_picks_v1';
 let picks=JSON.parse(localStorage.getItem(KEY)||'{{}}');
 function genPrompt(){{
   const ks=Object.keys(picks).map(Number).sort((a,b)=>a-b);
   const s=ks.map(r=>r+':'+picks[r]).join(', ');
   document.getElementById('out').value = s ? ('カバー採用: '+s) : '';
 }}
 function save(){{ localStorage.setItem(KEY,JSON.stringify(picks)); upd(); genPrompt(); }}
 function upd(){{
   document.querySelectorAll('.g').forEach(g=>{{
     const r=g.dataset.rank, sel=picks[r];
     g.querySelectorAll('.cand').forEach(c=>c.classList.toggle('sel', sel!=null && c.dataset.label===sel));
   }});
   document.getElementById('cnt').textContent=Object.keys(picks).length;
 }}
 // イベント委譲: 候補(img/spanを含む)のどこをクリックしても拾う
 document.addEventListener('click',e=>{{
   const c=e.target.closest('.cand'); if(!c) return;
   const g=c.closest('.g'); if(!g) return;
   const r=g.dataset.rank, lab=c.dataset.label;
   if(picks[r]===lab) delete picks[r]; else picks[r]=lab;
   save();
 }});
 function copyOut(){{
   const t=document.getElementById('out'); genPrompt();
   if(!t.value){{ alert('まだ何も選ばれていません'); return; }}
   t.removeAttribute('readonly'); t.select();
   try{{navigator.clipboard.writeText(t.value);}}catch(e){{}}
   try{{document.execCommand('copy');}}catch(e){{}}
   t.setAttribute('readonly','');
 }}
 function clearAll(){{ if(confirm('全部の選択を解除する？')){{picks={{}};save();}} }}
 upd(); genPrompt();
</script>
</body></html>'''
open("covers_candidates.html", "w", encoding="utf-8").write(out)
print(f"表示対象 {len(targets)} 本 / 候補ゼロで非表示 {len(omitted_nocand)} 本")
print("covers_candidates.html を更新（クリック選択版）")
