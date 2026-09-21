"""Ending-date epoch assignment, with global scores retained as diagnostics."""
import pandas as pd
from .base import BaseModel
from .regime_robust_delta import RegimeRobustDelta


class StructuralEpochRobustDelta(RegimeRobustDelta):
    group_name = "active_epoch"

    def fit(self, frame):
        BaseModel.fit(self, frame)
        self.groups = pd.Series(self.epochs["labels"][0], index=frame.index)
        for boundary, label in zip(self.epochs["boundaries"], self.epochs["labels"][1:]):
            self.groups.loc[frame.date.ge(pd.Timestamp(boundary))] = label
        self._fit_groups()
        self.warnings.append("Structural epoch boundaries are audit hypotheses, not estimated breaks; crossing changes belong to their ending epoch.")
        return self
