# CHronoZ agent bundle

Copy `vendor/` and `data/` from this folder into your agent repository, preserving this layout:

```text
your-agent-repo/
  src/                              # your existing agent code
  vendor/
    chronoz_benchmark_engine/        # Python engine, config, schema and docs
  data/
    cleaned/                        # 36 series CSVs plus series_metadata.csv
```

These are copies of the cleaned research data, not a live data feed. Original source files are unchanged. `DATA_MANIFEST.json` records SHA-256 hashes for all 37 copied CSVs. The metadata CSV is supplied for reference; the engine uses its own bundled registry and reads the requested series CSVs directly.

From your agent repository root:

```sh
python -m pip install -r vendor/chronoz_benchmark_engine/requirements.txt
python vendor/chronoz_benchmark_engine/benchmark_cli.py --data-root ./data/cleaned --series PPIACO INDPRO TCU --horizons 10 20 50 100 --pretty
```

Use your installed Python interpreter or virtual environment if `python` is not available on PATH. For Node subprocess calls, resolve both the CLI and data directory to absolute paths in the host application. See `vendor/chronoz_benchmark_engine/INTEGRATION.md` for the TypeScript example.

Merge these directories into the destination deliberately if files with the same names already exist. No agent code or integration has been added to another repository.
