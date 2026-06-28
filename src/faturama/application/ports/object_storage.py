"""Port for object storage interactions."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol


class ObjectStorage(Protocol):
    def download_to_path(self, bucket: str, object_key: str, destination: Path) -> Path: ...

    def upload_file(self, source: Path, bucket: str, object_key: str) -> str: ...

    def uri_for(self, bucket: str, object_key: str) -> str: ...
