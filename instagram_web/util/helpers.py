import boto3, botocore
from config import Config
from werkzeug.utils import secure_filename
import datetime
from flask import flash

s3 = boto3.client(
   "s3",
   aws_access_key_id=Config.S3_KEY,
   aws_secret_access_key=Config.S3_SECRET
)

def upload_file_to_s3(file, bucket_name, acl="public-read"):
    u_name =secure_filename(str(datetime.datetime.now()) + file.filename)
    try:
        s3.upload_fileobj(
            file,
            bucket_name,
            u_name,
            ExtraArgs={
                "ACL": acl,
                "ContentType": file.content_type
            }
        )
    except Exception as e:
        flash("Something Happened: ", e)
        return e
    return u_name