"""Retrospective prior-window speed groups, never identified policy regimes."""
import numpy as np
import pandas as pd
from .robust_delta import RobustDelta
from ..transforms.validation import native_grid


class RegimeRobustDelta(RobustDelta):
    group_name = "active_regime"

    def fit(self, frame):
        super().fit(frame)
        grid = native_grid(frame.date, self.spec["frequency"])
        series = frame.set_index("date").delta.reindex(grid)
        window = self.defaults["regime_window"]
        prior = series.shift(1).rolling(window, min_periods=window).mean().reindex(frame.date).to_numpy()
        self.prior = pd.Series(prior, index=frame.index)
        fit = self.prior.loc[self.eligible].dropna()
        self.lower = fit.quantile(self.defaults["regime_lower_percentile"]) if len(fit) else np.nan
        self.upper = fit.quantile(self.defaults["regime_upper_percentile"]) if len(fit) else np.nan
        self.groups = pd.Series(np.select(
            [self.prior.isna() | ~np.isfinite(self.lower), self.prior < self.lower, self.prior > self.upper],
            ["UNCLASSIFIED", "CONTRACTION", "EXPANSION"], default="NEUTRAL"), index=frame.index)
        self._fit_groups()
        self.warnings.append("Regime speed buckets and thresholds are experimental; they do not identify QE/QT or economic causes.")
        return self

    def _fit_groups(self):
        self.references = {group: self.frame.loc[self.eligible & self.groups.eq(group), "delta"].dropna()
                           for group in self.groups.unique() if group != "UNCLASSIFIED"}

    def group_at(self, date):
        rows = self.frame.index[self.frame.date.eq(pd.Timestamp(date))]
        return self.groups.loc[rows[0]] if len(rows) else "UNCLASSIFIED"

    def group_reference(self, date):
        group = self.group_at(date)
        ref = self.references.get(group, self.reference.iloc[:0])
        return ref if len(ref) >= self.defaults["minimum_group_observations"] else ref.iloc[:0]

    def score(self, value, date=None):
        date = self.frame.date.iloc[-1] if date is None else date
        group = self.group_at(date)
        ref = self.group_reference(date)
        result = self.continuous_score(value, ref, robust=True)
        result["score_type"] = "EPOCH_ROBUST_Z" if self.group_name == "active_epoch" else "REGIME_ROBUST_Z"
        details = result["model_specific"]
        details.update(self.timing_metadata())
        details.update({self.group_name: group,
                        "global_diagnostic_score": self.continuous_score(value, robust=True)["score"],
                        "global_diagnostic_z": self.continuous_score(value)["score"],
                        "global_percentile": self.continuous_score(value, robust=True)["percentile"],
                        "group_calibrations": {k: self.summary(v, robust=True) for k, v in self.references.items()},
                        "conditioned_score_available": len(ref) > 0})
        if self.group_name == "active_regime":
            details.update({"lower_threshold": self.lower, "upper_threshold": self.upper,
                            "prior_window": self.defaults["regime_window"]})
        else:
            details["epoch_partition"] = self.epochs
        return result

    def rolling_reference(self, date):
        return self.summary(self.group_reference(date), robust=True)
