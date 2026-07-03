"""Repository-local package shim for src layout.

Allows referencing the local codebase from a source checkout without requiring an
editable install first.
"""

from __future__ import annotations

from pathlib import Path

_PACKAGE_ROOT = Path(__file__).resolve().parent.parent / "src" / "faturama"
__path__ = [str(_PACKAGE_ROOT)]
