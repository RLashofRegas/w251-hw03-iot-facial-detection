"""Classes to aid in detecting faces."""
import numpy as np
import cv2 as cv
from typing import List, Union
import pathlib
import os
import errno
from abc import ABC, abstractmethod


class IFaceDetector(ABC):
    """Interface for FaceDetector."""

    @abstractmethod
    def get_faces(self, image: Union[np.ndarray, str]) -> List[List[int]]:
        """Return faces for an image."""
        raise NotImplementedError


class FaceDetector(IFaceDetector):
    """Detects faces in images."""

    def __init__(
            self,
            classifier: str = 'haarcascade_frontalface_default.xml') -> None:
        """Initialize classifier used for detecting faces.

        Args:
            classifier: openCV classifier to use.
                Defaults to haarcascade_frontalface_default.xml.
        """
        cv_path = pathlib.Path(os.path.dirname(cv.__file__))
        cv_files = list(cv_path.rglob(classifier))
        if len(cv_files) > 0:
            classifier_path = cv_files[0]
        else:
            cv_path = pathlib.Path('/usr/share/OpenCV')
            cv_files = list(cv_path.rglob(classifier))
            if len(cv_files) > 0:
                classifier_path = cv_files[0]
            else:
                raise FileNotFoundError(
                    errno.ENOENT, os.strerror(
                        errno.ENOENT), classifier)

        self._face_classifier = cv.CascadeClassifier(str(classifier_path))

    def get_faces(self, image: Union[np.ndarray, str]) -> List[List[int]]:
        """
        Return faces for an image.

        Args:
            image: image to classify.
                Either an image as an ndarray or path to an image on disk.

        Returns:
            array of tuples for coordinates of faces (x, y, w, h)
        """
        if(isinstance(image, str)):
            image = cv.imread(image)
        image = self._preprocess_image(image)
        faces: List[List[int]] = self._face_classifier.detectMultiScale(
            image, 1.3, 5)
        return faces

    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        grayscale_image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        return grayscale_image
