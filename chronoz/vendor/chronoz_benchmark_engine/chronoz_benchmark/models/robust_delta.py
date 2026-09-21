"""Median/MAD with the audit's explicit IQR fallback; tails retained."""
from .base import BaseModel


class RobustDelta(BaseModel):
    def score(self, value, date=None):
        result = self.continuous_score(value, robust=True)
        result["model_specific"].update(self.timing_metadata())
        result["model_specific"]["tail_flag"] = self.finite_flag(result["score"], self.defaults["robust_modified_z_threshold"])
        result["model_specific"]["global_z"] = self.continuous_score(value)["score"]
        result["model_specific"]["all_history_retained"] = True
        return result

    def rolling_reference(self, date):
        return self.summary(robust=True)
