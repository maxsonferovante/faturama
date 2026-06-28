from __future__ import annotations

from faturama.infrastructure.files.repository_reader import LocalRepositoryReader


def test_repository_reader_lists_and_searches_files(usage_report_repo):
    reader = LocalRepositoryReader(usage_report_repo)
    files = reader.list_files((".py", ".md", ".toml"))
    hits = reader.search("langgraph", (".toml", ".md"))

    assert any(path.as_posix() == "pyproject.toml" for path in files)
    assert any(hit.path == "pyproject.toml" for hit in hits)
