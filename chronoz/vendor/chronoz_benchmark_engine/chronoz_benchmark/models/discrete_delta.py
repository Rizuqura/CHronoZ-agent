"""Empirical point mass, right-inclusive cumulative percentile and rarity."""
import numpy as np
from .base import BaseModel
from ..historical.calibration import percentile, ranges


class DiscreteDelta(BaseModel):
    def fit(self, frame):
        super().fit(frame)
        self.decimals = self.spec["measurement_decimals"]
        self.reference = self.reference.round(self.decimals)
        counts = self.reference.value_counts().sort_index()
        self.pmf = [{"delta": float(k), "count": int(v), "probability": float(v / len(self.reference))}
                    for k, v in counts.items()]
        return self

    def score(self, value, date=None):
        value = round(value, self.decimals) if np.isfinite(value) else value
        p = float(self.reference.eq(value).mean()) if len(self.reference) and np.isfinite(value) else np.nan
        t = self.defaults["rarity_probability_thresholds"]
        state = ("COMMON" if p >= t["common"] else "LESS_COMMON" if p >= t["less_common"] else
                 "RARE" if p >= t["rare"] else "VERY_RARE") if np.isfinite(p) else "UNAVAILABLE"
        return {"score": p, "score_type": "PMF_PROBABILITY", "percentile": percentile(value, self.reference),
                "center": self.reference.median() if len(self.reference) else np.nan,
                "dispersion": None, "ranges": ranges(self.reference),
                "model_specific": {**self.timing_metadata(), "pmf_probability": p,
                                   "rarity": 1 - p, "rarity_state": state,
                                   "zero_share": float(self.reference.eq(0).mean()) if len(self.reference) else np.nan,
                                   "pmf": self.pmf, "measurement_decimals": self.decimals}}

    def rolling_reference(self, date):
        return {"center": None, "dispersion": None, "scale_method": "NOT_APPLICABLE_DISCRETE"}
