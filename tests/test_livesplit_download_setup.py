import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = (
    PROJECT_ROOT
    / "SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER.py"
)


def load_tracker_module():
    spec = importlib.util.spec_from_file_location(
        "smw_tracker_livesplit_download_test",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class LiveSplitDownloadSetupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tracker = load_tracker_module()

    @staticmethod
    def release_payload(url=None, size=15_869_856):
        return {
            "tag_name": "1.8.37",
            "assets": [
                {
                    "name": "LiveSplit_1.8.37.zip",
                    "size": size,
                    "browser_download_url": url
                    or (
                        "https://github.com/LiveSplit/LiveSplit/releases/"
                        "download/1.8.37/LiveSplit_1.8.37.zip"
                    ),
                    "digest": (
                        "sha256:"
                        "14bc8ef8ded9ef4033fb2f0cb6a152386d393127da18a4de"
                        "14f096c5347aa991"
                    ),
                }
            ],
        }

    def test_official_release_asset_is_selected_with_its_checksum(self):
        asset = self.tracker.select_livesplit_release_asset(
            self.release_payload()
        )
        self.assertEqual(asset["name"], "LiveSplit_1.8.37.zip")
        self.assertEqual(asset["version"], "1.8.37")
        self.assertEqual(
            asset["sha256"],
            "14bc8ef8ded9ef4033fb2f0cb6a152386d393127da18a4de"
            "14f096c5347aa991",
        )

    def test_release_asset_rejects_nonofficial_hosts_and_oversized_files(self):
        with self.assertRaises(RuntimeError):
            self.tracker.select_livesplit_release_asset(
                self.release_payload(
                    url="https://example.com/LiveSplit_1.8.37.zip"
                )
            )
        with self.assertRaises(RuntimeError):
            self.tracker.select_livesplit_release_asset(
                self.release_payload(
                    size=self.tracker.LIVESPLIT_RELEASE_MAX_BYTES + 1
                )
            )

    def test_new_settings_configures_port_and_tcp_auto_start(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            settings_path = Path(temporary_directory) / "settings.cfg"
            self.tracker.write_livesplit_tracker_settings(
                settings_path,
                16835,
            )
            root = ET.parse(settings_path).getroot()
            self.assertEqual(root.tag, "Settings")
            self.assertEqual(root.findtext("ServerPort"), "16835")
            self.assertEqual(root.findtext("ServerStartup"), "1")
            self.assertIsNotNone(root.find("HotkeyProfiles"))
            self.assertIsNotNone(root.find("RecentSplits"))
            self.assertIsNotNone(root.find("RecentLayouts"))
            self.assertIsNotNone(root.find("RaceProviderPlugins"))

    def test_existing_settings_keep_other_values_when_port_is_updated(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            settings_path = Path(temporary_directory) / "settings.cfg"
            settings_path.write_text(
                "<?xml version='1.0' encoding='utf-8'?>"
                "<Settings version='1.8.18'>"
                "<ServerPort>11111</ServerPort>"
                "<ServerStartup>0</ServerStartup>"
                "<CustomValue>keep me</CustomValue>"
                "</Settings>",
                encoding="utf-8",
            )
            self.tracker.write_livesplit_tracker_settings(
                settings_path,
                16834,
            )
            root = ET.parse(settings_path).getroot()
            self.assertEqual(root.findtext("ServerPort"), "16834")
            self.assertEqual(root.findtext("ServerStartup"), "1")
            self.assertEqual(root.findtext("CustomValue"), "keep me")


if __name__ == "__main__":
    unittest.main()
