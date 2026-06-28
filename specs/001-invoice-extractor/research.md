# Research: Extrator de Faturas Estruturadas

## Decision 1: SQLite será a base canônica da v1

**Rationale**: O escopo inicial é um histórico individual por usuário, com necessidade forte de idempotência, auditoria e consultas analíticas locais. SQLite atende esses requisitos com baixo custo operacional, sem introduzir infraestrutura desnecessária logo na primeira entrega.

**Alternatives considered**:

- **DuckDB**: forte para análise, mas menos natural como base transacional canônica com upserts frequentes, fila de revisão e atualização incremental de entidades.
- **Postgres**: opção robusta para evolução futura, porém adiciona overhead operacional desnecessário para a v1.
- **Parquet-only**: bom para exportação analítica, mas ruim para revisão operacional, reprocessamento idempotente e consultas incrementais de uso diário.

## Decision 2: A interface v1 será um CLI orientado a processamento e consulta

**Rationale**: O repositório atual ainda é mínimo e não há contrato prévio de API ou interface web. Um CLI permite validar o pipeline fim a fim, processar lotes de PDFs, consultar read models e manter o foco na semântica financeira antes de abrir uma superfície HTTP.

**Alternatives considered**:

- **FastAPI**: útil em fase posterior, mas exigiria definir autenticação, contrato HTTP e preocupação com deploy cedo demais.
- **Notebook-first**: bom para exploração, porém fraco como contrato operacional estável.
- **Interface web**: adiciona escopo de UX sem aumentar a confiança na extração.

## Decision 3: A extração seguirá precedência estrutural > regra > heurística > LLM > revisão humana

**Rationale**: Os refinamentos deixam claro que a LLM não deve ser fonte primária da verdade canônica. A política reduz custo, melhora auditabilidade e protege consultas futuras de interpretações opacas.

**Alternatives considered**:

- **LLM-first para cada linha**: custo mais alto, menor reprodutibilidade e pior explicabilidade.
- **Regra sem fallback**: cobertura insuficiente para linhas truncadas, OCR híbrido e layouts inconsistentes.

## Decision 4: O modelo canônico será estável e independente do emissor

**Rationale**: Os emissores mudam layout, mas as consultas centrais do produto não podem depender disso. A variabilidade deve ficar confinada à etapa de parsing e detecção de layout.

**Alternatives considered**:

- **Schema por emissor**: aumenta acoplamento e dificulta comparações históricas.
- **Armazenar apenas JSON bruto do extrator**: não resolve as consultas de negócio nem a revisão operacional.

## Decision 5: O matching de parcelamentos será conservador, explicável e começará por uma chave canônica simples

**Rationale**: Um falso agrupamento de parcelas é pior do que manter séries separadas temporariamente. O plano seguirá fronteira primária por cartão, progressão temporal coerente, total de parcelas e valor como sinais centrais. A identidade inicial do plano parcelado será formada por descrição normalizada, valor da parcela, cartão e data de origem aproximada, com revisão manual quando houver conflito material.

**Alternatives considered**:

- **Agrupamento agressivo por similaridade textual**: aumenta falsos positivos em compras recorrentes e lojistas com descrições parecidas.
- **Sem agrupamento histórico**: inviabiliza saldo restante e projeções úteis.

## Decision 6: Observado e projetado permanecerão como entidades separadas

**Rationale**: Consultas sobre passado/presente precisam refletir cobranças reais; consultas futuras dependem de projeções derivadas. Misturar os dois compromete a semântica de respostas como “quanto gastei” versus “quanto já está comprometido”.

**Alternatives considered**:

- **Tabela única com flag temporal**: mais simples fisicamente, mas mais ambígua para regras de consulta e auditoria.

## Decision 7: A política de confiança será persistida como dado operacional

**Rationale**: A base precisa explicar por que aceitou, rejeitou ou reteve uma entidade para revisão. Persistir decisão operacional, evidência primária e fontes conflitantes transforma ambiguidade em estado tratável, não em exceção invisível. Na v1, qualquer item abaixo do limiar configurado deve obrigatoriamente abrir fila de revisão, mesmo quando o restante da fatura puder ser persistido parcialmente.

**Alternatives considered**:

- **Logs apenas**: insuficientes para consultas e revisão histórica.
- **Confiar apenas em schema válido**: não cobre ambiguidade semântica e relacional.

## Decision 8: As materializações mínimas da v1 serão `monthly_card_summaries` e snapshots de parcelamento

**Rationale**: As consultas mais importantes exigem agregados recorrentes por competência/cartão e visão resumida do saldo parcelado. Materializações mínimas reduzem recomputação sem abrir um sistema analítico complexo.

**Alternatives considered**:

- **Tudo on-the-fly**: aumenta custo e complexidade das consultas recorrentes.
- **Muitas views derivadas desde o início**: cria manutenção desnecessária antes de validar uso real.
