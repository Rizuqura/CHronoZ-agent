import unittest
import numpy as np
import pandas as pd
from chronoz_benchmark.transforms.delta import calculate_delta
from chronoz_benchmark.transforms.validation import validate_frame, measurement_decimals
from tests.helpers import frame


class TransformTests(unittest.TestCase):
    def test_exact_formulas(self):
        f = frame([100., 110., 121.])
        for method, expected in [("LOG_DELTA", [100 * np.log(1.1)] * 2),
                                 ("ARITHMETIC_DELTA", [10., 11.]), ("BASIS_POINT_DELTA", [1000., 1100.])]:
            with self.subTest(method=method):
                result, checks = calculate_delta(f, "monthly", method)
                self.assertTrue(np.isnan(result.iloc[0]))
                np.testing.assert_allclose(result.iloc[1:], expected)
                self.assertEqual(checks["valid_deltas"], 2)

    def test_no_delta_across_any_native_calendar_gap(self):
        for frequency in ("monthly", "weekly", "quarterly"):
            f = frame([100., 105., 110., 121.], frequency).drop(index=1).reset_index(drop=True)
            for method in ("LOG_DELTA", "ARITHMETIC_DELTA", "BASIS_POINT_DELTA"):
                with self.subTest(frequency=frequency, method=method):
                    delta, checks = calculate_delta(f, frequency, method)
                    self.assertTrue(delta.iloc[:2].isna().all())
                    self.assertTrue(np.isfinite(delta.iloc[2]))
                    self.assertEqual(checks["gap_pairs"], 1)

    def test_nonpositive_and_missing_endpoints_not_dropped(self):
        f = frame([0., 2., np.nan, 3., 4.])
        delta, checks = calculate_delta(f, "monthly", "LOG_DELTA")
        self.assertEqual(len(delta), len(f))
        self.assertEqual(checks["nonpositive_pairs"], 1)
        self.assertEqual(checks["nonfinite_pairs"], 2)
        self.assertEqual(checks["valid_deltas"], 1)

    def test_signed_arithmetic(self):
        result, _ = calculate_delta(frame([-5., 0., 3.]), "monthly", "ARITHMETIC_DELTA")
        np.testing.assert_equal(result.iloc[1:].to_numpy(), [5., 3.])

    def test_validation_rejects_unsorted_duplicates_and_wrong_calendar(self):
        probes = [frame([1., 2.]).iloc[::-1], pd.concat([frame([1.]), frame([2.])]),
                  pd.DataFrame({"date": ["2020-01-15"], "value": [1.]})]
        for probe in probes:
            with self.assertRaises(ValueError):
                validate_frame(probe, "monthly")

    def test_validation_missing_is_preserved_but_infinity_rejected(self):
        self.assertTrue(validate_frame(frame([1., np.nan]), "monthly").value.isna().iloc[1])
        with self.assertRaises(ValueError):
            validate_frame(frame([1., np.inf]), "monthly")
        self.assertEqual(measurement_decimals(["34.1", "34.00", "34"]), 2)
