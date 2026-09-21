"""Model router and validated audit configuration."""
import math
import pandas as pd
from ..models.standard_delta import StandardDelta
from ..models.robust_delta import RobustDelta
from ..models.discrete_delta import DiscreteDelta
from ..models.discrete_plus_shock import DiscretePlusShock
from ..models.regime_robust_delta import RegimeRobustDelta
from ..models.structural_epoch import StructuralEpochRobustDelta
from ..transforms.validation import validate_horizons

MODELS = {"STANDARD_DELTA": StandardDelta, "ROBUST_DELTA": RobustDelta,
          "DISCRETE_DELTA": DiscreteDelta, "DISCRETE_PLUS_SHOCK": DiscretePlusShock,
          "REGIME_ROBUST_DELTA": RegimeRobustDelta,
          "STRUCTURAL_EPOCH_ROBUST_DELTA": StructuralEpochRobustDelta}


def validate_config(defaults, epochs, registry):
    validate_horizons(defaults["rolling_horizons"])
    for key in ("robust_modified_z_threshold", "regime_window", "minimum_group_observations"):
        if not isinstance(defaults[key], (int, float)) or not math.isfinite(defaults[key]) or defaults[key] <= 0:
            raise ValueError(f"{key} must be positive and finite")
    if type(defaults["regime_window"]) is not int or type(defaults["minimum_group_observations"]) is not int:
        raise ValueError("Regime window and minimum group observations must be integers")
    if not 0 <= defaults["regime_lower_percentile"] < defaults["regime_upper_percentile"] <= 1:
        raise ValueError("Regime percentile bounds must satisfy 0 <= lower < upper <= 1")
    if not 0 < defaults["rolling_min_fraction"] <= 1:
        raise ValueError("rolling_min_fraction must be in (0,1]")
    if not math.isfinite(defaults["acceleration_tolerance"]) or defaults["acceleration_tolerance"] < 0:
        raise ValueError("acceleration_tolerance must be nonnegative and finite")
    t = defaults["rarity_probability_thresholds"]
    if not 0 <= t["rare"] < t["less_common"] < t["common"] <= 1:
        raise ValueError("Rarity thresholds must be ordered probabilities")
    if defaults["relationship_transform_policy"] != "RESEARCH_PERCENT_OR_DIFFERENCE":
        raise ValueError("Unsupported relationship transform policy")
    if type(defaults["allow_same_frequency_nonmonthly_relationships"]) is not bool:
        raise ValueError("Nonmonthly relationship switch must be boolean")
    for h in (10, 20, 50, 100):
        n = defaults["minimum_samples"][f"rolling_correlation_{h}"]
        if type(n) is not int or not 2 <= n <= h:
            raise ValueError(f"Invalid minimum samples for horizon {h}")
    for sid, spec in registry.series.items():
        if spec["model_family"] not in MODELS:
            raise ValueError(f"Unknown model family for {sid}")
        if spec.get("calibration_filter") and spec["model_family"] != "STANDARD_DELTA":
            raise ValueError("Calibration-only filtering belongs to the standard benchmark family")
        if spec["model_family"] == "STRUCTURAL_EPOCH_ROBUST_DELTA":
            epoch = epochs[sid]
            boundaries = list(map(pd.Timestamp, epoch["boundaries"]))
            labels = epoch["labels"]
            if (any(pd.isna(x) for x in boundaries) or boundaries != sorted(set(boundaries)) or
                    len(labels) != len(boundaries) + 1 or len(labels) != len(set(labels)) or
                    epoch.get("assignment") != "ENDING_DATE"):
                raise ValueError(f"Invalid structural epoch partition for {sid}")


def build_model(spec, defaults, epochs):
    return MODELS[spec["model_family"]](spec, defaults, epochs.get(spec["series_id"]))
