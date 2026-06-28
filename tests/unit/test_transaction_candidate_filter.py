from __future__ import annotations

from faturama.domain.services.transaction_candidate_extractor import extract_candidates


def test_extract_candidates_ignores_header_lines():
    markdown = "Valor total R$ 100,00\n14/04/2026 LOJA TESTE R$ 20,00\nLimite R$ 500,00"
    candidates = extract_candidates(markdown)
    assert len(candidates) == 1
    assert candidates[0]["description_text"] == "LOJA TESTE"
