"""Execute the async processing contract against the existing pipeline."""

from __future__ import annotations

from pathlib import Path
import tempfile

from faturama.application.dto.processing_command_dto import ProcessingCommandDTO
from faturama.application.services.artifact_manifest_service import ArtifactManifestService
from faturama.application.services.processing_lifecycle import utc_now
from faturama.application.services.processing_status_service import ProcessingStatusService
from faturama.domain.value_objects.processing_status import ProcessingStatus
from faturama.infrastructure.aws.s3_storage import S3StorageAdapter
from faturama.infrastructure.config.settings import Settings
from faturama.infrastructure.database.postgres import connect_from_dsn
from faturama.infrastructure.database.sqlite import connect
from faturama.infrastructure.repositories.artifact_manifest_repository import ArtifactManifestRepository
from faturama.infrastructure.repositories.processing_job_repository import ProcessingJobRepository
from faturama.infrastructure.repositories.processing_status_repository import ProcessingStatusRepository
from faturama.infrastructure.repositories.statement_repository import StatementRepository
from faturama.application.use_cases.process_invoice import process_invoice


def _connection(settings: Settings):
    if settings.database_dsn:
        return connect_from_dsn(settings.database_dsn)
    return connect(settings.database_path)


def process_processing_command(
    command: ProcessingCommandDTO,
    *,
    settings: Settings,
    user_id: str = "async-system",
) -> dict[str, object]:
    connection = _connection(settings)
    job_repository = ProcessingJobRepository(connection)
    status_repository = ProcessingStatusRepository(connection)
    manifest_repository = ArtifactManifestRepository(connection)
    status_service = ProcessingStatusService(job_repository=job_repository, status_repository=status_repository)
    object_storage = S3StorageAdapter(endpoint_url=settings.aws_endpoint_url, region=settings.aws_region)

    job_repository.create_job(
        {
            "processing_id": command.processing_id,
            "source_event_id": command.metadata.get("source_event_id"),
            "execution_arn": command.metadata.get("execution_arn"),
            "dispatch_attempt": 1,
            "current_status": ProcessingStatus.PENDING.value,
            "status_detail": "accepted",
            "bucket_name": command.bucket,
            "object_key": command.object_key,
            "requested_at": utc_now(),
            "runtime_environment": settings.runtime_env,
        }
    )
    status_service.transition(command.processing_id, ProcessingStatus.PENDING, status_detail="accepted")
    status_service.transition(
        command.processing_id,
        ProcessingStatus.RUNNING,
        status_detail="downloading source",
        started_at=utc_now(),
    )

    try:
        with tempfile.TemporaryDirectory(prefix="faturama-async-") as tmp_dir:
            download_path = Path(tmp_dir) / Path(command.object_key).name
            object_storage.download_to_path(command.bucket, command.object_key, download_path)
            result = process_invoice(str(download_path), user_id=user_id, settings=settings)
            statement_repo = StatementRepository(connection)
            document = statement_repo.get_document_by_hash(result["file_hash"])

            manifest_service = ArtifactManifestService(
                storage=object_storage,
                repository=manifest_repository,
                artifact_bucket=settings.artifact_bucket,
                artifact_prefix=command.artifact_prefix or settings.artifact_prefix,
            )
            manifest = manifest_service.persist(
                processing_id=command.processing_id,
                document_id=result.get("document_id"),
                source_pdf_path=download_path,
                markdown_path=Path(result["artifacts"]["markdown_path"]) if result["artifacts"].get("markdown_path") else None,
                json_path=Path(result["artifacts"]["json_path"]) if result["artifacts"].get("json_path") else None,
                result_payload=result,
                source_object_key=command.object_key,
            )
    except Exception as exc:
        status_service.transition(
            command.processing_id,
            ProcessingStatus.FAILED,
            status_detail=str(exc),
            finished_at=utc_now(),
            failure_code=type(exc).__name__,
            failure_message=str(exc),
        )
        raise

    final_status = ProcessingStatus.REVIEW_REQUIRED if result["review_items_opened"] else ProcessingStatus.SUCCESS
    if result.get("partial_status") == "partial" and final_status != ProcessingStatus.REVIEW_REQUIRED:
        final_status = ProcessingStatus.PARTIAL
    status_service.transition(
        command.processing_id,
        final_status,
        status_detail=result["status"],
        document_id=result.get("document_id"),
        file_hash=result.get("file_hash"),
        result_reference=result.get("result_reference"),
        artifact_manifest_id=manifest["artifact_manifest_id"],
        finished_at=utc_now(),
    )
    job_repository.update_job(
        command.processing_id,
        document_id=result.get("document_id"),
        file_hash=result.get("file_hash"),
    )
    return {
        "processing_id": command.processing_id,
        "status": final_status.value,
        "result": result,
        "manifest": manifest,
        "document": document.document_id if document else result.get("document_id"),
    }
