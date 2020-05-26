"""Entrypoint for the message processing package for the cloud server."""
import argparse
from message_processing.message_saver import MessageSaver
from message_processing.processing_client import ProcessingClient
from typing import TypedDict, List
import json


class MessageProcessingRunner:
    """Runner of the message processing client."""

    def __init__(
            self,
            api_key: str,
            resource_crn: str,
            broker_host: str,
            broker_port: int,
            message_channel: str) -> None:
        """Initialize the MessageProcessingRunner."""
        message_saver = MessageSaver(api_key, resource_crn)
        self._processing_client = ProcessingClient(
            broker_host, broker_port, message_channel, message_saver)

    def run(self) -> None:
        """Run the message processing client."""
        self._processing_client.start()


class Credential(TypedDict):
    """Typed class for credential object in cos_credential."""

    apikey: str
    endpoints: str
    iam_apikey_description: str
    iam_apikey_name: str
    iam_role_crn: str
    iam_serviceid_crn: str
    resource_instance_id: str


class CosCredential(TypedDict):
    """Typed class for cos_credential."""

    guid: str
    id: str
    url: str
    created_at: str
    updated_at: str
    deleted_at: str
    name: str
    account_id: str
    resource_group_id: str
    source_crn: str
    state: str
    credentials: Credential
    iam_compatible: bool
    resource_instance_url: str
    crn: str


if(__name__ == "__main__"):
    arg_parser = argparse.ArgumentParser(
        description='Run the message processing pipeline.')
    arg_parser.add_argument(
        '-k', '--credential_file', type=str, required=True,
        help='Path to the cos credential file.')
    arg_parser.add_argument(
        '-b', '--broker', type=str, required=True,
        help='Hostname of the message broker.')
    arg_parser.add_argument(
        '-p', '--port', type=int, required=True,
        help='Port on the broker host to connect to.')
    arg_parser.add_argument(
        '-c', '--channel', type=str, default='faces',
        help='Channel to subscribe to for incoming messages.')
    args = arg_parser.parse_args()
    credentials: List[CosCredential]
    with open(args.credential_file, 'r') as credential_file:
        credentials = json.load(credential_file)
    credential = credentials[0]
    runner = MessageProcessingRunner(
        credential['credentials']['apikey'],
        credential['crn'],
        args.broker,
        args.port,
        args.channel)
    runner.run()
