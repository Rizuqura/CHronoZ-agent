# CHronoZ benchmark engine

Version **0.1.0**. Copy this entire folder into another project and supply a cleaned-data directory. The engine calculates descriptive economic benchmark measurements for the **36 research-selected series**. It does not require the original repository, notebooks, research output folders, network access, or a metadata CSV at runtime.

The engine does not call an LLM, read user prose, select relevant series for a question, infer causes, produce macro narratives, or recommend investments. Series selection and reasoning belong to the external agent. No agent repository is integrated here.

## Installation and entry points

Python 3.10 or newer is required. From this folder:

```sh
python -m pip install -r requirements.txt
python benchmark_cli.py --data-root /path/to/cleaned --series PPIACO INDPRO TCU --pretty
```

Alternatively, install the folder as a package:

```sh
python -m pip install .
chronoz-benchmark --data-root /path/to/cleaned --series PPIACO INDPRO TCU
```

Wheels bundle config, schema and VERSION under `chronoz_benchmark/_resources`. Source-folder execution resolves resources relative to the package file, independent of the working directory. `setup.py` only implements resource bundling; there are no external path dependencies. Runtime requirements are pandas, NumPy, PyYAML and jsonschema. Tests use the Python standard library's unittest.

## Data requirements

Pass `data_root` explicitly. Each requested series needs `<series_id>.csv` directly under that directory, with exactly these columns:

```csv
date,value
2026-01-01,101.2
2026-02-01,101.5
```

Dates must be sorted, unique, timezone-naive calendar dates. Monthly data uses month starts; quarterly data uses calendar quarter starts; weekly data uses one consistent weekday. Native frequency, name, category, units where needed, and selected model come from the bundled registry. No data path in the source metadata is carried into that registry. Replacing the data requires preserving each series' units and meaning.

Missing periods may be absent; missing values may be blank. They stay unavailable. Nonnumeric values, infinite values, duplicate dates, mixed weekly weekdays and noncanonical period labels fail validation. There is no sorting, resampling, interpolation, seasonal adjustment, filling or historical tail deletion. A delta requires consecutive native periods and two finite endpoints; log changes additionally require both endpoints to be positive. Missing October makes both October's delta and the September-to-November delta unavailable. The initial observation has no delta.

The latest indicator always refers to the last input row, even if its value/change is missing. The service does not silently substitute an older observation. Each indicator reports input SHA-256 and transform exclusion counts. Publish new input snapshots atomically if callers can read while files are updated; cross-file atomicity is the caller's responsibility.

## Model methodology

Source of selection: `CURRENT_MODEL_NOTES.md` dated 2026-09-20, the delta-analysis notebook and the PPIACO, PCEC96 and nonstandard-model audits. Source file hashes are retained in `config/historical_relationships.json`. This is a wrapped research implementation, not a validated forecasting model.

| Family | Series | Primary representation / reference |
| --- | --- | --- |
| STANDARD_DELTA | 29 GOOD series including PPIACO | Mean and sample std; signed z; right-inclusive empirical percentile; all tails retained |
| STANDARD_DELTA with MODIFIED_Z calibration filter | PCEC96 | Log delta; calibration-only exclusions; mean/std and ECDF fitted to retained eligible history |
| ROBUST_DELTA | ICSA | Median and 1.4826 MAD; robust z and empirical percentile; tails retained and flagged |
| DISCRETE_DELTA | AWHAETP | Empirical PMF, cumulative percentile, rarity, zero-share; no Gaussian primary score |
| DISCRETE_PLUS_SHOCK | UNRATE | Discrete distribution plus robust shock flag |
| REGIME_ROBUST_DELTA | WALCL, WRESBAL | Regime-specific robust primary score and global diagnostic scores |
| STRUCTURAL_EPOCH_ROBUST_DELTA | TOTRESNS | Ending-date epoch-specific robust primary score and global diagnostics |

LOG_DELTA is `100 * (ln(x_t) - ln(x_previous))`: approximate percent change for small moves, not annualized. ARITHMETIC_DELTA is `x_t - x_previous`. BASIS_POINT_DELTA is `100 * (x_t - x_previous)` and requires registry `level_unit: percent`. FEDFUNDS defaults to arithmetic percentage points, matching the notebook; changing its transform to basis points is explicit. PAYEMS retains log change. DRTSCILM and DRSDCILM retain their meaningful raw survey levels alongside changes.

Sample standard deviations use ddof=1, MAD is unscaled in summaries, and quantiles use linear interpolation. Percentile is `100 * count(reference <= observation) / N`; ties are right-inclusive. A z-score does not imply a Gaussian probability. PPIACO's regime-sensitivity caution and tails remain visible. State labels follow the PPIACO/PCEC96 audits, with signed ABOVE/BELOW referring to benchmark center, not necessarily positive/negative growth.

PCEC96 first fits median and MAD on pre-latest eligible history. It flags `abs(0.6745 * (delta - median) / MAD) > 3.5`, excludes those observations **only from calibration**, then scores every observation against the retained calibration mean/std and ECDF. The filter is one pass, with no date-specific crisis exclusions or winsorization. Its audit requires nonzero MAD; zero MAD makes that calibration unavailable with a warning. Other robust models use the audit's `IQR / 1.349` fallback when MAD is zero; zero MAD and IQR yield unavailable scores, not zero scores or false shock flags.

Discrete deltas are rounded to the source CSV's maximum recorded decimal precision before building the PMF. Unseen values have probability zero and rarity one. Rarity is `1 - point probability`, not a p-value. The full discrete history, including shock observations, remains eligible apart from the reporting holdout. UNRATE uses exact modified z when MAD is usable and the explicit IQR fallback otherwise.

Regimes use the **preceding** 13 native weekly deltas, excluding the current delta. P20/P80 of pre-latest prior-window means define CONTRACTION, NEUTRAL, EXPANSION; missing windows stay UNCLASSIFIED. These are relative statistical speed buckets, not identified QE/QT periods or guaranteed signs of growth. Thresholds and group references exclude the latest reporting row. Groups with fewer than 30 deltas have null conditioned scores; global scores are diagnostic and never silently replace them.

TOTRESNS defaults to PRE_2008, 2008_TO_2019, 2020_PLUS. Boundaries are editable audit hypotheses, not estimated structural breaks. Changes crossing a boundary belong to their ending-date epoch. The audit tested both two and three epochs; selecting three is an explicit V0 engineering default.

## Reference timing and retained history

PPIACO uses the full historical snapshot including the current observation, as in its audit. Other ordinary GOOD series follow that **exposed development default**, since their exact production timing is not specified by research. PCEC96 and all six alternative models use pre-latest calibration, as in their audits. Each series has `reference_timing` and optional `calibration_end` in `config/benchmark_registry.yaml`. A pinned cutoff for a PRE_LATEST series must precede the latest row.

Calibration metadata includes timing, eligible count, retained count and last eligible date. Earlier historical scores are retrospective: fitted parameters use later history relative to those earlier dates. This is not a vintage-aware or look-ahead-free backtest.

Model instances retain the full input frame and expose `score_history()` for audit/replay. The packet reports the latest observation and aggregate reference metadata, not every historical row. PCEC96's excluded historical events are still scoreable through `score_history()`; exclusion is never input deletion.

## Python usage and API

```python
from chronoz_benchmark import BenchmarkService

service = BenchmarkService(data_root="/path/to/cleaned")
packet = service.get_packet(["PPIACO", "INDPRO", "TCU"], horizons=[10, 20, 50, 100])
print(packet.to_json(pretty=True))
```

`examples/example_python_usage.py` is runnable with `--data-root`. APIs:

- `BenchmarkService(data_root, config_root=None)`: load and validate portable configuration.
- `get_series(series_ids, horizons=(10,20,50,100))`: JSON-safe indicator dictionary.
- `get_relationships(series_ids, horizons=(10,20,50,100))`: all unique requested pairs.
- `get_packet(series_ids, horizons=(10,20,50,100))`: validated `BenchmarkPacket` with `to_dict()`, `validate()`, `to_json(pretty=False)`.
- `describe_series(series_id)`: selected registry specification.
- `healthcheck()`: configuration/file-availability report; data contents are validated on request. Partial data directories are allowed.

Passing `horizons=None` uses `engine_defaults.yaml`; omitting the argument uses the documented four-window API default. Only nonempty, unique subsets of 10/20/50/100 are supported in V0. Unknown identifiers, invalid data/configuration and missing requested files fail explicitly; a partially built packet is not emitted. Each call reloads requested files. A packet reuses those loaded frames across indicators and relationships.

## CLI

```sh
python benchmark_cli.py --data-root /path/to/cleaned --series PPIACO INDPRO TCU
python benchmark_cli.py --data-root /path/to/cleaned --series PPIACO INDPRO TCU --horizons 10 20 50 100 --pretty --output packet.json
python /path/to/copied/engine/benchmark_cli.py --data-root /external/cleaned --series WALCL WRESBAL
```

Success writes one JSON document to stdout, including when `--output` also writes a file. Runtime diagnostics go to stderr; failures return exit code 2 with no packet on stdout. CLI help is standard argparse help. `--config-root` accepts a complete copy of the four config files. Outputs inside the data/config directories are rejected to avoid overwriting inputs.

## Packet contract

`schemas/benchmark_packet.schema.json` is the versioned JSON Schema (Draft 2020-12). The service validates packets; all nonfinite/unavailable numeric values serialize as JSON null. Top-level fields are `as_of`, `engine_version`, `data_root`, `requested_series`, `indicators`, `relationships`, `warnings`. `as_of` is UTC **generation time**, not an observation cutoff, publication time or data vintage.

Each indicator includes latest date/value/change, family, historical primary score and its `score_type`, empirical percentile/ranges, model-specific calibration diagnostics, rolling statistics, acceleration, flags and warnings. Discrete primary scores are PMF probabilities: do not compare their magnitude with z-scores. Regime/epoch global diagnostic scores are in `historical.model_specific`.

Model-specific diagnostics are an extensible object inside the otherwise constrained contract. Consumers must use `score_type` and `model_family` and inspect nulls/warnings. Requested horizon subsets appear as subsets of the rolling map; missing acceleration inputs yield UNAVAILABLE.

`examples/example_output.json` is generated from the current PPIACO/INDPRO/TCU research data, with only `data_root` replaced by an explanatory placeholder for portability. It is an example snapshot, not live data.

## Rolling structure and acceleration

Windows cover the latest 10/20/50/100 **native calendar positions**, including the latest observation. These mean weeks, months or quarters depending on the series. Calendar grids add missing positions as NaNs only; they never fabricate observations. Windows cannot reach farther back to replace missing values.

Every window exposes n, mean, median, sample std and unscaled MAD of available deltas, even when incomplete. By default, continuous scores require a full window and all observations. `rolling_min_fraction` is an editable engineering threshold. All tail observations participate in rolling statistics, including PCEC96 events excluded from historical fitting.

For standard models, rolling elevation is `(rolling mean - historical mean) / historical std`; local score is `(latest delta - rolling mean) / rolling std`. Robust models use median and robust scale. Regime/epoch elevation uses the **currently active group's** historical reference throughout the comparison; a rolling window can itself span groups. Discrete models return null elevation/local scores with an explanation. Zero scales remain unavailable.

Acceleration is elevation(10)-elevation(20), elevation(20)-elevation(50), elevation(50)-elevation(100). All positive differences imply BROAD_ACCELERATION; all negative imply BROAD_DECELERATION. A positive first difference with both remaining differences nonpositive implies SHORT_TERM_ACCELERATION; the symmetric rule implies SHORT_TERM_DECELERATION. Other finite combinations, including flat, are MIXED. Any unavailable input yields UNAVAILABLE. `acceleration_tolerance` defaults to zero and is configurable. These signed descriptive labels are engineering conventions, not causal economic interpretations. The historical reference remains the long-run benchmark; rolling windows do not replace it.

## Relationships

`config/historical_relationships.json` contains **351 monthly pairs** extracted from the original correlation, redundancy, lead-lag and rolling-correlation outputs. It includes Pearson/Spearman, overlap dates/counts, redundancy candidate, best descriptive lag, lag coefficient/count, original 60-month rolling summary, source timestamps and SHA-256 provenance. Original outputs are not read at runtime. Historical data is **frozen**, even if the external input data is newer or different. There is no automatic historical relationship refit.

The relationship research uses percentage changes for positive quantities and first differences for rates/hours. Live relationships intentionally use the same convention, reported under `live_transforms`; these differ from benchmark log deltas. Weekly/quarterly same-frequency calculation is an explicitly enabled development extension. Incompatible frequencies or weekly weekdays return null correlations and warnings, without resampling.

Live windows use exact aligned native dates, ending at the later series' latest date. Different endpoints remain missing. Require a complete elapsed window since the first paired delta and at least 8/15/40/80 valid pairs for horizons 10/20/50/100. Constant windows return null. Spearman is Pearson correlation of average within-window ranks. No significance tests or rolling lag search are implemented.

Sample-size labels are 10=LOW, 20=EXPLORATORY, 50=MODERATE, 100=STRONGER. They describe **only sample-size reliability**, not statistical significance or independence. Overlapping windows, autocorrelation and crisis observations can materially affect results.

Positive lag k means `corr(series_a[t], series_b[t+k])` using calendar months. Reversing a requested pair negates k. Correlation != causality. Lead-lag is descriptive timing association only. Redundancy != automatic deletion. The historical redundancy rule requires at least 60 pairs, abs(Pearson)>=0.8, abs(Spearman)>=0.6 and matching signs; V0 preserves the saved decisions.

## Configuration, tests and limitations

All audit thresholds live in `config/engine_defaults.yaml`; series transforms/timing live in `benchmark_registry.yaml`; epoch boundaries live in `structural_epochs.yaml`. These are current research/development defaults, not economic truth. To change installed package settings, copy the config directory elsewhere and supply `config_root`.

From this portable folder:

```sh
python -m unittest discover -s tests -t . -v
```

Synthetic tests need no source data. To enable the current-data smoke tests, set `CHRONOZ_TEST_DATA_ROOT` to your explicit cleaned-data directory, then run the same command. The smoke suite includes PPIACO/INDPRO/TCU, all 36 model selections and a snapshot-conditional reconciliation of PCEC96's 234 deltas, 233 eligible months, 12 exclusions and 221 retained calibration observations. Copy/move and CLI tests run with an unrelated working directory.

Creation-only `scripts/export_research_metadata.py --source-root PATH` can refresh the registry and frozen metadata from the original research layout; it is never needed for runtime and regenerates those two config files. `scripts/build_schema.py` regenerates the checked-in schema. Changes to either contract or methodology require review and an appropriate version change.

`scripts/validate_portability.py --data-root PATH` builds and exercises a wheel offline in an isolated temporary installation, using already installed setuptools/wheel. See `VALIDATION.md` for the executed checks and complete delivered file tree.

Limits: revised rather than vintage data; no release-time alignment; retrospective fitted history; unvalidated epoch boundaries/regimes/thresholds; precision-dependent discrete probabilities; no confidence intervals, forecasting, causality or production calibration guarantees. There is no HTTP server in V0. See `INTEGRATION.md` for the canonical subprocess boundary.
