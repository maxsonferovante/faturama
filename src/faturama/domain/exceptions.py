"""Domain-specific exceptions."""

from __future__ import annotations


class FaturamaError(Exception):
    """Base project error."""


class ArtifactNotFoundError(FaturamaError):
    """Raised when extracted artifacts cannot be found."""


class ParsingError(FaturamaError):
    """Raised when a document cannot be parsed safely."""


class ReviewRequiredError(FaturamaError):
    """Raised when manual review is required to proceed."""

