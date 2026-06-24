#!/usr/bin/env python3
"""game_ranking_draft.md の順位たたき台から game.html を生成する。
- 順位(1-100) / ジャンル絵文字 / tier を自動マッピング
- カバー画像は game_covers/<順位>.jpg を参照。無ければジャンル別カラータイルにフォールバック
- 画像はカラータイル上に contain 表示（横長ロゴでも綺麗）。読み込めたらプレースホルダーを隠す
使い方: python3 build_game_html.py
"""
import re, html

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

def hue(r):
    return (r * 37) % 360

def fig(r, tier):
    t = rank[r]; e = genre.get(t, "🎮"); th = html.escape(t); c = title2cid[t]
    return (f'<figure class="m {tier}" style="--i:{r};--h:{hue(r)}">'
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
  <figure class="herocard">
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
  footer a{color:var(--purple);font-weight:800}'''

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
  });'''

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

<script>
{JS}
</script>
</body>
</html>'''

open("game.html", "w", encoding="utf-8").write(doc)
print("game.html written:", len(doc), "bytes /", doc.count('<figure'), "figures")
