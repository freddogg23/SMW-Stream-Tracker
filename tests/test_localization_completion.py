import ast
import importlib.util
from pathlib import Path
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = (
    PROJECT_ROOT
    / "SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER.py"
)


def load_tracker_module():
    spec = importlib.util.spec_from_file_location(
        "smw_tracker_localization_completion_test",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class LocalizationCompletionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tracker = load_tracker_module()

    def test_every_completion_row_is_available_in_every_language(self):
        for row in self.tracker._LOCALIZATION_COMPLETION_ROWS:
            english_text = row[0]
            for language in ("es", "fr", "de", "pt-BR"):
                with self.subTest(text=english_text, language=language):
                    self.assertIn(
                        english_text,
                        self.tracker.UI_TRANSLATIONS[language],
                    )

    def test_every_window_row_is_available_in_every_language(self):
        for row in self.tracker._WINDOW_LOCALIZATION_ROWS:
            english_text = row[0]
            for language in ("es", "fr", "de", "pt-BR"):
                with self.subTest(text=english_text, language=language):
                    self.assertIn(
                        english_text,
                        self.tracker.UI_TRANSLATIONS[language],
                    )

    def test_named_pages_have_complete_control_translations(self):
        visible_labels = (
            "Preferred service",
            "Timer grace:",
            "Exit completion by difficulty",
            "Search title or creator",
            "Reset Filters",
            "Edit Selected",
            "Open SMWCentral",
            "Launch Game",
            "Remove from Tracker",
            "Clean SMW base ROM:",
            "Copy new ROMs to a mounted SD folder:",
            "Upload new ROMs through FXPAK Pro USB:",
            "Add Unmoderated Hack",
            "Expand All",
            "Jump to alphabetical segment:",
            "FXPAK Pro SD Card",
            "FXPAK Pro SD Card Could Not Be Opened",
            (
                "Make sure the console and FXPAK Pro are powered on, a USB "
                "data cable is connected, and QUsb2Snes or SNI shows the "
                "FXPAK Pro."
            ),
            "QUsb2Snes did not report a compatible SNES device.",
            "Refresh SD Card",
            "Remove Selected Hack(s)",
            "Hack Title",
            "Folder",
            "File Name",
            "Format",
            "SD Card Path",
            "OBS Text Settings",
            "Preview",
            "Overview",
            "Tracker Statistics",
            "Tracker Status Breakdown",
            "Difficulty Progress Graph",
            "Progress by Difficulty",
            "Recent Activity",
            "Status",
            "Tracked",
            "Completed",
            "Exits",
            "Rate",
            "My Tracker",
            "Refresh",
            "Close",
            "All",
            "Newcomer",
            "Casual",
            "Intermediate",
            "Advanced",
            "Expert",
            "Master",
            "Grandmaster",
            "Unranked",
            "Catalog {version}  •  Refreshed {date}",
        )
        for language in ("es", "fr", "de", "pt-BR"):
            for label in visible_labels:
                with self.subTest(language=language, label=label):
                    translated = self.tracker.UI_TRANSLATIONS[language]
                    self.assertIn(label, translated)
                    self.assertTrue(translated[label].strip())

    def test_sortable_table_headings_use_the_selected_language(self):
        class FakeTree:
            def __init__(self):
                self.displayed_headings = {}

            def heading(self, column, **options):
                self.displayed_headings.setdefault(column, {}).update(options)

        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        app.app_language = "de"
        tree = FakeTree()
        source_headings = {
            "#0": "Hack Title",
            "folder": "Folder",
            "filename": "File Name",
            "format": "Format",
            "path": "SD Card Path",
        }

        app._configure_treeview_sorting(
            tree,
            source_headings,
            default_column="#0",
        )

        self.assertEqual(tree._smw_sort_source_headings, source_headings)
        self.assertEqual(
            tree.displayed_headings["#0"]["text"],
            "Hack-Titel \u25B2",
        )
        self.assertEqual(
            tree.displayed_headings["folder"]["text"],
            "Ordner",
        )
        self.assertEqual(
            tree.displayed_headings["filename"]["text"],
            "Dateiname",
        )
        self.assertEqual(
            tree.displayed_headings["format"]["text"],
            "Format",
        )
        self.assertEqual(
            tree.displayed_headings["path"]["text"],
            "SD-Kartenpfad",
        )

    def test_all_message_boxes_use_the_localized_wrapper(self):
        tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
        init_method = next(
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
            and node.name == "__init__"
            and any(
                isinstance(child, ast.Attribute)
                and child.attr == "app_language"
                for child in ast.walk(node)
            )
        )
        called_attributes = {
            node.func.attr
            for node in ast.walk(init_method)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
        }
        self.assertIn(
            "_install_localized_messageboxes",
            called_attributes,
        )

    def test_fxpak_sd_connection_error_is_fully_localized(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        app.app_language = "de"
        title = "FXPAK Pro SD Card Could Not Be Opened"
        instructions = (
            "Make sure the console and FXPAK Pro are powered on, a USB "
            "data cable is connected, and QUsb2Snes or SNI shows the "
            "FXPAK Pro."
        )
        detail = "QUsb2Snes did not report a compatible SNES device."

        localized_title = app._translate_dialog_text(title)
        localized_message = app._translate_dialog_text(
            instructions + "\n\n" + detail
        )

        self.assertEqual(
            localized_title,
            "FXPAK-Pro-SD-Karte konnte nicht geöffnet werden",
        )
        self.assertNotIn("Make sure the console", localized_message)
        self.assertNotIn("did not report", localized_message)
        self.assertIn("Stelle sicher", localized_message)
        self.assertIn("kein kompatibles SNES-Gerät", localized_message)

    def test_partially_localized_settings_sentence_is_retranslated_whole(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        app.app_language = "de"
        mixed_text = (
            "Timers keep running for this many Sekunden whenever gameplay "
            "is interrupted anywhere in a hack, then pause until gameplay "
            "resumes."
        )

        localized = app._translate_ui_text(mixed_text)

        self.assertEqual(
            localized,
            self.tracker.UI_TRANSLATIONS["de"][
                "Timers keep running for this many seconds whenever gameplay "
                "is interrupted anywhere in a hack, then pause until gameplay "
                "resumes."
            ],
        )
        self.assertNotIn("whenever gameplay", localized)

    def test_readme_selection_uses_active_language(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        for language, filename in (
            self.tracker.README_LANGUAGE_FILENAMES.items()
        ):
            app.app_language = language
            with self.subTest(language=language):
                self.assertEqual(
                    app._selected_readme_path().name,
                    filename,
                )

    def test_feedback_command_and_url_keep_the_selected_language(self):
        command = self.tracker._feedback_webview_command("dark", "de")
        self.assertIn("--feedback-language=de", command)
        self.assertEqual(
            self.tracker._feedback_language_from_arguments(command),
            "de",
        )
        self.assertIn(
            "lang=de-DE",
            self.tracker._localized_feedback_form_url("de"),
        )
        self.assertIn(
            self.tracker.FEEDBACK_FORM_URLS["de"],
            self.tracker._localized_feedback_form_url("de"),
        )

    def test_each_app_language_uses_its_own_feedback_form(self):
        self.assertEqual(
            set(self.tracker.FEEDBACK_FORM_URLS),
            set(self.tracker.FEEDBACK_LANGUAGE_LOCALES),
        )
        self.assertEqual(
            len(set(self.tracker.FEEDBACK_FORM_URLS.values())),
            len(self.tracker.FEEDBACK_FORM_URLS),
        )
        for language, locale in self.tracker.FEEDBACK_LANGUAGE_LOCALES.items():
            with self.subTest(language=language):
                url = self.tracker._localized_feedback_form_url(language)
                self.assertIn(self.tracker.FEEDBACK_FORM_URLS[language], url)
                self.assertIn(f"lang={locale}", url)

    def test_about_documents_are_rendered_inside_about_window(self):
        tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
        about_method = next(
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
            and node.name == "open_about_dialog"
        )
        called_names = {
            node.func.attr
            for node in ast.walk(about_method)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
        }
        self.assertNotIn("_open_installed_document", called_names)
        self.assertIn("read_text", called_names)
        constants = {
            node.value
            for node in ast.walk(about_method)
            if isinstance(node, ast.Constant)
            and isinstance(node.value, str)
        }
        self.assertIn("Back", constants)

    def test_embedded_pages_localize_after_their_builder_finishes(self):
        tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
        page_method = next(
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
            and node.name == "_open_in_app_page"
        )
        called_attributes = {
            node.func.attr
            for node in ast.walk(page_method)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
        }
        self.assertIn("after_idle", called_attributes)
        self.assertIn("_localize_widget_tree", called_attributes)

    def test_about_documents_follow_the_selected_language(self):
        for language in ("es", "fr", "de", "pt-BR"):
            for filename in (
                "PRIVACY.txt",
                "LICENSE.txt",
                "THIRD_PARTY_NOTICE.txt",
            ):
                with self.subTest(language=language, filename=filename):
                    localized = (
                        self.tracker.localized_installed_document_path(
                            filename,
                            language,
                        )
                    )
                    self.assertTrue(localized.is_file())
                    self.assertIn("." + language + ".txt", localized.name)

    def test_embedded_settings_page_localizes_after_it_is_built(self):
        tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
        settings_method = next(
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
            and node.name == "_open_settings_dialog"
        )
        called_attributes = {
            node.func.attr
            for node in ast.walk(settings_method)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
        }
        self.assertIn("_localize_widget_tree", called_attributes)
        self.assertIn("_translate_ui_text", called_attributes)

        visible_labels = (
            "Preferred service",
            "Import workbook",
            "OBS text folder",
            "Local ROM library",
            "RetroArch core",
            "Appearance",
            "App language",
            "Timer grace:",
            "seconds",
            "Game LiveSplit port:",
            "Level LiveSplit port:",
            "Save Settings",
            "Cancel",
            "Browse",
        )
        for language in ("es", "fr", "de", "pt-BR"):
            for label in visible_labels:
                with self.subTest(language=language, label=label):
                    self.assertIn(
                        label,
                        self.tracker.UI_TRANSLATIONS[language],
                    )


if __name__ == "__main__":
    unittest.main()
