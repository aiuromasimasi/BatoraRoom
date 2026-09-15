#!/usr/bin/env python3
# coding: utf-8
"""アイラのコマンドガイド（チャットに投稿するヘルプ画像）を生成する。

  使い方:  uv run --with pillow python help/make_help_images.py

出力（このスクリプトと同じ help/ フォルダ）:
  help_01_voice.png … vol.1 声・見た目        （Botの /v が投稿）
  help_05_info.png  … vol.2 話題・情報・ヘルプ（general.gif の2枚目）
  help_02_play.png  … vol.3 みんなで遊ぶ      （Botの /asobi が投稿）
  help_03_adv.gif   … vol.4 上級者コマンド 2枚（Botの /asobi で上級者にだけ追加投稿）
  help_general.gif  … vol.1〜3 の3枚GIF       （Botの /h が投稿）

コマンドの中身は GravityDocument の agora_rtm_poc_v2.html（FUN_TIERS と
handleVoiceCommand）／チャットコマンド一覧.md が正。コマンドを増減したら
このスクリプトの PAGES を直して再生成し、command.htm も一緒に更新すること。
※ help_04_change.png（/ch の番号表）だけは実際のアイコン/フレーム画像なので
　 ここでは作らない（frame_number_table.html をスクショして置き換える）。
"""
import os
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.dirname(os.path.abspath(__file__))
W = H = 1024

# ── 配色（既存のヘルプ画像から採取した値をそのまま使う）──
C_HEADER = (44, 28, 68)        # ヘッダー帯
C_BG = (250, 255, 252)         # 本文の地
C_STRIPE = (238, 232, 252)     # 1行おきの薄紫
C_CMD = (107, 46, 210)         # コマンド名（紫）
C_DESC = (58, 36, 86)          # 説明文
C_TITLE = (255, 255, 255)
C_SUB = (198, 180, 240)        # ヘッダーの小見出し
C_FOOT = (176, 164, 200)       # フッター
C_ADV = (226, 108, 30)         # ⭐上級者マーク

# ── フォント（macOS 標準／追加インストール不要）──
F_JP_B = "/System/Library/AssetsV2/com_apple_MobileAsset_Font8/b7a6a6575a699e801915b73b9e1e75c74a3404ce.asset/AssetData/YuGothic-Bold.otf"
F_JP_M = "/System/Library/AssetsV2/com_apple_MobileAsset_Font8/ee89e7987a76cc8cfdff36c96bd7bc77655b343e.asset/AssetData/YuGothic-Medium.otf"
F_FALLBACK_B = "/System/Library/Fonts/Hiragino Sans GB.ttc"   # 見つからない環境用


def font(path, size, index=0, bold=False):
    try:
        return ImageFont.truetype(path, size, index=index)
    except Exception:
        return ImageFont.truetype(F_FALLBACK_B, size, index=2 if bold else 0)


def jp_bold(size):
    return font(F_JP_B, size, bold=True)


def jp_med(size):
    return font(F_JP_M, size)


# ── 掲載内容 ──────────────────────────────────────────────
# ページ = {title, subtitle, page(フッターの N/4), blocks:[(見出し, 帯色, [(コマンド, 説明, 上級者か)])]}
ADV = True

PAGE_VOICE = {
    "vol": "vol.1",
    "sub": "声をかえる ／ 見た目をかえる",
    "page": 1,
    "blocks": [
        ("声コマンド", (214, 51, 132), [
            ("/vc [声ID] [速度]", "読み上げ声を変える（ID:0〜126・速度0.5〜2.0）", False),
            ("/vs [速度]", "速度だけ変更（0.5〜2.0　標準=1.0）", False),
            ("/vr", "声の設定をおまかせに戻す", False),
            ("/vq", "自分の発言の読み上げ ON ↔ OFF", False),
            ("/v", "声コマンドの早見表（この画像）を投稿", False),
            ("/omoide", "前回・前々回に話した話題を思い出す", False),
        ]),
        ("見た目コマンド（登壇中だけ）", (56, 110, 230), [
            ("/ch", "アイコン・フレームの番号表を投稿（誰でも）", False),
            ("/ci [番号]", "自分のアイコンを番号表のものに変える", ADV),
            ("/cf [番号]", "自分のフレームを番号表のものに変える", ADV),
            ("/reset", "変えた見た目を元に戻す", ADV),
        ]),
    ],
}

PAGE_INFO = {
    "vol": "vol.2",
    "sub": "話題・情報 ／ ヘルプ",
    "page": 2,
    "blocks": [
        ("話題・情報コマンド", (10, 160, 100), [
            ("/time", "日時 ＋ 明日の天気を5地域まとめて投稿", False),
            ("/log", "最近チャットに出た話題を2件ピックアップ", False),
            ("/wadai", "直近1週間の話題ランキングを投稿", False),
            ("/wadai1  /wadai2", "直近1ヶ月 ／ 直近半年のランキング", False),
            ("/neta", "話題提案を3種類投稿する（旧 /wadai）", False),
            ("/2ch", "ランダムAA（顔文字アスキーアート）", False),
            ("/zelda", "謎解き効果音を鳴らす（3種ランダム）", False),
        ]),
        ("ヘルプコマンド", (120, 60, 220), [
            ("/h", "コマンド一覧（この画像）をチャットへ投稿", False),
            ("/asobi", "遊び・進行コマンドの一覧を投稿", False),
            ("/admin:h", "管理者コマンドの説明を投稿（誰でも見られる）", False),
        ]),
    ],
}

PAGE_PLAY = {
    "vol": "vol.3",
    "sub": "みんなで遊ぼう！　全員が使えるコマンド",
    "page": 3,
    "blocks": [
        ("遊び・進行コマンド", (10, 160, 100), [
            ("/omikuji  /o", "今日の運勢（同日は同じ結果になる）", False),
            ("/gacha  /g", "称号ガチャ（N/R/SR/SSR・永続保存）", False),
            ("/rank  /lv", "来場ランク・称号・次のランクまで表示", False),
            ("/poll お題|A|B", "チャット多数決（/poll end で集計）", False),
            ("/kazuate [最大]", "数当てゲーム（上下ヒント付き / /kz）", False),
            ("/react on|off", "888/www など自動反応のON/OFF", False),
            ("/cd [分] [名前]", "カウントダウン＋残り1分・0分で告知", False),
            ("/brb [分]  /back", "離席告知（時刻指定）/ 復帰は /back", False),
        ]),
        ("推理ゲームに参加する", (214, 51, 132), [
            ("？ をつけて発言", "みんなで推理に質問する（/s でも可）", False),
            ("/kotae [名前]", "推理の答えを言う（/k でも可）", False),
        ]),
    ],
}

PAGE_ADV1 = {
    "vol": "vol.4",
    "sub": "上級者コマンド [1/2ページ] 権限が必要",
    "page": 4,
    "blocks": [
        ("上級者コマンド（管理者が権限付与）", (120, 60, 220), [
            ("/story", "今日のあらすじをAIが物語風に要約", False),
            ("/scene op|ed", "シーン一括発動（あいさつ＋効果音＋話題）", False),
            ("/ogiri [お題]", "大喜利（回答収集 → /ogiri end で発表）", False),
            ("/quiz [答] [問]", "早押しクイズ（最速正解で勝者を発表）", False),
            ("/shiritori [語]", "しりとり（「ん」で終わると負け）", False),
            ("/raid [HP]", "レイドボス（コメント1件＝1ダメージ）", False),
            ("/aino [絵文字]", "合いの手（絵文字を3連投の演出）", False),
            ("/ng add|del|list", "NGワード設定（検知で自動注意）", False),
            ("/q on|off|clear", "質問キュー（？ で終わる発言を収集）", False),
        ]),
    ],
}

PAGE_ADV2 = {
    "vol": "vol.4",
    "sub": "上級者コマンド [2/2ページ] 権限が必要",
    "page": 4,
    "blocks": [
        ("上級者コマンド（管理者が権限付与）", (120, 60, 220), [
            ("/aishou A B", "相性診断（ハッシュで0〜100%・毎回固定）", False),
            ("/goal [額]|reset", "目標メーター（ギフト累計の達成バー）", False),
            ("/giftrank", "ギフト投げ銭ランキング上位5を表示", False),
            ("/corner [名]", "コーナー切替（宣言＋効果音）", False),
            ("/pin [文章]|off", "概要・ルールを10分ごとに自動再掲", False),
            ("/mizu [分]|off", "水分・休憩リマインド（既定30分）", False),
            ("/word", "頻出ワードTOP8（2回以上の語を表示）", False),
            ("/suiri [ジャンル]", "みんなで推理（質問と回答は全員できる）", False),
            ("/music [テーマ]", "その場で1曲つくる（数分〜10分かかる）", False),
            ("/image [内容]", "画像生成AIに描いてもらって自動投稿", False),
        ]),
    ],
}

TOTAL_PAGES = 4


# ── 描画 ──────────────────────────────────────────────────
def draw_page(page):
    im = Image.new("RGB", (W, H), C_BG)
    d = ImageDraw.Draw(im)

    # ヘッダー
    d.rectangle([0, 0, W, 92], fill=C_HEADER)
    f_title = jp_bold(44)
    title = f"アイラのコマンドガイド　{page['vol']}"
    tw = d.textlength(title, font=f_title)
    d.text(((W - tw) / 2, 12), title, font=f_title, fill=C_TITLE)
    f_sub = jp_med(21)
    sw = d.textlength(page["sub"], font=f_sub)
    d.text(((W - sw) / 2, 62), page["sub"], font=f_sub, fill=C_SUB)

    y = 102
    f_sec = jp_bold(27)
    f_cmd = jp_bold(34)
    f_desc = jp_med(24)
    f_adv = jp_bold(20)
    stripe = 0
    for bi, (sec_title, sec_color, rows) in enumerate(page["blocks"]):
        if bi:
            y += 14
        d.rectangle([20, y + 3, 26, y + 33], fill=sec_color)
        d.text((36, y), sec_title, font=f_sec, fill=sec_color)
        y += 46
        for cmd, desc, adv in rows:
            if stripe % 2 == 1:
                d.rectangle([20, y, W - 20, y + 69], fill=C_STRIPE)
            d.text((40, y + 16), cmd, font=f_cmd, fill=C_CMD)
            d.text((375, y + 22), desc, font=f_desc, fill=C_DESC)
            if adv:
                d.text((W - 96, y + 26), "★上級", font=f_adv, fill=C_ADV)
            y += 70
            stripe += 1
        y += 6

    # フッター
    f_foot = jp_med(19)
    d.text((22, H - 32), "アイラ コマンドガイド", font=f_foot, fill=C_FOOT)
    pg = f"{page['page']} / {TOTAL_PAGES}"
    d.text((W - 22 - d.textlength(pg, font=f_foot), H - 32), pg, font=f_foot, fill=C_FOOT)
    return im


def main():
    voice = draw_page(PAGE_VOICE)
    info = draw_page(PAGE_INFO)
    play = draw_page(PAGE_PLAY)
    adv1 = draw_page(PAGE_ADV1)
    adv2 = draw_page(PAGE_ADV2)

    voice.save(os.path.join(OUT, "help_01_voice.png"))
    info.save(os.path.join(OUT, "help_05_info.png"))
    play.save(os.path.join(OUT, "help_02_play.png"))
    adv1.save(os.path.join(OUT, "help_03_adv.gif"), save_all=True,
              append_images=[adv2], duration=4000, loop=0)
    voice.save(os.path.join(OUT, "help_general.gif"), save_all=True,
               append_images=[info, play], duration=4000, loop=0)
    for f in ("help_01_voice.png", "help_05_info.png", "help_02_play.png",
              "help_03_adv.gif", "help_general.gif"):
        p = os.path.join(OUT, f)
        print(f"{f}\t{os.path.getsize(p)//1024} KB")


if __name__ == "__main__":
    main()
