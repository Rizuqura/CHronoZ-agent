import unittest
import numpy as np
from chronoz_benchmark.models.standard_delta import StandardDelta
from tests.helpers import DEFAULTS, spec, delta_frame


class StandardTests(unittest.TestCase):
    def test_full_snapshot_tail_and_right_inclusive_ecdf(self):
        f = delta_frame([np.nan, -1., 0., 0., 1., 100.])
        model = StandardDelta(spec("PPIACO"), DEFAULTS).fit(f)
        r = model.score(0.)
        self.assertEqual(r["percentile"], 60.)
        self.assertAlmostEqual(r["center"], 20.)
        self.assertAlmostEqual(r["dispersion"], np.std([-1, 0, 0, 1, 100], ddof=1))
        self.assertEqual(model.reference.max(), 100.)

    def test_pcec_filter_only_calibration_and_holdout(self):
        deltas = [np.nan] + [-1., -.5, 0., .5, 1.] * 8 + [25., 100.]
        model = StandardDelta(spec("PCEC96"), DEFAULTS).fit(delta_frame(deltas))
        self.assertEqual(len(model.frame), 43)
        self.assertEqual(len(model.reference), 40)
        r = model.score(100.)
        self.assertEqual(r["model_specific"]["excluded_from_calibration_count"], 1)
        self.assertTrue(r["model_specific"]["outlier_flag"])
        self.assertEqual(r["percentile"], 100.)
        self.assertEqual(len(model.score_history()), 43)
        self.assertTrue(np.isfinite(model.score_history()[-2]["score"]))
        changed = delta_frame(deltas[:-1] + [1e6])
        other = StandardDelta(spec("PCEC96"), DEFAULTS).fit(changed)
        self.assertEqual(model.filter_stats, other.filter_stats)

    def test_constant_reference_is_undefined_not_zero_score(self):
        model = StandardDelta(spec("PPIACO"), DEFAULTS).fit(delta_frame([1.] * 10))
        self.assertTrue(np.isnan(model.score(1.)["score"]))
        self.assertEqual(model.score(1.)["percentile"], 100.)

    def test_pcec_zero_mad_no_invented_filter(self):
        model = StandardDelta(spec("PCEC96"), DEFAULTS).fit(delta_frame([1.] * 10 + [50.]))
        self.assertTrue(model.warnings)
        self.assertEqual(len(model.frame), 11)
        self.assertEqual(len(model.reference), 0)
        self.assertIsNone(model.score(50.)["model_specific"]["outlier_flag"])

    def test_explicit_cutoff_and_no_leaky_holdout_cutoff(self):
        f = delta_frame([1., 2., 3., 4.])
        s = spec("PCEC96")
        s["calibration_end"] = "2000-02-01"
        model = StandardDelta(s, DEFAULTS).fit(f)
        self.assertEqual(model.score(4.)["model_specific"]["eligible_count"], 2)
        s["calibration_end"] = "2000-04-01"
        with self.assertRaises(ValueError):
            StandardDelta(s, DEFAULTS).fit(f)
