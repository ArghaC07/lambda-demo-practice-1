import json
import boto3
from datetime import datetime
import logging
import os
import pandas as pd
import io
import openpyxl

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
                file_name = os.path.splitext(obj['Key'])[0]
                logger.info(f'File name without extension: {file_name}')

                # read the CSV file from S3
                try:
                    s3_body = s3_client.get_object(Bucket=source_bucket_name, Key=obj['Key'])
                    df = pd.read_csv(io.BytesIO(s3_body['Body'].read()))
                    logger.info('CSV File read successfully')
                    logger.info(f'CSV Data: {df}')
                except Exception as e:
                    logger.error(f'Error reading CSV file: {e}')
                    return {
                        'statusCode': 500,
                        'body': json.dumps('Error reading CSV file')
                    }

             

                # Convert the DataFrame to excel format
                try:
                    excel_buffer = io.BytesIO()
                    df_excel = df.to_excel(excel_buffer, index=False, engine='openpyxl')
                    excel_buffer.seek(0)  # Move the cursor to the beginning of the stream

                    #upload the excel file to S3
                    s3_client.upload_fileobj(
                        df_excel,
                        Bucket=destination_bucket_name,
                        Key=file_name + '-' + datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.xlsx'
                    )
                    logger.info('Excel file uploaded to target bucket')
                    
                    # DELETE the original CSV file from the source bucket
                    s3_client.delete_object(Bucket=source_bucket_name, Key=obj['Key'])
                    logger.info('CSV File moved to target bucket')

                except Exception as e:
                    logger.error(f'Error moving file: {e}')
                    return {
                        'statusCode': 500,
                        'body': json.dumps('Error moving file')
                    }
