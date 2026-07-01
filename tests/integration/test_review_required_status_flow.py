from __future__ import annotations

from faturama.application.services.processing_status_service import ProcessingStatusService
from faturama.domain.value_objects.processing_status import ProcessingStatus
from faturama.infrastructure.database.postgres import connect
from faturama.infrastructure.repositories.processing_job_repository import ProcessingJobRepository
from faturama.infrastructure.repositories.processing_status_repository import ProcessingStatusRepository


def test_review_required_remains_non_terminal(temp_db):
    connection = connect(temp_db)
    try:
        jobs = ProcessingJobRepository(connection)
        statuses = ProcessingStatusRepository(connection)
        jobs.create_job(
            {
                "processing_id": "evt-1",
                "source_event_id": "src-1",
                "execution_arn": None,
                "dispatch_attempt": 1,
                "current_status": "PENDING",
                "status_detail": None,
                "bucket_name": "pre-processamento-faturama",
                "object_key": "incoming/invoice.pdf",
                "requested_at": "2026-06-28T12:00:00Z",
                "runtime_environment": "test",
            }
        )
        service = ProcessingStatusService(job_repository=jobs, status_repository=statuses)
        service.transition("evt-1", ProcessingStatus.REVIEW_REQUIRED, status_detail="manual review required")
        status = statuses.get_status("evt-1")
        assert status is not None
        assert status["current_status"] == "REVIEW_REQUIRED"
        assert status["is_terminal"] is False
        assert status["review_required"] is True
    finally:
        connection.close()

