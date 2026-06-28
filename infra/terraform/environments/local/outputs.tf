output "runtime" {
  value = {
    input_bucket    = module.faturama_runtime.input_bucket_name
    artifact_bucket = module.faturama_runtime.artifact_bucket_name
    queue_name      = module.faturama_runtime.processing_queue_name
    state_machine   = module.faturama_runtime.state_machine_name
    ecs_cluster     = module.faturama_runtime.ecs_cluster_name
  }
}
