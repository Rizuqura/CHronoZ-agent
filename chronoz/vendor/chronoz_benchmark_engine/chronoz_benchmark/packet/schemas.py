"""Stable machine contract, validated before delivery."""
from dataclasses import dataclass
from typing import Any
import json
from jsonschema import Draft202012Validator, FormatChecker
from ..utils.io import read_json, resource_root, json_safe


@dataclass(frozen=True)
class BenchmarkPacket:
    as_of: str
    engine_version: str
    data_root: str
    requested_series: list[str]
    indicators: dict[str, Any]
    relationships: list[dict[str, Any]]
    warnings: list[str]

    def to_dict(self):
        return json_safe({key: getattr(self, key) for key in self.__dataclass_fields__})

    def validate(self):
        schema = read_json(resource_root() / "schemas" / "benchmark_packet.schema.json")
        Draft202012Validator(schema, format_checker=FormatChecker()).validate(self.to_dict())
        if set(self.requested_series) != set(self.indicators):
            raise ValueError("Packet indicators must exactly match requested_series")
        for sid, item in self.indicators.items():
            if item["series_id"] != sid:
                raise ValueError("Indicator key and series_id mismatch")
        return self

    def to_json(self, pretty=False):
        self.validate()
        return json.dumps(self.to_dict(), allow_nan=False, indent=2 if pretty else None)
