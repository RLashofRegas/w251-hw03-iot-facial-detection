import numpy as np
import cv2 as cv

class FaceDetector:
    def __init__(self):
        self.face_classifier = cv.CascadeClassifier('haarcascade_frontalface_default.xml')

    def get_faces(self, image_path):
        image = self._read_image(image_path)
        return self.face_classifier(image, 1.3, 5)

    def _read_image(self, image_path):
        raw_image = cv.imread(image_path)
        grayscale_image = cv.cvtColor(raw_image, cv.COLOR_BGR2GRAY)
        return grayscale_image
