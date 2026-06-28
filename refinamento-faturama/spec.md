# Extrator de Faturas com OpenDataLoader, LangGraph e Pydantic

## Goal
- Construir um pipeline para transformar faturas de cartão em dados estruturados, consultáveis por mês, cartão, compra, parcela e saldo futuro.
- Permitir responder perguntas como: quais parcelas vencem neste mês, quais vencem no próximo, quanto gastei no mês por cartão, quanto de compras parceladas ainda resta, e quais compras novas foram feitas no período.
- Separar claramente extração determinística, enriquecimento por LLM e persistência, para reduzir custo, aumentar auditabilidade e facilitar correções.

## Non-goals
- Não construir um chatbot financeiro genérico nesta fase.
- Não depender da LLM para extrair todos os campos da fatura quando eles puderem ser obtidos por regras determinísticas.
- Não tratar inicialmente boletos, empréstimos, limite, cashback, pontos, seguros e mensagens promocionais como entidades financeiras principais.
- Não tentar normalizar perfeitamente descrições de lojistas entre bancos diferentes na primeira versão.

## Background / context

O repositório já usa `opendataloader-pdf[hybrid]` para converter PDFs em `markdown` e `json`. Os exemplos atuais mostram que o output contém:

- metadados úteis da fatura, como valor total, vencimento, emissão e informações do cartão;
- itens textuais com ordem de leitura preservada;
- elementos estruturados com tipo semântico e `bounding box` no JSON;
- descrições explícitas de compras parceladas, incluindo padrões como `Parcela 02 de 10`;
- seções de próxima fatura e saldo de compras parceladas em alguns emissores.

Isso sugere uma arquitetura em 4 camadas:

1. `OpenDataLoader PDF` para extração base do documento.
2. Regras determinísticas para mapear seções, datas, valores e parcelas.
3. LLM com saída estruturada via Pydantic apenas para campos ambíguos.
4. LangGraph para orquestrar o fluxo, checkpoints, retries, validação e revisão humana.

O uso de agente deve ser restrito. O melhor desenho aqui não é um agente “livre” lendo a fatura inteira, mas um workflow com nós especializados:

1. ingestão do PDF;
2. parse estrutural do `json` e `markdown`;
3. extração determinística de lançamentos;
4. fallback com LLM para linhas ambíguas;
5. reconciliação e deduplicação;
6. projeção de parcelas futuras;
7. persistência;
8. geração opcional de resumo analítico.

Entidades de dados recomendadas para os contratos Pydantic:

- `InvoiceInput`: caminho do PDF, emissor conhecido, timezone, moeda, id do usuário.
- `RawInvoiceDocument`: metadados do arquivo e paths para `markdown`/`json`.
- `InvoiceStatement`: cartão, emissor, competência, fechamento, vencimento, total, mínimo, limite, lançamentos.
- `TransactionLine`: data da compra, descrição original, valor, tipo, cartão, página, confiança, hash da linha.
- `InstallmentPlan`: chave canônica da compra parcelada, descrição normalizada, parcela atual, total de parcelas, valor da parcela, data de origem, cartão.
- `FutureInstallmentProjection`: mês de competência, cartão, chave da compra, número da parcela, valor previsto.
- `MonthlyCardSummary`: totais por cartão e competência.

Persistir apenas o resultado final estruturado não é suficiente. Também é necessário salvar evidências de origem:

- texto original da linha;
- página;
- coordenadas ou referência do bloco extraído;
- estratégia usada (`rule` ou `llm`);
- score de confiança.

## Users & primary flows
1. Usuário adiciona uma ou mais faturas PDF e recebe um conjunto estruturado de dados versionados por competência e cartão.
2. Usuário consulta “quais parcelas eu tenho neste mês e nos próximos meses” e o sistema responde com base em projeções derivadas dos planos parcelados identificados.
3. Usuário consulta “quanto gastei este mês por cartão” e o sistema usa os lançamentos classificados da competência.
4. Usuário revisa itens ambíguos marcados com baixa confiança e corrige descrições, tipo da transação ou vínculo de parcelamento.
5. Usuário reprocessa a mesma fatura sem duplicar lançamentos ou projeções já persistidas.

## Functional requirements
- O pipeline deve aceitar PDFs de diferentes emissores usando `opendataloader-pdf` como extrator primário.
- O pipeline deve ler preferencialmente o `json` estruturado e usar o `markdown` como apoio para detecção de seções e recuperação contextual.
- O pipeline deve extrair do cabeçalho, quando disponíveis: emissor, cartão, competência, data de emissão, data de fechamento, vencimento, total da fatura, pagamento mínimo e limite.
- O pipeline deve identificar linhas que representam transações reais e separar conteúdos informativos, promocionais ou financeiros auxiliares.
- O pipeline deve detectar compras parceladas usando regras sobre descrição, seção e padrões como `Parcela X de Y`.
- O pipeline deve agrupar diferentes ocorrências da mesma compra parcelada em um plano único com projeções futuras.
- O pipeline deve distinguir:
- compras novas do mês;
- parcelas cobradas no mês;
- ajustes, estornos e pagamentos;
- parcelamento de fatura, quando houver, como categoria separada de compra parcelada.
- O pipeline deve calcular agregados por competência e cartão:
- total de compras do mês;
- total de parcelas cobradas no mês;
- saldo parcelado futuro;
- projeção da próxima fatura;
- total por categoria de transação.
- O workflow deve usar LLM apenas em nós de desambiguação, por exemplo:
- classificar linhas que falharam nas regras;
- extrair estrutura de uma linha pouco padronizada;
- normalizar descrições de lojista para melhorar o agrupamento.
- Todo output da LLM deve ser validado por modelos Pydantic.
- O workflow deve registrar confiança por item e encaminhar para revisão humana itens abaixo de um limiar configurável.
- O workflow deve ser idempotente para reprocessamento do mesmo PDF.
- O workflow deve persistir dados em formato apto a consulta analítica. SQLite é suficiente para a primeira versão.
- O workflow deve manter rastreabilidade entre cada registro estruturado e a evidência original extraída do PDF.
- O LangGraph deve controlar estado, retries, checkpoints e branches de revisão, em vez de concentrar toda a lógica em uma única chamada de agente.

## Acceptance criteria
1. Dado um PDF já suportado pelo OpenDataLoader, o sistema gera um `InvoiceStatement` válido com metadados básicos da fatura.
2. Dada uma linha como `MERCADOLIVRE ... (Parcela 02 de 10) - R$ 422,89`, o sistema produz um `InstallmentPlan` válido e projeta as parcelas restantes para as competências futuras.
3. Dadas duas faturas consecutivas do mesmo cartão, o sistema identifica corretamente compras novas do mês e parcelas recorrentes já existentes.
4. Dado o reprocessamento do mesmo PDF, o sistema não duplica transações nem projeções persistidas.
5. Itens classificados por LLM são rejeitados quando violam o schema Pydantic e entram em retry ou revisão.
6. O usuário consegue consultar, a partir da base persistida, o total do mês por cartão, a lista de parcelas do mês e o saldo parcelado futuro.
7. Cada transação persistida mantém referência à origem, incluindo ao menos arquivo, página, texto bruto e estratégia de extração.
8. O workflow consegue pausar após detecção de baixa confiança e retomar do checkpoint sem reprocessar todo o documento.

## Edge cases
- Faturas sem seção explícita de “próximas parcelas”.
- Mesmo lojista com descrições variantes entre meses.
- Estorno parcial de compra parcelada.
- Parcelamento de fatura confundido com compra parcelada.
- Cartão adicional misturado ao cartão titular.
- Datas abreviadas em formatos diferentes entre bancos.
- Linhas quebradas em duas ou mais estruturas no PDF.
- PDFs digitalizados ou híbridos com OCR imperfeito.
- Competência da compra diferente da competência da cobrança.
- Múltiplas moedas ou valores internacionais.

## Open questions
- Qual banco de persistência você quer como primeira base canônica: SQLite simples, DuckDB, Postgres ou arquivos Parquet?
- Você quer modelar categorias de gasto já na v1 ou primeiro estabilizar apenas a estrutura financeira bruta?
- O identificador canônico de uma compra parcelada deve priorizar descrição normalizada + valor + cartão + data, ou você quer uma etapa explícita de matching histórico entre meses?
- As consultas finais serão servidas por CLI, notebook, API FastAPI ou interface web?
- Você quer revisar manualmente itens de baixa confiança em uma fila, ou prefere aceitar heurísticas agressivas na v1?
