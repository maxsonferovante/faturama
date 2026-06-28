from __future__ import annotations

from pathlib import Path


def test_local_runtime_contract_files_exist():
    assert Path("docker-compose.yml").exists()
    assert Path("docker/worker/Dockerfile").exists()
    assert Path("infra/terraform/environments/local/main.tf").exists()
