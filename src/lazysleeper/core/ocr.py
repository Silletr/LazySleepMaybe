from collections import defaultdict
import pytesseract
from PIL import Image

img = Image.open("test.png")

data = pytesseract.image_to_data(
    img, config="--psm 11", output_type=pytesseract.Output.DICT
)

lines = defaultdict(list)

for i, text in enumerate(data["text"]):
    text = text.strip()

    if not text:
        continue

    key = (
        data["block_num"][i],
        data["par_num"][i],
        data["line_num"][i],
    )

    lines[key].append(i)

for indexes in lines.values():
    indexes.sort(key=lambda i: data["left"][i])

    full_text = " ".join(data["text"][i].strip() for i in indexes)

    x1 = min(data["left"][i] for i in indexes)
    y1 = min(data["top"][i] for i in indexes)

    x2 = max(data["left"][i] + data["width"][i] for i in indexes)
    y2 = max(data["top"][i] + data["height"][i] for i in indexes)

    print(f"Text: {full_text!r} | X: {x1}, Y: {y1}, W: {x2 - x1}, H: {y2 - y1}")
