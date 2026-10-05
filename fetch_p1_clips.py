#!/usr/bin/env python3
"""前半（101〜200位）のクリップを自動収集する。
- 予算: 前半動画 299秒以下 → 前半クリップは合計44本まで（4×44+2×56+ロール10=298秒）
- 101位側から優先して、クリップ未所持のゲームを順に取得
- 取得経路: ①Steamトレーラー（storesearch→appdetails→HLS切り出し） ②YouTube検索（yt-dlp ytsearch）
- 記録: YouTube産→ game_clips/sources.json + clip_meta.json {start,url}
        Steam産  → clip_meta.json {start}（sources.json に載せない＝Steam産の既存規約）
  → 以後は clips_review.html で検品し、clip_meta.json 調整 → fetch_clip_meta.py で差し替え可能
使い方: python3 fetch_p1_clips.py
        続けて python3 fetch_steam_trailers.py（レビュー用トレーラー取得）
        python3 build_clips_review.py && python3 build_movie.py"""
import difflib, glob, json, os, re, ssl, subprocess, time, urllib.parse, urllib.request

os.chdir(os.path.dirname(os.path.abspath(__file__)))
OUT = "game_clips"; TMP = "/tmp/ytclips"; os.makedirs(TMP, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0"}
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE
P1_CLIP_MAX = 44  # 前半クリップ本数の上限（299秒予算）

# ---- ランキング読み込み ----
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

src = open("fetch_covers.py", encoding="utf-8").read()
m = re.search(r'QUERY_FIX = (\{.*?\n\})', src, re.S)
QUERY_FIX = eval(m.group(1)) if m else {}

META = json.load(open("clip_meta.json", encoding="utf-8")) if os.path.exists("clip_meta.json") else {}
SRC_JSON = f"{OUT}/sources.json"
sources = json.load(open(SRC_JSON, encoding="utf-8")) if os.path.exists(SRC_JSON) else {}

def getj(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30, context=CTX) as r:
        return json.load(r)

def save_meta():
    json.dump(META, open("clip_meta.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(sources, open(SRC_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

def simila(a, b):
    a = re.sub(r'\s', '', a.lower()); b = re.sub(r'\s', '', b.lower())
    if a in b or b in a: return 1.0
    return difflib.SequenceMatcher(None, a, b).ratio()

def try_steam(cid, title):
    """Steamトレーラーから切り出し。成功時 start を返す"""
    q = QUERY_FIX.get(title, title)
    try:
        d = getj("https://store.steampowered.com/api/storesearch/?term=" + urllib.parse.quote(q) + "&cc=jp&l=japanese")
        items = d.get("items", [])
        if not items: return None
        item = items[0]
        if simila(q, item.get("name", "")) < 0.45:  # 別ゲーム誤マッチ防止
            return None
        appid = item["id"]
        ad = getj(f"https://store.steampowered.com/api/appdetails?appids={appid}&cc=jp&l=japanese")
        data = (ad.get(str(appid)) or {}).get("data") or {}
        # appdetails側の名前でも確認
        if simila(q, data.get("name", "")) < 0.45: return None
        movies = data.get("movies") or []
        if not movies: return None
        stream = movies[0].get("hls_h264") or movies[0].get("dash_h264")
        if not stream: return None
        s = 4
        tmp = f"{TMP}/p1_c{cid}.mp4"
        rr = subprocess.run(["ffmpeg","-y","-loglevel","error","-ss",str(s),"-i",stream,"-t","10","-an",
                             "-vf","scale=-2:720","-c:v","libx264","-preset","veryfast","-crf","26","-pix_fmt","yuv420p",tmp],
                            capture_output=True, timeout=300)
        if rr.returncode == 0 and os.path.exists(tmp) and os.path.getsize(tmp) > 30000:
            os.replace(tmp, f"{OUT}/c{cid}.mp4")
            print(f"  → Steam OK: {data.get('name','')[:36]} (appid {appid})")
            return s
        if os.path.exists(tmp): os.remove(tmp)
    except Exception as e:
        print(f"  → Steam ERR {type(e).__name__}")
    return None

def try_youtube(cid, title):
    """YouTube検索→セクションDL。成功時 (start, url) を返す"""
    query = f"ytsearch5:{title} ゲームプレイ"
    try:
        p = subprocess.run(["yt-dlp", query, "--flat-playlist",
                            "--print", "%(id)s\t%(title)s\t%(duration)s",
                            "--no-warnings", "--quiet", "--socket-timeout", "20"],
                           capture_output=True, text=True, timeout=120)
        cands = []
        for ln in p.stdout.strip().split("\n"):
            parts = ln.split("\t")
            if len(parts) != 3: continue
            vid, vt, du = parts
            try: du = int(float(du))
            except ValueError: du = 0
            cands.append((vid, vt, du))
        # 2分〜3時間の動画を優先（ショート・超長尺配信を避ける）
        pick = next((x for x in cands if 120 <= x[2] <= 10800), None) or next((x for x in cands if x[2] >= 60), None)
        if not pick: return None
        vid, vt, du = pick
        s = 90 if du >= 150 else max(5, du // 3)
        if s + 10 > du: s = max(0, du - 12)
        url = f"https://www.youtube.com/watch?v={vid}"
        for f_ in glob.glob(f"{TMP}/yt_c{cid}.*"): os.remove(f_)
        subprocess.run(["yt-dlp", url, "--no-playlist",
                        "--download-sections", f"*{s}-{s+10}", "--force-keyframes-at-cuts",
                        "-f", "bv*[height<=720]/b[height<=720]/b",
                        "--socket-timeout", "20", "--retries", "2", "--no-warnings", "--quiet",
                        "-o", f"{TMP}/yt_c{cid}.%(ext)s"], capture_output=True, timeout=300)
        files = [f_ for f_ in glob.glob(f"{TMP}/yt_c{cid}.*") if not f_.endswith((".part", ".ytdl"))]
        if not files: return None
        tmp2 = f"{OUT}/c{cid}.mp4.tmp.mp4"
        rr = subprocess.run(["ffmpeg","-y","-loglevel","error","-i",files[0],"-t","10","-an",
                             "-vf","scale=-2:720","-c:v","libx264","-preset","veryfast","-crf","26","-pix_fmt","yuv420p",tmp2],
                            capture_output=True, timeout=180)
        for f_ in files: os.remove(f_)
        if rr.returncode == 0 and os.path.exists(tmp2) and os.path.getsize(tmp2) > 30000:
            os.replace(tmp2, f"{OUT}/c{cid}.mp4")
            sources[str(cid)] = {"yt_title": vt, "url": url, "start": s}
            print(f"  → YouTube OK: {vt[:40]} ({du}s, {s}秒〜)")
            return (s, url)
        if os.path.exists(tmp2): os.remove(tmp2)
    except subprocess.TimeoutExpired:
        print("  → YouTube TIMEOUT")
    except Exception as e:
        print(f"  → YouTube ERR {type(e).__name__}")
    return None

# ---- 対象決定: 前半(101-200位)で、101位側から優先 ----
p1_ranks = sorted(r for r in rank if 101 <= r <= 200)
have = [r for r in p1_ranks if os.path.exists(f"{OUT}/c{title2cid[rank[r]]}.mp4")]
need = P1_CLIP_MAX - len(have)
print(f"前半クリップ: 現在{len(have)}本 / 上限{P1_CLIP_MAX}本 → あと{need}本取得")

got, fail = [], []
for r in p1_ranks:
    if need <= 0: break
    cid = title2cid[rank[r]]
    if os.path.exists(f"{OUT}/c{cid}.mp4"): continue
    title = rank[r]
    print(f"{r}位 c{cid} {title[:28]}", flush=True)
    res = try_steam(cid, title)
    if res is not None:
        META[str(cid)] = {**(META.get(str(cid)) or {}), "start": res}
        got.append(r); need -= 1; save_meta(); continue
    time.sleep(3)  # YouTubeレート制限対策
    res = try_youtube(cid, title)
    if res is not None:
        s, url = res
        META[str(cid)] = {**(META.get(str(cid)) or {}), "start": s, "url": url}
        got.append(r); need -= 1; save_meta(); continue
    print("  → 取得失敗（両経路NG）")
    fail.append(r)
    time.sleep(2)

save_meta()
print(f"\n=== 取得 {len(got)}本 / 失敗 {len(fail)}件 ===")
if fail: print("失敗:", ", ".join(f"{r}位" for r in fail))
n_clips = sum(1 for r in p1_ranks if os.path.exists(f"{OUT}/c{title2cid[rank[r]]}.mp4"))
total = 4 * n_clips + 2 * (len(p1_ranks) - n_clips) + 10
print(f"前半クリップ計{n_clips}本 → 前半動画 {total}秒（≤299秒: {'OK' if total <= 299 else 'NG!'}）")
print("次: python3 fetch_steam_trailers.py && python3 build_clips_review.py && python3 build_movie.py")
