output "runtime" {
  value = {
    input_bucket        = module.faturama_runtime.input_bucket_name
    artifact_bucket     = module.faturama_runtime.artifact_bucket_name
    ecs_cluster         = module.faturama_runtime.ecs_cluster_name
    ecs_cluster_arn     = module.faturama_runtime.ecs_cluster_arn
    ecs_task_definition = module.faturama_runtime.ecs_task_definition_arn
    dispatch_rule_name  = module.faturama_runtime.dispatch_rule_name
    dispatch_rule_arn   = module.faturama_runtime.dispatch_rule_arn
    api_role_arn        = module.faturama_runtime.api_role_arn
  }
}
