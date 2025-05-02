import json
import boto3
from datetime import datetime
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    s3_client = boto3.client('s3')
    source_bucket_name = 'source-bucket-4303'
    destination_bucket_name = 'target-bucket-4302'
    response = s3_client.list_objects_v2(Bucket=source_bucket_name)
    if 'Contents' in response:
        logger.info('Inside Contents') 
        for obj in response['Contents']:
            if obj['Key'].endswith('.csv'):
                logger.info('CSV File found in source bucket')
                
                # Extract file name without extension
                file_name_without_extension = os.path.splitext(obj['Key'])[0]
                logger.info(f'File name without extension: {file_name_without_extension}')
                try:
                    s3_client.copy_object(
                            Bucket=destination_bucket_name,
                            CopySource={'Bucket': source_bucket_name, 'Key': obj['Key']},
                            Key=file_name_without_extension + '-' + datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.csv'
                )
                    s3_client.delete_object(Bucket=source_bucket_name, Key=obj['Key'])
                    logger.info('CSV File moved to target bucket')
                    
                except Exception as e:
                    logger.error(f'Error moving file: {e}')
                    return {
                        'statusCode': 500,
                        'body': json.dumps('Error moving file')
                    }
