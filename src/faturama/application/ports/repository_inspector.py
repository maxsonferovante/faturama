"""Port for repository inspection."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(slots=True)
class SearchHit:
    path: str
    line_number: int
    line_text: str
    excerpt: str


class RepositoryInspector(Protocol):
    root: Path

    def list_files(self, suffixes: tuple[str, ...] | None = None) -> list[Path]:
        """Return files relative to the repository root."""

    def read_text(self, relative_path: str) -> str:
        """Read a text file from the repository."""

    def search(self, needle: str, suffixes: tuple[str, ...] | None = None) -> list[SearchHit]:
        """Search the repository for a plain-text needle."""

    def exists(self, relative_path: str) -> bool:
        """Check whether a file exists."""
