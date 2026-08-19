import importlib.util
import inspect
import io
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest import mock


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER.py"
)


def load_tracker_module():
    spec = importlib.util.spec_from_file_location(
        "smw_tracker_import_backup_google_test",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class TrackerImportBackupGoogleSyncTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tracker = load_tracker_module()

    def test_current_excel_export_round_trips_back_into_tracker(self):
        with tempfile.TemporaryDirectory(
            ignore_cleanup_errors=True
        ) as temporary_directory:
            root = Path(temporary_directory)
            source = self.tracker.TrackerDatabase(root / "source.db")
            source.complete_hack(
                {
                    "title": "Round Trip World",
                    "author": "Import Tester",
                    "total_exits": 4,
                    "difficulty": "Advanced",
                    "hack_type": "Kaizo",
                    "rating": 4.75,
                    "is_custom": True,
                },
                completed_exits=4,
                total_exits=4,
                playtime_seconds=3723,
                rating=4.5,
                notes="Round-trip note",
                total_deaths=27,
            )
            workbook_path = root / "tracker.xlsx"
            source.export_tracker_xlsx(workbook_path)

            destination = self.tracker.TrackerDatabase(
                root / "destination.db"
            )
            summary = destination.import_workbook(workbook_path)
            rows = destination.list_tracked()

            self.assertEqual(summary["tracked"], 1)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["title"], "Round Trip World")
            self.assertEqual(rows[0]["playtime_seconds"], 3723)
            self.assertEqual(rows[0]["total_deaths"], 27)
            self.assertEqual(rows[0]["personal_rating"], 4.5)
            self.assertEqual(rows[0]["notes"], "Round-trip note")

    def test_smart_import_recognizes_renamed_sheet_headers_and_title_rows(self):
        with tempfile.TemporaryDirectory(
            ignore_cleanup_errors=True
        ) as temporary_directory:
            root = Path(temporary_directory)
            workbook_path = root / "renamed-google-export.xlsx"
            workbook = self.tracker.Workbook()
            sheet = workbook.active
            sheet.title = "SMW Stream Tracker - Tracker"
            sheet.append(["My synchronized tracker data"])
            sheet.append([])
            sheet.append(
                [
                    "Number",
                    "Game Name",
                    "Creator",
                    "Total Exits",
                    "Cleared Exits",
                    "Progress",
                    "Difficulty Level",
                    "Hack Category",
                    "Official Rating",
                    "My Score",
                    "Time Played",
                    "Started",
                    "Finished",
                    "Deaths",
                    "Comments",
                    "SMW Central Page",
                ]
            )
            sheet.append(
                [
                    1,
                    "Recovered World",
                    "Recovery Tester",
                    7,
                    7,
                    "Completed",
                    "Expert",
                    "Kaizo",
                    4.8,
                    4.6,
                    "02:03:04",
                    "2026-08-01",
                    "2026-08-02",
                    123,
                    "Recovered by smart import",
                    "https://www.smwcentral.net/?a=details&id=45678&p=section",
                ]
            )
            workbook.save(workbook_path)
            workbook.close()

            destination = self.tracker.TrackerDatabase(
                root / "destination.db"
            )
            summary = destination.import_workbook(workbook_path)
            rows = destination.list_tracked()

            self.assertEqual(summary["tracked"], 1)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["title"], "Recovered World")
            self.assertEqual(rows[0]["author"], "Recovery Tester")
            self.assertEqual(rows[0]["completed_exits"], 7)
            self.assertEqual(rows[0]["total_deaths"], 123)
            self.assertEqual(rows[0]["personal_rating"], 4.6)
            self.assertEqual(rows[0]["playtime_seconds"], 7384)
            self.assertEqual(rows[0]["catalog_key"], "SMWC:45678")
            self.assertEqual(
                rows[0]["notes"],
                "Recovered by smart import",
            )

    def test_smart_import_uses_cell_values_for_unlabeled_categories(self):
        with tempfile.TemporaryDirectory(
            ignore_cleanup_errors=True
        ) as temporary_directory:
            root = Path(temporary_directory)
            workbook_path = root / "content-inference.xlsx"
            workbook = self.tracker.Workbook()
            sheet = workbook.active
            sheet.title = "Old Progress Log"
            sheet.append(
                [
                    "Game",
                    "Creator",
                    "Data A",
                    "Data B",
                    "Data C",
                    "Data D",
                ]
            )
            sheet.append(
                [
                    "Content Match World",
                    "Cell Reader",
                    "Expert",
                    "Kaizo",
                    "Completed",
                    "03:04:05",
                ]
            )
            workbook.save(workbook_path)
            workbook.close()

            destination = self.tracker.TrackerDatabase(
                root / "destination.db"
            )
            summary = destination.import_workbook(workbook_path)
            row = destination.list_tracked()[0]

            self.assertEqual(summary["tracked"], 1)
            self.assertEqual(row["difficulty"], "Expert")
            self.assertEqual(row["hack_type"], "Kaizo")
            self.assertEqual(row["status"], "Completed")
            self.assertEqual(row["playtime_seconds"], 11045)

    def test_google_script_supports_readback_and_current_columns(self):
        script = self.tracker.GOOGLE_SHEETS_APPS_SCRIPT
        for expected in (
            "function doGet(e)",
            "action || '') !== 'read'",
            "headers: headers, rows: rows",
            "'Total Deaths'",
            "'Playtime Seconds'",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, script)

    def test_google_settings_has_pull_sync_button(self):
        source = inspect.getsource(
            self.tracker.TrackerApp.open_google_sheets_sync
        )
        self.assertIn('text="Sync from Google Sheets"', source)
        self.assertIn("self._start_google_sheets_import(", source)
        self.assertIn('text="Close"', source)
        self.assertIn('dialog.bind(\n            "<Escape>"', source)

    def test_my_tracker_consolidates_spreadsheet_and_google_controls(self):
        source = inspect.getsource(
            self.tracker.TrackerApp.open_my_tracker
        )
        self.assertIn('"Spreadsheet Settings"', source)
        self.assertIn('"Google Sheets Settings"', source)
        self.assertIn('"Open SMW Central"', source)
        self.assertIn('"Launch Game"', source)
        self.assertIn("make_tracker_circle_action", source)
        self.assertIn('"+"', source)
        self.assertIn('"−"', source)
        self.assertNotIn('text="Edit Selected"', source)
        self.assertNotIn('"Sync to Google Sheets Now"', source)
        self.assertNotIn("spreadsheet_bar = tk.Frame", source)

    def test_spreadsheet_settings_uses_stream_desk_import_export_card(self):
        source = inspect.getsource(
            self.tracker.TrackerApp.open_spreadsheet_settings
        )
        self.assertIn("dialog._uses_stream_desk_palette = True", source)
        self.assertIn("self._create_stream_desk_page_header(", source)
        self.assertIn('footer.pack(side="bottom", fill="x")', source)
        self.assertIn('text="Import Spreadsheet..."', source)
        self.assertIn('text="Export My Tracker..."', source)

    def test_library_palette_exposes_colors_used_by_stream_desk_dialogs(self):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        for appearance, expected_palette in (
            ("dark", self.tracker.STREAM_DESK_DARK),
            ("light", self.tracker.STREAM_DESK_LIGHT),
        ):
            with self.subTest(appearance=appearance):
                app.appearance_var = mock.Mock()
                app.appearance_var.get.return_value = appearance
                palette = app._library_palette()
                for color_name in ("text_strong", "blue", "blue_dark"):
                    with self.subTest(
                        appearance=appearance,
                        color_name=color_name,
                    ):
                        self.assertEqual(
                            palette[color_name],
                            expected_palette[color_name],
                        )

    def test_every_stream_desk_color_lookup_exists_in_both_themes(self):
        source = MODULE_PATH.read_text(encoding="utf-8")
        used_colors = set(
            re.findall(r'STREAM_DESK\["([^"]+)"\]', source)
        )
        self.assertFalse(used_colors - set(self.tracker.STREAM_DESK_DARK))
        self.assertFalse(used_colors - set(self.tracker.STREAM_DESK_LIGHT))

    def test_google_settings_uses_stream_desk_and_includes_both_import_routes(self):
        source = inspect.getsource(
            self.tracker.TrackerApp.open_google_sheets_sync
        )
        self.assertIn("dialog._uses_stream_desk_palette = True", source)
        self.assertIn("self._create_stream_desk_page_header(", source)
        self.assertIn('button_bar.pack(side="bottom", fill="x")', source)
        self.assertIn('text="Google Sheets sharing link (import):"', source)
        self.assertIn("self._start_google_sheet_link_import(", source)
        self.assertIn("self._start_google_sheets_import(", source)

    def test_normal_google_sheet_link_converts_to_xlsx_export(self):
        source_url = (
            "https://docs.google.com/spreadsheets/d/"
            "abc_DEF-123/edit?usp=sharing#gid=42"
        )
        self.assertEqual(
            self.tracker.TrackerApp._google_sheet_export_url(source_url),
            (
                "https://docs.google.com/spreadsheets/d/"
                "abc_DEF-123/export?format=xlsx"
            ),
        )
        with self.assertRaises(ValueError):
            self.tracker.TrackerApp._google_sheet_export_url(
                "https://example.com/not-a-sheet"
            )

    def test_google_sheet_link_worker_downloads_a_valid_workbook(self):
        workbook_stream = io.BytesIO()
        workbook = self.tracker.Workbook()
        workbook.active.title = "My Tracker"
        workbook.active.append(["ROM Hack Title"])
        workbook.active.append(["Imported World"])
        workbook.save(workbook_stream)
        workbook.close()

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def read(self, _limit):
                return workbook_stream.getvalue()

        class ImmediateRoot:
            @staticmethod
            def after(_delay, callback):
                callback()

        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        app.root = ImmediateRoot()
        captured = {}

        def finish(path, row_count, error_text):
            captured.update(
                path=path,
                row_count=row_count,
                error_text=error_text,
            )

        app._finish_google_sheets_import = finish
        with mock.patch.object(
            self.tracker,
            "urlopen",
            return_value=FakeResponse(),
        ):
            app._google_sheet_link_import_worker(
                "https://docs.google.com/spreadsheets/d/test/export?format=xlsx"
            )
        workbook_path = captured["path"]
        try:
            self.assertEqual(captured["error_text"], "")
            self.assertTrue(workbook_path.exists())
            imported = self.tracker.load_workbook(
                workbook_path,
                read_only=True,
            )
            try:
                self.assertIn("My Tracker", imported.sheetnames)
            finally:
                imported.close()
        finally:
            workbook_path.unlink(missing_ok=True)

    def test_spreadsheet_import_refreshes_an_open_tracker_immediately(self):
        source = inspect.getsource(
            self.tracker.TrackerApp.import_existing_spreadsheet
        )
        self.assertIn("self._tracker_list_ui_is_alive()", source)
        self.assertIn("self._refresh_my_tracker()", source)

    def test_tracker_ui_liveness_requires_both_page_and_table(self):
        class Widget:
            def __init__(self, exists):
                self.exists = exists

            def winfo_exists(self):
                return self.exists

        app = self.tracker.TrackerApp.__new__(
            self.tracker.TrackerApp
        )
        app.tracker_list_dialog = Widget(True)
        app.tracker_list_widgets = {"tree": Widget(True)}
        self.assertTrue(app._tracker_list_ui_is_alive())

        app.tracker_list_widgets["tree"] = Widget(False)
        self.assertFalse(app._tracker_list_ui_is_alive())

    def test_each_recovery_backup_call_creates_a_separate_file(self):
        with tempfile.TemporaryDirectory(
            ignore_cleanup_errors=True
        ) as temporary_directory:
            root = Path(temporary_directory)
            database = self.tracker.TrackerDatabase(root / "tracker.db")
            database.add_to_tracker({"title": "Backup World"})
            app = self.tracker.TrackerApp.__new__(
                self.tracker.TrackerApp
            )
            app.stats_db = database
            app.config = {"automatic_backup_retention": 10}
            automatic_directory = root / "automatic"
            with mock.patch.multiple(
                self.tracker,
                AUTOMATIC_BACKUP_DIR=automatic_directory,
                CONFIG_FILE=root / "missing-config.json",
                TIMER_SAVE_FILE=root / "missing-times.json",
                DEATH_SAVE_FILE=root / "missing-deaths.json",
                LEVEL_PROGRESS_SAVE_FILE=root / "missing-levels.json",
            ):
                first = app._create_recovery_backup("exit")
                second = app._create_recovery_backup("exit")

            self.assertIsNotNone(first)
            self.assertIsNotNone(second)
            self.assertNotEqual(first, second)
            self.assertTrue(first.is_file())
            self.assertTrue(second.is_file())
            self.assertEqual(
                len(list(automatic_directory.glob("*.zip"))),
                2,
            )

    def test_permanent_excel_backup_is_outside_uninstall_app_data(self):
        backup = self.tracker.PERSISTENT_TRACKER_BACKUP_FILE.resolve()
        app_data = self.tracker.APP_DATA_DIR.resolve()
        self.assertFalse(backup.is_relative_to(app_data))
        self.assertIn("Documents", backup.parts)
        self.assertEqual(backup.suffix.casefold(), ".xlsx")

    def test_automatic_excel_backup_worker_writes_a_valid_workbook(self):
        class ImmediateRoot:
            @staticmethod
            def after(_delay, callback):
                callback()
                return "immediate"

        class Status:
            value = ""

            def set(self, value):
                self.value = value

        with tempfile.TemporaryDirectory(
            ignore_cleanup_errors=True
        ) as temporary_directory:
            root = Path(temporary_directory)
            database = self.tracker.TrackerDatabase(root / "tracker.db")
            database.add_to_tracker(
                {
                    "title": "Permanent Backup World",
                    "author": "Backup Tester",
                    "total_exits": 2,
                }
            )
            original_directory = self.tracker.PERSISTENT_TRACKER_BACKUP_DIR
            original_file = self.tracker.PERSISTENT_TRACKER_BACKUP_FILE
            backup_directory = root / "permanent"
            backup_file = backup_directory / "automatic.xlsx"
            self.tracker.PERSISTENT_TRACKER_BACKUP_DIR = backup_directory
            self.tracker.PERSISTENT_TRACKER_BACKUP_FILE = backup_file
            try:
                app = self.tracker.TrackerApp.__new__(
                    self.tracker.TrackerApp
                )
                app.root = ImmediateRoot()
                app.status_var = Status()
                app.stats_db = database
                app.tracker_excel_backup_thread = None
                app.tracker_excel_backup_pending = False
                app._automatic_tracker_excel_backup_worker()
                self.assertTrue(backup_file.exists())
                workbook = self.tracker.load_workbook(
                    backup_file,
                    data_only=True,
                )
                try:
                    self.assertIn("My Tracker", workbook.sheetnames)
                    self.assertEqual(
                        workbook["My Tracker"]["B2"].value,
                        "Permanent Backup World",
                    )
                finally:
                    workbook.close()
            finally:
                self.tracker.PERSISTENT_TRACKER_BACKUP_DIR = (
                    original_directory
                )
                self.tracker.PERSISTENT_TRACKER_BACKUP_FILE = original_file

    def test_all_tracker_changes_queue_permanent_excel_backup(self):
        source = inspect.getsource(
            self.tracker.TrackerApp._queue_google_sheets_sync
        )
        self.assertIn(
            "self._queue_automatic_tracker_excel_backup()",
            source,
        )

    def test_all_game_mode_dialog_headers_use_stream_desk_chrome(self):
        shell_source = inspect.getsource(
            self.tracker.TrackerApp._game_mode_dialog_shell
        )
        random_source = inspect.getsource(
            self.tracker.TrackerApp._play_random_main_hack
        )
        self.assertIn('bg=palette["window"]', shell_source)
        self.assertIn('bg=palette["panel"]', shell_source)
        self.assertIn('fg=STREAM_DESK["yellow"]', shell_source)
        self.assertIn("_game_mode_dialog_shell", random_source)
        self.assertNotIn('bg=THEME["blue"]', shell_source)
        self.assertNotIn('bg=THEME["blue"]', random_source)

    def test_new_interface_text_is_translated_in_every_language(self):
        phrases = (
            "Sync from Google Sheets",
            "Sync to Google Sheets Now",
            "Paste a Google Sheets Link",
            "Google Sheets link:",
            (
                "Paste the normal sharing link for your Google Sheet. "
                "Share it as Viewer with Anyone with the link first. "
                "The workbook must contain a Tracker or My Tracker tab."
            ),
            "Import Now",
            "Paste a valid Google Sheets sharing link.",
            (
                "Google could not export this sheet as an Excel workbook. "
                "Make sure it is shared as Viewer with Anyone with the link."
            ),
            "Google Sheets Import",
            "Google Sheets Import Failed",
            "Google Sheets Import Complete",
            "Synchronizing from Google Sheets…",
            "Open Automatic Tracker Excel Backup Folder",
        )
        for language in ("au", "es", "fr", "de", "pt-BR"):
            translations = self.tracker.UI_TRANSLATIONS[language]
            for phrase in phrases:
                with self.subTest(language=language, phrase=phrase):
                    self.assertIn(phrase, translations)
                    self.assertNotEqual(translations[phrase], phrase)


if __name__ == "__main__":
    unittest.main()
