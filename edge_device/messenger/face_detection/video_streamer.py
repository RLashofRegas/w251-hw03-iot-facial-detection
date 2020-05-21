"""Module to stream video from webcam into the face_detector."""
import numpy as np
import cv2 as cv
from typing import Union, Callable, List
from .face_detector import IFaceDetector
from abc import ABC, abstractmethod


class IVideoStreamer(ABC):
    """Interface for VideoStreamer."""

    @abstractmethod
    def start_stream(self, process_faces: Callable[[
                     np.ndarray, List[List[int]]], None]) -> None:
        """Start streaming faces."""
        raise NotImplementedError


class VideoStreamer(IVideoStreamer):
    """Streams video and outputs detected faces."""

    def __init__(self, face_detector: IFaceDetector,
                 video_input: Union[int, str] = 0) -> None:
        """Initialize the VideoStreamer.

        Args:
            video_input (int or str): If int, specifies the index of the video
                device (i.e. /dev/video0).
                If str, specifies video file to stream from.
                Defaults to 0 (/dev/video0).
        """
        self.video_input = video_input
        self.face_detector = face_detector

    def start_stream(self, process_faces: Callable[[
                     np.ndarray, List[List[int]]], None]) -> None:
        """Start streaming faces from video_input.

        Args:
            process_faces (callback): takes input of list of found faces in
                the frame and performs necessary action.
        """
        capture = cv.VideoCapture(self.video_input)

        input_is_str = isinstance(self.video_input, str)
        if (input_is_str and not capture.isOpened()):
            capture.open()

        while(not input_is_str or capture.isOpened()):
            read_successful: bool
            frame: np.ndarray
            read_successful, frame = capture.read()
            if(not read_successful):
                break
            faces = self.face_detector.get_faces(frame)
            process_faces(frame, faces)

        capture.release()
