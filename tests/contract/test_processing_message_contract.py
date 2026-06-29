from __future__ import annotations

import json
from pathlib import Path

from faturama.application.dto.processing_command_dto import ProcessingCommandDTO


def test_processing_message_contract_fixture_is_valid():
    fixture = Path("tests/contract/fixtures/processing_message.json")
    payload = json.loads(fixture.read_text(encoding="utf-8"))
    command = ProcessingCommandDTO.model_validate(payload)
    assert command.source == "aws.s3.eventbridge"
    assert command.bucket == "pre-processamento-faturama"
    assert command.upload_grant_id == "grant-20260628-001"
    assert command.metadata["source_event_id"] == "20260628-0001"
