"""Creation-time exporter only. Runtime never calls this or reads the research repo.

Usage: python scripts/export_research_metadata.py --source-root PATH
Writes only this portable folder's registry and frozen relationship snapshot.
"""
import argparse
from pathlib import Path
import hashlib
import json
import pandas as pd
import yaml


def export(source, destination):
    paths = ["data/cleaned/series_metadata.csv", "notebook/deltaAnalysis/CURRENT_MODEL_NOTES.md",
             "notebook/deltaAnalysis/analysis.ipynb", "notebook/deltaAnalysis/audit-PPIACO.ipynb",
             "notebook/deltaAnalysis/audit-PCEC96.ipynb", "notebook/deltaAnalysis/audit-nonstandard-delta-models.ipynb",
             "notebook/matrix-corrAnalysis.ipynb", "notebook/rolling-correlation.ipynb",
             "notebook/lead-lag-correlation.ipynb", "notebook/redundancy-map.ipynb",
             "outputs/correlation/all_change_pairs.csv", "outputs/correlation/change_spearman.csv",
             "outputs/correlation/transformation_registry.csv", "outputs/correlation/provenance.json",
             "outputs/redundancy/all_pairs.csv", "outputs/redundancy/provenance.json",
             "outputs/lead_lag/best_lags.csv", "outputs/lead_lag/provenance.json",
             "outputs/rolling_correlation/pair_stability_summary.csv", "outputs/rolling_correlation/provenance.json"]
    fingerprints = {p: hashlib.sha256((source / p).read_bytes()).hexdigest() for p in paths}
    meta = pd.read_csv(source / paths[0])
    arithmetic = set("DRSDCILM DRTSCILM DRBLACBS TCU CIVPART FEDFUNDS AWHMAN AWHAETP UNRATE".split())
    alternatives = dict(zip("AWHAETP ICSA UNRATE WALCL WRESBAL TOTRESNS".split(),
                            ["DISCRETE_DELTA", "ROBUST_DELTA", "DISCRETE_PLUS_SHOCK",
                             "REGIME_ROBUST_DELTA", "REGIME_ROBUST_DELTA", "STRUCTURAL_EPOCH_ROBUST_DELTA"]))
    caution = {
        "PPIACO": "Regime-sensitive historical distribution; tails retained; standard z is not a Gaussian probability.",
        "PCEC96": "Modified-z events are excluded from calibration only; all events remain scoreable; latest observation is held out.",
        "AWHMAN": "GOOD selection retained despite discrete rounding and substantial zero changes.",
        "PAYEMS": "Log change retained; absolute jobs change is an unimplemented proposal; crisis tails can dominate.",
        "IPMAN": "Separate manufacturing-production research annotation retained; crisis tails remain.",
        "M2SL": "Acceleration research annotation does not alter the log transform; pooled history is regime-sensitive.",
        "RPI": "Transfer-related extreme movements remain in the unconditional historical reference.",
        "FEDFUNDS": "Arithmetic changes are percentage points; policy steps and regimes limit unconditional interpretation.",
    }
    registry = {}
    for row in meta.itertuples():
        sid = row.series_id
        spec = {"name": row.name, "category": row.category, "frequency": row.expected_frequency,
                "transform": "ARITHMETIC_DELTA" if sid in arithmetic else "LOG_DELTA",
                "model_family": alternatives.get(sid, "STANDARD_DELTA"),
                "selection": "GOOD" if sid not in alternatives else "PASS_ALTERNATIVE_MODEL",
                "reference_timing": "PRE_LATEST" if sid in alternatives or sid == "PCEC96" else "FULL_SNAPSHOT",
                "calibration_end": None,
                "warnings": [caution[sid]] if sid in caution else []}
        if sid in {"DRBLACBS", "TCU", "CIVPART", "FEDFUNDS", "UNRATE", "DRSDCILM", "DRTSCILM"}:
            spec["level_unit"] = "percent"
        if sid == "PCEC96":
            spec["calibration_filter"] = "MODIFIED_Z"
        if spec["reference_timing"] == "FULL_SNAPSHOT":
            spec["warnings"].append("Full-snapshot reference includes the current observation; scores are retrospective.")
        registry[sid] = spec
    (destination / "benchmark_registry.yaml").write_text(
        yaml.safe_dump({"status": "RESEARCH SELECTION / DEVELOPMENT IMPLEMENTATION",
                        "methodology_source": "CURRENT_MODEL_NOTES.md, 2026-09-20",
                        "ordinary_good_timing": "Full snapshot is an exposed engineering default following PPIACO; no implied held-out validation.",
                        "series": registry}, sort_keys=False), encoding="utf-8")
    provenance = json.loads((source / "outputs/redundancy/provenance.json").read_text(encoding="utf-8"))
    name_to_id = {name: sid for sid, name in provenance["series_display_names"].items()}
    pairs = pd.read_csv(source / "outputs/correlation/all_change_pairs.csv")
    ranks = pd.read_csv(source / "outputs/correlation/change_spearman.csv", index_col=0)
    redundancy = pd.read_csv(source / "outputs/redundancy/all_pairs.csv")
    lags = pd.read_csv(source / "outputs/lead_lag/best_lags.csv")
    rolling = pd.read_csv(source / "outputs/rolling_correlation/pair_stability_summary.csv")

    def keyed(frame):
        return {frozenset((r["Dataset 1"], r["Dataset 2"])): r for r in frame.to_dict("records")}

    red, lag, roll = keyed(redundancy), keyed(lags), keyed(rolling)
    records = []
    for row in pairs.to_dict("records"):
        a, b = row["Dataset 1"], row["Dataset 2"]
        key = frozenset((a, b))
        r, l, w = red[key], lag[key], roll[key]
        k = int(l["Lag months"])
        if l["Dataset 1"] != a:
            k = -k
        records.append({"series_a": name_to_id[a], "series_b": name_to_id[b],
                        "pearson": row["Correlation"], "spearman": float(ranks.loc[a, b]),
                        "overlap": int(row["Overlapping observations"]),
                        "overlap_start": row["Overlap start"], "overlap_end": row["Overlap end"],
                        "redundancy_candidate": bool(r["Candidate"]),
                        "best_descriptive_lag": k, "lag_correlation": l["Pearson"],
                        "lag_overlap": int(l["Overlapping observations"]),
                        "research_rolling_60": {"latest_end": w["Latest window end"],
                                                "pearson": w["Latest correlation"],
                                                "overlap": int(w["Latest paired observations"]),
                                                "minimum": w["Minimum correlation"], "maximum": w["Maximum correlation"]},
                        "warnings": ["Historical monthly relationships use percentage changes / first differences, not benchmark log deltas.",
                                     "Historical coefficients are a frozen research snapshot; histories and lag-specific samples differ."]})
    sources = {}
    for section in ("correlation", "redundancy", "lead_lag", "rolling_correlation"):
        p = json.loads((source / f"outputs/{section}/provenance.json").read_text(encoding="utf-8"))
        sources[section] = {k: v for k, v in p.items() if k != "series_display_names"}
    payload = {"snapshot_as_of": sources["correlation"]["executed_utc"],
               "transform_policy": "RESEARCH_PERCENT_OR_DIFFERENCE",
               "frequency_scope": "monthly", "minimum_historical_overlap": 60,
               "lag_definition": "corr(series_a[t], series_b[t+k]); k>0 first precedes second, calendar months",
               "redundancy_screen": {"abs_pearson": .8, "abs_spearman": .6, "matching_signs": True, "minimum_overlap": 60},
               "source_file_sha256": fingerprints, "source_provenance": sources, "relationships": records}
    (destination / "historical_relationships.json").write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"Exported {len(registry)} series and {len(records)} historical pairs.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True, type=Path)
    args = parser.parse_args()
    export(args.source_root.resolve(), Path(__file__).resolve().parents[1] / "config")
