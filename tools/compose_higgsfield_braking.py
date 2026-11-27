"""Compose the two contact views emitted by review_higgsfield_motion.py --brake-frames."""

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def compose(frames, destination):
    tile_w, tile_h = 320, 256
    margin, gap, labels = 26, 6, 150
    first_x, first_y = margin + labels, 94
    width = first_x + 5 * tile_w + 4 * gap + margin
    sheet = Image.new("RGB", (width, first_y + 2 * tile_h + gap + margin), "#162127")
    draw = ImageDraw.Draw(sheet)
    title = ImageFont.truetype("DejaVuSans.ttf", 26)
    text = ImageFont.truetype("DejaVuSans.ttf", 19)
    bold = ImageFont.truetype("DejaVuSans-Bold.ttf", 20)
    ink, secondary = "#edf2ef", "#b9c9cd"
    draw.text((margin, 17), "Distrito Cero  /  Frenada del residente del Mercado", fill=ink, font=title)
    for i, time in enumerate(("0,00", "0,12", "0,24", "0,37", "0,49")):
        x = first_x + i * (tile_w + gap)
        draw.text((x, first_y - 30), time + " s", font=text, fill=secondary)
    for row, (name, leg) in enumerate((("FrenadaL", "izquierdo"), ("FrenadaR", "derecho"))):
        y = first_y + row * (tile_h + gap)
        draw.text((margin, y + tile_h // 2 - 31), "Apoyo", font=text, fill=secondary)
        draw.text((margin, y + tile_h // 2 - 4), leg, font=bold, fill=ink)
        for i in range(5):
            with Image.open(frames / f"{name}-apoyo-{i}.png") as image:
                assert image.size == (400, 320), (name, i, image.size)
                sheet.paste(image.convert("RGB").resize((tile_w, tile_h), Image.Resampling.LANCZOS),
                            (first_x + i * (tile_w + gap), y))
    sheet.save(destination, quality=94, subsampling=0, optimize=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("frames", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    compose(args.frames, args.destination)
