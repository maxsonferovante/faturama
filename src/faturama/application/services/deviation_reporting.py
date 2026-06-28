"""Formatting helpers for deviations."""

from __future__ import annotations

from dataclasses import asdict

from faturama.domain.entities.specification_deviation import SpecificationDeviation


def serialize_deviation(deviation: SpecificationDeviation) -> dict[str, object]:
    payload = asdict(deviation)
    payload["criticality"] = deviation.criticality.value
    return payload
