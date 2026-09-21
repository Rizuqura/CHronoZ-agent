"""Center elevation and latest local position; scales follow the selected model."""
import numpy as np
from ..historical.calibration import normalized, robust_scale


def spread(values, latest, stats, reference):
    method = reference["scale_method"]
    if method == "NOT_APPLICABLE_DISCRETE":
        return {"rolling_elevation": None, "local_score": None,
                "score_type": "NOT_APPLICABLE_DISCRETE"}
    robust = method != "SAMPLE_STD"
    center = stats["median"] if robust else stats["mean"]
    scale = robust_scale(values)[0] if robust else stats["std"]
    return {"rolling_elevation": normalized(center, reference["center"], reference["dispersion"]),
            "local_score": normalized(latest, center, scale),
            "score_type": "ROBUST_Z" if robust else "Z_SCORE"}
