import os
import json
from pathlib import Path
from typing import Union
from core.config import Config

class StorageManager:
    def __init__(self):
        self.is_aws = Config.is_aws_mode()
        if self.is_aws:
            import boto3
            self.s3_client = boto3.client('s3', region_name=Config.BEDROCK_REGION)
    
    def save_input(self, run_id: str, content: str) -> str:
        # Always save locally for now, even in AWS mode
        path = Path(f"data/input/{run_id}.txt")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
        return str(path)
    
    def save_output(self, run_id: str, filename: str, content: Union[str, dict]) -> str:
        if isinstance(content, dict):
            content = json.dumps(content, indent=2, default=str)
        
        if self.is_aws:
            key = f"followupsync/{run_id}/{filename}"
            self.s3_client.put_object(
                Bucket=Config.S3_BUCKET,
                Key=key,
                Body=content.encode('utf-8')
            )
            return f"s3://{Config.S3_BUCKET}/{key}"
        else:
            path = Path(f"data/output/{run_id}/{filename}")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8')
            return str(path)
    
    def read_input(self, run_id: str) -> str:
        if self.is_aws:
            key = f"followupsync/{run_id}/input.txt"
            response = self.s3_client.get_object(Bucket=Config.S3_BUCKET, Key=key)
            return response['Body'].read().decode('utf-8')
        else:
            path = Path(f"data/input/{run_id}.txt")
            return path.read_text(encoding='utf-8')
    
    def get_download_url(self, run_id: str, filename: str) -> str:
        if self.is_aws:
            key = f"followupsync/{run_id}/{filename}"
            return self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': Config.S3_BUCKET, 'Key': key},
                ExpiresIn=3600
            )
        else:
            return f"data/output/{run_id}/{filename}"