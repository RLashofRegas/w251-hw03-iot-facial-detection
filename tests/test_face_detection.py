"""Tests for the face_detector package."""
import pytest
from os import path
from edge_device.face_detection import face_detector
import pathlib


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
