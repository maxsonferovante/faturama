from __future__ import annotations

from faturama.domain.services.header_extractor import extract_header


def test_extract_header_from_markdown():
    payload = extract_header(
        "Inter 1234\nEmissao 10/04/2026\nFechamento 15/04/2026\nVencimento 20/04/2026\nValor total R$ 123,45\nPagamento mínimo R$ 50,00\nLimite R$ 5.000,00"
    )
    assert payload["card_last4"] == "1234"
    assert payload["billing_year"] == 2026
    assert payload["billing_month"] == 4
    assert payload["statement_total_amount"] == "123,45"
