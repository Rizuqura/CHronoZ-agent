"""Explicit input paths and portable resource resolution."""
from pathlib import Path
import json
import math

import numpy as np
import pandas as pd
import yaml


def resource_root():
    package = Path(__file__).resolve().parents[1]
    bundled = package / "_resources"
    return bundled if bundled.is_dir() else package.parent


def read_yaml(path):
    with Path(path).open(encoding="utf-8-sig") as stream:
        value = yaml.safe_load(stream)
    if not isinstance(value, dict):
        raise ValueError(f"Expected a configuration mapping: {path}")
    return value


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def json_safe(value):
    """JSON null for unavailable numeric results; never emit NaN or Infinity."""
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]
    if isinstance(value, np.generic):
        return json_safe(value.item())
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    return value
