terraform {
  required_version = ">= 1.5.7"
}

module "faturama_runtime" {
  source = "../../modules/faturama_runtime"

  aws_region                        = var.aws_region
  environment_name                  = var.environment_name
  input_bucket_name                 = var.input_bucket_name
  artifact_bucket_name              = var.artifact_bucket_name
  artifact_prefix                   = var.artifact_prefix
  signed_upload_expiration_seconds  = var.signed_upload_expiration_seconds
  processing_queue_name             = var.processing_queue_name
  processing_dlq_name               = var.processing_dlq_name
  pipe_name                         = var.pipe_name
  state_machine_name                = var.state_machine_name
  ecs_cluster_name                  = var.ecs_cluster_name
  ecs_task_family                   = var.ecs_task_family
  container_image_uri               = var.container_image_uri
  db_name                           = var.db_name
  db_username                       = var.db_username
  db_password_secret_ref            = var.db_password_secret_ref
  db_host                           = var.db_host
  db_port                           = var.db_port
  status_polling_visibility_seconds = var.status_polling_visibility_seconds
  use_local_aws_endpoints           = true
  local_aws_endpoint_url            = var.local_aws_endpoint_url
  subnet_ids                        = []
  security_group_ids                = []
  log_group_name                    = var.log_group_name
}
