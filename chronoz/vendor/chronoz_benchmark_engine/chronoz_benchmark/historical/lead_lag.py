"""Positive k means corr(series_a[t], series_b[t+k]); reversal negates k."""


def lead_lag_context(record, reverse=False):
    lag = record.get("best_descriptive_lag")
    return {"best_descriptive_lag": -lag if reverse and lag is not None else lag,
            "lag_correlation": record.get("lag_correlation"),
            "lag_overlap": record.get("lag_overlap"),
            "lag_unit": "calendar_months", "lag_definition": "corr(series_a[t], series_b[t+k])"}
