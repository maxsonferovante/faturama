"""Unit of work ports for PostgreSQL-backed persistence."""

from __future__ import annotations

from typing import Protocol

from faturama.application.ports.artifact_manifest_repository import ArtifactManifestRepositoryPort
from faturama.application.ports.checkpoint_store import CheckpointStore
from faturama.application.ports.processing_job_repository import ProcessingJobRepositoryPort
from faturama.application.ports.processing_status_repository import ProcessingStatusRepositoryPort


class UnitOfWork(Protocol):
    statement_repository: object
    evidence_repository: object
    transaction_repository: object
    installment_repository: object
    summary_repository: object
    review_repository: object
    decision_repository: object
    processing_job_repository: ProcessingJobRepositoryPort
    processing_status_repository: ProcessingStatusRepositoryPort
    artifact_manifest_repository: ArtifactManifestRepositoryPort
    checkpoint_store: CheckpointStore

    def commit(self) -> None: ...

    def rollback(self) -> None: ...

    def close(self) -> None: ...


class UnitOfWorkFactory(Protocol):
    def open(self) -> UnitOfWork: ...
