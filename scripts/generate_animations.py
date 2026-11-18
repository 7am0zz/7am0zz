"""Generate the profile GIFs with Pillow 13 and the DejaVu Sans fonts.

Run: python scripts/generate_animations.py
Pass --font-dir if the DejaVu fonts are installed in a different location.
"""

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

DESTINATION = Path(__file__).resolve().parents[1] / "assets" / "animations"
BLUE = (105, 192, 255)
ICE = (175, 219, 255)
VIOLET = (173, 138, 255)
TRACE = (30, 49, 83)
DIM = (54, 101, 162)
WHITE = (242, 247, 255)
NAVY = (6, 11, 25)
TOPICS = (
    "Artificial Intelligence", "Machine Learning", "Software Engineering",
    "Cybersecurity", "Cloud Computing", "Data Science", "Algorithms",
)


def mix(color, amount):
    amount = max(0, min(amount, 1))
    return tuple(round(base + (channel - base) * amount)
                 for base, channel in zip(NAVY, color))


def wave(phase):
    return (1 - math.cos(math.tau * phase)) / 2


def tracked(draw, x, y, label, font, color, spacing):
    for character in label:
        draw.text((x, y), character, font=font, fill=color, anchor="lt")
        x += font.getlength(character) + spacing


def hero_frames(font_dir, animations):
    title = ImageFont.truetype(str(font_dir / "DejaVuSans-Bold.ttf"), 37)
    subtitle = ImageFont.truetype(str(font_dir / "DejaVuSans.ttf"), 29)
    topic = ImageFont.truetype(str(font_dir / "DejaVuSansMono.ttf"), 25)
    name = ImageFont.truetype(str(font_dir / "DejaVuSans-Bold.ttf"), 32)
    base = Image.new("RGB", (1200, 360), NAVY)
    draw = ImageDraw.Draw(base)
    for x in range(24, 1200, 24):
        for y in range(24, 350, 24):
            draw.point((x, y), fill=(19, 31, 54))
    draw.rectangle((15, 15, 1184, 344), outline=TRACE)
    for x, sign in ((15, 1), (1184, -1)):
        for y, direction in ((15, 1), (344, -1)):
            draw.line((x + sign * 30, y, x, y, x, y + direction * 20), fill=DIM)

    # A directed graph with parallel paths and a shared output.
    points = ((768, 65), (825, 42), (825, 88), (902, 65), (967, 38),
              (967, 89), (1031, 65), (1105, 65))
    links = ((0, 1), (0, 2), (1, 3), (2, 3), (3, 4),
             (3, 5), (4, 6), (5, 6), (6, 7))
    edges = [(points[a], points[b]) for a, b in links]
    for start, end in edges:
        draw.line((start, end), fill=DIM, width=2)
    for index, (x, y) in enumerate(points):
        color = VIOLET if index in (0, len(points)-1) else BLUE
        draw.ellipse((x-5, y-5, x+5, y+5), fill=NAVY, outline=color, width=2)

    draw.rounded_rectangle((75, 36, 390, 89), 7, fill=NAVY, outline=TRACE)
    draw.line((87, 50, 87, 75), fill=VIOLET, width=3)
    draw.text((100, 50), "Mohamed Said", fill=WHITE, font=name, anchor="lt")
    tracked(draw, 82, 112, "COMPUTER SCIENCE | SOFTWARE ENGINEERING",
            title, WHITE, 1.1)
    draw.text((82, 164), "Building Intelligent Systems & Scalable Software",
              fill=ICE, font=subtitle, anchor="lt")

    tile_size = 104
    tile_x = [82 + index * 155 for index in range(len(animations))]
    tiles = [
        [frame.resize((tile_size, tile_size), Image.Resampling.LANCZOS)
         for frame in icon_frames(illustration)]
        for _, illustration in animations
    ]
    draw.line((tile_x[0], 284, tile_x[-1] + tile_size, 284), fill=TRACE, width=2)
    frame_count = 30 * len(TOPICS)
    for frame in range(frame_count):
        phase = frame / frame_count
        image = base.copy()
        draw = ImageDraw.Draw(image)
        for index, (start, end) in enumerate(edges):
            signal(draw, start, end, (phase * 3 - index * .14) % 1, BLUE)

        active, step = divmod(frame, 30)
        label = TOPICS[active]
        fade = min(1, (step+2)/5, (30-step+1)/5)
        draw.text((82, 208), "> " + label, fill=mix(BLUE, fade), font=topic, anchor="lt")
        cursor = 91 + round(topic.getlength("> " + label))
        draw.rectangle((cursor, 208, cursor+11, 225),
                       fill=mix(VIOLET, fade * (.24 + .76 * wave(step/15))))
        for index, (x, frames) in enumerate(zip(tile_x, tiles)):
            tile_frame = (int(phase * 4 * len(frames)) + index * 5) % len(frames)
            image.paste(frames[tile_frame], (x, 233))
            if index == active:
                draw.rounded_rectangle((x+6, 239, x+97, 330), 5,
                                       outline=mix(VIOLET, .55 + .45 * fade), width=2)
        yield image


def node(draw, x, y, color=ICE, radius=3):
    draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=color)


def signal(draw, start, end, phase, color=VIOLET):
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
            node(draw, x, y, mix(ICE, .50 + .50 * wave(phase - x / 145)))


def terminal(draw, phase):
    draw.rounded_rectangle((28, 43, 132, 116), 5, outline=DIM, width=2)
    draw.line((29, 59, 131, 59), fill=TRACE)
    for x in (38, 45, 52):
        node(draw, x, 51, DIM, 1)
    for index, length in enumerate((47, 64, 37)):
        y = 74 + index * 13
        extent = round(length * (.62 + .38 * wave(phase - index * .14)))
        draw.line((53, y, 53+extent, y), fill=BLUE if index == 0 else DIM, width=2)
        draw.line([(38, y-3), (42, y), (38, y+3)], fill=VIOLET)
        if index == 2:
            draw.rectangle((57+extent, y-3, 62+extent, y+3),
                           fill=mix(ICE, .18 + .82 * wave(phase * 2)))


def shield(draw, phase):
    outline = [(80, 34), (115, 48), (111, 86), (101, 105), (80, 124),
               (59, 105), (49, 86), (45, 48)]
    draw.polygon(outline, fill=(12, 23, 48), outline=DIM, width=2)
    draw.line([(69, 80), (77, 88), (93, 70)], fill=ICE, width=2)
    for points in ([(24, 64), (36, 64), (47, 74)], [(136, 64), (124, 64), (113, 74)],
                   [(25, 102), (40, 102), (51, 92)], [(135, 102), (120, 102), (109, 92)]):
        draw.line(points, fill=TRACE)
        node(draw, *points[0], DIM, 2)
    y = 52 + round(52 * wave(phase))
    half_width = round(27 - max(y-83, 0) * .48)
    draw.line((80-half_width, y, 80+half_width, y), fill=VIOLET)


def cloud(draw, phase):
    outline = [(48, 76), (42, 71), (40, 64), (43, 56), (50, 51), (58, 51),
               (64, 41), (75, 36), (87, 37), (97, 44), (101, 53), (110, 53),
               (118, 58), (121, 66), (118, 73), (112, 76), (48, 76)]
    draw.line(outline, fill=ICE, width=2, joint="curve")
    draw.line((80, 76, 80, 106), fill=DIM)
    draw.line((45, 106, 45, 94, 115, 94, 115, 106), fill=DIM)
    for index, x in enumerate((45, 80, 115)):
        draw.rounded_rectangle((x-11, 106, x+11, 122), 2, outline=DIM)
        draw.line((x-5, 114, x+1, 114), fill=TRACE)
        node(draw, x+5, 114, mix(BLUE, .25 + .75 * wave(phase-index / 3)), 1)
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
    draw.line(points, fill=VIOLET, width=2)
    for x, y in points:
        node(draw, x, y, ICE, 2)


def algorithm(draw, phase):
    positions = [(x, 78) for x in (34, 54, 80, 106, 126)] + [(80, 48), (80, 108)]
    edges = [(0, 1), (1, 2), (2, 3), (3, 4), (2, 5), (2, 6)]
    for a, b in edges:
        draw.line((positions[a], positions[b]), fill=DIM)
    traversal = (0, 1, 2, 5, 2, 3, 4, 3, 2, 6, 2, 1, 0)
    step = phase * (len(traversal)-1)
    index = int(step)
    for i, (x, y) in enumerate(positions):
        draw.ellipse((x-5, y-5, x+5, y+5), fill=NAVY,
                     outline=ICE if i == traversal[index] else DIM)
    signal(draw, positions[traversal[index]], positions[traversal[index+1]], step % 1)


def training(draw, phase):
    layer = [(38, y) for y in (51, 69, 87, 105)]
    hidden = [(61, y) for y in (62, 80, 98)]
    for a in layer:
        for b in hidden:
            draw.line((a, b), fill=TRACE)
    for x, y in layer + hidden:
        node(draw, x, y, mix(ICE, .48 + .52 * wave(phase - x / 121)), 2)
    draw.line((76, 48, 76, 113, 132, 113), fill=DIM)
    curve = [(x, round(57 + 47 * math.exp(-(x-78)/13))) for x in range(78, 132)]
    draw.line(curve, fill=TRACE, width=2)
    progress = 1 - (1-phase)**3
    end = 1 + round(progress * (len(curve)-1))
    color = mix(VIOLET, min(1, (1-phase)*9))
    draw.line(curve[:end], fill=color, width=2)
    node(draw, *curve[end-1], color, 2)


def icon_frames(illustration):
    base = Image.new("RGB", (160, 160), NAVY)
    draw = ImageDraw.Draw(base)
    draw.rounded_rectangle((10, 10, 149, 149), 8, outline=TRACE)
    for x in range(20, 150, 10):
        for y in range(20, 150, 10):
            draw.point((x, y), fill=(15, 26, 50))
    draw.line((20, 21, 32, 21), fill=DIM)
    draw.line((127, 138, 139, 138), fill=DIM)
    for frame in range(48):
        image = base.copy()
        illustration(ImageDraw.Draw(image), frame / 48)
        yield image


def save_gif(name, frames, duration):
    palette = Image.new("P", (1, 1))
    colors = [NAVY]
    for color in (BLUE, ICE, VIOLET, WHITE, TRACE, DIM):
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
    animations = (
        ("artificial-intelligence", neural_network),
        ("machine-learning", training),
        ("software-engineering", terminal),
        ("cybersecurity", shield),
        ("cloud-computing", cloud),
        ("data-science", analytics),
        ("algorithms", algorithm),
    )
    save_gif("network-hero", hero_frames(options.font_dir, animations), 60)
    for name, illustration in animations:
        save_gif(name, icon_frames(illustration), 70)


if __name__ == "__main__":
    main()
