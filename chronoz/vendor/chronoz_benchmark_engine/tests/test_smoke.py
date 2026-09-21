"""Opt-in real-data smoke: supply CHRONOZ_TEST_DATA_ROOT, never infer a repo root."""
import os
from pathlib import Path
import unittest
from chronoz_benchmark import BenchmarkService


@unittest.skipUnless(os.environ.get("CHRONOZ_TEST_DATA_ROOT"), "Set CHRONOZ_TEST_DATA_ROOT for repository-data smoke tests")
class RepositorySmokeTests(unittest.TestCase):
    def setUp(self):
        self.service = BenchmarkService(Path(os.environ["CHRONOZ_TEST_DATA_ROOT"]))

    def test_required_three_series_packet(self):
        packet = self.service.get_packet(["PPIACO", "INDPRO", "TCU"])
        packet.validate()
        self.assertEqual(len(packet.relationships), 3)
        for indicator in packet.indicators.values():
            self.assertIsNotNone(indicator["historical"]["score"])
            self.assertEqual(indicator["rolling"]["100"]["n"], 100)

    def test_all_36_research_selections(self):
        ids = list(self.service.registry.series)
        packet = self.service.get_packet(ids)
        self.assertEqual(len(packet.indicators), 36)
        self.assertEqual(len(packet.relationships), 630)
        self.assertEqual({i["model_family"] for i in packet.indicators.values()},
                         {"STANDARD_DELTA", "ROBUST_DELTA", "DISCRETE_DELTA", "DISCRETE_PLUS_SHOCK",
                          "REGIME_ROBUST_DELTA", "STRUCTURAL_EPOCH_ROBUST_DELTA"})

    def test_pcec_current_research_snapshot_reconciles(self):
        p = self.service.get_series(["PCEC96"])["PCEC96"]
        # Snapshot-specific regression only when dates and source count match the audit.
        details = p["historical"]["model_specific"]
        if p["latest_date"] != "2026-07-01" or details["history_count"] != 234:
            self.skipTest("External data is a different snapshot from the 2026-09-20 audit")
        self.assertEqual(details["eligible_count"], 233)
        self.assertEqual(details["excluded_from_calibration_count"], 12)
        self.assertEqual(details["calibration_count"], 221)
        self.assertAlmostEqual(p["historical"]["dispersion"], .2717, places=4)
