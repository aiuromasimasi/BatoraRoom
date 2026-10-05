#!/usr/bin/env python3
"""Steam産クリップの元トレーラーを全部ローカル保存（プレビュー用・360p軽量版）。
- 対象: game_clips/ にあり sources.json(YouTube出典) に載っていない cid ＝ Steam産
- 各ゲームの movies[] を全件DL → game_trailers/c<cid>_t<idx>.mp4（音声つき360p）
- game_trailers/index.json に {cid: {appid, game, movies:[{i,name,file,dur}]}} を記録
  → clips_review.html のフル視聴プレビュー / fetch_clip_meta.py のSteam切り直しに使う
使い方: python3 fetch_steam_trailers.py（再実行で差分のみ取得）"""
import glob, json, os, re, ssl, subprocess, time, urllib.parse, urllib.request

os.chdir(os.path.dirname(os.path.abspath(__file__)))
OUT = "game_trailers"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0"}
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE
MAX_TRAILERS = 5  # 1ゲームあたり最大

lines = open("game_ranking_draft.md", encoding="utf-8").read().split("\n")
title2cid = {}; c = 0
for l in lines:
    if l.startswith("---"): break
    if l.startswith("- "):
        c += 1; title2cid[l[2:].strip()] = c
cid2title = {v: k for k, v in title2cid.items()}

src = open("fetch_covers.py", encoding="utf-8").read()
m = re.search(r'QUERY_FIX = (\{.*?\n\})', src, re.S)
QUERY_FIX = eval(m.group(1)) if m else {}
APPID_FIX = {26: 39140, 22: 1173790, 23: 1173800, 24: 1173810, 25: 1173820,
             73: 646570, 93: 1509960, 40: 413420, 74: 39530, 64: 2320}

sources = json.load(open("game_clips/sources.json", encoding="utf-8")) if os.path.exists("game_clips/sources.json") else {}
index = json.load(open(f"{OUT}/index.json", encoding="utf-8")) if os.path.exists(f"{OUT}/index.json") else {}

def getj(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30, context=CTX) as r:
        return json.load(r)

# Steam産 = クリップがあり sources.json に無い cid
steam_cids = sorted(int(re.search(r'c(\d+)\.mp4$', p).group(1)) for p in glob.glob("game_clips/c*.mp4"))
steam_cids = [cid for cid in steam_cids if str(cid) not in sources]
print(f"Steam産クリップ: {len(steam_cids)}件", flush=True)

for cid in steam_cids:
    title = cid2title.get(cid, "?")
    try:
        if str(cid) in index and all(os.path.exists(mv["file"]) for mv in index[str(cid)]["movies"]):
            print(f"c{cid:<4} {title[:20]:<20} SKIP(取得済{len(index[str(cid)]['movies'])}本)", flush=True); continue
        if cid in APPID_FIX:
            appid = APPID_FIX[cid]
        else:
            d = getj("https://store.steampowered.com/api/storesearch/?term=" + urllib.parse.quote(QUERY_FIX.get(title, title)) + "&cc=jp&l=japanese")
            items = d.get("items", [])
            if not items:
                print(f"c{cid:<4} {title[:20]:<20} NO-MATCH", flush=True); continue
            appid = items[0]["id"]
        ad = getj(f"https://store.steampowered.com/api/appdetails?appids={appid}&cc=jp&l=japanese")
        data = (ad.get(str(appid)) or {}).get("data") or {}
        movies = (data.get("movies") or [])[:MAX_TRAILERS]
        if not movies:
            print(f"c{cid:<4} {title[:20]:<20} NO-MOVIE", flush=True); continue
        ent = {"appid": appid, "game": data.get("name",""), "movies": []}
        for i, mv in enumerate(movies):
            stream = mv.get("hls_h264") or mv.get("dash_h264")
            if not stream: continue
            f_ = f"{OUT}/c{cid}_t{i}.mp4"
            if not os.path.exists(f_):
                rr = subprocess.run(["ffmpeg","-y","-loglevel","error","-i",stream,
                                     "-vf","scale=-2:360","-c:v","libx264","-preset","veryfast","-crf","30",
                                     "-c:a","aac","-b:a","64k","-pix_fmt","yuv420p",f_],
                                    capture_output=True, timeout=600)
                if rr.returncode != 0 or not os.path.exists(f_) or os.path.getsize(f_) < 30000:
                    if os.path.exists(f_): os.remove(f_)
                    print(f"  c{cid} t{i}: DL失敗", flush=True); continue
            p = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f_],
                               capture_output=True, text=True)
            dur = round(float(p.stdout.strip() or 0))
            ent["movies"].append({"i": i, "name": mv.get("name",f"トレーラー{i+1}"), "file": f_, "dur": dur})
        if ent["movies"]:
            index[str(cid)] = ent
            json.dump(index, open(f"{OUT}/index.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
            tot = sum(os.path.getsize(mv["file"]) for mv in ent["movies"]) // 1048576
            print(f"c{cid:<4} {title[:20]:<20} OK {len(ent['movies'])}本 {tot}MB ({ent['game'][:24]})", flush=True)
    except Exception as e:
        print(f"c{cid:<4} {title[:20]:<20} ERR {type(e).__name__}", flush=True)
    time.sleep(.2)

total = sum(os.path.getsize(f_) for f_ in glob.glob(f"{OUT}/*.mp4")) // 1048576
print(f"\n=== 完了: {len(index)}ゲーム / 合計{total}MB → clips_review.html を再生成してください ===")
