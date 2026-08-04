from pathlib import Path

from PIL import Image, ImageChops


ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "_preview_bowser_25pct_fixed_flame_full.png"
BASE = ROOT / "_qa_current_banner_without_bowser.png"
OUTPUT = (
    ROOT
    / "banner_element_assets"
    / "bowser_25pct_fixed_flame_overlay.png"
)

reference_box = (0, 113, 312, 325)
target = Image.open(TARGET).convert("RGBA").crop(reference_box)
base = Image.open(BASE).convert("RGBA").crop(reference_box)
difference = ImageChops.difference(target.convert("RGB"), base.convert("RGB"))

alpha = Image.new("L", target.size, 0)
alpha_pixels = alpha.load()
difference_pixels = difference.load()
for y in range(target.height):
    for x in range(target.width):
        alpha_pixels[x, y] = (
            255 if max(difference_pixels[x, y]) > 2 else 0
        )

target.putalpha(alpha)
target.save(OUTPUT, optimize=True)
print(OUTPUT)
