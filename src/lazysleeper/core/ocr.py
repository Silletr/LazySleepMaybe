import re
import pytesseract
from PIL import Image, ImageOps


#    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
#    ┃                                  IMPORTANT:                                  ┃
#    ┃    CLAUDE-ASSISTED OCR CODE CUZ I COULDN'T COME UP HOW TO MAKE IT CORRECT    ┃
#    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛



img = Image.open("test.png").convert("L")
if sum(img.resize((64, 64)).getdata()) / 4096 < 128:  # dark theme -> invert
    img = ImageOps.invert(img)

W, H = img.size


def ocr_crop(box, whitelist, psm=7):
    crop = img.crop(box)
    crop = crop.resize((crop.width * 3, crop.height * 3), Image.LANCZOS)
    crop = crop.point(lambda p: 255 if p > 140 else 0)  # binarize
    cfg = f"--psm {psm} -c tessedit_char_whitelist={whitelist}"
    return pytesseract.image_to_string(crop, config=cfg).strip()


def to_minutes(text):
    nums = [int(n) for n in re.findall(r"\d+", text)]
    if len(nums) >= 2:
        return nums[0] * 60 + nums[1]
    if len(nums) == 1:
        return nums[0]  # only minutes shown
    return None


# 1. find anchor words on the full page
data = pytesseract.image_to_data(img, config="--psm 11", output_type=pytesseract.Output.DICT)
words = [
    dict(t=t.strip().lower(), x=data["left"][i], y=data["top"][i],
         w=data["width"][i], h=data["height"][i])
    for i, t in enumerate(data["text"]) if t.strip()
]


def find(word, below=0):
    hits = [w for w in words if word in w["t"] and w["y"] > below]
    return min(hits, key=lambda w: w["y"]) if hits else None


legend = find("deep")                    # legend row above the chart (y~1222)
ratio_y = legend["y"] + 300 if legend else H * 0.7
deep = find("deep", below=ratio_y)       # "Sleep ratio" section
light = find("light", below=ratio_y)
rem = find("rem", below=ratio_y)


def value_below(label):
    x, y = label["x"], label["y"] + label["h"] + 5
    return to_minutes(ocr_crop((x, y, x + 400, y + 90), "0123456789 "))


result = {
    "deep_min": value_below(deep) if deep else None,
    "light_min": value_below(light) if light else None,
    "rem_min": value_below(rem) if rem else None,
}

# 2. fall-asleep / wake-up: the two time labels under the chart
ty = legend["y"] - 110 if legend else int(H * 0.47)
result["fell_asleep"] = ocr_crop((40, ty, 300, ty + 60), "0123456789:")
result["woke_up"] = ocr_crop((W - 300, ty, W - 30, ty + 60), "0123456789:")

print(result)
