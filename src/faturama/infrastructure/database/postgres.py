"""PostgreSQL connection and unit-of-work helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

import psycopg
from psycopg.rows import dict_row

from faturama.application.ports.unit_of_work import UnitOfWorkFactory
from faturama.infrastructure.checkpoint.postgres_checkpoint_store import PostgresCheckpointStore
from faturama.infrastructure.database.schema import initialize_schema
from faturama.infrastructure.repositories.artifact_manifest_repository import ArtifactManifestRepository
from faturama.infrastructure.repositories.decision_repository import DecisionRepository
from faturama.infrastructure.repositories.evidence_repository import EvidenceRepository
from faturama.infrastructure.repositories.installment_repository import InstallmentRepository
from faturama.infrastructure.repositories.processing_job_repository import ProcessingJobRepository
from faturama.infrastructure.repositories.processing_status_repository import ProcessingStatusRepository
from faturama.infrastructure.repositories.review_repository import ReviewRepository
from faturama.infrastructure.repositories.statement_repository import StatementRepository
from faturama.infrastructure.repositories.summary_repository import SummaryRepository
from faturama.infrastructure.repositories.transaction_repository import TransactionRepository


class DatabaseConfigurationError(ValueError):
    """Raised when FATURAMA database configuration is invalid."""


def validate_postgres_dsn(dsn: str) -> str:
    if not dsn:
        raise DatabaseConfigurationError("FATURAMA_DB_DSN is required")
    parsed = urlparse(dsn)
    if parsed.scheme not in {"postgresql", "postgres"}:
        raise DatabaseConfigurationError(
            "FATURAMA_DB_DSN must use the postgresql:// or postgres:// scheme"
        )
    if dsn.endswith(".sqlite3") or dsn.endswith(".db"):
        raise DatabaseConfigurationError("FATURAMA_DB_DSN must point to PostgreSQL, not a local database file")
    return dsn


def connect(dsn: str) -> psycopg.Connection[Any]:
    connection = psycopg.connect(validate_postgres_dsn(dsn), row_factory=dict_row)
    initialize_schema(connection)
    return connection


def connect_from_dsn(dsn: str) -> psycopg.Connection[Any]:
    return connect(dsn)


@dataclass(slots=True)
class PostgresUnitOfWork:
    connection: psycopg.Connection[Any]

    def __post_init__(self) -> None:
        self.statement_repository = StatementRepository(self.connection)
        self.evidence_repository = EvidenceRepository(self.connection)
        self.transaction_repository = TransactionRepository(self.connection)
        self.installment_repository = InstallmentRepository(self.connection)
        self.summary_repository = SummaryRepository(self.connection)
        self.review_repository = ReviewRepository(self.connection)
        self.decision_repository = DecisionRepository(self.connection)
        self.processing_job_repository = ProcessingJobRepository(self.connection)
        self.processing_status_repository = ProcessingStatusRepository(self.connection)
        self.artifact_manifest_repository = ArtifactManifestRepository(self.connection)
        self.checkpoint_store = PostgresCheckpointStore(self.connection)

    def commit(self) -> None:
        self.connection.commit()

    def rollback(self) -> None:
        self.connection.rollback()

    def close(self) -> None:
        self.connection.close()


class PostgresUnitOfWorkFactory(UnitOfWorkFactory):
    def __init__(self, dsn: str) -> None:
        self.dsn = validate_postgres_dsn(dsn)

    def open(self) -> PostgresUnitOfWork:
        return PostgresUnitOfWork(connect(self.dsn))
