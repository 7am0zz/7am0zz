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


def draw_orbital_core(draw, phase):
    angle = math.tau * phase
    center_x = 920 + 15 * math.cos(angle)
    center_y = 164 + 10 * math.sin(2 * angle)

    def project(point):
        x, y, z = point
        scale = 380 / (380 - z)
        return round(center_x + x * scale), round(center_y + y * scale)

    def orbit(turn, radius, tilt, twist):
        x = radius * math.cos(turn)
        y = radius * math.sin(turn) * math.cos(tilt)
        z = radius * math.sin(turn) * math.sin(tilt)
        return (x * math.cos(twist) - y * math.sin(twist),
                x * math.sin(twist) + y * math.cos(twist), z)

    rear, front = [], []
    for index, (radius, tilt, twist, color) in enumerate((
        (98, 1.17, -.52, BLUE), (130, 1.24, .45, VIOLET), (158, .98, -.18, ICE),
    )):
        twist += .14 * math.sin(angle + index)
        vertices = [orbit(math.tau * step / 84, radius, tilt, twist) for step in range(85)]
        for a, b in zip(vertices, vertices[1:]):
            layer = front if a[2] + b[2] >= 0 else rear
            shade = .38 + .35 * max(0, a[2] / radius)
            layer.append((project(a), project(b), mix(color, shade), 2))
        for tail in range(17):
            turn = angle * (index + 1) + 1.7 * index - tail * .034
            a = orbit(turn, radius, tilt, twist)
            b = orbit(turn - .037, radius, tilt, twist)
            layer = front if a[2] + b[2] >= 0 else rear
            layer.append((project(a), project(b), mix(color, 1 - tail / 20),
                          4 if tail < 5 else 2))
        head = orbit(angle * (index + 1) + 1.7 * index, radius, tilt, twist)
        spot = project(head)
        (front if head[2] >= 0 else rear).append((spot, spot, WHITE, 5))

    for a, b, color, width in rear:
        draw.line((a, b), fill=color, width=width)
        if a == b:
            node(draw, *a, color, 3)

    # Rotate and project a faceted octahedron with a fixed light source.
    rotation = angle * 2 + .47
    vertices = [(x * math.cos(rotation) - z * math.sin(rotation),
                 y + z * .19,
                 x * math.sin(rotation) + z * math.cos(rotation))
                for x, y, z in ((0, -72, 0), (0, 72, 0), (54, 0, 0),
                                (0, 0, 54), (-54, 0, 0), (0, 0, -54))]
    faces = [(tip, side, next_side)
             for tip in (0, 1) for side, next_side in ((2, 3), (3, 4), (4, 5), (5, 2))]
    faces.sort(key=lambda face: sum(vertices[i][2] for i in face))
    for tip, a, b in faces:
        light = (vertices[a][2] + vertices[b][2] - vertices[a][0]) / 160
        color = BLUE if tip == 0 else VIOLET
        triangle = [project(vertices[i]) for i in (tip, a, b)]
        draw.polygon(triangle, fill=mix(color, .32 + .35 * light),
                     outline=mix(color, .62 + .33 * light), width=2)

    for a, b, color, width in front:
        draw.line((a, b), fill=color, width=width)
        if a == b:
            node(draw, *a, color, 3)


def hero_frames(font_dir):
    title = ImageFont.truetype(str(font_dir / "DejaVuSans-Bold.ttf"), 47)
    subtitle = ImageFont.truetype(str(font_dir / "DejaVuSans.ttf"), 25)
    topic = ImageFont.truetype(str(font_dir / "DejaVuSansMono.ttf"), 20)
    name = ImageFont.truetype(str(font_dir / "DejaVuSans-Bold.ttf"), 29)
    base = Image.new("RGB", (1200, 360), NAVY)
    draw = ImageDraw.Draw(base)
    for radius in range(243, 1, -3):
        shade = .16 * (1 - radius / 246) ** 2
        draw.ellipse((925-radius, 165-radius, 925+radius, 165+radius),
                     fill=mix(VIOLET, shade))
    for x in range(662, 1160, 22):
        for y in range(37, 264, 22):
            draw.point((x, y), fill=mix(BLUE, .17))
    draw.rectangle((16, 16, 1183, 343), outline=TRACE)
    for x, sign in ((16, 1), (1183, -1)):
        for y, direction in ((16, 1), (343, -1)):
            draw.line((x + sign * 36, y, x, y, x, y + direction * 23), fill=DIM, width=2)

    for x in range(671, 1180, 58):
        upper = round(917 + (x-917) * .33)
        draw.line((upper, 251, x, 330), fill=mix(BLUE, .19))
    for y in (251, 261, 275, 294, 319):
        spread = 82 + (y-251) * 2
        draw.line((917-spread, y, 917+spread, y), fill=mix(BLUE, .16))

    draw.line((66, 48, 66, 75), fill=VIOLET, width=3)
    draw.text((82, 50), "Mohamed Said", fill=WHITE, font=name, anchor="lt")
    draw.text((64, 114), "Computer Science", fill=WHITE, font=title, anchor="lt")
    draw.text((64, 169), "Software Engineering", fill=ICE, font=title, anchor="lt")
    draw.text((66, 233), "Building Intelligent Systems & Scalable Software",
              fill=ICE, font=subtitle, anchor="lt")
    draw.line((66, 272, 147, 272), fill=TRACE, width=2)

    frame_count = 30 * len(TOPICS)
    for frame in range(frame_count):
        phase = frame / frame_count
        image = base.copy()
        draw = ImageDraw.Draw(image)
        draw_orbital_core(draw, phase)
        index, step = divmod(frame, 30)
        label = TOPICS[index]
        fade = min(1, (step+2)/5, (31-step)/5)
        draw.text((66, 293), "> " + label, fill=mix(BLUE, fade), font=topic, anchor="lt")
        cursor = 75 + round(topic.getlength("> " + label))
        draw.rectangle((cursor, 293, cursor+8, 307),
                       fill=mix(VIOLET, fade * (.24 + .76 * wave(step/15))))
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
    save_gif("orbital-hero", hero_frames(options.font_dir), 60)
    for name, illustration in animations:
        save_gif(name, icon_frames(illustration), 70)


if __name__ == "__main__":
    main()
