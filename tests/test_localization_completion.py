import ast
import importlib.util
from pathlib import Path
import re
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = (
    PROJECT_ROOT
    / "SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER.py"
)
LOCALIZED_LANGUAGES = ("au", "es", "fr", "de", "pt-BR")
SELECTABLE_LOCALIZED_LANGUAGES = ("es", "fr", "de", "pt-BR")


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

    def test_every_app_language_has_the_same_complete_ui_keyset(self):
        expected = set(self.tracker.UI_TRANSLATIONS["es"])
        self.assertGreaterEqual(len(expected), 675)
        for language in LOCALIZED_LANGUAGES:
            with self.subTest(language=language):
                translations = self.tracker.UI_TRANSLATIONS[language]
                self.assertEqual(set(translations), expected)
                self.assertTrue(all(value.strip() for value in translations.values()))

    def test_every_setup_guide_language_has_the_same_complete_keyset(self):
        expected = set(self.tracker.SETUP_GUIDE_TRANSLATIONS["en"])
        self.assertGreaterEqual(len(expected), 65)
        for language in LOCALIZED_LANGUAGES:
            with self.subTest(language=language):
                translations = self.tracker.SETUP_GUIDE_TRANSLATIONS[language]
                self.assertEqual(set(translations), expected)
                self.assertTrue(all(value.strip() for value in translations.values()))

    def test_literal_localization_requests_have_language_coverage(self):
        tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
        requested = set()
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if isinstance(node.func, ast.Attribute):
                call_name = node.func.attr
            elif isinstance(node.func, ast.Name):
                call_name = node.func.id
            else:
                continue

            value_node = None
            if call_name in {"_translate_ui_text", "_format_ui_text"}:
                if node.args:
                    value_node = node.args[0]
            elif call_name == "_localized_string_var":
                if node.args:
                    value_node = node.args[0]
                else:
                    value_node = next(
                        (
                            keyword.value
                            for keyword in node.keywords
                            if keyword.arg == "value"
                        ),
                        None,
                    )

            if (
                isinstance(value_node, ast.Constant)
                and isinstance(value_node.value, str)
                and value_node.value.strip()
            ):
                requested.add(value_node.value.strip())

        self.assertGreaterEqual(len(requested), 215)
        for language in LOCALIZED_LANGUAGES:
            translations = self.tracker.UI_TRANSLATIONS[language]
            missing = requested.difference(translations)
            with self.subTest(language=language):
                self.assertEqual(missing, set())

    def test_australian_english_is_complete_and_playfully_distinct(self):
        translations = self.tracker.UI_TRANSLATIONS["au"]
        changed = {
            english: localized
            for english, localized in translations.items()
            if english != localized
        }
        self.assertGreaterEqual(len(changed), 200)
        sample = " ".join(changed.values()).casefold()
        for phrase in ("mate", "crikey", "yeah, nah", "you beauty"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, sample)

        setup_sample = " ".join(
            self.tracker.SETUP_GUIDE_TRANSLATIONS["au"].values()
        ).casefold()
        self.assertIn("mate", setup_sample)
        self.assertIn("crikey", setup_sample)

    def test_static_widget_and_message_text_has_language_coverage(self):
        tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
        visible_text = set()
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.keyword)
                and node.arg in {"text", "title", "label", "message"}
                and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)
            ):
                visible_text.add(node.value.value.strip())
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr
                in {
                    "showinfo",
                    "showwarning",
                    "showerror",
                    "askyesno",
                    "askokcancel",
                    "askretrycancel",
                }
            ):
                for argument in node.args[:2]:
                    if (
                        isinstance(argument, ast.Constant)
                        and isinstance(argument.value, str)
                    ):
                        visible_text.add(argument.value.strip())

        visible_text.discard("")
        language_neutral = {
            "FXPAK PRO",
            "★   1UP   ?   ★",
            "Status:",
        }
        for language in ("es", "fr", "de", "pt-BR"):
            app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
            app.app_language = language
            app.config = {"app_language": language}
            untranslated = {
                text
                for text in visible_text
                if len(text) > 1
                and not re.fullmatch(r"[\W\d_]+", text)
                and app._translate_ui_text(text) == text
                and text not in language_neutral
            }
            self.assertEqual(untranslated, set(), language)

    def test_literal_window_titles_have_language_coverage(self):
        tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
        titles = {
            node.args[0].value.strip()
            for node in ast.walk(tree)
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "title"
                and node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)
                and node.args[0].value.strip()
            )
        }
        language_neutral = {self.tracker.APP_NAME}
        for language in SELECTABLE_LOCALIZED_LANGUAGES:
            app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
            app.app_language = language
            app.config = {"app_language": language}
            untranslated = {
                title
                for title in titles
                if title not in language_neutral
                and app._translate_ui_text(title) == title
            }
            with self.subTest(language=language):
                self.assertEqual(untranslated, set())

    def test_hack_details_chrome_is_complete_in_every_language(self):
        required_text = {
            "Hack Details",
            "Untitled",
            "Unknown",
            "By:",
            "Unrated",
            "SMWCentral Rating:",
            "Type:",
            "Tags:",
            "Description",
            "No description is available for this hack.",
            "Screenshots",
            "Loading screenshots…",
            "No screenshots are available for this hack.",
            "Click any screenshot to enlarge it.",
            "Some screenshots could not be loaded.",
            "Screenshot Viewer",
            "Open SMWCentral",
            "Close",
        }
        for language in LOCALIZED_LANGUAGES:
            translations = self.tracker.UI_TRANSLATIONS[language]
            with self.subTest(language=language):
                self.assertEqual(required_text.difference(translations), set())

    def test_native_picker_titles_are_localized_before_windows_sees_them(self):
        tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
        picker_names = {
            "askopenfilename",
            "askdirectory",
            "asksaveasfilename",
            "askcolor",
        }
        for node in ast.walk(tree):
            if not (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr in picker_names
            ):
                continue
            title = next(
                (keyword.value for keyword in node.keywords if keyword.arg == "title"),
                None,
            )
            with self.subTest(line=node.lineno, picker=node.func.attr):
                self.assertIsInstance(title, ast.Call)
                self.assertIsInstance(title.func, ast.Attribute)
                self.assertIn(
                    title.func.attr,
                    {"_translate_ui_text", "_format_ui_text"},
                )

    def test_installer_custom_messages_are_complete_in_all_six_languages(self):
        scripts = (
            ("SMWStreamTrackerInstaller.iss", 64),
            ("SMWStreamTrackerUpdater.iss", 7),
        )
        for script_name, minimum_count in scripts:
            installer_path = PROJECT_ROOT / "installer" / script_name
            source = installer_path.read_text(encoding="utf-8")
            catalogs = {}
            for language, key in re.findall(
                r"^(english|australian|spanish|french|german|brazilianportuguese)\."
                r"([A-Za-z0-9_]+)=",
                source,
                flags=re.MULTILINE,
            ):
                catalogs.setdefault(language, set()).add(key)
            expected = catalogs["english"]
            self.assertGreaterEqual(len(expected), minimum_count)
            self.assertEqual(len(catalogs), 6)
            for language, keys in catalogs.items():
                with self.subTest(script=script_name, language=language):
                    self.assertEqual(keys, expected)

    def test_about_page_discord_button_is_linked_and_fully_localized(self):
        self.assertEqual(
            self.tracker.DISCORD_COMMUNITY_URL,
            "https://discord.gg/fHkTRgqjcr",
        )
        for language in LOCALIZED_LANGUAGES:
            with self.subTest(language=language):
                translations = self.tracker.UI_TRANSLATIONS[language]
                for text in (
                    "Join Discord",
                    "Discord Could Not Be Opened",
                    (
                        "The Discord invite could not be opened in your "
                        "default browser. You can copy this address instead:"
                    ),
                ):
                    self.assertIn(text, translations)
                    self.assertTrue(translations[text].strip())

        tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
        about_method = next(
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
            and node.name == "open_about_dialog"
        )
        constants = {
            node.value
            for node in ast.walk(about_method)
            if isinstance(node, ast.Constant)
            and isinstance(node.value, str)
        }
        called_attributes = {
            node.attr
            for node in ast.walk(about_method)
            if isinstance(node, ast.Attribute)
        }
        self.assertIn("Join Discord", constants)
        self.assertIn("open_discord_community", called_attributes)

    def test_about_page_uses_stream_desk_ui_and_links_twitch_channel(self):
        for language in LOCALIZED_LANGUAGES:
            with self.subTest(language=language):
                translations = self.tracker.UI_TRANSLATIONS[language]
                self.assertTrue(translations["Twitch Channel"].strip())
                self.assertTrue(translations["ABOUT"].strip())

        source = MODULE_PATH.read_text(encoding="utf-8")
        tree = ast.parse(source)
        about_method = next(
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
            and node.name == "open_about_dialog"
        )
        about_source = ast.get_source_segment(source, about_method)
        self.assertIn("_uses_stream_desk_palette", about_source)
        self.assertIn('STREAM_DESK["yellow"]', about_source)
        self.assertIn("https://www.twitch.tv/freddogg23", about_source)
        self.assertIn('text="About"', about_source)
        self.assertIn('dialog.title("About - SMW Stream Tracker")', about_source)
        self.assertIn('before=about_card', about_source)
        self.assertIn('side="bottom"', about_source)
        self.assertIn("restore_order", about_source)
        self.assertNotIn('"Check for Updates"', about_source)
        self.assertNotIn("self.check_for_updates", about_source)

    def test_every_completion_row_is_available_in_every_language(self):
        for row in self.tracker._LOCALIZATION_COMPLETION_ROWS:
            english_text = row[0]
            for language in LOCALIZED_LANGUAGES:
                with self.subTest(text=english_text, language=language):
                    self.assertIn(
                        english_text,
                        self.tracker.UI_TRANSLATIONS[language],
                    )

    def test_tracker_refresh_status_prefers_larger_font_with_safe_shrinking(self):
        source = MODULE_PATH.read_text(encoding="utf-8")
        self.assertIn("chosen_size = 9", source)
        self.assertIn("for size in range(9, 3, -1):", source)
        self.assertIn('width=self._ui_px(265)', source)

    def test_downloader_completion_summary_uses_complete_templates(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        app.app_language = "de"

        summary = app._translate_ui_text(
            "Missing-only download completed. Newly built: {built}; "
            "existing skipped: {existing}; failed: {failed}; "
            "no link: {no_link}."
        ).format(
            built="2",
            existing="1",
            failed="0",
            no_link="0",
        )
        usb_summary = app._translate_ui_text(
            "USB uploaded: {uploaded}; already on FXPAK: {existing}; "
            "USB upload failed: {failed}."
        ).format(
            uploaded="1",
            existing="0",
            failed="0",
        )
        report_label = app._translate_ui_text("Reports were saved in:")
        rendered = " ".join((summary, usb_summary, report_label))

        self.assertIn("Download fehlender Hacks abgeschlossen", rendered)
        self.assertIn("Per USB hochgeladen", rendered)
        self.assertIn("Berichte wurden gespeichert unter", rendered)
        self.assertNotIn("Fehlt-only", rendered)
        self.assertNotIn("Missing-only", rendered)
        self.assertNotIn("Newly built", rendered)
        self.assertNotIn("USB uploaded", rendered)
        self.assertNotIn("Reports were saved in", rendered)

    def test_catalog_refresh_completion_uses_localized_dynamic_template(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        app.app_language = "de"

        rendered = app._translate_ui_text(
            "Live SMW Central catalog refresh complete. Pages checked: "
            "{pages}; hacks checked: {checked}; new: {new}; updated: "
            "{updated}; removed: {removed}; official catalog: {official}."
        ).format(
            pages="2",
            checked="25",
            new="1",
            updated="3",
            removed="0",
            official="2,753",
        )

        self.assertIn("Aktualisierung des Live-Katalogs", rendered)
        self.assertIn("Geprüfte Seiten: 2", rendered)
        self.assertIn("geprüfte Hacks: 25", rendered)
        self.assertNotIn("Pages checked", rendered)
        self.assertNotIn("hacks checked", rendered)

        tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
        completed_method = next(
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
            and node.name == "_finish_catalog_refresh"
        )
        called_attributes = {
            node.func.attr
            for node in ast.walk(completed_method)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
        }
        self.assertIn("_show_localized_info", called_attributes)

    def test_every_window_row_is_available_in_every_language(self):
        for row in self.tracker._WINDOW_LOCALIZATION_ROWS:
            english_text = row[0]
            for language in LOCALIZED_LANGUAGES:
                with self.subTest(text=english_text, language=language):
                    self.assertIn(
                        english_text,
                        self.tracker.UI_TRANSLATIONS[language],
                    )

    def test_named_pages_have_complete_control_translations(self):
        visible_labels = (
            "Updates",
            "Preferred service",
            "AutoStop:",
            "Exit completion by difficulty",
            "Search title or creator",
            "Reset Filters",
            "Spreadsheet Settings",
            "Google Sheets Settings",
            "Open SMW Central",
            "Edit Selected",
            "Open SMWCentral",
            "Launch Game",
            "Add to Tracker",
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
            (
                "The FXPAK Pro USB destination is not ready. Connect the USB "
                "data cable, power on the console and FXPAK Pro, and make sure "
                "QUsb2Snes shows the device."
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
        for language in LOCALIZED_LANGUAGES:
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

    def test_downloaded_indicator_sort_toggles_unchecked_then_checked(self):
        class FakeTree:
            def __init__(self):
                self.order = ["checked_a", "unchecked_a", "checked_b", "unchecked_b"]
                self.text = {
                    "checked_a": "☑",
                    "unchecked_a": "",
                    "checked_b": "☑",
                    "unchecked_b": "",
                }
                self.displayed_headings = {}

            def heading(self, column, **options):
                self.displayed_headings.setdefault(column, {}).update(options)

            def get_children(self, _parent=""):
                return tuple(self.order)

            def item(self, iid, option=None, **_options):
                if option == "text":
                    return self.text[iid]
                return {"text": self.text[iid]}

            def set(self, _iid, _column):
                return ""

            def set_children(self, _parent, *iids):
                self.order = list(iids)

        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        app.app_language = "en"
        tree = FakeTree()
        app._configure_treeview_sorting(
            tree,
            {"#0": "Downloaded"},
            presence_columns={"#0"},
        )

        app._sort_treeview_by_column(tree, "#0", toggle=True)
        self.assertEqual(
            tree.order,
            ["unchecked_a", "unchecked_b", "checked_a", "checked_b"],
        )

        app._sort_treeview_by_column(tree, "#0", toggle=True)
        self.assertEqual(
            tree.order,
            ["checked_a", "checked_b", "unchecked_a", "unchecked_b"],
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

        tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
        failure_method = next(
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
            and node.name == "_fail_fxpak_sd_action"
        )
        called_attributes = {
            node.func.attr
            for node in ast.walk(failure_method)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
        }
        self.assertIn("_show_localized_info", called_attributes)
        self.assertNotIn("showerror", called_attributes)

    def test_download_confirmation_is_fully_localized(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        app.app_language = "de"

        self.assertEqual(
            app._translate_ui_text("Download Moderated Hacks"),
            "Moderierte Hacks herunterladen",
        )
        question = app._translate_ui_text(
            "Download and patch {count} missing moderated hack(s)?"
        ).format(count="12")
        skip_note = app._translate_ui_text(
            "Games already found in the local library or mapped in the "
            "FXPAK game library will be skipped again immediately before "
            "each download."
        )

        self.assertIn("12 fehlende moderierte", question)
        self.assertNotIn("Download and patch", question)
        self.assertIn("unmittelbar vor jedem Download", skip_note)
        self.assertNotIn("Games already found", skip_note)

        tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
        download_method = next(
            node
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == "_start_filtered_hack_download"
        )
        called_attributes = {
            node.func.attr
            for node in ast.walk(download_method)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
        }
        self.assertIn("_ask_localized_yes_no", called_attributes)

    def test_download_confirmation_uses_live_language_selection(self):
        class FakeLanguageVar:
            def __init__(self, value):
                self.value = value

            def get(self):
                return self.value

        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        app.app_language = "en"
        app.config = {"app_language": "en"}
        confirmation_text = (
            "Download Moderated Hacks",
            "Download and patch {count} missing moderated hack(s)?",
            "Base ROM:",
            "Output library:",
            "Also upload each completed ROM through the FXPAK Pro USB "
            "connection to:",
            "Games already found in the local library or mapped in the "
            "FXPAK game library will be skipped again immediately before "
            "each download.",
            "Yes",
            "No",
        )

        for language in SELECTABLE_LOCALIZED_LANGUAGES:
            with self.subTest(language=language):
                app.language_var = FakeLanguageVar(language)
                self.assertEqual(app._active_language_code(), language)
                changed_count = 0
                for english_text in confirmation_text:
                    localized = app._translate_ui_text(english_text)
                    self.assertEqual(
                        localized,
                        self.tracker.UI_TRANSLATIONS[language][english_text],
                    )
                    if localized != english_text:
                        changed_count += 1
                self.assertGreaterEqual(
                    changed_count,
                    7,
                )

        # Australian remains available only as archived translation data for
        # existing documents/installers; it is no longer a selectable app UI.
        app.language_var = FakeLanguageVar("au")
        self.assertEqual(app._active_language_code(), "en")
        self.assertEqual(app._translate_ui_text("Yes"), "Yes")
        self.assertEqual(app._translate_ui_text("No"), "No")

        app.language_var = FakeLanguageVar("en")
        self.assertEqual(app._active_language_code(), "en")
        for english_text in confirmation_text:
            self.assertEqual(app._translate_ui_text(english_text), english_text)

    def test_waiting_refresh_confirmation_is_fully_localized(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        app.app_language = "de"
        title = "Refresh Waiting Hacks from SMW Central"
        message = (
            "Refresh waiting hacks directly from SMW Central's live "
            "catalog?\n\nWaiting entries are not moderated yet and "
            "will appear in bright red throughout the app."
        )

        localized_title = app._translate_dialog_text(title)
        localized_message = app._translate_dialog_text(message)

        self.assertEqual(
            localized_title,
            "Wartende Hacks von SMW Central aktualisieren",
        )
        self.assertIn("Wartende Hacks direkt", localized_message)
        self.assertIn("noch nicht moderiert", localized_message)
        self.assertIn("leuchtend rot", localized_message)
        self.assertNotIn("waiting hacks", localized_message)
        self.assertNotIn("not moderated", localized_message)
        self.assertEqual(app._translate_ui_text("Yes"), "Ja")
        self.assertEqual(app._translate_ui_text("No"), "Nein")

    def test_localized_dialogs_use_the_live_appearance_variable(self):
        tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
        methods = {
            node.name: node
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name in {
                "_show_stream_desk_message_dialog",
                "_ask_stream_desk_string",
            }
        }

        self.assertEqual(
            set(methods),
            {"_show_stream_desk_message_dialog", "_ask_stream_desk_string"},
        )
        for method_name, method in methods.items():
            with self.subTest(method=method_name):
                attributes = {
                    node.attr
                    for node in ast.walk(method)
                    if isinstance(node, ast.Attribute)
                }
                self.assertIn("appearance_var", attributes)
                self.assertNotIn("appearance_mode", attributes)

    def test_all_one_button_messages_use_the_stream_desk_app_dialog(self):
        tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
        installer = next(
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
            and node.name == "_install_localized_messageboxes"
        )
        source = ast.get_source_segment(
            MODULE_PATH.read_text(encoding="utf-8"),
            installer,
        )

        for message_name in ("showinfo", "showwarning", "showerror"):
            with self.subTest(message_name=message_name):
                self.assertIn(f'"{message_name}"', source)
        self.assertIn("self._show_localized_info(", source)
        self.assertIn('return "ok"', source)

    def test_optional_software_found_prompt_uses_stream_desk_app_dialog(self):
        tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
        methods = {
            node.name: node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
            and node.name in {
                "install_optional_software",
                "_ask_localized_yes_no",
                "_show_stream_desk_message_dialog",
            }
        }
        install_source = ast.get_source_segment(
            MODULE_PATH.read_text(encoding="utf-8"),
            methods["install_optional_software"],
        )
        wrapper_source = ast.get_source_segment(
            MODULE_PATH.read_text(encoding="utf-8"),
            methods["_ask_localized_yes_no"],
        )
        dialog_source = ast.get_source_segment(
            MODULE_PATH.read_text(encoding="utf-8"),
            methods["_show_stream_desk_message_dialog"],
        )

        self.assertIn(
            "use_existing = self._ask_localized_yes_no(",
            install_source,
        )
        self.assertIn("_show_stream_desk_message_dialog(", wrapper_source)
        self.assertIn('STREAM_DESK["surface_deep"]', dialog_source)
        self.assertIn('STREAM_DESK["green"]', dialog_source)
        self.assertNotIn('bg=THEME["blue"]', dialog_source)
        self.assertNotIn('bg=THEME["orange"]', dialog_source)

    def test_messagebox_info_warning_and_error_route_to_stream_desk_dialog_at_runtime(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        calls = []
        owner = object()
        app._translate_dialog_text = lambda value: f"localized:{value}"
        app._show_localized_info = (
            lambda title, message, parent=None: calls.append(
                (title, message, parent)
            )
        )

        app._install_localized_messageboxes()
        try:
            for name in ("showinfo", "showwarning", "showerror"):
                with self.subTest(name=name):
                    result = getattr(self.tracker.messagebox, name)(
                        "Title",
                        "Message",
                        parent=owner,
                    )
                    self.assertEqual(result, "ok")
        finally:
            for name, original in (
                self.tracker._ORIGINAL_MESSAGEBOX_FUNCTIONS.items()
            ):
                setattr(self.tracker.messagebox, name, original)

        self.assertEqual(
            calls,
            [
                ("localized:Title", "localized:Message", owner),
                ("localized:Title", "localized:Message", owner),
                ("localized:Title", "localized:Message", owner),
            ],
        )

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
        for language in LOCALIZED_LANGUAGES:
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
            "Preferred Service",
            "Import / Refresh from Spreadsheet…",
            "OBS Text Files",
            "Local ROM Library",
            "QUsb2Snes Application",
            "SNI Application",
            "RetroArch Application",
            "RetroArch Core",
            "Appearance",
            "App Language",
            "Timer & LiveSplit Settings",
            "AutoStop:",
            "seconds",
            "Game LiveSplit port:",
            "Level LiveSplit port:",
            "LiveSplit Timers Setup...",
            "Save Settings",
            "Cancel",
            "Browse",
        )
        for language in LOCALIZED_LANGUAGES:
            for label in visible_labels:
                with self.subTest(language=language, label=label):
                    self.assertIn(
                        label,
                        self.tracker.UI_TRANSLATIONS[language],
                    )


if __name__ == "__main__":
    unittest.main()
