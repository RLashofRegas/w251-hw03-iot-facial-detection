"""Entrypoint for the message processing package for the cloud server."""
import argparse
from message_processing.message_saver import MessageSaver
from message_processing.processing_client import ProcessingClient
from typing import TypedDict, List


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
        print('Starting message processing.')
        self._processing_client.start()


if(__name__ == "__main__"):
    arg_parser = argparse.ArgumentParser(
        description='Run the message processing pipeline.')
    arg_parser.add_argument(
        '-k', '--api_key', type=str, required=True,
        help='COS API Key.')
    arg_parser.add_argument(
        '-n', '--crn', type=str, required=True,
        help='COS crn.')
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
    runner = MessageProcessingRunner(
        args.api_key,
        args.crn,
        args.broker,
        args.port,
        args.channel)
    runner.run()
