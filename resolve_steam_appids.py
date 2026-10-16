#!/usr/bin/env python3
"""残りのSteam産cidについて appid を解決し game_trailers/index.json に {appid, game} のみ記録。
fetch_clip_meta.py はここから appid を読み、appdetailsを都度取得してHLS切り出しするので
movies配列の事前ダウンロードは不要（clips_review.html用のフル視聴だけは別途fetch_steam_trailers.pyで補う）。
"""
import json, os, re, urllib.parse, urllib.request, ssl, time

os.chdir(os.path.dirname(os.path.abspath(__file__)))
UA = {"User-Agent": "Mozilla/5.0"}
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE

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

def getj(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30, context=CTX) as r:
        return json.load(r)

index = json.load(open("game_trailers/index.json", encoding="utf-8")) if os.path.exists("game_trailers/index.json") else {}

MISSING = [10,11,13,23,24,25,26,27,30,33,34,37,39,40,42,44,46,49,50,52,60,61,62,64,67,70,71,73,78,82,84,88,91,92,93,94,95,97,98,113,117]

ok, ng = [], []
for cid in MISSING:
    if str(cid) in index:
        print(f"c{cid}: SKIP(済)"); continue
    title = cid2title.get(cid, "?")
    try:
        if cid in APPID_FIX:
            appid = APPID_FIX[cid]
        else:
            q = QUERY_FIX.get(title, title)
            d = getj("https://store.steampowered.com/api/storesearch/?term=" + urllib.parse.quote(q) + "&cc=jp&l=japanese")
            items = d.get("items", [])
            if not items:
                print(f"c{cid} {title[:24]}: NO-MATCH"); ng.append(cid); continue
            appid = items[0]["id"]
        ad = getj(f"https://store.steampowered.com/api/appdetails?appids={appid}&cc=jp&l=japanese")
        data = (ad.get(str(appid)) or {}).get("data") or {}
        movies = data.get("movies") or []
        if not movies:
            print(f"c{cid} {title[:24]}: NO-MOVIE(appid={appid})"); ng.append(cid); continue
        index[str(cid)] = {"appid": appid, "game": data.get("name", title), "movies": []}
        json.dump(index, open("game_trailers/index.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"c{cid} {title[:24]} -> {data.get('name','')[:30]} (appid={appid}) OK")
        ok.append(cid)
    except Exception as e:
        print(f"c{cid} {title[:24]}: ERR {type(e).__name__}"); ng.append(cid)
    time.sleep(.15)

print(f"\n=== OK:{len(ok)} NG:{len(ng)} ===")
if ng: print("未解決:", ng)
