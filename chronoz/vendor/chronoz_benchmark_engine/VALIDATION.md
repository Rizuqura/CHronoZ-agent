# Delivery validation

Artifact: `export/chronoz_benchmark_engine/`, version **0.1.0**.

**39 tests passed**, with no skips, against the supplied repository data. The final suite was run with warnings promoted to errors:

```sh
python -W error -m unittest discover -s tests -t . -v
```

`CHRONOZ_TEST_DATA_ROOT` was explicitly set to the current repository's cleaned-data directory. The portable tests never infer a research repository root. Without that environment variable, the three real-data smoke tests skip and all synthetic tests remain runnable.

Coverage: external roots/configuration, all transforms and native-frequency gaps, all six model families, PCEC96 calibration-only exclusion/holdout, full-history scoring, discrete precision/unseen outcomes, zero scales, sparse regimes, prior-window timing, structural boundaries, rolling statistics/elevation/local scores, acceleration patterns, relationship lookup/lag orientation, direct rolling Pearson/Spearman comparisons, pair sample floors/frequency mismatch, missing latest observations, JSON serialization/schema rejection, CLI stdout/file output/errors and a copied-folder test from an unrelated working directory.

The real-data smoke created PPIACO/INDPRO/TCU packets and a full **36-indicator / 630-pair packet**. PCEC96 reconciles to the research audit: **234 valid deltas, 233 eligible, 12 calibration exclusions, 221 retained**, sample standard deviation approximately 0.2717. The frozen historical relationship config includes **351 monthly pairs**.

The CLI was run **inside the portable folder**, with an externally resolved absolute data root:

```powershell
python benchmark_cli.py --data-root $dataRoot --series PPIACO INDPRO TCU --horizons 10 20 50 100 --pretty --output examples/example_output.json
```

stdout parsed as JSON, and the saved example validates against the bundled JSON Schema. The example's `data_root` was then replaced with a descriptive placeholder and validated again, so it contains no machine-specific local path. All measured values and input fingerprints are retained. Latest observations in this example:

| Series | Observation date | Historical z |
| --- | --- | ---: |
| PPIACO | 2026-08-01 | 0.567527 |
| INDPRO | 2026-07-01 | -0.018534 |
| TCU | 2026-07-01 | 0.143816 |

`python scripts/validate_portability.py --data-root <external-directory>` also passed. It built `chronoz_benchmark_engine-0.1.0-py3-none-any.whl` offline using installed build tools, unpacked it into an isolated temporary directory and executed the Python API using `python -I -W error` from an unrelated cwd. Every imported `chronoz_benchmark` module and all runtime resources were verified to originate in that temporary installation. The wheel test returned three indicators and three relationships with valid JSON and empty stderr. Temporary build products are not part of this delivery.

Validation environment: Python 3.14; pandas 3.0.2; NumPy 2.4.4; setuptools 82.0.1. The declared Python/dependency ranges support installation elsewhere, but this delivery was not tested across an OS/version matrix.

Remaining experimental choices: regime speed buckets/13-week window/P20-P80 thresholds; minimum group size; two-versus-three epoch partition (three selected); outlier/rarity thresholds; ordinary GOOD-series full-snapshot timing; full-window rolling-score requirement; signed acceleration pattern rules; live 10/20/50/100 correlation sample floors and sample-size labels; extension of relationship calculations to compatible nonmonthly series. These choices and their source/engineering status are exposed in configuration and explained in README.md.

Portability status: **no known runtime dependency on the original repository**. Python and declared dependencies must be installed and cleaned economic CSVs must be provided externally, as intended. Only the optional creation-time metadata refresh script requires the original research layout. Historical relationship metadata remains a frozen snapshot. No FastAPI server or external agent integration was added.

Original tracked research notebooks, economic data and research outputs remain unchanged. All delivery changes are confined to the new portable folder. Source fingerprints used by metadata extraction were checked against the source files after implementation.

## Complete delivered file tree

```text
chronoz_benchmark_engine/
|-- chronoz_benchmark/
|   |-- historical/
|   |   |-- __init__.py
|   |   |-- calibration.py
|   |   |-- correlation.py
|   |   |-- lead_lag.py
|   |   |-- redundancy.py
|   |   `-- relationships.py
|   |-- live/
|   |   |-- __init__.py
|   |   |-- acceleration.py
|   |   |-- relationships.py
|   |   |-- rolling.py
|   |   `-- spread.py
|   |-- models/
|   |   |-- __init__.py
|   |   |-- base.py
|   |   |-- discrete_delta.py
|   |   |-- discrete_plus_shock.py
|   |   |-- regime_robust_delta.py
|   |   |-- robust_delta.py
|   |   |-- standard_delta.py
|   |   `-- structural_epoch.py
|   |-- packet/
|   |   |-- __init__.py
|   |   |-- builder.py
|   |   `-- schemas.py
|   |-- registry/
|   |   |-- __init__.py
|   |   |-- benchmark_registry.py
|   |   `-- series_registry.py
|   |-- service/
|   |   |-- __init__.py
|   |   |-- benchmark_service.py
|   |   `-- cli.py
|   |-- transforms/
|   |   |-- __init__.py
|   |   |-- delta.py
|   |   `-- validation.py
|   |-- utils/
|   |   |-- __init__.py
|   |   |-- io.py
|   |   `-- logging.py
|   `-- __init__.py
|-- config/
|   |-- benchmark_registry.yaml
|   |-- engine_defaults.yaml
|   |-- historical_relationships.json
|   `-- structural_epochs.yaml
|-- examples/
|   |-- example_input.json
|   |-- example_output.json
|   `-- example_python_usage.py
|-- schemas/
|   `-- benchmark_packet.schema.json
|-- scripts/
|   |-- build_schema.py
|   |-- export_research_metadata.py
|   `-- validate_portability.py
|-- tests/
|   |-- __init__.py
|   |-- helpers.py
|   |-- test_discrete.py
|   |-- test_live.py
|   |-- test_packet.py
|   |-- test_regime.py
|   |-- test_robust_delta.py
|   |-- test_smoke.py
|   |-- test_standard_delta.py
|   `-- test_transforms.py
|-- .gitignore
|-- INTEGRATION.md
|-- MANIFEST.in
|-- README.md
|-- VALIDATION.md
|-- VERSION
|-- benchmark_cli.py
|-- pyproject.toml
|-- requirements.txt
`-- setup.py
```
