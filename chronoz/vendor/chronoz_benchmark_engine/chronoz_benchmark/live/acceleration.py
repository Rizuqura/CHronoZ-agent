"""Signed differences of elevations. Labels have no causal economic meaning."""
import math


def calculate_acceleration(rolling, tolerance=0.0):
    result = {}
    for a, b in ((10, 20), (20, 50), (50, 100)):
        x = rolling.get(str(a), {}).get("rolling_elevation")
        y = rolling.get(str(b), {}).get("rolling_elevation")
        result[f"{a}_vs_{b}"] = x - y if x is not None and y is not None and math.isfinite(x) and math.isfinite(y) else None
    values = list(result.values())
    if any(v is None for v in values):
        pattern = "UNAVAILABLE"
    elif all(v > tolerance for v in values):
        pattern = "BROAD_ACCELERATION"
    elif all(v < -tolerance for v in values):
        pattern = "BROAD_DECELERATION"
    elif values[0] > tolerance and all(v <= tolerance for v in values[1:]):
        pattern = "SHORT_TERM_ACCELERATION"
    elif values[0] < -tolerance and all(v >= -tolerance for v in values[1:]):
        pattern = "SHORT_TERM_DECELERATION"
    else:
        pattern = "MIXED"
    return {**result, "pattern": pattern}
