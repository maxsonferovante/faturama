"""Service helpers around status transitions."""

from __future__ import annotations

from faturama.application.use_cases.update_processing_status import update_processing_status
from faturama.domain.value_objects.processing_status import ProcessingStatus


class ProcessingStatusService:
    def __init__(self, *, job_repository: object, status_repository: object) -> None:
        self.job_repository = job_repository
        self.status_repository = status_repository

    def transition(self, processing_id: str, status: ProcessingStatus, **kwargs: object) -> None:
        self.job_repository.update_job(
            processing_id,
            current_status=status.value,
            status_detail=kwargs.get("status_detail"),
            document_id=kwargs.get("document_id"),
            file_hash=kwargs.get("file_hash"),
            finished_at=kwargs.get("finished_at"),
            started_at=kwargs.get("started_at"),
            failure_code=kwargs.get("failure_code"),
            failure_message=kwargs.get("failure_message"),
        )
        update_processing_status(
            processing_id=processing_id,
            status=status,
            job_repository=self.job_repository,
            status_repository=self.status_repository,
            status_detail=kwargs.get("status_detail"),
            document_id=kwargs.get("document_id"),
            file_hash=kwargs.get("file_hash"),
            result_reference=kwargs.get("result_reference"),
            artifact_manifest_id=kwargs.get("artifact_manifest_id"),
        )
