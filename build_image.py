#!/usr/bin/env python3
"""Render the front page for Thursday 19 November 2026 as a 1024x1024 PNG.

The picture is a newspaper front page: masthead, one lead story with a
drawn neon-sunset skyline, six further stories in a grid, and a footer
ticker. Everything is fixed — palette, text, seeded details — so running
the script twice produces identical bytes. Only Pillow is needed to draw;
the graded entrypoint (main.py) is stdlib-only and just copies the PNG.

Stories verified for 19 Nov 2026 against Reuters, BBC, AP, FT, The Hindu,
Jagran Josh, Newsmriti and SimpleLife.news.
"""
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent
TARGET = BASE / "entry.png"

SIZE = 1024
BACKGROUND = (248, 244, 233)
BLACK = (20, 20, 20)
MUTED = (90, 86, 76)
SCARLET = (185, 28, 28)
FRAME = (60, 56, 48)
BODY = (52, 50, 44)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANSB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANSR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def load_font(path, size):
    return ImageFont.truetype(path, size)


def wrap_text(canvas, text, typeface, max_width):
    """Split text into lines no wider than max_width (greedy, word by word)."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = (current + " " + word).strip()
        if canvas.textlength(candidate, font=typeface) <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_paragraph(canvas, lines, x, y, typeface, colour, leading=4):
    """Draw stacked lines; return the y just below the last one."""
    for line in lines:
        canvas.text((x, y), line, font=typeface, fill=colour)
        y += typeface.size + leading
    return y


def paint_skyline(canvas, region):
    """Neon sunset over a Vice City-style coastal skyline."""
    left, top, right, bottom = region
    span = right - left
    height = bottom - top
    sea_line = top + int(height * 0.62)
    sky_top = (46, 16, 78)
    sky_mid = (168, 52, 110)
    sky_low = (255, 140, 66)
    row = top
    while row < sea_line:
        frac = (row - top) / max(1, sea_line - top)
        if frac < 0.55:
            blend = frac / 0.55
            shade = tuple(
                int(sky_top[i] + (sky_mid[i] - sky_top[i]) * blend)
                for i in range(3)
            )
        else:
            blend = (frac - 0.55) / 0.45
            shade = tuple(
                int(sky_mid[i] + (sky_low[i] - sky_mid[i]) * blend)
                for i in range(3)
            )
        canvas.line([(left, row), (right, row)], fill=shade)
        row += 1
    # low sun, half risen above the rooftops
    sun_x = (left + right) // 2 + 60
    sun_y = sea_line - 56
    sun_r = 46
    canvas.ellipse(
        [sun_x - sun_r, sun_y - sun_r, sun_x + sun_r, sun_y + sun_r],
        fill=(255, 214, 120),
    )
    canvas.ellipse(
        [sun_x - sun_r + 8, sun_y - sun_r + 8, sun_x + sun_r - 8, sun_y + sun_r - 8],
        fill=(255, 236, 170),
    )
    # stars high in the sky
    rng = random.Random(19)
    for _ in range(40):
        sx = rng.randint(left + 4, right - 4)
        sy = rng.randint(top + 4, top + 90)
        rad = rng.choice([1, 1, 2])
        canvas.ellipse([sx - rad, sy - rad, sx + rad, sy + rad], fill=(230, 220, 245))
    # two layers of towers: purple behind, near-black in front
    rear = [
        (0, 96, 30), (34, 70, 66), (70, 110, 96), (100, 60, 132),
        (136, 96, 168), (172, 78, 206), (210, 118, 240), (244, 84, 272),
        (276, 104, 306), (310, 64, 344), (348, 100, 380), (384, 74, 416),
        (420, 112, 452),
    ]
    for bx0, bh, bx1 in rear:
        canvas.rectangle(
            [left + bx0, sea_line - bh, left + bx1, sea_line], fill=(58, 26, 74)
        )
    fore = [
        (0, 58, 44), (48, 88, 84), (88, 46, 118), (122, 76, 158),
        (162, 52, 196), (200, 92, 238), (242, 60, 276), (280, 84, 316),
        (320, 48, 352), (356, 78, 392), (396, 56, 428), (432, 86, 468),
    ]
    for bx0, bh, bx1 in fore:
        canvas.rectangle(
            [left + bx0, sea_line - bh, left + bx1, sea_line], fill=(24, 10, 34)
        )
    # lit windows, seeded so they never move
    rng = random.Random(1911)
    for bx0, bh, bx1 in fore:
        for _ in range(9):
            wx = rng.randint(left + bx0 + 4, left + bx1 - 8)
            wy = rng.randint(sea_line - bh + 6, sea_line - 10)
            glow = rng.choice([(255, 200, 90), (120, 220, 255), (255, 120, 180)])
            canvas.rectangle([wx, wy, wx + 4, wy + 5], fill=glow)
    # palm silhouettes at both edges
    for px, py, scale in ((left + 26, sea_line - 6, 1.0), (right - 30, sea_line - 4, 0.85)):
        top_x = px + int(6 * scale)
        top_y = py - int(52 * scale)
        canvas.line([(px, py), (top_x, top_y)], fill=(16, 8, 24), width=5)
        for deg in (-70, -35, 0, 35, 70):
            ang = math.radians(deg - 90)
            tip_x = top_x + int(30 * scale * math.cos(ang))
            tip_y = top_y + int(30 * scale * math.sin(ang)) + 14
            canvas.line([(top_x, top_y), (tip_x, tip_y)], fill=(16, 8, 24), width=4)
    # water and the sun's reflection
    canvas.rectangle([left, sea_line, right, bottom], fill=(14, 18, 44))
    wave_y = sea_line + 8
    while wave_y < bottom - 6:
        canvas.line([(left + 12, wave_y), (right - 12, wave_y)], fill=(28, 40, 76))
        wave_y += 12
    for step, width in enumerate((110, 78, 48)):
        canvas.line(
            [(sun_x - width // 2, sea_line + 10 + step * 12),
             (sun_x + width // 2, sea_line + 10 + step * 12)],
            fill=(255, 170, 80),
            width=3,
        )
    canvas.text(
        (left + 12, bottom - 26),
        "ILLUSTRATION: VICE CITY AT SUNSET",
        font=load_font(SANSB, 13),
        fill=(210, 214, 220),
    )


def glyph_globe(canvas, region, colour):
    left, top, right, bottom = region
    cx, cy = (left + right) // 2, (top + bottom) // 2
    rad = min(right - left, bottom - top) // 2 - 2
    canvas.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], outline=colour, width=3)
    canvas.ellipse(
        [cx - rad // 2, cy - rad, cx + rad // 2, cy + rad], outline=colour, width=2
    )
    canvas.line([(cx - rad, cy), (cx + rad, cy)], fill=colour, width=2)


def glyph_waves(canvas, region, colour):
    left, top, right, _ = region
    for yy in (top + 10, top + 22, top + 34):
        canvas.arc([left, yy, right, yy + 16], 180, 360, fill=colour, width=3)


def glyph_swap(canvas, region, colour):
    left, top, right, bottom = region
    canvas.line([(left + 4, top + 12), (right - 10, top + 12)], fill=colour, width=3)
    canvas.polygon(
        [(right - 10, top + 6), (right - 2, top + 12), (right - 10, top + 18)],
        fill=colour,
    )
    canvas.line([(right - 4, bottom - 12), (left + 10, bottom - 12)], fill=colour, width=3)
    canvas.polygon(
        [(left + 10, bottom - 18), (left + 2, bottom - 12), (left + 10, bottom - 6)],
        fill=colour,
    )


def glyph_cyclone(canvas, region, colour):
    left, top, right, bottom = region
    cx, cy = (left + right) // 2, (top + bottom) // 2
    for rad in (18, 12, 6):
        canvas.arc([cx - rad, cy - rad, cx + rad, cy + rad], 30, 300, fill=colour, width=3)


def glyph_capitol(canvas, region, colour):
    left, top, right, bottom = region
    cx = (left + right) // 2
    canvas.polygon([(cx - 16, top + 8), (cx + 16, top + 8), (cx, top - 2)], fill=colour)
    canvas.rectangle([cx - 3, top + 4, cx + 3, top + 12], fill=colour)
    canvas.rectangle([left + 6, top + 14, right - 6, top + 20], fill=colour)
    for i in range(4):
        bx = left + 8 + i * 10
        canvas.rectangle([bx, top + 22, bx + 5, bottom - 8], fill=colour)
    canvas.rectangle([left + 4, bottom - 8, right - 4, bottom - 4], fill=colour)


def glyph_rocket(canvas, region, colour):
    left, top, right, bottom = region
    cx = (left + right) // 2
    canvas.polygon([(cx, top + 2), (cx + 9, top + 20), (cx - 9, top + 20)], fill=colour)
    canvas.rectangle([cx - 9, top + 20, cx + 9, bottom - 14], fill=colour)
    canvas.polygon(
        [(cx - 9, bottom - 14), (cx - 16, bottom - 4), (cx - 9, bottom - 8)], fill=colour
    )
    canvas.polygon(
        [(cx + 9, bottom - 14), (cx + 16, bottom - 4), (cx + 9, bottom - 8)], fill=colour
    )
    canvas.polygon(
        [(cx - 4, bottom - 12), (cx + 4, bottom - 12), (cx, bottom - 2)], fill=colour
    )


GLYPHS = {
    "globe": glyph_globe,
    "waves": glyph_waves,
    "swap": glyph_swap,
    "cyclone": glyph_cyclone,
    "capitol": glyph_capitol,
    "rocket": glyph_rocket,
}

ITEMS = [
    {
        "section": "US POLITICS",
        "colour": (21, 80, 160),
        "glyph": "capitol",
        "headline": "JEFFRIES SET TO BE FIRST BLACK SPEAKER",
        "standfirst": "Democrats nominate Hakeem Jeffries to lead the House.",
    },
    {
        "section": "UKRAINE",
        "colour": (158, 116, 8),
        "glyph": "swap",
        "headline": "EU PROPOSES €45BN LOAN FOR UKRAINE",
        "standfirst": "Brussels offers a 2027 loan, to be repaid from Russian reparations.",
    },
    {
        "section": "THE GULF",
        "colour": (14, 116, 144),
        "glyph": "waves",
        "headline": "US AND IRAN TRADE FIRE AGAIN",
        "standfirst": "US hits a missile site on Qeshm Island; Iran strikes a US radar in Bahrain and a base in Kuwait.",
    },
    {
        "section": "WEATHER",
        "colour": (29, 78, 216),
        "glyph": "cyclone",
        "headline": "CYCLONE AKVAN BEARS DOWN",
        "standfirst": "The Bay of Bengal storm heads for India's east coast.",
    },
    {
        "section": "SPACE",
        "colour": (109, 40, 217),
        "glyph": "rocket",
        "headline": "VOYAGER 1 REACHES ONE LIGHT-DAY",
        "standfirst": "Nearly 50 years after launch, NASA's probe hits the milestone.",
    },
    {
        "section": "EUROPE",
        "colour": (190, 18, 60),
        "glyph": "globe",
        "headline": "COALITION OF THE WILLING MEETS IN BERLIN",
        "standfirst": "Leaders gather on Ukraine support and security guarantees.",
    },
]


def render():
    page = Image.new("RGB", (SIZE, SIZE), BACKGROUND)
    canvas = ImageDraw.Draw(page)
    edge = 30
    canvas.rectangle(
        [edge - 8, edge - 8, SIZE - edge + 8, SIZE - edge + 8], outline=FRAME, width=2
    )

    # ---- masthead ----
    name_face = load_font(SERIF, 78)
    name = "THE WORLD TODAY"
    name_w = canvas.textlength(name, font=name_face)
    canvas.text(((SIZE - name_w) / 2, 30), name, font=name_face, fill=BLACK)
    cursor = 30 + 78 + 10
    canvas.line([(edge, cursor), (SIZE - edge, cursor)], fill=BLACK, width=3)
    canvas.line([(edge, cursor + 6), (SIZE - edge, cursor + 6)], fill=BLACK, width=1)
    cursor += 16
    date_face = load_font(SANSB, 27)
    dateline = "THURSDAY, 19 NOVEMBER 2026"
    date_w = canvas.textlength(dateline, font=date_face)
    canvas.text(((SIZE - date_w) / 2, cursor), dateline, font=date_face, fill=SCARLET)
    cursor += 27 + 10
    motto_face = load_font(SANSR, 16)
    motto = "ONE DAY  ·  ONE IMAGE  —  THE WORLD IN A SINGLE FRAME"
    motto_w = canvas.textlength(motto, font=motto_face)
    canvas.text(((SIZE - motto_w) / 2, cursor), motto, font=motto_face, fill=MUTED)
    cursor += 16 + 14

    # ---- lead story ----
    lead_top = cursor
    lead_height = 282
    canvas.rectangle(
        [edge, lead_top, SIZE - edge, lead_top + lead_height], outline=BLACK, width=2
    )
    picture = (edge + 2, lead_top + 2, edge + 482, lead_top + lead_height - 2)
    paint_skyline(canvas, picture)
    text_x = edge + 482 + 26
    text_w = SIZE - edge - 26 - text_x
    cursor = lead_top + 24
    canvas.text((text_x, cursor), "CULTURE", font=load_font(SANSB, 17), fill=SCARLET)
    cursor += 17 + 12
    lead_face = load_font(SANSB, 37)
    lead_lines = wrap_text(canvas, "GTA VI IS HERE AT LAST", lead_face, text_w)
    cursor = draw_paragraph(canvas, lead_lines, text_x, cursor, lead_face, BLACK, 6)
    cursor += 10
    canvas.line([(text_x, cursor), (text_x + 64, cursor)], fill=SCARLET, width=4)
    cursor += 18
    deck_face = load_font(SANSR, 18)
    deck = (
        "After a 13-year wait, Rockstar's blockbuster rolls out worldwide "
        "from New Zealand — Metacritic 99, preorders past $1.5 billion."
    )
    draw_paragraph(
        canvas, wrap_text(canvas, deck, deck_face, text_w), text_x, cursor, deck_face, BODY, 6
    )
    cursor = lead_top + lead_height + 16

    # ---- six stories in a 3 x 2 grid ----
    columns, rows = 3, 2
    gutter = 15
    cell_w = (SIZE - 2 * edge - (columns - 1) * gutter) // columns
    cell_h = 184
    grid_top = cursor
    for pos, item in enumerate(ITEMS):
        row, col = divmod(pos, columns)
        x = edge + col * (cell_w + gutter)
        y0 = grid_top + row * (cell_h + gutter)
        canvas.rectangle(
            [x, y0, x + cell_w, y0 + cell_h], outline=(150, 144, 128), width=1
        )
        canvas.rectangle([x, y0, x + cell_w, y0 + 5], fill=item["colour"])
        gx = x + cell_w - 52
        GLYPHS[item["glyph"]](
            canvas, (gx, y0 + 16, gx + 44, y0 + 60), item["colour"]
        )
        inner_x = x + 16
        inner_y = y0 + 16
        canvas.text(
            (inner_x, inner_y),
            item["section"],
            font=load_font(SANSB, 14),
            fill=item["colour"],
        )
        inner_y += 14 + 8
        head_face = load_font(SANSB, 20)
        head_lines = wrap_text(canvas, item["headline"], head_face, cell_w - 32 - 52)
        inner_y = draw_paragraph(canvas, head_lines, inner_x, inner_y, head_face, BLACK, 3)
        inner_y += 6
        deck_face = load_font(SANSR, 15)
        draw_paragraph(
            canvas,
            wrap_text(canvas, item["standfirst"], deck_face, cell_w - 32),
            inner_x,
            inner_y,
            deck_face,
            BODY,
            4,
        )

    # ---- footer ticker ----
    foot = grid_top + rows * cell_h + (rows - 1) * gutter + 16
    canvas.line([(edge, foot), (SIZE - edge, foot)], fill=BLACK, width=2)
    foot += 12
    tick_face = load_font(SANSB, 15)
    ticker = (
        "ALSO TODAY:   Nvidia chief Jensen Huang resigns; Colette Kress takes over  ·  "
        "Fed minutes point to more rate rises  ·  Modi meets the Prince and Princess of Wales  ·  "
        "Russian military plane crashes in Siberia, all 19 aboard killed  ·  "
        "Australia sanctions Israeli settlers"
    )
    foot = draw_paragraph(
        canvas, wrap_text(canvas, ticker, tick_face, SIZE - 2 * edge), edge, foot, tick_face, BLACK, 4
    )
    foot += 10
    credit_face = load_font(SANSR, 13)
    canvas.text(
        (edge, foot),
        "Sources: Reuters  ·  BBC  ·  AP  ·  FT  ·  The Hindu  —  19 November 2026",
        font=credit_face,
        fill=MUTED,
    )

    page.save(TARGET, format="PNG")
    print(f"wrote {TARGET} ({TARGET.stat().st_size} bytes)")


if __name__ == "__main__":
    render()
