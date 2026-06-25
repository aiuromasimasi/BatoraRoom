#!/usr/bin/env python3
"""100位→1位 カウントダウン・ムービー movie.html + movie.js を生成。
- 合計約3分(180秒)に自動配分。レイアウト4種を「レイアウト」ボタンで巡回切替：
  標準 / 全面カバー(案F) / シネマ(案G:レターボックス＋順位フラッシュ) / フィード(案H:連続スクロール)
- 横16:9 ⇄ 縦9:16、再生/一時停止/前後/速度/全画面、BGM任意(movie_bgm.mp3)
- レーダーは中心から外へ伸びるアニメ
使い方: python3 build_movie.py
"""
import re, json, csv, os

lines = open("game_ranking_draft.md", encoding="utf-8").read().split("\n")
title2cid = {}; c = 0
for l in lines:
    if l.startswith("---"): break
    if l.startswith("- "):
        c += 1; title2cid[l[2:].strip()] = c
rank = {}
for l in lines:
    m = re.match(r'^(\d+)\.\s+(.*)$', l)
    if m: rank[int(m.group(1))] = m.group(2).strip()
gd = {}
if os.path.exists("games_data.csv"):
    with open("games_data.csv", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            mm = re.search(r'c(\d+)\.jpg', row.get("画像", ""))
            if not mm: continue
            def _n(x):
                x = (x or "").strip(); return int(x) if x.isdigit() else None
            gd[int(mm.group(1))] = {"intro": row.get("ゲーム紹介","").strip(),"genre": row.get("ジャンル","").strip(),
                "year": row.get("発売年","").strip(),"m":_n(row.get("思い入れ度")),"i":_n(row.get("衝撃度")),
                "f":_n(row.get("面白さ")),"r":_n(row.get("ストーリー")),"mu":_n(row.get("音楽・サウンド"))}
games = []
for r in sorted(rank):
    cid = title2cid[rank[r]]; d = gd.get(cid, {})
    games.append({"rank": r, "title": rank[r], "img": f"game_covers/c{cid}.jpg",
        "intro": d.get("intro",""), "genre": d.get("genre",""), "year": d.get("year",""),
        "m": d.get("m"), "i": d.get("i"), "f": d.get("f"), "r": d.get("r"), "mu": d.get("mu")})
GAMES_JSON = json.dumps(games, ensure_ascii=False)

JS = '''const GAMES = __GAMES__;
const byRank = {}; GAMES.forEach(g=>byRank[g.rank]=g);
const AX=[{k:'m',a:-90,c:'#ff5ea8',l:'思'},{k:'i',a:-18,c:'#ff8a3d',l:'衝'},{k:'f',a:54,c:'#36c5ff',l:'面'},{k:'r',a:126,c:'#1bbf9a',l:'物'},{k:'mu',a:198,c:'#9b5cff',l:'音'}];
function radar(d){
  const R=80, rad=a=>a*Math.PI/180, P=(v,a)=>[((v||0)/10*R*Math.cos(rad(a))).toFixed(1),((v||0)/10*R*Math.sin(rad(a))).toFixed(1)];
  const ring=s=>AX.map(x=>[(R*s*Math.cos(rad(x.a))).toFixed(1),(R*s*Math.sin(rad(x.a))).toFixed(1)].join(',')).join(' ');
  const grid=[1,.66,.33].map(s=>`<polygon points="${ring(s)}" fill="none" stroke="rgba(255,255,255,.3)" stroke-width="1.2"/>`).join('');
  const ax=AX.map(x=>`<line x1="0" y1="0" x2="${(R*Math.cos(rad(x.a))).toFixed(1)}" y2="${(R*Math.sin(rad(x.a))).toFixed(1)}" stroke="rgba(255,255,255,.25)" stroke-width="1.2"/>`).join('');
  const V=AX.map(x=>P(d[x.k],x.a)), poly=V.map(p=>p.join(',')).join(' ');
  const dots=V.map((p,k)=>`<circle cx="${p[0]}" cy="${p[1]}" r="4.5" fill="${AX[k].c}" stroke="#fff" stroke-width="1"/>`).join('');
  const lab=AX.map(x=>{const lr=R+19;return `<text x="${(lr*Math.cos(rad(x.a))).toFixed(1)}" y="${(lr*Math.sin(rad(x.a))+5).toFixed(1)}" text-anchor="middle" font-size="16" font-weight="800" fill="${x.c}" stroke="rgba(0,0,0,.4)" stroke-width="2.8" paint-order="stroke">${x.l}${d[x.k]==null?'－':d[x.k]}</text>`;}).join('');
  return `<svg viewBox="-114 -110 228 224" class="radar"><defs><radialGradient id="sw"><stop offset="0" stop-color="#fff" stop-opacity=".45"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient></defs>
    ${grid}${ax}<g class="sweep"><path d="M0,0 L0,-${R} A${R},${R} 0 0 1 ${(R*Math.sin(rad(46))).toFixed(1)},-${(R*Math.cos(rad(46))).toFixed(1)} Z" fill="url(#sw)"/></g>
    <g style="transform-origin:0px 0px;animation:grow .9s cubic-bezier(.2,1,.3,1) backwards"><polygon points="${poly}" fill="rgba(255,255,255,.30)" stroke="#fff" stroke-width="3" style="filter:drop-shadow(0 0 8px rgba(255,255,255,.9))"/>${dots}</g>${lab}</svg>`;
}
function tierOf(r){return r<=1?'👑 第 1 位':r<=3?'BEST 3':r<=10?'TOP 10':r<=20?'BEST 20':r<=50?'BEST 50':'BEST 100';}
const BANNERS={100:['BEST 100','100位 → 51位'],50:['BEST 50','50位 → 21位'],20:['BEST 20','20位 → 11位'],10:['TOP 10','10位 → 4位'],3:['BEST 3','表彰台'],1:['👑 No.1','頂点']};
const steps=[];
for(let r=100;r>=1;r--){ if(BANNERS[r]) steps.push({t:'b',r}); steps.push({t:'g',r}); }
const TOTAL=180000;
const WT=s=>{ if(s.t==='b') return 0.7; const r=s.r; return r===1?3.0:r<=3?2.0:r<=10?1.5:r<=20?1.1:1.0; };
const sumW=steps.reduce((a,s)=>a+WT(s),0);
steps.forEach(s=>s.base=WT(s)/sumW*TOTAL);

const stage=document.getElementById('stage');
let si=0, playing=true, mult=1, LM=0, timer=null, feedRAF=null, feedStart=null;
const LMN=['標準','全面カバー','シネマ(案G)','フィード(案H)'];
function dur(s){return s.base*mult;}
function esc(s){return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;');}
function confetti(n){const w=document.createElement('div');w.className='cf';const cols=['#ff5ea8','#9b5cff','#36c5ff','#ffd23f','#3ff2c2','#ff8a3d'];
  for(let i=0;i<n;i++){const s=document.createElement('span');s.style.left=(Math.random()*100).toFixed(1)+'%';s.style.background=cols[i%cols.length];
    s.style.animationDelay=(Math.random()*.5).toFixed(2)+'s';s.style.animationDuration=(2+Math.random()*1.6).toFixed(2)+'s';w.appendChild(s);}
  stage.appendChild(w);setTimeout(()=>w.remove(),4200);}
function gameHTML(g,r,d){
  const rated=g.m!=null&&g.i!=null&&g.f!=null;
  const meta=[g.genre,(g.year?g.year+'年':'')].filter(Boolean).join(' ・ ');
  if(LM===1){ // 全面カバー(案F)
    return `<div class="slide full ${r===1?'no1':''}"><img class="bg" src="${g.img}" alt="" onerror="this.style.opacity=0" style="animation-duration:${(d/1000).toFixed(1)}s">
      <div class="scrim"></div><div class="rkF">${r}<span>位</span></div><div class="tierF">${tierOf(r)}</div>
      <div class="botF"><div class="tiF">${esc(g.title)}</div><div class="metaF">${esc(meta)}</div><div class="introF">${esc(g.intro)}</div></div>
      ${rated?'<div class="radF">'+radar(g)+'</div>':''}</div>`;
  }
  if(LM===2){ // シネマ(案G)
    return `<div class="slide cine ${r===1?'no1':''}"><div class="lb t"></div><div class="lb b"></div><div class="flash"></div>
      <div class="cineWrap"><div class="cineRk">${r}<span>位</span></div>
        <div class="cineCv"><img src="${g.img}" alt="" onerror="this.style.opacity=0"></div>
        <div class="cineInfo"><div class="tierC">${tierOf(r)}</div><div class="tiC">${esc(g.title)}</div><div class="metaC">${esc(meta)}</div>${rated?'<div class="radC">'+radar(g)+'</div>':''}</div>
      </div></div>`;
  }
  return `<div class="slide ${r===1?'no1':''}"><div class="rk">${r}<span class="rku">位</span></div>
    <div class="mid"><div class="cvwrap"><div class="cvglow"></div><img class="cv" src="${g.img}" alt="" onerror="this.style.opacity=0"></div></div>
    <div class="info"><div class="tier">${tierOf(r)}</div><div class="ti">${esc(g.title)}</div>
      <div class="meta">${esc(meta)}</div><div class="intro">${esc(g.intro)}</div>${rated?'<div class="rwrap">'+radar(g)+'</div>':''}</div></div>`;
}
function render(s){
  if(s.t==='b'){const [a,b]=BANNERS[s.r];stage.innerHTML=`<div class="banner"><div class="btxt">${a}</div><div class="bsub">${b}</div></div>`;return;}
  const g=byRank[s.r]; stage.innerHTML=gameHTML(g,s.r,dur(s));
  if(s.r===1) confetti(110); else if(s.r<=3) confetti(50);
}
function step(){ if(LM===3) return; render(steps[si]); clearTimeout(timer); if(playing) timer=setTimeout(()=>{ if(si<steps.length-1){si++;step();} else {playing=false;updateBtn();} }, dur(steps[si])); updateProg(); }
function updateProg(){const s=steps[si];document.getElementById('prog').textContent=(LM===3?'フィード再生中':((s.t==='g'?s.r+'位':'—')+' / 残り'+Math.max(0,steps.length-1-si)));}
function updateBtn(){document.getElementById('pp').textContent=playing?'⏸':'▶';}
function play(){if(LM===3)return;playing=true;updateBtn();step();}
function pause(){playing=false;clearTimeout(timer);updateBtn();}
// 案H フィード
function buildFeed(){
  const list=GAMES.slice().sort((a,b)=>b.rank-a.rank);
  stage.innerHTML='<div class="feed" id="feed">'+list.map(g=>`<div class="frow"><div class="frk">${g.rank}<small>位</small></div><div class="fcv"><img src="${g.img}" onerror="this.style.opacity=0"></div><div class="fti">${esc(g.title)}</div></div>`).join('')+'</div>';
  const feed=document.getElementById('feed'), rows=[...feed.children]; feedStart=null;
  const total=TOTAL*mult;
  function fa(t){ if(LM!==3) return; if(feedStart==null)feedStart=t; const p=Math.min(1,(t-feedStart)/total);
    const max=Math.max(1,feed.scrollHeight-stage.clientHeight); feed.style.transform='translateY('+(-max*p).toFixed(1)+'px)';
    const fi=Math.round(p*(rows.length-1)); rows.forEach((r,k)=>r.classList.toggle('focus',k===fi));
    if(p<1) feedRAF=requestAnimationFrame(fa); }
  feedRAF=requestAnimationFrame(fa);
}
document.getElementById('pp').onclick=()=>playing?pause():play();
document.getElementById('rs').onclick=()=>{ if(LM===3){cancelAnimationFrame(feedRAF);buildFeed();return;} si=0;play();};
document.getElementById('nx').onclick=()=>{if(LM===3)return;if(si<steps.length-1){si++;pause();render(steps[si]);updateProg();}};
document.getElementById('pv').onclick=()=>{if(LM===3)return;if(si>0){si--;pause();render(steps[si]);updateProg();}};
document.getElementById('sp').onchange=e=>{mult=+e.target.value;};
document.getElementById('lm').onclick=()=>{ LM=(LM+1)%4; document.getElementById('lm').textContent=LMN[LM]; cancelAnimationFrame(feedRAF);
  if(LM===3){ pause(); buildFeed(); updateProg(); } else { render(steps[si]); updateProg(); } };
document.getElementById('or').onclick=()=>{const f=document.getElementById('frame');f.classList.toggle('vert');document.getElementById('or').textContent=f.classList.contains('vert')?'縦 9:16':'横 16:9';if(LM===3){cancelAnimationFrame(feedRAF);buildFeed();}};
document.getElementById('fs').onclick=()=>{const f=document.getElementById('frame');(f.requestFullscreen||f.webkitRequestFullscreen||(()=>{})).call(f);};
const bgm=document.getElementById('bgm');
document.getElementById('mu').onclick=()=>{if(bgm.paused){bgm.play().catch(()=>{});document.getElementById('mu').textContent='🔊';}else{bgm.pause();document.getElementById('mu').textContent='🔇';}};
updateBtn(); step();
'''
JS = JS.replace("__GAMES__", GAMES_JSON)
open("movie.js", "w", encoding="utf-8").write(JS)

HTML = '''<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>思い入れのあるゲーム ランキング100 ✦ カウントダウン</title>
<link href="https://fonts.googleapis.com/css2?family=Mochiy+Pop+One&family=Baloo+2:wght@800&family=M+PLUS+Rounded+1c:wght@700;800&display=swap" rel="stylesheet">
<style>
  :root{--pink:#ff5ea8;--purple:#9b5cff;--blue:#36c5ff;--gold:#ffb800;--mint:#3ff2c2;--orange:#ff8a3d}
  *{margin:0;padding:0;box-sizing:border-box}
  body{font-family:"M PLUS Rounded 1c",sans-serif;background:#160d2a;min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px;padding:12px;color:#fff;overflow:hidden}
  #frame{position:relative;width:min(98vw,calc(90vh*16/9));aspect-ratio:16/9;border-radius:20px;overflow:hidden;box-shadow:0 24px 70px rgba(0,0,0,.6);border:3px solid rgba(255,255,255,.14)}
  #frame.vert{width:min(98vw,calc(90vh*9/16));aspect-ratio:9/16}
  #stage{position:absolute;inset:0;background:linear-gradient(135deg,#ff5ea8,#9b5cff,#36c5ff,#3ff2c2);background-size:400% 400%;animation:bg 16s ease infinite;overflow:hidden}
  @keyframes bg{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
  @keyframes spin{to{transform:rotate(360deg)}}
  @keyframes grow{from{transform:scale(0)}to{transform:scale(1)}}
  .banner{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:0 6%;animation:bpop .55s cubic-bezier(.2,1.4,.3,1)}
  @keyframes bpop{from{transform:scale(.4);opacity:0}to{transform:scale(1);opacity:1}}
  .btxt{font-family:"Mochiy Pop One";font-size:clamp(30px,6.4vw,84px);line-height:1.05;color:#fff;text-shadow:0 5px 0 rgba(0,0,0,.18),0 0 30px rgba(255,255,255,.6);white-space:nowrap}
  .bsub{font-weight:800;font-size:clamp(15px,2.6vw,28px);margin-top:8px;letter-spacing:2px}
  /* 標準 */
  .slide{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;gap:2%;padding:2.5% 3%}
  .rk{flex:none;font-family:"Baloo 2";font-weight:800;font-size:clamp(80px,22vh,320px);line-height:.82;color:#fff;text-shadow:0 7px 0 rgba(0,0,0,.2),0 0 34px rgba(255,255,255,.55);animation:rkin .55s cubic-bezier(.2,1.5,.3,1) backwards}
  .rk .rku{font-size:.34em;margin-left:2px}
  @keyframes rkin{from{transform:scale(2.4);opacity:0;filter:blur(6px)}to{transform:scale(1);opacity:1;filter:none}}
  .mid{flex:none;animation:cvin .6s cubic-bezier(.2,1.2,.3,1) backwards}
  @keyframes cvin{from{transform:scale(.6) rotate(-4deg);opacity:0}to{transform:none;opacity:1}}
  .cvwrap{position:relative;height:88%;aspect-ratio:3/4;border-radius:18px;overflow:hidden;border:5px solid #fff;box-shadow:0 18px 50px rgba(0,0,0,.5)}
  #frame.vert .cvwrap{height:46vh}
  .cvglow{position:absolute;inset:-30%;background:conic-gradient(from 0deg,var(--gold),var(--pink),var(--purple),var(--blue),var(--mint),var(--gold));animation:spin 8s linear infinite;opacity:.5;z-index:0}
  .cv{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;z-index:1}
  .info{flex:1;max-width:44%;display:flex;flex-direction:column;gap:10px;animation:infin .6s ease .12s backwards}
  @keyframes infin{from{transform:translateY(24px);opacity:0}to{transform:none;opacity:1}}
  .tier{align-self:flex-start;font-weight:800;font-size:clamp(13px,2vw,22px);background:rgba(255,255,255,.25);padding:5px 18px;border-radius:999px}
  .ti{font-family:"Mochiy Pop One";font-size:clamp(24px,3.8vw,56px);line-height:1.15;text-shadow:0 3px 10px rgba(0,0,0,.35)}
  .meta{font-weight:800;font-size:clamp(14px,2vw,26px);opacity:.95}
  .intro{font-weight:700;font-size:clamp(13px,1.8vw,22px);line-height:1.55;opacity:.96}
  .rwrap{margin-top:2px}.radar{width:clamp(200px,22vw,320px)}
  .sweep{transform-origin:0 0;animation:spin 3s linear infinite}
  #frame.vert .slide{flex-direction:column;gap:1%;padding:4% 5%}
  #frame.vert .info{max-width:92%;text-align:center;align-items:center}
  #frame.vert .tier{align-self:center}
  #frame.vert .rk{font-size:clamp(64px,12vh,180px)}
  .no1 .rk{color:var(--gold);text-shadow:0 0 44px rgba(255,184,0,.9),0 7px 0 rgba(0,0,0,.2)}
  .no1 .cvwrap{border-color:var(--gold);box-shadow:0 0 0 6px rgba(255,184,0,.5),0 20px 60px rgba(0,0,0,.5)}
  /* 全面カバー(案F) */
  .slide.full{padding:0}
  .slide.full .bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;transform-origin:center;animation:ken linear forwards}
  @keyframes ken{from{transform:scale(1.03)}to{transform:scale(1.18)}}
  .slide.full .scrim{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.5) 0%,rgba(0,0,0,0) 26%,rgba(0,0,0,0) 42%,rgba(0,0,0,.86) 100%)}
  .rkF{position:absolute;top:2.5%;left:3.5%;font-family:"Baloo 2";font-weight:800;font-size:clamp(80px,21vh,300px);line-height:.85;color:#fff;text-shadow:0 4px 22px rgba(0,0,0,.85),0 0 30px rgba(0,0,0,.5);animation:rkin .55s cubic-bezier(.2,1.5,.3,1) backwards}
  .rkF span{font-size:.34em}
  .tierF{position:absolute;top:4%;right:3.5%;font-weight:800;font-size:clamp(14px,2.4vw,28px);background:rgba(0,0,0,.5);padding:6px 18px;border-radius:999px;color:#fff}
  .botF{position:absolute;left:3.5%;right:27%;bottom:5%;color:#fff;text-shadow:0 3px 16px rgba(0,0,0,.95);animation:infin .6s ease .12s backwards}
  .tiF{font-family:"Mochiy Pop One";font-size:clamp(18px,2.4vw,34px);line-height:1.2}
  .metaF{font-weight:800;font-size:clamp(13px,1.8vw,22px);margin-top:6px;opacity:.95}
  .introF{font-weight:700;font-size:clamp(13px,1.8vw,22px);margin-top:5px;max-width:96%;line-height:1.5}
  .radF{position:absolute;right:2.5%;bottom:4%;background:rgba(0,0,0,.42);border-radius:18px;padding:6px}
  .radF .radar{width:clamp(160px,18vw,260px)}
  #frame.vert .botF{right:3.5%}#frame.vert .radF{top:13%;bottom:auto;right:3.5%}#frame.vert .radF .radar{width:clamp(120px,28vw,190px)}
  .full.no1 .rkF{color:var(--gold);text-shadow:0 0 44px rgba(255,184,0,.95),0 4px 18px rgba(0,0,0,.8)}
  /* シネマ(案G) */
  .slide.cine{padding:0;display:flex;align-items:center;justify-content:center}
  .cine .lb{position:absolute;left:0;right:0;height:11%;background:#000;z-index:3;animation:lbin .5s ease backwards}
  .cine .lb.t{top:0}.cine .lb.b{bottom:0}
  @keyframes lbin{from{height:50%}to{}}
  .cine .flash{position:absolute;inset:0;background:#fff;z-index:4;opacity:0;animation:fl .5s ease forwards;pointer-events:none}
  @keyframes fl{0%{opacity:.85}100%{opacity:0}}
  .cineWrap{display:flex;align-items:center;justify-content:center;gap:4%;width:100%;padding:0 6%}
  .cineRk{font-family:"Baloo 2";font-weight:800;font-size:clamp(70px,20vh,280px);line-height:.85;color:#fff;text-shadow:0 0 34px rgba(255,255,255,.6),0 6px 0 rgba(0,0,0,.25);animation:flashin .6s cubic-bezier(.2,1.6,.3,1) backwards}
  .cineRk span{font-size:.32em}
  @keyframes flashin{from{transform:scale(2.6);opacity:0;filter:blur(8px)}to{transform:scale(1);opacity:1;filter:none}}
  .cineCv{flex:none;height:66%;aspect-ratio:3/4;border-radius:14px;overflow:hidden;border:4px solid #fff;box-shadow:0 16px 44px rgba(0,0,0,.6);animation:slidein .6s cubic-bezier(.2,1.2,.3,1) .15s backwards}
  .cineCv img{width:100%;height:100%;object-fit:cover}
  @keyframes slidein{from{transform:translateX(80px);opacity:0}to{transform:none;opacity:1}}
  .cineInfo{max-width:34%;animation:infin .6s ease .3s backwards}
  .tierC{display:inline-block;font-weight:800;font-size:clamp(12px,1.8vw,20px);background:rgba(255,255,255,.22);padding:4px 14px;border-radius:999px}
  .tiC{font-family:"Mochiy Pop One";font-size:clamp(20px,2.8vw,40px);line-height:1.15;margin-top:8px;text-shadow:0 3px 10px rgba(0,0,0,.4)}
  .metaC{font-weight:800;font-size:clamp(13px,1.7vw,20px);margin-top:6px;opacity:.95}
  .radC .radar{width:clamp(150px,16vw,230px);margin-top:4px}
  #frame.vert .cineWrap{flex-direction:column;gap:2%}#frame.vert .cineInfo{max-width:88%;text-align:center}#frame.vert .cineCv{height:38vh}
  /* フィード(案H) */
  .feed{position:absolute;left:0;right:0;top:0;display:flex;flex-direction:column;gap:1.4vh;padding:46vh 7%;will-change:transform}
  .frow{display:flex;align-items:center;gap:3%;opacity:.35;transform:scale(.82);transition:opacity .35s,transform .35s}
  .frow.focus{opacity:1;transform:scale(1.06)}
  .frow .frk{flex:none;font-family:"Baloo 2";font-weight:800;font-size:clamp(30px,6vw,84px);min-width:2.2em;text-align:right;color:#fff;text-shadow:0 3px 0 rgba(0,0,0,.2)}
  .frow .frk small{font-size:.4em}
  .frow .fcv{flex:none;width:clamp(64px,10vw,130px);aspect-ratio:3/4;border-radius:10px;overflow:hidden;border:3px solid #fff;box-shadow:0 10px 26px rgba(0,0,0,.45)}
  .frow .fcv img{width:100%;height:100%;object-fit:cover}
  .frow .fti{font-family:"Mochiy Pop One";font-size:clamp(16px,2.8vw,38px);text-shadow:0 2px 8px rgba(0,0,0,.4)}
  .frow.focus .fcv{border-color:var(--gold)}
  .cf{position:absolute;inset:0;overflow:hidden;pointer-events:none;z-index:5}
  .cf span{position:absolute;top:-18px;width:11px;height:16px;border-radius:2px;animation:fall linear forwards}
  @keyframes fall{to{transform:translateY(110vh) rotate(680deg);opacity:.1}}
  .ctl{display:flex;gap:7px;align-items:center;flex-wrap:wrap;justify-content:center;background:rgba(255,255,255,.08);padding:8px 14px;border-radius:999px;max-width:98vw}
  .ctl button{font:inherit;font-weight:800;border:0;border-radius:999px;padding:8px 13px;cursor:pointer;background:rgba(255,255,255,.92);color:#2a1a4a}
  .ctl .prog{color:#fff;font-weight:800;font-size:13px;min-width:118px;text-align:center}
  .ctl select{font:inherit;border-radius:999px;border:0;padding:7px 10px;font-weight:800}
  .hint{color:rgba(255,255,255,.6);font-size:12px;font-weight:700;text-align:center}
</style></head><body>
  <div id="frame"><div id="stage"></div></div>
  <div class="ctl">
    <button id="pv">⏮</button><button id="pp">⏸</button><button id="nx">⏭</button><button id="rs">↺ 最初から</button>
    <span class="prog" id="prog">—</span>
    速度<select id="sp"><option value="1.5">ゆっくり</option><option value="1" selected>標準(3分)</option><option value="0.6">速い</option></select>
    <button id="lm">標準</button><button id="or">横 16:9</button><button id="fs">⛶ 全画面</button><button id="mu">🔇</button>
  </div>
  <div class="hint">「レイアウト」ボタンで 標準→全面カバー(案F)→シネマ(案G)→フィード(案H) を巡回切替／「縦 9:16」でショート向け。⛶全画面→画面収録で動画化。BGMは movie_bgm.mp3 を同フォルダに置くと🔇から再生。</div>
  <audio id="bgm" src="movie_bgm.mp3" loop></audio>
  <script src="movie.js"></script>
</body></html>'''
open("movie.html", "w", encoding="utf-8").write(HTML)
print(f"movie.html + movie.js 生成（{len(games)}作・4レイアウト）")
