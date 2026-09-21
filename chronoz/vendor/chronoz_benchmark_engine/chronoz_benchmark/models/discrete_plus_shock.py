"""Discrete reference plus robust shock flag; no crisis rows removed."""
from .discrete_delta import DiscreteDelta
from ..historical.calibration import robust_scale, normalized, statistics


class DiscretePlusShock(DiscreteDelta):
    def score(self, value, date=None):
        result = super().score(value, date)
        stats = statistics(self.reference)
        scale, method = robust_scale(self.reference)
        # The UNRATE audit uses exact modified z when MAD is usable.
        if method == "MAD":
            scale = stats["MAD"] / .6745
        z = normalized(value, stats["median"], scale)
        result["model_specific"].update({"modified_z": z, "shock_scale_method": method,
                                       "shock_flag": self.finite_flag(z, self.defaults["robust_modified_z_threshold"])})
        return result
