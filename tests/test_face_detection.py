"""Tests for the face_detection package."""
import pytest
from os import path
from edge_device.face_detection import face_detector, video_streamer
import pathlib
from typing import List


class MockFaceDetector(face_detector.IFaceDetector):
    """Mock for IFaceDetector interface."""

    def get_faces(self, image_path: str) -> List[List[int]]:
        """Mock implementation for get_faces always returns [[1]]."""
        return [[1]]


class TestFaceDetector:
    """Tests for the face_detector module."""

    def test_detect_faces(self) -> None:
        """Test that faces are detected in sample image."""
        test_file_path = pathlib.Path(__file__).parent.absolute()
        image_path = str(test_file_path / 'test_faces.jpg')
        detector = face_detector.FaceDetector()
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
    def _mock_callback(faces: List[List[int]]) -> None:
        """Mock callback for testing video stream."""
        assert faces[0][0] == 1

    def test_start_stream(self) -> None:
        """Test starting a stream with a mock FaceDetector."""
        face_detector = MockFaceDetector()
        test_file_path = pathlib.Path(__file__).parent.absolute()
        test_video_path = str(test_file_path / 'test_video.avi')
        streamer = video_streamer.VideoStreamer(face_detector, test_video_path)
        streamer.start_stream(self._mock_callback)
