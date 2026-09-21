"""Mean/sample-std benchmark, with PCEC96's separate calibration-only filter."""
import numpy as np
from .base import BaseModel
from ..historical.calibration import statistics, normalized


class StandardDelta(BaseModel):
    def fit(self, frame):
        super().fit(frame)
        self.filter_stats = statistics(self.reference)
        self.excluded = self.frame.delta.notna() & False
        if self.spec.get("calibration_filter") == "MODIFIED_Z":
            mad = self.filter_stats["MAD"]
            if not np.isfinite(mad) or mad <= np.finfo(float).eps:
                # The PCEC96 audit explicitly requires nonzero MAD. No invented fallback.
                self.reference = self.reference.iloc[:0]
                self.warnings.append("PCEC96 calibration unavailable: zero/undefined MAD; no observations deleted.")
            else:
                z = .6745 * (self.frame.delta - self.filter_stats["median"]) / mad
                self.excluded = z.abs().gt(self.defaults["robust_modified_z_threshold"])
                self.reference = self.frame.loc[self.eligible & ~self.excluded, "delta"].dropna()
        return self

    def score(self, value, date=None):
        result = self.continuous_score(value)
        details = result["model_specific"]
        details.update(self.timing_metadata())
        if self.spec.get("calibration_filter") == "MODIFIED_Z":
            modified = normalized(value, self.filter_stats["median"], self.filter_stats["MAD"] / .6745)
            flag = self.finite_flag(modified, self.defaults["robust_modified_z_threshold"])
            details.update({"modified_z": modified, "outlier_flag": flag,
                            "calibration_filter": "MODIFIED_Z",
                            "excluded_from_calibration_count": int((self.excluded & self.eligible).sum()),
                            "filter_reference": self.filter_stats,
                            "all_history_retained": True})
        else:
            flag = False
        z = result["score"]
        state = "UNAVAILABLE"
        if np.isfinite(z):
            a = abs(z)
            state = "CENTRAL" if a < .5 else "NORMAL" if a < 1 else "ELEVATED" if a < 2 else "EXTREME"
            if a >= 3:
                state = ("OUTLIER" if flag else "EXTREME") if self.spec.get("calibration_filter") else "SPIKE"
            if state != "CENTRAL":
                state += "_ABOVE" if z > 0 else "_BELOW"
        details["state"] = state
        return result
