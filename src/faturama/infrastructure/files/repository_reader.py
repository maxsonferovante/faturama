"""Repository scanning primitives."""

from __future__ import annotations

from pathlib import Path

from faturama.application.ports.repository_inspector import RepositoryInspector, SearchHit


IGNORED_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "venv",
    "build",
    "dist",
}


class LocalRepositoryReader(RepositoryInspector):
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()

    def list_files(self, suffixes: tuple[str, ...] | None = None) -> list[Path]:
        files: list[Path] = []
        for path in self.root.rglob("*"):
            if not path.is_file():
                continue
            if any(part in IGNORED_DIRS for part in path.relative_to(self.root).parts):
                continue
            if suffixes and path.suffix not in suffixes:
                continue
            files.append(path.relative_to(self.root))
        return sorted(files)

    def read_text(self, relative_path: str) -> str:
        return (self.root / relative_path).read_text(encoding="utf-8")

    def exists(self, relative_path: str) -> bool:
        return (self.root / relative_path).exists()

    def search(self, needle: str, suffixes: tuple[str, ...] | None = None) -> list[SearchHit]:
        hits: list[SearchHit] = []
        normalized = needle.casefold()
        for path in self.list_files(suffixes):
            text = (self.root / path).read_text(encoding="utf-8")
            lines = text.splitlines()
            for index, line in enumerate(lines, start=1):
                if normalized not in line.casefold():
                    continue
                excerpt = self._excerpt(lines, index)
                hits.append(
                    SearchHit(
                        path=path.as_posix(),
                        line_number=index,
                        line_text=line.strip(),
                        excerpt=excerpt,
                    )
                )
        return hits

    @staticmethod
    def _excerpt(lines: list[str], index: int, radius: int = 0) -> str:
        start = max(index - radius - 1, 0)
        end = min(index + radius, len(lines))
        return "\n".join(lines[start:end]).strip()
