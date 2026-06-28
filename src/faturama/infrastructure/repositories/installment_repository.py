"""Installment repository implementation."""

from __future__ import annotations

from dataclasses import asdict
from sqlite3 import Connection

from faturama.domain.entities.future_installment_projection import FutureInstallmentProjection
from faturama.domain.entities.installment_plan import InstallmentPlan


class InstallmentRepository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def save_plan(self, plan: InstallmentPlan) -> None:
        payload = asdict(plan)
        payload.setdefault("runtime_source", "official")
        payload.setdefault("legacy_status", "active")
        self.connection.execute(
            """
            INSERT OR REPLACE INTO installment_plans (
                installment_plan_id, user_id, card_fingerprint, installment_type, description_anchor,
                description_normalized, merchant_normalized, origin_purchase_date, installment_amount,
                installment_total, first_seen_statement_id, last_seen_statement_id, plan_status,
                plan_confidence, matching_strategy, canonical_key, runtime_source, legacy_status
            ) VALUES (
                :installment_plan_id, :user_id, :card_fingerprint, :installment_type, :description_anchor,
                :description_normalized, :merchant_normalized, :origin_purchase_date, :installment_amount,
                :installment_total, :first_seen_statement_id, :last_seen_statement_id, :plan_status,
                :plan_confidence, :matching_strategy, :canonical_key, :runtime_source, :legacy_status
            )
            """,
            payload,
        )
        self.connection.commit()

    def list_plans(self, user_id: str) -> list[InstallmentPlan]:
        rows = self.connection.execute(
            "SELECT * FROM installment_plans WHERE user_id = ? AND legacy_status != 'invalidated'",
            (user_id,),
        ).fetchall()
        return [InstallmentPlan(**dict(row)) for row in rows]

    def save_projections(self, plan_id: str, projections: list[FutureInstallmentProjection]) -> None:
        self.connection.execute("DELETE FROM projections WHERE installment_plan_id = ?", (plan_id,))
        for projection in projections:
            self.connection.execute(
                """
                INSERT OR REPLACE INTO projections (
                    projection_id, installment_plan_id, card_fingerprint, projected_billing_year,
                    projected_billing_month, projected_installment_number, projected_amount,
                    projection_status, projection_confidence
                ) VALUES (
                    :projection_id, :installment_plan_id, :card_fingerprint, :projected_billing_year,
                    :projected_billing_month, :projected_installment_number, :projected_amount,
                    :projection_status, :projection_confidence
                )
                """,
                asdict(projection),
            )
        self.connection.commit()

    def list_projections(self, year: int, month: int, user_id: str | None = None) -> list[dict]:
        query = """
            SELECT p.*, ip.user_id, ip.description_anchor, ip.installment_total, ip.plan_status, ip.plan_confidence
            FROM projections p
            JOIN installment_plans ip ON ip.installment_plan_id = p.installment_plan_id
            WHERE p.projected_billing_year = ? AND p.projected_billing_month = ?
              AND ip.legacy_status != 'invalidated'
        """
        params: list[object] = [year, month]
        if user_id:
            query += " AND ip.user_id = ?"
            params.append(user_id)
        rows = self.connection.execute(query, tuple(params)).fetchall()
        return [dict(row) for row in rows]
