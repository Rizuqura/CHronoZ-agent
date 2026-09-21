import unittest
import numpy as np
from chronoz_benchmark.models.regime_robust_delta import RegimeRobustDelta
from chronoz_benchmark.models.structural_epoch import StructuralEpochRobustDelta
from tests.helpers import DEFAULTS, EPOCHS, spec, delta_frame


class RegimeTests(unittest.TestCase):
    def test_prior_window_excludes_current_and_keeps_global_diagnostic(self):
        f = delta_frame(np.sin(np.arange(400) / 5), "weekly")
        model = RegimeRobustDelta(spec("WALCL"), DEFAULTS).fit(f)
        other_f = f.copy()
        other_f.loc[len(f) - 1, "delta"] = 999.
        other = RegimeRobustDelta(spec("WALCL"), DEFAULTS).fit(other_f)
        self.assertEqual(model.lower, other.lower)
        self.assertEqual(model.upper, other.upper)
        self.assertEqual(model.groups.iloc[-1], other.groups.iloc[-1])
        self.assertAlmostEqual(model.prior.iloc[-1], f.delta.iloc[-14:-1].mean())
        r = model.score(f.delta.iloc[-1])
        self.assertTrue(np.isfinite(r["score"]))
        self.assertIn("global_diagnostic_score", r["model_specific"])

    def test_gap_prevents_prior_window_compression(self):
        f = delta_frame(np.arange(40.), "weekly").drop(index=30).reset_index(drop=True)
        model = RegimeRobustDelta(spec("WRESBAL"), DEFAULTS).fit(f)
        self.assertEqual(model.groups.iloc[-1], "UNCLASSIFIED")
        self.assertTrue(np.isnan(model.score(39.)["score"]))

    def test_sparse_group_no_fallback_to_global_primary(self):
        f = delta_frame(np.sin(np.arange(25.)), "weekly")
        model = RegimeRobustDelta(spec("WALCL"), DEFAULTS).fit(f)
        r = model.score(1.)
        self.assertTrue(np.isnan(r["score"]))
        self.assertTrue(np.isfinite(r["model_specific"]["global_diagnostic_score"]))
        self.assertFalse(r["model_specific"]["conditioned_score_available"])

    def test_structural_epoch_ending_date_and_custom_partition(self):
        f = delta_frame(np.sin(np.arange(300.)), start="2000-01-01")
        model = StructuralEpochRobustDelta(spec("TOTRESNS"), DEFAULTS, EPOCHS["TOTRESNS"]).fit(f)
        self.assertEqual(model.group_at("2007-12-01"), "PRE_2008")
        self.assertEqual(model.group_at("2008-01-01"), "2008_TO_2019")
        self.assertEqual(model.group_at("2020-01-01"), "2020_PLUS")
        r = model.score(.5)
        self.assertEqual(r["model_specific"]["active_epoch"], "2020_PLUS")
        self.assertTrue(np.isfinite(r["score"]))
        self.assertIn("global_diagnostic_score", r["model_specific"])
