from __future__ import annotations

import json
from pathlib import Path


APRIL_MARKDOWN = """Inter Cartao final 1234
Emissao 10/04/2026
Fechamento 15/04/2026
Vencimento 20/04/2026
Valor total R$ 672,89
Pagamento minimo R$ 100,00
Limite R$ 5.000,00

Compras
14/04/2026 MERCADOLIVRE (Parcela 02 de 10) R$ 422,89
15/04/2026 SUPERMERCADO CENTRAL R$ 200,00
ASSINATURA DIGITAL R$ 50,00
"""


def write_async_source(root: Path, bucket: str, object_key: str, markdown: str = APRIL_MARKDOWN) -> Path:
    target = root / bucket / object_key
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b"%PDF-1.4 fake invoice")
    target.with_suffix(".md").write_text(markdown, encoding="utf-8")
    target.with_suffix(".json").write_text(json.dumps({"page_count": 1}), encoding="utf-8")
    output_dir = target.parent / "output" / target.stem
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / f"{target.stem}.md").write_text(markdown, encoding="utf-8")
    (output_dir / f"{target.stem}.json").write_text(json.dumps({"page_count": 1}), encoding="utf-8")
    return target
