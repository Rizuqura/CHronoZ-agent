"""Regenerate the V0 JSON Schema; contains no runtime/research dependencies."""
import json
from pathlib import Path


def obj(properties, required=None, additional=False):
    return {"type": "object", "properties": properties,
            "required": list(properties) if required is None else required, "additionalProperties": additional}


number = {"type": ["number", "null"]}
integer = {"type": "integer", "minimum": 0}
text = {"type": "string"}
warnings = {"type": "array", "items": text}
date = {"type": "string", "format": "date"}
nullable_date = {"type": ["string", "null"], "format": "date"}
percentile = {"type": ["number", "null"], "minimum": 0, "maximum": 100}
coefficient = {"type": ["number", "null"], "minimum": -1.0000000001, "maximum": 1.0000000001}
stats = {"n": integer, "mean": number, "median": number, "std": number, "MAD": number}
rolling = obj({**stats, "rolling_elevation": number, "local_score": number,
               "score_type": {"enum": ["Z_SCORE", "ROBUST_Z", "NOT_APPLICABLE_DISCRETE"]},
               "complete_window": {"type": "boolean"}, "start_date": date, "end_date": date, "warnings": warnings})


def windows(item):
    return {"type": "object", "minProperties": 1,
            "properties": {str(h): item for h in (10, 20, 50, 100)}, "additionalProperties": False}


indicator = obj({
    "series_id": text, "name": text, "category": text,
    "frequency": {"enum": ["weekly", "monthly", "quarterly"]}, "latest_date": date,
    "raw_value": number, "transformed_value": number,
    "model_family": {"enum": ["STANDARD_DELTA", "ROBUST_DELTA", "DISCRETE_DELTA", "DISCRETE_PLUS_SHOCK", "REGIME_ROBUST_DELTA", "STRUCTURAL_EPOCH_ROBUST_DELTA"]},
    "historical": obj({"score": number, "score_type": {"enum": ["Z_SCORE", "ROBUST_Z", "PMF_PROBABILITY", "REGIME_ROBUST_Z", "EPOCH_ROBUST_Z"]},
                       "percentile": percentile, "center": number, "dispersion": number,
                       "ranges": obj({f"P{q}": number for q in (5, 10, 25, 50, 75, 90, 95)}),
                       "model_specific": {"type": "object", "required": ["reference_timing", "calibration_count", "history_count"],
                                          "properties": {"reference_timing": {"enum": ["FULL_SNAPSHOT", "PRE_LATEST"]},
                                                         "calibration_count": integer, "history_count": integer},
                                          "additionalProperties": True}}),
    "rolling": windows(rolling),
    "acceleration": obj({"10_vs_20": number, "20_vs_50": number, "50_vs_100": number,
                         "pattern": {"enum": ["BROAD_ACCELERATION", "BROAD_DECELERATION", "SHORT_TERM_ACCELERATION", "SHORT_TERM_DECELERATION", "MIXED", "UNAVAILABLE"]}}),
    "flags": obj({"transform": {"enum": ["LOG_DELTA", "ARITHMETIC_DELTA", "BASIS_POINT_DELTA"]},
                  "transform_checks": obj({k: integer for k in ("valid_deltas", "gap_pairs", "nonpositive_pairs", "nonfinite_pairs")}),
                  "source_sha256": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
                  "outlier": {"type": ["boolean", "null"]}, "tail": {"type": ["boolean", "null"]},
                  "shock": {"type": ["boolean", "null"]}, "all_history_retained": {"const": True}}),
    "warnings": warnings})
relationship = obj({
    "series_a": text, "series_b": text,
    "historical": obj({"pearson": coefficient, "spearman": coefficient,
                       "overlap": {"type": ["integer", "null"], "minimum": 0},
                       "overlap_start": nullable_date, "overlap_end": nullable_date,
                       "redundancy_candidate": {"type": ["boolean", "null"]},
                       "best_descriptive_lag": {"type": ["integer", "null"]}, "lag_correlation": coefficient,
                       "lag_overlap": {"type": ["integer", "null"], "minimum": 0},
                       "lag_unit": text, "lag_definition": text, "transform_policy": text,
                       "snapshot_as_of": {"type": "string", "format": "date-time"}, "source": text,
                       "research_rolling_60": {"type": ["object", "null"]}}),
    "rolling": windows(obj({"pearson": coefficient, "spearman": coefficient, "n": integer,
                            "sample_size_label": {"enum": ["LOW", "EXPLORATORY", "MODERATE", "STRONGER"]},
                            "start_date": nullable_date, "end_date": nullable_date, "warnings": warnings})),
    "live_transforms": {"type": ["object", "null"]}, "warnings": warnings})
schema = {"$schema": "https://json-schema.org/draft/2020-12/schema", "title": "BenchmarkPacket V0",
          **obj({"as_of": {"type": "string", "format": "date-time"}, "engine_version": {"const": "0.1.0"},
                 "data_root": text, "requested_series": {"type": "array", "minItems": 1, "uniqueItems": True, "items": text},
                 "indicators": {"type": "object", "minProperties": 1, "additionalProperties": {"$ref": "#/$defs/indicator"}},
                 "relationships": {"type": "array", "items": {"$ref": "#/$defs/relationship"}}, "warnings": warnings}),
          "$defs": {"indicator": indicator, "relationship": relationship}}

if __name__ == "__main__":
    path = Path(__file__).resolve().parents[1] / "schemas" / "benchmark_packet.schema.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")
