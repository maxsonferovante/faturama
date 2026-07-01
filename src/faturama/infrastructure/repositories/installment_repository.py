"""Installment repository implementation."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from faturama.domain.entities.future_installment_projection import FutureInstallmentProjection
from faturama.domain.entities.installment_plan import InstallmentPlan


class InstallmentRepository:
    def __init__(self, connection: Any) -> None:
        self.connection = connection

    def save_plan(self, plan: InstallmentPlan) -> None:
        payload = asdict(plan)
        payload.setdefault("runtime_source", "official")
        payload.setdefault("legacy_status", "active")
        columns = list(payload.keys())
        values = tuple(payload[column] for column in columns)
        placeholders = ", ".join(["%s"] * len(columns))
        self.connection.execute(
            f"""
            INSERT INTO installment_plans ({', '.join(columns)})
            VALUES ({placeholders})
            ON CONFLICT (installment_plan_id) DO UPDATE SET
                user_id = EXCLUDED.user_id,
                card_fingerprint = EXCLUDED.card_fingerprint,
                installment_type = EXCLUDED.installment_type,
                description_anchor = EXCLUDED.description_anchor,
                description_normalized = EXCLUDED.description_normalized,
                merchant_normalized = EXCLUDED.merchant_normalized,
                origin_purchase_date = EXCLUDED.origin_purchase_date,
                installment_amount = EXCLUDED.installment_amount,
                installment_total = EXCLUDED.installment_total,
                first_seen_statement_id = EXCLUDED.first_seen_statement_id,
                last_seen_statement_id = EXCLUDED.last_seen_statement_id,
                plan_status = EXCLUDED.plan_status,
                plan_confidence = EXCLUDED.plan_confidence,
                matching_strategy = EXCLUDED.matching_strategy,
                canonical_key = EXCLUDED.canonical_key,
                runtime_source = EXCLUDED.runtime_source,
                legacy_status = EXCLUDED.legacy_status
            """,
            values,
        )

    def list_plans(self, user_id: str) -> list[InstallmentPlan]:
        rows = self.connection.execute(
            "SELECT * FROM installment_plans WHERE user_id = %s AND legacy_status != 'invalidated'",
            (user_id,),
        ).fetchall()
        return [InstallmentPlan(**dict(row)) for row in rows]

    def save_projections(self, plan_id: str, projections: list[FutureInstallmentProjection]) -> None:
        self.connection.execute("DELETE FROM projections WHERE installment_plan_id = %s", (plan_id,))
        for projection in projections:
            payload = asdict(projection)
            columns = list(payload.keys())
            values = tuple(payload[column] for column in columns)
            placeholders = ", ".join(["%s"] * len(columns))
            self.connection.execute(
                f"""
                INSERT INTO projections ({', '.join(columns)})
                VALUES ({placeholders})
                ON CONFLICT (projection_id) DO UPDATE SET
                    installment_plan_id = EXCLUDED.installment_plan_id,
                    card_fingerprint = EXCLUDED.card_fingerprint,
                    projected_billing_year = EXCLUDED.projected_billing_year,
                    projected_billing_month = EXCLUDED.projected_billing_month,
                    projected_installment_number = EXCLUDED.projected_installment_number,
                    projected_amount = EXCLUDED.projected_amount,
                    projection_status = EXCLUDED.projection_status,
                    projection_confidence = EXCLUDED.projection_confidence
                """,
                values,
            )

    def list_projections(self, year: int, month: int, user_id: str | None = None) -> list[dict]:
        query = """
            SELECT p.*, ip.user_id, ip.description_anchor, ip.installment_total, ip.plan_status, ip.plan_confidence
            FROM projections p
            JOIN installment_plans ip ON ip.installment_plan_id = p.installment_plan_id
            WHERE p.projected_billing_year = %s AND p.projected_billing_month = %s
              AND ip.legacy_status != 'invalidated'
        """
        params: list[object] = [year, month]
        if user_id:
            query += " AND ip.user_id = %s"
            params.append(user_id)
        rows = self.connection.execute(query, tuple(params)).fetchall()
        return [dict(row) for row in rows]
