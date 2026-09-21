"""Historical lookup from portable, provenance-backed metadata only."""
from ..utils.io import read_json
from .correlation import correlation_context
from .redundancy import redundancy_context
from .lead_lag import lead_lag_context

RELATIONSHIP_WARNINGS = ["Correlation != causality.",
                         "Lead-lag is descriptive timing association only; selected peaks are not predictive validation.",
                         "Redundancy != automatic deletion."]


class HistoricalRelationships:
    def __init__(self, path):
        self.data = read_json(path)
        self.records = {}
        for record in self.data["relationships"]:
            key = frozenset((record["series_a"], record["series_b"]))
            if len(key) != 2 or key in self.records:
                raise ValueError("Duplicate/invalid historical relationship pair")
            self.records[key] = record

    def lookup(self, a, b):
        record = self.records.get(frozenset((a, b)), {})
        warnings = list(RELATIONSHIP_WARNINGS)
        warnings += record.get("warnings", [])
        if not record:
            warnings.append("No historical relationship snapshot for this pair; original research covers monthly series only.")
        historical = {**correlation_context(record), **redundancy_context(record),
                      **lead_lag_context(record, record.get("series_a") == b),
                      "transform_policy": self.data["transform_policy"],
                      "snapshot_as_of": self.data["snapshot_as_of"],
                      "source": "config/historical_relationships.json",
                      "research_rolling_60": record.get("research_rolling_60")}
        return historical, warnings
