"""Compatibility layer for Pydantic-style models."""

from __future__ import annotations

from dataclasses import MISSING, asdict, dataclass, field, fields
from typing import Any, Callable

try:  # pragma: no cover - exercised when pydantic exists
    from pydantic import BaseModel, ConfigDict, Field, ValidationError
except Exception:  # pragma: no cover - fallback is tested instead
    ConfigDict = dict

    class ValidationError(ValueError):
        """Fallback validation error."""

    def Field(default: Any = MISSING, default_factory: Callable[[], Any] | None = None, **_: Any) -> Any:
        if default_factory is not None:
            return field(default_factory=default_factory)
        if default is MISSING:
            return field()
        return field(default=default)

    class BaseModel:
        """Minimal subset of the Pydantic API used by this project."""

        model_config = ConfigDict()

        def __init_subclass__(cls, **kwargs: Any) -> None:
            super().__init_subclass__(**kwargs)
            if not getattr(cls, "__dataclass_fields__", None):
                dataclass(cls)

        def __post_init__(self) -> None:
            for f in fields(self):
                value = getattr(self, f.name)
                if value is None and f.default is MISSING and f.default_factory is MISSING:
                    raise ValidationError(f"{f.name} is required")

        @classmethod
        def model_validate(cls, data: dict[str, Any] | "BaseModel") -> "BaseModel":
            if isinstance(data, cls):
                return data
            if not isinstance(data, dict):
                raise ValidationError("Expected a mapping")
            return cls(**data)

        def model_dump(self) -> dict[str, Any]:
            return asdict(self)

