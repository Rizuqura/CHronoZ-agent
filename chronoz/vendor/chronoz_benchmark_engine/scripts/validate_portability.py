"""Build and exercise a wheel offline, in isolated temporary directories.

Uses installed build requirements (setuptools and wheel); never installs packages
or reads research files. Supply --data-root containing PPIACO, INDPRO, TCU CSVs.
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile


def validate(data_root):
    source = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory(prefix="chronoz-wheel-check-") as directory:
        temporary = Path(directory).resolve()
        copied = temporary / "copied-source"
        shutil.copytree(source, copied, ignore=shutil.ignore_patterns("__pycache__", "build", "dist", "*.egg-info"))
        distribution = temporary / "wheels"
        distribution.mkdir()
        build = subprocess.run([sys.executable, "-c",
                                "from setuptools.build_meta import build_wheel; import sys; build_wheel(sys.argv[1])",
                                str(distribution)], cwd=copied, capture_output=True, text=True)
        if build.returncode:
            raise RuntimeError(build.stdout + build.stderr)
        wheel, = distribution.glob("*.whl")
        installed = temporary / "installed"
        with zipfile.ZipFile(wheel) as archive:
            for name in archive.namelist():
                if not (installed / name).resolve().is_relative_to(installed.resolve()):
                    raise RuntimeError("Unexpected wheel path")
            archive.extractall(installed)
        unrelated = temporary / "unrelated-cwd"
        unrelated.mkdir()
        code = '''
import json, sys
from pathlib import Path
installed = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(installed))
from chronoz_benchmark import BenchmarkService
from chronoz_benchmark.utils.io import resource_root
assert resource_root().is_relative_to(installed)
service = BenchmarkService(sys.argv[2])
packet = service.get_packet(["PPIACO", "INDPRO", "TCU"])
for name, module in list(sys.modules.items()):
    if name.startswith("chronoz_benchmark") and getattr(module, "__file__", None):
        assert Path(module.__file__).resolve().is_relative_to(installed), name
print(packet.to_json())
'''
        result = subprocess.run([sys.executable, "-I", "-W", "error", "-c", code, str(installed), str(data_root)],
                                cwd=unrelated, capture_output=True, text=True, check=True)
        packet = json.loads(result.stdout)
        assert set(packet["indicators"]) == {"PPIACO", "INDPRO", "TCU"}
        assert not result.stderr, result.stderr
        print(json.dumps({"wheel": wheel.name, "indicators": len(packet["indicators"]),
                          "relationships": len(packet["relationships"]), "isolated_imports_verified": True,
                          "bundled_resources_verified": True, "stdout_json_verified": True}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", required=True, type=Path)
    args = parser.parse_args()
    validate(args.data_root.resolve())
