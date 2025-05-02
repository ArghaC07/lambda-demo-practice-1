import json
import boto3
from datetime import datetime
import logging
import os
import pandas as pd

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

                # read the CSV file from S3
                try:
                    df = pd.read_csv(f's3://{source_bucket_name}/{obj["Key"]}')
                    logger.info('CSV File read successfully')
                    logger.info(f'CSV Data: {df}')
                except Exception as e:
                    logger.error(f'Error reading CSV file: {e}')
                    return {
                        'statusCode': 500,
                        'body': json.dumps('Error reading CSV file')
                    }

                # Extract file name without extension
                file_name_without_extension = os.path.splitext(obj['Key'])[0]
                logger.info(f'File name without extension: {file_name_without_extension}')

                # Convert the DataFrame to excel format
                try:
                    destination_path = "s3://" + \
                                        destination_bucket_name + '/' + \
                                        file_name_without_extension + \
                                        '-' + datetime.now().strftime('%Y-%m-%d-%H-%M-%S')\
                                        +'.xlsx' 
                    df.to_excel(destination_path, index=False)
                    logger.info('CSV File converted to Excel format')
                    
                    # DELETE the original CSV file from the source bucket
                    s3_client.delete_object(Bucket=source_bucket_name, Key=obj['Key'])
                    logger.info('CSV File moved to target bucket')

                except Exception as e:
                    logger.error(f'Error moving file: {e}')
                    return {
                        'statusCode': 500,
                        'body': json.dumps('Error moving file')
                    }
