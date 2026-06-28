from __future__ import annotations

from faturama.domain.services.transaction_parser import normalize_description


def test_normalize_description_strips_noise():
    assert normalize_description("MERCADOLIVRE*MERCADOL (Parcela 02 de 10)") == "MERCADOLIVRE MERCADOL PARCELA 02 DE 10"
