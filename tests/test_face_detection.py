"""Tests for the face_detection package."""
import numpy as np
from typing import List, Callable
import pathlib
import pytest
from os import path
from edge_device.face_detection.face_detector import (
    FaceDetector, IFaceDetector)
from edge_device.face_detection.messaging_client import (
    IMessagingClient, FaceMessenger)
from edge_device.face_detection.video_streamer import (
    IVideoStreamer, VideoStreamer)
import cv2 as cv


class MockFaceDetector(IFaceDetector):
    """Mock for IFaceDetector interface."""

    def get_faces(self, image_path: str) -> List[List[int]]:
        """Mock implementation for get_faces always returns [[1]]."""
        return [[1]]


class MockVideoStreamer(IVideoStreamer):
    """Mock for IVideoStreamer interface."""

    def __init__(self, test_image: np.ndarray, test_faces: List[List[int]]):
        """Initialize test image and faces to use in stream."""
        self.test_image = test_image
        self.test_faces = test_faces

    def start_stream(self, process_faces: Callable[[
                     np.ndarray, List[List[int]]], None]) -> None:
        """Start streaming faces."""
        process_faces(self.test_image, self.test_faces)


class MockMessagingClient(IMessagingClient):
    """Mock for IMessagingClient interface."""

    def __init__(self, hostname: str, port: int) -> None:
        """Initialize MockMessagingClient."""
        self.messages: List[str] = []
        self.connected = False
        self.looping = False
        self.hostname = hostname
        self.port = port

    def connect_async(self, hostname: str, port: int) -> None:
        """Set self.connected to True if host and port match."""
        if (hostname == self.hostname and port == self.port):
            self.connected = True

    def disconnect(self) -> None:
        """Set self.connected to False."""
        self.connected = False

    def loop_start(self) -> None:
        """Set self.looping to True."""
        self.looping = True

    def loop_stop(self) -> None:
        """Set self.looping to False."""
        self.looping = False

    def publish(
            self,
            output_channel: str,
            message: str,
            guarantee_level: int) -> None:
        """Publish message to messages array."""
        self.messages.append(
            f'channel: {output_channel}, qos: {guarantee_level}'
            + f', message: {message}')


class TestFaceDetector:
    """Tests for the face_detector module."""

    def test_detect_faces(self) -> None:
        """Test that faces are detected in sample image."""
        test_file_path = pathlib.Path(__file__).parent.absolute()
        image_path = str(test_file_path / 'test_faces.jpg')
        detector = FaceDetector()
        faces = detector.get_faces(image_path)
        assert len(faces) == 2
        expected_first_face = [285, 78, 164, 164]
        expected_second_face = [110, 254, 127, 127]
        for expected_face, actual_face in zip(
                [expected_first_face, expected_second_face], faces):
            for expected_val, actual_val in zip(expected_face, actual_face):
                assert actual_val == expected_val


class TestVideoStreamer:
    """Tests for the video_streamer module."""

    @staticmethod
    def _mock_callback(frame: np.ndarray, faces: List[List[int]]) -> None:
        """Mock callback for testing video stream."""
        assert faces[0][0] == 1

    def test_start_stream(self) -> None:
        """Test starting a stream with a mock FaceDetector."""
        face_detector = MockFaceDetector()
        test_file_path = pathlib.Path(__file__).parent.absolute()
        test_video_path = str(test_file_path / 'test_video.avi')
        streamer = VideoStreamer(face_detector, test_video_path)
        streamer.start_stream(self._mock_callback)


class TestMessagingClient:
    """Tests for the messaging_client module."""

    def _initialize_test_image(self, image_size: int = 4) -> np.ndarray:
        test_image = np.zeros((image_size, image_size))
        for i in range(image_size):
            for j in range(image_size):
                test_image[i, j] = (i * image_size + j) / 100.0
        return test_image

    def test_stream_faces(self) -> None:
        """Test streaming messages."""
        output_channel = 'test'
        host = 'localhost'
        port = 1234
        test_image = self._initialize_test_image()
        face_1 = [0, 0, 1, 1]
        face_2 = [2, 2, 2, 2]
        test_faces = [face_1, face_2]
        video_streamer = MockVideoStreamer(test_image, test_faces)
        messaging_client = MockMessagingClient(host, port)
        guarantee_level = 0
        messenger = FaceMessenger(
            output_channel,
            host,
            port,
            video_streamer,
            messaging_client,
            guarantee_level)
        messenger.stream_messages()

        assert len(messaging_client.messages) == 2

        face_1_image = np.array([[0]])
        _, face_1_png = cv.imencode('.png', face_1_image)
        face_1_message = f'channel: {output_channel}' + \
            f', qos: {guarantee_level}' + \
            f', message: {face_1_png.tobytes()}'
        assert face_1_message == messaging_client.messages[0]

        face_2_image = np.array(
            [[10 / 100.0, 11 / 100.0],
             [14 / 100.0, 15 / 100.0]])
        _, face_2_png = cv.imencode('.png', face_2_image)
        face_2_message = f'channel: {output_channel}' + \
            f', qos: {guarantee_level}' + \
            f', message: {face_2_png.tobytes()}'
        assert face_2_message == messaging_client.messages[1]
