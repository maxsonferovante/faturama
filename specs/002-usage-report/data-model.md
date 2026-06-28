# Data Model: Relatório de Uso

## Overview

O modelo da feature separa quatro conceitos principais:

1. alvo analisado;
2. evidência observada;
3. conclusão de uso ou desvio;
4. ação corretiva opcional.

## Entities

### 1. Analysis Target

**Purpose**: Representa um componente ou sinal estrutural que faz parte do escopo da análise.

**Fields**:

- `target_id`
- `target_name`
- `target_kind`
- `scope_group`
- `expected_behavior`
- `analysis_status`

**Validation Rules**:

- `target_name` deve ser único dentro de uma execução.
- `target_kind` deve distinguir biblioteca, adapter, workflow ou sinal estrutural.
- `analysis_status` deve suportar pelo menos `pending`, `analyzed`, `corrected`, `deferred`.

### 2. Evidence Record

**Purpose**: Representa a evidência concreta usada para classificar um alvo.

**Fields**:

- `evidence_id`
- `target_id`
- `evidence_kind`
- `source_path`
- `source_excerpt`
- `source_line_reference`
- `confidence_level`
- `observed_at`

**Validation Rules**:

- cada evidência deve apontar para um alvo analisado;
- `evidence_kind` deve distinguir execução observável, uso executável, teste reforçador, naming apenas ou dependência declarada;
- `source_path` não pode ser vazio.

### 3. Usage Finding

**Purpose**: Representa a conclusão principal sobre o status real de uso de um alvo.

**Fields**:

- `finding_id`
- `target_id`
- `usage_classification`
- `summary`
- `primary_evidence_id`
- `supporting_evidence_ids`
- `decision_reason`
- `finding_severity`

**Validation Rules**:

- `usage_classification` deve suportar ao menos `used_in_runtime`, `declared_not_used`, `conceptual_only`, `insufficient_context`;
- toda conclusão deve possuir ao menos uma evidência primária;
- `finding_severity` deve refletir o impacto do desvio encontrado.

### 4. Specification Deviation

**Purpose**: Representa uma diferença relevante entre o comportamento esperado e o comportamento observado.

**Fields**:

- `deviation_id`
- `target_id`
- `expected_statement`
- `observed_statement`
- `deviation_type`
- `criticality`
- `is_fixable_automatically`

**Validation Rules**:

- `expected_statement` e `observed_statement` devem ser explicitamente comparáveis;
- `criticality` deve suportar pelo menos `low`, `medium`, `high`;
- `is_fixable_automatically` só pode ser verdadeiro quando houver contexto suficiente para correção segura.

### 5. Remediation Action

**Purpose**: Representa a ação tomada ou sugerida após detectar um desvio.

**Fields**:

- `action_id`
- `deviation_id`
- `action_type`
- `action_status`
- `action_summary`
- `change_targets`
- `requires_manual_followup`

**Validation Rules**:

- `action_type` deve distinguir correção automática de recomendação manual;
- `action_status` deve suportar `planned`, `applied`, `skipped`, `manual_required`;
- `requires_manual_followup` deve ser verdadeiro quando a correção automática não for segura.

## Relationships

- Um `Analysis Target` pode possuir várias `Evidence Record`.
- Um `Usage Finding` pertence a um `Analysis Target` e referencia uma ou mais evidências.
- Um `Specification Deviation` pertence a um `Analysis Target` e pode derivar de uma `Usage Finding`.
- Uma `Remediation Action` pertence a um `Specification Deviation`.

## State Transitions

### Analysis Target

- `pending` → `analyzed`
- `analyzed` → `corrected`
- `analyzed` → `deferred`

### Remediation Action

- `planned` → `applied`
- `planned` → `skipped`
- `planned` → `manual_required`
