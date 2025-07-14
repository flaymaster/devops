import os
import boto3
import logging


logger = logging.getLogger(__name__)


def lambda_handler(event, context):
    s3 = boto3.client('s3')
    bucket_name = os.environ['S3_BUCKET_NAME']
    results = []
    records = event.get('Records', [])
    logger.info(f"sqs event received: {records}")
    for record in records:
        body = record.get('body')
        message_id = record.get('messageId')
        file_name = f"{message_id}.txt"
        # Write body to a file
        with open(file_name, 'w') as f:
            f.write(body)
        # Upload to S3
        s3.upload_file(file_name, bucket_name, file_name)
        logger.info(f'Received SQS message: {body}')
        logger.info(f'Uploaded {file_name} to S3 bucket {bucket_name}')
        results.append({
            'messageId': message_id,
            'status': 'processed',
            's3_key': file_name
        })
    return {'results': results}
