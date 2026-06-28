"""Money value object."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP


@dataclass(frozen=True, slots=True)
class Money:
    amount: Decimal
    currency: str = "BRL"

    @classmethod
    def from_str(cls, raw: str, currency: str = "BRL") -> "Money":
        normalized = (
            raw.replace("R$", "")
            .replace(".", "")
            .replace(",", ".")
            .replace(" ", "")
            .strip()
        )
        return cls(Decimal(normalized).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), currency)

    def __str__(self) -> str:
        return f"{self.currency} {self.amount}"
