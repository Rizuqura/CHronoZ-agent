import unittest
import numpy as np
from chronoz_benchmark.models.robust_delta import RobustDelta
from chronoz_benchmark.historical.calibration import robust_scale
from tests.helpers import DEFAULTS, spec, delta_frame


class RobustTests(unittest.TestCase):
    def test_median_mad_tail_retention_and_holdout(self):
        values = [-2., -1., 0., 1., 2., 1000., 3.]
        model = RobustDelta(spec("ICSA"), DEFAULTS).fit(delta_frame(values, "weekly"))
        r = model.score(1000.)
        self.assertEqual(len(model.reference), 6)
        self.assertEqual(model.reference.max(), 1000.)
        self.assertAlmostEqual(r["score"], (1000. - .5) / (1.4826 * 1.5))
        self.assertTrue(r["model_specific"]["tail_flag"])

    def test_iqr_fallback_and_zero_scale(self):
        scale, method = robust_scale([0., 0., 0., 0., 1., 1., 1.])
        self.assertEqual(method, "IQR_FALLBACK")
        self.assertAlmostEqual(scale, 1 / 1.349)
        scale, method = robust_scale([0.] * 10)
        self.assertTrue(np.isnan(scale))
        self.assertEqual(method, "ZERO_MAD_AND_IQR")
