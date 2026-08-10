import ast
from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = (
    PROJECT_ROOT
    / "SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER.py"
)
INSTALLER_PATH = PROJECT_ROOT / "installer" / "SMWStreamTrackerInstaller.iss"


class FirstLaunchSetupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = MODULE_PATH.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)
        cls.methods = {
            node.name: node
            for node in ast.walk(cls.tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }

    def test_first_launch_flag_and_welcome_schedule_are_present(self):
        self.assertIn('"first_launch_welcome_completed": False', self.source)
        self.assertIn(
            "self.root.after(1100, self._offer_first_launch_welcome)",
            self.source,
        )
        installer = INSTALLER_PATH.read_text(encoding="utf-8")
        self.assertIn('"first_launch_welcome_completed": false', installer)

    def test_guided_setup_methods_are_present(self):
        expected = {
            "_offer_first_launch_welcome",
            "start_guided_app_setup",
            "_guided_downloads_menu_button_clicked",
            "_guided_setup_set_stage",
            "_guided_setup_target_menu_entries",
            "_guided_install_optional_software",
            "_guided_optional_software_completed",
            "_guided_setup_show_catalog_filter_prompt",
            "_guided_setup_catalog_refreshed",
            "_guided_setup_downloader_opened",
            "_guided_setup_show_fxpak_prompt",
            "_guided_setup_hacks_downloaded",
            "_prompt_guided_obs_setup",
            "open_guided_obs_text_setup",
            "open_livesplit_obs_setup_guide",
        }
        self.assertFalse(expected.difference(self.methods))

    def test_required_stage_handoffs_are_hooked(self):
        self.assertIn(
            "self._guided_optional_software_completed(software)",
            ast.get_source_segment(
                self.source,
                self.methods["_finish_optional_software_install"],
            ),
        )
        self.assertIn(
            "self._guided_setup_catalog_refreshed()",
            ast.get_source_segment(
                self.source,
                self.methods["_finish_catalog_refresh"],
            ),
        )
        download_finish_source = ast.get_source_segment(
            self.source,
            self.methods["_finish_filtered_hack_download"],
        )
        self.assertIn(
            'getattr(\n                self,\n                "_guided_setup_hacks_downloaded"',
            download_finish_source,
        )
        self.assertIn("if callable(guided_setup_complete):", download_finish_source)
        self.assertIn("guided_setup_complete()", download_finish_source)

    def test_guide_starts_at_downloads_and_hides_after_it_is_selected(self):
        start_source = ast.get_source_segment(
            self.source,
            self.methods["start_guided_app_setup"],
        )
        click_source = ast.get_source_segment(
            self.source,
            self.methods["_guided_downloads_menu_button_clicked"],
        )
        self.assertIn('self._guided_setup_set_stage("downloads")', start_source)
        self.assertIn('if stage == "downloads":', click_source)
        self.assertIn("self._guided_setup_hide_dialog()", click_source)
        self.assertIn('self._guided_setup_set_stage("connection")', click_source)
        self.assertIn('elif stage == "downloads_again":', click_source)
        self.assertIn(
            'self._guided_setup_set_stage("download_missing")',
            click_source,
        )

    def test_connection_step_flashes_parent_and_all_three_choices(self):
        targets_source = ast.get_source_segment(
            self.source,
            self.methods["_guided_setup_target_menu_entries"],
        )
        self.assertIn('if stage == "connection":', targets_source)
        self.assertIn("connection_setup_menu_index", targets_source)
        self.assertIn("connection_option_menu_indexes", targets_source)
        self.assertIn(
            "self.connection_option_menu_indexes = tuple(",
            self.source,
        )

    def test_posted_native_menu_entries_are_stable_and_clickable(self):
        tick_source = ast.get_source_segment(
            self.source,
            self.methods["_guided_setup_flash_tick"],
        )
        start_source = ast.get_source_segment(
            self.source,
            self.methods["_guided_setup_start_flash"],
        )
        self.assertNotIn("entryconfigure", tick_source)
        self.assertIn("menu.entryconfigure(", start_source)
        self.assertIn('label=f"\\u2605  {label}"', start_source)
        self.assertIn('foreground=THEME["yellow"]', start_source)

    def test_connection_routes_require_the_expected_installs(self):
        completion_source = ast.get_source_segment(
            self.source,
            self.methods["_guided_optional_software_completed"],
        )
        self.assertIn('if choice == "qusb2snes":', completion_source)
        self.assertIn('configured_file("qusb2snes_path"', completion_source)
        self.assertIn('elif choice == "sni_retroarch":', completion_source)
        self.assertIn('configured_file("sni_path"', completion_source)
        self.assertIn(
            'configured_file("retroarch_executable_path")',
            completion_source,
        )
        self.assertIn(
            'configured_file("retroarch_core_path")',
            completion_source,
        )

    def test_catalog_and_download_handoffs_follow_requested_order(self):
        catalog_source = ast.get_source_segment(
            self.source,
            self.methods["open_smwcentral_catalog_browser"],
        )
        refresh_source = ast.get_source_segment(
            self.source,
            self.methods["_guided_setup_catalog_refreshed"],
        )
        downloader_source = ast.get_source_segment(
            self.source,
            self.methods["_guided_setup_downloader_opened"],
        )
        self.assertIn('self._guided_setup_set_stage("refresh_catalog")', catalog_source)
        self.assertIn("_guided_setup_show_catalog_filter_prompt", catalog_source)
        self.assertIn('self._guided_setup_set_stage("downloads_again")', refresh_source)
        self.assertIn('self._guided_setup_set_stage("download_all")', downloader_source)
        self.assertIn("_guided_setup_show_fxpak_prompt", downloader_source)

    def test_instruction_and_completion_popups_use_blue_app_dialogs(self):
        filter_source = ast.get_source_segment(
            self.source,
            self.methods["_guided_setup_show_catalog_filter_prompt"],
        )
        fxpak_source = ast.get_source_segment(
            self.source,
            self.methods["_guided_setup_show_fxpak_prompt"],
        )
        complete_source = ast.get_source_segment(
            self.source,
            self.methods["_prompt_guided_obs_setup"],
        )
        self.assertIn("self._show_localized_info(", filter_source)
        self.assertIn('"filter_prompt"', filter_source)
        self.assertIn("self._show_localized_info(", fxpak_source)
        self.assertIn('"fxpak_prompt"', fxpak_source)
        self.assertIn('bg=THEME["blue"]', complete_source)
        self.assertIn('"setup_complete_message"', complete_source)
        self.assertIn('"obs_prompt"', complete_source)

    def test_download_actions_include_patch_wording(self):
        self.assertIn('"Download & Patch Missing Hacks…"', self.source)
        self.assertIn('"Download & Patch All Matching Hacks"', self.source)
        self.assertNotIn('"Download Missing Hacks…"', self.source)
        self.assertNotIn('"Download All Matching Hacks"', self.source)

    def test_setup_help_menu_and_obs_paths_are_available(self):
        self.assertIn('self._setup_guide_text("setup_menu")', self.source)
        self.assertIn('self._setup_guide_text("app_setup")', self.source)
        self.assertIn('self._setup_guide_text("obs_setup")', self.source)
        for filename in (
            "hack_name.txt",
            "author.txt",
            "exits.txt",
            "level_deaths.txt",
            "total_deaths.txt",
        ):
            with self.subTest(filename=filename):
                self.assertIn(f'"{filename}"', self.source)

    def test_obs_setup_explains_how_to_reuse_existing_text_sources(self):
        obs_source = ast.get_source_segment(
            self.source,
            self.methods["open_guided_obs_text_setup"],
        )
        self.assertIn('"obs_existing_source_note"', obs_source)
        self.assertIn('highlightbackground=THEME["yellow"]', obs_source)
        self.assertIn('"\\u2605  "', obs_source)

    def test_livesplit_obs_guide_uses_two_copies_ports_and_window_capture(self):
        settings_source = ast.get_source_segment(
            self.source,
            self.methods["_open_settings_dialog"],
        )
        guide_source = ast.get_source_segment(
            self.source,
            self.methods["open_livesplit_obs_setup_guide"],
        )
        self.assertIn('"livesplit_obs_note"', settings_source)
        self.assertIn('"livesplit_obs_button"', settings_source)
        self.assertIn("local_game_port.get()", settings_source)
        self.assertIn("local_level_port.get()", settings_source)
        self.assertIn('"livesplit_obs_instructions"', guide_source)
        self.assertIn("game_port=resolved_game_port", guide_source)
        self.assertIn("level_port=resolved_level_port", guide_source)
        self.assertIn('style="Mario.Vertical.TScrollbar"', guide_source)
        self.assertIn('"game_livesplit_button"', guide_source)
        self.assertIn('"level_livesplit_button"', guide_source)
        self.assertIn("install_or_open_livesplit_copy", guide_source)

        assignment = next(
            node
            for node in self.tree.body
            if isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name)
                and target.id == "SETUP_GUIDE_TRANSLATIONS"
                for target in node.targets
            )
        )
        translations = ast.literal_eval(assignment.value)
        english = translations["en"]["livesplit_obs_instructions"]
        self.assertIn("SELECT GAME LIVESPLIT", english)
        self.assertIn("SELECT LEVEL LIVESPLIT", english)
        self.assertIn("When the button turns green", english)
        self.assertIn("automatic TCP server startup", english)
        self.assertIn("You do not need to edit LiveSplit ports", english)
        self.assertIn("Save Settings", english)
        self.assertIn("ADD THE GAME TIMER TO OBS", english)
        self.assertIn("ADD THE LEVEL TIMER TO OBS", english)
        self.assertIn("Window Capture", english)
        self.assertIn("{game_port}", english)
        self.assertIn("{level_port}", english)
        self.assertNotIn("Right-click LiveSplit", english)
        self.assertNotIn("Start TCP/WS Server", english)

        for language in ("en", "au", "es", "fr", "de", "pt-BR"):
            with self.subTest(language=language):
                instructions = translations[language]["livesplit_obs_instructions"]
                self.assertIn("{game_port}", instructions)
                self.assertIn("{level_port}", instructions)
                self.assertIn("6.", instructions)

    def test_every_supported_language_has_setup_copy(self):
        assignment = next(
            node
            for node in self.tree.body
            if isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name)
                and target.id == "SETUP_GUIDE_TRANSLATIONS"
                for target in node.targets
            )
        )
        translations = ast.literal_eval(assignment.value)
        required_keys = set(translations["en"])
        for language in ("es", "fr", "de", "pt-BR"):
            with self.subTest(language=language):
                self.assertFalse(required_keys.difference(translations[language]))
        self.assertIn("welcome_message", translations["au"])


if __name__ == "__main__":
    unittest.main()
