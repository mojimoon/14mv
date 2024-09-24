from PIL import Image, ImageDraw, ImageFont
import os
import shutil
import pandas as pd
import math

LHS = ["H", "C", "S", "G", "F", "B", "T"]
LHS_BONUS = ["Z", "G'"]
LHS_FULL = ["H", "C", "S", "G", "F", "B", "T", "Z", "G'"]
RHS = ["X", "D", "P", "E", "M", "A", "L"]
RHS_BONUS = ["X'", "I"]
RHS_FULL = ["X", "D", "P", "E", "M", "A", "L", "X'", "I"]
ATTACH_ORD = ["EX", "LD", "LM", "EA", "LX", "ED", "LP"]
ATTACH_BONUS = ["E'", "E^", "L'"]
COMBO_ALT = ["GH", "CH", "CG", "FG", "FH", "CF", "BH", "GR"]
RHS_CLUE = ["X", "D", "P", "M", "A"]
RHS_BOARD = ["E", "L"]

MAIN = ["V", *LHS, *RHS]
LHS_1 = ["Q", "C", "T", "O", "D", "S", "B"]
RHS_1 = ["M", "L", "W", "N", "X", "P", "E"]

pwd = os.path.dirname(os.path.abspath(__file__))

os.makedirs(os.path.join(pwd, "mv2", "output_stat"), exist_ok=True)
output_dir = os.path.join(pwd, "mv2", "output_stat")

replaces_dir = os.path.join(pwd, "mv2", "replaces")

for f in os.listdir(output_dir):
    os.remove(os.path.join(output_dir, f))

root = os.path.dirname(pwd)
in_file = os.path.join(root, "stat", "mv2", "mv2_stats_update1.csv")
df = pd.read_csv(in_file)

def get(df, filters, key):
    for k, v in filters.items():
        df = df[df[k] == v]
    return df[key].mean() if not df.empty else -1

font = [
    ImageFont.truetype("CopperplateCC-Heavy.ttf", 184), # 1 char
    ImageFont.truetype("CopperplateCC-Heavy.ttf", 108), # 2 chars
    ImageFont.truetype("CopperplateCC-Heavy.ttf", 84), # 3 chars
    ImageFont.truetype("CopperplateCC-Heavy.ttf", 168), # for [E^]
    ImageFont.truetype("CopperplateCC-Heavy.ttf", 96), # for 1+2
    ImageFont.truetype("CopperplateCC-Heavy.ttf", 48), # for 1+2 subscript
    ImageFont.truetype("CopperplateCC-Heavy.ttf", 52), # for workload
]

colors = [
    (0xfd, 0xfd, 0xfd), # white
    (0x9c, 0x9c, 0x9c), # gray
    (0xff, 0xff, 0x00), # yellow
    (0xf3, 0xd7, 0xa2), # orange
    (0xb2, 0xa5, 0x8f), # gray orange
]

SIZE = 256
BORDER = 8

counter = 0

def count_chars(s):
    # count all characters except ^ and '
    return sum(1 for c in s if c not in "^'")

class TempImage:
    def __init__(self, img, d0, d1):
        self.img = img
        self.d0 = int(d0)
        self.d1 = int(d1)
    
    def __lt__(self, other):
        return self.d1 < other.d1 or (self.d1 == other.d1 and self.d0 < other.d0)

images = []

def save(img):
    global counter
    counter += 1
    img.save(os.path.join(output_dir, f"{counter:03d}.jpg"))
    # images.append(TempImage(img, d0, d1))

def create(msg, tname, opt=0):
    canvas = Image.new("RGB", (SIZE, SIZE), color=(0, 0, 0))
    foreground = colors[opt]
    draw = ImageDraw.Draw(canvas)
    _font = font[count_chars(msg) - 1]
    if msg in ["1+2", "2+1"]:
        _font = font[1]
    elif count_chars(msg) == 1 and tname:
        _font = font[1]
    w, h = draw.textsize(msg, font=_font)
    ascent, descent = _font.getmetrics()
    y = (SIZE - h - descent) // 2
    draw.text(((SIZE - w) // 2, y), msg, font=_font, fill=foreground)
    draw.rectangle([0, 0, BORDER, SIZE], fill=foreground)
    draw.rectangle([0, 0, SIZE, BORDER], fill=foreground)
    draw.rectangle([SIZE - BORDER, 0, SIZE, SIZE], fill=foreground)
    draw.rectangle([0, SIZE - BORDER, SIZE, SIZE], fill=foreground)

    if tname:
        d0 = str(math.floor(get(df, {"type": tname, 'difficulty': 0, 'dimension': 8}, 'workload')))
        d1 = str(math.floor(get(df, {"type": tname, 'difficulty': 1, 'dimension': 8}, 'workload')))

        # d0: upper left, d1: upper right, d2: lower right
        w0, h0 = draw.textsize(d0, font=font[6])
        w1, h1 = draw.textsize(d1, font=font[6])
        y = BORDER + 10
        x0 = BORDER + 10
        x1 = SIZE - BORDER - w1 - 10
        draw.text((x0, y), d0, font=font[6], fill=colors[0])
        draw.text((x1, y), d1, font=font[6], fill=colors[2])

        if msg in MAIN:
            d2 = str(math.floor(get(df, {"type": tname, 'difficulty': 2, 'dimension': 8}, 'workload')))
            w2, h2 = draw.textsize(d2, font=font[6])
            y2 = SIZE - BORDER - h2 - 14
            x2 = SIZE - BORDER - w2 - 10
            draw.text((x2, y2), d2, font=font[6], fill=colors[3])

    save(canvas)

def create_1_2(a, b, sub1, sub2, opt=0):
    canvas = Image.new("RGB", (SIZE, SIZE), color=(0, 0, 0))
    foreground = colors[opt]
    draw = ImageDraw.Draw(canvas)

    _font = font[4]
    wa, ha = draw.textsize(a, font=_font)
    if b == 'W':
        wb, hb = draw.textsize(b, font=font[2])
    else:
        wb, hb = draw.textsize(b, font=_font)
    ascent, descent = _font.getmetrics()
    # left half for a, right half for b
    xa = (SIZE // 2 - wa) // 2 - 4
    xb = SIZE // 2 + (SIZE // 2 - wb) // 2 - 20
    ya = (SIZE - ha - descent) // 2
    yb = (SIZE - hb - descent) // 2

    sub_font = font[5]
    w1, h1 = draw.textsize(str(sub1), font=sub_font)
    w2, h2 = draw.textsize(str(sub2), font=sub_font)
    asub, dsub = sub_font.getmetrics()
    # sub 1 left-top x = a bottom-right x
    # sub 1 middle y = a bottom y
    sub_y = max(ya + ha - (h1 + dsub) // 2, yb + hb - (h2 + dsub) // 2)
    sub1_x = xa + wa - 2 * sub1
    sub2_x = xb + wb - 2 * sub2

    if b == "L" or b == "E":
        sub2_x += 2

    tname = f"{sub1}{a}-{sub2}{b}"
    d0 = str(math.floor(get(df, {"type": tname, 'difficulty': 0, 'dimension': 8}, 'workload')))
    d1 = str(math.floor(get(df, {"type": tname, 'difficulty': 1, 'dimension': 8}, 'workload')))

    w0, h0 = draw.textsize(d0, font=font[6])
    w1, h1 = draw.textsize(d1, font=font[6])
    y = BORDER + 10
    x0 = BORDER + 10
    x1 = SIZE - BORDER - w1 - 10
    draw.text((x0, y), d0, font=font[6], fill=colors[0])
    draw.text((x1, y), d1, font=font[6], fill=colors[2])
    
    draw.text((xa, ya), a, font=_font, fill=foreground)
    draw.text((xb, yb), b, font=_font, fill=foreground)
    draw.text((sub1_x, sub_y), str(sub1), font=sub_font, fill=foreground)
    draw.text((sub2_x, sub_y), str(sub2), font=sub_font, fill=foreground)
    draw.rectangle([0, 0, BORDER, SIZE], fill=foreground)
    draw.rectangle([0, 0, SIZE, BORDER], fill=foreground)
    draw.rectangle([SIZE - BORDER, 0, SIZE, SIZE], fill=foreground)
    draw.rectangle([0, SIZE - BORDER, SIZE, SIZE], fill=foreground)
    save(canvas)

def main():
    global counter

    create("V", "V", 0)
    for a in LHS:
        create(a, "2" + a, 0)
    for b in RHS:
        create(b, "2" + b, 0)
    
    create("?", "", 2)
    for a in LHS_BONUS:
        create(a, "2" + a, 1)
    for b in RHS_BONUS:
        create(b, "2" + b, 1)
    
    create("+'", "", 2)
    for ab in COMBO_ALT:
        if ab == "GR":
            create(ab, "2G-R", 1)
        else:
            create(ab, "2" + ab[0] + "-2" + ab[1], 1)
    
    create("&", "", 2)
    for b in RHS_BOARD:
        for c in RHS_CLUE:
            create(b + c, "2" + b + "-2" + c, (b + c not in ATTACH_ORD))
    
    create("&'", "", 2)
    for b in ATTACH_BONUS:
        create(b, "2" + b, 1)
    create("EL", "2E-2L", 1)
    
    create("#", "", 2)
    for b in RHS_BOARD:
        create(b + "#", "2" + b + "-2#", 0)
    
    create("+", "", 2)
    comb_id = counter
    for a in LHS_FULL:
        for b in RHS_FULL:
            opt = 0
            if a in LHS_BONUS or b in RHS_BONUS:
                opt = 1
            if b == "X":
                opt += 3
            create(a + b, "2" + a + "-2" + b, opt)

    create("&+", "", 2)
    attach_comb_id = counter
    for a in LHS_FULL:
        for bc in ATTACH_ORD:
            opt = 0
            if a in LHS_BONUS:
                opt = 1
            if bc == "EX":
                opt += 3
            create(a + bc, "2" + a + "-2" + bc[0] + "-2" + bc[1], opt)
    
    create("#+", "", 2)
    tag_comb_id = counter
    for a in LHS_FULL:
        for b in RHS_BOARD:
            create(a + b + "#", "2" + a + "-2" + b + "-2#", a in LHS_BONUS)
    
    create("2+1", "", 2)
    for a in LHS:
        for b in RHS_1:
            create_1_2(a, b, 2, 1, 3 if b == "M" else 0)
            # create_1_2(a, b, 2, 1, 0)
    
    create("1+2", "", 2)
    for a in LHS_1:
        for b in RHS:
            create_1_2(a, b, 1, 2, 3 if b == "X" else 0)
            # create_1_2(a, b, 1, 2, 0)

    shutil.copy(os.path.join(replaces_dir, "comb.jpg"), os.path.join(output_dir, f"{comb_id:03d}.jpg"))
    shutil.copy(os.path.join(replaces_dir, "attach_comb.jpg"), os.path.join(output_dir, f"{attach_comb_id:03d}.jpg"))
    shutil.copy(os.path.join(replaces_dir, "tag_comb.jpg"), os.path.join(output_dir, f"{tag_comb_id:03d}.jpg"))

    # images.sort()
    # images.reverse()
    # for i, img in enumerate(images):
    #     img.img.save(os.path.join(output_dir, f"{i+1:03d}.jpg"))

if __name__ == "__main__":
    main()
