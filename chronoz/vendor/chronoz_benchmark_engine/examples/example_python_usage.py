"""Run from any working directory: python /path/to/this/file.py --data-root PATH."""
import argparse
from pathlib import Path
import sys

# Source-folder example convenience; only this portable folder is added.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from chronoz_benchmark.service.benchmark_service import BenchmarkService


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", required=True)
    args = parser.parse_args()
    service = BenchmarkService(data_root=args.data_root)
    packet = service.get_packet(["PPIACO", "INDPRO", "TCU"], horizons=[10, 20, 50, 100])
    print(packet.to_json(pretty=True))


if __name__ == "__main__":
    main()
