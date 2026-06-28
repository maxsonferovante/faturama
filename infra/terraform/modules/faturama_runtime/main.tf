terraform {
  required_version = ">= 1.5.7"
}

locals {
  common_tags = {
    project     = "faturama"
    environment = var.environment_name
  }
}

resource "terraform_data" "runtime_contract" {
  input = {
    input_bucket     = var.input_bucket_name
    artifact_bucket  = var.artifact_bucket_name
    queue_name       = var.processing_queue_name
    state_machine    = var.state_machine_name
    ecs_cluster_name = var.ecs_cluster_name
  }
}
