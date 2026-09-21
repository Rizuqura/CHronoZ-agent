"""Validate native observations without sorting, filling, or dropping rows."""
from decimal import Decimal
import numpy as np
import pandas as pd

FREQUENCIES = {"monthly": "MS", "quarterly": "QS", "weekly": "7D"}


def validate_frame(frame, frequency):
    if frequency not in FREQUENCIES:
        raise ValueError(f"Unsupported native frequency: {frequency}")
    if list(frame.columns) != ["date", "value"] or frame.empty:
        raise ValueError("Expected nonempty CSV with exactly date,value columns")
    out = frame.copy()
    out["date"] = pd.to_datetime(out.date, errors="raise")
    out["value"] = pd.to_numeric(out.value, errors="raise")
    if out.date.isna().any() or not out.date.is_unique or not out.date.is_monotonic_increasing:
        raise ValueError("Dates must be valid, unique and sorted in increasing order")
    if out.date.dt.tz is not None or not out.date.eq(out.date.dt.normalize()).all():
        raise ValueError("Observation dates must be timezone-naive calendar dates")
    if np.isinf(out.value.to_numpy(dtype=float)).any():
        raise ValueError("Infinite input values are invalid; missing values may be blank")
    if frequency in {"monthly", "quarterly"}:
        period = out.date.dt.to_period("M" if frequency == "monthly" else "Q")
        if not period.is_unique or not out.date.eq(period.dt.start_time).all():
            raise ValueError(f"{frequency} dates must use unique native-period starts")
    elif out.date.dt.dayofweek.nunique() != 1:
        raise ValueError("Weekly dates must have a consistent weekday; no implicit realignment")
    return out.reset_index(drop=True)


def measurement_decimals(strings):
    values = [v for v in strings if pd.notna(v) and str(v).strip()]
    return max((max(0, -Decimal(str(v)).as_tuple().exponent) for v in values), default=0)


def native_grid(dates, frequency):
    return pd.date_range(dates.min(), dates.max(), freq=FREQUENCIES[frequency])


def validate_horizons(horizons):
    horizons = tuple(horizons)
    if not horizons or any(type(h) is not int or h not in (10, 20, 50, 100) for h in horizons):
        raise ValueError("Horizons must be a nonempty subset of 10, 20, 50, 100")
    if len(set(horizons)) != len(horizons):
        raise ValueError("Duplicate horizons are not allowed")
    return horizons
