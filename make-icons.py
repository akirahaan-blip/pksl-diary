# ============================================================
#  pksl日記 のアイコンを作るスクリプト
#  実行すると icon-180.png / icon-192.png / icon-512.png ができる。
#  （ピンクの角丸の四角に、白い月と日記のページ）
#  ふつうは動かす必要なし。アイコンを作り直したいときだけ使う。
# ============================================================
from PIL import Image, ImageDraw

def make(size):
    S = size * 4  # 大きく描いて最後に縮めるとフチがなめらかになる
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # 角丸の背景（テーマ色のピンク）
    d.rounded_rectangle([0, 0, S, S], radius=S * 0.22, fill=(196, 61, 116, 255))
    # 日記のページ（白い縦長の紙）
    px0, py0, px1, py1 = S * 0.24, S * 0.28, S * 0.76, S * 0.86
    d.rounded_rectangle([px0, py0, px1, py1], radius=S * 0.05, fill=(255, 245, 249, 255))
    # 紙の上の線（文字のつもり）
    for i in range(4):
        y = py0 + S * 0.16 + i * S * 0.11
        w = S * 0.36 if i < 3 else S * 0.22
        d.rounded_rectangle([px0 + S * 0.08, y, px0 + S * 0.08 + w, y + S * 0.035],
                            radius=S * 0.02, fill=(230, 160, 195, 255))
    # 月（白い丸から、ずらした背景色の丸を引いて三日月に）
    cx, cy, r = S * 0.70, S * 0.26, S * 0.15
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 250, 230, 255))
    d.ellipse([cx - r + S * 0.07, cy - r - S * 0.05, cx + r + S * 0.07, cy + r - S * 0.05],
              fill=(196, 61, 116, 255))
    return im.resize((size, size), Image.LANCZOS)

for s in (180, 192, 512):
    make(s).save(f"icon-{s}.png")
    print("wrote", f"icon-{s}.png")
