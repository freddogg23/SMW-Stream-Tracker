"""Build the app's idle and tracking icons from the supplied star artwork."""

from __future__ import annotations

from collections import deque
import math
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parent
ASSET_DIR = ROOT / "app_assets"
SOURCE = ASSET_DIR / "smw_stream_tracker_star.jpg"
IDLE_PNG = ASSET_DIR / "smw_stream_tracker_icon.png"
TRACKING_PNG = ASSET_DIR / "smw_stream_tracker_icon_tracking.png"
IDLE_ICO = ASSET_DIR / "smw_stream_tracker_icon.ico"
TRACKING_ICO = ASSET_DIR / "smw_stream_tracker_icon_tracking.ico"
PREVIEW = ASSET_DIR / "smw_stream_tracker_icon_preview.png"

RED_BACKGROUND = (224, 44, 38, 255)
GREEN_STAR = (38, 190, 74, 255)
GREEN_OUTLINE = (8, 92, 34, 255)


def _is_checkerboard(pixel: tuple[int, int, int, int]) -> bool:
    red, green, blue, alpha = pixel
    return (
        alpha > 0
        and min(red, green, blue) >= 185
        and max(red, green, blue) - min(red, green, blue) <= 22
    )


def replace_connected_checkerboard(source: Image.Image) -> Image.Image:
    """Replace only checkerboard pixels connected to the outer border."""
    image = source.convert("RGBA").copy()
    pixels = image.load()
    width, height = image.size
    pending: deque[tuple[int, int]] = deque()
    visited = bytearray(width * height)

    for x in range(width):
        pending.append((x, 0))
        pending.append((x, height - 1))
    for y in range(1, height - 1):
        pending.append((0, y))
        pending.append((width - 1, y))

    while pending:
        x, y = pending.popleft()
        index = y * width + x
        if visited[index]:
            continue
        visited[index] = 1
        if not _is_checkerboard(pixels[x, y]):
            continue

        pixels[x, y] = RED_BACKGROUND
        if x:
            pending.append((x - 1, y))
        if x + 1 < width:
            pending.append((x + 1, y))
        if y:
            pending.append((x, y - 1))
        if y + 1 < height:
            pending.append((x, y + 1))

    return image


def star_points(
    center_x: float,
    center_y: float,
    outer_radius: float,
    inner_radius: float,
) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    for point_index in range(10):
        angle = -math.pi / 2 + point_index * math.pi / 5
        radius = outer_radius if point_index % 2 == 0 else inner_radius
        points.append(
            (
                center_x + math.cos(angle) * radius,
                center_y + math.sin(angle) * radius,
            )
        )
    return points


def add_tracking_star(idle_icon: Image.Image) -> Image.Image:
    tracking = idle_icon.copy()
    draw = ImageDraw.Draw(tracking)
    center_x = tracking.width * 0.83
    center_y = tracking.height * 0.82
    radius = tracking.width * 0.125

    draw.polygon(
        star_points(center_x, center_y, radius + 5, radius * 0.47 + 3),
        fill=(255, 255, 255, 255),
    )
    draw.polygon(
        star_points(center_x, center_y, radius + 2, radius * 0.47 + 1),
        fill=GREEN_OUTLINE,
    )
    draw.polygon(
        star_points(center_x, center_y, radius - 2, radius * 0.43),
        fill=GREEN_STAR,
    )
    return tracking


def save_ico(image: Image.Image, destination: Path) -> None:
    image.save(
        destination,
        format="ICO",
        sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )


def build_preview(idle: Image.Image, tracking: Image.Image) -> None:
    preview = Image.new("RGBA", (640, 360), (245, 245, 245, 255))
    preview.alpha_composite(idle.resize((256, 256), Image.Resampling.LANCZOS), (32, 24))
    preview.alpha_composite(
        tracking.resize((256, 256), Image.Resampling.LANCZOS),
        (352, 24),
    )
    draw = ImageDraw.Draw(preview)
    draw.text((120, 298), "Idle", fill=(25, 25, 25, 255), anchor="ma")
    draw.text((448, 298), "Tracking", fill=(25, 25, 25, 255), anchor="ma")
    for index, icon in enumerate((idle, tracking)):
        icon_32 = icon.resize((32, 32), Image.Resampling.LANCZOS)
        preview.alpha_composite(icon_32, (128 + index * 320, 316))
    preview.convert("RGB").save(PREVIEW, quality=95)


def main() -> None:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    with Image.open(SOURCE) as supplied_star:
        idle = replace_connected_checkerboard(supplied_star)
    idle = idle.resize((256, 256), Image.Resampling.LANCZOS)
    tracking = add_tracking_star(idle)

    idle.save(IDLE_PNG)
    tracking.save(TRACKING_PNG)
    save_ico(idle, IDLE_ICO)
    save_ico(tracking, TRACKING_ICO)
    build_preview(idle, tracking)


if __name__ == "__main__":
    main()
