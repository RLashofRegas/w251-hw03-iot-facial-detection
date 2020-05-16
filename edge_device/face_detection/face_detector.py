"""Classes to aid in detecting faces."""
import numpy as np
import cv2 as cv
from typing import List, Tuple
import pathlib
import os


class FaceDetector:
    """Detects faces in images."""

    def __init__(
            self,
            classifier: str = 'haarcascade_frontalface_default') -> None:
        """Initialize classifier used for detecting faces.

        Args:
            classifier: openCV classifier to use.
                Defaults to haarcascade_frontalface_default.
        """
        cv_path = pathlib.Path(os.path.dirname(cv.__file__))
        cascadexml_path = str(cv_path / 'data' / f'{classifier}.xml')
        self._face_classifier = cv.CascadeClassifier(cascadexml_path)

    def get_faces(self, image_path: str) -> List[List[int]]:
        """
        Return faces for an image.

        Args:
            image_path: path to image to classify

        Returns:
            array of tuples for coordinates of faces (x, y, w, h)
        """
        image = self._read_image(image_path)
        faces: List[List[int]] = self._face_classifier.detectMultiScale(
            image, 1.3, 5)
        return faces

    def _read_image(self, image_path: str) -> np.ndarray:
        raw_image = cv.imread(image_path)
        grayscale_image = cv.cvtColor(raw_image, cv.COLOR_BGR2GRAY)
        return grayscale_image
