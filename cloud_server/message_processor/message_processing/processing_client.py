"""Module exposing messaging client to read messages and save them."""
import paho.mqtt.client as mqtt
from typing import Dict
from .message_saver import MessageSaver
from uuid import uuid4, UUID


class ProcessingClient:
    """Client to subscribe to broker and process messages."""

    def __init__(
            self,
            broker_host: str,
            broker_port: int,
            channel: str,
            message_saver: MessageSaver) -> None:
        """Initialize the client."""
        self._host = broker_host
        self._port = broker_port
        self._channel = f'{channel}/+'
        output_channel_uuid = str(uuid4())
        self._output_channel = f'{channel}-{output_channel_uuid}'
        self._client = mqtt.Client()
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        self._message_saver = message_saver

    def _on_connect(
            self,
            _: mqtt.Client,
            __: Dict[str, str],
            ___: Dict[str, int],
            ____: int) -> None:
        print(f'Connected to message broker. Subscribing to {self._channel}')
        self._client.subscribe(self._channel)
        print(f'Successfully subscribed.')

    def _on_message(
            self,
            _: mqtt.Client,
            __: Dict[str, str],
            message: str) -> None:
        object_name: str = str(uuid4())
        print('Received message. Processing...')
        self._message_saver.store_object(
            message, object_name, self._output_channel)
        print('Message processed successfully.')

    def start(self) -> None:
        """Subscribe to messaging server and start processing."""
        print('Connecting to message broker...')
        self._client.connect(self._host, self._port)
        print('Connected. Starting loop...')
        self._client.loop_forever()
