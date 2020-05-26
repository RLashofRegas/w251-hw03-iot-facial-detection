"""Module to save messages in cloud object storage."""
import ibm_boto3
from ibm_botocore.client import Config, ClientError
from typing import List


class MessageSaver:
    """Class to save messags to cloud object storage."""

    def __init__(
            self,
            api_key: str,
            resource_crn: str,
            endpoint: str = 'https://s3.wdc.us.cloud-object-storage' +
            '.appdomain.cloud',
            auth_endpoint: str = 'https://iam.cloud.ibm.com' +
            '/identity/token',
            bucket_location: str = 'us-standard') -> None:
        """Initialize MessageSaver client."""
        self._cos_client = ibm_boto3.resource(
            "s3",
            ibm_api_key_id=api_key,
            ibm_service_instance_id=resource_crn,
            ibm_auth_endpoint=auth_endpoint,
            config=Config(signature_version="oauth"),
            endpoint_url=endpoint)
        self._bucket_location = bucket_location
        self._checked_buckets: List[str] = []

    def store_object(
            self,
            message: str,
            object_name: str,
            bucket_name: str) -> None:
        """Store object in cloud storage."""
        # check if we already created the bucket
        if (bucket_name not in self._checked_buckets):
            # check if bucket exists
            existing_buckets: List[str]
            try:
                existing_buckets = [
                    bucket.name for bucket in self._cos_client.buckets.all()]
            except ClientError as error:
                print(f'Client error while listing buckets: {error}')
                raise error
            if (bucket_name not in existing_buckets):
                try:
                    print(f'Creating new bucket {bucket_name}.')
                    self._cos_client.Bucket(bucket_name).create(
                        CreateBucketConfiguration={
                            "LocationConstraint": self._bucket_location
                        }
                    )
                except ClientError as error:
                    print(f'Client error while creating bucket: {error}')
                    raise error
                self._checked_buckets.append(bucket_name)
            else:
                self._checked_buckets.append(bucket_name)
        try:
            self._cos_client.Object(bucket_name, object_name).put(
                Body=message
            )
        except ClientError as error:
            print(f'Client error while creating object: {error}')
            raise error
