"""Native-step transforms; absent periods never become adjacent observations."""
import numpy as np
import pandas as pd

TRANSFORMS = {"LOG_DELTA", "ARITHMETIC_DELTA", "BASIS_POINT_DELTA"}


def consecutive_pairs(dates, frequency):
    if frequency == "weekly":
        return dates.diff().eq(pd.Timedelta(days=7))
    period = {"monthly": "M", "quarterly": "Q"}[frequency]
    return dates.dt.to_period(period).astype("int64").diff().eq(1)


def calculate_delta(frame, frequency, transform):
    if transform not in TRANSFORMS:
        raise ValueError(f"Unknown transform: {transform}")
    current, previous = frame.value, frame.value.shift()
    has_previous = pd.Series(np.arange(len(frame)) > 0, index=frame.index)
    consecutive = consecutive_pairs(frame.date, frequency)
    finite = np.isfinite(current) & np.isfinite(previous)
    eligible = has_previous & consecutive & finite
    nonpositive = eligible & ((current <= 0) | (previous <= 0)) if transform == "LOG_DELTA" else eligible & False
    eligible &= ~nonpositive
    a, b = current.where(eligible), previous.where(eligible)
    with np.errstate(all="ignore"):
        result = 100 * (np.log(a) - np.log(b)) if transform == "LOG_DELTA" else a - b
        if transform == "BASIS_POINT_DELTA":
            result *= 100
    invalid_result = eligible & ~np.isfinite(result)
    result = result.where(eligible & ~invalid_result)
    checks = {
        "valid_deltas": int(result.notna().sum()),
        "gap_pairs": int((has_previous & ~consecutive).sum()),
        "nonpositive_pairs": int(nonpositive.sum()),
        "nonfinite_pairs": int((has_previous & consecutive & ~finite).sum() + invalid_result.sum()),
    }
    return result, checks
