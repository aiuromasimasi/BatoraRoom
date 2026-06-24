#!/usr/bin/env python3
"""candidates.json から、採用ピックの候補URLだけを game_covers/<順位>.jpg に保存する。
使い方:
  python3 fetch_picks.py 1:A 8:A 24:A ...
  （順位:ラベル を空白区切りで。'順位:なし' は無視）
PNG/webp等で来た場合は sips でJPEGへ変換（失敗時はそのまま保存＝<img>は内容判定で表示可）。
"""
import json, os, subprocess, sys, tempfile, urllib.request

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 BatoraFanPage/1.0"
cand = json.load(open("candidates.json", encoding="utf-8"))
os.makedirs("game_covers", exist_ok=True)

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()

def save_jpeg(data, dst):
    if data[:3] == b"\xff\xd8\xff":  # already JPEG
        open(dst, "wb").write(data); return "jpeg"
    # それ以外は sips で変換を試みる
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        tf.write(data); tmp = tf.name
    try:
        subprocess.run(["sips", "-s", "format", "jpeg", tmp, "--out", dst],
                       check=True, capture_output=True)
        os.unlink(tmp); return "converted"
    except Exception:
        open(dst, "wb").write(data)  # フォールバック: 生バイトを.jpgで保存
        if os.path.exists(tmp): os.unlink(tmp)
        return "raw"

picks = {}
for a in sys.argv[1:]:
    if ":" not in a:
        continue
    r, lab = a.split(":", 1)
    if lab.strip() in ("なし", "none", "-"):
        continue
    picks[r.strip()] = lab.strip().upper()

for r, lab in picks.items():
    items = cand.get(str(r), [])
    it = next((x for x in items if x.get("label") == lab), None)
    if not it:
        print(f"{r}: ラベル{lab} の候補なし → スキップ"); continue
    dst = f"game_covers/{r}.jpg"
    data = None
    for url in (it["url"], it.get("fallback") or ""):
        if not url:
            continue
        try:
            b = get(url)
            if b and len(b) > 1500:
                data = b; break
        except Exception as e:
            print(f"  {r}: 取得失敗 {url[:50]} ({e})")
    if not data:
        print(f"{r}: ダウンロード失敗 → スキップ"); continue
    how = save_jpeg(data, dst)
    print(f"{r}: OK [{lab}/{it['source']}] {how}  {it['note'][:36]}")

print("done")
