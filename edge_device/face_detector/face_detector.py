"""Classes to aid in detecting faces."""
import numpy as np
import cv2 as cv
from typing import List, Tuple


class FaceDetector:
    """Detects faces in images."""

    def __init__(self) -> None:
        """Initialize classifier used for detecting faces."""
        self.face_classifier = cv.CascadeClassifier(
            'haarcascade_frontalface_default.xml')

    def get_faces(self, image_path: str) -> List[Tuple[int, int, int, int]]:
        """
        Return faces for an image.

        Args:
            image_path: path to image to classify

        Returns:
            array of tuples for coordinates of faces (x, y, w, h)
        """
        image = self._read_image(image_path)
        faces: List[Tuple[int, int, int, int]
                    ] = self.face_classifier(image, 1.3, 5)
        return faces

    def _read_image(self, image_path: str) -> np.ndarray:
        raw_image = cv.imread(image_path)
        grayscale_image = cv.cvtColor(raw_image, cv.COLOR_BGR2GRAY)
        return grayscale_image
