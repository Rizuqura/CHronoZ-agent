"""Packet construction is deterministic except for generation time."""
from datetime import datetime, timezone
from .schemas import BenchmarkPacket
from ..utils.io import resource_root


def build_packet(data_root, ids, indicators, relationships):
    warnings = ["Research-use measurements; calibration choices are DEVELOPMENT / AUDIT DEFAULTS.",
                "as_of is packet generation time, not a release or vintage cutoff; latest_date is an observation date.",
                "Historical relationship context is a frozen research snapshot and is not refitted to the supplied data root."]
    for sid, item in indicators.items():
        warnings.extend(f"{sid}: {warning}" for warning in item["warnings"])
    return BenchmarkPacket(
        as_of=datetime.now(timezone.utc).isoformat(),
        engine_version=(resource_root() / "VERSION").read_text(encoding="utf-8").strip(),
        data_root=str(data_root), requested_series=ids, indicators=indicators,
        relationships=relationships, warnings=warnings).validate()
