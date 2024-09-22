from PIL import Image, ImageDraw, ImageFont
import os
import shutil

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

LHS_1 = ["Q", "C", "T", "O", "D", "S", "B"]
RHS_1 = ["M", "L", "W", "N", "X", "P", "E"]

pwd = os.path.dirname(os.path.abspath(__file__))

os.makedirs(os.path.join(pwd, "mv2", "output"), exist_ok=True)

output_dir = os.path.join(pwd, "mv2", "output")
replaces_dir = os.path.join(pwd, "mv2", "replaces")

for f in os.listdir(output_dir):
    os.remove(os.path.join(output_dir, f))

font = [
    ImageFont.truetype("CopperplateCC-Heavy.ttf", 184), # 1 char
    ImageFont.truetype("CopperplateCC-Heavy.ttf", 108), # 2 chars
    ImageFont.truetype("CopperplateCC-Heavy.ttf", 84), # 3 chars
    ImageFont.truetype("CopperplateCC-Heavy.ttf", 168), # for [E^]
    ImageFont.truetype("CopperplateCC-Heavy.ttf", 96), # for 1+2
    ImageFont.truetype("CopperplateCC-Heavy.ttf", 48), # for 1+2 subscript
]

colors = [
    (0xfd, 0xfd, 0xfd), # white
    (0x9c, 0x9c, 0x9c), # gray
    (0xff, 0xff, 0x00), # yellow
    (0xf3, 0xd7, 0xa2), # orange
]

SIZE = 256
BORDER = 8

counter = 0

def count_chars(s):
    # count all characters except ^ and '
    return sum(1 for c in s if c not in "^'")

def save(img):
    global counter
    counter += 1
    img.save(os.path.join(output_dir, f"{counter:03d}.jpg"))

def create(msg, opt=0):
    canvas = Image.new("RGB", (SIZE, SIZE), color=(0, 0, 0))
    foreground = colors[opt]
    draw = ImageDraw.Draw(canvas)
    _font = font[count_chars(msg) - 1]
    if "^" in msg:
        _font = font[3]
    elif msg == "1+2" or msg == "2+1":
        _font = font[1]
    w, h = draw.textsize(msg, font=_font)
    ascent, descent = _font.getmetrics()
    y = (SIZE - h - descent) // 2
    draw.text(((SIZE - w) // 2, y), msg, font=_font, fill=foreground)
    draw.rectangle([0, 0, BORDER, SIZE], fill=foreground)
    draw.rectangle([0, 0, SIZE, BORDER], fill=foreground)
    draw.rectangle([SIZE - BORDER, 0, SIZE, SIZE], fill=foreground)
    draw.rectangle([0, SIZE - BORDER, SIZE, SIZE], fill=foreground)
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
    sub1_x = xa + wa - 2
    sub2_x = xb + wb - 2
    
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
    create("V")
    for a in LHS:
        create(a)
    for b in RHS:
        create(b)
    
    create("?", 2)
    for a in LHS_BONUS:
        create(a, 1)
    for b in RHS_BONUS:
        create(b, 1)
    
    create("+", 2)
    for a in LHS_FULL:
        for b in RHS_FULL:
            opt = 0
            if a in LHS_BONUS or b in RHS_BONUS:
                opt = 1
            elif b == "X":
                opt = 3
            create(a + b, opt)
    
    create("+'", 2)
    for ab in COMBO_ALT:
        create(ab, 1)
    
    create("&", 2)
    for b in RHS_BOARD:
        for c in RHS_CLUE:
            create(b + c, ((b + c) not in ATTACH_ORD))
    
    create("&'", 2)
    for b in ATTACH_BONUS:
        create(b, 1)
    create("EL", 1)

    create("&+", 2)
    for a in LHS_FULL:
        for bc in ATTACH_ORD:
            opt = 0
            if a in LHS_BONUS:
                opt = 1
            elif bc == "EX":
                opt = 3
            create(a + bc, opt)
    
    create("#", 2)
    for b in RHS_BOARD:
        create(b + "#")
    
    create("#+", 2)
    for a in LHS_FULL:
        for b in RHS_BOARD:
            create(a + b + "#", (a in LHS_BONUS))
    
    create("2+1", 2)
    for a in LHS:
        for b in RHS_1:
            create_1_2(a, b, 2, 1, 3 if b == "M" else 0)
    
    create("1+2", 2)
    for a in LHS_1:
        for b in RHS:
            create_1_2(a, b, 1, 2, 3 if b == "X" else 0)

    for f in os.listdir(replaces_dir):
        shutil.copy(os.path.join(replaces_dir, f), output_dir)

if __name__ == "__main__":
    main()