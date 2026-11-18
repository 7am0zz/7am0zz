"""Generate the profile GIFs with Pillow 13 and the DejaVu Sans fonts.

Run: python scripts/generate_animations.py
Pass --font-dir if the DejaVu fonts are installed in a different location.
"""

import argparse
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

DESTINATION = Path(__file__).resolve().parents[1] / "assets" / "animations"
GREEN = (0, 255, 65)
MINT = (137, 254, 184)
CYAN = (67, 202, 190)
TRACE = (14, 66, 42)
DIM = (10, 126, 68)
WHITE = (229, 249, 237)
BLACK = (0, 0, 0)
TOPICS = (
    "Artificial Intelligence", "Machine Learning", "Software Engineering",
    "Cybersecurity", "Cloud Computing", "Data Science",
)


def mix(color, amount):
    return tuple(round(channel * max(0, min(amount, 1))) for channel in color)


def wave(phase):
    return (1 - math.cos(math.tau * phase)) / 2


def tracked(draw, x, y, label, font, color, spacing):
    for character in label:
        draw.text((x, y), character, font=font, fill=color, anchor="lt")
        x += font.getlength(character) + spacing


def hero_frames(font_dir):
    mono = ImageFont.truetype(str(font_dir / "DejaVuSansMono.ttf"), 15)
    title = ImageFont.truetype(str(font_dir / "DejaVuSans-Bold.ttf"), 37)
    subtitle = ImageFont.truetype(str(font_dir / "DejaVuSans.ttf"), 29)
    topic = ImageFont.truetype(str(font_dir / "DejaVuSansMono.ttf"), 25)
    width, height = 1200, 344
    base = Image.new("RGB", (width, height), BLACK)
    draw = ImageDraw.Draw(base)
    for x in range(24, width, 24):
        for y in range(24, height, 24):
            draw.point((x, y), fill=(11, 33, 23))
    draw.rectangle((15, 15, 1184, 328), outline=(11, 40, 26))
    for x, sign in ((15, 1), (1184, -1)):
        for y, direction in ((15, 1), (328, -1)):
            draw.line((x + sign * 30, y, x, y, x, y + direction * 20), fill=DIM)
    for path in (
        [(15, 72), (135, 72), (161, 98), (230, 98)],
        [(15, 291), (153, 291), (175, 269), (301, 269)],
        [(1184, 63), (1060, 63), (1040, 83), (944, 83)],
        [(1184, 278), (1074, 278), (1054, 258), (958, 258)],
    ):
        draw.line(path, fill=TRACE)
        x, y = path[-1]
        draw.ellipse((x-2, y-2, x+2, y+2), outline=DIM)
    rng = random.Random(41)
    streams = [
        (x, rng.randrange(384), rng.choice((1, 2)), rng.choices("01", k=12))
        for x in range(35, 1180, 21)
    ]
    particles = [(rng.randrange(35, 1165), rng.randrange(28, 316)) for _ in range(30)]
    for frame in range(180):
        phase = frame / 180
        image = base.copy()
        draw = ImageDraw.Draw(image)
        for x, offset, speed, digits in streams:
            head = (offset + 384 * speed * phase) % 384
            side = max(0, (abs(x - 600) - 250) / 330)
            for index, digit in enumerate(digits):
                y = int((head - 17 * index) % 384) - 20
                if 16 <= y <= 310:
                    edge = side * max(0, min(1, (y-16)/18, (310-y)/18))
                    intensity = (0.14 + 0.43 * edge) * (1 - index / len(digits))
                    if 105 < y < 247:
                        intensity *= 0.15 + 0.85 * side
                    draw.text((x, y), digit, fill=mix(GREEN, intensity), font=mono)
        for index, (x, y) in enumerate(particles):
            shift = round(6 * math.sin(math.tau * (phase + index / len(particles))))
            draw.point((x + shift, y), fill=mix(CYAN, .20 + .38 * wave(phase + index / 11)))
        draw.line((82, 110, 121, 110), fill=GREEN, width=2)
        tracked(draw, 82, 132, "COMPUTER SCIENCE | SOFTWARE ENGINEERING",
                title, WHITE, 1.1)
        draw.text((82, 190), "Building Intelligent Systems & Scalable Software",
                  fill=MINT, font=subtitle, anchor="lt")
        topic_index, step = divmod(frame, 30)
        label = TOPICS[topic_index]
        fade = min(1, (step+2)/5, (30-step+1)/5)
        draw.text((82, 251), "> " + label, fill=mix(GREEN, fade), font=topic, anchor="lt")
        cursor = 91 + round(topic.getlength("> " + label))
        draw.rectangle((cursor, 251, cursor+11, 269),
                       fill=mix(CYAN, fade * (.24 + .76 * wave(step/15))))
        for index in range(len(TOPICS)):
            x = 82 + 22 * index
            draw.line((x, 301, x+14, 301), fill=GREEN if index == topic_index else TRACE, width=2)
        yield image


def node(draw, x, y, color=MINT, radius=3):
    draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=color)


def signal(draw, start, end, phase, color=CYAN):
    x, y = (round(a + (b-a) * phase) for a, b in zip(start, end))
    brightness = math.sin(math.pi * phase)
    node(draw, x, y, mix(color, brightness), 2)


def neural_network(draw, phase):
    columns = [[(37, y) for y in (55, 80, 105)],
               [(80, y) for y in (44, 68, 92, 116)],
               [(123, y) for y in (62, 98)]]
    edges = [(a, b) for first, second in zip(columns, columns[1:])
             for a in first for b in second]
    for a, b in edges:
        draw.line((a, b), fill=TRACE)
    for index, (a, b) in enumerate(edges):
        if index % 3 == 0:
            signal(draw, a, b, (phase + index / 21) % 1)
    for column in columns:
        for x, y in column:
            node(draw, x, y, mix(MINT, .50 + .50 * wave(phase - x / 145)))


def terminal(draw, phase):
    draw.rounded_rectangle((28, 43, 132, 116), 5, outline=DIM, width=2)
    draw.line((29, 59, 131, 59), fill=TRACE)
    for x in (38, 45, 52):
        node(draw, x, 51, DIM, 1)
    for index, length in enumerate((47, 64, 37)):
        y = 74 + index * 13
        extent = round(length * (.62 + .38 * wave(phase - index * .14)))
        draw.line((53, y, 53+extent, y), fill=GREEN if index == 0 else DIM, width=2)
        draw.line([(38, y-3), (42, y), (38, y+3)], fill=CYAN)
        if index == 2:
            draw.rectangle((57+extent, y-3, 62+extent, y+3),
                           fill=mix(MINT, .18 + .82 * wave(phase * 2)))


def shield(draw, phase):
    outline = [(80, 34), (115, 48), (111, 86), (101, 105), (80, 124),
               (59, 105), (49, 86), (45, 48)]
    draw.polygon(outline, fill=(2, 18, 10), outline=DIM, width=2)
    draw.line([(69, 80), (77, 88), (93, 70)], fill=MINT, width=2)
    for points in ([(24, 64), (36, 64), (47, 74)], [(136, 64), (124, 64), (113, 74)],
                   [(25, 102), (40, 102), (51, 92)], [(135, 102), (120, 102), (109, 92)]):
        draw.line(points, fill=TRACE)
        node(draw, *points[0], DIM, 2)
    y = 52 + round(52 * wave(phase))
    half_width = round(27 - max(y-83, 0) * .48)
    draw.line((80-half_width, y, 80+half_width, y), fill=CYAN)


def cloud(draw, phase):
    outline = [(48, 76), (42, 71), (40, 64), (43, 56), (50, 51), (58, 51),
               (64, 41), (75, 36), (87, 37), (97, 44), (101, 53), (110, 53),
               (118, 58), (121, 66), (118, 73), (112, 76), (48, 76)]
    draw.line(outline, fill=MINT, width=2, joint="curve")
    draw.line((80, 76, 80, 106), fill=DIM)
    draw.line((45, 106, 45, 94, 115, 94, 115, 106), fill=DIM)
    for index, x in enumerate((45, 80, 115)):
        draw.rounded_rectangle((x-11, 106, x+11, 122), 2, outline=DIM)
        draw.line((x-5, 114, x+1, 114), fill=TRACE)
        node(draw, x+5, 114, mix(GREEN, .25 + .75 * wave(phase-index / 3)), 1)
        signal(draw, (80, 94), (x, 94), (phase + index / 3) % 1)


def analytics(draw, phase):
    draw.line((33, 41, 33, 117, 130, 117), fill=DIM)
    for y in (52, 71, 90):
        draw.line((34, y, 127, y), fill=TRACE)
    points = []
    for index, baseline in enumerate((19, 32, 26, 46, 53)):
        x = 45 + 17 * index
        y = 116 - baseline - round(9 * wave(phase-index*.16))
        draw.rectangle((x-4, y, x+4, 116), fill=TRACE, outline=DIM)
        points.append((x, y-10))
    draw.line(points, fill=CYAN, width=2)
    for x, y in points:
        node(draw, x, y, MINT, 2)


def algorithm(draw, phase):
    positions = [(x, 78) for x in (34, 54, 80, 106, 126)] + [(80, 48), (80, 108)]
    edges = [(0, 1), (1, 2), (2, 3), (3, 4), (2, 5), (2, 6)]
    for a, b in edges:
        draw.line((positions[a], positions[b]), fill=DIM)
    traversal = (0, 1, 2, 5, 2, 3, 4, 3, 2, 6, 2, 1, 0)
    step = phase * (len(traversal)-1)
    index = int(step)
    for i, (x, y) in enumerate(positions):
        draw.ellipse((x-5, y-5, x+5, y+5), fill=BLACK,
                     outline=MINT if i == traversal[index] else DIM)
    signal(draw, positions[traversal[index]], positions[traversal[index+1]], step % 1)


def training(draw, phase):
    layer = [(38, y) for y in (51, 69, 87, 105)]
    hidden = [(61, y) for y in (62, 80, 98)]
    for a in layer:
        for b in hidden:
            draw.line((a, b), fill=TRACE)
    for x, y in layer + hidden:
        node(draw, x, y, mix(MINT, .48 + .52 * wave(phase - x / 121)), 2)
    draw.line((76, 48, 76, 113, 132, 113), fill=DIM)
    curve = [(x, round(57 + 47 * math.exp(-(x-78)/13))) for x in range(78, 132)]
    draw.line(curve, fill=TRACE, width=2)
    progress = 1 - (1-phase)**3
    end = 1 + round(progress * (len(curve)-1))
    color = mix(CYAN, min(1, (1-phase)*9))
    draw.line(curve[:end], fill=color, width=2)
    node(draw, *curve[end-1], color, 2)


def icon_frames(illustration):
    base = Image.new("RGB", (160, 160), BLACK)
    draw = ImageDraw.Draw(base)
    draw.rounded_rectangle((10, 10, 149, 149), 8, outline=TRACE)
    for x in range(20, 150, 10):
        for y in range(20, 150, 10):
            draw.point((x, y), fill=(8, 29, 18))
    draw.line((20, 21, 32, 21), fill=DIM)
    draw.line((127, 138, 139, 138), fill=DIM)
    for frame in range(48):
        image = base.copy()
        illustration(ImageDraw.Draw(image), frame / 48)
        yield image


def save_gif(name, frames, duration):
    palette = Image.new("P", (1, 1))
    colors = [BLACK]
    for color in (GREEN, MINT, CYAN, WHITE, TRACE, DIM):
        colors.extend(mix(color, step / 42) for step in range(1, 43))
    palette.putpalette([channel for color in colors for channel in color])
    images = (frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in frames)
    first = next(images)
    first.save(DESTINATION / (name + ".gif"), save_all=True, append_images=images,
               duration=duration, loop=0, disposal=1, optimize=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font-dir", type=Path,
                        default=Path("/usr/share/fonts/truetype/dejavu"))
    options = parser.parse_args()
    DESTINATION.mkdir(parents=True, exist_ok=True)
    save_gif("matrix-hero", hero_frames(options.font_dir), 60)
    for name, illustration in (
        ("artificial-intelligence", neural_network),
        ("software-engineering", terminal),
        ("cybersecurity", shield),
        ("cloud-computing", cloud),
        ("data-science", analytics),
        ("algorithms", algorithm),
        ("machine-learning", training),
    ):
        save_gif(name, icon_frames(illustration), 70)


if __name__ == "__main__":
    main()
