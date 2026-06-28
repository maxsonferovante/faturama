"""Document section segmentation."""

from __future__ import annotations


SECTION_HINTS = {
    "transactions": ("lancamentos", "compras", "despesas"),
    "future": ("proxima fatura", "próxima fatura", "parcelas futuras"),
    "payments": ("pagamentos", "estorno", "ajuste", "encargos"),
}


def segment(markdown: str) -> dict[str, str]:
    lowered = markdown.lower()
    sections: dict[str, str] = {"full": markdown}
    for name, hints in SECTION_HINTS.items():
        if any(hint in lowered for hint in hints):
            sections[name] = markdown
    return sections
