terraform {
  required_version = ">= 1.5.7"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region                      = var.aws_region
  access_key                  = "ministack"
  secret_key                  = "ministack"
  s3_use_path_style           = true
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_region_validation      = true
  skip_requesting_account_id  = true

  endpoints {
    ecs    = var.local_aws_endpoint_url
    events = var.local_aws_endpoint_url
    iam    = var.local_aws_endpoint_url
    logs   = var.local_aws_endpoint_url
    s3     = var.local_aws_endpoint_url
    sts    = var.local_aws_endpoint_url
  }
}

module "faturama_runtime" {
  source = "../../modules/faturama_runtime"

  aws_region                       = var.aws_region
  environment_name                 = var.environment_name
  input_bucket_name                = var.input_bucket_name
  artifact_bucket_name             = var.artifact_bucket_name
  artifact_prefix                  = var.artifact_prefix
  signed_upload_expiration_seconds = var.signed_upload_expiration_seconds
  dispatch_rule_name               = var.dispatch_rule_name
  ecs_cluster_name                 = var.ecs_cluster_name
  ecs_task_family                  = var.ecs_task_family
  container_image_uri              = var.container_image_uri
  db_name                          = var.db_name
  db_username                      = var.db_username
  db_password_secret_ref           = var.db_password_secret_ref
  db_password                      = var.db_password
  db_host                          = var.db_host
  db_port                          = var.db_port
  use_local_aws_endpoints          = true
  local_aws_endpoint_url           = var.local_aws_endpoint_url
  local_container_aws_endpoint_url = var.local_container_aws_endpoint_url
  subnet_ids                       = []
  security_group_ids               = []
  log_group_name                   = var.log_group_name
}
