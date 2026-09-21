"""Copyable CLI entry point; works from any current working directory."""
from chronoz_benchmark.service.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
