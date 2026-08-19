import importlib.util
import json
from pathlib import Path
import sys
import threading
import unittest
from unittest import mock
from urllib.error import HTTPError


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = (
    PROJECT_ROOT
    / "SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER.py"
)


def load_tracker_module():
    spec = importlib.util.spec_from_file_location(
        "smw_tracker_cloudflare_fallback_test",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class _JsonResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


class _ImmediateRoot:
    def after(self, _delay, callback):
        callback()


class _CatalogDatabase:
    def __init__(self, catalog=None):
        self.catalog = list(catalog or [])

    def load_catalog(self):
        return list(self.catalog)


class SmwcentralCloudflareFallbackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tracker = load_tracker_module()

    def test_http_522_is_retried(self):
        first_error = HTTPError(
            "https://www.smwcentral.net/ajax.php",
            522,
            "Connection timed out",
            {},
            None,
        )
        response = _JsonResponse({"data": []})

        with mock.patch.object(
            self.tracker,
            "urlopen",
            side_effect=(first_error, response),
        ) as urlopen_mock, mock.patch.object(
            self.tracker,
            "smwc_throttle_request",
        ), mock.patch.object(
            self.tracker,
            "smwc_cancelable_wait",
        ) as wait_mock:
            payload = self.tracker.smwc_api_json(
                {"a": "getsectionlist"},
                max_retries=2,
            )

        self.assertEqual(payload, {"data": []})
        self.assertEqual(urlopen_mock.call_count, 2)
        wait_mock.assert_called_once()
        self.assertIn(
            522,
            self.tracker.SMWC_API_TRANSIENT_HTTP_CODES,
        )

    def _worker_app(self, catalog=None):
        app = self.tracker.TrackerApp.__new__(self.tracker.TrackerApp)
        app.stats_db = _CatalogDatabase(catalog)
        app.catalog_refresh_cancel_event = threading.Event()
        app.root = _ImmediateRoot()
        app._catalog_refresh_progress = mock.Mock()
        app._finish_catalog_refresh = mock.Mock()
        return app

    def test_moderated_refresh_uses_github_after_live_timeout(self):
        app = self._worker_app()
        github_summary = {
            "status": "refreshed",
            "fetched": 2800,
            "new": 4,
            "updated": 2,
            "removed": 0,
            "official": 2800,
        }

        with mock.patch.object(
            self.tracker,
            "refresh_catalog_from_smwcentral_site",
            side_effect=RuntimeError("HTTP 522"),
        ), mock.patch.object(
            self.tracker,
            "refresh_catalog_from_github_repository",
            return_value=github_summary,
        ) as github_refresh:
            app._catalog_refresh_worker(waiting=False)

        github_refresh.assert_called_once()
        summary, error_message = app._finish_catalog_refresh.call_args.args
        self.assertEqual(error_message, "")
        self.assertTrue(summary["fallback_from_live"])
        self.assertEqual(summary["official"], 2800)

    def test_saved_catalog_remains_available_if_both_sources_fail(self):
        app = self._worker_app(
            [{"title": "Saved One"}, {"title": "Saved Two"}]
        )

        with mock.patch.object(
            self.tracker,
            "refresh_catalog_from_smwcentral_site",
            side_effect=RuntimeError("HTTP 522"),
        ), mock.patch.object(
            self.tracker,
            "refresh_catalog_from_github_repository",
            side_effect=RuntimeError("GitHub unavailable"),
        ):
            app._catalog_refresh_worker(waiting=False)

        summary, error_message = app._finish_catalog_refresh.call_args.args
        self.assertEqual(error_message, "")
        self.assertEqual(summary["status"], "saved_catalog")
        self.assertEqual(summary["official"], 2)
        self.assertTrue(summary["fallback_cached"])


if __name__ == "__main__":
    unittest.main()
