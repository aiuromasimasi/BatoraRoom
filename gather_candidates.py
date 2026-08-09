#!/usr/bin/env python3
"""未取得カバーの「候補ピッカー」を生成する。
各ゲームにつき複数の候補画像URLを公開APIから集める:
  - Steam ストア検索の上位3件（縦長カプセル / 無ければ header.jpg にフォールバック）
  - 日本語Wikipedia の代表画像
  - iTunes/App Store 検索の上位2件（モバイル移植のアートワーク）
出力:
  - candidates.json … {順位: [{label,url,fallback,source,note}, ...]}
  - covers_candidates.html … ブラウザで見て A/B/C を選ぶための一覧ページ
※ ここでは画像はダウンロードしない（候補ページはCDN直リンク、壊れURLはonerrorで自動非表示）。
   採用が決まったら fetch_picks.py で選んだURLだけ保存する。
使い方: python3 gather_candidates.py
"""
import json, os, re, time, html, urllib.parse, urllib.request

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 BatoraFanPage/1.0"
SGDB_KEY = os.environ.get("SGDB_KEY", "")

# SteamGridDB 検索用の英語エイリアス（日本語タイトルだと当たりにくいもの）
SGDB_ALIAS = {
    "ブレス オブ ザ ワイルド": "The Legend of Zelda Breath of the Wild",
    "ティアーズ オブ ザ キングダム": "The Legend of Zelda Tears of the Kingdom",
    "ゼルダの伝説 神々のトライフォース": "The Legend of Zelda A Link to the Past",
    "ゼルダの伝説 夢をみる島": "The Legend of Zelda Link's Awakening",
    "ゼルダの伝説（初代）": "The Legend of Zelda",
    "スーパーマリオ オデッセイ": "Super Mario Odyssey",
    "スーパーマリオワールド": "Super Mario World",
    "スーパーマリオブラザーズ2（ディスクシステム）": "Super Mario Bros. The Lost Levels",
    "星のカービィ ディスカバリー": "Kirby and the Forgotten Land",
    "ヨッシーストーリー": "Yoshi's Story",
    "カエルのために鐘は鳴る": "For the Frog the Bell Tolls",
    "悪魔城ドラキュラX 月下の夜想曲": "Castlevania Symphony of the Night",
    "レッドアリーマー（魔界村外伝）": "Gargoyle's Quest",
    "ロックマン2": "Mega Man 2",
    "バーチャファイター2": "Virtua Fighter 2",
    "鉄拳3": "Tekken 3",
    "レイディアント シルバーガン": "Radiant Silvergun",
    "グラディウスII": "Gradius II",
    "グラディウスIII": "Gradius III",
    "グラディウス外伝": "Gradius Gaiden",
    "怒首領蜂": "DoDonPachi",
    "スーパーストリートファイターII X": "Super Street Fighter II Turbo",
    "ストリートファイターIII 3rd STRIKE": "Street Fighter III 3rd Strike",
    "真・女神転生II": "Shin Megami Tensei II",
    "デビルサマナー": "Shin Megami Tensei Devil Summoner",
    "英雄伝説3 白き魔女": "The Legend of Heroes III",
    "魔界塔士Sa・Ga2 秘宝伝説": "Final Fantasy Legend II",
    "トルネコの大冒険 不思議のダンジョン": "Torneko no Daibouken",
    "ドラゴンクエスト4": "Dragon Quest IV",
    "ドラゴンクエスト10": "Dragon Quest X",
    "NiGHTS into dreams...": "NiGHTS into Dreams",
    "デイトナUSA": "Daytona USA",
    "セガラリー": "Sega Rally Championship",
    "コナミワイワイワールド": "Konami Wai Wai World",
    "DDR（Dance Dance Revolution）": "Dance Dance Revolution",
    "ウルティマオンライン": "Ultima Online",
    "WarCraft III": "Warcraft III Reign of Chaos",
    "弟切草": "Otogirisou",
    "街 〜運命の交差点〜": "Machi",
}

rank = {}
for l in open("game_ranking_draft.md", encoding="utf-8"):
    m = re.match(r'^(\d+)\.\s+(.*)$', l)
    if m:
        rank[int(m.group(1))] = m.group(2).strip()

# 既に取得済み(game_covers/N.jpg がある)順位は対象外
have = set()
for fn in os.listdir("game_covers") if os.path.isdir("game_covers") else []:
    m = re.match(r'^(\d+)\.jpg$', fn)
    if m and os.path.getsize(os.path.join("game_covers", fn)) > 2000:
        have.add(int(m.group(1)))
targets = [r for r in range(1, 101) if r not in have]

QUERY_FIX = {
    "ブレス オブ ザ ワイルド": "ゼルダの伝説 ブレス オブ ザ ワイルド",
    "ティアーズ オブ ザ キングダム": "ゼルダの伝説 ティアーズ オブ ザ キングダム",
    "ドラゴンクエスト5": "ドラゴンクエストV 天空の花嫁",
    "ドラゴンクエスト3": "ドラゴンクエストIII そして伝説へ",
    "ドラゴンクエスト4": "ドラゴンクエストIV 導かれし者たち",
    "ドラゴンクエスト10": "ドラゴンクエストX",
    "真・女神転生II": "真・女神転生II",
    "グラディウスII": "グラディウスII GOFERの野望",
    "スーパーマリオRPG": "スーパーマリオRPG",
    "悪魔城ドラキュラX 月下の夜想曲": "悪魔城ドラキュラX 月下の夜想曲",
    "スーパーマリオワールド": "スーパーマリオワールド",
    "スーパーマリオ オデッセイ": "スーパーマリオ オデッセイ",
    "星のカービィ ディスカバリー": "星のカービィ ディスカバリー",
    "フォートナイト": "Fortnite",
    "ウルティマオンライン": "Ultima Online",
    "WarCraft III": "Warcraft III Reforged",
    "ロックマン2": "ロックマン2 Dr.ワイリーの謎",
}

def http_json(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "ja,en"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))

def sgdb_candidates(title, n=4):
    """SteamGridDB から縦長カバー(600x900)を最大n枚。検索はエイリアス優先。"""
    if not SGDB_KEY:
        return []
    term = SGDB_ALIAS.get(title, title)
    hdr = {"Authorization": "Bearer " + SGDB_KEY, "User-Agent": UA}
    def jget(url):
        req = urllib.request.Request(url, headers=hdr)
        with urllib.request.urlopen(req, timeout=25) as r:
            return json.loads(r.read().decode("utf-8", "replace"))
    try:
        s = jget("https://www.steamgriddb.com/api/v2/search/autocomplete/" + urllib.parse.quote(term))
        games = s.get("data") or []
        if not games:
            return []
        gid = games[0].get("id")
        gname = games[0].get("name", "")
        g = jget(f"https://www.steamgriddb.com/api/v2/grids/game/{gid}"
                 f"?dimensions=600x900&types=static&nsfw=false&humor=false&limit=10")
        out = []
        for it in (g.get("data") or [])[:n]:
            u = it.get("url")
            if u:
                out.append({"url": u, "fallback": "", "source": "SteamGridDB", "note": gname})
        return out
    except Exception:
        return []

def steam_candidates(term, n=3):
    out = []
    try:
        url = "https://store.steampowered.com/api/storesearch/?" + urllib.parse.urlencode(
            {"term": term, "cc": "jp", "l": "japanese"})
        data = http_json(url)
        for it in (data.get("items") or [])[:n]:
            aid = it.get("id")
            if not aid:
                continue
            out.append({
                "url": f"https://cdn.cloudflare.steamstatic.com/steam/apps/{aid}/library_600x900_2x.jpg",
                "fallback": f"https://cdn.cloudflare.steamstatic.com/steam/apps/{aid}/header.jpg",
                "source": "Steam", "note": it.get("name", "")})
    except Exception:
        pass
    return out

def wiki_candidate(term):
    try:
        url = "https://ja.wikipedia.org/w/api.php?" + urllib.parse.urlencode({
            "action": "query", "generator": "search", "gsrsearch": term, "gsrlimit": 1,
            "prop": "pageimages", "piprop": "original", "format": "json", "redirects": 1})
        data = http_json(url)
        pages = (data.get("query") or {}).get("pages") or {}
        for p in pages.values():
            orig = (p.get("original") or {}).get("source")
            if orig and not orig.lower().endswith(".svg"):
                return [{"url": orig, "fallback": "", "source": "Wikipedia", "note": p.get("title", "")}]
    except Exception:
        pass
    return []

def itunes_candidates(term, n=2):
    out = []
    try:
        url = "https://itunes.apple.com/search?" + urllib.parse.urlencode(
            {"term": term, "entity": "software", "limit": n, "country": "jp"})
        data = http_json(url)
        for it in (data.get("results") or [])[:n]:
            art = it.get("artworkUrl512") or it.get("artworkUrl100", "")
            if art:
                art = art.replace("100x100", "512x512")
                out.append({"url": art, "fallback": "", "source": "App Store", "note": it.get("trackName", "")})
    except Exception:
        pass
    return out

cand = {}
for r in targets:
    title = rank[r]
    term = QUERY_FIX.get(title, title)
    items = sgdb_candidates(title, 4) + steam_candidates(term, 2) + wiki_candidate(term) + itunes_candidates(term, 1)
    # ラベル付与 A,B,C...
    for i, it in enumerate(items):
        it["label"] = chr(ord("A") + i)
    cand[r] = items
    print(f"{r:>3} {title}: {len(items)}候補")
    time.sleep(0.2)

json.dump(cand, open("candidates.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---- review HTML ----
def card(r):
    title = html.escape(rank[r])
    items = cand.get(r, [])
    cells = []
    for it in items:
        fb = html.escape(it.get("fallback", ""))
        onerr = (f"if(this.dataset.fb){{this.src=this.dataset.fb;this.dataset.fb='';}}else{{this.closest('.cand').style.display='none';}}")
        cells.append(
            f'<div class="cand"><div class="lab">{it["label"]}</div>'
            f'<img loading="lazy" src="{html.escape(it["url"])}" data-fb="{fb}" onerror="{onerr}">'
            f'<div class="src">{html.escape(it["source"])}<br><span>{html.escape(it["note"])[:40]}</span></div></div>')
    if not cells:
        cells.append('<div class="cand none">候補なし</div>')
    return (f'<section class="g"><h2><b>{r}位</b> {title}　'
            f'<small>→ 採用は「{r}:ラベル」、不要は「{r}:なし」で返答</small></h2>'
            f'<div class="row">{"".join(cells)}</div></section>')

body = "\n".join(card(r) for r in targets)
out_html = f'''<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>カバー候補ピッカー（未取得{len(targets)}本）</title>
<style>
 body{{font-family:"Hiragino Kaku Gothic ProN",sans-serif;background:#f4f1fb;color:#2a1a4a;margin:0;padding:20px}}
 h1{{font-size:20px}} .lead{{color:#6a4d8a;font-size:13px;line-height:1.7;margin-bottom:16px}}
 .g{{background:#fff;border-radius:14px;padding:12px 14px;margin:0 0 14px;box-shadow:0 4px 12px rgba(58,36,86,.08)}}
 .g h2{{font-size:15px;margin:0 0 10px}} .g h2 b{{color:#9b5cff}} .g h2 small{{color:#a18bbf;font-weight:400;font-size:11px}}
 .row{{display:flex;gap:12px;flex-wrap:wrap}}
 .cand{{width:130px;text-align:center;border:1px solid #eee;border-radius:10px;padding:6px;background:#fafafa}}
 .cand .lab{{font-weight:800;color:#fff;background:#9b5cff;border-radius:6px;display:inline-block;padding:1px 9px;margin-bottom:4px}}
 .cand img{{width:100%;height:160px;object-fit:contain;background:#fff;border-radius:6px}}
 .cand .src{{font-size:10px;color:#888;margin-top:4px;line-height:1.3}} .cand .src span{{color:#bbb}}
 .cand.none{{display:flex;align-items:center;justify-content:center;color:#bbb;height:180px;width:200px}}
</style></head><body>
<h1>🎮 カバー候補ピッカー（未取得 {len(targets)} 本）</h1>
<p class="lead">各ゲームの候補から正しいものを選んでね。返答例：<b>8:B, 24:A, 50:なし, 47:C</b> …（複数まとめてOK）<br>
ラベルは A/B/C…。Steam＝公式縦カプセル、Wikipedia＝代表画像、App Store＝モバイル版アート。正解が無ければ「なし」。</p>
{body}
</body></html>'''
open("covers_candidates.html", "w", encoding="utf-8").write(out_html)
print(f"\n対象 {len(targets)} 本 / covers_candidates.html と candidates.json を出力")
