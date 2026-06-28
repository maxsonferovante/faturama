# Relatório de Uso

## Resumo Executivo

- Report ID: `09795d76-652e-492e-9723-75d13d169f95`
- Targets analyzed: `4`
- Findings: `4`
- Critical deviations: `0`
- Auto fixes applied: `0`
- Manual followups: `0`

## Alvos Analisados

### LangGraph

- Classification: `used_in_runtime`
- Severity: `low`
- Summary: LangGraph possui evidência concreta de uso no runtime atual.
- Decision reason: Há evidência executável ou sinal direto de runtime.
- Primary evidence: `src/faturama/infrastructure/database/langgraph_checkpoint.py:103`

### OpenDataLoader

- Classification: `used_in_runtime`
- Severity: `low`
- Summary: OpenDataLoader possui evidência concreta de uso no runtime atual.
- Decision reason: Há evidência executável ou sinal direto de runtime.
- Primary evidence: `src/faturama/infrastructure/opendataloader/extractor.py:71`

### Workflow Checkpoints

- Classification: `used_in_runtime`
- Severity: `low`
- Summary: Workflow Checkpoints possui evidência concreta de uso no runtime atual.
- Decision reason: Há evidência executável ou sinal direto de runtime.
- Primary evidence: `tests/integration/test_langgraph_workflow.py:16`

### Markdown/JSON Sidecars

- Classification: `used_in_runtime`
- Severity: `low`
- Summary: Markdown/JSON Sidecars possui evidência concreta de uso no runtime atual.
- Decision reason: Há evidência executável ou sinal direto de runtime.
- Primary evidence: `src/faturama/infrastructure/repositories/statement_repository.py:24`

## Evidências

### LangGraph

- `src/faturama/infrastructure/database/langgraph_checkpoint.py:103` [executable_usage]
- `src/faturama/application/use_cases/process_invoice.py:22` [executable_usage]
- `src/faturama/application/use_cases/process_invoice.py:118` [executable_usage]
- `src/faturama/application/services/workflow_builder.py:7` [executable_usage]
- `src/faturama/application/services/workflow_builder.py:14` [executable_usage]
- `pyproject.toml:9` [declared_dependency]
- `pyproject.toml:10` [declared_dependency]
- `specs/001-invoice-extractor/tasks.md:41` [documentation_expectation]
- `specs/001-invoice-extractor/tasks.md:22` [documentation_expectation]
- `specs/001-invoice-extractor/plan.md:15` [documentation_expectation]
- `refinamento-faturama/workflow_refinement.md:5` [documentation_expectation]
- `refinamento-faturama/workflow_refinement.md:439` [documentation_expectation]
- `refinamento-faturama/workflow_refinement.md:18` [documentation_expectation]
- `refinamento-faturama/spec.md:94` [documentation_expectation]
- `refinamento-faturama/spec.md:29` [documentation_expectation]
- `refinamento-faturama/spec.md:1` [documentation_expectation]
- `README.md:10` [documentation_expectation]

### OpenDataLoader

- `src/faturama/infrastructure/opendataloader/extractor.py:71` [executable_usage]
- `src/faturama/infrastructure/opendataloader/extractor.py:36` [executable_usage]
- `src/faturama/infrastructure/opendataloader/extractor.py:34` [executable_usage]
- `src/faturama/infrastructure/llm/review_context_loader.py:18` [executable_usage]
- `pyproject.toml:12` [declared_dependency]
- `pyproject.toml:11` [declared_dependency]
- `specs/001-invoice-extractor/tasks.md:42` [documentation_expectation]
- `specs/001-invoice-extractor/tasks.md:40` [documentation_expectation]
- `specs/001-invoice-extractor/tasks.md:22` [documentation_expectation]
- `specs/001-invoice-extractor/plan.md:80` [documentation_expectation]
- `specs/001-invoice-extractor/plan.md:15` [documentation_expectation]
- `refinamento-faturama/workflow_refinement.md:92` [documentation_expectation]
- `refinamento-faturama/workflow_refinement.md:84` [documentation_expectation]
- `refinamento-faturama/workflow_refinement.md:546` [documentation_expectation]
- `refinamento-faturama/workflow_refinement.md:15` [documentation_expectation]
- `refinamento-faturama/spec.md:97` [documentation_expectation]
- `refinamento-faturama/spec.md:68` [documentation_expectation]
- `refinamento-faturama/spec.md:26` [documentation_expectation]
- `refinamento-faturama/spec.md:16` [documentation_expectation]
- `refinamento-faturama/spec.md:1` [documentation_expectation]
- `refinamento-faturama/pyproject.toml:8` [documentation_expectation]
- `refinamento-faturama/main.py:18` [documentation_expectation]
- `refinamento-faturama/main.py:1` [documentation_expectation]
- `refinamento-faturama/confidence_policy.md:20` [documentation_expectation]
- `README.md:44` [documentation_expectation]
- `README.md:32` [documentation_expectation]
- `README.md:30` [documentation_expectation]
- `README.md:12` [documentation_expectation]
- `README.md:11` [documentation_expectation]
- `src/faturama/infrastructure/opendataloader/extractor.py:8` [naming_only]
- `src/faturama/infrastructure/opendataloader/extractor.py:1` [naming_only]
- `refinamento-faturama/main.py:18` [naming_only]
- `refinamento-faturama/main.py:17` [naming_only]
- `refinamento-faturama/main.py:1` [naming_only]

### Workflow Checkpoints

- `tests/integration/test_langgraph_workflow.py:16` [execution_signal]
- `src/faturama/infrastructure/database/schema.py:182` [execution_signal]
- `src/faturama/infrastructure/database/langgraph_checkpoint.py:85` [execution_signal]
- `src/faturama/infrastructure/database/langgraph_checkpoint.py:69` [execution_signal]
- `src/faturama/infrastructure/database/langgraph_checkpoint.py:47` [execution_signal]
- `src/faturama/infrastructure/database/langgraph_checkpoint.py:20` [execution_signal]
- `src/faturama/infrastructure/database/langgraph_checkpoint.py:12` [execution_signal]
- `src/faturama/application/use_cases/process_invoice.py:94` [execution_signal]
- `src/faturama/application/use_cases/process_invoice.py:89` [execution_signal]
- `src/faturama/application/use_cases/process_invoice.py:88` [execution_signal]
- `src/faturama/application/use_cases/process_invoice.py:87` [execution_signal]
- `src/faturama/application/use_cases/process_invoice.py:8` [execution_signal]
- `src/faturama/application/use_cases/process_invoice.py:73` [execution_signal]
- `src/faturama/application/use_cases/process_invoice.py:71` [execution_signal]
- `src/faturama/application/use_cases/process_invoice.py:22` [execution_signal]
- `src/faturama/application/use_cases/process_invoice.py:115` [execution_signal]
- `src/faturama/application/use_cases/process_invoice.py:106` [execution_signal]
- `src/faturama/application/services/workflow_nodes.py:95` [execution_signal]
- `src/faturama/application/services/workflow_nodes.py:86` [execution_signal]
- `src/faturama/application/services/workflow_nodes.py:76` [execution_signal]
- `src/faturama/application/services/workflow_nodes.py:67` [execution_signal]
- `src/faturama/application/services/workflow_nodes.py:45` [execution_signal]
- `src/faturama/application/services/workflow_nodes.py:332` [execution_signal]
- `src/faturama/application/services/workflow_nodes.py:329` [execution_signal]
- `src/faturama/application/services/workflow_nodes.py:320` [execution_signal]
- `src/faturama/application/services/workflow_nodes.py:222` [execution_signal]
- `src/faturama/application/services/workflow_nodes.py:205` [execution_signal]
- `src/faturama/application/services/workflow_nodes.py:113` [execution_signal]
- `src/faturama/application/services/workflow_nodes.py:101` [execution_signal]
- `src/faturama/application/services/workflow_builder.py:12` [execution_signal]
- `specs/001-invoice-extractor/tasks.md:74` [documentation_expectation]
- `specs/001-invoice-extractor/tasks.md:44` [documentation_expectation]
- `specs/001-invoice-extractor/tasks.md:41` [documentation_expectation]
- `specs/001-invoice-extractor/tasks.md:130` [documentation_expectation]
- `specs/001-invoice-extractor/tasks.md:125` [documentation_expectation]
- `specs/001-invoice-extractor/tasks.md:102` [documentation_expectation]
- `specs/001-invoice-extractor/plan.md:15` [documentation_expectation]
- `refinamento-faturama/workflow_refinement.md:439` [documentation_expectation]
- `refinamento-faturama/workflow_refinement.md:18` [documentation_expectation]
- `refinamento-faturama/spec.md:94` [documentation_expectation]
- `refinamento-faturama/spec.md:29` [documentation_expectation]
- `refinamento-faturama/spec.md:104` [documentation_expectation]
- `README.md:28` [documentation_expectation]
- `README.md:10` [documentation_expectation]

### Markdown/JSON Sidecars

- `src/faturama/infrastructure/repositories/statement_repository.py:24` [execution_signal]
- `src/faturama/infrastructure/repositories/statement_repository.py:21` [execution_signal]
- `src/faturama/infrastructure/opendataloader/extractor.py:30` [execution_signal]
- `src/faturama/infrastructure/opendataloader/extractor.py:11` [execution_signal]
- `src/faturama/infrastructure/files/artifacts.py:29` [execution_signal]
- `src/faturama/infrastructure/files/artifacts.py:11` [execution_signal]
- `src/faturama/infrastructure/database/schema.py:16` [execution_signal]
- `src/faturama/infrastructure/database/schema.py:15` [execution_signal]
- `src/faturama/domain/entities/raw_document.py:15` [execution_signal]
- `src/faturama/domain/entities/raw_document.py:14` [execution_signal]
- `src/faturama/application/services/workflow_nodes.py:54` [execution_signal]
- `src/faturama/application/services/workflow_nodes.py:245` [execution_signal]
- `src/faturama/application/services/workflow_nodes.py:244` [execution_signal]
- `src/faturama/application/services/workflow_nodes.py:20` [execution_signal]
- `src/faturama/application/dto/document_dto.py:14` [execution_signal]
- `src/faturama/application/dto/document_dto.py:13` [execution_signal]
- `specs/001-invoice-extractor/data-model.md:36` [documentation_expectation]
- `specs/001-invoice-extractor/data-model.md:28` [documentation_expectation]
- `specs/001-invoice-extractor/data-model.md:27` [documentation_expectation]
- `refinamento-faturama/workflow_refinement.md:43` [documentation_expectation]
- `refinamento-faturama/workflow_refinement.md:42` [documentation_expectation]
- `refinamento-faturama/data_model_refinement.md:437` [documentation_expectation]
- `refinamento-faturama/data_model_refinement.md:436` [documentation_expectation]
- `refinamento-faturama/data_model_refinement.md:152` [documentation_expectation]
- `refinamento-faturama/data_model_refinement.md:151` [documentation_expectation]
- `specs/003-align-runtime-architecture/tasks.md:59` [documentation_expectation]
- `specs/003-align-runtime-architecture/tasks.md:47` [documentation_expectation]
- `specs/003-align-runtime-architecture/tasks.md:110` [documentation_expectation]
- `specs/003-align-runtime-architecture/spec.md:82` [documentation_expectation]
- `specs/003-align-runtime-architecture/spec.md:15` [documentation_expectation]
- `specs/003-align-runtime-architecture/spec.md:129` [documentation_expectation]

## Desvios

Nenhum desvio material identificado.

## Ações Corretivas ou Pendências Manuais

Nenhuma ação corretiva necessária.
