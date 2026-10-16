"""Draws the app icon: a panda holding its breath (puffed cheeks, eyes squeezed shut).

    pip install pillow
    python tools/make_icon.py

Writes panda_breath_control/assets/icon.ico, icon-64.png and docs/logo.png.
Drawn at 1024 px and scaled down, so edit the coordinates below at that size.
"""
import math
import os

from PIL import Image, ImageDraw

S = 1024
INK = (34, 34, 38, 255)
WHITE = (255, 255, 255, 255)
BLUSH = (255, 120, 140, 150)
OUTLINE = 26

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def ellipse(d, cx, cy, rx, ry, fill, grow=0):
    d.ellipse((cx - rx - grow, cy - ry - grow, cx + rx + grow, cy + ry + grow), fill=fill)


def tilted_ellipse(d, cx, cy, rx, ry, angle_deg, fill):
    a = math.radians(angle_deg)
    pts = []
    for i in range(120):
        u = 2 * math.pi * i / 120
        x, y = rx * math.cos(u), ry * math.sin(u)
        pts.append((cx + x * math.cos(a) - y * math.sin(a), cy + x * math.sin(a) + y * math.cos(a)))
    d.polygon(pts, fill=fill)


def round_line(d, pts, width, fill):
    d.line(pts, fill=fill, width=width, joint="curve")
    r = width / 2
    for x, y in (pts[0], pts[-1]):
        d.ellipse((x - r, y - r, x + r, y + r), fill=fill)


def draw():
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    ears = ((232, 270, 140), (792, 270, 140))
    head = (512, 540, 370, 320)
    cheeks = ((292, 700, 205, 180), (732, 700, 205, 180))  # the held breath

    for cx, cy, r in ears:
        ellipse(d, cx, cy, r, r, INK)
    # outline: the face silhouette grown by OUTLINE, then the white face on top
    ellipse(d, *head, INK, grow=OUTLINE)
    for c in cheeks:
        ellipse(d, *c, INK, grow=OUTLINE)
    ellipse(d, *head, WHITE)
    for c in cheeks:
        ellipse(d, *c, WHITE)

    # blush from the effort
    blush = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    bd = ImageDraw.Draw(blush)
    ellipse(bd, 262, 735, 92, 58, BLUSH)
    ellipse(bd, 762, 735, 92, 58, BLUSH)
    img.alpha_composite(blush)
    d = ImageDraw.Draw(img)

    # eye patches, drooping outwards
    tilted_ellipse(d, 360, 500, 92, 128, 35, INK)
    tilted_ellipse(d, 664, 500, 92, 128, -35, INK)
    # eyes squeezed shut: > <
    round_line(d, [(322, 452), (398, 500), (322, 548)], 30, WHITE)
    round_line(d, [(702, 452), (626, 500), (702, 548)], 30, WHITE)

    # nose
    ellipse(d, 512, 618, 54, 36, INK)
    # lips pressed together, slightly wavy
    round_line(d, [(450, 712), (480, 700), (512, 712), (544, 700), (574, 712)], 22, INK)
    return img


def main():
    img = draw()
    assets = os.path.join(ROOT, "panda_breath_control", "assets")
    docs = os.path.join(ROOT, "docs")
    os.makedirs(assets, exist_ok=True)
    os.makedirs(docs, exist_ok=True)
    # crop to the drawing so small sizes use the whole square
    box = img.getbbox()
    side = max(box[2] - box[0], box[3] - box[1]) + 40
    cx, cy = (box[0] + box[2]) // 2, (box[1] + box[3]) // 2
    square = img.crop((cx - side // 2, cy - side // 2, cx + side // 2, cy + side // 2))
    square.resize((512, 512), Image.LANCZOS).save(os.path.join(docs, "logo.png"))
    square.resize((64, 64), Image.LANCZOS).save(os.path.join(assets, "icon-64.png"))
    square.resize((256, 256), Image.LANCZOS).save(
        os.path.join(assets, "icon.ico"), sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print("wrote", os.path.join(docs, "logo.png"))


if __name__ == "__main__":
    main()
