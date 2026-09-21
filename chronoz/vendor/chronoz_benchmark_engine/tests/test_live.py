import unittest
import numpy as np
from chronoz_benchmark.models.standard_delta import StandardDelta
from chronoz_benchmark.models.discrete_delta import DiscreteDelta
from chronoz_benchmark.live.rolling import calculate_rolling
from chronoz_benchmark.live.acceleration import calculate_acceleration
from chronoz_benchmark.live.relationships import rolling_relationship
from chronoz_benchmark.historical.relationships import HistoricalRelationships
from tests.helpers import ROOT, DEFAULTS, spec, frame, delta_frame


class LiveTests(unittest.TestCase):
    def test_rolling_stats_elevation_local_and_sample_std(self):
        f = delta_frame(np.arange(101.))
        model = StandardDelta(spec("PPIACO"), DEFAULTS).fit(f)
        r = calculate_rolling(f, spec("PPIACO"), model, [10, 20, 50, 100], DEFAULTS)
        self.assertEqual(r["10"]["n"], 10)
        self.assertEqual(r["10"]["mean"], 95.5)
        self.assertEqual(r["10"]["MAD"], 2.5)
        self.assertAlmostEqual(r["10"]["std"], np.std(np.arange(91., 101.), ddof=1))
        self.assertAlmostEqual(r["10"]["rolling_elevation"], (95.5 - 50) / np.std(np.arange(101.), ddof=1))
        self.assertAlmostEqual(r["10"]["local_score"], 4.5 / r["10"]["std"])

    def test_rolling_gap_never_compressed(self):
        f = delta_frame(np.arange(101.)).drop(index=95).reset_index(drop=True)
        model = StandardDelta(spec("PPIACO"), DEFAULTS).fit(f)
        r = calculate_rolling(f, spec("PPIACO"), model, [10], DEFAULTS)["10"]
        self.assertEqual(r["n"], 9)
        self.assertIsNone(r["rolling_elevation"])
        self.assertEqual(r["mean"], np.mean([x for x in range(91, 101) if x != 95]))

    def test_discrete_is_not_forced_into_gaussian_elevation(self):
        f = delta_frame([0., .1, -.1] * 50)
        model = DiscreteDelta(spec("AWHAETP"), DEFAULTS).fit(f)
        r = calculate_rolling(f, spec("AWHAETP"), model, [10], DEFAULTS)["10"]
        self.assertIsNone(r["rolling_elevation"])
        self.assertIsNone(r["local_score"])
        self.assertEqual(r["n"], 10)

    def test_acceleration_patterns(self):
        for values, expected in [([4, 3, 2, 1], "BROAD_ACCELERATION"), ([1, 2, 3, 4], "BROAD_DECELERATION"),
                                 ([3, 1, 2, 2], "SHORT_TERM_ACCELERATION"), ([0, 2, 1, 1], "SHORT_TERM_DECELERATION"),
                                 ([3, 2, 3, 2], "MIXED"), ([1, 1, 1, 1], "MIXED"), ([1, None, 3, 4], "UNAVAILABLE")]:
            r = {str(h): {"rolling_elevation": v} for h, v in zip((10, 20, 50, 100), values)}
            self.assertEqual(calculate_acceleration(r)["pattern"], expected)
        self.assertEqual(calculate_acceleration({})["pattern"], "UNAVAILABLE")

    def test_historical_lookup_lag_orientation_and_missing(self):
        lookup = HistoricalRelationships(ROOT / "config" / "historical_relationships.json")
        hist, _ = lookup.lookup("INDPRO", "TCU")
        self.assertAlmostEqual(hist["pearson"], .9836908972962007)
        self.assertTrue(hist["redundancy_candidate"])
        record = next(r for r in lookup.records.values() if r["best_descriptive_lag"] != 0)
        a, _ = lookup.lookup(record["series_a"], record["series_b"])
        b, _ = lookup.lookup(record["series_b"], record["series_a"])
        self.assertEqual(a["best_descriptive_lag"], -b["best_descriptive_lag"])
        empty, notes = lookup.lookup("ICSA", "TCU")
        self.assertIsNone(empty["pearson"])
        self.assertTrue(any("No historical" in n for n in notes))

    def test_rolling_correlations_match_direct_research_percent_changes(self):
        a = frame(100 + np.arange(140.) + 2 * np.sin(np.arange(140.)))
        b = frame(90 + .8 * np.arange(140.) + 3 * np.cos(np.arange(140.)))
        r, _, methods = rolling_relationship(a, spec("PPIACO"), b, spec("INDPRO"), [10, 20, 50, 100], DEFAULTS)
        x = 100 * (a.value / a.value.shift() - 1)
        y = 100 * (b.value / b.value.shift() - 1)
        for h in (10, 20, 50, 100):
            self.assertEqual(r[str(h)]["n"], h)
            self.assertAlmostEqual(r[str(h)]["pearson"], x.tail(h).corr(y.tail(h)))
            self.assertAlmostEqual(r[str(h)]["spearman"], x.tail(h).rank().corr(y.tail(h).rank()))
        self.assertEqual(methods["series_a"], "PERCENT_CHANGE")

    def test_relationship_gap_sample_floor_and_constant_window(self):
        a = frame(np.arange(1., 141.))
        b = a.drop(index=[131, 134, 137]).reset_index(drop=True)
        r, _, _ = rolling_relationship(a, spec("PPIACO"), b, spec("INDPRO"), [10], DEFAULTS)
        self.assertEqual(r["10"]["n"], 4)
        self.assertIsNone(r["10"]["pearson"])
        constant = frame(np.ones(140))
        r, _, _ = rolling_relationship(a, spec("PPIACO"), constant, spec("TCU"), [10], DEFAULTS)
        self.assertIsNone(r["10"]["pearson"])

    def test_frequency_and_weekday_mismatch(self):
        a, b = frame(np.arange(1., 141.)), frame(np.arange(1., 141.), "weekly")
        r, notes, _ = rolling_relationship(a, spec("PPIACO"), b, spec("ICSA"), [10], DEFAULTS)
        self.assertIsNone(r["10"]["pearson"])
        self.assertTrue(notes)
        c = frame(np.arange(1., 141.), "weekly", "2000-01-02")
        r, notes, _ = rolling_relationship(b, spec("ICSA"), c, spec("WALCL"), [10], DEFAULTS)
        self.assertIsNone(r["10"]["pearson"])
        self.assertIn("weekdays", notes[0])
