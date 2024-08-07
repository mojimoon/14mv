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

image_dict = (dict(), dict())

pwd = os.path.dirname(os.path.abspath(__file__))

os.makedirs(os.path.join(pwd, "output"), exist_ok=True)

# clear output folder
for f in os.listdir(os.path.join(pwd, "output")):
    os.remove(os.path.join(pwd, "output", f))

SIZE = 256

counter = 0

def p(s, opt=False):
    return os.path.join(pwd, "assets", opt and f"22{s}.jpg" or f"2{s}.jpg")

def read(s, opt=False):
    # return Image.open(os.path.join(pwd, "assets", f"2{s}.jpg"))
    if s not in image_dict[opt]:
        image_dict[opt][s] = Image.open(p(s, opt))
    return image_dict[opt][s]

def save(img):
    global counter
    counter += 1
    img.save(os.path.join(pwd, "output", f"{counter:03d}.png"))

def combine2(a, b, opt=False):
    img = Image.new("RGBA", (SIZE, SIZE), (255, 255, 255, 0))
    img.paste(read(a, opt).resize((128, 128)), (0, 0))
    img.paste(read(b, opt).resize((128, 128)), (128, 128))
    return img

def combine2_alt(a, b, opt=False):
    img = Image.new("RGBA", (SIZE, SIZE), (255, 255, 255, 0))
    img.paste(read(a, opt).resize((128, 128)), (128, 0))
    img.paste(read(b, opt).resize((128, 128)), (0, 128))
    return img

# def combine2(a, b, opt=False):
#     img = Image.new("RGBA", (256, 128), (255, 255, 255, 0))
#     img.paste(read(a, opt).resize((128, 128)), (0, 0))
#     img.paste(read(b, opt).resize((128, 128)), (128, 0))
#     return img

# def combine2_alt(a, b, opt=False):
#     img = Image.new("RGBA", (128, 256), (255, 255, 255, 0))
#     img.paste(read(a, opt).resize((128, 128)), (0, 0))
#     img.paste(read(b, opt).resize((128, 128)), (0, 128))
#     return img

def combine3(a, b, c, opt=False):
    img = Image.new("RGBA", (SIZE, SIZE), (255, 255, 255, 0))
    img.paste(read(a, opt).resize((128, 128)), (64, 0))
    img.paste(read(b, opt).resize((128, 128)), (0, 128))
    img.paste(read(c, opt).resize((128, 128)), (128, 128))
    return img

def main():
    save(read("V"))
    for a in LHS:
        save(read(a))
    for b in RHS:
        save(read(b))
    for a in LHS_BONUS:
        save(read(a, True))
    for b in RHS_BONUS:
        save(read(b, True))
    
    save(read("+"))
    for a in LHS_FULL:
        for b in RHS_FULL:
            save(combine2(a, b, (a not in LHS or b not in RHS)))
    
    save(read("+", True))
    for ab in COMBO_ALT:
        save(combine2(ab[0], ab[1], True))
    
    save(read("&"))
    for bc in ATTACH:
        save(combine2_alt(bc[0], bc[1]))
    
    save(read("&", True))
    for bc in ATTACH_ALT:
        save(combine2_alt(bc[0], bc[1], True))
    for b in ATTACH_BONUS:
        save(read(b, True))
    save(combine2_alt(TAG[0], TAG[1], True))
    
    save(read("&+"))
    for a in LHS_FULL:
        for bc in ATTACH:
            save(combine3(a, bc[0], bc[1], (a not in LHS)))
    
    save(read("#"))
    for b in TAG:
        save(combine2_alt(b, "#"))
    
    save(read("#+"))
    for a in LHS_FULL:
        for b in TAG:
            save(combine3(a, b, "#", (a not in LHS)))

if __name__ == "__main__":
    main()