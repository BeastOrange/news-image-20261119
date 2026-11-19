#!/usr/bin/env python3
"""Draw the 19 November 2026 world-news front page (1024x1024 PNG).

Deterministic: fixed text, fixed palette, seeded star field, no timestamps.
Requires Pillow only for the build; main.py (the graded entrypoint) is
stdlib-only and just copies the finished image to /output/entry.png.

News sources cross-checked for 19 Nov 2026: Reuters, BBC, AP, FT,
The Hindu, Jagran Josh, Newsmriti, SimpleLife.news.
"""
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
OUT = HERE / "entry.png"

W = H = 1024
PAPER = (248, 244, 233)
INK = (20, 20, 20)
GREY = (90, 86, 76)
RED = (185, 28, 28)
RULE = (60, 56, 48)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width):
    """Greedy word wrap; returns list of lines that fit in width."""
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=fnt) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, lines, x, y, fnt, fill, spacing=4):
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += fnt.size + spacing
    return y


def draw_vice_city_scene(draw, box):
    """Neon sunset over a Vice City-style coastal skyline: gradient sky,
    low sun, tower silhouettes, palm trees, water with reflections."""
    x0, y0, x1, y1 = box
    pw, ph = x1 - x0, y1 - y0
    # sunset gradient sky, top purple to orange horizon
    top = (46, 16, 78)
    mid = (168, 52, 110)
    bot = (255, 140, 66)
    horizon = y0 + int(ph * 0.62)
    for yy in range(y0, horizon):
        t = (yy - y0) / max(1, horizon - y0)
        if t < 0.55:
            s = t / 0.55
            col = tuple(int(top[i] + (mid[i] - top[i]) * s) for i in range(3))
        else:
            s = (t - 0.55) / 0.45
            col = tuple(int(mid[i] + (bot[i] - mid[i]) * s) for i in range(3))
        draw.line([(x0, yy), (x1, yy)], fill=col)
    # sun: big disc half-sunk at the horizon
    sx, sy, sr = (x0 + x1) // 2 + 60, horizon - 56, 46
    draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(255, 214, 120))
    draw.ellipse([sx - sr + 8, sy - sr + 8, sx + sr - 8, sy + sr - 8],
                 fill=(255, 236, 170))
    # stars in the upper sky
    rnd = random.Random(19)
    for _ in range(40):
        x = rnd.randint(x0 + 4, x1 - 4)
        y = rnd.randint(y0 + 4, y0 + 90)
        r = rnd.choice([1, 1, 2])
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(230, 220, 245))
    # skyline: back layer (dark purple) and front layer (near black)
    back = [(0, 96, 30, 150), (34, 70, 66, 150), (70, 110, 96, 150),
            (100, 60, 132, 150), (136, 96, 168, 150), (172, 78, 206, 150),
            (210, 118, 240, 150), (244, 84, 272, 150), (276, 104, 306, 150),
            (310, 64, 344, 150), (348, 100, 380, 150), (384, 74, 416, 150),
            (420, 112, 452, 150)]
    for bx0, bh, bx1, _ in back:
        draw.rectangle([x0 + bx0, horizon - bh, x0 + bx1, horizon],
                       fill=(58, 26, 74))
    front = [(0, 58, 44, 150), (48, 88, 84, 150), (88, 46, 118, 150),
             (122, 76, 158, 150), (162, 52, 196, 150), (200, 92, 238, 150),
             (242, 60, 276, 150), (280, 84, 316, 150), (320, 48, 352, 150),
             (356, 78, 392, 150), (396, 56, 428, 150), (432, 86, 468, 150)]
    for bx0, bh, bx1, _ in front:
        draw.rectangle([x0 + bx0, horizon - bh, x0 + bx1, horizon],
                       fill=(24, 10, 34))
    # lit windows, seeded
    rnd = random.Random(1911)
    for bx0, bh, bx1, _ in front:
        for _ in range(9):
            wx = rnd.randint(x0 + bx0 + 4, x0 + bx1 - 8)
            wy = rnd.randint(horizon - bh + 6, horizon - 10)
            wc = rnd.choice([(255, 200, 90), (120, 220, 255), (255, 120, 180)])
            draw.rectangle([wx, wy, wx + 4, wy + 5], fill=wc)
    # palm trees on the left and right edges
    for px, py, s in ((x0 + 26, horizon - 6, 1.0), (x1 - 30, horizon - 4, 0.85)):
        draw.line([(px, py), (px + int(6 * s), py - int(52 * s))],
                  fill=(16, 8, 24), width=5)
        for ang in (-70, -35, 0, 35, 70):
            a = math.radians(ang - 90)
            ex = px + int(6 * s) + int(30 * s * math.cos(a))
            ey = py - int(52 * s) + int(30 * s * math.sin(a)) + 14
            draw.line([(px + int(6 * s), py - int(52 * s)), (ex, ey)],
                      fill=(16, 8, 24), width=4)
    # water
    draw.rectangle([x0, horizon, x1, y1], fill=(14, 18, 44))
    for yy in range(horizon + 8, y1 - 6, 12):
        draw.line([(x0 + 12, yy), (x1 - 12, yy)], fill=(28, 40, 76))
    # sun reflection streaks
    for i, ww in enumerate((110, 78, 48)):
        draw.line([(sx - ww // 2, horizon + 10 + i * 12),
                   (sx + ww // 2, horizon + 10 + i * 12)],
                  fill=(255, 170, 80), width=3)
    # caption
    draw.text((x0 + 12, y1 - 26), "ILLUSTRATION: VICE CITY AT SUNSET",
              font=font(SANS_B, 13), fill=(210, 214, 220))


def icon_globe(draw, box, col):
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    r = min(x1 - x0, y1 - y0) // 2 - 2
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=3)
    draw.ellipse([cx - r // 2, cy - r, cx + r // 2, cy + r], outline=col, width=2)
    draw.line([(cx - r, cy), (cx + r, cy)], fill=col, width=2)


def icon_waves(draw, box, col):
    x0, y0, x1, y1 = box
    for yy in (y0 + 10, y0 + 22, y0 + 34):
        draw.arc([x0, yy, x1, yy + 16], 180, 360, fill=col, width=3)


def icon_arrows(draw, box, col):
    x0, y0, x1, y1 = box
    draw.line([(x0 + 4, y0 + 12), (x1 - 10, y0 + 12)], fill=col, width=3)
    draw.polygon([(x1 - 10, y0 + 6), (x1 - 2, y0 + 12), (x1 - 10, y0 + 18)], fill=col)
    draw.line([(x1 - 4, y1 - 12), (x0 + 10, y1 - 12)], fill=col, width=3)
    draw.polygon([(x0 + 10, y1 - 18), (x0 + 2, y1 - 12), (x0 + 10, y1 - 6)], fill=col)


def icon_ban(draw, box, col):
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    r = min(x1 - x0, y1 - y0) // 2 - 2
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=3)
    draw.line([(cx - r * 0.7, cy + r * 0.7), (cx + r * 0.7, cy - r * 0.7)],
              fill=col, width=3)


def icon_cyclone(draw, box, col):
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    for r in (18, 12, 6):
        draw.arc([cx - r, cy - r, cx + r, cy + r], 30, 300, fill=col, width=3)


def icon_capitol(draw, box, col):
    x0, y0, x1, y1 = box
    cx = (x0 + x1) // 2
    draw.polygon([(cx - 16, y0 + 8), (cx + 16, y0 + 8), (cx, y0 - 2)], fill=col)
    draw.rectangle([cx - 3, y0 + 4, cx + 3, y0 + 12], fill=col)
    draw.rectangle([x0 + 6, y0 + 14, x1 - 6, y0 + 20], fill=col)
    for i in range(4):
        bx = x0 + 8 + i * 10
        draw.rectangle([bx, y0 + 22, bx + 5, y1 - 8], fill=col)
    draw.rectangle([x0 + 4, y1 - 8, x1 - 4, y1 - 4], fill=col)


def icon_rocket(draw, box, col):
    x0, y0, x1, y1 = box
    cx = (x0 + x1) // 2
    draw.polygon([(cx, y0 + 2), (cx + 9, y0 + 20), (cx - 9, y0 + 20)], fill=col)
    draw.rectangle([cx - 9, y0 + 20, cx + 9, y1 - 14], fill=col)
    draw.polygon([(cx - 9, y1 - 14), (cx - 16, y1 - 4), (cx - 9, y1 - 8)], fill=col)
    draw.polygon([(cx + 9, y1 - 14), (cx + 16, y1 - 4), (cx + 9, y1 - 8)], fill=col)
    draw.polygon([(cx - 4, y1 - 12), (cx + 4, y1 - 12), (cx, y1 - 2)], fill=col)


ICONS = {
    "globe": icon_globe,
    "waves": icon_waves,
    "arrows": icon_arrows,
    "ban": icon_ban,
    "cyclone": icon_cyclone,
    "capitol": icon_capitol,
    "rocket": icon_rocket,
}

STORIES = [
    ("US POLITICS", (21, 80, 160), "capitol",
     "JEFFRIES SET TO BE FIRST BLACK SPEAKER",
     "Democrats nominate Hakeem Jeffries to lead the House."),
    ("UKRAINE", (158, 116, 8), "arrows",
     "EU PROPOSES \u20ac45BN LOAN FOR UKRAINE",
     "Brussels offers a 2027 loan, to be repaid from Russian reparations."),
    ("THE GULF", (14, 116, 144), "waves",
     "US AND IRAN TRADE FIRE AGAIN",
     "US hits a missile site on Qeshm Island; Iran strikes a US radar in Bahrain and a base in Kuwait."),
    ("WEATHER", (29, 78, 216), "cyclone",
     "CYCLONE AKVAN BEARS DOWN",
     "The Bay of Bengal storm heads for India's east coast."),
    ("SPACE", (109, 40, 217), "rocket",
     "VOYAGER 1 REACHES ONE LIGHT-DAY",
     "Nearly 50 years after launch, NASA's probe hits the milestone."),
    ("EUROPE", (190, 18, 60), "globe",
     "COALITION OF THE WILLING MEETS IN BERLIN",
     "Leaders gather on Ukraine support and security guarantees."),
]


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 30  # margin
    # outer hairline
    d.rectangle([M - 8, M - 8, W - M + 8, H - M + 8], outline=RULE, width=2)

    # ---- masthead ----
    title_f = font(SERIF_B, 78)
    title = "THE WORLD TODAY"
    tw = d.textlength(title, font=title_f)
    d.text(((W - tw) / 2, 30), title, font=title_f, fill=INK)
    y = 30 + 78 + 10
    d.line([(M, y), (W - M, y)], fill=INK, width=3)
    d.line([(M, y + 6), (W - M, y + 6)], fill=INK, width=1)
    y += 16
    date_f = font(SANS_B, 27)
    date = "THURSDAY, 19 NOVEMBER 2026"
    dw = d.textlength(date, font=date_f)
    d.text(((W - dw) / 2, y), date, font=date_f, fill=RED)
    y += 27 + 10
    tag_f = font(SANS, 16)
    tag = "ONE DAY  ·  ONE IMAGE  —  THE WORLD IN A SINGLE FRAME"
    tw2 = d.textlength(tag, font=tag_f)
    d.text(((W - tw2) / 2, y), tag, font=tag_f, fill=GREY)
    y += 16 + 14

    # ---- lead story ----
    lead_top, lead_h = y, 282
    d.rectangle([M, lead_top, W - M, lead_top + lead_h], outline=INK, width=2)
    pic = (M + 2, lead_top + 2, M + 482, lead_top + lead_h - 2)
    draw_vice_city_scene(d, pic)
    tx = M + 482 + 26
    tw_ = W - M - 26 - tx
    yy = lead_top + 24
    d.text((tx, yy), "CULTURE", font=font(SANS_B, 17), fill=RED)
    yy += 17 + 12
    head_f = font(SANS_B, 37)
    lines = wrap(d, "GTA VI IS HERE AT LAST", head_f, tw_)
    yy = draw_lines(d, lines, tx, yy, head_f, INK, spacing=6)
    yy += 10
    d.line([(tx, yy), (tx + 64, yy)], fill=RED, width=4)
    yy += 18
    deck_f = font(SANS, 18)
    deck = ("After a 13-year wait, Rockstar's blockbuster rolls out worldwide "
            "from New Zealand — Metacritic 99, preorders past $1.5 billion.")
    draw_lines(d, wrap(d, deck, deck_f, tw_), tx, yy, deck_f, (52, 50, 44), spacing=6)
    yy = lead_top + lead_h + 16

    # ---- grid of six stories ----
    cols, rows = 3, 2
    gap = 15
    cell_w = (W - 2 * M - (cols - 1) * gap) // cols
    cell_h = 184
    grid_top = yy
    for i, (kicker, col, icon, headline, deck) in enumerate(STORIES):
        r, c = divmod(i, cols)
        x = M + c * (cell_w + gap)
        y0 = grid_top + r * (cell_h + gap)
        d.rectangle([x, y0, x + cell_w, y0 + cell_h], outline=(150, 144, 128), width=1)
        d.rectangle([x, y0, x + cell_w, y0 + 5], fill=col)
        ix = x + cell_w - 52
        ICONS[icon](d, (ix, y0 + 16, ix + 44, y0 + 60), col)
        cx = x + 16
        cy = y0 + 16
        d.text((cx, cy), kicker, font=font(SANS_B, 14), fill=col)
        cy += 14 + 8
        hf = font(SANS_B, 20)
        lines = wrap(d, headline, hf, cell_w - 32 - 52)
        cy = draw_lines(d, lines, cx, cy, hf, INK, spacing=3)
        cy += 6
        df = font(SANS, 15)
        draw_lines(d, wrap(d, deck, df, cell_w - 32), cx, cy, df, (52, 50, 44), spacing=4)

    # ---- footer ----
    fy = grid_top + rows * cell_h + (rows - 1) * gap + 16
    d.line([(M, fy), (W - M, fy)], fill=INK, width=2)
    fy += 12
    tick_f = font(SANS_B, 15)
    tick = ("ALSO TODAY:   Nvidia chief Jensen Huang resigns; Colette Kress takes over  ·  "
            "Fed minutes point to more rate rises  ·  Modi meets the Prince and Princess of Wales  ·  "
            "Russian military plane crashes in Siberia, all 19 aboard killed  ·  "
            "Australia sanctions Israeli settlers")
    fy = draw_lines(d, wrap(d, tick, tick_f, W - 2 * M), M, fy, tick_f, INK, spacing=4)
    fy += 10
    src_f = font(SANS, 13)
    src = "Sources: Reuters  ·  BBC  ·  AP  ·  FT  ·  The Hindu  —  19 November 2026"
    d.text((M, fy), src, font=src_f, fill=GREY)

    img.save(OUT, format="PNG")
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
