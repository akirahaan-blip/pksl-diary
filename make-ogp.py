# -*- coding: utf-8 -*-
"""
============================================================
 ポケスリダイアリー
 X や LINE に URL を貼ったときに出る「カード画像」（ogp.png 1200x630）を作るツール

 ふだんは使いません。文字や色を変えたくなったときだけ使います。

 使いかた：
   PowerShell でこのフォルダに移動して  python make-ogp.py
 できるもの：
   ogp.png が同じフォルダに保存されます

 ポケモンの公式の絵は一切使っていません。月・星・日記帳だけで描いています。
============================================================
"""

import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ---------- 設定：ここを書き換えれば見た目が変わります ----------
TITLE = "ポケスリダイアリー"
LEAD  = "ねむって、撮って、ひとこと。"
DESC1 = "ポケモンスリープの毎日を、スクショと一言で残す"
DESC2 = "自分だけの日記帳。絵日記にしてXにも。"
NOTE  = "非公式ファンツール"

W, H = 1200, 630
S = 2                      # 2倍の大きさで描いて最後に縮める（フチがなめらかになる）

# 色（アプリ本体の「暗い画面」と同じ系統）
PLUM_TOP    = (0x1E, 0x08, 0x16)   # 夜空の上のほう
PLUM_BOTTOM = (0x5A, 0x1C, 0x46)   # 夜空の下のほう（少し明るいプラム）
PINK        = (0xFF, 0x8E, 0xC4)   # 明るいピンク（タイトル）
PINK_DEEP   = (0xC4, 0x3D, 0x74)   # 濃いピンク（日記の表紙など）
CREAM       = (0xFF, 0xF5, 0xD6)   # 月の色
PAPER       = (0xFF, 0xF5, 0xF9)   # 日記のページ（桜白）
WHITE       = (0xFF, 0xFF, 0xFF)
MUTED       = (0xE8, 0xC6, 0xD8)   # うすい文字

FONT_HEAVY = "C:/Windows/Fonts/MPLUS1p-ExtraBold.ttf"   # 800
FONT_BOLD  = "C:/Windows/Fonts/MPLUS1p-Bold.ttf"        # 700
FALLBACKS  = ["C:/Windows/Fonts/YuGothB.ttc", "C:/Windows/Fonts/meiryob.ttc"]

here = os.path.dirname(os.path.abspath(__file__))


def font(path, size):
    for p in [path] + FALLBACKS:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# ---------- 夜空のグラデーション ----------
def sky():
    im = Image.new("RGB", (W * S, H * S), PLUM_TOP)
    d = ImageDraw.Draw(im)
    for y in range(H * S):
        t = y / (H * S)
        d.line([(0, y), (W * S, y)], fill=lerp(PLUM_TOP, PLUM_BOTTOM, t ** 1.4))
    # 右下にほんのりピンクの光
    glow = Image.new("RGB", im.size, (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([W * S * 0.55, H * S * 0.55, W * S * 1.25, H * S * 1.45], fill=(70, 20, 50))
    glow = glow.filter(ImageFilter.GaussianBlur(120 * S))
    im = Image.blend(im, Image.eval(glow, lambda v: v), 0.0)  # （形だけ。下で加算する）
    from PIL import ImageChops
    im = ImageChops.add(im, glow)
    return im


# ---------- 星 ----------
def stars(im):
    d = ImageDraw.Draw(im, "RGBA")
    rnd = random.Random(7)          # 毎回同じ配置になるように
    for _ in range(90):
        x = rnd.randint(0, W * S)
        y = rnd.randint(0, int(H * S * 0.8))
        r = rnd.choice([1, 1, 1, 2, 2, 3]) * S
        a = rnd.randint(90, 220)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 245, 230, a))
    # キラッとした4つ角の星をいくつか
    for (x, y, r) in [(150, 90, 16), (430, 60, 11), (620, 170, 13), (1080, 80, 15), (980, 300, 10), (300, 330, 9)]:
        x, y, r = x * S, y * S, r * S
        pts = []
        for i in range(8):
            ang = math.pi / 4 * i
            rr = r if i % 2 == 0 else r * 0.35
            pts.append((x + math.cos(ang) * rr, y + math.sin(ang) * rr))
        d.polygon(pts, fill=(255, 240, 210, 230))


# ---------- 三日月（光つき） ----------
def moon(im, cx, cy, r):
    # 光
    glow = Image.new("RGBA", im.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([cx - r * 1.4, cy - r * 1.4, cx + r * 1.4, cy + r * 1.4], fill=(255, 235, 180, 70))
    glow = glow.filter(ImageFilter.GaussianBlur(40 * S))
    im.alpha_composite(glow)
    # 月＝クリーム色の丸から、ずらした丸をくり抜く
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.ellipse([cx - r, cy - r, cx + r, cy + r], fill=CREAM + (255,))
    cut = Image.new("L", im.size, 0)
    ImageDraw.Draw(cut).ellipse([cx - r + r * 0.55, cy - r - r * 0.25, cx + r + r * 0.55, cy + r - r * 0.25], fill=255)
    alpha = layer.split()[3]
    from PIL import ImageChops
    alpha = ImageChops.subtract(alpha, cut)
    layer.putalpha(alpha)
    im.alpha_composite(layer)


# ---------- 開いた日記帳 ----------
def diary(im, cx, cy, w, h):
    d = ImageDraw.Draw(im, "RGBA")
    # 表紙（濃いピンク）：ページより少し大きい
    pad = 14 * S
    d.rounded_rectangle([cx - w / 2 - pad, cy - h / 2 - pad, cx + w / 2 + pad, cy + h / 2 + pad],
                        radius=22 * S, fill=PINK_DEEP + (255,))
    # 左右のページ
    gap = 4 * S
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx - gap, cy + h / 2], radius=10 * S, fill=PAPER + (255,))
    d.rounded_rectangle([cx + gap, cy - h / 2, cx + w / 2, cy + h / 2], radius=10 * S, fill=PAPER + (255,))
    # 真ん中のとじ目の影
    d.rectangle([cx - gap, cy - h / 2, cx + gap, cy + h / 2], fill=(150, 40, 90, 255))
    # 左ページ：絵（うすいピンクの四角＝スクショのつもり）
    m = 22 * S
    d.rounded_rectangle([cx - w / 2 + m, cy - h / 2 + m, cx - gap - m, cy + h * 0.12],
                        radius=8 * S, fill=(255, 214, 232, 255))
    # その中に小さな月
    mx, my, mr = cx - w / 4 - gap / 2, cy - h / 2 + m + (h * 0.62 - 2 * m) / 2, h * 0.11
    d.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(255, 236, 180, 255))
    d.ellipse([mx - mr + mr * 0.5, my - mr - mr * 0.25, mx + mr + mr * 0.5, my + mr - mr * 0.25], fill=(255, 214, 232, 255))
    # 左ページ：絵の下の横書きの線
    y = cy + h * 0.12 + 20 * S
    for i in range(3):
        ww = (w / 2 - 2 * m - gap) * (1.0 if i < 2 else 0.55)
        d.rounded_rectangle([cx - w / 2 + m, y, cx - w / 2 + m + ww, y + 7 * S], radius=3 * S, fill=(235, 160, 200, 255))
        y += 22 * S
    # 右ページ：縦書きの線（原稿用紙ふう）
    x = cx + w / 2 - m - 6 * S
    for i in range(6):
        hh = h - 2 * m
        if i in (1, 4):
            hh *= 0.6
        d.rounded_rectangle([x - 7 * S, cy - h / 2 + m, x, cy - h / 2 + m + hh], radius=3 * S,
                            fill=(235, 160, 200, 255) if i < 2 else (250, 215, 232, 255))
        x -= 26 * S


# ---------- Zzz ----------
def zzz(im, x, y):
    d = ImageDraw.Draw(im, "RGBA")
    for i, size in enumerate([34, 46, 60]):
        f = font(FONT_HEAVY, size * S)
        d.text((x + i * 42 * S, y - i * 48 * S), "z" if i < 2 else "Z", font=f, fill=PINK + (235,))


# ---------- 本体 ----------
def make():
    base = sky().convert("RGBA")
    stars(base)

    # 左側：月と日記帳
    moon(base, 265 * S, 215 * S, 118 * S)
    diary(base, 300 * S, 450 * S, 300 * S, 190 * S)
    zzz(base, 360 * S, 245 * S)

    # 右側：文字
    d = ImageDraw.Draw(base)
    x0 = 535 * S
    d.text((x0, 152 * S), TITLE, font=font(FONT_HEAVY, 76 * S), fill=PINK)
    d.text((x0 + 4 * S, 262 * S), LEAD, font=font(FONT_HEAVY, 40 * S), fill=WHITE)
    d.text((x0 + 4 * S, 352 * S), DESC1, font=font(FONT_BOLD, 27 * S), fill=MUTED)
    d.text((x0 + 4 * S, 392 * S), DESC2, font=font(FONT_BOLD, 27 * S), fill=MUTED)
    # 下の小さな注意書き
    d.text((x0 + 4 * S, 545 * S), NOTE, font=font(FONT_BOLD, 22 * S), fill=(200, 150, 180))

    out = base.convert("RGB").resize((W, H), Image.LANCZOS)
    out.save(os.path.join(here, "ogp.png"), optimize=True)
    print("wrote ogp.png", out.size)


if __name__ == "__main__":
    make()
