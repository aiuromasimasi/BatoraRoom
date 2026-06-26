#!/usr/bin/env python3
"""game_ranking_draft.md の順位たたき台から game.html を生成する。
- 順位(1-100) / ジャンル絵文字 / tier を自動マッピング
- カバー画像は game_covers/<順位>.jpg を参照。無ければジャンル別カラータイルにフォールバック
- 画像はカラータイル上に contain 表示（横長ロゴでも綺麗）。読み込めたらプレースホルダーを隠す
使い方: python3 build_game_html.py
"""
import re, html, csv, json, os

src = open("game_ranking_draft.md", encoding="utf-8").read()
lines = src.split("\n")

emoji_map = {
    "ゼルダ/任天堂": "🎮", "JRPG": "⚔️", "ノベル": "📖", "STG": "🚀", "FPS": "🔫",
    "PC洋ゲー": "🖥️", "パズル": "🎯", "インディー": "🌟", "アクション/アーケード": "🕹️",
}
def emoji_for(header):
    for k, v in emoji_map.items():
        if k in header:
            return v
    return "🎮"

genre = {}
title2cid = {}        # タイトル -> 固定ID（確定候補セクションの並び順。順位が変わっても不変）
_cid = 0
cur = "🎮"
for l in lines:
    if l.startswith("---"):
        break
    if l.startswith("### "):
        cur = emoji_for(l[4:])
    elif l.startswith("- "):
        t = l[2:].strip()
        genre[t] = cur
        _cid += 1
        title2cid[t] = _cid

rank = {}
for l in lines:
    m = re.match(r'^(\d+)\.\s+(.*)$', l)
    if m:
        rank[int(m.group(1))] = m.group(2).strip()
assert len(rank) == 100 and set(rank) == set(range(1, 101)), "ranking not 1..100"

# games_data.csv から各ゲームの紹介・評価値を読み込む（cidをキーに。順位が変わっても不変）
gdata = {}
if os.path.exists("games_data.csv"):
    with open("games_data.csv", encoding="utf-8-sig") as _f:
        for row in csv.DictReader(_f):
            mm = re.search(r'c(\d+)\.jpg', row.get("画像", ""))
            if not mm:
                continue
            def _n(x):
                x = (x or "").strip()
                return int(x) if x.isdigit() else None
            gdata[int(mm.group(1))] = {
                "t": row.get("タイトル", "").strip(),
                "intro": row.get("ゲーム紹介", "").strip(),
                "genre": row.get("ジャンル", "").strip(),
                "year": row.get("発売年", "").strip(),
                "plat": row.get("プラットフォーム", "").strip(),
                "played": row.get("主に遊んだ年", "").strip(),
                "m": _n(row.get("思い入れ度")), "i": _n(row.get("衝撃度")), "f": _n(row.get("面白さ")),
                "r": _n(row.get("ストーリー")), "mu": _n(row.get("音楽・サウンド")),
            }
GD_JSON = json.dumps(gdata, ensure_ascii=False)

def hue(r):
    return (r * 37) % 360

def fig(r, tier):
    t = rank[r]; e = genre.get(t, "🎮"); th = html.escape(t); c = title2cid[t]
    return (f'<figure class="m {tier}" data-cid="{c}" style="--i:{r};--h:{hue(r)}">'
            f'<span class="rk">{r}</span>'
            f'<span class="cv"><span class="ph"><span class="pe">{e}</span><span class="pt">{th}</span></span>'
            f'<img loading="lazy" alt="{th}" src="game_covers/c{c}.jpg" onerror="this.remove()"></span>'
            f'<figcaption class="ti">{th}</figcaption></figure>')

def section(tier, lo, hi, bemo, h2, p):
    figs = "\n".join(fig(r, tier) for r in range(hi, lo - 1, -1))
    return (f'<section class="tier {tier}">\n'
            f'  <div class="banner"><span class="bemo">{bemo}</span><div><h2>{h2}</h2><p>{p}</p></div></div>\n'
            f'  <div class="grid">\n{figs}\n  </div>\n</section>')

sections = [
    section("t100", 51, 100, "🕹️", "BEST 100", "100位 → 51位　ウォームアップ！"),
    section("t50", 21, 50, "🔥", "BEST 50", "50位 → 21位　ここから本気♪"),
    section("t20", 11, 20, "💎", "BEST 20", "20位 → 11位　神ゲーぞろい！"),
    section("t10", 4, 10, "🏆", "TOP 10", "10位 → 4位　殿堂入り！"),
    section("t3", 2, 3, "🥈", "BEST 3", "3位・2位　表彰台！"),
]

t1 = rank[1]; e1 = genre.get(t1, "🎮"); t1h = html.escape(t1)
spark = ''.join(f'<span style="--n:{n}">✨</span>' for n in range(14))
hero = f'''<section class="tier t1" id="no1">
  <div class="spark">{spark}</div>
  <div class="crownwrap"><div class="crown">👑</div><div class="no1label">第 1 位</div></div>
  <figure class="herocard" data-cid="{title2cid[t1]}">
    <div class="heroglow"></div>
    <span class="cv" style="--h:{hue(1)}"><span class="ph"><span class="pe">{e1}</span><span class="pt">{t1h}</span></span><img alt="{t1h}" src="game_covers/c{title2cid[t1]}.jpg" onerror="this.remove()"></span>
    <figcaption>
      <span class="no1tag">堂々の N o . 1 🎉</span>
      <h2 class="herotitle">{t1h}</h2>
      <p class="herosub">バトラの「思い入れのあるゲーム」第1位はコレ！</p>
    </figcaption>
  </figure>
</section>'''

CSS = '''  :root{--pink:#ff5ea8;--purple:#9b5cff;--blue:#36c5ff;--yellow:#ffd23f;--mint:#3ff2c2;--orange:#ff8a3d;--gold:#ffb800;--ink:#2a1a4a;}
  *{margin:0;padding:0;box-sizing:border-box}
  html{scroll-behavior:smooth}
  body{font-family:"M PLUS Rounded 1c","Baloo 2",sans-serif;color:var(--ink);
    background:linear-gradient(135deg,#ffd6ec,#d6e4ff,#d9fff4,#fff3c4,#ffd6ec);
    background-size:400% 400%;animation:bg 22s ease infinite;overflow-x:hidden;padding-bottom:60px}
  @keyframes bg{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
  @keyframes pop{from{transform:scale(.6) translateY(10px);opacity:0}to{transform:scale(1);opacity:1}}
  @keyframes floaty{0%,100%{transform:translateY(0)}50%{transform:translateY(-10px)}}
  @keyframes wob{0%,100%{transform:rotate(-3deg)}50%{transform:rotate(3deg)}}
  @keyframes shine{0%{background-position:0% 50%}100%{background-position:200% 50%}}
  @keyframes spin{to{transform:rotate(360deg)}}
  @keyframes sparkle{0%,100%{transform:scale(.4);opacity:0}50%{transform:scale(1.2);opacity:1}}

  header{text-align:center;padding:52px 16px 6px}
  .title{font-family:"Mochiy Pop One",sans-serif;font-size:clamp(28px,7vw,58px);line-height:1.12;
    background:linear-gradient(90deg,var(--pink),var(--orange),var(--yellow),var(--mint),var(--blue),var(--purple),var(--pink));
    background-size:200% auto;-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;
    filter:drop-shadow(0 3px 0 rgba(255,255,255,.8));animation:shine 6s linear infinite}
  .title .em{-webkit-text-fill-color:initial;display:inline-block;animation:wob 2.5s ease-in-out infinite}
  .sub{margin-top:12px;font-weight:800;color:#6a4d8a;font-size:clamp(14px,3.6vw,17px)}
  .hint{margin:14px auto 0;max-width:560px;background:rgba(255,255,255,.9);border:3px solid #fff;border-radius:20px;
    padding:12px 16px;font-weight:700;color:var(--ink);line-height:1.6;box-shadow:0 10px 24px rgba(155,92,255,.18)}
  .hint b{color:var(--pink)}
  .scroll{margin-top:14px;font-weight:800;color:var(--purple);font-size:14px;animation:floaty 2s ease-in-out infinite}

  .tier{max-width:1180px;margin:0 auto;padding:14px 16px 8px;position:relative}
  .banner{position:sticky;top:8px;z-index:10;display:inline-flex;align-items:center;gap:12px;margin:18px 0 16px;
    padding:10px 22px 10px 14px;border-radius:999px;background:rgba(255,255,255,.92);border:3px solid #fff;
    box-shadow:0 10px 24px rgba(58,36,86,.18)}
  .banner .bemo{font-size:30px;animation:floaty 4s ease-in-out infinite}
  .banner h2{font-family:"Mochiy Pop One",sans-serif;font-size:clamp(18px,4.4vw,26px);line-height:1.1;
    background:linear-gradient(90deg,var(--purple),var(--pink));-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
  .banner p{font-weight:800;color:#6a4d8a;font-size:12.5px;margin-top:2px}

  .grid{display:grid;gap:14px}
  .m{position:relative;background:#fff;border-radius:16px;padding:8px;box-shadow:0 8px 18px rgba(58,36,86,.16);
    animation:pop .5s backwards;transition:transform .16s,box-shadow .16s;display:flex;flex-direction:column}
  .m:hover{transform:translateY(-6px) rotate(-1deg);box-shadow:0 18px 34px rgba(58,36,86,.28);z-index:5}
  .m .cv{position:relative;display:block;border-radius:10px;overflow:hidden;aspect-ratio:3/4;
    background:linear-gradient(150deg,hsl(var(--h,200),85%,70%),hsl(calc(var(--h,200) + 48),88%,56%))}
  .m .cv .ph{position:absolute;inset:0;z-index:0;display:flex;flex-direction:column;align-items:center;justify-content:center;
    gap:6px;padding:8px;text-align:center}
  .m .cv .ph .pe{font-size:34px;line-height:1;filter:drop-shadow(0 3px 5px rgba(0,0,0,.28))}
  .m .cv .ph .pt{font-weight:800;font-size:11px;line-height:1.3;color:#fff;text-shadow:0 2px 6px rgba(0,0,0,.45)}
  .m .cv img{position:absolute;inset:0;z-index:1;width:100%;height:100%;object-fit:contain;display:block;padding:6px}
  .m.has-cover .cv img{object-fit:cover;padding:0}
  .m .rk{position:absolute;top:-8px;left:-8px;z-index:3;min-width:30px;height:30px;padding:0 7px;border-radius:999px;
    display:grid;place-items:center;font-family:"Baloo 2";font-weight:800;color:#fff;font-size:14px;
    background:linear-gradient(135deg,var(--blue),var(--purple));box-shadow:0 4px 8px rgba(58,36,86,.25)}
  .m .ti{margin-top:7px;font-weight:800;font-size:12px;line-height:1.35;color:var(--ink);text-align:center;
    display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;min-height:2.6em}

  /* ===== tier sizing: 1位に近づくほど大きく豪華に ===== */
  .t100 .grid{grid-template-columns:repeat(auto-fill,minmax(118px,1fr))}
  .t50  .grid{grid-template-columns:repeat(auto-fill,minmax(150px,1fr))}
  .t20  .grid{grid-template-columns:repeat(auto-fill,minmax(190px,1fr))}
  .t10  .grid{grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:20px}
  .t3   .grid{grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:26px;max-width:760px;margin:0 auto}

  .t50 .m .ti,.t20 .m .ti{font-size:13px}
  .t10 .m{padding:10px;border-radius:20px}
  .t10 .m .ti{font-size:15px}
  .t10 .m .cv .ph .pe{font-size:48px}.t10 .m .cv .ph .pt{font-size:14px}
  .t10 .m .rk{height:38px;min-width:38px;font-size:18px;background:linear-gradient(135deg,var(--orange),var(--pink));
    box-shadow:0 0 0 3px #fff,0 6px 14px rgba(255,138,61,.5)}
  .t10{background:radial-gradient(120% 120% at 50% 0,rgba(255,210,63,.35),transparent 60%);border-radius:32px}

  /* 表彰台 2・3位 */
  .t3{background:radial-gradient(120% 120% at 50% 0,rgba(255,184,0,.45),transparent 62%);border-radius:36px;padding-top:24px}
  .t3 .m{padding:14px;border-radius:26px;border:4px solid #fff;
    box-shadow:0 0 0 4px rgba(255,184,0,.35),0 18px 36px rgba(58,36,86,.3)}
  .t3 .m .cv{border-radius:18px}
  .t3 .m .cv .ph .pe{font-size:64px}.t3 .m .cv .ph .pt{font-size:18px}
  .t3 .m .ti{font-size:18px;min-height:auto;margin-top:12px}
  .t3 .m .rk{height:50px;min-width:50px;font-size:24px;top:-14px;left:50%;transform:translateX(-50%);
    background:linear-gradient(135deg,var(--gold),var(--orange));box-shadow:0 0 0 4px #fff,0 8px 18px rgba(255,184,0,.6)}
  .t3 .m::after{content:"";position:absolute;inset:0;border-radius:26px;pointer-events:none;
    background:linear-gradient(120deg,transparent 30%,rgba(255,255,255,.55) 48%,transparent 60%);
    background-size:200% 100%;animation:shine 3.5s linear infinite}

  /* ===== No.1 hero ===== */
  .t1{max-width:760px;text-align:center;padding:30px 16px 50px;position:relative}
  .crownwrap{position:relative;z-index:3}
  .crown{font-size:64px;animation:floaty 3s ease-in-out infinite;filter:drop-shadow(0 6px 10px rgba(255,184,0,.5))}
  .no1label{font-family:"Mochiy Pop One",sans-serif;font-size:clamp(22px,6vw,34px);margin-top:2px;
    background:linear-gradient(90deg,var(--gold),var(--orange),var(--pink),var(--gold));background-size:200% auto;
    -webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;animation:shine 4s linear infinite}
  .herocard{position:relative;margin:18px auto 0;max-width:430px;background:#fff;border-radius:30px;padding:18px;
    border:5px solid #fff;box-shadow:0 0 0 5px rgba(255,184,0,.4),0 26px 60px rgba(58,36,86,.4);
    animation:pop .7s backwards;overflow:hidden}
  .heroglow{position:absolute;inset:-40%;z-index:0;background:conic-gradient(from 0deg,var(--gold),var(--pink),var(--purple),var(--blue),var(--mint),var(--gold));
    opacity:.22;animation:spin 12s linear infinite}
  .herocard .cv{position:relative;z-index:1;display:block;border-radius:18px;overflow:hidden;aspect-ratio:3/4;
    background:linear-gradient(150deg,hsl(var(--h,40),85%,68%),hsl(calc(var(--h,40) + 48),88%,54%))}
  .herocard .cv .ph{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;padding:12px;text-align:center}
  .herocard .cv .ph .pe{font-size:90px;line-height:1;filter:drop-shadow(0 5px 8px rgba(0,0,0,.3))}
  .herocard .cv .ph .pt{font-weight:800;font-size:22px;line-height:1.3;color:#fff;text-shadow:0 2px 8px rgba(0,0,0,.45)}
  .herocard .cv img{position:absolute;inset:0;z-index:1;width:100%;height:100%;object-fit:contain;display:block;padding:10px}
  .herocard.has-cover .cv img{object-fit:cover;padding:0}
  .herocard figcaption{position:relative;z-index:1}
  .no1tag{display:inline-block;margin-top:16px;font-weight:800;color:#fff;font-size:13px;letter-spacing:1px;
    background:linear-gradient(135deg,var(--pink),var(--purple));padding:6px 16px;border-radius:999px}
  .herotitle{font-family:"Mochiy Pop One",sans-serif;font-size:clamp(22px,6vw,32px);margin-top:12px;line-height:1.25;color:var(--ink)}
  .herosub{margin-top:10px;font-weight:800;color:#6a4d8a;font-size:14px}
  .spark{position:absolute;inset:0;pointer-events:none;z-index:1}
  .spark span{position:absolute;font-size:22px;animation:sparkle 2.2s ease-in-out infinite;
    left:calc((var(--n)*67%)%100%);top:calc((var(--n)*43%)%96%);animation-delay:calc(var(--n)*.16s)}

  footer{text-align:center;margin-top:30px;color:#6a4d8a;font-weight:700;font-size:13px;padding:0 16px;line-height:1.9}
  footer a{color:var(--purple);font-weight:800}

  /* ===== 詳細モーダル（画像タップで表示） ===== */
  .m .cv,.herocard .cv{cursor:pointer}
  .ov{position:fixed;inset:0;z-index:200;background:rgba(42,26,74,.72);display:none;align-items:center;justify-content:center;
    padding:18px;opacity:0;transition:opacity .25s}
  .ov.show{display:flex;opacity:1}
  .mod{position:relative;width:100%;max-width:720px;max-height:92vh;overflow:auto;border-radius:28px;border:4px solid #fff;
    background:linear-gradient(160deg,#ffffff,#fff5fb);box-shadow:0 30px 80px rgba(58,36,86,.55);padding:22px 18px 26px;
    animation:mpop .45s cubic-bezier(.2,1.25,.3,1)}
  @keyframes mpop{from{transform:scale(.82) translateY(18px);opacity:0}to{transform:none;opacity:1}}
  .mx{position:absolute;top:10px;right:12px;width:34px;height:34px;border:0;border-radius:50%;cursor:pointer;font-weight:800;
    font-size:16px;color:#fff;background:linear-gradient(135deg,var(--purple),var(--pink));box-shadow:0 4px 10px rgba(155,92,255,.5);z-index:3}
  .mhead{display:flex;gap:16px;align-items:flex-start;flex-wrap:wrap}
  .mcv{width:130px;flex:none;aspect-ratio:3/4;border-radius:14px;overflow:hidden;
    background:linear-gradient(150deg,#c9d6ff,#a18bbf);box-shadow:0 10px 24px rgba(58,36,86,.3)}
  .mcv img{width:100%;height:100%;object-fit:cover}
  .mhd{flex:1;min-width:190px}
  .mrk{display:inline-block;font-family:"Baloo 2","Mochiy Pop One";font-weight:800;color:#fff;font-size:13px;padding:3px 12px;
    border-radius:999px;background:linear-gradient(135deg,var(--blue),var(--purple))}
  .mti{font-family:"Mochiy Pop One";font-size:clamp(18px,4.6vw,24px);margin:8px 0;line-height:1.3;color:var(--ink)}
  .mmeta{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:9px}
  .mmeta b{font-weight:800;font-size:11px;padding:3px 10px;border-radius:999px;background:#f0e8ff;color:#6a4d8a}
  .mintro{font-weight:700;color:var(--ink);font-size:13.5px;line-height:1.75}
  .vrow{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:14px;margin-top:18px}
  .vbox{background:rgba(255,255,255,.78);border:2px solid #fff;border-radius:20px;padding:10px 8px 8px;text-align:center;
    box-shadow:0 8px 18px rgba(58,36,86,.12);overflow:hidden}
  .vbox h4{font-family:"Mochiy Pop One";font-size:12px;color:var(--purple);margin-bottom:6px}
  .leg2{margin-top:12px;font-weight:800;color:var(--ink);font-size:12.5px;text-align:center;
    background:rgba(255,255,255,.7);border-radius:14px;padding:8px}
  .nodata{margin-top:16px;text-align:center;font-weight:800;color:#a18bbf;background:rgba(255,255,255,.7);border-radius:16px;padding:16px}
  @keyframes draw{from{stroke-dashoffset:var(--len)}to{stroke-dashoffset:0}}
  @keyframes popin{from{transform:scale(0);opacity:0}to{transform:scale(1);opacity:1}}
  @keyframes trace{to{stroke-dashoffset:0}}
  @keyframes grow{from{transform:scale(0)}to{transform:scale(1)}}
  .sweep{transform-origin:0 0;animation:spin 3.2s linear infinite}
  .confetti{position:absolute;inset:0;overflow:hidden;pointer-events:none;z-index:6;border-radius:28px}
  .confetti span{position:absolute;top:-16px;width:8px;height:13px;border-radius:2px;animation:fall linear forwards}
  @keyframes fall{to{transform:translateY(560px) rotate(600deg);opacity:.15}}'''

JS = '''  // reveal stagger within each grid row
  document.querySelectorAll('.grid').forEach(g=>{
    [...g.children].forEach((c,i)=>{c.style.animationDelay=(i%12*30)+'ms';});
  });
  // カバー画像が読めたらプレースホルダーを隠し、ポスター風(cover)に切替
  document.querySelectorAll('.cv img').forEach(img=>{
    const card=img.closest('.m,.herocard');
    const reveal=()=>{const ph=img.parentElement.querySelector('.ph'); if(ph) ph.style.display='none';
      // 縦長〜正方形の画像はポスター風に全面表示
      if(card && img.naturalWidth && img.naturalHeight && img.naturalWidth/img.naturalHeight <= 1.1) card.classList.add('has-cover');};
    if(img.complete && img.naturalWidth>0) reveal();
    else img.addEventListener('load',reveal);
  });

  // ===== 詳細モーダル（画像タップ／クリックで表示） =====
  const ov=document.getElementById('ov'), mb=document.getElementById('mbody');
  const esc=s=>(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;');
  const AX=[{k:'m',a:-90,c:'#ff5ea8',l:'思い入れ'},{k:'i',a:-18,c:'#ff8a3d',l:'衝撃'},{k:'f',a:54,c:'#36c5ff',l:'面白さ'},{k:'r',a:126,c:'#1bbf9a',l:'物語'},{k:'mu',a:198,c:'#9b5cff',l:'音楽'}];
  function radar(d){
    const R=70, rad=a=>a*Math.PI/180, P=(v,a)=>[((v||0)/10*R*Math.cos(rad(a))).toFixed(1),((v||0)/10*R*Math.sin(rad(a))).toFixed(1)];
    const ringPts=s=>AX.map(x=>[(R*s*Math.cos(rad(x.a))).toFixed(1),(R*s*Math.sin(rad(x.a))).toFixed(1)].join(',')).join(' ');
    const grid=[1,.66,.33].map(s=>`<polygon points="${ringPts(s)}" fill="none" stroke="#e6dbf8" stroke-width="1"/>`).join('');
    const axes=AX.map(x=>`<line x1="0" y1="0" x2="${(R*Math.cos(rad(x.a))).toFixed(1)}" y2="${(R*Math.sin(rad(x.a))).toFixed(1)}" stroke="#ece3fb" stroke-width="1"/>`).join('');
    const V=AX.map(x=>P(d[x.k],x.a));
    const poly=V.map(p=>p.join(',')).join(' ');
    const dots=V.map((p,k)=>`<circle cx="${p[0]}" cy="${p[1]}" r="3.5" fill="${AX[k].c}"/>`).join('');
    const labels=AX.map(x=>{const lr=R+16,X=(lr*Math.cos(rad(x.a))).toFixed(1),Y=(lr*Math.sin(rad(x.a))+4).toFixed(1),val=(d[x.k]==null?'－':d[x.k]);
      return `<text x="${X}" y="${Y}" text-anchor="middle" font-size="13" font-weight="800" fill="${x.c}">${x.l[0]}${val}</text>`;}).join('');
    return `<svg viewBox="-108 -100 216 210" width="100%" style="max-width:212px"><defs><radialGradient id="sw"><stop offset="0" stop-color="#9b5cff" stop-opacity=".5"/><stop offset="1" stop-color="#9b5cff" stop-opacity="0"/></radialGradient></defs>
      ${grid}${axes}
      <g class="sweep"><path d="M0,0 L0,-${R} A${R},${R} 0 0 1 ${(R*Math.sin(rad(44))).toFixed(1)},-${(R*Math.cos(rad(44))).toFixed(1)} Z" fill="url(#sw)"/></g>
      <g style="transform-origin:0px 0px;animation:grow .9s cubic-bezier(.2,1,.3,1) backwards">
        <polygon points="${poly}" fill="rgba(155,92,255,.30)" stroke="#9b5cff" stroke-width="2.5" style="filter:drop-shadow(0 0 7px rgba(155,92,255,.8))"/>
        ${dots}</g>${labels}</svg>`;
  }
  function aura(m,i,f,rk){
    const ring=(rad,col,v,dir,dur)=>{const w=(3+v/10*8).toFixed(1);return `<div style="position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:${rad*2}px;height:${rad*2}px;border-radius:50%;border:${w}px solid ${col};box-shadow:0 0 ${(6+v).toFixed(0)}px ${col},inset 0 0 ${(4+v/2).toFixed(0)}px ${col};opacity:${(.5+v/24).toFixed(2)};animation:spin ${dur}s linear infinite ${dir}"></div>`;};
    return `<div style="position:relative;width:176px;height:176px;margin:0 auto">${ring(84,'#36c5ff',f,'',9)}${ring(64,'#ff8a3d',i,'reverse',7)}${ring(46,'#ff5ea8',m,'',5)}
      <div style="position:absolute;inset:0;display:grid;place-items:center;font-family:'Mochiy Pop One';font-size:30px;color:#9b5cff;animation:pulse 2.5s ease-in-out infinite">${rk}</div></div>`;
  }
  function donut(m,i,f){
    const C=465, seg=v=>(v/10*140), avg=((m+i+f)/3).toFixed(1);
    const arc=(v,col,rot)=>`<circle r="74" fill="none" stroke="${col}" stroke-width="15" stroke-linecap="round" stroke-dasharray="${seg(v).toFixed(1)} ${C}" transform="rotate(${rot})" style="--len:${seg(v).toFixed(1)};stroke-dashoffset:0;animation:draw 1.05s ease-out backwards;filter:drop-shadow(0 0 5px ${col})"/>`;
    return `<svg viewBox="0 0 200 200" width="100%" style="max-width:190px"><g transform="translate(100,100)">
      <circle r="74" fill="none" stroke="#eee5ff" stroke-width="15"/>${arc(m,'#ff5ea8',-90)}${arc(i,'#ff8a3d',30)}${arc(f,'#36c5ff',150)}
      <text x="0" y="-3" text-anchor="middle" font-size="12" font-weight="800" fill="#6a4d8a">総合</text>
      <text x="0" y="23" text-anchor="middle" font-family="'Mochiy Pop One'" font-size="24" fill="#9b5cff" class="cnt" data-to="${avg}" data-dec="1">0.0</text></g></svg>`;
  }
  function countUp(el,to,dur,dec){let st=null;function f(t){if(st==null)st=t;let p=Math.min(1,(t-st)/dur);p=1-Math.pow(1-p,3);el.textContent=(to*p).toFixed(dec);if(p<1)requestAnimationFrame(f);}requestAnimationFrame(f);}
  function confetti(){const cols=['#ff5ea8','#9b5cff','#36c5ff','#ffd23f','#3ff2c2','#ff8a3d'];const w=document.createElement('div');w.className='confetti';
    for(let i=0;i<42;i++){const s=document.createElement('span');s.style.left=(Math.random()*100).toFixed(1)+'%';s.style.background=cols[i%cols.length];
      s.style.animationDelay=(Math.random()*.4).toFixed(2)+'s';s.style.animationDuration=(1.8+Math.random()*1.3).toFixed(2)+'s';w.appendChild(s);}
    mb.appendChild(w);setTimeout(()=>{if(w.parentNode)w.remove();},3400);}
  function openModal(fig){
    const cid=fig.dataset.cid, d=GD[cid]; if(!d) return;
    const rk=(fig.querySelector('.rk')?.textContent)||'1';
    const cover='game_covers/c'+cid+'.jpg';
    const meta=[['🎮',d.genre,'#7b53d6'],['🕹',d.plat,'#0f8f6e'],['📅',(d.year?d.year+'年':''),'#1f86c8'],['⏱',(d.played?'主に'+d.played:''),'#c25a16']]
      .filter(p=>p[1]).map(p=>'<b style="color:'+p[2]+'">'+p[0]+' '+esc(p[1])+'</b>').join('');
    const rated = d.m!=null&&d.i!=null&&d.f!=null;
    let viz;
    if(rated){
      const leg=[['💖',d.m,'#ff5ea8'],['⚡',d.i,'#ff8a3d'],['🎉',d.f,'#36c5ff'],['📖',d.r,'#1bbf9a'],['🎵',d.mu,'#9b5cff']]
        .map(p=>p[0]+' '+(p[1]==null?'<b style="color:#c3b8dc">－</b>':'<b class="cnt" data-to="'+p[1]+'" data-dec="0" style="color:'+p[2]+'">0</b>')).join('　');
      viz='<div class="vrow"><div class="vbox"><h4>5軸レーダー</h4>'+radar(d)+'</div>'
        +'<div class="vbox"><h4>オーラリング</h4>'+aura(d.m,d.i,d.f,rk)+'</div>'
        +'<div class="vbox"><h4>三つ巴スコア</h4>'+donut(d.m,d.i,d.f)+'</div></div>'
        +'<div class="leg2">'+leg+'</div>';
    } else {
      viz='<div class="nodata">評価データは準備中（思い入れ度・衝撃度・面白さ 未入力）</div>';
    }
    mb.innerHTML='<div class="mhead"><div class="mcv"><img src="'+cover+'" alt="" onerror="this.style.opacity=0"></div>'
      +'<div class="mhd"><span class="mrk">第 '+rk+' 位</span><div class="mti">'+esc(d.t)+'</div>'
      +'<div class="mmeta">'+meta+'</div><div class="mintro">'+esc(d.intro)+'</div></div></div>'+viz;
    ov.classList.add('show');
    if(rated){mb.querySelectorAll('.cnt').forEach(el=>countUp(el,+el.dataset.to,950,+el.dataset.dec||0)); confetti();}
  }
  function closeModal(){ov.classList.remove('show');}
  document.querySelectorAll('figure[data-cid] .cv').forEach(cv=>{
    cv.addEventListener('click',e=>{e.preventDefault();openModal(cv.closest('figure'));});
  });
  document.getElementById('mx').onclick=closeModal;
  ov.addEventListener('click',e=>{if(e.target===ov)closeModal();});
  document.addEventListener('keydown',e=>{if(e.key==='Escape')closeModal();});'''

doc = f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>思い入れのあるゲーム ランキング100 ✦ バトラ</title>
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@600;800&family=Mochiy+Pop+One&family=M+PLUS+Rounded+1c:wght@500;700;800&display=swap" rel="stylesheet" />
<style>
{CSS}
</style>
</head>
<body>
  <header>
    <h1 class="title"><span class="em">🎮</span> 思い入れのあるゲーム ランキング 100 <span class="em">🏆</span></h1>
    <p class="sub">バトラのオールタイム・ベスト100 ✦ 100位からカウントダウン！</p>
    <p class="hint">単なる「好きなゲーム」ではなく、<b>思い出補正</b>だったり、<b>娘の影響</b>だったり、<b>歳をとってから感動した</b>もの、<b>当時衝撃を受けた</b>もの…そんな“心に残った度”が評価軸の中心になっているよ。</p>
    <p class="hint">下にスクロールするほど上位＝<b>1位に近づくほどレイアウトが豪華に</b>なっていくよ。最後の <b>👑 第1位</b> まで一気にどうぞ！</p>
    <p class="scroll">▼ スクロールしてカウントダウン開始 ▼</p>
  </header>

{chr(10).join(sections)}

{hero}

  <footer>
    全100タイトル ✦ レトロ〜現行・PC洋ゲーまで全部入り ✦ <a href="manga.html">マンガ100</a>／<a href="command.htm">コマンドずかん</a>／<a href="voicevox.html">声の図鑑</a> もどうぞ 💖<br>
    <a href="index.html">← トップへ戻る</a><br>
    <a href="rank_edit.html">✏️ 順位を編集（ドラッグ&ドロップ）</a>
  </footer>

  <div class="ov" id="ov"><div class="mod" id="mod"><button class="mx" id="mx" aria-label="閉じる">✕</button><div id="mbody"></div></div></div>

<script>const GD = {GD_JSON};</script>
<script>
{JS}
</script>
</body>
</html>'''

open("game.html", "w", encoding="utf-8").write(doc)
print("game.html written:", len(doc), "bytes /", doc.count('<figure'), "figures")
