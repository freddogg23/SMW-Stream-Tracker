from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "banner_character_assets_user" / "bowser.png"
FIXED_FLAME = (
    ROOT
    / "banner_element_assets"
    / "bowser_25pct_fixed_flame_overlay.png"
)
OUTPUT = (
    ROOT
    / "banner_element_assets"
    / "bowser_25pct_fixed_flame_uncropped_overlay.png"
)

# Reference coordinates match the full-width QA banner used for the approved
# 25%-larger Bowser treatment. The previous overlay began at x=0, but the
# enlarged body naturally starts at x=-52. Retain ten pixels of transparent
# margin beyond that body edge so it never ends on a hard vertical cut.
reference_width = 2048
reference_height = 353
reference_center_x = reference_width * 0.075
reference_bottom_y = reference_height * 0.925
overlay_origin_x = -60
overlay_origin_y = 100
overlay_right = 312
overlay_bottom = 330

source = Image.open(SOURCE).convert("RGBA")
target_height = round(reference_height * 0.625)
target_width = round(source.width * target_height / source.height)
rendered = source.resize(
    (target_width, target_height),
    Image.Resampling.LANCZOS,
).transpose(Image.Transpose.FLIP_LEFT_RIGHT)

rendered_left = round(reference_center_x - target_width / 2)
rendered_top = round(reference_bottom_y - target_height)
missing_width = max(0, -rendered_left)
missing_body = rendered.crop((0, 0, missing_width, rendered.height))

extended = Image.new(
    "RGBA",
    (overlay_right - overlay_origin_x, overlay_bottom - overlay_origin_y),
    (0, 0, 0, 0),
)
extended.alpha_composite(
    missing_body,
    (
        rendered_left - overlay_origin_x,
        rendered_top - overlay_origin_y,
    ),
)

fixed_flame = Image.open(FIXED_FLAME).convert("RGBA")
extended.alpha_composite(
    fixed_flame,
    (0 - overlay_origin_x, 113 - overlay_origin_y),
)

# The body/flame split used by the earlier preview clipped the far edge of
# Bowser's forward fist. Recover that small body-only region from the complete
# 25%-larger source and place it above the fixed-size flame treatment.
hand_box = (145, 125, 215, 195)
hand_source = rendered.crop(
    (
        hand_box[0] - rendered_left,
        hand_box[1] - rendered_top,
        hand_box[2] - rendered_left,
        hand_box[3] - rendered_top,
    )
)
extended.alpha_composite(
    hand_source,
    (
        hand_box[0] - overlay_origin_x,
        hand_box[1] - overlay_origin_y,
    ),
)

extended.save(OUTPUT, optimize=True)
print(OUTPUT)
