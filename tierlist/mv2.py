from PIL import Image, ImageDraw, ImageFont
import os

LHS = ["H", "C", "S", "G", "F", "B", "T"]
LHS_BONUS = ["Z", "G'"]
LHS_FULL = ["H", "C", "S", "G", "F", "B", "T", "Z", "G'"]
RHS = ["X", "D", "P", "E", "M", "A", "L"]
RHS_BONUS = ["X'", "I"]
RHS_FULL = ["X", "D", "P", "E", "M", "A", "L", "X'", "I"]
ATTACH = ["EX", "ED", "EA", "LX", "LD", "LM", "LP"]
ATTACH_ORD = ["EX", "LD", "LM", "EA", "LX", "ED", "LP"]
ATTACH_ALT = ["EM", "EP", "LA"]
ATTACH_BONUS = ["E'", "E^", "L'"]
COMBO_ALT = ["GH", "CH", "CG", "FG", "FH", "CF", "BH", "GR"]
TAG = ["E", "L"]

pwd = os.path.dirname(os.path.abspath(__file__))

root = os.path.dirname(pwd)

os.makedirs(os.path.join(pwd, "mv2", "output"), exist_ok=True)

for f in os.listdir(os.path.join(pwd, "mv2", "output")):
    os.remove(os.path.join(pwd, "mv2", "output", f))

image_dict = (dict(), dict())

font = [
    ImageFont.truetype("CopperplateCC-Heavy.ttf", 184), # 1 char
    ImageFont.truetype("CopperplateCC-Heavy.ttf", 112), # 2 chars
    ImageFont.truetype("CopperplateCC-Heavy.ttf", 80), # 3 chars
    ImageFont.truetype("CopperplateCC-Heavy.ttf", 160), # for E^
]

colors = [
    (0xfd, 0xfd, 0xfd), # white
    (0x9c, 0x9c, 0x9c), # gray
    (0xff, 0xff, 0x00), # yellow
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
    img.save(os.path.join(pwd, "mv2", "output", f"{counter:03d}.jpg"))

def create(msg, opt=0):
    canvas = Image.new("RGB", (SIZE, SIZE), color=(0, 0, 0))
    foreground = colors[opt]
    draw = ImageDraw.Draw(canvas)
    _font = font[count_chars(msg) - 1]
    if "^" in msg:
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
            create(a + b, (a in LHS_BONUS) or (b in RHS_BONUS))
    
    create("+'", 2)
    for ab in COMBO_ALT:
        create(ab, 1)
    
    create("&", 2)
    for bc in ATTACH:
        create(bc)
    
    create("&'", 2)
    for bc in ATTACH_ALT:
        create(bc, 1)
    for b in ATTACH_BONUS:
        create(b, 1)
    create("EL", 1)

    create("&+", 2)
    for a in LHS_FULL:
        for bc in ATTACH_ORD:
            create(a + bc, (a in LHS_BONUS))
    
    create("#", 2)
    for b in TAG:
        create(b + "#")
    
    create("#+", 2)
    for a in LHS_FULL:
        for b in TAG:
            create(a + b + "#", (a in LHS_BONUS))

if __name__ == "__main__":
    main()