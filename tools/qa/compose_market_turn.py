#!/usr/bin/env python3
"""Compose a Mercado contact sheet and a synchronized video from native captures.

Requires Pillow, ffmpeg with libx264, and DejaVu Sans. Example:
    python3 tools/qa/compose_market_turn.py --before artifacts/giro/antes \
        --after artifacts/giro/despues --output qa/market-turn-v02030
"""
import argparse
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory

from PIL import Image, ImageDraw, ImageFont


ENDS = {"south": "Extremo sur", "north": "Extremo norte"}
TICKS = range(0, 145, 6)
STAGES = ("Antes · v0.20.29", "Después · v0.20.30")
BACKGROUND, WHITE, MUTED, MINT = "#18211f", "#f4f3ee", "#c6cec9", "#a7e9c5"
REGULAR = ImageFont.truetype("DejaVuSans.ttf", 18)
BOLD = ImageFont.truetype("DejaVuSans-Bold.ttf", 23)


def stamp(tick):
    return f"{tick / 60:.1f} s".replace(".", ",")


def read_frame(folder, end, tick):
    path = folder / f"{end}-{tick:03}.png"
    with Image.open(path) as image:
        if image.format != "PNG":
            raise ValueError(f"Expected a PNG capture: {path}")
        return image.convert("RGB")


def check_capture_reports(folders):
    reports = [folder / "measurements.json" for folder in folders]
    if not any(path.exists() for path in reports):
        return
    before, after = [json.loads(path.read_text()) for path in reports]
    for key in ("seed", "actor", "canvas"):
        if before["environment"][key] != after["environment"][key]:
            raise ValueError(f"The captures differ in {key}")
    for end in ENDS:
        a, b = [report["endpoints"][end] for report in (before, after)]
        for key in ("eye", "target", "dest", "towardEnd", "fov", "quality"):
            if a.get(key) != b.get(key):
                raise ValueError(f"The captures differ in {key} at {end}")


def load_pair(folders, end, tick, size):
    frames = [read_frame(folder, end, tick) for folder in folders]
    if any(frame.size != size for frame in frames):
        raise ValueError(f"Inconsistent capture dimensions at {end}-{tick:03}; expected {size}")
    return frames


def crop_center(image, width, top, bottom):
    left = (image.width - width) // 2
    return image.crop((left, top, left + width, bottom))


def video_frame(pair, end, tick):
    panel = 480
    margin, gutter, heading = 20, 12, 84
    canvas = Image.new("RGB", (2 * margin + 2 * panel + gutter, heading + panel + margin), BACKGROUND)
    draw = ImageDraw.Draw(canvas)
    draw.text((margin, 11), f"Mercado  /  {ENDS[end]}", font=BOLD, fill=WHITE)
    draw.text((canvas.width - margin, 16), f"{stamp(tick)} desde la llegada", anchor="rt",
              font=REGULAR, fill=MUTED)
    for col, frame in enumerate(pair):
        x = margin + col * (panel + gutter)
        draw.text((x, 51), STAGES[col], font=REGULAR, fill=(MUTED, MINT)[col])
        width = min(frame.width, frame.height)
        picture = crop_center(frame, width, 0, frame.height)
        # Preserve the aspect of portrait inputs, even though the native camera is landscape.
        picture.thumbnail((panel, panel), Image.Resampling.LANCZOS)
        canvas.paste(picture, (x + (panel - picture.width) // 2, heading + (panel - picture.height) // 2))
    return canvas


def gallery(folders, ticks, size):
    cell_w, cell_h, margin, gap, label_w = 314, 206, 24, 8, 181
    title_h, section_h = 74, 64 + 2 * (cell_h + gap) + 18
    canvas = Image.new("RGB", (2 * margin + label_w + len(ticks) * (cell_w + gap) - gap,
                                title_h + len(ENDS) * section_h), BACKGROUND)
    draw = ImageDraw.Draw(canvas)
    draw.text((margin, 22), "Mercado  /  Apoyo del calzado durante el giro", font=BOLD, fill=WHITE)
    for number, (end, name) in enumerate(ENDS.items()):
        row = title_h + number * section_h
        draw.line((margin, row, canvas.width - margin, row), fill="#476257")
        draw.text((margin, row + 19), name, font=BOLD, fill=WHITE)
        for col, tick in enumerate(ticks):
            x = margin + label_w + col * (cell_w + gap)
            draw.text((x, row + 21), stamp(tick) + " desde la llegada", font=REGULAR, fill=MUTED)
            for stage, frame in enumerate(load_pair(folders, end, tick, size)):
                y = row + 64 + stage * (cell_h + gap)
                if col == 0:
                    draw.text((margin, y + 10), STAGES[stage], font=REGULAR, fill=(MUTED, MINT)[stage])
                # A fixed lower-body crop at both versions and endpoints keeps shoe motion comparable.
                bottom = round(frame.height * .99)
                height = min(round(frame.height * .42), frame.width * cell_h // cell_w)
                width = round(height * cell_w / cell_h)
                picture = crop_center(frame, width, bottom - height, bottom)
                canvas.paste(picture.resize((cell_w, cell_h), Image.Resampling.LANCZOS), (x, y))
    return canvas


def distance_sheet(folders):
    check_capture_reports(folders)
    tick = 72
    size = read_frame(folders[0], 'south', tick).size
    w, h = size
    canvas = Image.new('RGB', (2*w + 48, 2*h + 138), BACKGROUND)
    draw = ImageDraw.Draw(canvas)
    draw.text((16, 12), 'Mercado  /  Giro desde la cámara lejana', font=BOLD, fill=WHITE)
    for row, (end, name) in enumerate(ENDS.items()):
        y = 48 + row*(h + 42)
        for col, picture in enumerate(load_pair(folders, end, tick, size)):
            x = 16 + col*(w + 16)
            draw.text((x, y), name + '  ·  ' + STAGES[col] + '  ·  ' + stamp(tick),
                      font=REGULAR, fill=(MUTED, MINT)[col])
            canvas.paste(picture, (x, y + 29))
    return canvas


def compose(before, after, output, ticks, far=None):
    folders = (before, after)
    check_capture_reports(folders)
    size = read_frame(before, "north", TICKS[0]).size
    if min(size) < 100:
        raise ValueError(f"Need native frames at least 100 pixels wide and tall; found {size}")
    if any(t not in TICKS for t in ticks) or list(ticks) != sorted(set(ticks)):
        raise ValueError("--ticks must be three increasing captured ticks in 0, 6, …, 144")

    output.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=output) as staging:
        stage = Path(staging)
        # Ten captured instants per second of simulation. Keep the last tick at each stop.
        index = 0
        for end in ENDS:
            for tick in TICKS:
                pair = load_pair(folders, end, tick, size)
                video_frame(pair, end, tick).save(stage / f"{index:03}.png")
                index += 1
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin",
                        "-framerate", "10", "-i", str(stage / "%03d.png"), "-an",
                        "-c:v", "libx264", "-threads", "1", "-crf", "18", "-pix_fmt", "yuv420p",
                        "-movflags", "+faststart", str(stage / "giro.mp4")], check=True)
        gallery(folders, ticks, size).save(stage / "apoyos.jpg", quality=91, optimize=True, subsampling=0)
        names = ['giro.mp4', 'apoyos.jpg']
        if far:
            distance_sheet(far).save(stage / 'distancia.jpg', quality=89, optimize=True, subsampling=0)
            names.append('distancia.jpg')
        for name in names:
            (stage / name).replace(output / name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ("before", "after", "output"):
        parser.add_argument("--" + key, type=Path, required=True)
    parser.add_argument("--ticks", type=int, nargs=3, default=(36, 54, 108),
                        help="Three captured ticks from arrival for the contact sheet (60 ticks/second)")
    parser.add_argument('--far', type=Path, nargs=2, metavar=('BEFORE', 'AFTER'),
                        help='Add a distance contact sheet from the native captures at tick 72')
    args = parser.parse_args()
    compose(args.before, args.after, args.output, args.ticks, args.far)
