"""Copied historical coefficients retain their original transform and coverage."""


def correlation_context(record):
    keys = ("pearson", "spearman", "overlap", "overlap_start", "overlap_end")
    return {key: record.get(key) for key in keys}
