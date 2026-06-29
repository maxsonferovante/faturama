variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "environment_name" {
  type    = string
  default = "local"
}

variable "input_bucket_name" {
  type    = string
  default = "pre-processamento-faturama"
}

variable "artifact_bucket_name" {
  type    = string
  default = "processados-faturama"
}

variable "artifact_prefix" {
  type    = string
  default = "processed"
}

variable "signed_upload_expiration_seconds" {
  type    = number
  default = 300
}

variable "dispatch_rule_name" {
  type    = string
  default = "faturama-processing-dispatch"
}

variable "ecs_cluster_name" {
  type    = string
  default = "faturama-cluster"
}

variable "ecs_task_family" {
  type    = string
  default = "faturama-worker"
}

variable "container_image_uri" {
  type    = string
  default = "faturama-worker:local"
}

variable "db_name" {
  type    = string
  default = "faturama"
}

variable "db_username" {
  type    = string
  default = "faturama"
}

variable "db_password_secret_ref" {
  type    = string
  default = "local/faturama/db-password"
}

variable "db_password" {
  type    = string
  default = "faturama"
}

variable "db_host" {
  type    = string
  default = "postgres"
}

variable "db_port" {
  type    = number
  default = 5432
}

variable "local_aws_endpoint_url" {
  type    = string
  default = "http://localhost:4566"
}

variable "local_container_aws_endpoint_url" {
  type    = string
  default = "http://ministack:4566"
}

variable "log_group_name" {
  type    = string
  default = "/faturama/local/worker"
}
