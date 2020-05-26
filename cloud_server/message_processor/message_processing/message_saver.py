"""Module to save messages in cloud object storage."""
import ibm_boto3
from ibm_botocore.client import Config, ClientError
from typing import List, Tuple
from uuid import UUID, uuid4


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
        self._checked_buckets: List[Tuple[str, str]] = []

    def store_object(
            self,
            message: bytes,
            object_name: str,
            bucket_name: str) -> None:
        """Store object in cloud storage."""
        # check if we already created the bucket
        print('Received message. Checking of bucket exists...')
        if (bucket_name not in [name for (name, _) in self._checked_buckets]):
            # check if bucket exists
            existing_buckets: List[str]
            try:
                existing_buckets = [
                    bucket.name for bucket in self._cos_client.buckets.all()]
                short_names = [name[:len(bucket_name)]
                               for name in existing_buckets]
            except ClientError as error:
                print(f'Client error while listing buckets: {error}')
                raise error
            except Exception as error:
                print(f'Unknown exception while listing buckets: {error}')
                raise error
            if (bucket_name not in short_names):
                try:
                    bucket_uuid = uuid4()
                    full_name = f'{bucket_name}-{bucket_uuid}'[:63]
                    print(f'Creating new bucket {full_name}.')
                    self._cos_client.Bucket(full_name).create(
                        CreateBucketConfiguration={
                            "LocationConstraint": self._bucket_location
                        }
                    )
                except ClientError as error:
                    print(f'Client error while creating bucket: {error}')
                    raise error
                except Exception as error:
                    print(f'Unknown exception while creating bucket: {error}')
                    raise error
                self._checked_buckets.append((bucket_name, full_name))
            else:
                full_name = existing_buckets[short_names.index(bucket_name)]
                self._checked_buckets.append((bucket_name, full_name))
        try:
            full_name = self._checked_buckets[[name for (
                name, _) in self._checked_buckets].index(bucket_name)][1]
            print(f'Posting object {object_name} to bucket: {full_name}.')
            self._cos_client.Object(full_name, object_name).put(
                Body=message
            )
        except ClientError as error:
            print(f'Client error while creating object: {error}')
            raise error
        except Exception as error:
            print(f'Unknown exception while creating object: {error}')
            raise error
