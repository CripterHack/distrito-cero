#!/usr/bin/env python3
"""Build the braking comparison from synchronized, unmodified street captures."""
import argparse
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory

from PIL import Image, ImageDraw

from compose_market_turn import (BACKGROUND, BOLD, ENDS, MINT, MUTED, REGULAR, WHITE,
                                 check_capture_reports, crop_center, load_pair, read_frame)


TICKS = range(-36, 31, 3)
VERSIONS = ('Antes · v0.20.30', 'Después · v0.20.31')
MARGIN, GAP = 20, 12


def clock(tick):
    sign = '−' if tick < 0 else '+' if tick > 0 else ''
    return (f'{sign}{abs(tick) / 60:.2f} s').replace('.', ',')


def versions(draw, x, y, width):
    for i, (label, color) in enumerate(zip(VERSIONS, (MUTED, MINT))):
        draw.text((x + i * (width + GAP), y), label, font=REGULAR, fill=color)


def video_frame(pair, end, tick):
    width, height = 536, 380
    canvas = Image.new('RGB', (2 * (MARGIN + width) + GAP, 96 + height + MARGIN), BACKGROUND)
    draw = ImageDraw.Draw(canvas)
    draw.text((MARGIN, 12), f'Frenada en el Mercado  /  {ENDS[end]}', font=BOLD, fill=WHITE)
    draw.text((canvas.width - MARGIN, 15), 'Velocidad ×0,75', font=REGULAR, fill=MUTED, anchor='rt')
    versions(draw, MARGIN, 63, width)
    moment = 'Llegada' if tick == 0 else clock(abs(tick)).lstrip('+') + (' antes de llegar' if tick < 0 else ' tras llegar')
    draw.text((canvas.width - MARGIN, 65), moment, font=REGULAR, fill=WHITE, anchor='rt')
    for i, frame in enumerate(pair):
        # Fixed crop from hip to pavement. Both shoes remain in the same camera coordinates.
        bottom, top = round(frame.height * .99), round(frame.height * .35)
        region = crop_center(frame, round((bottom - top) * width / height), top, bottom)
        canvas.paste(region.resize((width, height), Image.Resampling.LANCZOS),
                     (MARGIN + i * (width + GAP), 96))
    return canvas


def contact_sheet(folders, size, ticks):
    width, height = 346, 208
    ticks = tuple(ticks)
    label_width, title_top, row_space = 222, 66, 2 * (height + GAP) + 60
    canvas = Image.new('RGB', (2 * MARGIN + label_width + len(ticks) * (width + GAP) - GAP,
                               title_top + len(ENDS) * row_space + MARGIN), BACKGROUND)
    draw = ImageDraw.Draw(canvas)
    draw.text((MARGIN, 15), 'Frenada del residente  /  Apoyos en la acera', font=BOLD, fill=WHITE)
    for section, (end, label) in enumerate(ENDS.items()):
        top = title_top + section * row_space
        draw.line((MARGIN, top, canvas.width - MARGIN, top), fill='#476257')
        draw.text((MARGIN, top + 14), label, font=BOLD, fill=WHITE)
        for j, tick in enumerate(ticks):
            x = MARGIN + label_width + j * (width + GAP)
            phase = 'Aproximación' if tick < 0 else 'Llegada' if tick == 0 else 'Tras la llegada'
            draw.text((x, top + 17), f'{phase}  ·  {clock(tick)}', font=REGULAR, fill=MUTED)
            for i, frame in enumerate(load_pair(folders, end, tick, size)):
                y = top + 52 + i * (height + GAP)
                if not j:
                    draw.text((MARGIN, y + 9), VERSIONS[i], font=REGULAR, fill=(MUTED, MINT)[i])
                bottom, crop_h = round(frame.height * .99), round(frame.height * .38)
                region = crop_center(frame, round(crop_h * width / height), bottom - crop_h, bottom)
                canvas.paste(region.resize((width, height), Image.Resampling.LANCZOS), (x, y))
    return canvas


def distance_sheet(folders):
    tick = 6
    size = read_frame(folders[0], 'south', tick).size
    width, height = size
    section_h, top = 74 + height, 62
    canvas = Image.new('RGB', (2 * (width + MARGIN) + GAP, top + len(ENDS) * section_h + MARGIN),
                       BACKGROUND)
    draw = ImageDraw.Draw(canvas)
    draw.text((MARGIN, 16), 'Frenada en el Mercado  /  Cámara lejana', font=BOLD, fill=WHITE)
    for section, (end, name) in enumerate(ENDS.items()):
        y = top + section * section_h
        draw.text((MARGIN, y), f'{name}  ·  0,10 s tras llegar', font=BOLD, fill=WHITE)
        versions(draw, MARGIN, y + 35, width)
        for i, frame in enumerate(load_pair(folders, end, tick, size)):
            canvas.paste(frame, (MARGIN + i * (width + GAP), y + 61))
    return canvas


def compose(before, after, output, ticks, far):
    if not (len(ticks) == 3 and ticks[0] < ticks[1] == 0 < ticks[2] and all(t in TICKS for t in ticks)):
        raise ValueError('Choose a captured approach tick, 0 for arrival and a positive settling tick.')
    folders = (before, after)
    for group in (folders, far):
        for folder in group:
            if not (folder / 'measurements.json').is_file():
                raise ValueError('Missing capture report in ' + str(folder))
        check_capture_reports(group)
    size = read_frame(before, 'south', TICKS[0]).size
    output.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=output) as staging:
        stage = Path(staging)
        for section, end in enumerate(ENDS):
            for i, tick in enumerate(TICKS):
                pair = load_pair(folders, end, tick, size)
                video_frame(pair, end, tick).save(stage / f'{section * len(TICKS) + i:03}.png')
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-nostdin',
                        '-framerate', '15', '-i', str(stage / '%03d.png'), '-an', '-c:v', 'libx264',
                        '-threads', '1', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
                        str(stage / 'frenada.mp4')], check=True)
        contact_sheet(folders, size, ticks).save(stage / 'apoyos.jpg', quality=92, optimize=True, subsampling=0)
        distance_sheet(far).save(stage / 'distancia.jpg', quality=90, optimize=True, subsampling=0)
        for name in ('frenada.mp4', 'apoyos.jpg', 'distancia.jpg'):
            (stage / name).replace(output / name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ('before', 'after', 'output'):
        parser.add_argument('--' + key, type=Path, required=True)
    parser.add_argument('--far', nargs=2, type=Path, required=True, metavar=('BEFORE', 'AFTER'))
    parser.add_argument('--ticks', nargs=3, type=int, default=(-15, 0, 12), metavar=('APPROACH', 'ARRIVAL', 'SETTLE'))
    args = parser.parse_args()
    compose(args.before, args.after, args.output, args.ticks, args.far)
