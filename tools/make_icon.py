"""Draws the app icon: a panda holding its breath (puffed cheeks, eyes squeezed shut).

    pip install pillow
    python tools/make_icon.py

Writes panda_breath_control/assets/icon.ico, icon-64.png and docs/logo.png.

Two drawings, because one drawing cannot serve every size:
- 16, 20, 24 and 32 px are drawn directly at their own size on the pixel grid,
  with no anti-aliasing and fewer details, so they stay sharp in the title bar
  and taskbar. Shrinking a large drawing makes them blurry.
- 40 px and up are drawn at 1024 px with every detail and scaled down.

Both have a thin white edge ("sticker" outline) so the black ears do not
disappear on a dark taskbar or GitHub's dark theme.
"""
import math
import os

from PIL import Image, ImageDraw

INK = (34, 34, 38, 255)
WHITE = (255, 255, 255, 255)
BLUSH = (255, 128, 150, 255)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


# ---------------------------------------------------------------------------
# Small sizes: pixel grid, no anti-aliasing
# ---------------------------------------------------------------------------
# Coordinates are pixel boxes (x0, y0, x1, y1), inclusive, per size.
SMALL = {
    16: {
        "ears": [(1, 1, 5, 5), (10, 1, 14, 5)],
        "head": [(2, 3, 13, 13), (1, 7, 7, 14), (8, 7, 14, 14)],
        "patches": [(4, 6, 6, 9), (9, 6, 11, 9)],
        "eyes": [],
        "nose": [(7, 10, 8, 10)],
        "mouth": [],
        "blush": [(2, 11, 3, 11), (12, 11, 13, 11)],
    },
    20: {
        "ears": [(1, 1, 6, 6), (13, 1, 18, 6)],
        "head": [(2, 3, 17, 16), (1, 9, 9, 18), (10, 9, 18, 18)],
        "patches": [(5, 7, 8, 11), (11, 7, 14, 11)],
        "eyes": [],
        "nose": [(9, 12, 10, 12)],
        "mouth": [(9, 14, 10, 14)],
        "blush": [(3, 13, 4, 14), (15, 13, 16, 14)],
    },
    24: {
        "ears": [(1, 1, 7, 7), (16, 1, 22, 7)],
        "head": [(2, 3, 21, 20), (1, 11, 11, 22), (12, 11, 22, 22)],
        "patches": [(5, 8, 9, 13), (14, 8, 18, 13)],
        "eyes": [[(6, 10), (7, 11), (6, 12)], [(17, 10), (16, 11), (17, 12)]],
        "nose": [(11, 14, 12, 15)],
        "mouth": [(10, 17, 13, 17)],
        "blush": [(3, 16, 5, 17), (18, 16, 20, 17)],
    },
    32: {
        "ears": [(1, 1, 10, 10), (21, 1, 30, 10)],
        "head": [(2, 4, 29, 27), (1, 14, 15, 30), (16, 14, 30, 30)],
        "patches": [(7, 10, 13, 17), (18, 10, 24, 17)],
        "eyes": [[(8, 12), (9, 13), (10, 14), (9, 15), (8, 16)],
                 [(23, 12), (22, 13), (21, 14), (22, 15), (23, 16)]],
        "nose": [(14, 19, 17, 20)],
        "mouth": [(13, 23, 14, 23), (15, 22, 16, 22), (17, 23, 18, 23)],
        "blush": [(3, 21, 7, 23), (24, 21, 28, 23)],
    },
}


def draw_small(n):
    """Sticker outline (white), ink outline, white face, features. No AA."""
    spec = SMALL[n]
    # Layers on a grid, composited by priority: keyline < outline < face < features.
    grid = {}

    def fill_ellipse(box, value, grow=0):
        x0, y0, x1, y1 = box
        x0, y0, x1, y1 = x0 - grow, y0 - grow, x1 + grow, y1 + grow
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        rx, ry = (x1 - x0 + 1) / 2, (y1 - y0 + 1) / 2
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if ((x + 0.5 - (cx + 0.5)) / rx) ** 2 + ((y + 0.5 - (cy + 0.5)) / ry) ** 2 <= 1.0:
                    if 0 <= x < n and 0 <= y < n:
                        grid[(x, y)] = value

    def fill_rect(box, value):
        x0, y0, x1, y1 = box
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                grid[(x, y)] = value

    # The shapes are given with their outline included; the white sticker edge
    # is added outside by growing the silhouette by one pixel.
    silhouette = spec["ears"] + spec["head"]
    for box in silhouette:
        fill_ellipse(box, "key", grow=1)
    for box in silhouette:
        fill_ellipse(box, "ink")
    for box in spec["head"]:
        fill_ellipse(box, "face", grow=-1)
    for box in spec["patches"]:
        fill_ellipse(box, "ink")
    for eye in spec["eyes"]:
        for p in eye:
            grid[p] = "face"
    for box in spec["nose"] + spec["mouth"]:
        fill_rect(box, "ink")
    for box in spec["blush"]:
        fill_rect(box, "blush")

    colors = {"key": WHITE, "ink": INK, "face": WHITE, "blush": BLUSH}
    img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    px = img.load()
    for (x, y), v in grid.items():
        if 0 <= x < n and 0 <= y < n:
            px[x, y] = colors[v]
    return img


# ---------------------------------------------------------------------------
# Large sizes: detailed drawing at 1024 px
# ---------------------------------------------------------------------------
S = 1024
OUTLINE = 26
KEYLINE = 30
BLUSH_SOFT = (255, 120, 140, 150)


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


def draw_large():
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    ears = ((232, 270, 140), (792, 270, 140))
    head = (512, 540, 370, 320)
    cheeks = ((292, 700, 205, 180), (732, 700, 205, 180))  # the held breath

    # white sticker edge around everything
    for cx, cy, r in ears:
        ellipse(d, cx, cy, r, r, WHITE, grow=KEYLINE)
    ellipse(d, *head, WHITE, grow=OUTLINE + KEYLINE)
    for c in cheeks:
        ellipse(d, *c, WHITE, grow=OUTLINE + KEYLINE)
    # ink: ears, then the face silhouette grown by OUTLINE
    for cx, cy, r in ears:
        ellipse(d, cx, cy, r, r, INK)
    ellipse(d, *head, INK, grow=OUTLINE)
    for c in cheeks:
        ellipse(d, *c, INK, grow=OUTLINE)
    ellipse(d, *head, WHITE)
    for c in cheeks:
        ellipse(d, *c, WHITE)

    blush = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    bd = ImageDraw.Draw(blush)
    ellipse(bd, 262, 735, 92, 58, BLUSH_SOFT)
    ellipse(bd, 762, 735, 92, 58, BLUSH_SOFT)
    img.alpha_composite(blush)
    d = ImageDraw.Draw(img)

    tilted_ellipse(d, 360, 500, 92, 128, 35, INK)
    tilted_ellipse(d, 664, 500, 92, 128, -35, INK)
    round_line(d, [(322, 452), (398, 500), (322, 548)], 30, WHITE)
    round_line(d, [(702, 452), (626, 500), (702, 548)], 30, WHITE)
    ellipse(d, 512, 618, 54, 36, INK)
    round_line(d, [(450, 712), (480, 700), (512, 712), (544, 700), (574, 712)], 22, INK)

    box = img.getbbox()
    side = max(box[2] - box[0], box[3] - box[1]) + 8
    cx, cy = (box[0] + box[2]) // 2, (box[1] + box[3]) // 2
    return img.crop((cx - side // 2, cy - side // 2, cx + side // 2, cy + side // 2))


def main():
    assets = os.path.join(ROOT, "panda_breath_control", "assets")
    docs = os.path.join(ROOT, "docs")
    os.makedirs(assets, exist_ok=True)
    os.makedirs(docs, exist_ok=True)
    large = draw_large()
    frames = {n: draw_small(n) for n in SMALL}
    for n in (40, 48, 64, 128, 256):
        frames[n] = large.resize((n, n), Image.LANCZOS)
    large.resize((512, 512), Image.LANCZOS).save(os.path.join(docs, "logo.png"))
    frames[64].save(os.path.join(assets, "icon-64.png"))
    sizes = sorted(frames)
    frames[256].save(os.path.join(assets, "icon.ico"), sizes=[(n, n) for n in sizes],
                     append_images=[frames[n] for n in sizes if n != 256])
    print("wrote icon.ico with sizes", sizes)


if __name__ == "__main__":
    main()
