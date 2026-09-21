import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import numpy as np
import yaml
from jsonschema import Draft202012Validator, ValidationError
from chronoz_benchmark import BenchmarkService
from chronoz_benchmark.utils.io import read_json
from tests.helpers import DataTest, ROOT


class PacketTests(DataTest):
    def make_packet(self):
        for sid in ("PPIACO", "INDPRO", "TCU"):
            self.write(sid)
        return BenchmarkService(self.data).get_packet(["PPIACO", "INDPRO", "TCU"])

    def test_json_schema_and_contract(self):
        packet = self.make_packet()
        payload = json.loads(packet.to_json())
        self.assertEqual(set(payload["indicators"]), set(payload["requested_series"]))
        self.assertEqual(len(payload["relationships"]), 3)
        validator = Draft202012Validator(read_json(ROOT / "schemas" / "benchmark_packet.schema.json"))
        validator.validate(payload)
        del payload["indicators"]["PPIACO"]["historical"]["percentile"]
        with self.assertRaises(ValidationError):
            validator.validate(payload)

    def test_invalid_schema_value_rejected(self):
        payload = self.make_packet().to_dict()
        payload["indicators"]["TCU"]["rolling"]["10"]["n"] = "ten"
        with self.assertRaises(ValidationError):
            Draft202012Validator(read_json(ROOT / "schemas" / "benchmark_packet.schema.json")).validate(payload)

    def test_latest_missing_does_not_fall_back_and_json_has_no_nan(self):
        self.write("PPIACO", list(range(1, 120)) + [np.nan])
        packet = BenchmarkService(self.data).get_packet(["PPIACO"])
        r = json.loads(packet.to_json())["indicators"]["PPIACO"]
        self.assertIsNone(r["raw_value"])
        self.assertIsNone(r["transformed_value"])
        self.assertIsNone(r["historical"]["score"])
        self.assertNotIn("NaN", packet.to_json())

    def test_single_observation_returns_null_scores(self):
        self.write("PPIACO", [100.])
        p = BenchmarkService(self.data).get_packet(["PPIACO"]).to_dict()
        self.assertIsNone(p["indicators"]["PPIACO"]["historical"]["score"])

    def test_external_root_config_override_and_healthcheck(self):
        self.write("PPIACO")
        config = self.root / "custom config"
        shutil.copytree(ROOT / "config", config)
        path = config / "engine_defaults.yaml"
        defaults = yaml.safe_load(path.read_text())
        defaults["rolling_horizons"] = [20]
        path.write_text(yaml.safe_dump(defaults))
        service = BenchmarkService(self.data, config)
        self.assertEqual(service.describe_series("PCEC96")["calibration_filter"], "MODIFIED_Z")
        self.assertEqual(service.healthcheck()["status"], "partial")
        self.assertEqual(set(service.get_series(["PPIACO"], horizons=None)["PPIACO"]["rolling"]), {"20"})
        defaults["regime_lower_percentile"] = .9
        path.write_text(yaml.safe_dump(defaults))
        with self.assertRaises(ValueError):
            BenchmarkService(self.data, config)

    def test_reject_unknown_series_root_horizons_and_prose(self):
        service = BenchmarkService(self.data)
        for ids in (["../PPIACO"], ["UNKNOWN"], [], ["TCU", "TCU"], "PPIACO"):
            with self.assertRaises(ValueError):
                service.get_packet(ids)
        for horizons in ([5], [], [10, 10], [True]):
            with self.assertRaises(ValueError):
                service.get_series(["TCU"], horizons)
        with self.assertRaises(ValueError):
            BenchmarkService(self.root / "missing")

    def test_cli_json_output_and_failure_diagnostics(self):
        self.make_packet()
        output = self.root / "packet.json"
        command = [sys.executable, str(ROOT / "benchmark_cli.py"), "--data-root", str(self.data),
                   "--series", "PPIACO", "INDPRO", "TCU", "--pretty", "--output", str(output)]
        completed = subprocess.run(command, cwd=self.root, text=True, capture_output=True, check=True)
        self.assertEqual(json.loads(completed.stdout), json.loads(output.read_text()))
        self.assertEqual(completed.stderr, "")
        failed = subprocess.run([sys.executable, str(ROOT / "benchmark_cli.py"), "--data-root", str(self.data),
                                 "--series", "UNKNOWN"], cwd=self.root, text=True, capture_output=True)
        self.assertNotEqual(failed.returncode, 0)
        self.assertEqual(failed.stdout, "")
        self.assertIn("Unknown series", failed.stderr)

    def test_copied_folder_executes_from_unrelated_working_directory(self):
        self.make_packet()
        copied = self.root / "different repository" / "engine"
        shutil.copytree(ROOT, copied, ignore=shutil.ignore_patterns("__pycache__", "build", "dist", "*.egg-info"))
        unrelated = self.root / "unrelated cwd"
        unrelated.mkdir()
        env = dict(os.environ)
        env.pop("PYTHONPATH", None)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        result = subprocess.run([sys.executable, str(copied / "benchmark_cli.py"), "--data-root", str(self.data),
                                 "--series", "PPIACO", "INDPRO", "TCU"], cwd=unrelated, env=env,
                                text=True, capture_output=True, check=True)
        self.assertEqual(len(json.loads(result.stdout)["indicators"]), 3)
        self.assertEqual(result.stderr, "")
