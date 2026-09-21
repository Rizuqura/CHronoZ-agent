"""Calendar-position windows, including the latest observation; never compress gaps."""
import math
import numpy as np
from ..historical.calibration import statistics
from ..transforms.validation import native_grid
from .spread import spread


def calculate_rolling(frame, spec, model, horizons, defaults):
    grid = native_grid(frame.date, spec["frequency"])
    series = frame.set_index("date").delta.reindex(grid)
    reference = model.rolling_reference(frame.date.iloc[-1])
    result = {}
    for h in horizons:
        window = series.iloc[-h:]
        stats = statistics(window)
        enough = len(window) == h and stats["n"] >= math.ceil(h * defaults["rolling_min_fraction"])
        scores = spread(window, frame.delta.iloc[-1], stats, reference)
        warnings = []
        if not enough:
            scores.update(rolling_elevation=None, local_score=None)
            warnings.append("Insufficient native-period coverage; summary statistics describe available observations only.")
        if scores["score_type"] == "NOT_APPLICABLE_DISCRETE":
            warnings.append("Continuous elevation/local score is not defined for this discrete model.")
        elif enough:
            if not np.isfinite(scores["rolling_elevation"]):
                warnings.append("Historical center/scale is unavailable for rolling elevation.")
            if not np.isfinite(scores["local_score"]):
                warnings.append("Latest delta or local dispersion is unavailable for local scoring.")
        result[str(h)] = {**stats, **scores, "complete_window": len(window) == h,
                          "start_date": str(window.index.min().date()), "end_date": str(window.index.max().date()),
                          "warnings": warnings}
    return result
