"""Generate anti-aliased Stream Deck assets from the tracker star artwork."""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "streamdeck" / "com.freddogg23.smwstreamtracker.sdPlugin"
STAR_SOURCE = ROOT / "app_assets" / "smw_stream_tracker_icon.png"
SCALE = 4
BACKGROUND = "#2B2A25"
BACKGROUND_ACTIVE = "#375D6C"
WHITE = "#F8FAFC"
BLUE = "#9EE5FF"
YELLOW = "#FFD84A"


def label_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    try:
        return ImageFont.truetype(
            "C:/Windows/Fonts/segoeuib.ttf",
            size * SCALE,
        )
    except OSError:
        return ImageFont.load_default(size=size * SCALE)


def save_pair(image: Image.Image, base: Path, size: int) -> None:
    base.parent.mkdir(parents=True, exist_ok=True)
    image.resize((size, size), Image.Resampling.LANCZOS).save(
        base.with_suffix(".png")
    )
    image.resize((size * 2, size * 2), Image.Resampling.LANCZOS).save(
        base.with_name(base.name + "@2x").with_suffix(".png")
    )


def transparent_star() -> Image.Image:
    source = Image.open(STAR_SOURCE).convert("RGBA")
    pixels = source.load()
    for y in range(source.height):
        for x in range(source.width):
            red, green, blue, alpha = pixels[x, y]
            if red > 175 and green < 95 and blue < 95:
                pixels[x, y] = (red, green, blue, 0)
            else:
                pixels[x, y] = (red, green, blue, alpha)
    return source.getbbox() and source.crop(source.getbbox()) or source


def canvas(active: bool = False) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    size = 72 * SCALE
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle(
        (4 * SCALE, 4 * SCALE, 68 * SCALE, 68 * SCALE),
        radius=13 * SCALE,
        fill=BACKGROUND_ACTIVE if active else BACKGROUND,
        outline="#79DFFF" if active else "#46443D",
        width=2 * SCALE,
    )
    return image, draw


def arrow_head(
    draw: ImageDraw.ImageDraw,
    point: tuple[float, float],
    angle: float,
    color: str,
    length: float = 8,
    width: float = 7,
) -> None:
    px, py = (value * SCALE for value in point)
    angle_radians = math.radians(angle)
    back_x = px - math.cos(angle_radians) * length * SCALE
    back_y = py - math.sin(angle_radians) * length * SCALE
    side_x = math.sin(angle_radians) * width * SCALE / 2
    side_y = -math.cos(angle_radians) * width * SCALE / 2
    draw.polygon(
        [
            (px, py),
            (back_x + side_x, back_y + side_y),
            (back_x - side_x, back_y - side_y),
        ],
        fill=color,
    )


def add_star_mark(image: Image.Image) -> None:
    star = transparent_star().resize(
        (13 * SCALE, 13 * SCALE),
        Image.Resampling.LANCZOS,
    )
    image.alpha_composite(star, (51 * SCALE, 8 * SCALE))


def play_pause(playing: bool) -> Image.Image:
    image, draw = canvas(active=playing)
    color = BLUE if playing else WHITE
    if playing:
        draw.rounded_rectangle(
            (25 * SCALE, 22 * SCALE, 32 * SCALE, 52 * SCALE),
            radius=2 * SCALE,
            fill=color,
        )
        draw.rounded_rectangle(
            (40 * SCALE, 22 * SCALE, 47 * SCALE, 52 * SCALE),
            radius=2 * SCALE,
            fill=color,
        )
    else:
        draw.polygon(
            [
                (26 * SCALE, 19 * SCALE),
                (52 * SCALE, 36 * SCALE),
                (26 * SCALE, 53 * SCALE),
            ],
            fill=color,
        )
    add_star_mark(image)
    return image


def radio_start() -> Image.Image:
    image, draw = canvas(active=True)
    draw.arc(
        (12 * SCALE, 12 * SCALE, 60 * SCALE, 60 * SCALE),
        start=205,
        end=515,
        fill=BLUE,
        width=4 * SCALE,
    )
    draw.arc(
        (20 * SCALE, 20 * SCALE, 52 * SCALE, 52 * SCALE),
        start=205,
        end=515,
        fill="#B9F3FF",
        width=4 * SCALE,
    )
    draw.polygon(
        [
            (30 * SCALE, 24 * SCALE),
            (50 * SCALE, 36 * SCALE),
            (30 * SCALE, 48 * SCALE),
        ],
        fill=WHITE,
    )
    add_star_mark(image)
    return image


def radio_close() -> Image.Image:
    image, draw = canvas()
    draw.rounded_rectangle(
        (16 * SCALE, 17 * SCALE, 56 * SCALE, 55 * SCALE),
        radius=8 * SCALE,
        outline=BLUE,
        width=4 * SCALE,
    )
    draw.line(
        (27 * SCALE, 28 * SCALE, 45 * SCALE, 46 * SCALE),
        fill=WHITE,
        width=6 * SCALE,
    )
    draw.line(
        (45 * SCALE, 28 * SCALE, 27 * SCALE, 46 * SCALE),
        fill=WHITE,
        width=6 * SCALE,
    )
    add_star_mark(image)
    return image


def restart() -> Image.Image:
    image, draw = canvas()
    draw.arc(
        (18 * SCALE, 17 * SCALE, 57 * SCALE, 56 * SCALE),
        start=215,
        end=540,
        fill=WHITE,
        width=6 * SCALE,
    )
    arrow_head(draw, (18, 30), 230, WHITE, length=10, width=10)
    add_star_mark(image)
    return image


def next_track() -> Image.Image:
    image, draw = canvas()
    draw.polygon(
        [
            (20 * SCALE, 20 * SCALE),
            (48 * SCALE, 36 * SCALE),
            (20 * SCALE, 52 * SCALE),
        ],
        fill=WHITE,
    )
    draw.rounded_rectangle(
        (49 * SCALE, 19 * SCALE, 55 * SCALE, 53 * SCALE),
        radius=2 * SCALE,
        fill=BLUE,
    )
    add_star_mark(image)
    return image


def loop(active: bool) -> Image.Image:
    image, draw = canvas(active=active)
    color = BLUE if active else WHITE
    draw.arc(
        (15 * SCALE, 19 * SCALE, 57 * SCALE, 49 * SCALE),
        start=200,
        end=340,
        fill=color,
        width=6 * SCALE,
    )
    draw.arc(
        (15 * SCALE, 23 * SCALE, 57 * SCALE, 53 * SCALE),
        start=20,
        end=160,
        fill=color,
        width=6 * SCALE,
    )
    arrow_head(draw, (56, 29), -18, color, length=9, width=9)
    arrow_head(draw, (16, 43), 162, color, length=9, width=9)
    add_star_mark(image)
    return image


def seek(forward: bool) -> Image.Image:
    image, draw = canvas()
    color = BLUE if forward else WHITE
    if forward:
        draw.arc(
            (14 * SCALE, 17 * SCALE, 58 * SCALE, 57 * SCALE),
            start=210,
            end=520,
            fill=color,
            width=5 * SCALE,
        )
        arrow_head(draw, (58, 31), -25, color, length=9, width=9)
    else:
        draw.arc(
            (14 * SCALE, 17 * SCALE, 58 * SCALE, 57 * SCALE),
            start=20,
            end=330,
            fill=color,
            width=5 * SCALE,
        )
        arrow_head(draw, (14, 31), 205, color, length=9, width=9)
    draw.text(
        (36 * SCALE, 37 * SCALE),
        "10",
        anchor="mm",
        font=label_font(16),
        fill=YELLOW,
        stroke_width=1 * SCALE,
        stroke_fill="#392F00",
    )
    add_star_mark(image)
    return image


def volume(up: bool) -> Image.Image:
    image, draw = canvas()
    draw.polygon(
        [
            (16 * SCALE, 31 * SCALE),
            (25 * SCALE, 31 * SCALE),
            (38 * SCALE, 21 * SCALE),
            (38 * SCALE, 51 * SCALE),
            (25 * SCALE, 41 * SCALE),
            (16 * SCALE, 41 * SCALE),
        ],
        fill=WHITE,
    )
    color = BLUE if up else YELLOW
    draw.rounded_rectangle(
        (46 * SCALE, 33 * SCALE, 61 * SCALE, 39 * SCALE),
        radius=2 * SCALE,
        fill=color,
    )
    if up:
        draw.rounded_rectangle(
            (50.5 * SCALE, 28.5 * SCALE, 56.5 * SCALE, 43.5 * SCALE),
            radius=2 * SCALE,
            fill=color,
        )
    add_star_mark(image)
    return image


def write_action(name: str, states: dict[str, Image.Image]) -> None:
    folder = PLUGIN / "imgs" / "actions" / name
    for filename, image in states.items():
        save_pair(image, folder / filename, 72)
    first_image = next(iter(states.values()))
    save_pair(first_image, folder / "action-icon", 20)


def main() -> None:
    source = Image.open(STAR_SOURCE).convert("RGBA")
    save_pair(source, PLUGIN / "imgs" / "plugin-icon", 256)

    category = Image.new("RGBA", (56 * SCALE, 56 * SCALE), (0, 0, 0, 0))
    star = transparent_star().resize(
        (50 * SCALE, 50 * SCALE),
        Image.Resampling.LANCZOS,
    )
    category.alpha_composite(star, (3 * SCALE, 3 * SCALE))
    save_pair(category, PLUGIN / "imgs" / "category-icon", 28)

    write_action("radio-start", {"key": radio_start()})
    write_action("radio-close", {"key": radio_close()})
    write_action("play-pause", {"play": play_pause(False), "pause": play_pause(True)})
    write_action("restart", {"key": restart()})
    write_action("next", {"key": next_track()})
    write_action("loop", {"off": loop(False), "on": loop(True)})
    write_action("seek-back", {"key": seek(False)})
    write_action("seek-forward", {"key": seek(True)})
    write_action("volume-down", {"key": volume(False)})
    write_action("volume-up", {"key": volume(True)})


if __name__ == "__main__":
    main()
