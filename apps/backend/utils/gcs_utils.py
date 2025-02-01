import logging
from typing import Any

from google.cloud import storage
import io

logger = logging.getLogger(__name__)


def upload_blob_from_stream(bucket_name: str, destination_blob_name: str, content: Any):
    """Uploads bytes from a stream or other file-like object to a blob."""
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        logger.debug("blob is %s", f"{blob}")
        file_obj = io.BytesIO()
        if content:
            file_obj.write(content)
            logger.debug("file_obj after write is: %s", f"{file_obj.readline(0)}")
            blob.upload_from_file(
                file_obj=file_obj,
                rewind=True,
            )
        return blob.public_url
    except Exception as e:
        logging.error(f"Opps. Blob upload broke somewhere! {e}")


def upload_blob_from_memory(bucket_name: str, contents: str, destination_blob_name: str):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(contents)
    print(f"{destination_blob_name} with contents {contents} uploaded to {bucket_name}.")
    return blob.public_url
