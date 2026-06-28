"""AWS S3 object storage adapter."""

from __future__ import annotations

from pathlib import Path
import os

from boto3 import client
from botocore.config import Config

from faturama.application.ports.object_storage import ObjectStorage


class S3StorageAdapter(ObjectStorage):
    def __init__(
        self,
        *,
        endpoint_url: str | None = None,
        region: str = "us-east-1",
    ) -> None:
        access_key = os.getenv("AWS_ACCESS_KEY_ID") or "ministack"
        secret_key = os.getenv("AWS_SECRET_ACCESS_KEY") or "ministack"
        session_token = os.getenv("AWS_SESSION_TOKEN")
        self.s3 = client(
            "s3",
            endpoint_url=endpoint_url,
            region_name=region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            aws_session_token=session_token,
            config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
        )

    def download_to_path(self, bucket: str, object_key: str, destination: Path) -> Path:
        destination.parent.mkdir(parents=True, exist_ok=True)
        self.s3.download_file(bucket, object_key, str(destination))
        return destination

    def upload_file(self, source: Path, bucket: str, object_key: str) -> str:
        self.s3.upload_file(str(source), bucket, object_key)
        return self.uri_for(bucket, object_key)

    def uri_for(self, bucket: str, object_key: str) -> str:
        return f"s3://{bucket}/{object_key}"
