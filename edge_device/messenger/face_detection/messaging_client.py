"""Module to publish detected faces to the message broker."""
import paho.mqtt.client as mqtt
from .face_detector import IFaceDetector
from .video_streamer import IVideoStreamer
from abc import ABC, abstractmethod
import numpy as np
from typing import List
import cv2 as cv


class IMessagingClient(ABC):
    """Internal messaging client used by FaceMessenger."""

    @abstractmethod
    def connect_async(self, hostname: str, port: int) -> None:
        """Connect to message broker and return control to current thread."""
        raise NotImplementedError

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the message broker."""
        raise NotImplementedError

    @abstractmethod
    def loop_start(self) -> None:
        """Start new thread to process network traffic with broker."""
        raise NotImplementedError

    @abstractmethod
    def loop_stop(self) -> None:
        """Stop loop previously started with loop_start."""
        raise NotImplementedError

    @abstractmethod
    def publish(
            self,
            output_channel: str,
            message: str,
            guarantee_level: int) -> None:
        """Publish message to broker.

        Args:
            output_channel: channel on which to publish message.
            message: message to publish.
            guarantee_level: level of guarantee that message is delivered.
        """
        raise NotImplementedError


class MqttClient(IMessagingClient):
    """Mqtt implementation of IMessagingClient."""

    def __init__(self) -> None:
        """Initialize mqtt.Client."""
        self._client = mqtt.Client()

    def connect_async(self, hostname: str, port: int) -> None:
        """Connect asyncronously to Mqtt broker."""
        self._client.connect_async(hostname, port)

    def disconnect(self) -> None:
        """Disconnect from the message broker."""
        self._client.disconnect()

    def loop_start(self) -> None:
        """Start processing network traffic with broker."""
        self._client.loop_start()

    def loop_stop(self) -> None:
        """Stop loop previously started with loop_start."""
        self._client.loop_stop()

    def publish(
            self,
            output_channel: str,
            message: str,
            guarantee_level: int) -> None:
        """Publish message to broker.

        Args:
            output_channel: topic to publish message onto.
            message: message to publish.
            guarantee_level: mqtt quality of service to use when publishing
                message.
                0 = at most once, 1 = at least once, 2 = exactly once.
        """
        self._client.publish(output_channel, message, guarantee_level)


class FaceMessenger:
    """Client for passing faces to broker."""

    def __init__(
            self,
            output_channel: str,
            broker_host: str,
            broker_port: int,
            video_streamer: IVideoStreamer,
            messaging_client: IMessagingClient = MqttClient(),
            guarantee_level: int = 0) -> None:
        """Initialize the client.

        Args:
            messaging_client: client to use for sending messages.
                Defaults to MqttClient.
            output_channel: name of the channel to publish messages to.
            broker_host: hostname or ip address of broker.
            broker_port: port to use when connecting to broker.
            video_streamer: streamer used to stream video.
            guarantee_level: level of guarantee for message delivery.
                Defaults to 0 (at most once)
        """
        self._client = messaging_client
        self.output_channel = output_channel
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.video_streamer = video_streamer
        self.guarantee_level = guarantee_level

    def _process_faces(self, image: np.ndarray,
                       faces: List[List[int]]) -> None:
        """Cut faces from image and send to broker."""
        for (x, y, w, h) in faces:
            cut_image = image[y:y + h, x:x + w]
            _, png = cv.imencode('.png', cut_image)
            png_bytes = png.tobytes()
            self._client.publish(
                self.output_channel,
                png_bytes,
                self.guarantee_level)

    def stream_messages(self) -> None:
        """Start streaming messages."""
        self._client.connect_async(self.broker_host, self.broker_port)
        self._client.loop_start()
        self.video_streamer.start_stream(self._process_faces)
        self._client.loop_stop()
        self._client.disconnect()
