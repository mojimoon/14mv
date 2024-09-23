from PIL import Image, ImageDraw, ImageFont
import os
import shutil

LHS = ["Q", "C", "T", "O", "D", "S", "B"]
LHS_BONUS = ["D'", "A", "H", "T'"]
LHS_FULL = LHS + LHS_BONUS
RHS = ["M", "L", "W", "N", "X", "P", "E"]
RHS_BONUS = ["X'", "K", "W'", "E'"]
RHS_FULL = RHS + RHS_BONUS
COMBO_ALT = [
    "CD", "CQ", "CT", "OQ", "OT", "QT",
    "LM", "MX", "MN", "NX", "UW"
]
TAG = ["#", "#'"]

pwd = os.path.dirname(os.path.abspath(__file__))

os.makedirs(os.path.join(pwd, "mv", "output"), exist_ok=True)

output_dir = os.path.join(pwd, "mv", "output")
replaces_dir = os.path.join(pwd, "mv", "replaces")

for f in os.listdir(output_dir):
    os.remove(os.path.join(output_dir, f))

font = [
    ImageFont.truetype("CopperplateCC-Heavy.ttf", 184), # 1 char
    ImageFont.truetype("CopperplateCC-Heavy.ttf", 108), # 2 chars
    ImageFont.truetype("CopperplateCC-Heavy.ttf", 164), # for [W']
    ImageFont.truetype("CopperplateCC-Heavy.ttf", 96), # for [+][W']
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
    return sum(1 for c in s if c not in "'")

def save(img):
    global counter
    counter += 1
    img.save(os.path.join(output_dir, f"{counter:03d}.jpg"))

def create(msg, opt=0):
    canvas = Image.new("RGB", (SIZE, SIZE), color=(0, 0, 0))
    foreground = colors[opt]
    draw = ImageDraw.Draw(canvas)
    _font = font[count_chars(msg) - 1]
    if msg == "W'":
        _font = font[2]
    elif "W'" in msg:
        _font = font[3]
    w, h = draw.textsize(msg, font=_font)
    ascent, descent = _font.getmetrics()
    y = (SIZE - h - descent) // 2
    draw.text(((SIZE - w) // 2, y), msg, font=_font, fill=foreground)
    draw.rectangle([0, 0, BORDER, SIZE], fill=foreground)
    draw.rectangle([0, 0, SIZE, BORDER], fill=foreground)
    draw.rectangle([SIZE - BORDER, 0, SIZE, SIZE], fill=foreground)
    draw.rectangle([0, SIZE - BORDER, SIZE, SIZE], fill=foreground)
    save(canvas)

def main():
    global counter
    
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
    
    create("+'", 2)
    for ab in COMBO_ALT:
        create(ab, 1)
    
    create("#")
    create("#'", 1)

    create("+", 2)
    comb_id = counter
    for a in LHS_FULL:
        for b in RHS_FULL:
            opt = 0
            if a in LHS_BONUS or b in RHS_BONUS:
                opt = 1
            if b == "M":
                opt += 3
            create(a + b, opt)

    create("#+", 2)
    tag_comb_id = counter
    for b in TAG:
        for a in LHS_FULL:
            create(a + b, (a in LHS_BONUS) or (b == "#'"))
    
    shutil.copy(os.path.join(replaces_dir, "comb.jpg"), os.path.join(output_dir, f"{comb_id:03d}.jpg"))
    shutil.copy(os.path.join(replaces_dir, "tag_comb.jpg"), os.path.join(output_dir, f"{tag_comb_id:03d}.jpg"))

if __name__ == "__main__":
    main()
