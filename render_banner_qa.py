from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER.py"

spec = spec_from_file_location("smw_tracker_banner_qa", SOURCE)
module = module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)

app = object.__new__(module.TrackerApp)

background_directory = ROOT / "banner_background_assets"
for background_name in (
    "mushroom_kingdom_character_stage_supplied_question_blocks.png",
    "mushroom_kingdom_character_stage_question_blocks.png",
    "mushroom_kingdom_character_stage.png",
    "continuous_mario_landscape.png",
):
    background_path = background_directory / background_name
    if background_path.exists():
        app.banner_background_source = Image.open(background_path).convert("RGBA")
        break

repeat_path = background_directory / "mushroom_kingdom_open_meadow.png"
app.banner_repeat_background_source = (
    Image.open(repeat_path).convert("RGBA") if repeat_path.exists() else None
)

title_path = ROOT / "banner_title_assets" / "smw_stream_tracker_logo.png"
app.banner_title_source = Image.open(title_path).convert("RGBA")

character_directory = ROOT / "banner_character_assets_user"
character_files = {
    "bowser": "bowser.png",
    "bowser_jr": "bowser_jr.png",
    "goomba": "goomba.png",
    "green_toad": "green_toad.png",
    "kamek": "kamek.png",
    "koopa": "koopa_replacement.png",
    "koopa_shell": "koopa_shell.png",
    "luigi": "luigi.png",
    "mario": "mario.png",
    "peach": "peach.png",
    "piranha": "piranha_lip_repaired.png",
    "toad": "toad.png",
    "toadette": "toadette_white_hair_circles.png",
    "yoshi": "yoshi_tongue_source.png",
}
app.user_banner_character_sources = {}
for character_name, filename in character_files.items():
    image = Image.open(character_directory / filename).convert("RGBA")
    if character_name == "bowser":
        image = module.repair_bowser_toenail_image(image)
    elif character_name == "yoshi":
        image = module.recolor_yoshi_body_blue_image(image)
    app.user_banner_character_sources[character_name] = image

element_directory = ROOT / "banner_element_assets"
app.banner_element_sources = {}
for element_name in (
    "green_pipe",
    "block_pair",
    "original_spotted_hills",
    "bowser_25pct_fixed_flame_overlay",
    "bowser_25pct_fixed_flame_uncropped_overlay",
    "question_block_row_supplied",
    "question_block_row",
):
    element_path = element_directory / f"{element_name}.png"
    if element_path.exists():
        app.banner_element_sources[element_name] = Image.open(element_path).convert(
            "RGBA"
        )

width, height = 2048, 353
full_banner = app._build_user_character_banner(width, height)
assert full_banner is not None
full_banner.save(ROOT / "_qa_current_banner_full.png")

wide_banner = app._build_user_character_banner(3840, 550)
assert wide_banner is not None
wide_banner.save(ROOT / "_qa_current_banner_ultrawide.png")

bowser = app.user_banner_character_sources.pop("bowser")
bowser_overlay = app.banner_element_sources.pop(
    "bowser_25pct_fixed_flame_uncropped_overlay",
    None,
)
without_bowser = app._build_user_character_banner(width, height)
app.user_banner_character_sources["bowser"] = bowser
if bowser_overlay is not None:
    app.banner_element_sources[
        "bowser_25pct_fixed_flame_uncropped_overlay"
    ] = bowser_overlay
assert without_bowser is not None
without_bowser.save(ROOT / "_qa_current_banner_without_bowser.png")

print(ROOT / "_qa_current_banner_full.png")
print(ROOT / "_qa_current_banner_without_bowser.png")
