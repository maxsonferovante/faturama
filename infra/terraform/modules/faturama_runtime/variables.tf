variable "aws_region" {
  type = string
}

variable "environment_name" {
  type = string
}

variable "input_bucket_name" {
  type = string
}

variable "artifact_bucket_name" {
  type = string
}

variable "artifact_prefix" {
  type = string
}

variable "signed_upload_expiration_seconds" {
  type = number
}

variable "processing_queue_name" {
  type = string
}

variable "processing_dlq_name" {
  type = string
}

variable "pipe_name" {
  type = string
}

variable "state_machine_name" {
  type = string
}

variable "ecs_cluster_name" {
  type = string
}

variable "ecs_task_family" {
  type = string
}

variable "container_image_uri" {
  type = string
}

variable "db_name" {
  type = string
}

variable "db_username" {
  type = string
}

variable "db_password_secret_ref" {
  type = string
}

variable "db_host" {
  type = string
}

variable "db_port" {
  type = number
}

variable "status_polling_visibility_seconds" {
  type = number
}

variable "use_local_aws_endpoints" {
  type = bool
}

variable "local_aws_endpoint_url" {
  type    = string
  default = null
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
  type = string
}
