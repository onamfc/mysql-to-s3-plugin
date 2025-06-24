import sys
import os
sys.path.append("/opt")  # If using Lambda Layers

from main import export_to_parquet

def lambda_handler(event, context):
    export_to_parquet()
    return {
        "statusCode": 200,
        "body": "Export completed"
    }