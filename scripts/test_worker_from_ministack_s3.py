from __future__ import annotations

import json
from pathlib import Path
import subprocess
import time

import boto3

# Edite somente este bloco.
TEST_CONFIG = {
    "pdf_path": "/Users/USER_PROFILE/Documents/faturama/refinamento-faturama/faturajunhointer.pdf",
    "object_key": "incoming/faturajunhointer.pdf",
    "endpoint_url": "http://localhost:4566",
    "aws_region": "us-east-1",
    "input_bucket": "pre-processamento-faturama",
    "artifact_bucket": "processados-faturama",
    "artifact_prefix": "processed",
    "dispatch_rule_name": "faturama-processing-dispatch",
    "wait_timeout_seconds": 180,
    "poll_interval_seconds": 5,
    "worker_image": "faturama-worker:local",
    "ministack_container_name": "faturama-ministack-1",
    "show_docker_progress": True,
}


def ensure_buckets(s3, *buckets: str) -> None:
    for bucket in buckets:
        try:
            s3.create_bucket(Bucket=bucket)
        except Exception:
            pass


def list_relevant_artifacts(
    s3, *, bucket: str, artifact_prefix: str, object_stem: str
) -> list[str]:
    output_listing = s3.list_objects_v2(
        Bucket=bucket,
        Prefix=f"{artifact_prefix.rstrip('/')}/",
    )
    relevant = []
    marker = f"/{object_stem}-"
    for item in output_listing.get("Contents", []):
        key = item["Key"]
        if marker in key:
            relevant.append(key)
    return relevant


def log_progress(message: str) -> None:
    print(f"[test-worker] {message}", flush=True)


def list_worker_containers(worker_image: str) -> list[dict[str, str]]:
    result = subprocess.run(
        [
            "docker",
            "ps",
            "-a",
            "--filter",
            f"ancestor={worker_image}",
            "--format",
            "{{.ID}}\t{{.Names}}\t{{.Status}}",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return []

    containers: list[dict[str, str]] = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        container_id, name, status = (line.split("\t", 2) + ["", ""])[:3]
        containers.append({"id": container_id, "name": name, "status": status})
    return containers


def read_container_logs(container_id: str) -> str:
    result = subprocess.run(
        ["docker", "logs", "--tail", "20", container_id],
        capture_output=True,
        text=True,
        check=False,
    )
    output = (result.stdout or "") + (result.stderr or "")
    return output.strip()


def read_ministack_logs(container_name: str, *, tail: int = 200) -> str:
    result = subprocess.run(
        ["docker", "logs", "--tail", str(tail), container_name],
        capture_output=True,
        text=True,
        check=False,
    )
    output = (result.stdout or "") + (result.stderr or "")
    return output.strip()


def main() -> int:
    pdf_path = Path(TEST_CONFIG["pdf_path"]).expanduser().resolve()
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    object_key = TEST_CONFIG["object_key"]
    object_stem = pdf_path.stem
    seen_containers: dict[str, str] = {}
    last_artifact_count = 0

    s3 = boto3.client(
        "s3",
        endpoint_url=TEST_CONFIG["endpoint_url"],
        region_name=TEST_CONFIG["aws_region"],
    )
    ensure_buckets(s3, TEST_CONFIG["input_bucket"], TEST_CONFIG["artifact_bucket"])
    existing_artifacts = set(
        list_relevant_artifacts(
            s3,
            bucket=TEST_CONFIG["artifact_bucket"],
            artifact_prefix=TEST_CONFIG["artifact_prefix"],
            object_stem=object_stem,
        )
    )
    existing_container_ids = {
        container["id"]
        for container in list_worker_containers(TEST_CONFIG["worker_image"])
    }

    log_progress(
        f"enviando {pdf_path.name} para s3://{TEST_CONFIG['input_bucket']}/{object_key}"
    )
    s3.upload_file(str(pdf_path), TEST_CONFIG["input_bucket"], object_key)
    log_progress("aguardando processamento real via S3 -> EventBridge -> ECS")

    deadline = time.time() + int(TEST_CONFIG["wait_timeout_seconds"])
    artifact_keys: list[str] = []
    new_container_ids: list[str] = []
    while time.time() < deadline:
        current_containers = list_worker_containers(TEST_CONFIG["worker_image"])
        fresh_containers = [
            container
            for container in current_containers
            if container["id"] not in existing_container_ids
        ]
        current_new_container_ids = [container["id"] for container in fresh_containers]
        if current_new_container_ids != new_container_ids:
            new_container_ids = current_new_container_ids
            for container in fresh_containers:
                log_progress(
                    f"container novo {container['name']} ({container['id'][:12]}) -> {container['status']}"
                )

        if TEST_CONFIG["show_docker_progress"]:
            for container in current_containers:
                previous_status = seen_containers.get(container["id"])
                if previous_status != container["status"]:
                    seen_containers[container["id"]] = container["status"]
                    log_progress(
                        f"container {container['name']} ({container['id'][:12]}) -> {container['status']}"
                    )
                    container_logs = read_container_logs(container["id"])
                    if container_logs:
                        log_progress(
                            f"logs recentes de {container['name']}:\n{container_logs}"
                        )

        ministack_logs = read_ministack_logs(TEST_CONFIG["ministack_container_name"])
        unsupported_target_line = next(
            (
                line
                for line in ministack_logs.splitlines()
                if "EventBridge: unsupported target type for ARN" in line
            ),
            None,
        )
        if unsupported_target_line:
            raise SystemExit(
                json.dumps(
                    {
                        "status": "unsupported_runtime",
                        "message": (
                            "O MiniStack provisionou a regra EventBridge, mas a versao atual do emulador "
                            "nao executa target ECS. O upload chegou ao S3, porem o dispatch real "
                            "EventBridge -> ECS nao e suportado neste runtime local."
                        ),
                        "pdf_path": str(pdf_path),
                        "input_bucket": TEST_CONFIG["input_bucket"],
                        "artifact_bucket": TEST_CONFIG["artifact_bucket"],
                        "object_key": object_key,
                        "dispatch_rule_name": TEST_CONFIG["dispatch_rule_name"],
                        "new_container_ids": new_container_ids,
                        "artifact_prefix": TEST_CONFIG["artifact_prefix"],
                        "ministack_container_name": TEST_CONFIG[
                            "ministack_container_name"
                        ],
                        "ministack_log_evidence": unsupported_target_line,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )

        artifact_keys = sorted(
            set(
                list_relevant_artifacts(
                    s3,
                    bucket=TEST_CONFIG["artifact_bucket"],
                    artifact_prefix=TEST_CONFIG["artifact_prefix"],
                    object_stem=object_stem,
                )
            )
            - existing_artifacts
        )
        if len(artifact_keys) != last_artifact_count:
            last_artifact_count = len(artifact_keys)
            log_progress(f"artefatos encontrados: {last_artifact_count}")
            for key in artifact_keys:
                log_progress(f"artifact {key}")
        if artifact_keys:
            break
        time.sleep(int(TEST_CONFIG["poll_interval_seconds"]))

    if not artifact_keys:
        raise SystemExit(
            json.dumps(
                {
                    "status": "timeout",
                    "message": (
                        "O arquivo foi enviado para o bucket de entrada, mas nenhuma evidencia de processamento "
                        "real apareceu no bucket de artefatos dentro do tempo limite."
                    ),
                    "pdf_path": str(pdf_path),
                    "input_bucket": TEST_CONFIG["input_bucket"],
                    "artifact_bucket": TEST_CONFIG["artifact_bucket"],
                    "object_key": object_key,
                    "dispatch_rule_name": TEST_CONFIG["dispatch_rule_name"],
                    "new_container_ids": new_container_ids,
                    "artifact_prefix": TEST_CONFIG["artifact_prefix"],
                },
                ensure_ascii=False,
                indent=2,
            )
        )

    print(
        json.dumps(
            {
                "status": "ok",
                "message": (
                    "O script apenas enviou o PDF ao S3 do MiniStack e esperou pelo processamento assíncrono real."
                ),
                "pdf_path": str(pdf_path),
                "input_bucket": TEST_CONFIG["input_bucket"],
                "artifact_bucket": TEST_CONFIG["artifact_bucket"],
                "object_key": object_key,
                "dispatch_rule_name": TEST_CONFIG["dispatch_rule_name"],
                "new_container_ids": new_container_ids,
                "artifact_prefix": TEST_CONFIG["artifact_prefix"],
                "artifact_keys": artifact_keys,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
