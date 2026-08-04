from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "_qa_current_banner_full.png"
OUTPUT = ROOT / "_preview_consistent_ground_shadows.png"
COMPARISON = ROOT / "_preview_consistent_ground_shadows_comparison.png"
GROUND_CLOSEUP = ROOT / "_preview_consistent_ground_shadows_closeup.png"

banner = Image.open(SOURCE).convert("RGBA")
original_banner = banner.copy()
width, height = banner.size

# All shadows use one upper-left key light. On the ground plane this sends
# every cast shadow toward the lower-right by the same direction vector.
light_direction_x = height * 0.18
light_direction_y = height * 0.025

# center-x, ground-y, footprint width, cast length, opacity, softness
shadow_specs = (
    (0.112, 0.925, 0.46, 1.00, 92, 0.90),  # Bowser
    (0.214, 0.875, 0.19, 0.82, 76, 0.90),  # Luigi
    (0.265, 0.875, 0.18, 0.78, 72, 0.95),  # Kamek
    (0.325, 0.875, 0.16, 0.72, 70, 0.90),  # Goombas
    (0.385, 0.875, 0.13, 0.68, 65, 0.90),  # Green Toad
    (0.413, 0.875, 0.11, 0.55, 32, 1.45),  # Airborne Mario
    (0.625, 0.875, 0.14, 0.68, 68, 0.90),  # Toadette
    (0.657, 0.875, 0.13, 0.64, 66, 0.90),  # Toad
    (0.718, 0.875, 0.17, 0.72, 70, 0.90),  # Yoshi
    (0.785, 0.875, 0.17, 0.72, 70, 0.90),  # Peach
    (0.827, 0.875, 0.13, 0.64, 65, 0.90),  # Koopa
    (0.885, 0.875, 0.16, 0.66, 38, 1.35),  # Airborne Bowser Jr.
    (0.987, 0.875, 0.13, 0.60, 64, 0.90),  # Piranha/pipe
)

shadow_layer = Image.new("RGBA", banner.size, (0, 0, 0, 0))
for (
    center_fraction,
    ground_fraction,
    footprint_fraction,
    cast_scale,
    opacity,
    softness,
) in shadow_specs:
    center_x = width * center_fraction
    ground_y = height * ground_fraction
    footprint = height * footprint_fraction
    cast_x = light_direction_x * cast_scale
    cast_y = light_direction_y * cast_scale

    local = Image.new("RGBA", banner.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(local)

    near_half = footprint * 0.43
    far_half = footprint * 0.22
    draw.polygon(
        (
            (center_x - near_half, ground_y - 2),
            (center_x + near_half, ground_y - 2),
            (
                center_x + cast_x + far_half,
                ground_y + cast_y + height * 0.030,
            ),
            (
                center_x + cast_x - far_half,
                ground_y + cast_y + height * 0.030,
            ),
        ),
        fill=(12, 18, 28, opacity),
    )

    contact_half = footprint * 0.37
    draw.ellipse(
        (
            center_x - contact_half + cast_x * 0.10,
            ground_y - height * 0.014,
            center_x + contact_half + cast_x * 0.34,
            ground_y + height * 0.034,
        ),
        fill=(8, 14, 22, min(112, opacity + 18)),
    )

    local = local.filter(
        ImageFilter.GaussianBlur(
            radius=max(2.0, height * 0.012 * softness)
        )
    )
    shadow_layer.alpha_composite(local)

banner.alpha_composite(shadow_layer)
banner.save(OUTPUT, optimize=True)

try:
    label_font = ImageFont.truetype(
        str(Path(r"C:\Windows\Fonts\arialbd.ttf")),
        max(16, round(height * 0.050)),
    )
except OSError:
    label_font = ImageFont.load_default()

label_height = max(28, round(height * 0.10))
comparison = Image.new(
    "RGB",
    (width, height * 2 + label_height * 2),
    (8, 15, 28),
)
comparison_draw = ImageDraw.Draw(comparison)
comparison_draw.text(
    (18, (label_height - label_font.size) / 2),
    "CURRENT",
    font=label_font,
    fill=(235, 242, 255),
)
comparison.paste(original_banner.convert("RGB"), (0, label_height))
second_label_y = label_height + height
comparison_draw.text(
    (18, second_label_y + (label_height - label_font.size) / 2),
    "PREVIEW - ONE UPPER-LEFT LIGHT SOURCE",
    font=label_font,
    fill=(255, 216, 48),
)
comparison.paste(
    banner.convert("RGB"),
    (0, second_label_y + label_height),
)
comparison.save(COMPARISON, optimize=True)

closeup_box = (0, round(height * 0.48), round(width * 0.31), height)
current_closeup = original_banner.crop(closeup_box).convert("RGB")
shadow_closeup = banner.crop(closeup_box).convert("RGB")
closeup_width = current_closeup.width * 2
closeup_height = current_closeup.height
ground_closeup = Image.new(
    "RGB",
    (closeup_width, closeup_height + label_height),
    (8, 15, 28),
)
ground_closeup_draw = ImageDraw.Draw(ground_closeup)
ground_closeup_draw.text(
    (12, (label_height - label_font.size) / 2),
    "CURRENT",
    font=label_font,
    fill=(235, 242, 255),
)
ground_closeup_draw.text(
    (current_closeup.width + 12, (label_height - label_font.size) / 2),
    "SHADOW PREVIEW",
    font=label_font,
    fill=(255, 216, 48),
)
ground_closeup.paste(current_closeup, (0, label_height))
ground_closeup.paste(
    shadow_closeup,
    (current_closeup.width, label_height),
)
ground_closeup.save(GROUND_CLOSEUP, optimize=True)

print(OUTPUT)
print(COMPARISON)
print(GROUND_CLOSEUP)
