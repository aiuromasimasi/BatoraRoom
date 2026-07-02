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
CLIP_META = json.load(open("clip_meta.json", encoding="utf-8")) if os.path.exists("clip_meta.json") else {}
def mkgame(r, cid):
    d = gd.get(cid, {})
    clip = f"game_clips/c{cid}.mp4"
    pos = (CLIP_META.get(str(cid)) or {}).get("pos")
    return {"rank": r, "title": cid2title.get(cid, "?"), "img": f"game_covers/c{cid}.jpg",
        "clip": clip if os.path.exists(clip) else None,
        "cpos": pos if pos in ("left", "right") else None,
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
const TAME_MAX=20; // タメ(正体伏せ)演出の対象範囲: この順位以下で発動
const steps=[];
const T1=60000, T2=180000; // Part1(200→101)=1分(2倍速) / Part2(100→1)=3分 → 合計4分
const WT=s=>{ if(s.t==='b') return 0.85; const r=s.r;
  if(s.t==='tame') return r===1?3.0:r<=3?2.4:2.0;
  return r===1?3.6:r<=3?2.6:r<=10?2.0:r<=20?1.5:r<=50?1.15:0.78; };
function buildSteps(){ steps.length=0;
  const has=r=>byRank[r]!=null;
  // ---- オープニング（8秒・固定尺） ----
  steps.push({t:'op',r:200,base:8000});
  // ---- Part1: 200→101位（暫定cid順）1枚ずつラッシュ・帯なし。見せ方はP1(0〜4)で切替 ----
  const p1=[];
  for(let r=200;r>=101;r--){ if(has(r)) p1.push({t:'p1one',r}); }
  const sm=p1.length||1; p1.forEach(s=>s.base=T1/sm);
  // ---- Part2: 100→1位（T2に正規化。リキャップは固定尺で別枠） ----
  const p2=[];
  for(let r=100;r>=1;r--){
    if(r===1) p2.push({t:'recap',r:1,base:7600,fixed:true}); // 1位発表直前のTOP10リキャップ
    if(BANNERS[r]) p2.push({t:'b',r}); if(TM && r<=TAME_MAX) p2.push({t:'tame',r}); p2.push({t:'g',r});
  }
  const norm=p2.filter(s=>!s.fixed);
  const sumW=norm.reduce((a,s)=>a+WT(s),0); norm.forEach(s=>s.base=WT(s)/sumW*T2);
  for(const s of p1) steps.push(s); for(const s of p2) steps.push(s);
  // ---- TOP3表彰台フィナーレ（12秒・固定尺） ----
  steps.push({t:'podium',r:1,base:12000});
}

const stage=document.getElementById('stage');
let si=0, playing=true, mult=1, AUTO=false, LM=1, mode=2, TS=1, BG=0, TM=2, timer=null, feedRAF=null, feedStart=null;
let P1=0; // Part1（200→101）ラッシュの見せ方
const LMN=['標準','全面カバー','シネマ(案G)','フィード(案H)'];
const P1N=['①全面','②ブラー','③カード','④シネスコ','⑤ステージ'];
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
// 常時のキラキラ演出（後半100→1位に段階適用: 51-100=控えめ/11-50=中/1-10=豪華）
function sparkleTier(r){return r<=10?3:r<=50?2:1;}
function sparkleHTML(r){
  const tier=sparkleTier(r), n=tier===3?32:tier===2?18:9;
  const cols=tier===3?['#ffd23f','#fff8dd','#ff9ee0','#9be8ff']:tier===2?['#fff','#bfe9ff','#ffd9f0']:['#fff'];
  let s=`<div class="spkwrap t${tier}">`;
  for(let i=0;i<n;i++){
    const x=(Math.random()*100).toFixed(1), y=(Math.random()*100).toFixed(1);
    const d=(1.5+Math.random()*2.3).toFixed(2), dl=(Math.random()*3.2).toFixed(2);
    const sz=(tier===3?3.6+Math.random()*4.4:2.2+Math.random()*2.6).toFixed(1);
    s+=`<span class="spk" style="left:${x}%;top:${y}%;width:${sz}px;height:${sz}px;background:${cols[i%cols.length]};animation-duration:${d}s;animation-delay:${dl}s"></span>`;
  }
  return s+'</div>';
}
// ==== canvas花火（1位・表彰台用） ====
function fireworks(n){ n=n||3;
  const cv=document.createElement('canvas'); cv.className='fw';
  cv.width=stage.clientWidth; cv.height=stage.clientHeight; stage.appendChild(cv);
  const ctx=cv.getContext('2d'); const parts=[]; const cols=['#ffd23f','#ff5ea8','#36c5ff','#3ff2c2','#ff8a3d','#ffffff'];
  for(let b=0;b<n;b++){
    const cx=cv.width*(0.18+Math.random()*0.64), cy=cv.height*(0.12+Math.random()*0.4), col=cols[b%cols.length], t0=b*380;
    for(let i=0;i<64;i++){ const a=Math.PI*2*i/64+Math.random()*.12, sp=2+Math.random()*3.4;
      parts.push({cx,cy,vx:Math.cos(a)*sp,vy:Math.sin(a)*sp,t0,col,life:900+Math.random()*600}); } }
  let start=null;
  function fr(ts){ if(!start)start=ts; const el=ts-start; ctx.clearRect(0,0,cv.width,cv.height); let alive=false;
    for(const p of parts){ const t=el-p.t0; if(t<0){alive=true;continue;} if(t>p.life)continue; alive=true;
      const k=t/16.7, x=p.cx+p.vx*k, y=p.cy+p.vy*k+0.018*k*k, o=1-t/p.life;
      ctx.globalAlpha=o; ctx.fillStyle=p.col; ctx.beginPath(); ctx.arc(x,y,2.3,0,7); ctx.fill(); }
    if(alive&&cv.parentNode) requestAnimationFrame(fr); else cv.remove(); }
  requestAnimationFrame(fr);
}
// ==== 実機動画クリップ: g.clip があれば <video> を重ねる（失敗時は自滅してカバー画像に戻る） ====
// hideS(秒)指定時: その時点でフェードアウト→下の表紙画像が見える（clip→表紙の2段構成）
// g.cpos: 縦画面での見せ位置（left/right。clip_meta.json で指定）
const vid=(g,cls,hideS)=>{ if(!g||!g.clip) return '';
  let st=''; if(g.cpos) st+='object-position:'+g.cpos+' center;';
  if(hideS!=null) st+='animation:clipHide .5s ease '+hideS.toFixed(2)+'s forwards;';
  return `<video class="${cls||''}" src="${g.clip}" autoplay muted loop playsinline${st?` style="${st}"`:''} onerror="this.remove()"></video>`; };
// ==== SE（Web Audio 合成・素材ファイル不要） ====
let AC=null, SEon=true;
function actx(){ if(!AC){ try{AC=new (window.AudioContext||window.webkitAudioContext)();}catch(e){} }
  if(AC&&AC.state==='suspended'){ try{AC.resume().catch(()=>{});}catch(e){} } return AC; }
function tone(type,f0,f1,t0,d,peak){ const c=AC,o=c.createOscillator(),g=c.createGain();
  o.type=type; o.frequency.setValueAtTime(f0,t0); if(f1)o.frequency.exponentialRampToValueAtTime(f1,t0+d);
  g.gain.setValueAtTime(0,t0); g.gain.linearRampToValueAtTime(peak,t0+0.012); g.gain.exponentialRampToValueAtTime(0.0001,t0+d);
  o.connect(g).connect(c.destination); o.start(t0); o.stop(t0+d+0.1); }
function noiseSE(t0,d,peak,fc){ const c=AC,len=Math.floor(c.sampleRate*d),b=c.createBuffer(1,len,c.sampleRate),dd=b.getChannelData(0);
  for(let i=0;i<len;i++)dd[i]=Math.random()*2-1;
  const s=c.createBufferSource(); s.buffer=b; const f=c.createBiquadFilter(); f.type='lowpass'; f.frequency.value=fc||1000;
  const g=c.createGain(); g.gain.setValueAtTime(0,t0); g.gain.linearRampToValueAtTime(peak,t0+0.008); g.gain.exponentialRampToValueAtTime(0.0001,t0+d);
  s.connect(f).connect(g).connect(c.destination); s.start(t0); }
function se(kind,big){ if(!SEon)return; const c=actx(); if(!c||c.state!=='running')return; const t=c.currentTime+0.02;
  try{
    if(kind==='whoosh'){ noiseSE(t,0.26,0.09,900); }
    else if(kind==='don'){ tone('sine',big?160:120,big?52:60,t,0.32,big?0.5:0.3); noiseSE(t,0.1,big?0.2:0.1,420); }
    else if(kind==='tick'){ tone('square',1180,null,t,0.045,0.045); }
    else if(kind==='heart'){ tone('sine',88,54,t,0.15,0.4); tone('sine',76,50,t+0.22,0.15,0.28); }
    else if(kind==='shine'){ [1568,2093,2637].forEach((f,i)=>tone('triangle',f,null,t+i*0.055,0.3,0.06)); }
    else if(kind==='fanfare'){ [523,659,784].forEach((f,i)=>tone('square',f,null,t+i*0.15,0.32,0.085));
      [523,659,784,1047].forEach(f=>tone('triangle',f,null,t+0.62,1.0,0.075)); }
  }catch(e){}
}
let hbTimer=null;
function heartbeatLoop(){ clearTimeout(hbTimer);
  if(!document.querySelector('.slide.tame'))return;
  se('heart'); hbTimer=setTimeout(heartbeatLoop,840); }
function gameHTML(g,r,d,lm){
  const rated=g.m!=null&&g.i!=null&&g.f!=null;
  // clip→表紙の2段構成: クリップは最大5秒、スライドのラスト1秒は表紙を見せる
  const hs=Math.max(0.8, Math.min(5, d/1000-1));
  const meta=[g.genre,g.plat,(g.year?g.year+'年':'')].filter(Boolean).join(' ・ ');
  const metaSp=`<span class="mg">${esc(g.genre)}</span>`+(g.plat?`<span class="mp">${esc(g.plat)}</span>`:'')+(g.year?`<span class="my">${esc(g.year)}年</span>`:'');
  if(lm===1){ // 全面カバー(案F)
    const rev=(TM&&r<=TAME_MAX)?(TM===3?'<div class="curt l"></div><div class="curt r"></div>':'<div class="revflash"></div>'):'';
    return `<div class="slide full ${r===1?'no1':''} ${TM&&r<=TAME_MAX?'rev':''}"><img class="bg" src="${g.img}" alt="" onerror="this.style.opacity=0" style="animation-duration:${(d/1000).toFixed(1)}s">${vid(g,'bg',hs)}
      <div class="scrim"></div><div class="rkF">${r}<span>位</span></div><div class="tierF">${tierOf(r)}</div>
      <div class="botF ts${TS}"><div class="tiF">${esc(g.title)}</div><div class="metaF">${metaSp}</div><div class="introF">${esc(g.intro)}</div></div>
      ${rated?'<div class="radF">'+radar(g)+'</div>':''}${rev}</div>`;
  }
  if(lm===2){ // シネマ(案G)
    return `<div class="slide cine ${r===1?'no1':''}"><div class="lb t"></div><div class="lb b"></div><div class="flash"></div>
      <div class="cineWrap"><div class="cineRk">${r}<span>位</span></div>
        <div class="cineCv"><img src="${g.img}" alt="" onerror="this.style.opacity=0">${vid(g,null,hs)}</div>
        <div class="cineInfo"><div class="tierC">${tierOf(r)}</div><div class="tiC">${esc(g.title)}</div><div class="metaC">${esc(meta)}</div>${rated?'<div class="radC">'+radar(g)+'</div>':''}</div>
      </div></div>`;
  }
  return `<div class="slide ${r===1?'no1':''}"><div class="rk">${r}<span class="rku">位</span></div>
    <div class="mid"><div class="cvwrap"><div class="cvglow"></div><img class="cv" src="${g.img}" alt="" onerror="this.style.opacity=0">${vid(g,'cv',hs)}</div></div>
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
// ===== Part1（200→101位）ラッシュ5案ビルダー =====
function p1meta(g){ return `<span class="mg">${esc(g.genre)}</span>`+(g.plat?`<span class="mp">${esc(g.plat)}</span>`:'')+(g.year?`<span class="my">${esc(g.year)}年</span>`:''); }
function p1oneHTML(g,r){
  const ti=esc(g.title), mt=p1meta(g), intro=esc(g.intro||''), src=g.img, ts='ts'+TS;
  const cap=`<div class="cti">${ti}</div><div class="cmeta">${mt}</div>`+(intro?`<div class="cintro">${intro}</div>`:'');
  if(P1===0){ // ① 全面ブチ抜き
    return `<div class="p1one fb"><img class="fbimg" src="${src}" onerror="this.style.opacity=0">${vid(g,'fbimg')}<div class="fbscrim"></div>
      <div class="fbrk">${r}<span>位</span></div><div class="p1cap fbcap ${ts}">${cap}</div></div>`;
  }
  if(P1===1){ // ② ブラー自己背景
    return `<div class="p1one blur"><img class="bgblur" src="${src}" onerror="this.style.opacity=0"><div class="blurdark"></div>
      <div class="blurcv"><img src="${src}" onerror="this.style.opacity=0">${vid(g)}</div>
      <div class="brk">${r}<span>位</span></div><div class="p1cap blurcap ${ts}">${cap}</div></div>`;
  }
  if(P1===2){ // ③ カード送り
    return `<div class="p1one slide"><div class="slcard"><img src="${src}" onerror="this.style.opacity=0">${vid(g)}</div>
      <div class="slside"><div class="slrk">${r}<span>位</span></div><div class="p1cap slcap ${ts}">${cap}</div></div></div>`;
  }
  if(P1===3){ // ④ シネスコ黒帯
    return `<div class="p1one cs"><div class="csbar t"></div><div class="csbar b"></div><div class="csflash"></div>
      <div class="cswrap"><div class="csrk">${r}<span>位</span></div><div class="cscv"><img src="${src}" onerror="this.style.opacity=0">${vid(g)}</div>
      <div class="p1cap cscap ${ts}">${cap}</div></div></div>`;
  }
  // ⑤ スポットステージ
  return `<div class="p1one st"><div class="stbg"></div><div class="stcv"><img src="${src}" onerror="this.style.opacity=0">${vid(g)}</div>
    <div class="stbot"><div class="strk">${r}<span>位</span></div><div class="p1cap stcap ${ts}">${cap}</div></div></div>`;
}
// ==== オープニング（8秒） ====
function opHTML(d){
  const sd=x=>'animation-delay:'+(d*x/1000).toFixed(2)+'s';
  return `<div class="op">${MOSAIC}<div class="opscrim"></div>
    <div class="opin"><div class="opkicker" style="${sd(.04)}">バトラの</div>
      <div class="optitle" style="${sd(.10)}">思い入れのある<br>ゲームランキング</div>
      <div class="opnum" style="${sd(.28)}">TOP <span>200</span></div></div>
    <div class="opcnt"><span style="${sd(.60)}">3</span><span style="${sd(.73)}">2</span><span style="${sd(.86)}">1</span></div></div>`;
}
// ==== 1位発表直前のTOP10リキャップ ====
function recapHTML(d){
  let cards='';
  for(let r=10;r>=2;r--){ const g=byRank[r]; if(!g)continue; const idx=10-r;
    cards+=`<div class="rcCard" style="animation-delay:${(d*(0.04+idx*0.082)/1000).toFixed(2)}s"><img src="${g.img}"><span class="rcRk">${r}<small>位</small></span></div>`; }
  return `<div class="recap"><div class="rcLabel">ここまでの TOP10</div>${cards}
    <div class="rcDark" style="animation-delay:${(d*0.80/1000).toFixed(2)}s"><div class="rcNext">第 1 位 は ——</div></div></div>`;
}
// ==== TOP3表彰台フィナーレ ====
function podiumHTML(d){
  const g1=byRank[1],g2=byRank[2],g3=byRank[3];
  const box=(g,cls,medal,f)=>g?`<div class="pd ${cls}" style="animation-delay:${(d*f/1000).toFixed(2)}s">
      <div class="pdCv"><img src="${g.img}">${vid(g)}</div><div class="pdMedal">${medal}</div>
      <div class="pdTi">${esc(g.title)}</div><div class="pdBlock"></div></div>`:'';
  return `<div class="podium"><div class="pdLabel">🏆 RESULT</div>
    <div class="pdRow">${box(g2,'silver','🥈 第2位',0.30)}${box(g1,'gold','👑 第1位',0.56)}${box(g3,'bronze','🥉 第3位',0.05)}</div></div>`;
}
// タイトルが長い時は折り返しすぎ・はみ出しを避けて自動縮小（単語単位折返しはCSS側）
function fitEl(el,maxLines){ if(!el) return; el.style.fontSize='';
  const cs=getComputedStyle(el); const lh=parseFloat(cs.lineHeight)||parseFloat(cs.fontSize)*1.2;
  let fs=parseFloat(cs.fontSize),g=0; const maxH=lh*maxLines+2;
  while((el.scrollHeight>maxH||el.scrollWidth>el.clientWidth+1)&&fs>13&&g<60){ fs-=1; el.style.fontSize=fs+'px'; g++; } }
function fitTitles(root){ if(!root) return;
  fitEl(root.querySelector('.cti'),3); fitEl(root.querySelector('.ti'),3);
  fitEl(root.querySelector('.tiF'),3); fitEl(root.querySelector('.tiC'),3); }
function render(s){
  if(s.t==='op'){ const dd=dur(s); stage.innerHTML=opHTML(dd); stage.insertAdjacentHTML('beforeend',sparkleHTML(30));
    se('shine');
    [[.60,'tick'],[.73,'tick'],[.86,'don']].forEach(([f,k])=>setTimeout(()=>{if(document.querySelector('.op'))se(k,k==='don');},dd*f));
    setProgP(0); return; }
  if(s.t==='recap'){ const dd=dur(s); stage.innerHTML=recapHTML(dd); stage.insertAdjacentHTML('beforeend',sparkleHTML(1));
    se('whoosh');
    for(let i=0;i<9;i++) setTimeout(()=>{if(document.querySelector('.recap'))se('tick');},dd*(0.04+i*0.082));
    setTimeout(()=>{if(document.querySelector('.recap'))se('don',true);},dd*0.82);
    setProg(2); return; }
  if(s.t==='podium'){ const dd=dur(s); stage.innerHTML=podiumHTML(dd); stage.insertAdjacentHTML('beforeend',sparkleHTML(1));
    se('shine');
    setTimeout(()=>{if(document.querySelector('.podium'))se('don',true);},dd*0.05);
    setTimeout(()=>{if(document.querySelector('.podium'))se('don',true);},dd*0.30);
    setTimeout(()=>{if(document.querySelector('.podium')){se('fanfare');fireworks(5);confetti(120);}},dd*0.56);
    setProg(1); return; }
  if(s.t==='p1one'){
    if(!stage.querySelector('.p1one')){ stage.innerHTML=p1oneHTML(byRank[s.r],s.r); }
    else { // 暗転せずクロスフェード: 新スライドを上に重ね、旧スライドは少し残してから除去
      stage.insertAdjacentHTML('beforeend', p1oneHTML(byRank[s.r],s.r));
      const sl=stage.querySelectorAll('.p1one'); for(let i=0;i<sl.length-2;i++) sl[i].remove();
      const prev=sl[sl.length-2]; if(prev) setTimeout(()=>{ if(prev.parentNode) prev.remove(); }, 320);
    }
    fitTitles(stage.querySelector('.p1one:last-child'));
    se('tick');
    const nx=byRank[s.r-1]; if(nx){ const im=new Image(); im.src=nx.img; } // 次カバー先読み
    setProg(s.r); return; }
  if(s.t==='b'){const [a,b]=BANNERS[s.r];stage.innerHTML=`<div class="banner bg${BG}">${MOSAIC}<div class="bscrim"></div><div class="bshock"></div><div class="btxt">${a}</div><div class="bsub">${b}</div><div class="bflash"></div>${sparkleHTML(s.r)}</div>`;se('don',true);se('shine');setProg(s.r);return;}
  if(s.t==='tame'){stage.innerHTML=tameHTML(byRank[s.r],s.r,dur(s));stage.insertAdjacentHTML('beforeend',sparkleHTML(s.r));se('don');heartbeatLoop();setProg(s.r);return;}
  const g=byRank[s.r]; stage.innerHTML=gameHTML(g,s.r,dur(s),curLM(s.r));
  stage.insertAdjacentHTML('beforeend',sparkleHTML(s.r));
  fitTitles(stage);
  se('whoosh'); se('don', s.r<=10);
  if(s.r===1){ confetti(140); fireworks(4); se('fanfare'); }
  else if(s.r<=3){ confetti(70); se('shine'); }
  else if(s.r<=10) confetti(34); else if(s.r<=20) confetti(14);
  setProg(s.r);
}
function step(){ if(isFeed()) return; const s=steps[si]; render(s); clearTimeout(timer);
  if(playing) timer=setTimeout(()=>{ if(si<steps.length-1){si++;step();} else {playing=false;updateBtn();} }, dur(s)); updateProg(); }
function updateProg(){const s=steps[si]; let t;
  if(isFeed()) t='フィード再生中';
  else if(s.t==='op') t='オープニング';
  else if(s.t==='recap') t='TOP10リキャップ';
  else if(s.t==='podium') t='表彰台';
  else if(s.t==='p1one') t='前半 '+s.r+'位 / 残り'+Math.max(0,steps.length-1-si);
  else t=(s.t==='b'?'—':s.r+'位'+(s.t==='tame'?'(タメ)':''))+' / 残り'+Math.max(0,steps.length-1-si);
  document.getElementById('prog').textContent=t;}
function updateBtn(){document.getElementById('pp').textContent=playing?'⏸':'▶';}
function play(){ if(isFeed())return; playing=true; updateBtn(); step(); }
function pause(){ playing=false; clearTimeout(timer); updateBtn(); }
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
document.getElementById('rs').onclick=()=>{ if(isFeed()){cancelAnimationFrame(feedRAF);buildFeed();return;} si=0; playing=true; updateBtn(); step(); };
document.getElementById('nx').onclick=()=>{if(isFeed())return;if(si<steps.length-1){si++;pause();render(steps[si]);updateProg();}};
document.getElementById('pv').onclick=()=>{if(isFeed())return;if(si>0){si--;pause();render(steps[si]);updateProg();}};
document.getElementById('sp').onchange=e=>{mult=+e.target.value;};
document.getElementById('lm').onclick=()=>{ mode=(mode+1)%5; cancelAnimationFrame(feedRAF);
  if(mode===0){AUTO=true;document.getElementById('lm').textContent='オート';}
  else{AUTO=false;LM=mode-1;document.getElementById('lm').textContent=LMN[LM];}
  if(isFeed()){ pause(); buildFeed(); updateProg(); } else { render(steps[si]); updateProg(); } };
document.getElementById('p1').onclick=()=>{ P1=(P1+1)%5; document.getElementById('p1').textContent='前半'+P1N[P1];
  cancelAnimationFrame(feedRAF); buildSteps(); si=0; pause(); render(steps[si]); updateProg(); };
document.getElementById('se').onclick=()=>{ SEon=!SEon; actx(); document.getElementById('se').textContent=SEon?'SE ON':'SE OFF'; if(SEon)se('shine'); };
document.getElementById('ts').onclick=()=>{TS=(TS+1)%3;document.getElementById('ts').textContent='文字'+['A','B','C'][TS];if(!isFeed())render(steps[si]);};
document.getElementById('bg').onclick=()=>{BG=(BG+1)%3;document.getElementById('bg').textContent='背景'+['A','B','C'][BG];cancelAnimationFrame(feedRAF);pause();si=steps.findIndex(s=>s.t==='b'&&s.r===20);render(steps[si]);updateProg();};
document.getElementById('tame').onclick=()=>{ const cr=steps[si]?steps[si].r:100;
  TM=(TM+1)%4; document.getElementById('tame').textContent='タメ'+TMN[TM]; buildSteps();
  const tr=(TM&&cr>TAME_MAX)?15:cr; let i=steps.findIndex(s=>s.r===tr&&s.t==='tame'); if(i<0)i=steps.findIndex(s=>s.r===tr&&s.t==='g'); if(i<0)i=0;
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
  #frame{position:relative;width:min(98vw,calc(90vh*16/9));aspect-ratio:16/9;border-radius:20px;overflow:hidden;box-shadow:0 24px 70px rgba(0,0,0,.6);border:3px solid rgba(255,255,255,.14);container-type:size}
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
  .ti{font-family:"Mochiy Pop One";font-size:clamp(20px,5.6cqmin,52px);line-height:1.15;text-shadow:0 3px 10px rgba(0,0,0,.35)}
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
  .tiF{font-family:"Mochiy Pop One";font-size:clamp(17px,4.2cqmin,40px);line-height:1.26}
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
  .tiC{font-family:"Mochiy Pop One";font-size:clamp(17px,4.4cqmin,42px);line-height:1.16;margin-top:8px;text-shadow:0 3px 10px rgba(0,0,0,.4)}
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
  /* ===== Part1（200→101位）ラッシュ5案 ===== */
  .p1one{position:absolute;inset:0;overflow:hidden;background:#070310;animation:p1in .3s ease backwards}
  .p1one img{display:block}
  @keyframes p1in{from{opacity:0}to{opacity:1}}
  @keyframes ctrin{from{transform:translate(-50%,-50%) scale(.93)}to{transform:translate(-50%,-50%) scale(1)}}
  @keyframes fbin{from{transform:scale(1.06)}to{transform:none}}
  @keyframes slcin{from{transform:translate(36%,-50%)}to{transform:translate(-50%,-50%)}}
  @keyframes csin{from{transform:translateX(40px)}to{transform:none}}
  @keyframes csbarin{from{height:50%}to{}}
  /* ① 全面ブチ抜き */
  .p1one.fb .fbimg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;animation:fbin .45s ease backwards}
  .p1one.fb .fbscrim{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.5) 0%,rgba(0,0,0,0) 18%,rgba(0,0,0,0) 36%,rgba(0,0,0,.95) 100%)}
  .p1one.fb .fbrk{position:absolute;top:3%;left:4%;font-family:"Baloo 2";font-weight:800;font-size:clamp(60px,18vh,240px);line-height:.82;color:#fff;text-shadow:0 4px 24px rgba(0,0,0,.9);animation:rkin .45s cubic-bezier(.2,1.5,.3,1) backwards}
  .p1one.fb .fbrk span{font-size:.3em}
  .p1one.fb .fbcap{position:absolute;left:4%;right:4%;bottom:4.5%;animation:infin .5s ease .08s backwards}
  /* ② ブラー自己背景 */
  .p1one.blur .bgblur{position:absolute;inset:-8%;width:116%;height:116%;object-fit:cover;filter:blur(34px) saturate(1.25);animation:fbin .45s ease backwards}
  .p1one.blur .blurdark{position:absolute;inset:0;background:rgba(8,5,18,.55)}
  .p1one.blur .blurcv{position:absolute;top:37%;left:50%;transform:translate(-50%,-50%);height:64%;aspect-ratio:3/4;border-radius:16px;overflow:hidden;border:4px solid rgba(255,255,255,.95);box-shadow:0 22px 64px rgba(0,0,0,.65);animation:ctrin .5s cubic-bezier(.2,1.2,.3,1) backwards}
  .p1one.blur .blurcv img{width:100%;height:100%;object-fit:cover}
  .p1one.blur .brk{position:absolute;top:3%;left:4%;z-index:2;font-family:"Baloo 2";font-weight:800;font-size:clamp(50px,13vh,170px);line-height:.82;color:#fff;text-shadow:0 4px 22px rgba(0,0,0,.85);animation:rkin .45s cubic-bezier(.2,1.5,.3,1) backwards}
  .p1one.blur .brk span{font-size:.3em}
  .p1one.blur .blurcap{position:absolute;left:0;right:0;bottom:3%;z-index:2;padding:0 6%;text-align:center;animation:infin .5s ease .08s backwards}
  .p1one.blur .blurcap .cmeta{justify-content:center}
  #frame.vert .p1one.blur .blurcv{height:48%;top:31%}
  /* ③ カード送り */
  .p1one.slide{background:radial-gradient(120% 90% at 50% 28%,#241a3e,#0b0716)}
  .p1one.slide .slcard{position:absolute;top:50%;left:39%;transform:translate(-50%,-50%);height:82%;aspect-ratio:3/4;border-radius:16px;overflow:hidden;border:4px solid #fff;box-shadow:0 22px 64px rgba(0,0,0,.65);animation:slcin .5s cubic-bezier(.2,1.1,.3,1) backwards}
  .p1one.slide .slcard img{width:100%;height:100%;object-fit:cover}
  .p1one.slide .slside{position:absolute;right:4%;top:50%;transform:translateY(-50%);width:36%;animation:infin .5s ease .12s backwards}
  .p1one.slide .slrk{font-family:"Baloo 2";font-weight:800;font-size:clamp(50px,14vh,180px);line-height:.82;color:#fff;text-shadow:0 5px 0 rgba(0,0,0,.22),0 0 26px rgba(255,255,255,.4)}
  .p1one.slide .slrk span{font-size:.28em}
  .p1one.slide .slcap{margin-top:8px}
  #frame.vert .p1one.slide .slcard{left:50%;height:52%;top:36%}
  #frame.vert .p1one.slide .slside{left:0;right:0;top:auto;bottom:4%;width:100%;text-align:center;transform:none}
  #frame.vert .p1one.slide .slcap .cmeta{justify-content:center}
  /* ④ シネスコ黒帯 */
  .p1one.cs{background:#000}
  .p1one.cs .csbar{position:absolute;left:0;right:0;height:10%;background:#000;z-index:3}
  .p1one.cs .csbar.t{top:0;animation:csbarin .5s ease backwards}
  .p1one.cs .csbar.b{bottom:0;animation:csbarin .5s ease backwards}
  .p1one.cs .csflash{position:absolute;inset:0;background:#fff;z-index:4;opacity:0;animation:fl .45s ease forwards;pointer-events:none}
  .p1one.cs .cswrap{position:absolute;inset:0;height:100%;display:flex;align-items:center;justify-content:center;gap:4%;padding:0 6%}
  .p1one.cs .csrk{position:absolute;top:11%;left:5%;z-index:2;font-family:"Baloo 2";font-weight:800;font-size:clamp(44px,13vh,170px);line-height:.82;color:#fff;text-shadow:0 0 30px rgba(255,255,255,.4);animation:flashin .5s cubic-bezier(.2,1.6,.3,1) backwards}
  .p1one.cs .csrk span{font-size:.28em}
  .p1one.cs .cscv{flex:none;height:70%;aspect-ratio:3/4;border-radius:12px;overflow:hidden;border:4px solid #fff;box-shadow:0 16px 48px rgba(0,0,0,.7);animation:csin .5s cubic-bezier(.2,1.2,.3,1) backwards}
  .p1one.cs .cscv img{width:100%;height:100%;object-fit:cover}
  .p1one.cs .cscap{flex:1;max-width:42%;animation:infin .5s ease .15s backwards}
  #frame.vert .p1one.cs .csbar{display:none}#frame.vert .p1one.cs .cswrap{flex-direction:column;gap:2%}#frame.vert .p1one.cs .csrk{top:5%;left:6%;font-size:clamp(34px,7vh,92px)}#frame.vert .p1one.cs .cscap{max-width:90%;text-align:center}#frame.vert .p1one.cs .cscap .cmeta{justify-content:center}#frame.vert .p1one.cs .cscv{height:44%}
  /* ⑤ スポットステージ */
  .p1one.st .stbg{position:absolute;inset:0;background:radial-gradient(58% 70% at 50% 16%,rgba(255,244,214,.24),rgba(10,7,20,0) 56%),radial-gradient(120% 100% at 50% 52%,#1b1532,#070310 82%)}
  .p1one.st .stcv{position:absolute;top:39%;left:50%;transform:translate(-50%,-50%);height:60%;aspect-ratio:3/4;border-radius:16px;overflow:hidden;border:4px solid rgba(255,255,255,.92);box-shadow:0 0 64px rgba(255,221,140,.32),0 26px 72px rgba(0,0,0,.7);animation:ctrin .6s cubic-bezier(.2,1.1,.3,1) backwards}
  .p1one.st .stcv img{width:100%;height:100%;object-fit:cover}
  .p1one.st .stbot{position:absolute;left:0;right:0;bottom:3.5%;text-align:center;padding:0 6%;animation:infin .5s ease .15s backwards}
  .p1one.st .strk{font-family:"Baloo 2";font-weight:800;font-size:clamp(34px,7.5vh,104px);line-height:.82;color:var(--gold);text-shadow:0 0 30px rgba(255,200,80,.5)}
  .p1one.st .strk span{font-size:.3em;color:#fff}
  .p1one.st .stcap .cmeta{justify-content:center}
  #frame.vert .p1one.st .stcv{height:46%;top:34%}
  /* Part1 共通キャプション（紹介文/ジャンル/年・文字A/B/C対応） */
  .p1cap .cti{font-family:"Mochiy Pop One";font-size:clamp(18px,5.4cqmin,48px);line-height:1.14}
  .p1cap .cmeta{display:flex;gap:7px;flex-wrap:wrap;align-items:center;font-weight:800;font-size:clamp(12px,1.7vw,23px);margin-top:7px}
  .p1cap .cintro{font-weight:700;font-size:clamp(12px,1.6vw,21px);line-height:1.48;margin-top:6px;opacity:.97;word-break:auto-phrase;overflow-wrap:break-word}
  .p1cap.ts0{background:rgba(12,8,28,.55);border:1.5px solid rgba(255,255,255,.3);border-radius:16px;padding:12px 16px}
  .p1cap.ts0 .mg{color:#ffd23f}.p1cap.ts0 .my{color:#7fd7ff}.p1cap.ts0 .mp{color:#5cf0c8}
  .p1cap.ts1 .cti,.p1cap.ts1 .cmeta span,.p1cap.ts1 .cintro{text-shadow:-1.5px -1.5px 0 #160d2a,1.5px -1.5px 0 #160d2a,-1.5px 1.5px 0 #160d2a,1.5px 1.5px 0 #160d2a,0 3px 10px rgba(0,0,0,.95)}
  .p1cap.ts1 .mg{color:#ff8ad1}.p1cap.ts1 .my{color:#ffe14d}.p1cap.ts1 .mp{color:#7dffb0}
  .p1cap.ts2{border-left:6px solid #ff5ea8;border-radius:0 14px 14px 0;background:linear-gradient(90deg,rgba(0,0,0,.62),rgba(0,0,0,.05));padding:10px 14px}
  .p1cap.ts2 .cmeta span{padding:3px 12px;border-radius:999px;font-size:.92em}
  .p1cap.ts2 .mg{background:#ffd23f;color:#5a3d00}.p1cap.ts2 .my{background:#36c5ff;color:#06324f}.p1cap.ts2 .mp{background:#3ff2c2;color:#064b3a}
  /* タイトルは単語単位で折り返し（中途半端な改行を防止）＋はみ出しは自動縮小(JS) */
  .ti,.tiF,.tiC,.p1cap .cti{word-break:auto-phrase;overflow-wrap:break-word;line-break:strict}
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
  /* 常時のキラキラ（後半100→1位・段階豪華化） */
  .spkwrap{position:absolute;inset:0;overflow:hidden;pointer-events:none;z-index:6}
  .spk{position:absolute;border-radius:50%;opacity:0;animation:spkTwinkle ease-in-out infinite}
  @keyframes spkTwinkle{0%{opacity:0;transform:scale(.3) rotate(0deg)}50%{opacity:1;transform:scale(1.2) rotate(90deg)}100%{opacity:0;transform:scale(.3) rotate(180deg)}}
  .spkwrap.t1 .spk{box-shadow:0 0 4px rgba(255,255,255,.7)}
  .spkwrap.t2 .spk{box-shadow:0 0 8px rgba(255,255,255,.85)}
  .spkwrap.t3 .spk{box-shadow:0 0 14px rgba(255,210,63,.9),0 0 4px #fff}
  /* canvas花火 */
  .fw{position:absolute;inset:0;width:100%;height:100%;z-index:7;pointer-events:none}
  /* 実機動画クリップのオーバーレイ（img の上に重なる。onerror で自滅→表紙に戻る） */
  .cvwrap video,.cineCv video,.blurcv video,.slcard video,.cscv video,.stcv video,.pdCv video{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;z-index:1}
  .cineCv{position:relative}.p1one.cs .cscv{position:relative}
  .slide.full video.bg{animation:none}
  /* clip→表紙の2段構成: hideS秒後にクリップがフェードアウトして下の表紙が見える */
  @keyframes clipHide{to{opacity:0;visibility:hidden}}
  /* ===== オープニング ===== */
  .op{position:absolute;inset:0;overflow:hidden;background:#12092a}
  .op .bgrid{filter:blur(6px) brightness(.45) saturate(.9)}
  .opscrim{position:absolute;inset:0;background:radial-gradient(110% 85% at 50% 42%,rgba(18,9,42,.25),rgba(18,9,42,.9))}
  .opin{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:1.6vh;text-align:center;z-index:2;padding:0 6%}
  .opkicker{font-weight:800;font-size:clamp(15px,3.4cqmin,30px);letter-spacing:6px;color:#ffd9f0;opacity:0;animation:tmIn .5s ease forwards;text-shadow:0 2px 12px rgba(0,0,0,.7)}
  .optitle{font-family:"Mochiy Pop One";font-size:clamp(26px,7.2cqmin,64px);line-height:1.24;color:#fff;text-shadow:0 5px 0 rgba(0,0,0,.22),0 0 34px rgba(255,255,255,.5);opacity:0;animation:opIn .6s cubic-bezier(.16,.9,.3,1.05) forwards}
  .opnum{font-family:"Baloo 2";font-weight:800;font-size:clamp(40px,12cqmin,120px);line-height:.9;color:#fff;opacity:0;animation:opIn .55s cubic-bezier(.16,.9,.3,1.05) forwards}
  @keyframes opIn{0%{opacity:0;transform:scale(2.6);filter:blur(12px)}60%{opacity:1}80%{transform:scale(.94)}100%{opacity:1;transform:scale(1);filter:none}}
  .opnum span{color:var(--gold);text-shadow:0 0 40px rgba(255,184,0,.8);font-size:1.25em}
  .opcnt{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;z-index:3;pointer-events:none}
  .opcnt span{position:absolute;font-family:"Baloo 2";font-weight:800;font-size:clamp(110px,42cqmin,420px);color:#fff;opacity:0;text-shadow:0 0 60px rgba(255,255,255,.75);animation:opCnt .9s cubic-bezier(.2,.9,.3,1) forwards}
  @keyframes opCnt{0%{opacity:0;transform:scale(2.6)}22%{opacity:1;transform:scale(1)}78%{opacity:1}100%{opacity:0;transform:scale(.72)}}
  /* ===== TOP10リキャップ ===== */
  .recap{position:absolute;inset:0;overflow:hidden;background:radial-gradient(120% 90% at 50% 30%,#241a3e,#0a0616)}
  .rcLabel{position:absolute;top:4.5%;left:0;right:0;text-align:center;font-family:"Mochiy Pop One";font-size:clamp(18px,4.4cqmin,40px);color:#ffd23f;text-shadow:0 3px 0 rgba(0,0,0,.25),0 0 22px rgba(255,210,63,.5);z-index:2}
  .rcCard{position:absolute;top:50%;left:50%;width:min(56cqw,46cqh);aspect-ratio:3/4;transform:translate(-50%,-50%);border-radius:14px;overflow:hidden;border:4px solid #fff;box-shadow:0 18px 50px rgba(0,0,0,.6);opacity:0;animation:rcFlash .62s ease both}
  .rcCard img{width:100%;height:100%;object-fit:cover}
  .rcCard .rcRk{position:absolute;left:0;top:0;background:rgba(0,0,0,.72);color:#fff;font-family:"Baloo 2";font-weight:800;font-size:clamp(20px,5cqmin,44px);padding:2px 14px;border-bottom-right-radius:14px}
  .rcCard .rcRk small{font-size:.5em}
  @keyframes rcFlash{0%{opacity:0;transform:translate(-50%,-50%) scale(.55) rotate(-5deg)}18%{opacity:1;transform:translate(-50%,-50%) scale(1.02) rotate(0)}82%{opacity:1;transform:translate(-50%,-50%) scale(1.05)}100%{opacity:0;transform:translate(-50%,-50%) scale(1.18)}}
  .rcDark{position:absolute;inset:0;background:#05020c;display:flex;align-items:center;justify-content:center;opacity:0;z-index:3;animation:rcDarkIn .7s ease forwards}
  @keyframes rcDarkIn{to{opacity:1}}
  .rcNext{font-family:"Mochiy Pop One";font-size:clamp(24px,6.4cqmin,60px);color:#fff;letter-spacing:2px;text-shadow:0 0 34px rgba(255,255,255,.5);animation:tmIn .6s ease .35s both}
  /* ===== TOP3表彰台 ===== */
  .podium{position:absolute;inset:0;overflow:hidden;background:radial-gradient(70% 55% at 50% 12%,rgba(255,240,200,.20),rgba(10,6,20,0) 58%),radial-gradient(130% 100% at 50% 55%,#221740,#070310 84%)}
  .pdLabel{position:absolute;top:3.6%;left:0;right:0;text-align:center;font-family:"Baloo 2";font-weight:800;letter-spacing:6px;font-size:clamp(20px,5cqmin,46px);color:var(--gold);text-shadow:0 0 26px rgba(255,184,0,.6);z-index:2}
  .pdRow{position:absolute;left:3%;right:3%;bottom:6%;display:flex;align-items:flex-end;justify-content:center;gap:2.5%}
  .pd{flex:1;max-width:31%;display:flex;flex-direction:column;align-items:center;gap:.8vh;opacity:0;animation:pdIn .7s cubic-bezier(.2,1.25,.3,1) both}
  @keyframes pdIn{from{opacity:0;transform:translateY(60px) scale(.75)}to{opacity:1;transform:none}}
  .pdCv{position:relative;width:100%;aspect-ratio:3/4;border-radius:12px;overflow:hidden;border:4px solid #fff;box-shadow:0 14px 40px rgba(0,0,0,.6)}
  .pdCv img{width:100%;height:100%;object-fit:cover}
  .pdMedal{font-weight:800;font-size:clamp(14px,3.2cqmin,28px);color:#fff;text-shadow:0 2px 10px rgba(0,0,0,.7)}
  .pdTi{font-family:"Mochiy Pop One";font-size:clamp(11px,2.4cqmin,20px);line-height:1.25;text-align:center;color:#fff;text-shadow:0 2px 10px rgba(0,0,0,.8);display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
  .pdBlock{width:86%;border-radius:8px 8px 0 0;background:linear-gradient(180deg,rgba(255,255,255,.34),rgba(255,255,255,.08));border:2px solid rgba(255,255,255,.35);border-bottom:0}
  .pd.gold{max-width:36%;z-index:2}
  .pd.gold .pdCv{border-color:var(--gold);box-shadow:0 0 0 5px rgba(255,184,0,.45),0 0 54px rgba(255,184,0,.45),0 18px 50px rgba(0,0,0,.6)}
  .pd.gold .pdBlock{height:13cqh;background:linear-gradient(180deg,rgba(255,210,63,.6),rgba(255,184,0,.16));border-color:rgba(255,220,120,.7)}
  .pd.gold .pdMedal{color:var(--gold);font-size:clamp(17px,4cqmin,34px)}
  .pd.silver .pdBlock{height:8.5cqh}
  .pd.bronze .pdBlock{height:6cqh;background:linear-gradient(180deg,rgba(224,148,86,.5),rgba(224,148,86,.12));border-color:rgba(230,170,110,.55)}
  .ctl{display:flex;gap:7px;align-items:center;flex-wrap:wrap;justify-content:center;background:rgba(255,255,255,.08);padding:8px 14px;border-radius:999px;max-width:98vw}
  .ctl button{font:inherit;font-weight:800;border:0;border-radius:999px;padding:8px 13px;cursor:pointer;background:rgba(255,255,255,.92);color:#2a1a4a}
  .ctl .prog{color:#fff;font-weight:800;font-size:13px;min-width:118px;text-align:center}
  .ctl select{font:inherit;border-radius:999px;border:0;padding:7px 10px;font-weight:800}
  .hint{color:rgba(255,255,255,.6);font-size:12px;font-weight:700;text-align:center}
</style></head><body>
  <div id="frame" class="vert"><div id="stage"></div><div id="pbar"><div id="pfill"></div></div></div>
  <div class="ctl">
    <button id="pv">⏮</button><button id="pp">⏸</button><button id="nx">⏭</button><button id="rs">↺ 最初から</button>
    <span class="prog" id="prog">—</span>
    速度<select id="sp"><option value="1.5">ゆっくり</option><option value="1" selected>標準(4分)</option><option value="0.6">速い</option></select>
    <button id="p1">前半①全面</button><button id="lm">全面カバー</button><button id="ts">文字B</button><button id="tame">タメ案B</button><button id="bg">背景A</button><button id="or">縦 9:16</button><button id="se">SE ON</button><button id="fs">⛶ 全画面</button><button id="mu">🔇</button>
  </div>
  <div class="hint">構成＝<b>オープニング(8秒)→前半200→101位を高速→後半100→1位→TOP10リキャップ→1位→🏆表彰台フィナーレ</b>（全体約4分半）。既定は<b>縦9:16・全面カバー・前半①全面</b>。<b>game_clips/c番号.mp4</b>を置くとそのゲームは表紙の代わりに<b>実機映像</b>が流れる（無ければ表紙）。<b>「前半」</b>で見せ方巡回、<b>「レイアウト」</b>で後半切替、<b>「タメ」</b>でTOP20の正体伏せ、<b>「SE」</b>で効果音（初回はどれかボタンを押すと音が出ます）。⛶全画面→画面収録で動画化。BGMは movie_bgm.mp3。</div>
  <audio id="bgm" src="movie_bgm.mp3" loop></audio>
  <script src="movie.js"></script>
</body></html>'''
open("movie.html", "w", encoding="utf-8").write(HTML)
p1n = sum(1 for g in games if g["rank"] > 100)
clips = sum(1 for g in games if g.get("clip"))
print(f"movie.html + movie.js 生成（前半{p1n}作+後半100作=計{len(games)}作・OP/リキャップ/表彰台つき・実機クリップ{clips}本）")
