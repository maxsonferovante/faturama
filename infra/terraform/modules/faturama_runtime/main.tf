locals {
  common_tags = {
    project     = "faturama"
    environment = var.environment_name
  }

  use_awsvpc = !var.use_local_aws_endpoints && length(var.subnet_ids) > 0 && length(var.security_group_ids) > 0

  worker_environment = {
    FATURAMA_RUNTIME_ENV                      = var.environment_name
    FATURAMA_DB_DSN                           = format("postgresql://%s:%s@%s:%d/%s", var.db_username, var.db_password, var.db_host, var.db_port, var.db_name)
    FATURAMA_AWS_REGION                       = var.aws_region
    FATURAMA_INPUT_BUCKET                     = var.input_bucket_name
    FATURAMA_ARTIFACT_BUCKET                  = var.artifact_bucket_name
    FATURAMA_ARTIFACT_PREFIX                  = var.artifact_prefix
    FATURAMA_SIGNED_UPLOAD_EXPIRATION_SECONDS = tostring(var.signed_upload_expiration_seconds)
    FATURAMA_AWS_ENDPOINT_URL                 = var.use_local_aws_endpoints ? var.local_container_aws_endpoint_url : null
  }

  worker_environment_pairs = [
    for name, value in local.worker_environment : {
      name  = name
      value = value
    } if value != null
  ]
}

resource "aws_s3_bucket" "input" {
  bucket = var.input_bucket_name
  tags   = local.common_tags
}

resource "aws_s3_bucket" "artifact" {
  bucket = var.artifact_bucket_name
  tags   = local.common_tags
}

resource "aws_s3_bucket_notification" "input" {
  bucket      = aws_s3_bucket.input.id
  eventbridge = true

  dynamic "lambda_function" {
    for_each = var.use_local_aws_endpoints ? [1] : []
    content {
      lambda_function_arn = aws_lambda_function.local_dispatcher[0].arn
      events              = ["s3:ObjectCreated:*"]
      filter_prefix       = "incoming/"
      filter_suffix       = ".pdf"
    }
  }

  depends_on = [
    aws_lambda_permission.allow_s3
  ]
}

resource "aws_iam_role" "ecs_task_execution" {
  name = "${var.ecs_task_family}-execution-role-${var.environment_name}"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "sts:AssumeRole"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
  tags = local.common_tags
}

resource "aws_iam_role" "ecs_task" {
  name = "${var.ecs_task_family}-task-role-${var.environment_name}"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "sts:AssumeRole"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
  tags = local.common_tags
}

resource "aws_iam_role_policy" "ecs_task" {
  name = "${var.ecs_task_family}-task-policy-${var.environment_name}"
  role = aws_iam_role.ecs_task.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.input.arn,
          "${aws_s3_bucket.input.arn}/*",
          aws_s3_bucket.artifact.arn,
          "${aws_s3_bucket.artifact.arn}/*"
        ]
      }
    ]
  })
}

resource "aws_ecs_cluster" "runtime" {
  name = var.ecs_cluster_name
  tags = local.common_tags
}

resource "aws_ecs_task_definition" "worker" {
  family                   = var.ecs_task_family
  requires_compatibilities = local.use_awsvpc ? ["FARGATE"] : ["EC2"]
  network_mode             = local.use_awsvpc ? "awsvpc" : "bridge"
  cpu                      = "1024"
  memory                   = "2048"
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn
  container_definitions = jsonencode([
    {
      name        = "worker"
      image       = var.container_image_uri
      essential   = true
      cpu         = 1024
      memory      = 2048
      environment = local.worker_environment_pairs
    }
  ])
  tags = local.common_tags
}

resource "aws_iam_role" "eventbridge_ecs" {
  name = "${var.dispatch_rule_name}-role-${var.environment_name}"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "sts:AssumeRole"
        Principal = {
          Service = "events.amazonaws.com"
        }
      }
    ]
  })
  tags = local.common_tags
}

resource "aws_iam_role_policy" "eventbridge_ecs" {
  name = "${var.dispatch_rule_name}-policy-${var.environment_name}"
  role = aws_iam_role.eventbridge_ecs.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["ecs:RunTask"]
        Resource = aws_ecs_task_definition.worker.arn
      },
      {
        Effect = "Allow"
        Action = ["iam:PassRole"]
        Resource = [
          aws_iam_role.ecs_task_execution.arn,
          aws_iam_role.ecs_task.arn
        ]
      }
    ]
  })
}

resource "aws_cloudwatch_event_rule" "dispatch" {
  name        = var.dispatch_rule_name
  description = "Dispatch uploaded PDFs from S3 directly to the faturama ECS worker"
  event_pattern = jsonencode({
    source        = ["aws.s3"]
    "detail-type" = ["Object Created"]
    detail = {
      bucket = {
        name = [aws_s3_bucket.input.bucket]
      }
      object = {
        key = [
          {
            wildcard = "incoming/*.pdf"
          }
        ]
      }
    }
  })
  tags = local.common_tags
}

resource "aws_cloudwatch_event_target" "dispatch" {
  rule      = aws_cloudwatch_event_rule.dispatch.name
  target_id = "dispatch-ecs-worker"
  arn       = aws_ecs_cluster.runtime.arn
  role_arn  = aws_iam_role.eventbridge_ecs.arn

  ecs_target {
    task_count          = 1
    task_definition_arn = aws_ecs_task_definition.worker.arn
    launch_type         = local.use_awsvpc ? "FARGATE" : "EC2"

    dynamic "network_configuration" {
      for_each = local.use_awsvpc ? [1] : []
      content {
        subnets          = var.subnet_ids
        security_groups  = var.security_group_ids
        assign_public_ip = true
      }
    }
  }

  input_transformer {
    input_paths = {
      event_id   = "$.id"
      bucket     = "$.detail.bucket.name"
      object_key = "$.detail.object.key"
      event_time = "$.time"
      etag       = "$.detail.object.etag"
      version_id = "$.detail.object.version-id"
      sequencer  = "$.detail.object.sequencer"
      request_id = "$.detail.request-id"
      requester  = "$.detail.requester"
      reason     = "$.detail.reason"
    }
    input_template = <<-EOT
{
  "containerOverrides": [
    {
      "name": "worker",
      "environment": [
        {
          "name": "FATURAMA_PROCESSING_MESSAGE",
          "value": "{\"processing_id\":\"evtbridge-<event_id>\",\"bucket\":\"<bucket>\",\"object_key\":\"<object_key>\",\"event_time\":\"<event_time>\",\"source\":\"aws.s3.eventbridge\",\"artifact_prefix\":\"${var.artifact_prefix}\",\"metadata\":{\"source_event_id\":\"<event_id>\",\"eventbridge_id\":\"<event_id>\",\"etag\":\"<etag>\",\"version_id\":\"<version_id>\",\"sequencer\":\"<sequencer>\",\"request_id\":\"<request_id>\",\"requester\":\"<requester>\",\"reason\":\"<reason>\"}}"
        }
      ]
    }
  ]
}
EOT
  }
}
