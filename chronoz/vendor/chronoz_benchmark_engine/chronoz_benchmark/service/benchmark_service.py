"""External-data-root service. No agent, network, original repo or prose dependency."""
from itertools import combinations
from pathlib import Path
import hashlib
import io
import numpy as np
import pandas as pd
from ..registry.series_registry import SeriesRegistry
from ..registry.benchmark_registry import validate_config, build_model
from ..transforms.validation import validate_frame, measurement_decimals, validate_horizons
from ..transforms.delta import calculate_delta
from ..historical.relationships import HistoricalRelationships
from ..live.rolling import calculate_rolling
from ..live.acceleration import calculate_acceleration
from ..live.relationships import rolling_relationship
from ..packet.builder import build_packet
from ..utils.io import read_yaml, resource_root, json_safe


class BenchmarkService:
    def __init__(self, data_root, config_root=None):
        self.data_root = Path(data_root).expanduser().resolve()
        if not self.data_root.is_dir():
            raise ValueError(f"Data root is not a directory: {self.data_root}")
        self.config_root = Path(config_root).expanduser().resolve() if config_root is not None else resource_root() / "config"
        self.defaults = read_yaml(self.config_root / "engine_defaults.yaml")
        self.epochs = read_yaml(self.config_root / "structural_epochs.yaml")
        self.registry = SeriesRegistry(self.config_root)
        validate_config(self.defaults, self.epochs, self.registry)
        self.historical_relationships = HistoricalRelationships(self.config_root / "historical_relationships.json")

    def describe_series(self, series_id):
        return self.registry.get(series_id)

    def healthcheck(self):
        missing = [sid for sid in self.registry.series if not (self.data_root / f"{sid}.csv").is_file()]
        return {"status": "ok" if not missing else "partial", "data_root": str(self.data_root),
                "registered_series": len(self.registry.series), "missing_series": missing,
                "scope": "Configuration and file availability only; contents validated when requested."}

    def _load(self, ids):
        loaded = {}
        for sid in ids:
            spec = self.registry.get(sid)
            path = self.data_root / f"{sid}.csv"
            contents = path.read_bytes()
            raw = pd.read_csv(io.BytesIO(contents), dtype={"value": str})
            frame = validate_frame(raw, spec["frequency"])
            spec["measurement_decimals"] = measurement_decimals(raw.value)
            delta, checks = calculate_delta(frame, spec["frequency"], spec["transform"])
            if spec["model_family"].startswith("DISCRETE"):
                delta = delta.round(spec["measurement_decimals"])
            frame["delta"] = delta
            loaded[sid] = (frame, spec, checks, hashlib.sha256(contents).hexdigest())
        return loaded

    def _indicators(self, loaded, horizons):
        indicators = {}
        for sid, (frame, spec, checks, fingerprint) in loaded.items():
            model = build_model(spec, self.defaults, self.epochs).fit(frame)
            latest = frame.iloc[-1]
            historical = model.score(latest.delta, latest.date)
            rolling = calculate_rolling(frame, spec, model, horizons, self.defaults)
            warnings = list(spec.get("warnings", [])) + model.warnings
            if any(checks[k] for k in ("gap_pairs", "nonpositive_pairs", "nonfinite_pairs")):
                warnings.append(f"Unavailable transform pairs (no filling or deletion): {checks}")
            if not np.isfinite(latest.delta):
                warnings.append("Latest transformed observation is unavailable; no fallback to an older observation.")
            if historical["score"] is None or not np.isfinite(historical["score"]):
                warnings.append("Primary historical score unavailable: insufficient reference or undefined dispersion.")
            if any(r["n"] < int(h) for h, r in rolling.items()):
                warnings.append("Some rolling windows have incomplete native-period coverage; inspect their n and warnings.")
            details = historical["model_specific"]
            indicators[sid] = {"series_id": sid, "name": spec["name"], "category": spec["category"],
                               "frequency": spec["frequency"], "latest_date": str(latest.date.date()),
                               "raw_value": latest.value, "transformed_value": latest.delta,
                               "model_family": spec["model_family"], "historical": historical,
                               "rolling": rolling,
                               "acceleration": calculate_acceleration(rolling, self.defaults["acceleration_tolerance"]),
                               "flags": {"transform": spec["transform"], "transform_checks": checks,
                                         "source_sha256": fingerprint, "outlier": details.get("outlier_flag"),
                                         "tail": details.get("tail_flag"), "shock": details.get("shock_flag"),
                                         "all_history_retained": True}, "warnings": warnings}
        return json_safe(indicators)

    def _relationships(self, loaded, horizons):
        result = []
        for a, b in combinations(loaded, 2):
            historical, warnings = self.historical_relationships.lookup(a, b)
            frame_a, spec_a, _, _ = loaded[a]
            frame_b, spec_b, _, _ = loaded[b]
            rolling, notes, transforms = rolling_relationship(frame_a, spec_a, frame_b, spec_b, horizons, self.defaults)
            result.append({"series_a": a, "series_b": b, "historical": historical,
                           "rolling": rolling, "live_transforms": transforms,
                           "warnings": warnings + notes + ["Sample-size labels describe only sample-size reliability; they do not establish significance."]})
        return json_safe(result)

    def _prepare(self, series_ids, horizons):
        ids = self.registry.validate_ids(series_ids)
        horizons = validate_horizons(self.defaults["rolling_horizons"] if horizons is None else horizons)
        return ids, horizons, self._load(ids)

    def get_series(self, series_ids, horizons=(10, 20, 50, 100)):
        _, horizons, loaded = self._prepare(series_ids, horizons)
        return self._indicators(loaded, horizons)

    def get_relationships(self, series_ids, horizons=(10, 20, 50, 100)):
        _, horizons, loaded = self._prepare(series_ids, horizons)
        return self._relationships(loaded, horizons)

    def get_packet(self, series_ids, horizons=(10, 20, 50, 100)):
        ids, horizons, loaded = self._prepare(series_ids, horizons)
        return build_packet(self.data_root, ids, self._indicators(loaded, horizons), self._relationships(loaded, horizons))
