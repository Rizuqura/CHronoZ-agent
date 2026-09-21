import unittest
import numpy as np
from chronoz_benchmark.models.discrete_delta import DiscreteDelta
from chronoz_benchmark.models.discrete_plus_shock import DiscretePlusShock
from tests.helpers import DEFAULTS, spec, delta_frame


class DiscreteTests(unittest.TestCase):
    def test_precision_pmf_ecdf_and_unseen_point(self):
        model = DiscreteDelta(spec("AWHAETP"), DEFAULTS).fit(delta_frame([0., 0., .10000000003, -.1, .2]))
        self.assertEqual(model.score(0.)["score"], .5)
        self.assertEqual(model.score(0.)["percentile"], 75.)
        self.assertEqual(model.score(.1)["score"], .25)
        unseen = model.score(.2)
        self.assertEqual(unseen["score"], 0.)
        self.assertEqual(unseen["model_specific"]["rarity"], 1.)
        self.assertEqual(unseen["model_specific"]["zero_share"], .5)
        self.assertIsNone(unseen["dispersion"])

    def test_unrate_shock_keeps_all_observations(self):
        values = [-.2, -.1, 0., .1, .2] * 10 + [10.]
        model = DiscretePlusShock(spec("UNRATE"), DEFAULTS).fit(delta_frame(values))
        r = model.score(10.)
        self.assertTrue(r["model_specific"]["shock_flag"])
        self.assertAlmostEqual(r["model_specific"]["modified_z"], 67.45)
        self.assertEqual(len(model.frame), 51)

    def test_undefined_shock_flag_is_null(self):
        model = DiscretePlusShock(spec("UNRATE"), DEFAULTS).fit(delta_frame([0.] * 10 + [10.]))
        self.assertIsNone(model.score(10.)["model_specific"]["shock_flag"])
        self.assertTrue(np.isnan(model.score(10.)["model_specific"]["modified_z"]))
