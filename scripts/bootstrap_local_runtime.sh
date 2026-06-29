#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
TF_DIR="$ROOT_DIR/infra/terraform/environments/local"

cd "$ROOT_DIR"

export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-faturama}"
export MINISTACK_PORT="${MINISTACK_PORT:-4566}"
export TF_VAR_local_aws_endpoint_url="http://localhost:${MINISTACK_PORT}"
export TF_VAR_local_container_aws_endpoint_url="${TF_VAR_local_container_aws_endpoint_url:-http://ministack:4566}"

echo "[0/5] Limpando estado legado do runtime local"
docker compose rm -sf ministack >/dev/null 2>&1 || true
rm -rf "$TF_DIR/.terraform"
rm -f "$TF_DIR/.terraform.lock.hcl" "$TF_DIR/terraform.tfstate" "$TF_DIR/terraform.tfstate.backup"

echo "[1/5] Subindo dependencias locais (postgres + ministack)"
docker compose up -d postgres ministack

echo "[2/5] Construindo imagem local do worker (faturama-worker:local)"
docker compose build worker

echo "[3/5] Inicializando Terraform local"
terraform -chdir="$TF_DIR" init -backend=false

echo "[4/5] Validando Terraform local"
terraform -chdir="$TF_DIR" validate

echo "[5/5] Aplicando infraestrutura local"
terraform -chdir="$TF_DIR" import module.faturama_runtime.aws_s3_bucket.input pre-processamento-faturama >/dev/null 2>&1 || true
terraform -chdir="$TF_DIR" import module.faturama_runtime.aws_s3_bucket.artifact processados-faturama >/dev/null 2>&1 || true
terraform -chdir="$TF_DIR" apply -auto-approve

MINISTACK_VERSION="$(docker inspect --format '{{ index .Config.Env }}' "${COMPOSE_PROJECT_NAME}-ministack-1" 2>/dev/null | tr ' ' '\n' | sed -n 's/^MINISTACK_VERSION=//p' | head -n1)"

echo
echo "Ambiente local pronto."
echo "Imagem ECS local: faturama-worker:local"
echo "Compose status: docker compose ps"
echo "MiniStack endpoint: ${TF_VAR_local_aws_endpoint_url}"
echo "Terraform outputs: terraform -chdir=infra/terraform/environments/local output"
if [[ -n "${MINISTACK_VERSION}" ]]; then
  echo "MiniStack version: ${MINISTACK_VERSION}"
fi
echo "Observacao: o Terraform provisiona o alvo S3 -> EventBridge -> ECS, mas o MiniStack atual pode nao executar target ECS do EventBridge."
echo "Validacao real: uv run scripts/test_worker_from_ministack_s3.py"
