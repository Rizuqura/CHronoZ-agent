"""Portable series definitions; never read original repository metadata."""
from copy import deepcopy
import re
from ..utils.io import read_yaml
from ..transforms.delta import TRANSFORMS
from ..transforms.validation import FREQUENCIES


class SeriesRegistry:
    def __init__(self, config_root):
        self.series = read_yaml(config_root / "benchmark_registry.yaml")["series"]
        if not isinstance(self.series, dict) or not self.series:
            raise ValueError("Series registry must be a nonempty mapping")
        for sid, spec in self.series.items():
            if not re.fullmatch(r"[A-Z0-9_]+", sid):
                raise ValueError(f"Invalid series identifier: {sid}")
            for key in ("name", "category", "frequency", "transform", "model_family", "reference_timing"):
                if key not in spec:
                    raise ValueError(f"Missing {key} in {sid}")
            if spec["frequency"] not in FREQUENCIES or spec["transform"] not in TRANSFORMS:
                raise ValueError(f"Invalid frequency/transform for {sid}")
            if spec["reference_timing"] not in {"FULL_SNAPSHOT", "PRE_LATEST"}:
                raise ValueError(f"Invalid reference timing for {sid}")
            if spec["transform"] == "BASIS_POINT_DELTA" and spec.get("level_unit") != "percent":
                raise ValueError("BASIS_POINT_DELTA requires levels explicitly stored in percent")
            if spec.get("calibration_filter") not in (None, "MODIFIED_Z"):
                raise ValueError(f"Unknown calibration filter: {sid}")

    def get(self, series_id):
        if series_id not in self.series:
            raise ValueError(f"Unknown series: {series_id}")
        return {"series_id": series_id, **deepcopy(self.series[series_id])}

    def validate_ids(self, series_ids):
        if isinstance(series_ids, str):
            raise ValueError("series_ids must be a sequence of identifiers, not prose or a single string")
        ids = list(series_ids)
        if not ids or len(set(ids)) != len(ids):
            raise ValueError("Supply at least one series with no duplicate identifiers")
        for sid in ids:
            self.get(sid)
        return ids
