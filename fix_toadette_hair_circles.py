from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "banner_character_assets_user" / "toadette.png"
OUTPUT = ROOT / "banner_character_assets_user" / "toadette_white_hair_circles.png"


def inside_ellipse(x, y, cx, cy, rx, ry):
    return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0


image = Image.open(SOURCE).convert("RGBA")
pixels = image.load()

# The four cool-gray spots on the two mushroom-shaped hair ornaments.
spots = (
    (64, 220, 15, 21),
    (53, 248, 23, 20),
    (292, 237, 28, 28),
    (333, 254, 24, 21),
)

for y in range(image.height):
    for x in range(image.width):
        if not any(inside_ellipse(x, y, *spot) for spot in spots):
            continue

        red, green, blue, alpha = pixels[x, y]
        if alpha == 0:
            continue

        # Exclude the surrounding pink material and recolor only the
        # low-saturation gray/blue spot pixels. Retain their original
        # highlights and shadows while shifting the material to white.
        if max(red, green, blue) - min(red, green, blue) > 58:
            continue

        luminance = 0.2126 * red + 0.7152 * green + 0.0722 * blue
        white = round(max(218, min(255, 218 + (luminance - 75) * 0.24)))
        pixels[x, y] = (white, white, white, alpha)

# Background removal erased parts of two white spots on the left hair
# ornament, leaving round transparent openings that show the blue banner
# through them. Restore the spots underneath the original character so the
# surrounding pink pixels and their antialiased edge stay untouched.
restored_spot = Image.new("RGBA", image.size, (0, 0, 0, 0))
restored_pixels = restored_spot.load()
missing_spots = (
    (14.0, 235.0, 18.0, 23.0),
    (69.0, 222.0, 18.0, 23.0),
)
for spot_center_x, spot_center_y, spot_radius_x, spot_radius_y in missing_spots:
    for y in range(
        max(0, round(spot_center_y - spot_radius_y - 2)),
        min(image.height, round(spot_center_y + spot_radius_y + 2)),
    ):
        for x in range(
            max(0, round(spot_center_x - spot_radius_x - 2)),
            min(image.width, round(spot_center_x + spot_radius_x + 2)),
        ):
            normalized_distance = (
                ((x - spot_center_x) / spot_radius_x) ** 2
                + ((y - spot_center_y) / spot_radius_y) ** 2
            ) ** 0.5
            if normalized_distance > 1.0:
                continue
            edge_alpha = round(
                255
                * max(
                    0.0,
                    min(1.0, (1.0 - normalized_distance) / 0.08),
                )
            )
            shade = round(
                max(
                    226,
                    min(
                        255,
                        252
                        - 13 * ((x - spot_center_x) / spot_radius_x)
                        - 10 * ((y - spot_center_y) / spot_radius_y),
                    ),
                )
            )
            restored_pixels[x, y] = (shade, shade, shade, edge_alpha)

restored_spot.alpha_composite(image)
image = restored_spot

# Add the missing half-spot along the outer-left edge of the main mushroom
# cap. Restrict it to the existing pink cap pixels so the character silhouette
# and transparent background remain unchanged.
pixels = image.load()
half_spot_center_x = 88.0
half_spot_center_y = 112.0
half_spot_radius_x = 34.0
half_spot_radius_y = 43.0
for y in range(
    max(0, round(half_spot_center_y - half_spot_radius_y - 2)),
    min(image.height, round(half_spot_center_y + half_spot_radius_y + 2)),
):
    for x in range(
        max(0, round(half_spot_center_x - half_spot_radius_x - 2)),
        min(image.width, round(half_spot_center_x + half_spot_radius_x + 2)),
    ):
        red, green, blue, alpha = pixels[x, y]
        if alpha == 0 or not (
            red > 145
            and blue > 85
            and red > green * 1.28
            and blue > green * 1.04
        ):
            continue
        normalized_distance = (
            ((x - half_spot_center_x) / half_spot_radius_x) ** 2
            + ((y - half_spot_center_y) / half_spot_radius_y) ** 2
        ) ** 0.5
        if normalized_distance > 1.0:
            continue
        blend = max(
            0.0,
            min(1.0, (1.0 - normalized_distance) / 0.10),
        )
        shade = round(
            max(
                226,
                min(
                    255,
                    251
                    - 10
                    * ((x - half_spot_center_x) / half_spot_radius_x)
                    - 8
                    * ((y - half_spot_center_y) / half_spot_radius_y),
                ),
            )
        )
        pixels[x, y] = (
            round(red * (1.0 - blend) + shade * blend),
            round(green * (1.0 - blend) + shade * blend),
            round(blue * (1.0 - blend) + shade * blend),
            alpha,
        )

image.save(OUTPUT, optimize=True)
print(OUTPUT)
