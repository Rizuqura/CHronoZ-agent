"""JSON-only stdout on success; diagnostics on stderr and nonzero errors."""
import argparse
import logging
from pathlib import Path
import sys
from .benchmark_service import BenchmarkService
from ..utils.logging import configure_logging


def main(argv=None):
    parser = argparse.ArgumentParser(description="Portable CHronoZ benchmark measurements")
    parser.add_argument("--data-root", required=True)
    parser.add_argument("--config-root")
    parser.add_argument("--series", nargs="+", required=True)
    parser.add_argument("--horizons", nargs="+", type=int, choices=[10, 20, 50, 100])
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    configure_logging()
    try:
        service = BenchmarkService(args.data_root, args.config_root)
        packet = service.get_packet(args.series, args.horizons)
        payload = packet.to_json(pretty=args.pretty)
        if args.output:
            target = args.output.expanduser().resolve()
            if target.is_relative_to(service.data_root) or target.is_relative_to(service.config_root):
                raise ValueError("Output must not overwrite files inside data_root or config_root")
            target.write_text(payload + "\n", encoding="utf-8")
        sys.stdout.write(payload + "\n")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        logging.error("%s", error)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
