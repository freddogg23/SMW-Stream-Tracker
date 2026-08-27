import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import zipfile

from release_tools import build_smwc_music_index as builder


def _page(page, last_page):
    return {
        "last_page": last_page,
        "data": [
            {
                "id": str(page),
                "name": f"Song {page}",
                "time": str(1000 + page),
            }
        ],
    }


class SmwcMusicIndexBuilderTests(unittest.TestCase):
    def test_amk_previews_supersede_legacy_copies_but_keep_variants(self):
        with tempfile.TemporaryDirectory() as temp_folder:
            archive_path = Path(temp_folder) / "music.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("Song.spc", b"legacy")
                archive.writestr("Song.amk.spc", b"amk")
                archive.writestr("Song-Fluted.amk.spc", b"variant")
                archive.writestr("readme.txt", b"notes")

            members = builder._spc_members(archive_path)

            self.assertEqual(
                [member.filename for member in members],
                ["Song.amk.spc", "Song-Fluted.amk.spc"],
            )

    def test_completed_cache_stays_complete_after_incremental_check(self):
        with tempfile.TemporaryDirectory() as temp_folder:
            catalog_path = Path(temp_folder) / "catalog.json"
            catalog_path.write_text(
                json.dumps(
                    {
                        "complete": True,
                        "submissions": {
                            str(page): _page(page, 3)["data"][0]
                            for page in range(1, 4)
                        },
                    }
                ),
                encoding="utf-8",
            )
            with (
                mock.patch.object(
                    builder,
                    "_request_json",
                    side_effect=[_page(1, 3), _page(2, 3)],
                ) as request,
                mock.patch.object(builder.time, "sleep"),
            ):
                submissions, complete = builder.fetch_catalog(catalog_path)

            self.assertTrue(complete)
            self.assertEqual(len(submissions), 3)
            self.assertEqual(request.call_count, 2)

    def test_partial_cache_must_finish_every_catalog_page(self):
        with tempfile.TemporaryDirectory() as temp_folder:
            catalog_path = Path(temp_folder) / "catalog.json"
            catalog_path.write_text(
                json.dumps(
                    {
                        "complete": False,
                        "submissions": {
                            "1": _page(1, 3)["data"][0],
                            "2": _page(2, 3)["data"][0],
                        },
                    }
                ),
                encoding="utf-8",
            )
            with (
                mock.patch.object(
                    builder,
                    "_request_json",
                    side_effect=[_page(1, 3), _page(2, 3), _page(3, 3)],
                ) as request,
                mock.patch.object(builder.time, "sleep"),
            ):
                submissions, complete = builder.fetch_catalog(catalog_path)

            self.assertTrue(complete)
            self.assertEqual(len(submissions), 3)
            self.assertEqual(request.call_count, 3)


if __name__ == "__main__":
    unittest.main()
