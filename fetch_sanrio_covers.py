#!/usr/bin/env python3
"""sanrio_candidates.json の候補URLから採用ピックを sanrio_covers/cN.png に保存。

運用: Web取得 → アップスケール → (sanrio_covers_review.html で)確認 → 問題があれば差し替え。

使い方:
  python3 fetch_sanrio_covers.py                 # 全キャラの候補A を取得(既定)
  python3 fetch_sanrio_covers.py 1:B 8:C 14:A    # 順位:ラベル を個別指定(差し替え)
  python3 fetch_sanrio_covers.py --upscale 2     # 取得後 sips で2倍リサンプル(簡易アップスケール)
  （順位:なし は無視 / 個別指定が無い順位は触らない。引数に順位指定が1つも無ければ全A取得）

注意:
- ここでの --upscale は sips(bicubic)の簡易拡大。ディテール復元はしない。高品質化は外部AIアップスケーラ
  (Real-ESRGAN/waifu2x 等)を sanrio_covers/ のPNGに適用するのを推奨。
- 画像はサンリオ公式の著作物。利用範囲は各自で確認すること。
"""
import json, os, subprocess, sys, tempfile, urllib.request

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 BatoraFanPage/1.0"
OUT = "sanrio_covers"
os.makedirs(OUT, exist_ok=True)
cand = json.load(open("sanrio_candidates.json", encoding="utf-8"))

# 引数パース
upscale = None
picks = {}
args = sys.argv[1:]
i = 0
while i < len(args):
    a = args[i]
    if a == "--upscale":
        i += 1; upscale = float(args[i]) if i < len(args) else 2.0
    elif ":" in a:
        r, lab = a.split(":", 1)
        if lab.strip() not in ("なし", "none", "-"):
            picks[r.strip()] = lab.strip().upper()
    i += 1

# 個別指定が無ければ全キャラの候補A
if not picks:
    picks = {r: "A" for r in cand.keys()}
    print(f"[既定] 全{len(picks)}キャラの候補A を取得します")

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()

def save_png(data, dst):
    """PNGで保存。PNG以外は sips でPNGへ変換。"""
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        open(dst, "wb").write(data); return "png"
    with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as tf:
        tf.write(data); tmp = tf.name
    try:
        subprocess.run(["sips", "-s", "format", "png", tmp, "--out", dst],
                       check=True, capture_output=True)
        return "converted"
    except Exception:
        open(dst, "wb").write(data); return "raw"
    finally:
        if os.path.exists(tmp): os.unlink(tmp)

def do_upscale(path, factor):
    try:
        out = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", path],
                             check=True, capture_output=True, text=True).stdout
        w = h = None
        for line in out.splitlines():
            if "pixelWidth" in line: w = int(line.split(":")[1])
            if "pixelHeight" in line: h = int(line.split(":")[1])
        if not w or not h: return False
        subprocess.run(["sips", "-z", str(int(h*factor)), str(int(w*factor)), path],
                       check=True, capture_output=True)
        return True
    except Exception as e:
        print(f"   upscale失敗 {os.path.basename(path)}: {e}"); return False

ok = 0
for r, lab in sorted(picks.items(), key=lambda x: int(x[0])):
    entry = cand.get(str(r))
    if not entry:
        print(f"{r}: 候補なし → スキップ"); continue
    it = next((x for x in entry["candidates"] if x.get("label") == lab), None)
    if not it:
        print(f"{r}: ラベル{lab} の候補なし → スキップ"); continue
    dst = f"{OUT}/c{r}.png"
    data = None
    for url in (it["url"], it.get("fallback") or ""):
        if not url: continue
        try:
            b = get(url)
            if b and len(b) > 1500:
                data = b; break
        except Exception as e:
            print(f"  {r}: 取得失敗 {url[:60]} ({e})")
    if not data:
        print(f"{r}: ダウンロード失敗 → スキップ"); continue
    how = save_png(data, dst)
    up = ""
    if upscale:
        up = " +upscale" if do_upscale(dst, upscale) else ""
    sz = os.path.getsize(dst)
    print(f"{r:>2}: OK [{lab}/{entry['name']}] {how}{up}  {sz//1024}KB  {it['note'][:30]}")
    ok += 1

print(f"done ({ok}/{len(picks)})  → {OUT}/cN.png")
