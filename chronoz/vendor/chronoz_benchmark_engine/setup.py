"""Bundle canonical root resources in wheels without duplicating source config."""
from pathlib import Path
from shutil import copytree, copy2
from setuptools import setup
from setuptools.command.build_py import build_py


class BuildWithResources(build_py):
    def run(self):
        super().run()
        root = Path(__file__).resolve().parent
        destination = Path(self.build_lib) / "chronoz_benchmark" / "_resources"
        destination.mkdir(parents=True, exist_ok=True)
        for name in ("config", "schemas"):
            copytree(root / name, destination / name, dirs_exist_ok=True)
        copy2(root / "VERSION", destination / "VERSION")


setup(cmdclass={"build_py": BuildWithResources})
