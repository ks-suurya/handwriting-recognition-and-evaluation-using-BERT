import boto3
from flask import current_app


def get_s3_client():
    """
    Initializes and returns a boto3 S3 client using credentials from the app config.
    """
    return boto3.client(
        's3',
        aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY'],
        region_name=current_app.config['AWS_REGION']
    )


def upload_file_to_s3(file, s3_key, content_type=None):
    """
    Uploads a file-like object or bytes to the configured S3 bucket.

    :param file: The file-like object (e.g., from request.files) or bytes to upload.
    :param s3_key: The destination key (path) in the S3 bucket.
    :param content_type: Optional content type for the S3 object.
    :return: The S3 key of the uploaded file.
    """
    s3_client = get_s3_client()
    bucket_name = current_app.config['S3_BUCKET_NAME']

    # ExtraArgs can be used to set metadata like ContentType
    extra_args = {'ContentType': content_type} if content_type else {}

    try:
        # Works for file-like objects from request.files
        s3_client.upload_fileobj(file, bucket_name, s3_key, ExtraArgs=extra_args)
    except AttributeError:
        # Fallback for when 'file' is raw bytes
        s3_client.put_object(Bucket=bucket_name, Key=s3_key, Body=file, **extra_args)

    return s3_key


def download_file_from_s3(s3_key):
    """
    Downloads a file from the S3 bucket and returns its content as bytes.

    :param s3_key: The key (path) of the file to download.
    :return: The content of the file as bytes.
    """
    s3_client = get_s3_client()
    bucket_name = current_app.config['S3_BUCKET_NAME']

    s3_object = s3_client.get_object(Bucket=bucket_name, Key=s3_key)
    return s3_object['Body'].read()
