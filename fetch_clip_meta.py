#!/usr/bin/env python3
"""clip_meta.json の指定に従いクリップを取り直す。
  clip_meta.json: { "18": {"start": 222, "pos": "left", "url": "...", "tidx": 1}, ... }
  - start: 切り出し開始秒（省略時: YouTube=90 / Steam=4）
  - url  : YouTube差し替えURL（省略時: sources.json の出典 → 無ければSteam産として処理）
  - tidx : Steamトレーラー番号（clips_review.html のドロップダウンで選択。省略時0）
  - pos  : 表示位置（left/right）— 再取得不要。build_movie.py が読む
start / url / tidx のあるエントリだけ再ダウンロードする。
Steam産は game_trailers/index.json（fetch_steam_trailers.py が生成）の appid を使う。
使い方: python3 fetch_clip_meta.py && python3 build_movie.py"""
import glob, json, os, ssl, subprocess, urllib.request

os.chdir(os.path.dirname(os.path.abspath(__file__)))
OUT = "game_clips"; TMP = "/tmp/ytclips"; os.makedirs(TMP, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0"}
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE
META = json.load(open("clip_meta.json", encoding="utf-8")) if os.path.exists("clip_meta.json") else {}
SRC_JSON = f"{OUT}/sources.json"
sources = json.load(open(SRC_JSON, encoding="utf-8")) if os.path.exists(SRC_JSON) else {}
TRAILERS = json.load(open("game_trailers/index.json", encoding="utf-8")) if os.path.exists("game_trailers/index.json") else {}

def getj(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30, context=CTX) as r:
        return json.load(r)

def norm(src_file, dst):
    """720p/無音/10秒に正規化。成功時のみ dst を置き換え"""
    tmp = dst + ".tmp.mp4"
    rr = subprocess.run(["ffmpeg","-y","-loglevel","error","-i",src_file,"-t","10","-an",
                         "-vf","scale=-2:720","-c:v","libx264","-preset","veryfast","-crf","26","-pix_fmt","yuv420p",tmp],
                        capture_output=True, timeout=180)
    if rr.returncode == 0 and os.path.exists(tmp) and os.path.getsize(tmp) > 30000:
        os.replace(tmp, dst); return True
    if os.path.exists(tmp): os.remove(tmp)
    return False

todo = [(cid, ent) for cid, ent in META.items()
        if ent.get("start") is not None or ent.get("url") or ent.get("tidx") is not None]
if not todo:
    print("再取得対象なし（start / url / tidx 指定のあるエントリがありません。pos だけなら build_movie.py の再実行のみでOK）")
    raise SystemExit

ok, ng = [], []
for cid, ent in todo:
    dst = f"{OUT}/c{cid}.mp4"
    yt_url = ent.get("url") or (sources.get(str(cid)) or {}).get("url")
    if yt_url and yt_url != "?":
        # ---- YouTube 経路 ----
        s = int(ent.get("start") or 90)
        yt_url = yt_url.split("&list")[0]
        for f_ in glob.glob(f"{TMP}/yt_c{cid}.*"): os.remove(f_)
        meta = f"{TMP}/meta_c{cid}.txt"
        if os.path.exists(meta): os.remove(meta)
        print(f"c{cid}: YouTube {yt_url[:44]}  {s}秒〜", flush=True)
        try:
            subprocess.run(["yt-dlp", yt_url, "--no-playlist",
                            "--download-sections", f"*{s}-{s+10}", "--force-keyframes-at-cuts",
                            "-f", "bv*[height<=720]/b[height<=720]/b",
                            "--socket-timeout", "20", "--retries", "2", "--no-warnings", "--quiet",
                            "--print-to-file", "%(title)s\t%(webpage_url)s", meta,
                            "-o", f"{TMP}/yt_c{cid}.%(ext)s"], capture_output=True, timeout=300)
        except subprocess.TimeoutExpired:
            print(f"c{cid}: TIMEOUT"); ng.append(cid); continue
        files = [f_ for f_ in glob.glob(f"{TMP}/yt_c{cid}.*") if not f_.endswith((".part",".ytdl"))]
        if not files:
            print(f"c{cid}: ダウンロード失敗（URL/開始秒を確認）"); ng.append(cid); continue
        good = norm(files[0], dst)
        for f_ in files: os.remove(f_)
        if not good:
            print(f"c{cid}: 変換失敗"); ng.append(cid); continue
        vt, vu = "?", yt_url
        if os.path.exists(meta):
            p = open(meta, encoding="utf-8").read().strip().split("\t")
            if len(p) >= 2: vt, vu = p[0], p[1]
        e = sources.get(str(cid)) or {}
        e.update({"yt_title": vt, "url": vu, "start": s})
        sources[str(cid)] = e
        json.dump(sources, open(SRC_JSON,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"c{cid}: OK ({os.path.getsize(dst)//1024}KB) ← {vt[:40]}"); ok.append(cid)
    else:
        # ---- Steam 経路（game_trailers/index.json の appid + tidx で切り直し） ----
        info = TRAILERS.get(str(cid))
        if not info:
            print(f"c{cid}: Steam情報なし（先に python3 fetch_steam_trailers.py を実行するか url を指定）"); ng.append(cid); continue
        tidx = int(ent.get("tidx") or 0); s = int(ent.get("start") or 4)
        try:
            ad = getj(f"https://store.steampowered.com/api/appdetails?appids={info['appid']}&cc=jp&l=japanese")
            movies = ((ad.get(str(info["appid"])) or {}).get("data") or {}).get("movies") or []
            if tidx >= len(movies):
                print(f"c{cid}: トレーラー{tidx}が存在しない（全{len(movies)}本）"); ng.append(cid); continue
            stream = movies[tidx].get("hls_h264") or movies[tidx].get("dash_h264")
            if not stream:
                print(f"c{cid}: ストリームなし"); ng.append(cid); continue
            tmp = f"{TMP}/steam_c{cid}.mp4"
            print(f"c{cid}: Steam {info['game'][:24]} トレーラー{tidx+1}  {s}秒〜", flush=True)
            rr = subprocess.run(["ffmpeg","-y","-loglevel","error","-ss",str(s),"-i",stream,"-t","10","-an",
                                 "-vf","scale=-2:720","-c:v","libx264","-preset","veryfast","-crf","26","-pix_fmt","yuv420p",tmp],
                                capture_output=True, timeout=300)
            if rr.returncode == 0 and os.path.exists(tmp) and os.path.getsize(tmp) > 30000:
                os.replace(tmp, dst)
                print(f"c{cid}: OK ({os.path.getsize(dst)//1024}KB)"); ok.append(cid)
            else:
                if os.path.exists(tmp): os.remove(tmp)
                print(f"c{cid}: 切り出し失敗（開始{s}秒がトレーラー尺超過の可能性）→ 旧クリップ温存"); ng.append(cid)
        except Exception as e:
            print(f"c{cid}: ERR {type(e).__name__}"); ng.append(cid)

print(f"\n=== OK:{len(ok)} NG:{len(ng)} ===  続けて python3 build_movie.py を実行してください")
