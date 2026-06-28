"""Local-friendly S3-style storage adapter."""

from __future__ import annotations

from pathlib import Path
import shutil

from faturama.application.ports.object_storage import ObjectStorage


class S3StorageAdapter(ObjectStorage):
    def __init__(self, *, root_dir: Path) -> None:
        self.root_dir = root_dir
        self.root_dir.mkdir(parents=True, exist_ok=True)

    def _object_path(self, bucket: str, object_key: str) -> Path:
        return self.root_dir / bucket / object_key

    def download_to_path(self, bucket: str, object_key: str, destination: Path) -> Path:
        source = self._object_path(bucket, object_key)
        if not source.exists():
            raise FileNotFoundError(f"Object not found: s3://{bucket}/{object_key}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        for suffix in (".md", ".json"):
            sidecar = source.with_suffix(suffix)
            if sidecar.exists():
                shutil.copy2(sidecar, destination.with_suffix(suffix))
        output_dir = source.parent / "output" / source.stem
        if output_dir.exists():
            target_output = destination.parent / "output" / destination.stem
            if target_output.exists():
                shutil.rmtree(target_output)
            shutil.copytree(output_dir, target_output)
        return destination

    def upload_file(self, source: Path, bucket: str, object_key: str) -> str:
        destination = self._object_path(bucket, object_key)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        return self.uri_for(bucket, object_key)

    def uri_for(self, bucket: str, object_key: str) -> str:
        return f"s3://{bucket}/{object_key}"
