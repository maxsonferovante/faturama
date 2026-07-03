import json
import urllib.parse
import os
import uuid
import boto3

def lambda_handler(event, context):
    print("Received event:", json.dumps(event))
    
    records = event.get("Records", [])
    if not records:
        print("No records found in event.")
        return {"statusCode": 200, "body": "No records"}

    ecs = boto3.client("ecs")
    
    cluster = os.environ["ECS_CLUSTER_NAME"]
    task_definition = os.environ["ECS_TASK_DEFINITION_ARN"]
    launch_type = os.environ.get("ECS_LAUNCH_TYPE", "EC2")
    artifact_prefix = os.environ.get("FATURAMA_ARTIFACT_PREFIX", "processed")
    
    for record in records:
        bucket = record["s3"]["bucket"]["name"]
        key = urllib.parse.unquote_plus(record["s3"]["object"]["key"])
        event_time = record["eventTime"]
        
        etag = record["s3"]["object"].get("eTag", "")
        version_id = record["s3"]["object"].get("versionId", "null")
        sequencer = record["s3"]["object"].get("sequencer", "")
        
        event_id = f"local-lambda-{str(uuid.uuid4())[:8]}"
        
        processing_message = {
            "processing_id": f"evtbridge-{event_id}",
            "bucket": bucket,
            "object_key": key,
            "event_time": event_time,
            "source": "aws.s3.eventbridge",
            "artifact_prefix": artifact_prefix,
            "metadata": {
                "source_event_id": event_id,
                "eventbridge_id": event_id,
                "etag": etag,
                "version_id": version_id,
                "sequencer": sequencer,
                "request_id": "",
                "requester": "",
                "reason": ""
            }
        }
        
        processing_message_str = json.dumps(processing_message, ensure_ascii=False)
        print(f"Triggering ECS RunTask on cluster {cluster} for S3 object: s3://{bucket}/{key}")
        print(f"FATURAMA_PROCESSING_MESSAGE: {processing_message_str}")
        
        try:
            response = ecs.run_task(
                cluster=cluster,
                taskDefinition=task_definition,
                launchType=launch_type,
                count=1,
                overrides={
                    "containerOverrides": [
                        {
                            "name": "worker",
                            "environment": [
                                {
                                    "name": "FATURAMA_PROCESSING_MESSAGE",
                                    "value": processing_message_str
                                }
                            ]
                        }
                    ]
                }
            )
            print("ECS RunTask response:", json.dumps(response, default=str))
        except Exception as e:
            print("Failed to run task on ECS:", str(e))
            raise e
            
    return {"statusCode": 200, "body": "Processed successfully"}
