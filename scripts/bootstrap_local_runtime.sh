#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
TF_DIR="$ROOT_DIR/infra/terraform/environments/local"

cd "$ROOT_DIR"

export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-faturama}"
export MINISTACK_PORT="${MINISTACK_PORT:-4566}"
export TF_VAR_local_aws_endpoint_url="http://localhost:${MINISTACK_PORT}"

echo "[1/4] Subindo dependencias locais (postgres + ministack)"
docker compose up -d postgres ministack

echo "[2/4] Construindo imagem local do worker (faturama-worker:local)"
docker compose build worker

echo "[3/4] Inicializando Terraform local"
terraform -chdir="$TF_DIR" init -backend=false

echo "[4/4] Aplicando infraestrutura local"
terraform -chdir="$TF_DIR" apply -auto-approve

echo
echo "Ambiente local pronto."
echo "Imagem ECS local: faturama-worker:local"
echo "Compose status: docker compose ps"
echo "MiniStack endpoint: ${TF_VAR_local_aws_endpoint_url}"
echo "Terraform outputs: terraform -chdir=infra/terraform/environments/local output"
