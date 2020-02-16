import os
import boto3
import logging
from datetime import datetime

S3 = boto3.resource("s3",
    aws_access_key_id       = os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key   = os.getenv('AWS_SECRET_ACCESS_KEY'),
    endpoint_url            = "https://cog.sanger.ac.uk"
)

KEY_STORAGE_BUCKET  = os.getenv("AWS_BUCKET_NAME", "nf-server")
KEY_STORAGE_PREFIX  = os.getenv('AWS_KEY_PREFIX', 'keys/')
KEY_STORAGE_PATH    = os.getenv("KEY_STORAGE_PATH", "./keys")

if not os.path.exists(KEY_STORAGE_PATH):
    os.makedirs(KEY_STORAGE_PATH)

def download_all_keys():        
    logging.info("Downloading all keys from S3")
    for object_summary in S3.Bucket(KEY_STORAGE_BUCKET).objects.filter(Prefix = KEY_STORAGE_PREFIX):
        if object_summary.key[-1] != "/": # is not a folder
            key_name = os.path.basename(object_summary.key)
            local_path = os.path.join(KEY_STORAGE_PATH, key_name)
            logging.info(f"Downloading {key_name}")
            S3.meta.client.download_file(KEY_STORAGE_BUCKET, object_summary.key, local_path)

def sync_keys():
    logging.info("Syncing keys from S3")
    for object_summary in S3.Bucket(KEY_STORAGE_BUCKET).objects.filter(Prefix = KEY_STORAGE_PREFIX):
        if object_summary.key[-1] != "/": # is not a folder
            key_name = os.path.basename(object_summary.key)
            local_path = os.path.join(KEY_STORAGE_PATH, key_name)
            if not os.path.isfile(local_path): # local key missing -> download
                logging.info(f"Downloading {key_name}")
                S3.meta.client.download_file(KEY_STORAGE_BUCKET, object_summary.key, local_path)
            else:
                remote_timestamp = datetime.timestamp(object_summary.last_modified)
                local_timestamp = os.path.getmtime(local_path)
                if remote_timestamp > local_timestamp: # s3 key newer than local -> update
                    logging.info(f"Updating {key_name}")
                    S3.meta.client.download_file(KEY_STORAGE_BUCKET, object_summary.key, local_path)

def get_key(host):
    key_file = os.path.join(KEY_STORAGE_PATH, host) 
    if not os.path.isfile(key_file):
        object_summary = S3.Bucket(KEY_STORAGE_BUCKET).objects.filter(Prefix = f"{KEY_STORAGE_PREFIX}{host}")
        if len(list(object_summary))!=0:
            sync_keys()
        else:
            raise Exception(f"Missing key for '{host}'")
    return key_file
