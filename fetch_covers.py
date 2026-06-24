#!/usr/bin/env python3
"""ベストエフォートでカバー画像を収集して game_covers/<順位>.jpg に保存する。

優先ソース: Steam 公式ストア（縦長カプセル library_600x900＝ポスター型でタイルに最適）。
- Steam ストア検索APIで appid を解決 → 公式CDNから縦長カプセルを取得（無ければ header.jpg）。
- Steam に無いタイトル（レトロ/アーケード/同人/コンシューマ専用 等）は取得できないので
  プレースホルダー（カラータイル）のまま。
- 取得済み(非空)はスキップするので再実行で差分だけ補完できる。
※ 取得結果は「自分の順位タイトル → Steamでヒットした名前」をログ出力。誤マッチ確認に使う。

使い方: python3 fetch_covers.py
"""
import json, os, re, time, urllib.parse, urllib.request

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 BatoraFanPage/1.0"
OUT = "game_covers"
os.makedirs(OUT, exist_ok=True)

# rank -> title
rank = {}
for l in open("game_ranking_draft.md", encoding="utf-8"):
    m = re.match(r'^(\d+)\.\s+(.*)$', l)
    if m:
        rank[int(m.group(1))] = m.group(2).strip()

# 検索精度を上げるためのクエリ補正（よくある別表記）
QUERY_FIX = {
    "ブレス オブ ザ ワイルド": "The Legend of Zelda Breath of the Wild",
    "ティアーズ オブ ザ キングダム": "The Legend of Zelda Tears of the Kingdom",
    "STEINS;GATE": "STEINS GATE",
    "ファイナルファンタジー7": "FINAL FANTASY VII",
    "ファイナルファンタジー6": "FINAL FANTASY VI",
    "ファイナルファンタジー5": "FINAL FANTASY V",
    "ファイナルファンタジー4": "FINAL FANTASY IV",
    "ファイナルファンタジー3": "FINAL FANTASY III",
    "斑鳩 IKARUGA": "Ikaruga",
    "TETRIS THE GRAND MASTER 4 -ABSOLUTE EYE-": "Tetris The Grand Master 4 Absolute Eye",
    "NieR:Automata": "NieR Automata",
    "Slay the Spire": "Slay the Spire",
    "It Takes Two": "It Takes Two",
    "PICO PARK": "PICO PARK",
    "デイヴ・ザ・ダイバー": "Dave the Diver",
    "Orcs Must Die! 3": "Orcs Must Die 3",
    "VA-11 Hall-A": "VA-11 Hall-A",
    "都市伝説解体センター": "都市伝説解体センター",
    "レイジングループ": "Raging Loop",
    "キミガシネ": "Your Turn To Die",
    "God of War": "God of War",
    "UNDERTALE": "Undertale",
    "CUPHEAD": "Cuphead",
    "QUAKE": "Quake",
    "UNREAL": "Unreal Gold",
    "Unreal Tournament": "Unreal Tournament",
    "Left 4 Dead": "Left 4 Dead",
    "ディアブロII": "Diablo II Resurrected",
    "ロックマン2": "Mega Man 2",
}

# Steamに原典が無い等で検索が必ず別ゲームを拾うタイトルは取得せずプレースホルダーのまま
SKIP_TITLES = {"ICO", "真・女神転生", "StarCraft", "ロックマン2", "PICO PARK"}

# 検索だと別ゲーム/続編を拾ってしまうタイトルは、確実な公式appidを直接指定
APPID_OVERRIDE = {
    "QUAKE": 2310,          # Quake (1996 原典)
    "Left 4 Dead": 500,     # Left 4 Dead (1)
    "Slay the Spire": 646570,
    "AIR": 2983250,         # AIR (Key / Steam版)
}

def http_get(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "ja,en"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def steam_appid(term):
    url = "https://store.steampowered.com/api/storesearch/?" + urllib.parse.urlencode(
        {"term": term, "cc": "jp", "l": "japanese"})
    try:
        data = json.loads(http_get(url).decode("utf-8", "replace"))
    except Exception:
        return None, None
    items = data.get("items") or []
    if not items:
        return None, None
    return items[0].get("id"), items[0].get("name")

def try_download(appid):
    cdn = "https://cdn.cloudflare.steamstatic.com/steam/apps/%s/%s"
    for fn in ("library_600x900_2x.jpg", "library_600x900.jpg", "header.jpg"):
        try:
            b = http_get(cdn % (appid, fn))
            if b and len(b) > 2000 and b[:3] == b"\xff\xd8\xff":  # valid jpeg
                return b, fn
        except Exception:
            pass
    return None, None

results = []
for r in range(1, 101):
    dst = os.path.join(OUT, f"{r}.jpg")
    if os.path.exists(dst) and os.path.getsize(dst) > 2000:
        results.append((r, rank[r], "skip(exists)", ""))
        continue
    title = rank[r]
    if title in SKIP_TITLES:
        results.append((r, title, "SKIP(placeholder)", ""))
        continue
    if title in APPID_OVERRIDE:
        appid, sname = APPID_OVERRIDE[title], f"(override {APPID_OVERRIDE[title]})"
    else:
        term = QUERY_FIX.get(title, title)
        appid, sname = steam_appid(term)
    if not appid:
        results.append((r, title, "MISS(no steam)", ""))
        time.sleep(0.25)
        continue
    b, fn = try_download(appid)
    if b:
        open(dst, "wb").write(b)
        results.append((r, title, f"OK [{fn}]", f"steam:{sname}"))
    else:
        results.append((r, title, "MISS(no image)", f"steam:{sname}"))
    time.sleep(0.3)

ok = sum(1 for x in results if x[2].startswith("OK"))
sk = sum(1 for x in results if x[2].startswith("skip"))
print(f"=== 取得結果: OK {ok} / skip {sk} / MISS {100-ok-sk} ===")
for r, t, st, note in results:
    print(f"{r:>3} {st:<16} {t}  {note}")
