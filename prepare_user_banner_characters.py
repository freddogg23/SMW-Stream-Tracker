from __future__ import annotations

import argparse
from collections import deque
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter


PROJECT_DIRECTORY = Path(__file__).resolve().parent
DEFAULT_SOURCE_DIRECTORY = PROJECT_DIRECTORY / "banner_character_sources"
DEFAULT_OUTPUT_DIRECTORY = PROJECT_DIRECTORY / "banner_character_assets_user"


def normalized_name(path: Path) -> str:
    return path.stem.lower().replace(" ", "_") + ".png"


def is_light_neutral(pixel: tuple[int, int, int, int]) -> bool:
    red, green, blue, alpha = pixel
    return (
        alpha > 0
        and min(red, green, blue) >= 178
        and max(red, green, blue) - min(red, green, blue) <= 24
    )


def remove_edge_checkerboard(
    image: Image.Image,
    subject_name: str,
) -> Image.Image:
    rgba = image.convert("RGBA")
    width, height = rgba.size
    pixels = list(rgba.getdata())
    background = bytearray(width * height)
    queue: deque[int] = deque()
    preserve_white_subject = subject_name in {
        "bowser_jr",
        "piranha",
    }

    def is_background_pixel(
        pixel: tuple[int, int, int, int],
    ) -> bool:
        if not preserve_white_subject:
            return is_light_neutral(pixel)
        red, green, blue, alpha = pixel
        darkest = min(red, green, blue)
        lightest = max(red, green, blue)
        return (
            alpha > 0
            and lightest - darkest <= 3
            and (
                236 <= darkest <= 242
                or darkest >= 252
            )
        )

    def add_seed(x: int, y: int) -> None:
        index = y * width + x
        if (
            background[index]
            or not is_background_pixel(pixels[index])
        ):
            return
        background[index] = 1
        queue.append(index)

    for x in range(width):
        add_seed(x, 0)
        add_seed(x, height - 1)
    for y in range(height):
        add_seed(0, y)
        add_seed(width - 1, y)

    while queue:
        index = queue.popleft()
        x = index % width
        y = index // width
        for neighbor_x, neighbor_y in (
            (x - 1, y),
            (x + 1, y),
            (x, y - 1),
            (x, y + 1),
        ):
            if (
                neighbor_x < 0
                or neighbor_x >= width
                or neighbor_y < 0
                or neighbor_y >= height
            ):
                continue
            neighbor_index = neighbor_y * width + neighbor_x
            if background[neighbor_index]:
                continue
            if is_background_pixel(pixels[neighbor_index]):
                background[neighbor_index] = 1
                queue.append(neighbor_index)

    alpha_mask = Image.new("L", (width, height), 255)
    alpha_mask.putdata(
        [0 if is_background else pixels[index][3]
         for index, is_background in enumerate(background)]
    )
    if preserve_white_subject:
        alpha_mask = alpha_mask.filter(
            ImageFilter.GaussianBlur(0.32)
        )
    else:
        alpha_mask = alpha_mask.filter(
            ImageFilter.MedianFilter(3)
        ).filter(
            ImageFilter.GaussianBlur(0.55)
        )

    # White mushroom caps can touch the checkerboard's white cells. Restore
    # only their safely inset interiors so their supplied artwork remains
    # intact without bringing the checkerboard back around the silhouette.
    restore_mask = Image.new("L", (width, height), 0)
    restore_draw = ImageDraw.Draw(restore_mask)
    if subject_name == "toad":
        restore_draw.ellipse(
            (292, 52, 600, 318),
            fill=255,
        )
        restore_draw.ellipse(
            (337, 427, 506, 541),
            fill=255,
        )
    elif subject_name == "green_toad":
        restore_draw.ellipse(
            (142, 55, 602, 445),
            fill=255,
        )
        restore_draw.ellipse(
            (247, 593, 485, 744),
            fill=255,
        )
    alpha_mask = ImageChops.lighter(
        alpha_mask,
        restore_mask.filter(ImageFilter.GaussianBlur(0.45)),
    )
    rgba.putalpha(alpha_mask)

    bounds = rgba.getbbox()
    if bounds is None:
        return rgba
    left, top, right, bottom = bounds
    padding = max(4, round(max(width, height) * 0.008))
    return rgba.crop(
        (
            max(0, left - padding),
            max(0, top - padding),
            min(width, right + padding),
            min(height, bottom + padding),
        )
    )


def restore_clean_whites(
    image: Image.Image,
    subject_name: str,
) -> Image.Image:
    """Brighten neutral artwork whites without flattening colored shading."""
    restored = image.convert("RGBA")
    corrected_pixels = []
    if subject_name == "piranha":
        minimum_brightness = 115
        maximum_spread = 100
        white_strength = 0.92
    else:
        minimum_brightness = 145
        maximum_spread = 72
        white_strength = 0.88
    for red, green, blue, alpha in restored.getdata():
        lightest = max(red, green, blue)
        darkest = min(red, green, blue)
        if (
            alpha > 0
            and darkest >= minimum_brightness
            and lightest - darkest <= maximum_spread
        ):
            red = round(
                red + (255 - red) * white_strength
            )
            green = round(
                green + (255 - green) * white_strength
            )
            blue = round(
                blue + (255 - blue) * white_strength
            )
        corrected_pixels.append((red, green, blue, alpha))
    restored.putdata(corrected_pixels)
    return restored


def prepare_characters(
    source_directory: Path,
    output_directory: Path,
) -> None:
    if not source_directory.is_dir():
        raise FileNotFoundError(
            "Character source folder not found: "
            f"{source_directory}. Supply it with --source."
        )
    output_directory.mkdir(parents=True, exist_ok=True)

    for source_path in sorted(source_directory.iterdir()):
        if source_path.suffix.lower() not in {".png", ".jpg", ".jpeg"}:
            continue
        with Image.open(source_path) as source_image:
            rgba = source_image.convert("RGBA")
        alpha_extrema = rgba.getchannel("A").getextrema()
        if alpha_extrema[0] < 255:
            cleaned = rgba
            bounds = cleaned.getbbox()
            if bounds is not None:
                left, top, right, bottom = bounds
                padding = max(4, round(max(rgba.size) * 0.008))
                cleaned = cleaned.crop(
                    (
                        max(0, left - padding),
                        max(0, top - padding),
                        min(rgba.width, right + padding),
                        min(rgba.height, bottom + padding),
                    )
                )
        else:
            cleaned = remove_edge_checkerboard(
                rgba,
                source_path.stem.lower().replace(" ", "_"),
            )
        subject_name = source_path.stem.lower().replace(" ", "_")
        if subject_name in {"bowser_jr", "piranha"}:
            cleaned.putalpha(
                cleaned.getchannel("A").point(
                    lambda alpha: 255 if alpha >= 128 else 0
                )
            )
            cleaned = restore_clean_whites(cleaned, subject_name)
        output_path = output_directory / normalized_name(source_path)
        cleaned.save(output_path, optimize=True)
        print(f"{source_path.name} -> {output_path.name} {cleaned.size}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Prepare transparent character artwork for the app banner."
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE_DIRECTORY,
        help="Folder containing source PNG/JPG character artwork.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_DIRECTORY,
        help="Folder for cleaned transparent PNG artwork.",
    )
    arguments = parser.parse_args()
    prepare_characters(arguments.source, arguments.output)


if __name__ == "__main__":
    main()
