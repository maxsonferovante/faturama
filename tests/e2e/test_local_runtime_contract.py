from __future__ import annotations

from pathlib import Path


def test_local_runtime_contract_files_exist():
    assert Path("docker-compose.yml").exists()
    assert Path("docker/worker/Dockerfile").exists()
    assert Path("infra/terraform/environments/local/main.tf").exists()


def test_local_runtime_contract_targets_direct_eventbridge_dispatch():
    main_tf = Path("infra/terraform/modules/faturama_runtime/main.tf").read_text(encoding="utf-8")
    outputs_tf = Path("infra/terraform/environments/local/outputs.tf").read_text(encoding="utf-8")

    assert "ecs_target" in main_tf
    assert "eventbridge = true" in main_tf
    assert "aws_sfn_state_machine" not in main_tf
    assert "aws_sqs_queue" not in main_tf
    assert "state_machine_arn" not in outputs_tf
