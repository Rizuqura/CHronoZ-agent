"""Shared descriptive statistics, ECDF and explicit calibration timing."""
import numpy as np
import pandas as pd


def statistics(values):
    s = pd.Series(values, dtype=float).dropna()
    median = s.median() if len(s) else np.nan
    return {"n": len(s), "mean": s.mean() if len(s) else np.nan,
            "median": median, "std": s.std(ddof=1) if len(s) > 1 else np.nan,
            "MAD": (s - median).abs().median() if len(s) else np.nan}


def robust_scale(values):
    s = pd.Series(values, dtype=float).dropna()
    if s.empty:
        return np.nan, "UNAVAILABLE"
    mad = (s - s.median()).abs().median()
    if mad > np.finfo(float).eps:
        return 1.4826 * mad, "MAD"
    iqr = s.quantile(.75) - s.quantile(.25)
    if iqr > np.finfo(float).eps:
        return iqr / 1.349, "IQR_FALLBACK"
    return np.nan, "ZERO_MAD_AND_IQR"


def normalized(value, center, scale):
    if not np.isfinite([value, center, scale]).all() or scale <= 0:
        return np.nan
    return (value - center) / scale


def percentile(value, reference):
    s = pd.Series(reference, dtype=float).dropna()
    return 100 * float(s.le(value).sum()) / len(s) if len(s) and np.isfinite(value) else np.nan


def ranges(reference):
    s = pd.Series(reference, dtype=float).dropna()
    return {f"P{q}": s.quantile(q / 100) if len(s) else np.nan for q in (5, 10, 25, 50, 75, 90, 95)}


def eligibility(frame, spec):
    cutoff = spec.get("calibration_end")
    if cutoff is not None:
        cutoff = pd.Timestamp(cutoff)
        if cutoff >= frame.date.iloc[-1] and spec["reference_timing"] == "PRE_LATEST":
            raise ValueError("Pinned calibration_end must precede the latest reporting observation")
        return frame.date.le(cutoff)
    if spec["reference_timing"] == "PRE_LATEST":
        return frame.date.lt(frame.date.iloc[-1])
    return pd.Series(True, index=frame.index)
