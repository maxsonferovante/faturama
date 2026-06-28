"""Transaction candidate extraction."""

from __future__ import annotations

import re


LINE_RE = re.compile(
    r"(?P<date>\d{2}/\d{2}(?:/\d{4})?)?\s*(?P<desc>.+?)\s+(?P<amount>-?\s*R\$\s*[0-9\.\,]+)",
    re.IGNORECASE,
)
IGNORED_PREFIXES = (
    "valor total",
    "total da fatura",
    "pagamento minimo",
    "pagamento mínimo",
    "limite",
    "vencimento",
    "fechamento",
    "emissao",
    "emissão",
)


def extract_candidates(markdown: str) -> list[dict]:
    candidates: list[dict] = []
    for index, line in enumerate(markdown.splitlines(), start=1):
        clean = " ".join(line.split())
        if "R$" not in clean:
            continue
        if clean.lower().startswith(IGNORED_PREFIXES):
            continue
        match = LINE_RE.search(clean)
        if not match:
            continue
        candidates.append(
            {
                "candidate_id": f"cand-{index}",
                "raw_text": clean,
                "line_date_text": match.group("date"),
                "amount_text": match.group("amount"),
                "description_text": match.group("desc").strip(),
                "page_number": 1,
            }
        )
    return candidates
