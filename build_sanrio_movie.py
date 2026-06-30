#!/usr/bin/env python3
"""2026年 サンリオキャラクター大賞 TOP20 カウントダウン発表ムービー sanrio_movie.html を生成。

構成「THE VOTE COUNTDOWN」:
- 投票数の0→実数ローリング・カウントアップを「タメ＝爆発」の主装置に。
- 画面左の常設「順位レーン」で昨年→今年の順位変動(下剋上)を毎回視覚化。
- 10位以下(10〜20位)は「誕生日/デビュー年/趣味/好きなもの」をヒントに出す“プロフィールクイズ”でタメてから公開。
- 9位以上はタメ・派手さを段階解禁。No.1は「二段階確定ニアミス」で頂点を爆破。
- 大きめのキャラ画像カード＋順位/称号をステッカー化。
- 可愛いポップ配色3テーマ(①ゆめかわ ②キャンディ ③リボン)を「テーマ」で切替。
- 縦9:16(ショート既定)／横16:9、再生/一時停止/前後/速度/全画面/BGM(movie_bgm.mp3)。

データ元: sanrio_data.csv (順位,キャラクター名,投票数,紹介,昨年順位,好きなもの,デビュー年,趣味,誕生日,画像)
画像は sanrio_covers/cN.png を置くと使用。無ければ色付きプレースホルダー(キャラ名)に自動フォールバック。
クイズ対象の境界は JS の QUIZ_FROM(既定10=「10位以下」)。11に変えるとTOP10圏外のみクイズ。
使い方: python3 build_sanrio_movie.py
"""
import csv, json, os, glob

rows = []
with open("sanrio_data.csv", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        def n(x):
            x = (x or "").strip()
            return int(x.replace(",", "")) if x.replace(",", "").isdigit() else None
        g = lambda k: (row.get(k) or "").strip()
        rows.append({
            "rank": n(row.get("順位")),
            "name": g("キャラクター名"),
            "votes": n(row.get("投票数")) or 0,
            "intro": g("紹介"),
            "lastRank": n(g("昨年順位")),
            "likes": g("好きなもの") or "ひみつ♡",
            "debut": g("デビュー年") or "ひみつ♡",
            "hobby": g("趣味") or "ひみつ♡",
            "birthday": g("誕生日") or "ひみつ♡",
            "img": g("画像"),
        })
rows.sort(key=lambda c: c["rank"])
CHARS_JSON = json.dumps(rows, ensure_ascii=False)

# バナー背景モザイク用：TOP20圏外（ランク外）キャラの立ち絵を sanrio_covers/out/ から採用
OUT_IMGS = sorted(glob.glob("sanrio_covers/out/*.png"))
OUTIMGS_JSON = json.dumps(OUT_IMGS, ensure_ascii=False)

CSS = r"""
:root{--pink:#ff7ec1;--pink2:#ff5ea8;--purple:#9b5cff;--blue:#36c5ff;--gold:#ffb800;--mint:#3ff2c2;--accent:#ff4fa3;--accent2:#9b5cff}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:"M PLUS Rounded 1c",sans-serif;background:#1a1030;min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px;padding:12px;color:#fff;overflow:hidden}
#frame{position:relative;width:min(98vw,calc(92vh*9/16));aspect-ratio:9/16;border-radius:22px;overflow:hidden;box-shadow:0 24px 70px rgba(0,0,0,.6);border:3px solid rgba(255,255,255,.18);container-type:size}
#frame.horiz{width:min(98vw,calc(86vh*16/9));aspect-ratio:16/9}
#stage{position:absolute;inset:0;overflow:hidden;background:linear-gradient(135deg,#ffe3f3,#efe2ff,#dff4ff,#e6fff4);background-size:400% 400%;animation:bg 18s ease infinite}
@keyframes bg{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes fadeup{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}
#pbar{position:absolute;left:0;right:0;bottom:0;height:6px;background:rgba(255,255,255,.3);z-index:9;pointer-events:none}
#pfill{height:100%;width:0;background:hsl(330,92%,62%);box-shadow:0 0 12px rgba(255,255,255,.6);transition:width .4s linear,background .4s linear}
/* バナー */
.banner{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:0 6%;animation:shake .5s .15s both}
@keyframes shake{0%,100%{transform:translate(0,0)}12%{transform:translate(-8px,5px)}26%{transform:translate(7px,-5px)}40%{transform:translate(-6px,4px)}55%{transform:translate(5px,-3px)}72%{transform:translate(-3px,2px)}88%{transform:translate(2px,-1px)}}
.btxt{position:relative;z-index:3;font-family:"Mochiy Pop One";font-size:clamp(40px,13cqw,120px);line-height:1.05;color:#fff;text-shadow:0 5px 0 rgba(255,94,168,.5),0 0 34px rgba(255,255,255,.8);animation:impact .55s cubic-bezier(.16,.9,.3,1.05) backwards}
@keyframes impact{0%{transform:scale(3.1);opacity:0;filter:blur(14px)}55%{opacity:1}80%{transform:scale(.92)}100%{transform:scale(1);filter:none}}
.bsub{position:relative;z-index:3;font-weight:800;font-size:clamp(16px,4.4cqw,32px);margin-top:12px;letter-spacing:2px;color:#fff;text-shadow:0 2px 10px rgba(255,94,168,.6);animation:fadeup .5s .4s backwards}
.bflash{position:absolute;inset:0;background:#fff;opacity:0;pointer-events:none;animation:bflash .5s .12s backwards;z-index:5}
@keyframes bflash{0%{opacity:0}12%{opacity:.9}100%{opacity:0}}
.bshock{position:absolute;left:50%;top:50%;width:10px;height:10px;border-radius:50%;border:14px solid rgba(255,255,255,.85);transform:translate(-50%,-50%);opacity:0;animation:shock .8s ease-out .2s backwards;z-index:3}
@keyframes shock{0%{width:10px;height:10px;opacity:.85;border-width:16px}100%{width:175%;height:175%;opacity:0;border-width:1px}}
.bgrid{position:absolute;inset:0;z-index:0;display:grid;grid-template-columns:repeat(4,1fr);gap:6px;overflow:hidden;opacity:.55}
.bcol{display:flex;flex-direction:column;gap:6px}
.bcol.up{animation:mUp 40s linear infinite}.bcol.down{animation:mDown 46s linear infinite}
.bcol:nth-child(2){animation-duration:52s}.bcol:nth-child(3){animation-duration:44s}.bcol:nth-child(4){animation-duration:58s}
@keyframes mUp{from{transform:translateY(0)}to{transform:translateY(-50%)}}
@keyframes mDown{from{transform:translateY(-50%)}to{transform:translateY(0)}}
.mtile{position:relative;aspect-ratio:3/4;border-radius:12px;overflow:hidden}
.mtile img{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;padding:7%}
.bscrim{position:absolute;inset:0;z-index:1;background:radial-gradient(120% 90% at 50% 50%,rgba(70,30,90,.28),rgba(60,20,80,.66))}
/* キャラスライド */
.cardslide{position:absolute;inset:0;overflow:hidden}
.lane{position:absolute;left:2.6%;top:9%;bottom:9%;width:30px;z-index:4}
.lane::before{content:"";position:absolute;left:50%;top:0;bottom:0;width:4px;transform:translateX(-50%);background:rgba(130,90,160,.3);border-radius:2px}
.ltick{position:absolute;left:50%;width:9px;height:2px;background:rgba(130,90,160,.45);transform:translate(-50%,-50%)}
.ltick.on{width:18px;height:4px;background:var(--accent);box-shadow:0 0 8px var(--accent)}
.lghost{position:absolute;left:50%;width:14px;height:14px;border-radius:50%;border:2px solid rgba(130,90,160,.7);background:rgba(255,255,255,.7);transform:translate(-50%,-50%);z-index:2}
.llive{position:absolute;left:50%;width:18px;height:18px;border-radius:50%;background:#caa0e6;border:2px solid #fff;transform:translate(-50%,-50%);box-shadow:0 0 10px rgba(170,120,210,.8);transition:top .9s cubic-bezier(.5,1.6,.4,1);z-index:3}
.llive.up{background:#1ec79a;box-shadow:0 0 16px #3ff2c2}
.llive.down{background:#2aa3e6;box-shadow:0 0 16px #8fd3ff}
.llive.unknown{background:#9b6cff}
.cmain{position:absolute;inset:0;padding:3.5% 5% 7% 10%;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:1cqh;text-align:center}
.cardfx{position:absolute;left:50%;top:34%;transform:translate(-50%,-50%);width:min(130cqw,620px);aspect-ratio:1;z-index:0;pointer-events:none}
.cardwrap{position:relative;z-index:1;width:min(60cqw,300px);aspect-ratio:3/4;margin-bottom:.3cqh;animation:cvin .6s cubic-bezier(.2,1.2,.3,1) backwards}
@keyframes cvin{from{transform:scale(.72) rotate(-3deg);opacity:0}to{transform:none;opacity:1}}
.ccard{position:absolute;inset:0;border-radius:26px;overflow:hidden;border:6px solid #fff;box-shadow:0 18px 46px rgba(0,0,0,.32);transition:filter .55s ease}
.cardslide.revealed .ccard{animation:pop .5s cubic-bezier(.2,1.3,.3,1)}
@keyframes pop{from{transform:scale(.86)}to{transform:scale(1)}}
.cglow{position:absolute;inset:-30%;background:conic-gradient(from 0deg,var(--gold),var(--pink),var(--purple),var(--blue),var(--mint),var(--gold));animation:spin 8s linear infinite;opacity:.5;z-index:0}
.ph{position:absolute;inset:0;z-index:0}
.sil{position:absolute;inset:0;z-index:1;background:linear-gradient(135deg,#d8c6e8,#c4b2db);opacity:0;transition:opacity .55s ease}
.cardslide:not(.revealed) .sil{opacity:1}
.phname{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;text-align:center;padding:10px;font-family:"Mochiy Pop One";font-size:clamp(15px,5cqw,28px);color:rgba(90,40,90,.92);z-index:2;line-height:1.3}
.ccard.hasimg .phname{display:none}
.cardslide:not(.revealed) .phname{visibility:hidden}
.ccard img{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;padding:6%;z-index:3;transition:filter .55s ease}
.cardslide:not(.revealed) .ccard img{filter:brightness(0)}
.crank{position:absolute;left:-10px;top:-16px;z-index:4;font-family:"Baloo 2";font-weight:800;font-size:clamp(24px,8.4cqw,50px);line-height:1;color:#fff;background:var(--accent);border:3px solid #fff;border-radius:16px;padding:3px 12px;box-shadow:0 6px 16px rgba(0,0,0,.22);transform:rotate(-7deg);animation:rkin .55s cubic-bezier(.2,1.5,.3,1) backwards}
.crank span{font-size:.46em;margin-left:1px}
@keyframes rkin{from{transform:rotate(-7deg) scale(2.1);opacity:0;filter:blur(6px)}to{transform:rotate(-7deg) scale(1);opacity:1}}
.ctier{position:absolute;right:-8px;top:14px;z-index:4;font-weight:800;font-size:clamp(11px,3cqw,18px);background:#fff;color:var(--accent2);padding:5px 13px;border-radius:999px;box-shadow:0 4px 12px rgba(0,0,0,.18);transform:rotate(5deg)}
.cinfo{display:flex;flex-direction:column;align-items:center;gap:.55cqh;position:relative;z-index:1;width:100%}
.qhead{font-family:"Mochiy Pop One";font-size:clamp(14px,4.2cqw,24px);color:#ff3f95;text-shadow:0 2px 0 #fff,0 0 14px rgba(255,255,255,.6);animation:fadeup .5s ease backwards}
.cardslide:not(.quiz) .qhead{display:none}
.cardslide.quiz.revealed .qhead{display:none}
.cname{font-family:"Mochiy Pop One";font-size:clamp(20px,6.6cqw,40px);line-height:1.15;color:#ff3f95;text-shadow:0 2px 0 #fff,0 3px 12px rgba(255,138,209,.5)}
.cardslide.revealed .cname{animation:pop2 .5s cubic-bezier(.2,1.5,.3,1)}
@keyframes pop2{from{transform:scale(1.8);opacity:0;filter:blur(6px)}to{transform:scale(1);opacity:1}}
.cprofile{display:flex;flex-wrap:wrap;justify-content:center;gap:5px;max-width:96%}
.pitem{display:flex;align-items:center;gap:6px;background:rgba(255,255,255,.74);border-radius:999px;padding:3px 11px;font-weight:800;font-size:clamp(10px,2.8cqw,15px);color:#6b2f57;box-shadow:0 2px 8px rgba(0,0,0,.08)}
.pitem .pk{color:#ff5fa6;white-space:nowrap}
.pitem .pv{max-width:46cqw;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.cardslide:not(.quiz):not(.revealed) .cprofile{display:none}
.cardslide.quiz:not(.revealed) .cprofile{flex-direction:column;gap:1cqh;max-width:90%}
.cardslide.quiz:not(.revealed) .pitem{width:100%;justify-content:flex-start;font-size:clamp(13px,3.7cqw,22px);padding:7px 16px;opacity:0;animation:qin .5s ease forwards}
.cardslide.quiz:not(.revealed) .pitem .pv{white-space:normal;max-width:none}
.cardslide.quiz:not(.revealed) .pitem:nth-child(1){animation-delay:.2s}
.cardslide.quiz:not(.revealed) .pitem:nth-child(2){animation-delay:1.0s}
.cardslide.quiz:not(.revealed) .pitem:nth-child(3){animation-delay:1.8s}
.cardslide.quiz:not(.revealed) .pitem:nth-child(4){animation-delay:2.6s}
@keyframes qin{from{opacity:0;transform:translateX(-14px)}to{opacity:1;transform:none}}
.cardslide.quiz:not(.revealed) .cbadge,.cardslide.quiz:not(.revealed) .cvote,.cardslide.quiz:not(.revealed) .clead,.cardslide.quiz:not(.revealed) .cintro{display:none}
.cbadge{display:inline-flex;flex-direction:column;align-items:center;font-weight:800;font-size:clamp(13px,3.8cqw,22px);padding:5px 18px;border-radius:14px;opacity:0;transform:scale(.5);color:#3a1840;box-shadow:0 4px 12px rgba(0,0,0,.14)}
.cbadge.show{animation:badge .5s cubic-bezier(.2,1.7,.3,1) forwards}
@keyframes badge{to{opacity:1;transform:scale(1)}}
.cbadge small{font-weight:700;font-size:.6em;opacity:.9;color:#5a3a60;margin-top:1px}
.cbadge.up{background:linear-gradient(135deg,#7df0c8,#3ff2c2)}
.cbadge.down{background:linear-gradient(135deg,#cfe6ff,#8fd3ff)}
.cbadge.stay{background:rgba(255,255,255,.92)}
.cbadge.unk{background:rgba(155,120,210,.6);color:#fff}
.cbadge.unk small{color:#fff}
.cvote{display:flex;align-items:baseline;gap:6px;font-family:"Baloo 2";transition:opacity .3s}
.cardslide:not(.revealed) .cvote{opacity:.3}
.cnum{font-size:clamp(34px,12cqw,76px);font-weight:800;line-height:1;color:#ff3f95;text-shadow:0 2px 0 #fff,0 0 22px rgba(255,255,255,.55)}
.cnum.rolling{animation:numpulse .12s linear infinite}
@keyframes numpulse{0%,100%{transform:scale(1)}50%{transform:scale(1.04)}}
.cunit{font-size:clamp(16px,4cqw,26px);font-weight:800;color:#ff7ab0}
.clead{font-weight:800;font-size:clamp(12px,3.2cqw,20px);color:#6b2f57;min-height:1.1em;transition:opacity .3s}
.cardslide:not(.revealed) .clead{opacity:0}
.clead b{color:#ff3f95}
.cintro{font-weight:700;font-size:clamp(11px,3.2cqw,19px);line-height:1.45;max-width:92%;color:#6b2f57;text-shadow:0 1px 0 rgba(255,255,255,.5);transition:opacity .3s}
.cardslide:not(.revealed) .cintro{opacity:0}
.flash{position:absolute;inset:0;background:#fff;opacity:0;z-index:6;pointer-events:none}
.flash.go{animation:fl .55s ease forwards}
@keyframes fl{0%{opacity:0}18%{opacity:.85}100%{opacity:0}}
.cardslide.champ .crank{background:var(--gold);color:#7a4a00}
.cardslide.champ .ccard{border-color:var(--gold);box-shadow:0 0 0 6px rgba(255,184,0,.55),0 20px 60px rgba(0,0,0,.4)}
.cardslide.champ .cnum{color:#ff9d00;font-size:clamp(38px,13cqw,86px)}
.cardslide.champ .cmain{background:radial-gradient(60% 50% at 50% 38%,rgba(255,200,80,.22),transparent 70%)}
/* OP */
.op{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;text-align:center}
.opscrim{position:absolute;inset:0;background:radial-gradient(120% 90% at 50% 45%,rgba(70,30,90,.42),rgba(50,16,70,.8));z-index:1}
.opinner{position:relative;z-index:2;padding:0 8%;display:flex;flex-direction:column;gap:3cqh;align-items:center}
.optitle{font-weight:800;font-size:clamp(15px,4.2cqw,26px);color:#fff;line-height:1.5}
.optitle b{font-family:"Mochiy Pop One";font-size:clamp(22px,7.2cqw,50px);color:#fff;text-shadow:0 0 30px rgba(255,255,255,.7);display:block;margin-top:6px;animation:impact .6s cubic-bezier(.16,.9,.3,1.05) backwards;text-align:center;line-height:1.2}
.opsub{font-weight:800;font-size:clamp(15px,4.4cqw,26px);color:#fff;background:var(--accent);padding:6px 22px;border-radius:999px}
.opvote{display:flex;flex-direction:column;align-items:center;gap:4px;font-family:"Baloo 2";color:#fff;margin-top:1.5cqh}
.opvote span{font-weight:800;font-family:"M PLUS Rounded 1c";font-size:clamp(13px,3.6cqw,20px)}
.opvote .cnum{color:#fff;font-size:clamp(38px,14cqw,88px);font-weight:800;text-shadow:0 0 30px rgba(255,255,255,.7)}
/* ED */
.ed{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:6%;gap:2cqh}
.edttl{font-family:"Mochiy Pop One";font-size:clamp(19px,5.8cqw,40px);color:#fff;line-height:1.3;text-shadow:0 3px 14px rgba(255,94,168,.5);animation:impact .6s cubic-bezier(.16,.9,.3,1.05) backwards}
.edgrid{display:grid;grid-template-columns:repeat(2,1fr);gap:5px 14px;width:100%;max-width:94%}
.ecell{display:flex;gap:8px;align-items:center;background:rgba(255,255,255,.2);border-radius:10px;padding:4px 9px;font-size:clamp(10px,2.8cqw,15px)}
.ecell b{font-family:"Baloo 2";color:#ffe08a;min-width:1.6em;text-align:right}
.ecell span{font-weight:700;color:#fff;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.edthx{font-family:"Mochiy Pop One";font-size:clamp(16px,5cqw,30px);color:#fff;text-shadow:0 0 20px rgba(255,255,255,.6)}
.cf{position:absolute;inset:0;overflow:hidden;pointer-events:none;z-index:7}
.cf span{position:absolute;top:-24px;animation:fall linear forwards;text-shadow:0 1px 2px rgba(0,0,0,.2)}
@keyframes fall{to{transform:translateY(122cqh) rotate(680deg);opacity:.1}}
/* 横向き微調整 */
#frame.horiz .cmain{padding:3% 5% 6% 8%}
#frame.horiz .lane{width:26px;left:1.8%}
#frame.horiz .cardwrap{width:min(30cqw,260px)}
/* ===== 可愛いポップ 3テーマ ===== */
#frame.theme-a{--accent:#ff7ac1;--accent2:#9b7bff}
#frame.theme-a #stage{background:linear-gradient(135deg,#ffe3f3,#efe2ff,#dff4ff,#e6fff4);background-size:400% 400%;animation:bg 18s ease infinite}
#frame.theme-a #stage::before{content:"";position:absolute;inset:0;background:radial-gradient(rgba(255,255,255,.55) 2.5px,transparent 3.5px) 0 0/28px 28px;opacity:.55;pointer-events:none}
#frame.theme-a .cardfx{background:radial-gradient(circle,rgba(255,255,255,.55),transparent 60%)}
#frame.theme-a .ccard{box-shadow:0 16px 44px rgba(255,138,209,.42),0 0 0 5px rgba(255,255,255,.55)}
#frame.theme-b{--accent:#ff2e90;--accent2:#1aa6ff}
#frame.theme-b #stage{background:linear-gradient(135deg,#ff9ed4,#8ad6ff,#fff07a,#ffa3d1);background-size:420% 420%;animation:bg 14s ease infinite}
#frame.theme-b #stage::before{content:"";position:absolute;inset:0;background:radial-gradient(rgba(255,255,255,.75) 6px,transparent 7px) 0 0/46px 46px;opacity:.4;pointer-events:none}
#frame.theme-b .cardfx{background:repeating-conic-gradient(from 0deg,rgba(255,255,255,.6) 0deg 8deg,transparent 8deg 16deg);border-radius:50%;-webkit-mask:radial-gradient(circle,#000 26%,transparent 70%);mask:radial-gradient(circle,#000 26%,transparent 70%);animation:spin 26s linear infinite;opacity:.55}
#frame.theme-b .ccard{border-width:8px;border-radius:24px;box-shadow:0 12px 0 rgba(0,0,0,.12),0 18px 38px rgba(0,0,0,.22)}
#frame.theme-b .cname,#frame.theme-b .cnum{color:#ff2e90;text-shadow:-2px -2px 0 #fff,2px -2px 0 #fff,-2px 2px 0 #fff,2px 2px 0 #fff,0 6px 0 rgba(0,0,0,.12)}
#frame.theme-b .cunit{color:#1aa6ff}
#frame.theme-b .cintro,#frame.theme-b .clead,#frame.theme-b .pitem{color:#4a1f3e}
#frame.theme-b .clead b{color:#ff2e90}
#frame.theme-c{--accent:#ff6aa6;--accent2:#cf9430}
#frame.theme-c #stage{background:linear-gradient(135deg,#fff2f8,#ffdcec,#fff6e2,#ffe7f1);background-size:400% 400%;animation:bg 20s ease infinite}
#frame.theme-c #stage::before{content:"";position:absolute;inset:0;background:radial-gradient(circle at 18% 26%,rgba(255,213,120,.65) 0 2px,transparent 3px),radial-gradient(circle at 72% 58%,rgba(255,213,120,.5) 0 2px,transparent 3px),radial-gradient(circle at 46% 82%,rgba(255,255,255,.75) 0 2px,transparent 3px);background-size:190px 190px;opacity:.8;pointer-events:none}
#frame.theme-c .cardfx{background:radial-gradient(circle,rgba(255,221,150,.5),transparent 60%)}
#frame.theme-c .ccard{box-shadow:0 0 0 5px #ffd98a,0 16px 44px rgba(217,162,58,.35)}
#frame.theme-c .cardwrap::after{content:"🎀";position:absolute;left:50%;top:-22px;transform:translateX(-50%);font-size:clamp(26px,9cqw,46px);z-index:6;filter:drop-shadow(0 3px 4px rgba(0,0,0,.2))}
#frame.theme-c .cname{color:#e84f93}
/* コントロール */
.ctl{display:flex;gap:7px;align-items:center;flex-wrap:wrap;justify-content:center;background:rgba(255,255,255,.08);padding:8px 14px;border-radius:999px;max-width:98vw}
.ctl button{font:inherit;font-weight:800;border:0;border-radius:999px;padding:8px 13px;cursor:pointer;background:rgba(255,255,255,.92);color:#3a1840}
.ctl button#th{background:linear-gradient(135deg,#ff8ad1,#9b7bff);color:#fff}
.ctl .prog{color:#fff;font-weight:800;font-size:13px;min-width:128px;text-align:center}
.ctl select{font:inherit;border-radius:999px;border:0;padding:7px 10px;font-weight:800}
.hint{color:rgba(255,255,255,.6);font-size:12px;font-weight:700;text-align:center;max-width:780px}
/* ============ kawaii強化レイヤー ============ */
/* 案5: 環境エフェクト（玉ボケ／流れ星／常駐マスコット／ドキドキ） */
#envfx{position:absolute;inset:0;z-index:2;pointer-events:none;overflow:hidden;mix-blend-mode:screen}
.bokeh{position:absolute;bottom:-12%;border-radius:50%;background:radial-gradient(circle at 35% 35%,rgba(255,255,255,.95),rgba(255,255,255,0) 70%);animation-name:bokehFloat;animation-timing-function:linear;animation-iteration-count:infinite}
@keyframes bokehFloat{0%{transform:translateY(0) scale(.5);opacity:0}15%{opacity:.85}85%{opacity:.5}100%{transform:translateY(-130cqh) scale(1.15);opacity:0}}
.shoot{position:absolute;width:3px;height:3px;background:#fff;border-radius:50%;box-shadow:0 0 8px 3px rgba(255,255,255,.95);animation-name:shoot;animation-timing-function:ease-in;animation-iteration-count:infinite}
.shoot::after{content:"";position:absolute;right:1px;top:50%;width:64px;height:2px;background:linear-gradient(90deg,rgba(255,255,255,.95),transparent);transform:translateY(-50%);border-radius:2px}
@keyframes shoot{0%{transform:translate(0,0) rotate(18deg);opacity:0}8%{opacity:1}55%{opacity:1}100%{transform:translate(-150cqw,75cqh) rotate(18deg);opacity:0}}
#halftone{position:absolute;inset:0;z-index:3;pointer-events:none;background-image:radial-gradient(rgba(120,60,120,.4) 1.3px,transparent 1.6px);background-size:13px 13px;opacity:.1;mix-blend-mode:multiply}
#deco{position:absolute;inset:0;z-index:5;pointer-events:none;overflow:hidden}
.mascot{position:absolute;font-size:clamp(20px,6.5cqw,38px);animation-name:mascotFloat;animation-timing-function:ease-in-out;animation-iteration-count:infinite;filter:drop-shadow(0 3px 4px rgba(0,0,0,.18))}
@keyframes mascotFloat{0%,100%{transform:translateY(0) rotate(-5deg)}50%{transform:translateY(-9px) rotate(5deg)}}
.dokidoki{position:absolute;inset:0;opacity:0;transition:opacity .25s}
.dokidoki.on{opacity:1}
.dokidoki span{position:absolute;font-size:clamp(18px,5.5cqw,30px);animation:doki .52s ease-in-out infinite;filter:drop-shadow(0 2px 3px rgba(0,0,0,.15))}
@keyframes doki{0%,100%{transform:scale(1)}50%{transform:scale(1.45)}}
/* 案1: リビールバースト＆もちもちフロート */
.burst{position:absolute;left:50%;top:46%;z-index:5;pointer-events:none}
.burst span{position:absolute;left:0;top:0;font-size:clamp(15px,4.6cqw,28px);will-change:transform,opacity;animation:burstgo .95s cubic-bezier(.15,.7,.3,1) forwards}
@keyframes burstgo{0%{transform:translate(0,0) scale(.2) rotate(0);opacity:0}12%{opacity:1}100%{transform:translate(var(--bx),var(--by)) scale(1.05) rotate(var(--br));opacity:0}}
.cardslide.revealed .cardwrap{animation:cvin .6s cubic-bezier(.2,1.2,.3,1) backwards,mochi 3.4s ease-in-out .7s infinite}
@keyframes mochi{0%,100%{transform:translateY(0) scale(1,1)}50%{transform:translateY(-2.4%) scale(1.018,.982)}}
/* 案2: オノマトペ＆吹き出し尻尾＆手書きフォント */
.onoma{position:absolute;left:50%;top:6.5%;transform:translate(-50%,-50%);z-index:7;pointer-events:none;white-space:nowrap;font-family:"Mochiy Pop One";font-size:clamp(18px,5.6cqw,36px);color:#fff;text-shadow:0 3px 0 var(--accent),-2px -2px 0 var(--accent),2px 2px 0 var(--accent),0 0 18px rgba(255,255,255,.8);animation:onomago 1.3s cubic-bezier(.2,1.5,.3,1) forwards}
@keyframes onomago{0%{transform:translate(-50%,-30%) scale(.3) rotate(-10deg);opacity:0}20%{transform:translate(-50%,-50%) scale(1.12) rotate(-5deg);opacity:1}40%{transform:translate(-50%,-50%) scale(.96) rotate(-7deg)}75%{opacity:1}100%{transform:translate(-50%,-78%) scale(1) rotate(-6deg);opacity:0}}
.cardslide.quiz:not(.revealed) .qhead{background:#fff;color:#ff3f95;padding:6px 20px;border-radius:999px;box-shadow:0 5px 0 rgba(255,94,168,.35),0 8px 16px rgba(0,0,0,.12);position:relative}
.cardslide.quiz:not(.revealed) .qhead::after{content:"";position:absolute;left:50%;bottom:-9px;transform:translateX(-50%);border:8px solid transparent;border-top-color:#fff;border-bottom:0}
.cardslide.quiz:not(.revealed) .qhead{font-family:"Yomogi",cursive;font-weight:700}
.cardslide.quiz:not(.revealed) .pitem .pk{font-family:"Yomogi",cursive}
/* 案3: カーテン／リボン・スワイプ */
#wipe{position:absolute;inset:0;z-index:8;pointer-events:none;overflow:hidden;display:none}
#wipe.go{display:block}
#wipe .wipe-sweep{position:absolute;top:0;bottom:0;left:-60%;width:60%;background:linear-gradient(105deg,transparent,rgba(255,255,255,.92) 30%,#ffd9ee 50%,rgba(255,255,255,.92) 70%,transparent);box-shadow:0 0 60px 30px rgba(255,255,255,.5);animation:sweep .5s ease-in-out forwards}
#wipe .wipe-sweep::before,#wipe .wipe-sweep::after{content:"🎀";position:absolute;left:50%;transform:translateX(-50%);font-size:clamp(24px,8cqw,44px)}
#wipe .wipe-sweep::before{top:8%}
#wipe .wipe-sweep::after{bottom:8%}
@keyframes sweep{0%{left:-60%}100%{left:160%}}
/* 案4: ステッカー強化＆数字ポン */
.crank{background-image:repeating-linear-gradient(48deg,rgba(255,255,255,.22) 0 5px,rgba(255,255,255,0) 5px 11px)}
.ctier{background-image:linear-gradient(135deg,#fff,#ffe9f5)}
.cnum.ding{animation:ding .42s cubic-bezier(.2,1.6,.3,1)}
@keyframes ding{0%{transform:scale(1)}45%{transform:scale(1.14)}100%{transform:scale(1)}}
/* ベスト10: チャプターバナー強化＆スポットライト */
.banner.top10x .btxt{color:#fff8e1;text-shadow:0 4px 0 #d99b1c,0 0 30px rgba(255,210,120,.9)}
.banner.top10x .bscrim{background:radial-gradient(120% 90% at 50% 50%,rgba(120,70,20,.3),rgba(80,40,10,.72))}
.banner.champx .btxt{color:#fff;text-shadow:0 4px 0 #c98a00,0 0 40px rgba(255,200,80,1)}
.spot{position:absolute;inset:0;z-index:0;pointer-events:none;opacity:0;transition:opacity .6s;background:radial-gradient(58% 42% at 50% 33%,rgba(255,255,255,.5),rgba(255,255,255,0) 60%),radial-gradient(140% 100% at 50% 40%,transparent 40%,rgba(60,25,80,.26) 100%)}
.cardslide.spotlight.revealed .spot{opacity:1}
/* ②: フリー素材オーバーレイ動画（加算合成） */
#ov{position:absolute;inset:0;z-index:4;width:100%;height:100%;object-fit:cover;mix-blend-mode:screen;opacity:0;transition:opacity .45s;pointer-events:none}
#ov.on{opacity:.72}
.ctl button#ovb.active{background:linear-gradient(135deg,#9b7bff,#36c5ff);color:#fff}
"""

JS = r"""
const CHARS = __CHARS__;
const OUTIMGS = __OUTIMGS__;  // TOP20圏外キャラの立ち絵(バナー背景用)
const byRank={}; CHARS.forEach(c=>byRank[c.rank]=c);
const N=CHARS.length;
const TOTALVOTES=70647379; // 2026 第41回 総得票数(公式)
const QUIZ_FROM=1;         // 全ランク(1〜20位)プロフィールクイズ
const isQuiz=r=>r>=QUIZ_FROM;
const fmt=n=>n.toLocaleString('en-US');
const PAL=[['#ffe0a3','#ffc04d'],['#d9c2ff','#b794ff'],['#bfe9ff','#8fd3ff'],['#c6ffe9','#7df0c8'],['#ffd1e8','#ff9ec4'],['#ffd9c2','#ffb38f']];
const pal=r=>PAL[(r-1)%PAL.length];

const stage=document.getElementById('stage');
let si=0,playing=true,mult=1,gen=0,timer=null,pending=[];
let theme=1;const THN=['①ゆめかわ','②キャンディ','③リボン'],THC=['theme-a','theme-b','theme-c'];
function clearPending(){pending.forEach(clearTimeout);pending=[];if(timer){clearTimeout(timer);timer=null;}}
function later(fn,ms){const id=setTimeout(fn,ms);pending.push(id);return id;}

const BANNERS={20:['BEST 20','20位 ▶ 11位'],10:['TOP 10','10位 ▶ 6位'],5:['BEST 5','5位 ▶ 4位'],3:['BEST 3','✦ 表彰台 ✦'],1:['\u{1F451} No.1','　頂　点　']};
const tierOf=r=>r===1?'\u{1F451} 第 1 位':r<=3?'BEST 3':r<=5?'BEST 5':r<=10?'TOP 10':'BEST 20';
const dramaOf=r=>r===1?4:r<=3?3:r<=5?2:r<=10?1:0;

function mkMosaic(src){if(!src||!src.length)return'';const MIN=32;let imgs=[];while(imgs.length<MIN)imgs=imgs.concat(src);const cols=['','','',''];imgs.forEach((s,k)=>{const p=PAL[k%PAL.length];cols[k%4]+=`<div class="mtile" style="background:linear-gradient(135deg,${p[0]},${p[1]})"><img src="${s}" loading="lazy" onerror="this.remove()"></div>`;});return '<div class="bgrid">'+cols.map((c,k)=>`<div class="bcol ${k%2?'down':'up'}">${c}${c}</div>`).join('')+'</div>';}
const TOP20IMGS=CHARS.map(c=>c.img);
const MOSAIC=mkMosaic((OUTIMGS&&OUTIMGS.length)?OUTIMGS:TOP20IMGS);  // 章バナー/OP=ランク外キャラ
const MOSAIC20=mkMosaic(TOP20IMGS);                                   // 最後のED=TOP20キャラのみ

const steps=[];
const TOTAL=175000;
function WT(s){if(s.t==='op')return 1.5;if(s.t==='ed')return 1.4;if(s.t==='b')return .85;const r=s.r;return r===1?3.8:r<=3?2.6:r<=5?2.0:1.6;}
function buildSteps(){steps.length=0;steps.push({t:'op'});for(let r=N;r>=1;r--){if(BANNERS[r])steps.push({t:'b',r});steps.push({t:'c',r});}steps.push({t:'ed'});const sum=steps.reduce((a,s)=>a+WT(s),0);steps.forEach(s=>s.base=WT(s)/sum*TOTAL);}
const dur=s=>s.base*mult;

function esc(s){return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
function setProgP(p){const f=document.getElementById('pfill');if(!f)return;p=Math.max(0,Math.min(1,p));f.style.width=(p*100).toFixed(1)+'%';const h=330-130*p;f.style.background='linear-gradient(90deg,hsl('+h.toFixed(0)+',92%,64%),hsl('+(h+14).toFixed(0)+',95%,68%))';}
function setProg(r){setProgP((N-r)/(N-1));}

function confetti(n,gold){const th=document.getElementById('frame').className;const gl=/theme-b/.test(th)?'★':/theme-c/.test(th)?'✦':'♥';const w=document.createElement('div');w.className='cf';const cols=gold?['#ffd23f','#ffe08a','#fff3c4','#ffb800']:['#ff8ad1','#b794ff','#8fd3ff','#7df0c8','#ffd766','#ff9ec4'];for(let i=0;i<n;i++){const s=document.createElement('span');s.textContent=gl;s.style.left=(Math.random()*100).toFixed(1)+'%';s.style.color=cols[i%cols.length];s.style.fontSize=(11+Math.random()*18).toFixed(0)+'px';s.style.animationDelay=(Math.random()*.6).toFixed(2)+'s';s.style.animationDuration=(2+Math.random()*1.8).toFixed(2)+'s';w.appendChild(s);}stage.appendChild(w);later(()=>w.remove(),4600);}

// ①: SEエンジン（Web Audio合成 ＋ sounds/ にmp3があれば自動差し替え）
const SFX=(()=>{
  let ctx=null,master=null,on=false,tickTok=0,heartTok=0;
  const NAMES=['pop','ding','sparkle','fanfare','whoosh','tick','heart'];
  const FILE={};// name -> {el,ready}
  function init(){if(ctx)return;try{ctx=new (window.AudioContext||window.webkitAudioContext)();master=ctx.createGain();master.gain.value=.5;master.connect(ctx.destination);}catch(e){}
    NAMES.forEach(n=>{const el=new Audio('sounds/'+n+'.mp3');el.preload='auto';const o={el,ready:false};el.addEventListener('canplaythrough',()=>o.ready=true,{once:true});el.addEventListener('error',()=>o.ready=false);FILE[n]=o;});}
  function enable(v){on=v;init();if(ctx&&ctx.state==='suspended')ctx.resume();}
  function file(n){const f=FILE[n];if(on&&f&&f.ready){try{const c=f.el.cloneNode();c.volume=.6;c.play().catch(()=>{});return true;}catch(e){}}return false;}
  function tone(freq,t,dur,type,peak){const o=ctx.createOscillator(),g=ctx.createGain();o.type=type||'sine';o.frequency.setValueAtTime(freq,t);g.gain.setValueAtTime(0,t);g.gain.linearRampToValueAtTime(peak||.3,t+.006);g.gain.exponentialRampToValueAtTime(.0001,t+.006+dur);o.connect(g);g.connect(master);o.start(t);o.stop(t+dur+.05);}
  function slide(f0,f1,t,dur,type,peak){const o=ctx.createOscillator(),g=ctx.createGain();o.type=type||'sine';o.frequency.setValueAtTime(f0,t);o.frequency.exponentialRampToValueAtTime(f1,t+dur);g.gain.setValueAtTime(0,t);g.gain.linearRampToValueAtTime(peak||.3,t+.006);g.gain.exponentialRampToValueAtTime(.0001,t+dur);o.connect(g);g.connect(master);o.start(t);o.stop(t+dur+.05);}
  return {
    enable,
    pop(){if(file('pop')||!on||!ctx)return;slide(520,940,ctx.currentTime,.11,'triangle',.22);},
    ding(){if(file('ding')||!on||!ctx)return;const t=ctx.currentTime;tone(1318,t,.5,'sine',.3);tone(1976,t,.5,'sine',.14);},
    sparkle(){if(file('sparkle')||!on||!ctx)return;const t=ctx.currentTime;[1568,2093,2637,3136].forEach((f,i)=>tone(f,t+i*.05,.22,'sine',.14));},
    fanfare(gold){if(file('fanfare')||!on||!ctx)return;const t=ctx.currentTime;const seq=gold?[523,659,784,1047]:[523,659,784];seq.forEach((f,i)=>tone(f,t+i*.12,.34,'square',.16));tone(seq[seq.length-1],t+seq.length*.12,.5,'triangle',.2);},
    whoosh(){if(file('whoosh')||!on||!ctx)return;slide(1100,240,ctx.currentTime,.4,'sawtooth',.1);},
    rollStart(ms){if(!on||!ctx)return;const tok=++tickTok;const t0=performance.now();(function tick(){if(tok!==tickTok)return;if(performance.now()-t0>ms)return;if(!file('tick'))tone(2300,ctx.currentTime,.03,'square',.08);setTimeout(tick,70);})();},
    rollStop(){tickTok++;},
    heartStart(ms){if(!on||!ctx)return;const tok=++heartTok;const t0=performance.now();(function beat(){if(tok!==heartTok)return;if(performance.now()-t0>ms)return;if(!file('heart')){const t=ctx.currentTime;tone(120,t,.1,'sine',.25);tone(95,t+.16,.12,'sine',.22);}setTimeout(beat,520);})();},
    heartStop(){heartTok++;}
  };
})();

// 案5: 環境レイヤーを #frame に常駐注入（stage差し替えでも消えない）
function injectEnv(){const f=document.getElementById('frame');if(document.getElementById('envfx'))return;
  let h='';
  for(let i=0;i<11;i++){const sz=(14+(i*37%46));h+=`<div class="bokeh" style="width:${sz}px;height:${sz}px;left:${(i*53%100)}%;animation-duration:${(9+i*0.9).toFixed(1)}s;animation-delay:${(-i*1.3).toFixed(1)}s"></div>`;}
  for(let i=0;i<3;i++){h+=`<div class="shoot" style="left:${65+i*12}%;top:${i*14}%;animation-duration:${(6+i*1.6).toFixed(1)}s;animation-delay:${(-i*2.7).toFixed(1)}s"></div>`;}
  const env=document.createElement('div');env.id='envfx';env.innerHTML=h;
  const ht=document.createElement('div');ht.id='halftone';
  const MG=['☁️','⭐','🎀','🌈'];const SP=[['6%','9%'],['90%','13%'],['7%','85%'],['91%','87%']];
  let d='';SP.forEach((p,k)=>{d+=`<div class="mascot" style="left:${p[0]};top:${p[1]};animation-duration:${(3+k*0.4).toFixed(1)}s;animation-delay:${(-k*0.6).toFixed(1)}s">${MG[k%MG.length]}</div>`;});
  d+='<div class="dokidoki" id="doki"><span style="left:3%;top:6%">💗</span><span style="right:3%;top:6%">💗</span><span style="left:3%;bottom:6%">💗</span><span style="right:3%;bottom:6%">💗</span></div>';
  const deco=document.createElement('div');deco.id='deco';deco.innerHTML=d;
  const wipe=document.createElement('div');wipe.id='wipe';wipe.innerHTML='<div class="wipe-sweep"></div>';
  const ov=document.createElement('video');ov.id='ov';ov.muted=true;ov.loop=true;ov.playsInline=true;ov.setAttribute('playsinline','');
  ov.innerHTML='<source src="overlays/sparkle.webm" type="video/webm"><source src="overlays/sparkle.mp4" type="video/mp4">';
  ov.addEventListener('error',()=>ov.classList.remove('on'));
  const pbar=document.getElementById('pbar');
  f.insertBefore(env,pbar);f.insertBefore(ht,pbar);f.insertBefore(ov,pbar);f.insertBefore(deco,pbar);f.appendChild(wipe);}
// 案3: スライド切替のスワイプ
function doWipe(){const w=document.getElementById('wipe');if(!w)return;w.classList.remove('go');void w.offsetWidth;w.classList.add('go');SFX.whoosh();}
// 案1: リビール瞬間の放射バースト
function burst(slide,gold){const wrap=slide.querySelector('.cardwrap');if(!wrap)return;const b=document.createElement('div');b.className='burst';const gl=['★','♥','🎀','✨'];const n=gold?26:16;for(let i=0;i<n;i++){const a=Math.PI*2*i/n+(i%3)*0.18;const dist=92+(i*29%120);const s=document.createElement('span');s.textContent=gl[i%gl.length];s.style.setProperty('--bx',(Math.cos(a)*dist).toFixed(0)+'px');s.style.setProperty('--by',(Math.sin(a)*dist).toFixed(0)+'px');s.style.setProperty('--br',((i*97%720)-360)+'deg');s.style.animationDelay=((i%6)*0.015).toFixed(3)+'s';if(gold)s.style.color=['#ffd23f','#ffe08a','#fff3c4'][i%3];b.appendChild(s);}wrap.appendChild(b);later(()=>b.remove(),1100);}
// 案2: オノマトペ・ステッカー
function onoma(slide,r){const m=slide.querySelector('.cmain');if(!m)return;const txt=r===1?'ジャジャーン!!':r<=3?'おめでとう★':r<=10?'せいかい！':'だ〜れだ→せいかい★';const e=document.createElement('div');e.className='onoma';e.textContent=txt;m.appendChild(e);later(()=>e.remove(),1400);}

function delta(c){if(!c.lastRank)return null;const d=c.lastRank-c.rank;if(d>0)return{cls:'up',dir:'up',txt:'▲ '+d+'ランクUP'};if(d<0)return{cls:'down',dir:'down',txt:'▼ '+(-d)+'ランクDOWN'};return{cls:'stay',dir:'stay',txt:'＝ キープ'};}

function laneHTML(c){const pos=r=>((r-1)/(N-1)*100).toFixed(2);let t='';for(let r=1;r<=N;r++)t+=`<i class="ltick${r===c.rank?' on':''}" style="top:${pos(r)}%"></i>`;const dl=delta(c);const ghost=c.lastRank?`<i class="lghost" style="top:${pos(c.lastRank)}%"></i>`:'';const live=`<i class="llive ${dl?dl.dir:'unknown'}" data-top="${pos(c.rank)}" style="top:${c.lastRank?pos(c.lastRank):pos(c.rank)}%"></i>`;return `<div class="lane">${t}${ghost}${live}</div>`;}

function rollVotes(el,target,durMs,myGen,twoStage){const t0=performance.now();const ease=x=>1-Math.pow(1-x,3);el.classList.add('rolling');(function f(now){if(myGen!==gen)return;let p=Math.min(1,(now-t0)/durMs),e;if(twoStage){if(p<.68)e=ease(p/.68)*.988;else if(p<.84)e=.988;else e=.988+ease((p-.84)/.16)*.012;}else e=ease(p);el.textContent=fmt(Math.round(target*e));if(p<1)requestAnimationFrame(f);else{el.textContent=fmt(target);el.classList.remove('rolling');el.classList.add('ding');}})(t0);}

function profileHTML(c){return `<div class="cprofile">
  <div class="pitem"><span class="pk">🎂 誕生日</span><span class="pv">${esc(c.birthday)}</span></div>
  <div class="pitem"><span class="pk">📅 デビュー</span><span class="pv">${esc(c.debut)}</span></div>
  <div class="pitem"><span class="pk">🎯 趣味</span><span class="pv">${esc(c.hobby)}</span></div>
  <div class="pitem"><span class="pk">💕 好きなもの</span><span class="pv">${esc(c.likes)}</span></div>
</div>`;}

function charHTML(c){const p=pal(c.rank);const dl=delta(c);const lead=c.rank<N?(c.votes-byRank[c.rank+1].votes):null;const cls=['lv0','lv1','lv2','lv3','lv4'][dramaOf(c.rank)];const quiz=isQuiz(c.rank);
  return `<div class="cardslide ${cls} ${quiz?'quiz':''} ${c.rank<=10?'spotlight':''} ${c.rank===1?'champ':''}">${laneHTML(c)}<div class="spot"></div><div class="flash"></div>
  <div class="cmain"><div class="cardfx"></div>
  <div class="cardwrap"><div class="ccard"><div class="cglow"></div><div class="ph" style="background:linear-gradient(135deg,${p[0]},${p[1]})"></div><div class="sil"></div><div class="phname"><span>${esc(c.name)}</span></div><img src="${c.img}" alt="" onload="this.closest('.ccard').classList.add('hasimg')" onerror="this.remove()"></div><div class="crank">${c.rank}<span>位</span></div><div class="ctier">${tierOf(c.rank)}</div></div>
  <div class="cinfo">
    ${quiz?'<div class="qhead">❓ だ〜れだ？</div>':''}
    <div class="cname">？？？</div>
    ${profileHTML(c)}
    <div class="cbadge ${dl?dl.cls:'unk'}">${dl?dl.txt:'—'}<small>${c.lastRank?'昨年 '+c.lastRank+'位':'昨年は圏外'}</small></div>
    <div class="cvote"><b class="cnum">0</b><span class="cunit">票</span></div>
    <div class="clead">${lead!=null?'次点に <b>+'+fmt(lead)+'</b> 票':''}</div>
    <div class="cintro">${esc(c.intro)}</div>
  </div></div></div>`;}

function playChar(c,D){const myGen=gen;const slide=stage.firstElementChild;const r=c.rank;const quiz=isQuiz(r);
  // quiz: 4番目ヒント(好きなもの)のCSS delay 2600ms + 出現アニメ500ms + 追加ポーズ500ms = 最低3600ms
  const revealAt=Math.max(D*(r===1?0.60:r<=3?0.56:r<=5?0.52:0.48)+(quiz?500:0),quiz?3600:0);
  const rollDur=Math.min(r===1?5400:r<=3?4200:r<=5?3100:2000,D*0.42);
  if(quiz){[200,1000,1800,2600].forEach(d=>later(()=>{if(myGen===gen)SFX.pop();},d));}
  later(()=>{if(myGen!==gen)return;
    slide.classList.add('revealed');
    slide.querySelector('.cname').textContent=c.name;
    slide.querySelector('.flash').classList.add('go');
    burst(slide,r<=3);onoma(slide,r);SFX.ding();SFX.sparkle();
    const doki=document.getElementById('doki');if(doki){doki.classList.add('on');later(()=>{if(myGen===gen)doki.classList.remove('on');},rollDur+250);}
    const live=slide.querySelector('.llive');if(live)live.style.top=live.dataset.top+'%';
    const num=slide.querySelector('.cnum');
    SFX.rollStart(rollDur);SFX.heartStart(rollDur);later(()=>{SFX.rollStop();SFX.heartStop();if(myGen===gen&&r<=3)SFX.fanfare(r===1);},rollDur+40);
    rollVotes(num,c.votes,rollDur,myGen,r===1);
    later(()=>{if(myGen===gen)slide.querySelector('.cbadge').classList.add('show');},Math.min(rollDur*.5,500));
    if(r===1){const cl=slide.querySelector('.clead');const lead=c.votes-byRank[2].votes;later(()=>{if(myGen===gen)cl.innerHTML='2位に <b>+'+fmt(lead)+'</b> 票差！';},rollDur);}
    if(r<=3)later(()=>{if(myGen===gen)confetti(r===1?190:70,r===1);},r===1?rollDur*.55:140);
  },revealAt);
}

function renderOP(){stage.innerHTML=`<div class="op">${MOSAIC}<div class="opscrim"></div><div class="opinner"><div class="optitle">2026年<br>人気投票でえらばれた<br>いちばんすきなコ<br><b>サンリオキャラクター<br>大賞</b></div><div class="opsub">人気投票ランキング TOP20</div><div class="opvote"><span>総投票数</span><b class="cnum">0</b><span>票</span></div></div><div class="bflash"></div></div>`;const myGen=gen;const num=stage.querySelector('.cnum');later(()=>{if(myGen===gen)rollVotes(num,TOTALVOTES,2800,myGen,false);},600);setProgP(0);}
function renderED(){const list=CHARS.slice().sort((a,b)=>a.rank-b.rank);stage.innerHTML=`<div class="ed">${MOSAIC20}<div class="opscrim"></div><div class="edttl" style="position:relative;z-index:2">2026年 サンリオキャラクター大賞<br>TOP20 ♡</div><div class="edgrid" style="position:relative;z-index:2">`+list.map(c=>`<div class="ecell"><b>${c.rank}</b><span>${esc(c.name)}</span></div>`).join('')+`</div><div class="edthx" style="position:relative;z-index:2">ご投票ありがとう ♥</div></div>`;confetti(90);SFX.fanfare(true);setProgP(1);}

function render(s){gen++;clearPending();doWipe();const myGen=gen;
  if(s.t==='op'){renderOP();return;}
  if(s.t==='ed'){renderED();return;}
  if(s.t==='b'){const[x,y]=BANNERS[s.r];const sp=s.r===1?'champx':s.r<=10?'top10x':'';stage.innerHTML=`<div class="banner ${sp}">${MOSAIC}<div class="bscrim"></div><div class="bshock"></div><div class="btxt">${x}</div><div class="bsub">${y}</div><div class="bflash"></div></div>`;setProg(s.r);if(s.r<=10){later(()=>{if(myGen===gen)confetti(s.r===1?70:36,s.r<=3);},140);later(()=>{if(myGen===gen)SFX.fanfare(s.r<=3);},180);}return;}
  const c=byRank[s.r];stage.innerHTML=charHTML(c);setProg(s.r);playChar(c,dur(s));}

function step(){render(steps[si]);if(timer){clearTimeout(timer);timer=null;}if(playing)timer=setTimeout(()=>{if(si<steps.length-1){si++;step();}else{playing=false;updateBtn();}},dur(steps[si]));updateProg();}
function updateProg(){const s=steps[si];const lbl=s.t==='op'?'オープニング':s.t==='ed'?'エンディング':s.t==='b'?'— 章 —':s.r+'位'+(isQuiz(s.r)?'(クイズ)':'');document.getElementById('prog').textContent=lbl+' / 残り'+Math.max(0,steps.length-1-si);}
function updateBtn(){document.getElementById('pp').textContent=playing?'⏸':'▶';}
function play(){playing=true;updateBtn();step();}
function pause(){playing=false;clearPending();updateBtn();}
function applyTheme(){const f=document.getElementById('frame');f.classList.remove('theme-a','theme-b','theme-c');f.classList.add(THC[theme]);document.getElementById('th').textContent='テーマ'+THN[theme];}

document.getElementById('pp').onclick=()=>playing?pause():play();
document.getElementById('rs').onclick=()=>{si=0;play();};
document.getElementById('nx').onclick=()=>{if(si<steps.length-1){si++;pause();render(steps[si]);updateProg();}};
document.getElementById('pv').onclick=()=>{if(si>0){si--;pause();render(steps[si]);updateProg();}};
document.getElementById('sp').onchange=e=>{mult=+e.target.value;buildSteps();};
document.getElementById('th').onclick=()=>{theme=(theme+1)%3;applyTheme();};
document.getElementById('or').onclick=()=>{const f=document.getElementById('frame');f.classList.toggle('horiz');document.getElementById('or').textContent=f.classList.contains('horiz')?'横 16:9':'縦 9:16';pause();render(steps[si]);updateProg();};
document.getElementById('fs').onclick=()=>{const f=document.getElementById('frame');(f.requestFullscreen||f.webkitRequestFullscreen||(()=>{})).call(f);};
const bgm=document.getElementById('bgm');let soundOn=false;
document.getElementById('mu').onclick=()=>{soundOn=!soundOn;SFX.enable(soundOn);if(soundOn){bgm.play().catch(()=>{});document.getElementById('mu').textContent='\u{1F50A} 音ON';}else{bgm.pause();document.getElementById('mu').textContent='\u{1F507} 音OFF';}};
document.getElementById('ovb').onclick=()=>{const v=document.getElementById('ov');if(!v)return;const on=v.classList.toggle('on');document.getElementById('ovb').classList.toggle('active',on);if(on)v.play().catch(()=>{});else v.pause();};

injectEnv();applyTheme();buildSteps();updateBtn();step();
"""

HTML = """<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>2026年 サンリオキャラクター大賞 TOP20 ✦ カウントダウン</title>
<link href="https://fonts.googleapis.com/css2?family=Mochiy+Pop+One&family=Baloo+2:wght@800&family=M+PLUS+Rounded+1c:wght@700;800&family=Yomogi&family=Kosugi+Maru&display=swap" rel="stylesheet">
<style>__CSS__</style></head><body>
  <div id="frame" class="theme-b"><div id="stage"></div><div id="pbar"><div id="pfill"></div></div></div>
  <div class="ctl">
    <button id="pv">⏮</button><button id="pp">⏸</button><button id="nx">⏭</button><button id="rs">↺ 最初から</button>
    <span class="prog" id="prog">—</span>
    速度<select id="sp"><option value="1.5">ゆっくり</option><option value="1" selected>標準(約3分)</option><option value="0.6">速い</option></select>
    <button id="th">テーマ②キャンディ</button><button id="or">横 16:9</button><button id="fs">⛶ 全画面</button><button id="ovb">✨ 素材</button><button id="mu">🔇 音OFF</button>
  </div>
  <div class="hint"><b>全20位</b>「誕生日／デビュー年／趣味／好きなもの」を1つずつ出す<b>プロフィールクイズ</b>でタメてから公開。投票数の<b>カウントアップ</b>がタメの主役で、画面左の<b>順位レーン</b>が下剋上を可視化。<b>No.1は二段階確定ニアミス</b>で爆発。<b>「テーマ」</b>で可愛い配色3案を切替。<b>「🔇音」</b>で効果音＋BGM(自動合成。sounds/に置けばフリー素材に差替)、<b>「✨素材」</b>で加算合成オーバーレイ(overlays/で差替)。⛶全画面→画面収録で動画化。データは sanrio_data.csv を編集して再ビルド。</div>
  <audio id="bgm" src="movie_bgm.mp3" loop></audio>
  <script>__JS__</script>
</body></html>"""

JS_FULL = JS.replace("__CHARS__", CHARS_JSON).replace("__OUTIMGS__", OUTIMGS_JSON)
OUT = HTML.replace("__CSS__", CSS).replace("__JS__", JS_FULL)
open("sanrio_movie.html", "w", encoding="utf-8").write(OUT)
print(f"sanrio_movie.html 生成完了（{len(rows)}キャラ・2026データ・4項目クイズ・3テーマ）")
