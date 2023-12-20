import os
import boto3
from botocore.exceptions import NoCredentialsError


def upload_file_to_s3(aws_access_key_id, aws_secret_access_key, aws_region, bucket_name, local_file_path, s3_object_key=None):
    try:
        s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=aws_region)
        if s3_object_key is None:
            s3_object_key = os.path.basename(local_file_path)
        s3.upload_file(local_file_path, bucket_name, s3_object_key)
        print(f'Successfully uploaded {local_file_path} to {bucket_name}/{s3_object_key}')
    except NoCredentialsError as e:
        print(f'Error with credentials: {e}')
    except Exception as e:
        print(f'Error uploading file: {e}')

