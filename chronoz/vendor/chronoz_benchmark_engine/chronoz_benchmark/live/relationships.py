"""Pairwise native-calendar correlations, using the relationship research transforms."""
import numpy as np
import pandas as pd
from ..transforms.delta import consecutive_pairs
from ..transforms.validation import FREQUENCIES

LABELS = {10: "LOW", 20: "EXPLORATORY", 50: "MODERATE", 100: "STRONGER"}


def relationship_changes(frame, spec):
    a, b = frame.value, frame.value.shift()
    valid = consecutive_pairs(frame.date, spec["frequency"]) & np.isfinite(a) & np.isfinite(b)
    if spec["transform"] == "LOG_DELTA":
        valid &= a.gt(0) & b.gt(0)
        with np.errstate(all="ignore"):
            values = 100 * (a.where(valid) / b.where(valid) - 1)
        method = "PERCENT_CHANGE"
    else:
        values = (a - b).where(valid)
        method = "ARITHMETIC_DELTA"
    return pd.Series(values.where(np.isfinite(values)).to_numpy(), index=frame.date), method


def rolling_relationship(frame_a, spec_a, frame_b, spec_b, horizons, defaults):
    warnings = []
    freq = spec_a["frequency"]
    reason = None
    if freq != spec_b["frequency"]:
        reason = "Different native frequencies; no resampling or rolling correlation performed."
    elif freq == "weekly" and frame_a.date.iloc[0].dayofweek != frame_b.date.iloc[0].dayofweek:
        reason = "Weekly observation weekdays differ; native alignment is unavailable."
    elif freq != "monthly" and not defaults["allow_same_frequency_nonmonthly_relationships"]:
        reason = "Nonmonthly relationship calculations disabled by configuration."
    if reason:
        return {str(h): {"pearson": None, "spearman": None, "n": 0,
                         "sample_size_label": LABELS[h], "start_date": None, "end_date": None,
                         "warnings": [reason]} for h in horizons}, [reason], None
    a, method_a = relationship_changes(frame_a, spec_a)
    b, method_b = relationship_changes(frame_b, spec_b)
    start, end = min(a.index.min(), b.index.min()), max(a.index.max(), b.index.max())
    grid = pd.date_range(start, end, freq=FREQUENCIES[freq])
    aligned = pd.concat([a.rename("a"), b.rename("b")], axis=1, sort=True).reindex(grid)
    if freq != "monthly":
        warnings.append("Same-frequency nonmonthly correlations are a DEVELOPMENT extension of monthly research.")
    if a.index.max() != b.index.max():
        warnings.append("Latest observation dates differ; windows end at the later date and missing positions remain missing.")
    first_pair = aligned.dropna().index.min()
    result = {}
    for h in horizons:
        window = aligned.iloc[-h:]
        pairs = window.dropna()
        notes = []
        complete = len(window) == h and pd.notna(first_pair) and first_pair <= window.index[0]
        enough = len(pairs) >= defaults["minimum_samples"][f"rolling_correlation_{h}"]
        varying = pairs.a.nunique() > 1 and pairs.b.nunique() > 1
        if not complete or not enough:
            notes.append("Insufficient paired observations or elapsed native periods for this window.")
        elif not varying:
            notes.append("Constant paired window: correlation is undefined.")
        pearson = float(pairs.a.corr(pairs.b)) if complete and enough and varying else None
        # Pearson of average ranks is Spearman, with pairwise ties handled explicitly.
        spearman = float(pairs.a.rank().corr(pairs.b.rank())) if pearson is not None else None
        result[str(h)] = {"pearson": pearson, "spearman": spearman, "n": len(pairs),
                          "sample_size_label": LABELS[h], "start_date": str(window.index.min().date()),
                          "end_date": str(window.index.max().date()), "warnings": notes}
    return result, warnings, {"series_a": method_a, "series_b": method_b, "frequency": freq}
