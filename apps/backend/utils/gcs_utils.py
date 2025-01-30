from google.cloud import storage
import io

def upload_blob_from_stream(bucket_name: str, file_obj: io.BytesIO, destination_blob_name: str) -> None:
    """Uploads bytes from a stream or other file-like object to a blob."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    file_obj.seek(0)
    blob.upload_from_file(file_obj)
    print(f"Stream data uploaded to {destination_blob_name} in bucket {bucket_name}.")

def upload_blob_from_memory(bucket_name: str, contents: str, destination_blob_name: str) -> None:
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(contents)
    print(f"{destination_blob_name} with contents {contents} uploaded to {bucket_name}.")
