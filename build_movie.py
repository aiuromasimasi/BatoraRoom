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
                "year": row.get("発売年","").strip(),"plat": row.get("プラットフォーム","").strip(),
                "m":_n(row.get("思い入れ度")),"i":_n(row.get("衝撃度")),
                "f":_n(row.get("面白さ")),"r":_n(row.get("ストーリー")),"mu":_n(row.get("音楽・サウンド"))}
cid2title = {v: k for k, v in title2cid.items()}
def mkgame(r, cid):
    d = gd.get(cid, {})
    return {"rank": r, "title": cid2title.get(cid, "?"), "img": f"game_covers/c{cid}.jpg",
        "intro": d.get("intro",""), "genre": d.get("genre",""), "year": d.get("year",""), "plat": d.get("plat",""),
        "m": d.get("m"), "i": d.get("i"), "f": d.get("f"), "r": d.get("r"), "mu": d.get("mu")}
games = [mkgame(r, title2cid[rank[r]]) for r in sorted(rank)]
# Part1: ランク外（予備軍）を cid 昇順で 101〜200 位に暫定割当（最大100作）
ranked_cids = {title2cid[t] for t in rank.values()}
reserve = sorted(cid for cid in range(1, c + 1) if cid not in ranked_cids)
for i, cid in enumerate(reserve[:100]):
    games.append(mkgame(101 + i, cid))
GAMES_JSON = json.dumps(games, ensure_ascii=False)

JS = '''const GAMES = __GAMES__;
const byRank = {}; GAMES.forEach(g=>byRank[g.rank]=g);
const COVERS=GAMES.filter(g=>g.rank<=100).map(g=>g.img);
const MOSAIC=(()=>{const cols=['','','',''];COVERS.forEach((s,k)=>{cols[k%4]+=`<img src="${s}" alt="" loading="lazy">`;});return '<div class="bgrid">'+cols.map((c,k)=>`<div class="bcol ${k%2?'down':'up'}">${c}${c}</div>`).join('')+'</div>';})();
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
const T1=120000, T2=180000; // Part1(200→101)=2分 / Part2(100→1)=3分 → 合計5分
const WT=s=>{ if(s.t==='b') return 0.85; const r=s.r;
  if(s.t==='tame') return r===1?3.0:r<=3?2.4:2.0;
  return r===1?3.6:r<=3?2.6:r<=10?2.0:r<=20?1.5:r<=50?1.15:0.78; };
function buildSteps(){ steps.length=0;
  const has=r=>byRank[r]!=null;
  // ---- Part1: 200→101位（暫定cid順）。P1: 0=A タイル / 1=B 横流し / 2=C 2列 / 3=D ラッシュ / 4=E モザイク ----
  const p1=[];
  if(P1===3){ // D ズームラッシュ：1枚ずつ＋10区切りのレンジ帯
    for(let r=200;r>=101;r--){ if(!has(r))continue; if(r%10===0) p1.push({t:'p1rb',r}); p1.push({t:'p1one',r}); }
    const w=s=>s.t==='p1rb'?0.55:1, sm=p1.reduce((a,s)=>a+w(s),0)||1; p1.forEach(s=>s.base=w(s)/sm*T1);
  } else if(P1===1||P1===2){ // B/C 連続スクロール：1ステップ
    p1.push({t:'p1cont',sub:P1===1?'film':'dual',base:T1});
  } else { // A/E ページ：10作×最大10ページ
    const sub=P1===0?'tile':'mosaic';
    for(let hi=200;hi>=110;hi-=10){ const ranks=[]; for(let r=hi;r>hi-10;r--) if(has(r)) ranks.push(r); if(ranks.length) p1.push({t:'p1page',sub,ranks,hi,lo:hi-9}); }
    const n=p1.length||1; p1.forEach(s=>s.base=T1/n);
  }
  // ---- Part2: 100→1位（現状維持・T2に正規化） ----
  const p2=[];
  for(let r=100;r>=1;r--){ if(BANNERS[r]) p2.push({t:'b',r}); if(TM && r<=10) p2.push({t:'tame',r}); p2.push({t:'g',r}); }
  const sumW=p2.reduce((a,s)=>a+WT(s),0); p2.forEach(s=>s.base=WT(s)/sumW*T2);
  for(const s of p1) steps.push(s); for(const s of p2) steps.push(s);
}

const stage=document.getElementById('stage');
let si=0, playing=true, mult=1, AUTO=true, LM=0, mode=0, TS=1, BG=0, TM=2, timer=null, feedRAF=null, feedStart=null;
let P1=0, contRAF=null, contElapsed=0, contDur=0, contApply=null, contLast=0; // Part1（200→101）状態
const LMN=['標準','全面カバー','シネマ(案G)','フィード(案H)'];
const P1N=['A タイル','B 横流し','C 2列','D ラッシュ','E モザイク'];
const TMN=['OFF','案A','案B','案C'];
function isFeed(){return !AUTO && LM===3;}
function curLM(r){return AUTO ? (r<=10?1:r<=50?2:0) : LM;} // オート昇格:51-100標準/11-50シネマ/1-10全面カバー
function dur(s){return s.base*mult;}
function setProgP(p){const f=document.getElementById('pfill');if(!f)return;f.style.width=(Math.max(0,Math.min(1,p))*100).toFixed(1)+'%';const h=200*(1-Math.max(0,Math.min(1,p)));f.style.background='linear-gradient(90deg,hsl('+h.toFixed(0)+',92%,58%),hsl('+(h-22).toFixed(0)+',95%,62%))';}
function setProg(r){ let p; if(r>100){p=((200-r)/100)*0.4;} else {p=0.4+((100-r)/99)*0.6;} setProgP(p); }
function esc(s){return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;');}
function confetti(n){const w=document.createElement('div');w.className='cf';const cols=['#ff5ea8','#9b5cff','#36c5ff','#ffd23f','#3ff2c2','#ff8a3d'];
  for(let i=0;i<n;i++){const s=document.createElement('span');s.style.left=(Math.random()*100).toFixed(1)+'%';s.style.background=cols[i%cols.length];
    s.style.animationDelay=(Math.random()*.5).toFixed(2)+'s';s.style.animationDuration=(2+Math.random()*1.6).toFixed(2)+'s';w.appendChild(s);}
  stage.appendChild(w);setTimeout(()=>w.remove(),4200);}
function gameHTML(g,r,d,lm){
  const rated=g.m!=null&&g.i!=null&&g.f!=null;
  const meta=[g.genre,g.plat,(g.year?g.year+'年':'')].filter(Boolean).join(' ・ ');
  const metaSp=`<span class="mg">${esc(g.genre)}</span>`+(g.plat?`<span class="mp">${esc(g.plat)}</span>`:'')+(g.year?`<span class="my">${esc(g.year)}年</span>`:'');
  if(lm===1){ // 全面カバー(案F)
    const rev=(TM&&r<=10)?(TM===3?'<div class="curt l"></div><div class="curt r"></div>':'<div class="revflash"></div>'):'';
    return `<div class="slide full ${r===1?'no1':''} ${TM&&r<=10?'rev':''}"><img class="bg" src="${g.img}" alt="" onerror="this.style.opacity=0" style="animation-duration:${(d/1000).toFixed(1)}s">
      <div class="scrim"></div><div class="rkF">${r}<span>位</span></div><div class="tierF">${tierOf(r)}</div>
      <div class="botF ts${TS}"><div class="tiF">${esc(g.title)}</div><div class="metaF">${metaSp}</div><div class="introF">${esc(g.intro)}</div></div>
      ${rated?'<div class="radF">'+radar(g)+'</div>':''}${rev}</div>`;
  }
  if(lm===2){ // シネマ(案G)
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
function tameHTML(g,r,d){
  const rated=g.m!=null&&g.i!=null&&g.f!=null;
  const sd=x=>'animation-delay:'+(d*x/1000).toFixed(2)+'s';
  const cls=['','tmA','tmB','tmC'][TM];
  const genre=esc(g.genre)||'？', year=g.year?esc(g.year)+'年':'？', intro=esc(g.intro)||'…';
  const L = TM===2
    ? {g:'GENRE / ',y:'YEAR / ',i:'FILE / ',lab:'ANALYZING…',rk:'RANK #'+r}
    : {g:'ジャンル｜',y:'発売｜',i:'',lab:(TM===3?'？ ？ ？':'このゲームは…'),rk:(TM===3?'第 '+r+' 位':r+'位')};
  return `<div class="slide tame ${cls}"><div class="tmbg"></div>
    <div class="tmlabel" style="${sd(.02)}">${L.lab}</div>
    <div class="tmrank" style="${sd(0)}">${L.rk}</div>
    <div class="tmhints">
      <div class="thint" style="${sd(.12)}"><span class="thk">${L.g}</span>${genre}</div>
      <div class="thint" style="${sd(.30)}"><span class="thk">${L.y}</span>${year}</div>
      <div class="thint ti3" style="${sd(.48)}">${L.i?'<span class="thk">'+L.i+'</span>':''}${intro}</div>
    </div>
    ${rated?'<div class="tmradar" style="'+sd(.66)+'">'+radar(g)+'</div>':''}
    ${TM===1?'<div class="tmq" style="'+sd(.66)+'">?</div>':''}
  </div>`;
}
// ===== Part1（200→101位）ビルダー =====
function p1pageHTML(s){
  const cells=s.ranks.map((r,k)=>{ const g=byRank[r];
    let st;
    if(s.sub==='tile'){ st='animation-delay:'+(k*0.06).toFixed(2)+'s'; }
    else { const a=k*2.39996; const dx=Math.round(Math.cos(a)*130), dy=Math.round(Math.sin(a)*130), rot=(k%2?1:-1)*12;
      st='--dx:'+dx+'px;--dy:'+dy+'px;--rot:'+rot+'deg;animation-delay:'+(k*0.05).toFixed(2)+'s'; }
    return `<div class="p1cell" style="${st}"><span class="pn">${r}</span><img src="${g.img}" loading="lazy" onerror="this.style.opacity=0"><span class="pt">${esc(g.title)}</span></div>`;
  }).join('');
  return `<div class="p1page ${s.sub}"><div class="p1head">${s.hi} <span>→</span> ${s.lo} <small>位</small></div><div class="p1grid">${cells}</div></div>`;
}
function p1oneHTML(g,r){ const meta=[g.genre,(g.year?g.year+'年':'')].filter(Boolean).join(' ・ ');
  return `<div class="p1one"><div class="o-rk">${r}<span>位</span></div><div class="o-cv"><img src="${g.img}" onerror="this.style.opacity=0"></div>
    <div class="o-info"><div class="o-ti">${esc(g.title)}</div><div class="o-meta">${esc(meta)}</div></div></div>`; }
function p1rbHTML(r){ return `<div class="p1rb"><div class="rbn">${r} <span>→</span> ${r-9}</div><div class="rbs">第 ${r-9} 〜 ${r} 位</div><div class="bflash"></div></div>`; }
function buildCont(s){ contElapsed=0; contDur=dur(s);
  const ranks=[]; for(let r=200;r>=101;r--) if(byRank[r]) ranks.push(r);
  if(s.sub==='film'){
    stage.innerHTML='<div class="p1film" id="p1sc">'+ranks.map(r=>{const g=byRank[r];
      return `<div class="fcell"><div class="fcv"><span class="fn">${r}</span><img src="${g.img}" loading="lazy" onerror="this.style.opacity=0"></div><div class="ft">${esc(g.title)}</div></div>`;}).join('')+'</div>';
    const sc=document.getElementById('p1sc'), shift=Math.max(1,sc.scrollWidth-stage.clientWidth);
    contApply=p=>{ sc.style.transform='translateX('+(-shift*p).toFixed(1)+'px)'; };
  } else { // dual
    const half=Math.ceil(ranks.length/2), L=ranks.slice(0,half), R=ranks.slice(half);
    const col=(arr,cls)=>`<div class="p1dcol ${cls}">`+arr.map(r=>{const g=byRank[r];
      return `<div class="dcell"><span class="dn">${r}</span><img src="${g.img}" loading="lazy" onerror="this.style.opacity=0"><span class="dt">${esc(g.title)}</span></div>`;}).join('')+'</div>';
    stage.innerHTML='<div class="bignum" id="p1big">200</div><div class="p1dual">'+col(L,'l')+col(R,'r')+'</div>';
    const cl=document.querySelector('.p1dcol.l'), cr=document.querySelector('.p1dcol.r'), big=document.getElementById('p1big');
    const sl=Math.max(1,cl.scrollHeight-stage.clientHeight), sr=Math.max(1,cr.scrollHeight-stage.clientHeight);
    contApply=p=>{ cl.style.transform='translateY('+(-sl*p).toFixed(1)+'px)'; cr.style.transform='translateY('+(-sr*p).toFixed(1)+'px)';
      big.textContent=Math.round(200-99*p); };
  }
}
function contFrame(ts){ if(!playing)return; if(contLast)contElapsed+=ts-contLast; contLast=ts;
  const p=Math.min(1,contElapsed/contDur); if(contApply)contApply(p); setProgP(p*0.4);
  if(p>=1){ contLast=0; contElapsed=0; if(si<steps.length-1){si++;step();} else {playing=false;updateBtn();} return; }
  contRAF=requestAnimationFrame(contFrame); }
function render(s){
  if(s.t==='p1page'){ stage.innerHTML=p1pageHTML(s); setProg(s.lo); return; }
  if(s.t==='p1one'){ stage.innerHTML=p1oneHTML(byRank[s.r],s.r); setProg(s.r); return; }
  if(s.t==='p1rb'){ stage.innerHTML=p1rbHTML(s.r); setProg(s.r); return; }
  if(s.t==='p1cont'){ buildCont(s); return; }
  if(s.t==='b'){const [a,b]=BANNERS[s.r];stage.innerHTML=`<div class="banner bg${BG}">${MOSAIC}<div class="bscrim"></div><div class="bshock"></div><div class="btxt">${a}</div><div class="bsub">${b}</div><div class="bflash"></div></div>`;setProg(s.r);return;}
  if(s.t==='tame'){stage.innerHTML=tameHTML(byRank[s.r],s.r,dur(s));setProg(s.r);return;}
  const g=byRank[s.r]; stage.innerHTML=gameHTML(g,s.r,dur(s),curLM(s.r));
  if(s.r===1) confetti(110); else if(s.r<=3) confetti(50);
  setProg(s.r);
}
function step(){ if(isFeed()) return; const s=steps[si]; render(s); clearTimeout(timer); cancelAnimationFrame(contRAF);
  if(s.t==='p1cont'){ if(playing){ contLast=0; contRAF=requestAnimationFrame(contFrame); } updateProg(); return; }
  if(playing) timer=setTimeout(()=>{ if(si<steps.length-1){si++;step();} else {playing=false;updateBtn();} }, dur(s)); updateProg(); }
function updateProg(){const s=steps[si]; let t;
  if(isFeed()) t='フィード再生中';
  else if(s.t==='p1page') t='前半 '+s.hi+'–'+s.lo+'位';
  else if(s.t==='p1one') t=s.r+'位';
  else if(s.t==='p1rb') t=s.r+'–'+(s.r-9)+'位';
  else if(s.t==='p1cont') t='前半（'+(s.sub==='film'?'横流し':'2列')+'）';
  else t=(s.t==='b'?'—':s.r+'位'+(s.t==='tame'?'(タメ)':''))+' / 残り'+Math.max(0,steps.length-1-si);
  document.getElementById('prog').textContent=t;}
function updateBtn(){document.getElementById('pp').textContent=playing?'⏸':'▶';}
function play(){ if(isFeed())return; playing=true; updateBtn(); const s=steps[si];
  if(s&&s.t==='p1cont'){ contLast=0; contRAF=requestAnimationFrame(contFrame); return; } step(); }
function pause(){ playing=false; clearTimeout(timer); cancelAnimationFrame(contRAF); contLast=0; updateBtn(); }
// 案H フィード
function buildFeed(){
  const list=GAMES.slice().sort((a,b)=>b.rank-a.rank);
  stage.innerHTML='<div class="feed" id="feed">'+list.map(g=>`<div class="frow"><div class="frk">${g.rank}<small>位</small></div><div class="fcv"><img src="${g.img}" onerror="this.style.opacity=0"></div><div class="fti">${esc(g.title)}</div></div>`).join('')+'</div>';
  const feed=document.getElementById('feed'), rows=[...feed.children]; feedStart=null;
  const total=(T1+T2)*mult;
  function fa(t){ if(LM!==3) return; if(feedStart==null)feedStart=t; const p=Math.min(1,(t-feedStart)/total);
    const max=Math.max(1,feed.scrollHeight-stage.clientHeight); feed.style.transform='translateY('+(-max*p).toFixed(1)+'px)';
    const fi=Math.round(p*(rows.length-1)); rows.forEach((r,k)=>r.classList.toggle('focus',k===fi)); setProgP(p);
    if(p<1) feedRAF=requestAnimationFrame(fa); }
  feedRAF=requestAnimationFrame(fa);
}
document.getElementById('pp').onclick=()=>playing?pause():play();
document.getElementById('rs').onclick=()=>{ if(isFeed()){cancelAnimationFrame(feedRAF);buildFeed();return;} cancelAnimationFrame(contRAF); si=0; contElapsed=0; playing=true; updateBtn(); step(); };
document.getElementById('nx').onclick=()=>{if(isFeed())return;if(si<steps.length-1){si++;pause();render(steps[si]);updateProg();}};
document.getElementById('pv').onclick=()=>{if(isFeed())return;if(si>0){si--;pause();render(steps[si]);updateProg();}};
document.getElementById('sp').onchange=e=>{mult=+e.target.value;};
document.getElementById('lm').onclick=()=>{ mode=(mode+1)%5; cancelAnimationFrame(feedRAF);
  if(mode===0){AUTO=true;document.getElementById('lm').textContent='オート';}
  else{AUTO=false;LM=mode-1;document.getElementById('lm').textContent=LMN[LM];}
  if(isFeed()){ pause(); buildFeed(); updateProg(); } else { render(steps[si]); updateProg(); } };
document.getElementById('p1').onclick=()=>{ P1=(P1+1)%5; document.getElementById('p1').textContent='前半'+P1N[P1];
  cancelAnimationFrame(contRAF); cancelAnimationFrame(feedRAF); buildSteps(); si=0; contElapsed=0; pause(); render(steps[si]); updateProg(); };
document.getElementById('ts').onclick=()=>{TS=(TS+1)%3;document.getElementById('ts').textContent='文字'+['A','B','C'][TS];if(!isFeed())render(steps[si]);};
document.getElementById('bg').onclick=()=>{BG=(BG+1)%3;document.getElementById('bg').textContent='背景'+['A','B','C'][BG];cancelAnimationFrame(feedRAF);pause();si=steps.findIndex(s=>s.t==='b'&&s.r===20);render(steps[si]);updateProg();};
document.getElementById('tame').onclick=()=>{ const cr=steps[si]?steps[si].r:100;
  TM=(TM+1)%4; document.getElementById('tame').textContent='タメ'+TMN[TM]; buildSteps();
  const tr=(TM&&cr>10)?7:cr; let i=steps.findIndex(s=>s.r===tr&&s.t==='tame'); if(i<0)i=steps.findIndex(s=>s.r===tr&&s.t==='g'); if(i<0)i=0;
  si=i; cancelAnimationFrame(feedRAF); pause(); if(isFeed()){buildFeed();}else{render(steps[si]);} updateProg(); };
document.getElementById('or').onclick=()=>{const f=document.getElementById('frame');f.classList.toggle('vert');document.getElementById('or').textContent=f.classList.contains('vert')?'縦 9:16':'横 16:9';if(isFeed()){cancelAnimationFrame(feedRAF);buildFeed();}};
document.getElementById('fs').onclick=()=>{const f=document.getElementById('frame');(f.requestFullscreen||f.webkitRequestFullscreen||(()=>{})).call(f);};
const bgm=document.getElementById('bgm');
document.getElementById('mu').onclick=()=>{if(bgm.paused){bgm.play().catch(()=>{});document.getElementById('mu').textContent='🔊';}else{bgm.pause();document.getElementById('mu').textContent='🔇';}};
document.getElementById('p1').textContent='前半'+P1N[P1];
buildSteps(); updateBtn(); step();
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
  /* 進行バー（青→赤の温度カラー） */
  #pbar{position:absolute;left:0;right:0;bottom:0;height:6px;background:rgba(255,255,255,.14);z-index:6;pointer-events:none}
  #pfill{height:100%;width:0;background:hsl(200,92%,58%);box-shadow:0 0 12px rgba(255,255,255,.55);transition:width .45s linear,background .45s linear}
  .banner{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:0 6%;animation:shake .5s .33s both}
  @keyframes shake{0%,100%{transform:translate(0,0)}12%{transform:translate(-8px,5px)}26%{transform:translate(7px,-5px)}40%{transform:translate(-6px,4px)}55%{transform:translate(5px,-3px)}72%{transform:translate(-3px,2px)}88%{transform:translate(2px,-1px)}}
  .btxt{font-family:"Mochiy Pop One";font-size:clamp(30px,6.4vw,84px);line-height:1.05;color:#fff;text-shadow:0 5px 0 rgba(0,0,0,.2),0 0 34px rgba(255,255,255,.7);white-space:nowrap;animation:impact .55s cubic-bezier(.16,.9,.3,1.05) backwards}
  @keyframes impact{0%{transform:scale(3.1);opacity:0;filter:blur(14px)}55%{opacity:1}80%{transform:scale(.92)}100%{transform:scale(1);filter:none}}
  .bsub{font-weight:800;font-size:clamp(15px,2.6vw,28px);margin-top:10px;letter-spacing:2px;animation:infin .5s ease .5s backwards}
  .bflash{position:absolute;inset:0;background:#fff;opacity:0;pointer-events:none;animation:bflash .5s .33s backwards}
  @keyframes bflash{0%{opacity:0}12%{opacity:.9}100%{opacity:0}}
  .bshock{position:absolute;left:50%;top:50%;width:10px;height:10px;border-radius:50%;border:14px solid rgba(255,255,255,.85);transform:translate(-50%,-50%);opacity:0;pointer-events:none;animation:shock .75s ease-out .35s backwards}
  @keyframes shock{0%{width:10px;height:10px;opacity:.85;border-width:16px}100%{width:150%;height:150%;opacity:0;border-width:1px}}
  /* バナー背景：全カバー4列モザイク＋上下スクロール */
  .bgrid{position:absolute;inset:0;z-index:0;display:grid;grid-template-columns:repeat(4,1fr);gap:6px;overflow:hidden}
  .bcol{display:flex;flex-direction:column;gap:6px}
  .bcol img{width:100%;aspect-ratio:3/4;object-fit:cover;border-radius:6px;display:block}
  .bcol.up{animation:mUp 38s linear infinite}.bcol.down{animation:mDown 44s linear infinite}
  .bcol:nth-child(2){animation-duration:50s}.bcol:nth-child(3){animation-duration:42s}.bcol:nth-child(4){animation-duration:56s}
  @keyframes mUp{from{transform:translateY(0)}to{transform:translateY(-50%)}}
  @keyframes mDown{from{transform:translateY(-50%)}to{transform:translateY(0)}}
  .bscrim{position:absolute;inset:0;z-index:1}
  .banner .btxt,.banner .bsub{position:relative;z-index:3}
  .banner .bshock,.banner .bflash{z-index:2}
  .banner.bg0 .bgrid{filter:blur(5px) brightness(.5) saturate(.9)}
  .banner.bg0 .bscrim{background:radial-gradient(120% 90% at 50% 50%,rgba(22,13,42,.4),rgba(22,13,42,.84))}
  .banner.bg1 .bgrid{filter:grayscale(.85) brightness(.55);opacity:.55}
  .banner.bg1 .bscrim{background:linear-gradient(135deg,rgba(255,94,168,.55),rgba(155,92,255,.5),rgba(54,197,255,.55))}
  .banner.bg2 .bgrid{filter:brightness(.72) saturate(1.05)}
  .banner.bg2 .bscrim{background:radial-gradient(58% 46% at 50% 50%,rgba(0,0,0,.82) 0%,rgba(0,0,0,.5) 46%,rgba(0,0,0,.12) 100%)}
  /* 標準 */
  .slide{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;gap:2%;padding:2.5% 3%}
  .rk{flex:none;font-family:"Baloo 2";font-weight:800;font-size:clamp(80px,22vh,320px);line-height:.82;color:#fff;text-shadow:0 7px 0 rgba(0,0,0,.2),0 0 34px rgba(255,255,255,.55);animation:rkin .55s cubic-bezier(.2,1.5,.3,1) backwards}
  .rk .rku{font-size:.34em;margin-left:2px}
  @keyframes rkin{from{transform:scale(2.4);opacity:0;filter:blur(6px)}to{transform:scale(1);opacity:1;filter:none}}
  .mid{flex:none;height:100%;display:flex;align-items:center;justify-content:center;animation:cvin .6s cubic-bezier(.2,1.2,.3,1) backwards}
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
  .tiF{font-family:"Mochiy Pop One";font-size:clamp(18px,2.4vw,34px);line-height:1.28;word-break:keep-all;overflow-wrap:break-word}
  .metaF{display:flex;gap:8px;flex-wrap:wrap;align-items:center;font-weight:800;font-size:clamp(13px,1.8vw,22px);margin-top:7px}
  .introF{font-weight:700;font-size:clamp(13px,1.8vw,22px);margin-top:6px;max-width:96%;line-height:1.55;word-break:auto-phrase;overflow-wrap:break-word}
  /* 文字スタイル3案（全面カバー） */
  .botF.ts0{background:rgba(12,8,28,.52);border:1.5px solid rgba(255,255,255,.3);border-radius:18px;padding:14px 18px}
  .botF.ts0 .mg{color:#ffd23f}.botF.ts0 .my{color:#7fd7ff}.botF.ts0 .mp{color:#5cf0c8}
  .botF.ts1 .tiF,.botF.ts1 .metaF span,.botF.ts1 .introF{text-shadow:-1.5px -1.5px 0 #160d2a,1.5px -1.5px 0 #160d2a,-1.5px 1.5px 0 #160d2a,1.5px 1.5px 0 #160d2a,0 3px 10px rgba(0,0,0,.95)}
  .botF.ts1 .mg{color:#ff8ad1}.botF.ts1 .my{color:#ffe14d}.botF.ts1 .mp{color:#7dffb0}
  .botF.ts2{border-left:6px solid #ff5ea8;border-radius:0 14px 14px 0;background:linear-gradient(90deg,rgba(0,0,0,.6),rgba(0,0,0,.05));padding:12px 16px}
  .botF.ts2 .metaF span{padding:3px 12px;border-radius:999px;font-size:.92em}
  .botF.ts2 .mg{background:#ffd23f;color:#5a3d00}.botF.ts2 .my{background:#36c5ff;color:#06324f}.botF.ts2 .mp{background:#3ff2c2;color:#064b3a}
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
  /* TOP10 タメ演出（案A/B/C） */
  .slide.tame{flex-direction:column;gap:1.6vh;padding:5% 7%;text-align:center;overflow:hidden}
  .tame .tmbg{position:absolute;inset:0;z-index:0}
  .tame .tmlabel,.tame .tmrank,.tame .tmhints,.tame .tmradar,.tame .tmq{position:relative;z-index:2}
  .tame .thint,.tame .tmradar,.tame .tmlabel,.tame .tmq{opacity:0;animation:tmIn .5s ease both}
  @keyframes tmIn{from{opacity:0;transform:translateY(22px)}to{opacity:1;transform:none}}
  .tmrank{font-family:"Baloo 2";font-weight:800;line-height:.85;animation:rkin .55s cubic-bezier(.2,1.5,.3,1) backwards}
  .tmhints{display:flex;flex-direction:column;gap:1.1vh;max-width:90%}
  .thint{font-weight:800;font-size:clamp(16px,2.6vw,34px);line-height:1.4}
  .thint .thk{opacity:.9}
  .thint.ti3{font-weight:700;font-size:clamp(13px,1.9vw,24px);opacity:.96}
  .tmradar .radar{width:clamp(160px,20vw,300px)}
  .tmA .tmbg{background:radial-gradient(120% 100% at 50% 38%,#221540,#0a0612)}
  .tmA .tmlabel{font-family:"Mochiy Pop One";font-size:clamp(15px,2.4vw,28px);color:#ffd23f}
  .tmA .tmrank{font-size:clamp(70px,18vh,240px);color:#ffd23f;text-shadow:0 0 34px rgba(255,210,63,.5),0 6px 0 rgba(0,0,0,.25)}
  .tmA .thint .thk{color:#ff8ad1}
  .tmA .tmq{position:absolute;right:5%;bottom:4%;font-family:"Baloo 2";font-weight:800;font-size:clamp(120px,40vh,460px);color:rgba(255,255,255,.09);z-index:1}
  .tmB .tmbg{background:#04060a}
  .tmB .tmbg::before{content:"";position:absolute;inset:0;background:repeating-linear-gradient(0deg,rgba(54,197,255,.10) 0 1px,transparent 1px 4px)}
  .tmB .tmbg::after{content:"";position:absolute;inset:0;background:radial-gradient(60% 60% at 50% 45%,rgba(54,197,255,.12),transparent 70%)}
  .tmB .tmlabel{font-family:"Baloo 2";letter-spacing:3px;font-size:clamp(14px,2.2vw,26px);color:#36c5ff;text-shadow:0 0 12px rgba(54,197,255,.6)}
  .tmB .tmrank{position:absolute;top:5%;right:5%;font-size:clamp(28px,6vw,72px);color:rgba(54,197,255,.9)}
  .tmB .tmhints{font-family:"Baloo 2"}
  .tmB .thint{color:#dff4ff;letter-spacing:.5px}
  .tmB .thint .thk{color:#36c5ff}
  .tmB .tmradar{filter:drop-shadow(0 0 10px rgba(54,197,255,.5))}
  .tmC .tmbg{background:radial-gradient(42% 60% at 50% 36%,#3a3216,#150d24 50%,#070310 82%)}
  .tmC .tmlabel{font-family:"Mochiy Pop One";font-size:clamp(15px,2.4vw,28px);color:rgba(255,232,170,.85);letter-spacing:6px}
  .tmC .tmrank{font-size:clamp(64px,16vh,220px);color:var(--gold);text-shadow:0 0 44px rgba(255,184,0,.6)}
  .tmC .thint{color:#fff;text-shadow:0 2px 16px rgba(0,0,0,.8)}
  .tmC .thint .thk{color:var(--gold)}
  .tmC .tmradar{filter:drop-shadow(0 0 16px rgba(255,210,120,.55))}
  /* タメ→公開のつなぎ */
  .full.rev .revflash{position:absolute;inset:0;background:#fff;z-index:9;opacity:0;animation:rflash .5s ease forwards;pointer-events:none}
  @keyframes rflash{0%{opacity:.92}100%{opacity:0}}
  .full.rev .curt{position:absolute;top:0;bottom:0;width:51%;background:#070310;z-index:9;pointer-events:none}
  .full.rev .curt.l{left:0;animation:curtL .7s cubic-bezier(.7,0,.25,1) forwards}
  .full.rev .curt.r{right:0;animation:curtR .7s cubic-bezier(.7,0,.25,1) forwards}
  @keyframes curtL{to{transform:translateX(-101%)}}
  @keyframes curtR{to{transform:translateX(101%)}}
  /* ===== Part1（200→101位）高速パート ===== */
  /* A タイル / E モザイク（10作ページ） */
  .p1page{position:absolute;inset:0;display:flex;flex-direction:column;padding:2.6% 3.2%;gap:1.4vh;background:radial-gradient(120% 90% at 50% 26%,rgba(155,92,255,.4),rgba(22,13,42,.72))}
  .p1head{font-family:"Mochiy Pop One";font-size:clamp(22px,5vw,60px);text-align:center;color:#fff;text-shadow:0 4px 0 rgba(0,0,0,.22),0 0 26px rgba(255,255,255,.5);animation:impact .5s cubic-bezier(.16,.9,.3,1.05) backwards}
  .p1head span{color:var(--gold);margin:0 .15em}.p1head small{font-size:.5em;opacity:.85}
  .p1grid{flex:1;display:grid;grid-template-columns:repeat(5,1fr);grid-template-rows:repeat(2,1fr);gap:1vh .9vw;min-height:0}
  .p1cell{position:relative;border-radius:12px;overflow:hidden;border:3px solid #fff;box-shadow:0 8px 22px rgba(0,0,0,.5);background:#241836}
  .p1cell img{width:100%;height:100%;object-fit:cover;display:block}
  .p1cell .pn{position:absolute;left:0;top:0;background:rgba(0,0,0,.66);color:#fff;font-family:"Baloo 2";font-weight:800;padding:1px 9px;border-bottom-right-radius:10px;font-size:clamp(13px,1.7vw,24px)}
  .p1cell .pt{position:absolute;left:0;right:0;bottom:0;background:linear-gradient(0deg,rgba(0,0,0,.88),transparent);color:#fff;font-size:clamp(9px,1.05vw,14px);padding:15px 6px 4px;font-weight:700;line-height:1.2;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .p1page.tile .p1cell{opacity:0;animation:p1pop .5s cubic-bezier(.2,1.7,.3,1) forwards}
  @keyframes p1pop{from{opacity:0;transform:scale(.35)}to{opacity:1;transform:scale(1)}}
  .p1page.mosaic .p1cell{opacity:0;animation:p1fly .6s cubic-bezier(.2,1.05,.3,1) forwards}
  @keyframes p1fly{from{opacity:0;transform:translate(var(--dx,0),var(--dy,0)) scale(.3) rotate(var(--rot,0))}to{opacity:1;transform:none}}
  #frame.vert .p1grid{grid-template-columns:repeat(2,1fr);grid-template-rows:repeat(5,1fr)}
  /* D ズームラッシュ（1枚ずつ） */
  .p1one{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;gap:4%;padding:4%;background:radial-gradient(120% 90% at 50% 40%,rgba(54,197,255,.28),rgba(22,13,42,.72))}
  .p1one .o-rk{font-family:"Baloo 2";font-weight:800;font-size:clamp(60px,16vh,200px);line-height:.85;color:#fff;text-shadow:0 6px 0 rgba(0,0,0,.22),0 0 28px rgba(255,255,255,.5);animation:rkin .32s cubic-bezier(.2,1.5,.3,1) backwards}
  .p1one .o-rk span{font-size:.32em}
  .p1one .o-cv{flex:none;height:64%;aspect-ratio:3/4;border-radius:14px;overflow:hidden;border:4px solid #fff;box-shadow:0 14px 40px rgba(0,0,0,.6);animation:slidein .32s cubic-bezier(.2,1.2,.3,1) backwards}
  .p1one .o-cv img{width:100%;height:100%;object-fit:cover}
  .p1one .o-info{max-width:36%}
  .p1one .o-ti{font-family:"Mochiy Pop One";font-size:clamp(18px,3vw,42px);line-height:1.18;text-shadow:0 3px 10px rgba(0,0,0,.4)}
  .p1one .o-meta{font-weight:800;font-size:clamp(13px,1.8vw,22px);opacity:.92;margin-top:6px}
  #frame.vert .p1one{flex-direction:column;gap:2%}#frame.vert .p1one .o-info{max-width:88%;text-align:center}#frame.vert .p1one .o-cv{height:40vh}
  .p1rb{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;background:radial-gradient(circle at 50% 50%,rgba(255,94,168,.45),rgba(22,13,42,.82))}
  .p1rb .rbn{font-family:"Mochiy Pop One";font-size:clamp(44px,11vw,140px);color:#fff;text-shadow:0 6px 0 rgba(0,0,0,.25),0 0 30px rgba(255,255,255,.6);animation:impact .5s cubic-bezier(.16,.9,.3,1.05) backwards}
  .p1rb .rbn span{color:var(--gold)}
  .p1rb .rbs{font-weight:800;letter-spacing:3px;margin-top:6px;font-size:clamp(14px,2.4vw,26px);opacity:.9}
  /* B 横フィルム */
  .p1film{position:absolute;top:0;bottom:0;left:0;display:flex;align-items:center;gap:1.4vw;padding:0 50vw;will-change:transform}
  .p1film .fcell{flex:none;width:clamp(120px,15vw,210px)}
  .p1film .fcv{position:relative;aspect-ratio:3/4;border-radius:12px;overflow:hidden;border:3px solid #fff;box-shadow:0 12px 30px rgba(0,0,0,.5)}
  .p1film .fcv img{width:100%;height:100%;object-fit:cover}
  .p1film .fn{position:absolute;left:0;top:0;background:rgba(0,0,0,.66);color:#fff;font-family:"Baloo 2";font-weight:800;padding:1px 9px;border-bottom-right-radius:10px;font-size:clamp(13px,1.6vw,22px)}
  .p1film .ft{text-align:center;font-family:"Mochiy Pop One";font-size:clamp(12px,1.5vw,20px);margin-top:8px;text-shadow:0 2px 8px rgba(0,0,0,.5);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  /* C 縦2列 */
  .p1dual{position:absolute;inset:0;display:flex;gap:4%;padding:0 9%;overflow:hidden}
  .p1dcol{flex:1;display:flex;flex-direction:column;align-items:center;gap:1.3vh;will-change:transform}
  .p1dcol.r{margin-top:-10vh}
  .p1dual .dcell{position:relative;width:clamp(108px,14vh,188px);border-radius:11px;overflow:hidden;border:3px solid #fff;box-shadow:0 8px 22px rgba(0,0,0,.5);flex:none}
  .p1dual .dcell img{width:100%;aspect-ratio:3/4;object-fit:cover;display:block}
  .p1dual .dcell .dn{position:absolute;left:0;top:0;background:rgba(0,0,0,.66);color:#fff;font-family:"Baloo 2";font-weight:800;padding:1px 9px;border-bottom-right-radius:10px;font-size:clamp(12px,1.5vw,20px)}
  .p1dual .dcell .dt{position:absolute;left:0;right:0;bottom:0;background:linear-gradient(0deg,rgba(0,0,0,.84),transparent);color:#fff;font-size:clamp(9px,1vw,13px);padding:13px 6px 3px;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .bignum{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);font-family:"Baloo 2";font-weight:800;font-size:clamp(90px,30vh,360px);color:rgba(255,255,255,.13);z-index:3;pointer-events:none}
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
  <div id="frame"><div id="stage"></div><div id="pbar"><div id="pfill"></div></div></div>
  <div class="ctl">
    <button id="pv">⏮</button><button id="pp">⏸</button><button id="nx">⏭</button><button id="rs">↺ 最初から</button>
    <span class="prog" id="prog">—</span>
    速度<select id="sp"><option value="1.5">ゆっくり</option><option value="1" selected>標準(5分)</option><option value="0.6">速い</option></select>
    <button id="p1">前半A タイル</button><button id="lm">オート</button><button id="ts">文字B</button><button id="tame">タメ案B</button><button id="bg">背景A</button><button id="or">横 16:9</button><button id="fs">⛶ 全画面</button><button id="mu">🔇</button>
  </div>
  <div class="hint">全体5分＝<b>前半（200→101位）を一気に</b>＋<b>後半（100→1位）はじっくり</b>。<b>「前半」</b>ボタンで200→101位の見せ方を巡回（A タイルドカン／B 横流し／C 2列スクロール／D ズームラッシュ／E モザイク集合）。後半は<b>オート</b>で順位が上がるほど豪華化（51〜100:標準 → 11〜50:シネマ → 1〜10:全面カバー）、「レイアウト」で切替。<b>「タメ」</b>でTOP10の正体伏せ演出。下端の<b>進行バー</b>は青→赤へ。「縦 9:16」でショート向け。⛶全画面→画面収録で動画化。BGMは movie_bgm.mp3。</div>
  <audio id="bgm" src="movie_bgm.mp3" loop></audio>
  <script src="movie.js"></script>
</body></html>'''
open("movie.html", "w", encoding="utf-8").write(HTML)
p1n = sum(1 for g in games if g["rank"] > 100)
print(f"movie.html + movie.js 生成（前半{p1n}作+後半100作=計{len(games)}作・5分構成・前半5案A〜E切替）")
