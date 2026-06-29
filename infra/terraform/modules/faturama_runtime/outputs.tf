output "input_bucket_name" {
  value = aws_s3_bucket.input.bucket
}

output "artifact_bucket_name" {
  value = aws_s3_bucket.artifact.bucket
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.runtime.name
}

output "ecs_cluster_arn" {
  value = aws_ecs_cluster.runtime.arn
}

output "ecs_task_definition_arn" {
  value = aws_ecs_task_definition.worker.arn
}

output "dispatch_rule_name" {
  value = aws_cloudwatch_event_rule.dispatch.name
}

output "dispatch_rule_arn" {
  value = aws_cloudwatch_event_rule.dispatch.arn
}
