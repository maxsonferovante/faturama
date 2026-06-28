variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "environment_name" {
  type    = string
  default = "aws-dev"
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

variable "processing_queue_name" {
  type    = string
  default = "faturama-processing"
}

variable "processing_dlq_name" {
  type    = string
  default = "faturama-processing-dlq"
}

variable "pipe_name" {
  type    = string
  default = "faturama-processing-pipe"
}

variable "state_machine_name" {
  type    = string
  default = "faturama-processing-sm"
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
  default = "123456789012.dkr.ecr.us-east-1.amazonaws.com/faturama-worker:latest"
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
  default = "arn:aws:secretsmanager:us-east-1:123456789012:secret:faturama/db"
}

variable "db_host" {
  type    = string
  default = "faturama.cluster.local"
}

variable "db_port" {
  type    = number
  default = 5432
}

variable "status_polling_visibility_seconds" {
  type    = number
  default = 30
}

variable "subnet_ids" {
  type    = list(string)
  default = []
}

variable "security_group_ids" {
  type    = list(string)
  default = []
}

variable "log_group_name" {
  type    = string
  default = "/faturama/aws-dev/worker"
}
