from pathlib import Path
import tempfile
import unittest
import numpy as np
import pandas as pd
from chronoz_benchmark.registry.series_registry import SeriesRegistry
from chronoz_benchmark.utils.io import resource_root, read_yaml

ROOT = resource_root()
DEFAULTS = read_yaml(ROOT / "config" / "engine_defaults.yaml")
EPOCHS = read_yaml(ROOT / "config" / "structural_epochs.yaml")
REGISTRY = SeriesRegistry(ROOT / "config")


def spec(sid):
    return {**REGISTRY.get(sid), "measurement_decimals": 1}


def frame(values, frequency="monthly", start="2000-01-01"):
    freq = {"monthly": "MS", "weekly": "7D", "quarterly": "QS"}[frequency]
    return pd.DataFrame({"date": pd.date_range(start, periods=len(values), freq=freq),
                         "value": values})


def delta_frame(values, frequency="monthly", start="2000-01-01"):
    f = frame(np.ones(len(values)), frequency, start)
    f["delta"] = values
    return f


class DataTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="chronoz-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.data = self.root / "external cleaned data"
        self.data.mkdir()

    def write(self, sid, values=None, count=140, start="2000-01-01"):
        s = spec(sid)
        if values is None:
            values = 100 * np.exp(np.cumsum(.001 + .008 * np.sin(np.arange(count) * .7)))
        f = frame(values, s["frequency"], start)
        f.to_csv(self.data / f"{sid}.csv", index=False)
        return f
