import os
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

class R2Client:
    def __init__(self):
        self.access_key_id = os.getenv("R2_ACCESS_KEY_ID")
        self.secret_access_key = os.getenv("R2_SECRET_ACCESS_KEY")
        self.bucket_name = os.getenv("R2_BUCKET_NAME")
        self.endpoint_url = os.getenv("R2_ENDPOINT_URL")
        
        if not all([self.access_key_id, self.secret_access_key, self.bucket_name, self.endpoint_url]):
            raise ValueError("One or more R2 environment variables are not set.")

        self.s3_client = boto3.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            config=Config(signature_version='s3v4')
        )

    def generate_presigned_upload_url(self, object_key: str, expiration: int = 3600) -> str:
        """Generate a presigned URL for uploading a file to R2."""
        try:
            response = self.s3_client.generate_presigned_url(
                'put_object',
                Params={'Bucket': self.bucket_name, 'Key': object_key},
                ExpiresIn=expiration
            )
            return response
        except ClientError as e:
            print(f"Error generating presigned URL: {e}")
            return None

    def generate_presigned_download_url(self, object_key: str, expiration: int = 3600) -> str:
        """Generate a presigned URL for downloading a file from R2."""
        try:
            response = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': object_key},
                ExpiresIn=expiration
            )
            return response
        except ClientError as e:
            print(f"Error generating presigned download URL: {e}")
            return None

# Singleton instance
r2_client = R2Client()

def get_r2_client() -> R2Client:
    return r2_client
