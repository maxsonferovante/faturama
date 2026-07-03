data "archive_file" "lambda_zip" {
  count       = var.use_local_aws_endpoints ? 1 : 0
  type        = "zip"
  source_file = "${path.module}/lambda/local_dispatcher.py"
  output_path = "${path.module}/lambda/local_dispatcher.zip"
}

resource "aws_iam_role" "lambda_local" {
  count = var.use_local_aws_endpoints ? 1 : 0
  name  = "faturama-lambda-local-role-${var.environment_name}"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "lambda_local" {
  count = var.use_local_aws_endpoints ? 1 : 0
  name  = "faturama-lambda-local-policy-${var.environment_name}"
  role  = aws_iam_role.lambda_local[0].id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "ecs:RunTask",
          "iam:PassRole",
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}

resource "aws_lambda_function" "local_dispatcher" {
  count            = var.use_local_aws_endpoints ? 1 : 0
  filename         = data.archive_file.lambda_zip[0].output_path
  source_code_hash = data.archive_file.lambda_zip[0].output_base64sha256
  function_name    = "faturama-local-dispatcher-${var.environment_name}"
  role             = aws_iam_role.lambda_local[0].arn
  handler          = "local_dispatcher.lambda_handler"
  runtime          = "python3.11"
  timeout          = 30

  environment {
    variables = {
      ECS_CLUSTER_NAME         = aws_ecs_cluster.runtime.name
      ECS_TASK_DEFINITION_ARN  = aws_ecs_task_definition.worker.arn
      ECS_LAUNCH_TYPE          = local.use_awsvpc ? "FARGATE" : "EC2"
      FATURAMA_ARTIFACT_PREFIX = var.artifact_prefix
    }
  }

  tags = local.common_tags
}

resource "aws_lambda_permission" "allow_s3" {
  count         = var.use_local_aws_endpoints ? 1 : 0
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.local_dispatcher[0].arn
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.input.arn
}
