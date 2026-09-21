"""Model contract: fit a reference, then score any retained observation."""
from abc import ABC, abstractmethod
import numpy as np
from ..historical.calibration import eligibility, statistics, ranges, percentile, normalized, robust_scale


class BaseModel(ABC):
    def __init__(self, spec, defaults, epochs=None):
        self.spec, self.defaults, self.epochs = spec, defaults, epochs
        self.warnings = []

    def fit(self, frame):
        self.frame = frame.copy()
        self.eligible = eligibility(self.frame, self.spec)
        self.reference = self.frame.loc[self.eligible, "delta"].dropna()
        if len(self.reference) < 2:
            self.warnings.append("Insufficient calibration observations; scores may be unavailable.")
        return self

    def summary(self, reference=None, robust=False):
        reference = self.reference if reference is None else reference
        stats = statistics(reference)
        scale, method = robust_scale(reference) if robust else (stats["std"], "SAMPLE_STD")
        return {**stats, "center": stats["median"] if robust else stats["mean"],
                "dispersion": scale, "scale_method": method}

    def continuous_score(self, value, reference=None, robust=False):
        ref = self.reference if reference is None else reference
        stats = self.summary(ref, robust)
        return {"score": normalized(value, stats["center"], stats["dispersion"]),
                "score_type": "ROBUST_Z" if robust else "Z_SCORE",
                "percentile": percentile(value, ref), "center": stats["center"],
                "dispersion": stats["dispersion"], "ranges": ranges(ref),
                "model_specific": {"calibration": stats}}

    def timing_metadata(self):
        dates = self.frame.loc[self.eligible, "date"]
        return {"reference_timing": self.spec["reference_timing"],
                "calibration_end": str(dates.max().date()) if len(dates) else None,
                "history_count": int(self.frame.delta.notna().sum()),
                "eligible_count": int((self.eligible & self.frame.delta.notna()).sum()),
                "calibration_count": len(self.reference),
                "historical_scores_are_retrospective": True}

    def score_history(self):
        """Score every row, including held-out and calibration-excluded events."""
        return [self.score(row.delta, row.date) for row in self.frame.itertuples()]

    @abstractmethod
    def score(self, value, date=None):
        raise NotImplementedError

    def rolling_reference(self, date):
        return self.summary()

    @staticmethod
    def finite_flag(score, threshold):
        return bool(abs(score) > threshold) if np.isfinite(score) else None
