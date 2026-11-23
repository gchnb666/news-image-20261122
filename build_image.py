#!/usr/bin/env python3
"""Compose the 1024x1024 front-page image for news-image-20261122.

Renders all text with PIL (crisp, no garbled text) and crops a generated
editorial illustration (assets/cop31-hero.webp, a vast, mostly empty UN
climate summit hall with a glowing Earth above the stage) into the lead
slot. Run: python3 build_image.py
Writes entry.png (1024x1024, under 1 MiB). Requires Pillow locally only;
the entry itself is shipped as entry.png and main.py just copies it.
"""
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
NAVY = (15, 42, 74)
AMBER = (245, 176, 65)
INK = (18, 18, 18)
GREY = (90, 90, 90)
RED = (178, 34, 34)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

HERO = "assets/cop31-hero.webp"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


img = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(img)

# ---- masthead ----
d.rectangle([0, 0, W, 96], fill=NAVY)
d.text((32, 12), "WORLD NEWS", font=font(SERIF_B, 56), fill="white")
d.text((32, 64), "SUNDAY, 22 NOVEMBER 2026", font=font(SANS_B, 25), fill=AMBER)
d.text((W - 32, 20), "THE DAY IN", font=font(SANS_B, 23), fill="white", anchor="ra")
d.text((W - 32, 52), "ONE IMAGE", font=font(SANS_B, 23), fill="white", anchor="ra")

y = 96
# ---- lead kicker + headline (one line) ----
y += 14
d.text((32, y), "CLIMATE  •  TURKEY", font=font(SANS_B, 21), fill=RED)
y += 30
headline = "COP31 climate talks collapse"
d.text((32, y), headline, font=font(SANS_B, 44), fill=INK)
assert d.textlength(headline, font=font(SANS_B, 44)) <= W - 64, "headline too wide"
y += 54
y += 8

# ---- hero image ----
hero = Image.open(HERO).convert("RGB")
hero = hero.crop((0, 320, 1920, 910)).resize((W - 64, 290), Image.LANCZOS)
img.paste(hero, (32, y))
y += 290 + 10
# ---- lead summary ----
lead = ("UN summit ends without agreement as the EU rejects a pact that never "
        "names fossil fuels; the longest COP in history.")
for line in wrap(d, lead, font(SANS, 25), W - 64):
    d.text((32, y), line, font=font(SANS, 25), fill=(40, 40, 40))
    y += 32
y += 8
d.line([(32, y), (W - 32, y)], fill=INK, width=2)
y += 14

# ---- secondary stories (headline + one-line summary each) ----
stories = [
    ("LIBYA", "Ukrainian drones hit Russian warship in Libya",
     "Corvette struck at Benghazi port; a second vessel was also targeted."),
    ("UKRAINE", "Russian drone wrecks apartment block near Kyiv",
     "Three killed and 14 missing in Dymer as rescuers dig through rubble."),
    ("USA", "Democrats clinch 258 House seats, most since 1992",
     "AP calls North Carolina recount for Hubbard; Foxx concedes Sunday."),
    ("INDONESIA", "Candy factory fire kills 3, dozens missing",
     "Rescuers search the ruins in Cikande as the hunt for the missing goes on."),
    ("SPACE", "BepiColombo reaches Mercury orbit after 8 years",
     "ESA reports a thruster glitch in the burn; the spacecraft is safe."),
]
for tag, head, summ in stories:
    d.text((32, y), tag, font=font(SANS_B, 19), fill=RED)
    assert d.textlength(head, font=font(SANS_B, 27)) <= W - 64 - 133, (tag, head)
    d.text((165, y), head, font=font(SANS_B, 27), fill=INK)
    y += 32
    lines = wrap(d, summ, font(SANS, 21), W - 64 - 133)
    assert len(lines) == 1, (tag, lines)
    d.text((165, y), lines[0], font=font(SANS, 21), fill=GREY)
    y += 27
    y += 18

# ---- footer ----
d.line([(32, y + 2), (W - 32, y + 2)], fill=INK, width=2)
d.text((W // 2, y + 12), "22 NOVEMBER 2026  •  THE DAY'S WORLD NEWS IN ONE IMAGE",
       font=font(SANS_B, 20), fill=GREY, anchor="ma")
assert y + 12 + 24 <= H - 8, ("layout overflow", y)

# outer border
d.rectangle([0, 0, W - 1, H - 1], outline=INK, width=3)

img.save("entry.png", optimize=True)
print("saved entry.png", img.size)
print("bytes:", os.path.getsize("entry.png"))
